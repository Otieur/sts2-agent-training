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
    }
}
