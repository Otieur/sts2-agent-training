// Fidelity mode (docs/simulator-integrity.md FP-3): replays a finished, recorded fight with its true random state, to
// test that the host reproduces the game. Never used for decisions.
using System.Reflection;
using MegaCrit.Sts2.Core.Multiplayer.Replay;
using MegaCrit.Sts2.Core.Multiplayer.Serialization;
using MegaCrit.Sts2.Core.Runs;

public static class Replay
{
    public static CombatReplay Load(string path)
    {
        var bytes = File.ReadAllBytes(path);
        var reader = new PacketReader();
        reader.Reset(bytes);
        // Watchdog for the spike: a stuck read is reported with the reader position instead of hanging the job.
        var done = false;
        var watchdog = new Thread(() =>
        {
            for (var i = 0; i < 20 && !done; i++)
            {
                Thread.Sleep(500);
                if (!done && i % 4 == 3) Console.WriteLine($"     ... reading: bit {reader.BitPosition} of {bytes.Length * 8}; engine calls {Stubs.TotalCalls}");
            }
            if (!done) { Console.WriteLine("STUCK in replay read"); Stubs.Report("stuck"); Environment.Exit(3); }
        }) { IsBackground = true };
        watchdog.Start();
        var replay = reader.Read<CombatReplay>();   // the same call the game's own loader makes (NMultiplayerTest.LoadReplay)
        done = true;
        return replay;
    }

    public static int Run(string[] args)
    {
        try { Stages.Boot(false); } catch (Stages.StageFailed) { return 1; }
        CombatReplay replay = null;
        RunState run = null;
        try
        {
            Stages.Step("read replay", () => replay = Load(args[0]));
            var ours = ModelIdSerializationCache.Hash;
            Console.WriteLine($"     replay {replay.version} {replay.gitCommit}; model-id hash replay {replay.modelIdHash}, host {ours}: {(replay.modelIdHash == ours ? "MATCH" : "DIFFERENT")}");
            Console.WriteLine($"     events {replay.events.Count} ({string.Join(", ", replay.events.GroupBy(e => e.eventType).Select(g => g.Key + " " + g.Count()))}); checksums {replay.checksumData.Count}");
            Stages.Step("RunState.FromSerializable", () => run = RunState.FromSerializable(replay.serializableRun));
            var p = run.Players[0];
            Console.WriteLine($"     players {run.Players.Count}; character {p.Character.Id.Entry}; deck {p.Deck.Cards.Count} cards; relics {p.Relics.Count}; HP {p.Creature.CurrentHp}/{p.Creature.MaxHp}; act index {run.CurrentActIndex}; ascension {run.AscensionLevel}");
            var ctx = new SimContext();
            SynchronizationContext.SetSynchronizationContext(ctx);
            var infos = 0;
            var problems = new Dictionary<string, int>();
            var contexts = new Dictionary<string, int>();
            MegaCrit.Sts2.Core.Logging.Log.LogCallback += (level, text, skip) =>
            {
                if (level.ToString() is "Info" or "Debug" or "VeryDebug" or "Load") { infos++; if (args.Contains("verbose")) Console.WriteLine($"     [game {level}] {text}"); }
                else
                {
                    // one line per distinct problem: the message and the first two stack frames
                    var lines = text.Split('\n');
                    var key = string.Join(" | ", lines.Take(3).Select(l => l.Trim())).Replace("MegaCrit.Sts2.Core.", "");
                    if (key.StartsWith("Replay state divergence")) key = "Replay state divergence (the game's own check)";
                    problems[key] = problems.GetValueOrDefault(key) + 1;
                }
            };
            Stages.Step("game-method stubs", () =>
            {
                var sm = typeof(MegaCrit.Sts2.Core.Saves.SaveManager);
                foreach (var m in new[] { "SaveRun", "SaveRunHistory", "SaveProgressFile", "SavePrefsFile", "SaveSettings", "SaveProfile" })
                    Stubs.Skip(sm, m, "SA-1: the simulator never writes saves");
                Stubs.Skip(typeof(MegaCrit.Sts2.Core.Assets.PreloadManager), "LoadRoomCombatAssets", "assets only: preloads scenes and textures");
                Stubs.Skip(typeof(RunManager), "WriteReplay", "SA-1: the game writes replays/latest.mcr into the save profile at the end of a fight and on clean-up");
                // Localised text is display and log text. The tables live in the game's resource pack, which only the
                // engine can read, so text lookups return an empty string.
                foreach (var m in new[] { "GetFormattedText", "GetRawText" })
                    Stubs.Skip(typeof(MegaCrit.Sts2.Core.Localization.LocString), m, "display and log text only");
                Stubs.MakeInertHelper(typeof(MegaCrit.Sts2.Core.Helpers.GodotTreeExtensions));
                Stubs.AnswerTrue(typeof(MegaCrit.Sts2.Core.Localization.LocString), "Exists", "display text only: every text is treated as present (cards throw when their prompt text is missing)");
                Stubs.Skip(typeof(MegaCrit.Sts2.Core.Models.CardModel), "PlayPowerCardFlyVfx", "display only: the Power card's fly effect");
            });
            Stages.Step("display helpers on the test path", () =>
            {
                // Command-layer methods that check TestMode to skip visuals (list built from the call graph:
                // Commands, Entities.Creatures, Combat and GameActions classes only; never card, monster or relic logic).
                var asm = typeof(RunManager).Assembly;
                var list = System.Text.Json.JsonSerializer.Deserialize<List<string>>(File.ReadAllText(Environment.GetEnvironmentVariable("SIM_TESTPATH")!))!;
                foreach (var full in list)
                {
                    var parts = full.Split("::");
                    var type = asm.GetType(parts[0]);
                    if (type == null) continue;
                    try { Stubs.TestPath(type, parts[1], "display only"); } catch (MissingMethodException) { }
                }
            });
            Stages.Step("inert UI", () =>
            {
                var list = System.Text.Json.JsonSerializer.Deserialize<List<string>>(File.ReadAllText(Environment.GetEnvironmentVariable("SIM_UI_TYPES")!))!;
                var n = Stubs.MakeInertAll(list);
                Console.WriteLine($"     {n} UI classes inert: {Stubs.InertMethods} methods replaced, {Stubs.InertFailed} could not be");
            });
            var rm = RunManager.Instance;
            var pid = p.NetId;
            var checks = 0; var diverged = 0; var same = 0; var different = 0; var unmatched = 0;
            var recorded = new Dictionary<string, Queue<ReplayChecksumData>>();
            Action<MegaCrit.Sts2.Core.Entities.Multiplayer.NetChecksumData, string, MegaCrit.Sts2.Core.Entities.Multiplayer.NetFullCombatState> onChecksum = null;
            void Refill()
            {
                recorded.Clear();
                foreach (var c in replay.checksumData)
                {
                    if (!recorded.TryGetValue(c.context, out var q)) recorded[c.context] = q = new Queue<ReplayChecksumData>();
                    q.Enqueue(c);
                }
            }
            void Apply(MegaCrit.Sts2.Core.Multiplayer.Replay.CombatReplayEvent ev)
            {
                switch (ev.eventType.ToString())
                {
                    case "GameAction": rm.ActionQueueSet.EnqueueWithoutSynchronizing(ev.action.ToGameAction(run.GetPlayer(ev.playerId.Value))); break;
                    case "HookAction": rm.ActionQueueSet.EnqueueWithoutSynchronizing(rm.ActionQueueSynchronizer.GetHookActionForId(ev.hookId.Value, ev.playerId.Value, ev.gameActionType.Value)); break;
                    case "ResumeAction": rm.ActionQueueSet.ResumeActionWithoutSynchronizing(ev.actionId.Value); break;
                    case "PlayerChoice": rm.PlayerChoiceSynchronizer.ReceiveReplayChoice(run.GetPlayer(ev.playerId.Value), ev.choiceId.Value, ev.playerChoiceResult.Value); break;
                }
            }
            Stages.Step("SetUpReplay", () => rm.SetUpReplay(run, replay, pid));
            Stages.Step("checksum hooks", () =>
            {
                rm.CombatStateSynchronizer.IsDisabled = true;
                // The host produces fewer checkpoints than the recording (see the report), so ids do not line up.
                // Checkpoints are paired by their context text, in order.
                Refill();
                onChecksum = (data, context, state) =>
                {
                    checks++;
                    if (!recorded.TryGetValue(context, out var queue) || queue.Count == 0) { unmatched++; contexts[context] = contexts.GetValueOrDefault(context) + 1; return; }
                    var rec = queue.Dequeue();
                    // The recorded hash was made with the real player id; the file stores the anonymised full state
                    // next to it. Compare the states as text (stronger than a hash: FI-12).
                    // Anonymised player ids differ between processes: mask them.
                    string Mask(string s) => System.Text.RegularExpressions.Regex.Replace(s, @"(?i)(player (?:with )?ID: )(\d+|#)", "$1#");
                    var mine = Mask(state.Anonymized().ToString());
                    var theirs = Mask(rec.fullState.ToString());
                    if (mine == theirs) same++;
                    else
                    {
                        different++;
                        if (different <= 2)
                        {
                            var i = 0; while (i < mine.Length && i < theirs.Length && mine[i] == theirs[i]) i++;
                            string Cut(string s) => s.Substring(Math.Max(0, i - 160), Math.Min(s.Length - Math.Max(0, i - 160), 420)).Replace("\n", " / ");
                            Console.WriteLine($"     STATE DIFFERS at checksum id {data.id} ({context}; game: {rec.context}); first difference at character {i} of {mine.Length}/{theirs.Length}:\n       host: {Cut(mine)}\n       game: {Cut(theirs)}");
                        }
                    }
                };
                rm.ChecksumTracker.ChecksumGenerated += onChecksum;
                rm.ChecksumTracker.StateDiverged += (id, state) => { diverged++; Console.WriteLine($"     STATE DIVERGED at checksum id {id}"); };
            });
            Stages.Step("Launch", () => rm.Launch());
            Stages.Step("GenerateMap", () => ctx.RunUntil(rm.GenerateMap(), "GenerateMap"));
            Stages.Step("fast-forward ids", () =>
            {
                rm.ActionQueueSet.FastForwardNextActionId(replay.nextActionId);
                rm.ActionQueueSynchronizer.FastForwardHookId(replay.nextHookId);
                rm.ChecksumTracker.LoadReplayChecksums(replay.checksumData, replay.nextChecksumId);
                rm.PlayerChoiceSynchronizer.FastForwardChoiceIds(replay.choiceIds);
                rm.RewardsSetSynchronizer.FastForwardRewardIds(replay.rewardIds);
            });
            Stages.Step("enter the room", () =>
            {
                var room = MegaCrit.Sts2.Core.Rooms.AbstractRoom.FromSerializable(replay.serializableRun.PreFinishedRoom, run);
                Console.WriteLine($"     room {room?.GetType().Name}");
                ctx.RunUntil(rm.LoadIntoLatestMapCoord(room), "LoadIntoLatestMapCoord");
            });
            string Board()
            {
                var cs = MegaCrit.Sts2.Core.Combat.CombatManager.Instance.DebugOnlyGetState();
                var me = run.Players[0].Creature;
                return $"HP {me.CurrentHp}/{me.MaxHp} block {me.Block} | " + string.Join(", ", cs.Enemies.Select(e => $"{e.ModelId.Entry} {e.CurrentHp}/{e.MaxHp}{(e.Block > 0 ? " block " + e.Block : "")}"));
            }
            Console.WriteLine($"     combat started: {Board()}");
            Console.WriteLine($"     checksums so far: {checks} generated, {same} states equal to the game's, {different} different, {unmatched} without a recorded partner");
            var sw = System.Diagnostics.Stopwatch.StartNew();
            var applied = 0;
            Stages.Step("apply the recorded events", () =>
            {
                foreach (var ev in replay.events)
                {
                    ctx.Drain();
                    var label = ev.eventType.ToString();
                    switch (label)
                    {
                        case "GameAction":
                            var ga = ev.action.ToGameAction(run.GetPlayer(ev.playerId.Value));
                            label = ga.GetType().Name;
                            rm.ActionQueueSet.EnqueueWithoutSynchronizing(ga);
                            break;
                        case "HookAction":
                            rm.ActionQueueSet.EnqueueWithoutSynchronizing(rm.ActionQueueSynchronizer.GetHookActionForId(ev.hookId.Value, ev.playerId.Value, ev.gameActionType.Value));
                            break;
                        case "ResumeAction":
                            rm.ActionQueueSet.ResumeActionWithoutSynchronizing(ev.actionId.Value);
                            break;
                        case "PlayerChoice":
                            rm.PlayerChoiceSynchronizer.ReceiveReplayChoice(run.GetPlayer(ev.playerId.Value), ev.choiceId.Value, ev.playerChoiceResult.Value);
                            break;
                    }
                    ctx.Drain();
                    applied++;
                    if (args.Contains("trace")) Console.WriteLine($"     {applied,3} {label,-22} {Board()}");
                }
            });
            sw.Stop();
            var cm = MegaCrit.Sts2.Core.Combat.CombatManager.Instance;
            Console.WriteLine($"     events applied {applied} of {replay.events.Count} in {sw.Elapsed.TotalMilliseconds:F1} ms; combat in progress: {cm.IsInProgress}; final {Board()}");
            Console.WriteLine($"     checksums: {checks} generated, {same} states equal to the game's, {different} different, {unmatched} without a recorded partner; recorded {replay.checksumData.Count}; divergence events {diverged}");
            Console.WriteLine($"     posted continuations {ctx.Posted}; inert UI calls {Stubs.InertCalls}; game info lines {infos}");
            // Repeat the same fight in the same process: warm timing (P7.E1.S4) and a first isolation check (FI-11).
            if (args.Contains("nolog"))
            {
                // The game formats and prints a log line for most actions; in the host the print goes to an engine stub.
                Stubs.Skip(typeof(MegaCrit.Sts2.Core.Logging.Logger), "LogMessage", "log output only");
            }
            var passes = int.Parse(args.FirstOrDefault(a => a.StartsWith("passes="))?.Split('=')[1] ?? "21");
            var setups = new List<double>(); var fights = new List<double>(); var exact = 0;
            var nocheck = args.Contains("nocheck");
            var proc = System.Diagnostics.Process.GetCurrentProcess();
            TimeSpan cpu0 = default; long eng0 = 0, inert0 = 0, test0 = 0; var counted = 0;
            for (var pass = 2; pass <= passes && !args.Contains("once"); pass++)
            {
                if (pass == 2 + (passes - 1) / 2) { proc.Refresh(); cpu0 = proc.TotalProcessorTime; eng0 = Stubs.TotalCalls; inert0 = Stubs.InertCalls; test0 = Stubs.TestPathCalls; counted = passes - pass + 1; }
                try
                {
                    var sw2 = System.Diagnostics.Stopwatch.StartNew();
                    rm.CleanUp(true);
                    ctx.Drain();
                    run = RunState.FromSerializable(replay.serializableRun);
                    Refill(); checks = same = different = unmatched = 0;
                    rm.SetUpReplay(run, replay, run.Players[0].NetId);
                    rm.CombatStateSynchronizer.IsDisabled = true;
                    // "nocheck": plain simulation speed. No state comparison by the host, no checkpoint hashing and no
                    // replay comparison by the game; the pass is judged by the final HP and the fight ending.
                    if (nocheck) rm.ChecksumTracker.IsEnabled = false; else rm.ChecksumTracker.ChecksumGenerated += onChecksum;
                    rm.Launch();
                    ctx.RunUntil(rm.GenerateMap(), "GenerateMap");
                    rm.ActionQueueSet.FastForwardNextActionId(replay.nextActionId);
                    rm.ActionQueueSynchronizer.FastForwardHookId(replay.nextHookId);
                    if (!nocheck) rm.ChecksumTracker.LoadReplayChecksums(replay.checksumData, replay.nextChecksumId);
                    rm.PlayerChoiceSynchronizer.FastForwardChoiceIds(replay.choiceIds);
                    rm.RewardsSetSynchronizer.FastForwardRewardIds(replay.rewardIds);
                    ctx.RunUntil(rm.LoadIntoLatestMapCoord(null), "enter the room");
                    var setup = sw2.Elapsed.TotalMilliseconds;
                    sw2.Restart();
                    foreach (var ev in replay.events) { ctx.Drain(); Apply(ev); ctx.Drain(); }
                    var fight = sw2.Elapsed.TotalMilliseconds;
                    setups.Add(setup); fights.Add(fight);
                    var ok = (nocheck || (same == checks && different == 0 && checks == 26)) && run.Players[0].Creature.CurrentHp == 87 && !MegaCrit.Sts2.Core.Combat.CombatManager.Instance.IsInProgress;
                    if (ok) exact++;
                    if (pass <= 4 || !ok || args.Contains("trace"))
                        Console.WriteLine($"     pass {pass}: set-up {setup:F1} ms, fight {fight:F1} ms; states equal {same} of {checks} ({different} different); final HP {run.Players[0].Creature.CurrentHp}/{run.Players[0].Creature.MaxHp}; in progress {MegaCrit.Sts2.Core.Combat.CombatManager.Instance.IsInProgress}");
                }
                catch (Exception e) { Console.WriteLine($"     pass {pass} FAILED: {e.GetType().Name}: {e.Message.Split('\n')[0]}\n{string.Join("\n", (e.StackTrace ?? "").Split('\n').Take(5))}"); break; }
            }
            if (fights.Count > 0)
            {
                double Med(List<double> xs) { var s = xs.OrderBy(x => x).ToList(); return s[s.Count / 2]; }
                Console.WriteLine($"     WARM PASSES {fights.Count}{(nocheck ? " (checking off)" : " (checking on)")}: correct {exact} of {fights.Count} ({(nocheck ? "final HP 87, fight over" : "26 of 26 states equal, final HP 87, fight over")})");
                var late = fights.Skip(fights.Count / 2).ToList();
                Console.WriteLine($"     fight, second half of the passes only ({late.Count}): median {Med(late):F2} ms, min {late.Min():F2} ms");
                Console.WriteLine($"     fight (45 events): median {Med(fights):F2} ms, min {fights.Min():F2} ms, max {fights.Max():F2} ms");
                Console.WriteLine($"     set-up (rebuild run state, launch, map, enter room, start combat): median {Med(setups):F2} ms, min {setups.Min():F2} ms");
                if (counted > 0 && fights.Count == passes - 1)
                {
                    proc.Refresh();
                    // CPU time of the whole process (all threads, including the JIT and the garbage collector), so it
                    // does not depend on how busy the machine is. Measured over the second half of the passes.
                    Console.WriteLine($"     CPU time per fight including set-up (second half, {counted} passes): {(proc.TotalProcessorTime - cpu0).TotalMilliseconds / counted:F2} ms");
                    Console.WriteLine($"     per fight: engine-stub calls {(Stubs.TotalCalls - eng0) / counted}, inert UI calls {(Stubs.InertCalls - inert0) / counted}, scoped test-path calls {(Stubs.TestPathCalls - test0) / counted}");
                }
                Console.WriteLine($"     whole fight including set-up: median {Med(fights.Zip(setups, (a, b) => a + b).ToList()):F2} ms; memory {GC.GetTotalMemory(false) / 1048576} MB managed");
            }
            Console.WriteLine($"     recorded checkpoints by kind: {string.Join("; ", replay.checksumData.GroupBy(c => System.Text.RegularExpressions.Regex.Replace(c.context, @"card: .*|potion.*", "...")).Select(g => g.Key + " x" + g.Count()))}");
            Console.WriteLine($"     host checkpoints without a recorded partner: {string.Join("; ", contexts.Select(kv => kv.Key + " x" + kv.Value))}");
            Console.WriteLine($"     game errors and warnings: {problems.Values.Sum()} in {problems.Count} kinds");
            foreach (var kv in problems.OrderByDescending(k => k.Value)) Console.WriteLine($"       {kv.Value,4}x {(kv.Key.Length > 330 ? kv.Key[..330] : kv.Key)}");
        }
        catch (Stages.StageFailed) { Stubs.ReportSkips(); return 1; }
        Stubs.ReportSkips();
        Stubs.Report("replay");
        return 0;
    }
}
