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
        Stages.Step("game-method stubs", () =>
        {
            var sm = typeof(MegaCrit.Sts2.Core.Saves.SaveManager);
            foreach (var m in new[] { "SaveRun", "SaveRunHistory", "SaveProgressFile", "SavePrefsFile", "SaveSettings", "SaveProfile" })
                Stubs.Skip(sm, m, "SA-1: the simulator never writes saves");
            Stubs.MakeInertHelper(typeof(MegaCrit.Sts2.Core.Assets.PreloadManager));   // assets only: preloads scenes and textures
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
                ("MegaCrit.Sts2.Core.Models.Monsters.FakeMerchantMonster", "ShowDialogueForMove", "dialogue bubble") })
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
        });
        Stages.Step("inert UI", () =>
        {
            var list = System.Text.Json.JsonSerializer.Deserialize<List<string>>(File.ReadAllText(Environment.GetEnvironmentVariable("SIM_UI_TYPES")!))!;
            var n = Stubs.MakeInertAll(list);
            Console.WriteLine($"     {n} UI classes inert: {Stubs.InertMethods} methods replaced, {Stubs.InertFailed} could not be");
        });
    }
}
