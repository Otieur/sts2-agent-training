// JSON-lines server for tools/sim.py (P7.E4.S5). One request per line on stdin; one reply per line on stdout, prefixed
// with "@@" so it cannot be confused with anything the game prints. Errors come back as {"ok": false, "error": ...};
// the process keeps running (EN-5).
//
// Requests: {"cmd":"load","path":..} · {"cmd":"reset","events":k,"seed":n|null} · {"cmd":"observe"} · {"cmd":"legal"}
//           {"cmd":"step","action":{..}} · {"cmd":"hidden"} (tests only) · {"cmd":"rollout","policy":"first"|"random","seed":n,"max_steps":m}
//           {"cmd":"resample","sample_seed":n} · {"cmd":"snapshot"} · {"cmd":"restore","id":k} · {"cmd":"stats"} · {"cmd":"quit"}
using System.Text.Json;
using System.Text.Json.Nodes;

public static class Serve
{
    static void Reply(JsonObject o) { Console.Out.WriteLine("@@" + o.ToJsonString()); Console.Out.Flush(); }

    public static int Run(string[] args)
    {
        try { Stages.Boot(false); Choices.Install(); Host.InstallStubs(); } catch (Stages.StageFailed) { return 1; }
        if (!args.Contains("log")) Stubs.CaptureLog();
        // debugging aid: SIM_DEBUG_NRE=1 prints the frames (with IL offsets) of every NullReferenceException to stderr
        if (Environment.GetEnvironmentVariable("SIM_DEBUG_NRE") == "1")
            AppDomain.CurrentDomain.FirstChanceException += (_, e) =>
            {
                if (e.Exception is not NullReferenceException) return;
                var st = new System.Diagnostics.StackTrace(e.Exception, false);
                Console.Error.WriteLine("NRE: " + string.Join(" <- ", st.GetFrames().Take(5).Select(f => $"{f.GetMethod()?.DeclaringType?.Name}.{f.GetMethod()?.Name}@IL{f.GetILOffset():X4}")));
            };
        var s = new Session();
        SynchronizationContext.SetSynchronizationContext(s.Ctx);
        var info = Path.Combine(Path.GetDirectoryName(Program.GameDir.TrimEnd('/'))!, "release_info.json");
        var build = File.Exists(info) ? JsonNode.Parse(File.ReadAllText(info)) : null;
        Reply(new JsonObject { ["ok"] = true, ["ready"] = true, ["game_version"] = (string)build?["version"], ["game_commit"] = (string)build?["commit"],
                               ["model_id_hash"] = MegaCrit.Sts2.Core.Multiplayer.Serialization.ModelIdSerializationCache.Hash });
        string line;
        long steps = 0, resets = 0;
        while ((line = Console.In.ReadLine()) != null)
        {
            if (line.Trim().Length == 0) continue;
            var reply = new JsonObject { ["ok"] = true };
            try
            {
                var req = JsonNode.Parse(line)!;
                switch ((string)req["cmd"])
                {
                    case "load":
                        s.Load((string)req["path"]);
                        // FI-3: refuse a recording from another build or with another model list
                        if (s.Replay.modelIdHash != MegaCrit.Sts2.Core.Multiplayer.Serialization.ModelIdSerializationCache.Hash)
                            throw new InvalidOperationException($"model-id hash differs: replay {s.Replay.modelIdHash}, host {MegaCrit.Sts2.Core.Multiplayer.Serialization.ModelIdSerializationCache.Hash}");
                        if (build != null && s.Replay.gitCommit != (string)build["commit"])
                            throw new InvalidOperationException($"game build differs: replay {s.Replay.gitCommit}, installed {(string)build["commit"]}");
                        reply["events"] = s.Replay.events.Count;
                        reply["version"] = s.Replay.version;
                        reply["commit"] = s.Replay.gitCommit;
                        break;
                    case "points":
                        if (s.Run == null) s.Reset(0, null);
                        reply["decision_points"] = new JsonArray(s.DecisionPoints().Select(i => (JsonNode)i).ToArray());
                        break;
                    case "reset":
                        s.Reset((int)req["events"], req["seed"] == null ? null : (ulong)req["seed"]);
                        resets++;
                        reply["obs"] = s.Observe();
                        reply["generators_reseeded"] = req["seed"] == null ? 0 : Sanitizer.LastCount;
                        break;
                    case "new_fight":
                        s.NewFight(req["spec"]!, (ulong)(req["sample_seed"]?.GetValue<long>() ?? 1L));
                        resets++;
                        reply["obs"] = s.Observe();
                        reply["generators_reseeded"] = Sanitizer.LastCount;
                        break;
                    case "new_run":
                        s.NewRun(req["spec"]!, (ulong)(req["sample_seed"]?.GetValue<long>() ?? 1L));
                        resets++;
                        reply["obs"] = s.RunObserve();
                        break;
                    case "run_legal": reply["actions"] = s.RunLegal(); break;
                    case "run_step":
                        s.RunStep(req["action"]!);
                        s.AfterRewardTaken();
                        steps++;
                        reply["obs"] = s.RunObserve();
                        break;
                    case "run_observe": reply["obs"] = s.RunObserve(); break;
                    case "coop_deliver_like":   // co-op runs: another seat acts the way the host just did (sim/CoopNet.cs)
                    {
                        if (s.Net == null) throw new InvalidOperationException("not a co-op run");
                        var fields = new Dictionary<string, object>();
                        foreach (var kv in (req["fields"] as JsonObject) ?? new JsonObject()) fields[kv.Key] = kv.Value!.GetValue<long>();
                        reply["handlers"] = s.Net.DeliverLike((string)req["type"], fields, (ulong)(req["from"]?.GetValue<long>() ?? 2L));
                        s.Ctx.Drain();
                        reply["obs"] = s.RunObserve();
                        break;
                    }
                    case "map": reply["map"] = s.MapView(); break;
                    case "debug_rng": reply["counters"] = s.DebugRngCounters(); break;   // fidelity tests only (FP-2)
                    case "move_to":
                        s.MoveTo((int)req["col"], (int)req["row"]);
                        steps++;
                        reply["obs"] = s.RunObserve();
                        break;
                    case "encounters":
                    {
                        // which act each encounter belongs to, from the game's default act list (1-based position)
                        var acts = new Dictionary<string, List<int>>();
                        var list = MegaCrit.Sts2.Core.Models.ActModel.GetDefaultList().ToList();
                        for (var i = 0; i < list.Count; i++)
                            foreach (var e in list[i].AllEncounters)
                                (acts.TryGetValue(e.Id.Entry, out var l) ? l : acts[e.Id.Entry] = new List<int>()).Add(i + 1);
                        reply["encounters"] = new JsonArray(MegaCrit.Sts2.Core.Models.ModelDb.AllEncounters
                            .Select(e => (JsonNode)new JsonObject { ["id"] = e.Id.Entry, ["room_type"] = e.RoomType.ToString(), ["weak"] = e.IsWeak,
                                ["acts"] = new JsonArray((acts.TryGetValue(e.Id.Entry, out var a) ? a : new List<int>()).Select(x => (JsonNode)x).ToArray()) }).ToArray());
                        break;
                    }
                    case "card_pool":   // the character's card pool as the game defines it (for generated fight specs)
                    {
                        var ch = MegaCrit.Sts2.Core.Models.ModelDb.AllCharacters.First(c => c.Id.Entry == ((string)req["character"] ?? "IRONCLAD"));
                        reply["cards"] = new JsonArray(ch.CardPool.AllCards.Select(c => (JsonNode)new JsonObject
                            { ["id"] = c.Id.Entry, ["rarity"] = c.Rarity.ToString(), ["type"] = c.Type.ToString() }).ToArray());
                        break;
                    }
                    case "observe": reply["obs"] = s.Observe(); break;
                    case "legal": reply["actions"] = s.Legal(); break;
                    case "step":
                    {
                        var errors = Stubs.ExceptionCount;
                        s.Step(req["action"]!);
                        s.NoteStep(req["action"]!);
                        steps++;
                        // a game exception the game caught and only logged (FI-7b): the step is reported as failed
                        if (Stubs.ExceptionCount != errors) throw new InvalidOperationException("game exception during the step: " + Stubs.LastException);
                        reply["obs"] = s.Observe();
                        break;
                    }
                    case "hidden": reply["hidden"] = s.Hidden(); break;   // tests only
                    case "resample":                                       // decision mode: a new sample of the hidden state
                        if (!s.Sanitized) throw new InvalidOperationException("resample works on a sanitized (decision-mode) state only");
                    {
                        var seed = (ulong)(req["sample_seed"]?.GetValue<long>() ?? 1L);
                        Sanitizer.Apply(s, seed);
                        s.NoteResample(seed);
                        reply["generators_reseeded"] = Sanitizer.LastCount;
                        break;
                    }
                    case "snapshot": reply["id"] = s.Snapshot(); break;          // P7.E4.S4: decision-mode fights only
                    case "restore":
                        s.Restore((int)req["id"]);
                        reply["obs"] = s.Observe();
                        reply["restore_ms"] = s.LastRestoreMs;
                        break;
                    case "selfcheck": reply["result"] = s.OwnActionsReplay(); break;
                    case "rollout":
                    {
                        var rng = new Random((int)(req["seed"] ?? 0));
                        var max = (int)(req["max_steps"] ?? 400);
                        var n = 0;
                        var errors = Stubs.ExceptionCount;
                        while (n < max && s.Status() == "in_progress" && !s.Blocked)
                        {
                            var acts = s.Legal();
                            if (acts.Count == 0) break;
                            var pick = (string)req["policy"] == "random" ? acts[rng.Next(acts.Count)]! : acts[0]!;
                            s.Step(pick);
                            s.NoteStep(pick);
                            n++; steps++;
                        }
                        reply["steps"] = n;
                        reply["game_exceptions"] = Stubs.ExceptionCount - errors;
                        if (Stubs.ExceptionCount != errors) reply["last_exception"] = Stubs.LastException;
                        reply["obs"] = s.Observe();
                        break;
                    }
                    case "diag":
                        reply["problems"] = new JsonArray(Stubs.Problems.TakeLast((int)(req["last"] ?? 6)).Select(x => (JsonNode)x).ToArray());
                        reply["last_action"] = s.LastAction();
                        if (req["clear"] != null) Stubs.Problems.Clear();
                        break;
                    case "export_fight":
                        reply["replay_b64"] = Convert.ToBase64String(s.ExportFight());
                        reply["events"] = s.LastExportEvents;
                        break;
                    case "fight_from_save":
                    {
                        var reader = new MegaCrit.Sts2.Core.Multiplayer.Serialization.PacketReader();
                        reader.Reset(Convert.FromBase64String((string)req["data"]!));
                        var rec = reader.Read<MegaCrit.Sts2.Core.Multiplayer.Replay.CombatReplay>();
                        s.FightFromSave(rec, req["actions"]?.AsArray() ?? new JsonArray(), (ulong)(req["sample_seed"]?.GetValue<long>() ?? 1L));
                        resets++;
                        reply["obs"] = s.Observe();
                        break;
                    }
                    case "load_b64":
                        s.LoadBytes(Convert.FromBase64String((string)req["data"]!));
                        if (s.Replay.modelIdHash != MegaCrit.Sts2.Core.Multiplayer.Serialization.ModelIdSerializationCache.Hash)
                            throw new InvalidOperationException("model-id hash differs from the host's");
                        reply["events"] = s.Replay.events.Count;
                        break;
                    case "stats":
                        reply["steps"] = steps; reply["resets"] = resets; reply["engine_calls"] = Stubs.TotalCalls;
                        reply["managed_mb"] = GC.GetTotalMemory(false) / 1048576; reply["sanitize_ms"] = Sanitizer.LastMs;
                        reply["draw_samples"] = DrawKnowledge.Samples; reply["draw_rejections"] = DrawKnowledge.Rejections;
                        reply["draw_fallbacks"] = DrawKnowledge.Fallbacks; reply["draw_last_fallback"] = DrawKnowledge.LastFallback;
                        reply["game_exceptions"] = Stubs.ExceptionCount;
                        reply["newfight_ms"] = new JsonObject(Session.NewFightMs.Select(kv => new KeyValuePair<string, JsonNode>(kv.Key, Math.Round(kv.Value, 2))));
                        reply["slow_waits"] = new JsonArray(s.Ctx.SlowWaits.TakeLast(10).Select(x => (JsonNode)x).ToArray());
                        break;
                    case "quit": Reply(reply); return 0;
                    default: throw new ArgumentException("unknown cmd");
                }
            }
            catch (Exception e)
            {
                var inner = e; while (inner.InnerException != null) inner = inner.InnerException;
                reply = new JsonObject { ["ok"] = false, ["error"] = inner.GetType().Name + ": " + inner.Message.Split('\n')[0],
                                         ["where"] = string.Join(" <- ", (inner.StackTrace ?? "").Split('\n').Take(4).Select(x => x.Trim())) };
            }
            Reply(reply);
        }
        return 0;
    }
}
