// Phase 7 simulator host, feasibility spike (P7.E1). Loads the game's assemblies from the install folder and runs
// game logic without the Godot engine, Steam or saves. Rules: docs/simulator-integrity.md.
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.Loader;

public static class Program
{
    public static string GameDir = "";

    public static int Main(string[] args)
    {
        System.Globalization.CultureInfo.DefaultThreadCurrentCulture = System.Globalization.CultureInfo.InvariantCulture;
        GameDir = Environment.GetEnvironmentVariable("STS2_DATA_DIR") ?? "";
        var home = Environment.GetEnvironmentVariable("HOME") ?? "";
        if (!File.Exists(Path.Combine(GameDir, "sts2.dll"))) { Console.Error.WriteLine("STS2_DATA_DIR does not hold sts2.dll"); return 2; }
        // SA-1: the host runs with HOME pointing at a sandbox, never at the real user folder that holds the game's saves.
        if (Directory.Exists(Path.Combine(home, "Library/Application Support/SlayTheSpire2")) || !home.Contains("sandbox"))
        { Console.Error.WriteLine("refusing to run: HOME must be a sandbox folder without game saves"); return 2; }
        AssemblyLoadContext.Default.Resolving += (ctx, name) =>
        {
            var p = Path.Combine(GameDir, name.Name + ".dll");
            return File.Exists(p) ? ctx.LoadFromAssemblyPath(p) : null;
        };
        var stage = args.Length > 0 ? args[0] : "info";
        try { return Stages.Run(stage, args.Skip(1).ToArray()); }
        catch (Exception e) { Console.WriteLine("EXCEPTION " + e.GetType().FullName + ": " + e.Message + "\n" + e.StackTrace); return 1; }
    }
}
