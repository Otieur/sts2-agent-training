// Shared preparation for every host mode: the stubs that replace saving, assets, text and UI (see Stubs.cs for the
// reasons each kind is logic-neutral, and docs/simulator-integrity.md FI-1b, FI-7, SA-1 to SA-4).
using MegaCrit.Sts2.Core.Runs;

public static class Host
{
    static bool _installed;

    public static void InstallStubs()
    {
        if (_installed) return;
        _installed = true;
        // UI first. Every later patch compiles a replacement method at patch time, and the JIT may inline small callees
        // into it; a UI method that is not yet inert would then run with its real body inside game logic. So the UI
        // classes (and the game's own scene-node classes) are made inert before any game-logic method is patched.
        Stages.Step("inert UI", () =>
        {
            var list = System.Text.Json.JsonSerializer.Deserialize<List<string>>(File.ReadAllText(Environment.GetEnvironmentVariable("SIM_UI_TYPES")!))!;
            var n = Stubs.MakeInertAll(list);
            Console.WriteLine($"     {n} UI classes (the {list.Count} listed and the UI classes they return) and {Stubs.GameNodeTypes} game scene-node classes inert: {Stubs.InertMethods} methods replaced, {Stubs.InertFailed} could not be; {Stubs.InstanceFieldsFilled} Instance fields filled ({string.Join(", ", Stubs.FilledNames)})");
        });
        Stages.Step("game-method stubs", () =>
        {
            var sm = typeof(MegaCrit.Sts2.Core.Saves.SaveManager);
            foreach (var m in new[] { "SaveRun", "SaveRunHistory", "SaveProgressFile", "SavePrefsFile", "SaveSettings", "SaveProfile" })
                Stubs.Skip(sm, m, "SA-1: the simulator never writes saves");
            Stubs.Skip(sm, "IncrementNumReloads", "SA-1: save bookkeeping when a saved run is set up (fight_from_save); the simulator never writes saves");
            Stubs.MakeInertHelper(typeof(MegaCrit.Sts2.Core.Assets.PreloadManager));  // assets only: preloads scenes and textures
            Stubs.MakeInertHelper(typeof(MegaCrit.Sts2.Core.Assets.AssetCache));       // assets only: loaded scenes and textures
            Stubs.Skip(typeof(RunManager), "WriteReplay", "SA-1: the game writes replays/latest.mcr into the save profile at the end of a fight and on clean-up");
            // Localised text is display and log text. The tables live in the game's resource pack, which only the
            // engine can read, so text lookups return an empty string.
            foreach (var m in new[] { "GetFormattedText", "GetRawText" })
                Stubs.Skip(typeof(MegaCrit.Sts2.Core.Localization.LocString), m, "display and log text only");
            Stubs.MakeInertHelper(typeof(MegaCrit.Sts2.Core.Helpers.GodotTreeExtensions));
            Console.WriteLine($"     {Stubs.NullEngineResources(sm.Assembly)} game methods returning engine resources (textures, scenes) answer null");
            Console.WriteLine($"     {Stubs.EmptyHoverTips(sm.Assembly)} hover-tip getters answer empty");
            Console.WriteLine($"     {Stubs.ForceDisplayFlags(sm.Assembly)} game commands run with previews, visuals, animation and sound off");
            Stubs.MakeInertHelper(typeof(MegaCrit.Sts2.Core.Commands.VfxCmd));   // visual effects only
            Stubs.MakeInertHelper(typeof(MegaCrit.Sts2.Core.Commands.SfxCmd));   // sound effects only
            // Speech bubbles are display only.
            Stubs.MakeInertHelper(typeof(MegaCrit.Sts2.Core.Commands.TalkCmd));
            // The game reads preferences and settings from files in the save folder. The host gives it default objects
            // of its own, with the Instant speed so no logic waits on a display timer.
            var prefs = new MegaCrit.Sts2.Core.Saves.PrefsSave { FastMode = MegaCrit.Sts2.Core.Settings.FastModeType.Instant };
            Stubs.Return(sm, "get_PrefsSave", prefs, "preferences object owned by the host (no file)");
            Stubs.Return(sm, "get_SettingsSave", Activator.CreateInstance(typeof(MegaCrit.Sts2.Core.Saves.SettingsSave), true), "settings object owned by the host (no file)");
            // End of a run (SA-1 to SA-4): no telemetry upload, no achievements or Steam stats, no daily score, no
            // run history, no progress update, and above all no deletion of the current-run save file.
            foreach (var name in new[] { "MegaCrit.Sts2.Core.Runs.Metrics.MetricUtilities", "MegaCrit.Sts2.Core.Achievements.AchievementsHelper",
                                         "MegaCrit.Sts2.Core.Platform.StatsManager", "MegaCrit.Sts2.Core.Daily.DailyRunUtility",
                                         "MegaCrit.Sts2.Core.Debug.SentryService", "MegaCrit.Sts2.Core.Runs.RunHistoryUtilities" })
                Stubs.MakeInertHelper(sm.Assembly.GetType(name)!);
            foreach (var m in new[] { "UpdateProgressWithRunData", "BeginSaveBatch", "DeleteCurrentRun", "DeleteCurrentMultiplayerRun" })
                Stubs.Skip(sm, m, "SA-1: no progress update and no save-file deletion");
            Stubs.Skip(typeof(RunManager), "UpdateRichPresence", "SA-2: no Steam rich presence");
            Stubs.Skip(typeof(MegaCrit.Sts2.Core.Saves.Managers.ProgressSaveManager), "SaveProgress", "SA-1: no progress file");
            // Display-only methods inside monster and power classes, found by the encounter sweep (reports/phase7/encounter-sweep.md).
            var asm = sm.Assembly;
            foreach (var (type, method, why) in new[] {
                ("MegaCrit.Sts2.Core.Models.Powers.SandpitPower", "UpdateCreaturePositions", "moves creature sprites"),
                ("MegaCrit.Sts2.Core.Models.Powers.SandpitPower", "AfterRemoved", "moves creature sprites back (tweens only)"),
                ("MegaCrit.Sts2.Core.Models.Monsters.DecimillipedeSegment", "AnimSegmentsAttack", "attack animation"),
                ("MegaCrit.Sts2.Core.Models.Monsters.FakeMerchantMonster", "ShowDialogueForMove", "dialogue bubble"),
                // reached only when a creature node exists; its one logic call, MonsterModel.OnDieToDoom, is empty in the
                // base class and visuals-only in its one override (TorchHeadAmalgam); the kill itself is CreatureCmd.Kill in DoomKill
                ("MegaCrit.Sts2.Core.Models.Powers.DoomPower", "StartDoomAnim", "Doom death animation"),
                // instantiates an effect scene on the event portrait; no random generator or game state involved
                ("MegaCrit.Sts2.Core.Models.Events.Trial", "AddVfxAnchoredToPortrait", "effect on the event portrait") })
                Stubs.Skip(asm.GetType(type)!, method, "display only: " + why);
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
            // One power drives its damage from a visual effect's signal outside the test path: Rolling Boulder creates
            // the boulder effect, deals damage to each creature in the effect's hit callback and awaits the effect's end
            // signal. The inert effect never signals, so the turn would hang (found 2026-11-20: every rollout of a deck
            // with Rolling Boulder stuck at the next turn start). Its test path deals the same damage to all hittable
            // enemies at once, then grows the power the same way; the order of the hits within the call may differ.
            // The call graph lists no other model logic that awaits a Godot signal (only CombatState.GodotTimerTask,
            // which checks TestMode itself).
            Stubs.TestPath(asm.GetType("MegaCrit.Sts2.Core.Models.Powers.RollingBoulderPower")!, "AfterPlayerTurnStart",
                           "damage is dealt in the inert boulder effect's signal callback outside the test path");
        });
        // Raw real-time pauses inside game logic (not the game's own Cmd.Wait, which fast mode skips). The call graph
        // finds them only in the Amalgamator event's two options (between the sound cues of combining cards); the host
        // does not wait in real time, so the option would stay unfinished. The pauses complete at once instead.
        // Like every patch, after the inert UI step (a UI method not yet inert would be inlined into the rewritten method
        // with its real body: NGame.ScreenShakeTrauma).
        // Observers of the draw pile for the decision-mode sampler (FP-5); the inserts they wrap run unchanged.
        Stages.Step("known draw-pile positions", DrawKnowledge.Install);
        Stages.Step("no real-time pauses in game logic", () =>
            NoRealTimeDelays(typeof(MegaCrit.Sts2.Core.Models.EventModel).Assembly.GetType("MegaCrit.Sts2.Core.Models.Events.Amalgamator")!, "CombineStrikes", "CombineDefends"));
    }

    // Replaces Task.Delay calls inside the async methods named (their compiler-generated state machines) with a task
    // that is already complete. Fails loudly when a named method has no such call, so a game update cannot hide it.
    static void NoRealTimeDelays(Type owner, params string[] asyncMethods)
    {
        var transpiler = new HarmonyLib.HarmonyMethod(typeof(Host).GetMethod(nameof(DelayTranspiler), System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic));
        foreach (var name in asyncMethods)
        {
            var sm = owner.GetNestedTypes(System.Reflection.BindingFlags.NonPublic).SingleOrDefault(t => t.Name.StartsWith("<" + name + ">"))
                     ?? throw new MissingMethodException(owner.FullName, name);
            var moveNext = sm.GetMethod("MoveNext", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public)!;
            _replaced = 0;
            Stubs.H.Patch(moveNext, transpiler: transpiler);
            if (_replaced == 0) throw new InvalidOperationException($"{owner.Name}.{name} has no Task.Delay call to replace (game changed?)");
        }
    }

    static int _replaced;

    static IEnumerable<HarmonyLib.CodeInstruction> DelayTranspiler(IEnumerable<HarmonyLib.CodeInstruction> code)
    {
        foreach (var ins in code)
        {
            if (ins.operand is System.Reflection.MethodInfo m && m.DeclaringType == typeof(Task) && m.Name == "Delay")
            {
                var replacement = typeof(Host).GetMethod(nameof(NoDelay), m.GetParameters().Select(p => p.ParameterType).ToArray())
                                  ?? throw new MissingMethodException("Host.NoDelay for " + m);
                ins.operand = replacement;
                _replaced++;
            }
            yield return ins;
        }
    }

    public static Task NoDelay(int ms) => Task.CompletedTask;
    public static Task NoDelay(TimeSpan t) => Task.CompletedTask;
    public static Task NoDelay(int ms, CancellationToken c) => Task.CompletedTask;
    public static Task NoDelay(TimeSpan t, CancellationToken c) => Task.CompletedTask;
}
