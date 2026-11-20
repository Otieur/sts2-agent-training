using System.Reflection;
using System.Runtime.CompilerServices;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.TestSupport;

public static class Stages
{
    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int Run(string stage, string[] args)
    {
        switch (stage)
        {
            case "info": return Info();
            case "sig": return Sig(args);
            case "modeldb": return ModelDbStage(args);
            case "replay": return Replay.Run(args);
            default: Console.Error.WriteLine("unknown stage " + stage); return 2;
        }
    }

    // Prints the signatures of a type's members (declared only): sim/run.sh sig <full type name> [name filter]
    static int Sig(string[] args)
    {
        var t = typeof(TestMode).Assembly.GetType(args[0]) ?? typeof(Godot.Node).Assembly.GetType(args[0]);
        if (t == null) { Console.WriteLine("type not found"); return 1; }
        var flags = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance | BindingFlags.DeclaredOnly;
        string N(Type x) => x.IsGenericType ? x.Name.Split('`')[0] + "<" + string.Join(",", x.GetGenericArguments().Select(N)) + ">" : x.Name;
        foreach (var m in t.GetMembers(flags))
        {
            if (args.Length > 1 && !m.Name.Contains(args[1], StringComparison.OrdinalIgnoreCase)) continue;
            if (m.Name.StartsWith("<")) continue;
            switch (m)
            {
                case MethodBase mb:
                    var ret = mb is MethodInfo mi ? N(mi.ReturnType) + " " : "";
                    Console.WriteLine($"{(mb.IsStatic ? "static " : "")}{(mb.IsPublic ? "public " : "nonpublic ")}{ret}{mb.Name}({string.Join(", ", mb.GetParameters().Select(p => N(p.ParameterType) + " " + p.Name))})");
                    break;
                case FieldInfo f: Console.WriteLine($"{(f.IsStatic ? "static " : "")}field {N(f.FieldType)} {f.Name}"); break;
                case PropertyInfo pr: Console.WriteLine($"prop {N(pr.PropertyType)} {pr.Name}"); break;
            }
        }
        return 0;
    }

    public static void Step(string name, Action a)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        try { a(); Console.WriteLine($"ok   {name} ({sw.ElapsedMilliseconds} ms)"); }
        catch (Exception e)
        {
            var inner = e; while (inner.InnerException != null) inner = inner.InnerException;
            Console.WriteLine($"FAIL {name}: {inner.GetType().Name}: {inner.Message}");
            Console.WriteLine(string.Join("\n", (inner.StackTrace ?? "").Split('\n').Take(8)));
            throw new StageFailed();
        }
    }

    public class StageFailed : Exception { }

    // Starts the game's model database without the engine (P7.E1.S2). TestMode stays off (FI-1); waits are skipped
    // through NonInteractiveMode (FI-2b).
    public static void Boot(bool loc)
    {
        Step("NonInteractiveMode on", () => { NonInteractiveMode.AutoSlayerCheck = () => true; if (TestMode.IsOn) throw new Exception("TestMode is on"); });
        Step("fake engine", () => Console.WriteLine($"     {Stubs.InstallFakeEngine()} engine functions replaced by recording stubs"));
        Step("engine singletons", () => Console.WriteLine($"     {Stubs.InstallSingletons()} singleton placeholders"));
        if (loc) Step("LocManager.Initialize", () => MegaCrit.Sts2.Core.Localization.LocManager.Initialize());
        // No mods in the simulator: mark the mod manager as finished with an empty mod list (the real initialiser reads
        // settings and scans the mods folder through the engine).
        Step("ModManager state", () =>
        {
            var mm = typeof(MegaCrit.Sts2.Core.Modding.ModManager);
            var state = mm.GetProperty("State", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic)!;
            var values = Enum.GetValues(state.PropertyType);
            state.SetValue(null, values.GetValue(values.Length - 1));
            Console.WriteLine($"     ModManager.State = {state.GetValue(null)}");
        });
        Step("AssemblyInfo.Init", () => MegaCrit.Sts2.Core.Modding.AssemblyInfo.Init());
        Step("ModelDb.Init", () => MegaCrit.Sts2.Core.Models.ModelDb.Init(null));
        Step("ModelIdSerializationCache.Init", () => MegaCrit.Sts2.Core.Multiplayer.Serialization.ModelIdSerializationCache.Init());
        Step("ModelDb.InitIds", () => MegaCrit.Sts2.Core.Models.ModelDb.InitIds());
        Step("MessageTypes.Initialize", () => MegaCrit.Sts2.Core.Multiplayer.Serialization.MessageTypes.Initialize());
        Step("ActionTypes.Initialize", () => MegaCrit.Sts2.Core.GameActions.Multiplayer.ActionTypes.Initialize());
    }

    static int ModelDbStage(string[] args)
    {
        try { Boot(args.Contains("loc")); } catch (StageFailed) { return 1; }
        Console.WriteLine($"model-id hash {MegaCrit.Sts2.Core.Multiplayer.Serialization.ModelIdSerializationCache.Hash}");
        var all = MegaCrit.Sts2.Core.Models.ModelDb.All.ToList();
        Console.WriteLine($"models {all.Count}: " + string.Join(", ", all.GroupBy(m => m.Id.Category).OrderByDescending(g => g.Count()).Select(g => g.Key + " " + g.Count())));
        Stubs.Report("start-up");
        return 0;
    }

    static int Info()
    {
        var asm = typeof(TestMode).Assembly;
        Console.WriteLine($"runtime {Environment.Version}; sts2 {asm.GetName().Version}; types {asm.GetTypes().Length}");
        Console.WriteLine($"TestMode.IsOn={TestMode.IsOn} NonInteractive={NonInteractiveMode.IsActive}");
        var info = Path.Combine(Path.GetDirectoryName(Program.GameDir.TrimEnd('/'))!, "release_info.json");
        Console.WriteLine(File.Exists(info) ? File.ReadAllText(info).Replace("\n", " ") : "no release_info.json");
        return 0;
    }
}
