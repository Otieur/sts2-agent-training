// Engine-call handling for the simulator host (P7.E3.S2, integrity rule FI-7).
//
// GodotSharp reaches the engine only through Godot.NativeInterop.NativeFuncs: a table of 225 function pointers that the
// engine fills in at start-up (NativeFuncs.Initialize). Without the engine the table is empty and any call kills the
// process. The fake engine below fills the table with our own stubs: each returns zero and records which function was
// called and from where, so every engine call the game logic makes can be listed, judged and, where it matters, given a
// real answer. No Godot code runs; nothing is rendered, loaded or saved through the engine.
using System.Reflection;
using System.Runtime.InteropServices;

public static class Stubs
{
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    delegate IntPtr NativeStub();

    public class Hit { public string Name = ""; public long Count; public string FirstStack = ""; }

    public static readonly List<Hit> Slots = new();
    static readonly List<Delegate> KeepAlive = new();
    public static bool RecordStacks = true;
    public static long TotalCalls;

    public static int InstallFakeEngine()
    {
        var nf = typeof(Godot.GodotObject).Assembly.GetType("Godot.NativeInterop.NativeFuncs")!;
        var table = nf.GetNestedType("UnmanagedCallbacks", BindingFlags.NonPublic | BindingFlags.Public)!;
        var fields = table.GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
        var size = fields.Length * IntPtr.Size;
        var mem = Marshal.AllocHGlobal(size);
        var ctorStub = new NativeStub(FakeObject);
        KeepAlive.Add(ctorStub);
        var ctorPtr = Marshal.GetFunctionPointerForDelegate(ctorStub);
        var dummy = Marshal.AllocHGlobal(256);
        for (var i = 0; i < fields.Length; i++)
        {
            var hit = new Hit { Name = fields[i].Name };
            Slots.Add(hit);
            // The constructor lookup must return a callable pointer: GodotObject's constructor calls what it returns.
            // Method lookups must return a non-null handle too (GodotSharp throws on null); the handle is only ever
            // passed back to the call stubs, which ignore it.
            NativeStub d = hit.Name == "godotsharp_get_class_constructor" ? () => { Record(hit); return ctorPtr; }
                : hit.Name.StartsWith("godotsharp_method_bind_get_method") ? () => { Record(hit); return dummy; }
                : () => { Record(hit); return IntPtr.Zero; };
            KeepAlive.Add(d);
            Marshal.WriteIntPtr(mem, i * IntPtr.Size, Marshal.GetFunctionPointerForDelegate(d));
        }
        nf.GetMethod("Initialize", BindingFlags.Static | BindingFlags.Public)!.Invoke(null, new object[] { mem, size });
        return fields.Length;
    }

    static IntPtr FakeObject() => Marshal.AllocHGlobal(256);  // a dummy native object handle; never dereferenced by us

    // Godot singletons (OS, Engine, Time, ...): each static class caches a wrapper object in a private static field
    // named "singleton". Without the engine the lookup returns null and every call on the singleton throws. We place an
    // uninitialised wrapper with a dummy native handle there, so calls reach the recording stubs and return zeros.
    public static int InstallSingletons()
    {
        var n = 0;
        var nativePtr = typeof(Godot.GodotObject).GetField("NativePtr", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
        foreach (var t in typeof(Godot.GodotObject).Assembly.GetTypes())
        {
            var f = t.GetField("singleton", BindingFlags.Static | BindingFlags.NonPublic);
            var prop = t.GetProperty("Singleton", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
            if (f == null || prop == null || !typeof(Godot.GodotObject).IsAssignableFrom(prop.PropertyType) || prop.PropertyType.IsAbstract) continue;
            var obj = System.Runtime.CompilerServices.RuntimeHelpers.GetUninitializedObject(prop.PropertyType);
            nativePtr!.SetValue(obj, Marshal.AllocHGlobal(256));
            GC.SuppressFinalize(obj);
            KeepAliveObjects.Add(obj);
            f.SetValue(null, obj);
            n++;
        }
        return n;
    }

    static readonly List<object> KeepAliveObjects = new();

    static void Record(Hit hit)
    {
        TotalCalls++;
        if (hit.Count++ == 0 && RecordStacks)
            hit.FirstStack = string.Join(" <- ", new System.Diagnostics.StackTrace(2, false).GetFrames()
                .Select(f => f.GetMethod()).Where(m => m != null && m.DeclaringType != null)
                .Select(m => (m!.DeclaringType!.FullName ?? "").Replace("MegaCrit.Sts2.Core.", "") + "." + m.Name)
                .Where(s => !s.StartsWith("Stubs") && !s.StartsWith("Stages") && !s.StartsWith("Program") && !s.StartsWith("System.")).Take(7));
    }

    // ---- Game-method stubs (Harmony, bundled with the game). Each entry must be logic-neutral: UI, audio, saving,
    // achievements or telemetry only (docs/simulator-integrity.md FI-7, SA-1 to SA-4). The reason is recorded and printed.
    public static readonly HarmonyLib.Harmony H = new("sim.host");
    public static readonly Dictionary<string, long> Skipped = new();
    static readonly List<(string, string)> SkipList = new();

    public static void Skip(Type type, string method, string reason)
    {
        var flags = BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
        var targets = type.GetMethods(flags).Where(m => m.Name == method).ToList();
        if (targets.Count == 0) throw new MissingMethodException(type.FullName, method);
        foreach (var m in targets)
        {
            // void and Task are counted; other return types get the inert value (zero, "", null or an inert UI object)
            var name = m.ReturnType == typeof(void) ? nameof(SkipVoid) : m.ReturnType == typeof(Task) ? nameof(SkipTask)
                     : m.ReturnType.IsValueType ? nameof(InertDefault) : nameof(InertRef);
            H.Patch(m, prefix: new HarmonyLib.HarmonyMethod(typeof(Stubs).GetMethod(name, BindingFlags.Static | BindingFlags.NonPublic)));
        }
        SkipList.Add(($"{type.Name}.{method}", reason));
    }

    static bool SkipVoid(MethodBase __originalMethod) { Count(__originalMethod); return false; }
    static bool SkipTrue(MethodBase __originalMethod, ref bool __result) { Count(__originalMethod); __result = true; return false; }

    public static void AnswerTrue(Type type, string method, string reason)
    {
        var flags = BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
        foreach (var m in type.GetMethods(flags).Where(m => m.Name == method && m.ReturnType == typeof(bool)))
            H.Patch(m, prefix: new HarmonyLib.HarmonyMethod(typeof(Stubs).GetMethod(nameof(SkipTrue), BindingFlags.Static | BindingFlags.NonPublic)));
        SkipList.Add(($"{type.Name}.{method}", reason));
    }
    static bool SkipTask(MethodBase __originalMethod, ref Task __result) { Count(__originalMethod); __result = Task.CompletedTask; return false; }
    static void Count(MethodBase m) { var k = m.DeclaringType!.Name + "." + m.Name; Skipped[k] = Skipped.GetValueOrDefault(k) + 1; }

    // ---- Inert UI. Game logic calls 165 UI classes (MegaCrit.Sts2.Core.Nodes.*) directly: scene nodes, screens, audio
    // and effects. In the host none of them exists. Every method of those classes is replaced by one that does nothing
    // and returns an empty value: zero, a completed task, or an inert instance when the return type is itself a UI
    // class. Their static Instance getters therefore return inert objects instead of null. This is logic-neutral only
    // if no game rule lives in a UI class; the checksum comparison against recorded fights is the test of that (FI-12).
    static readonly Dictionary<Type, object> Inert = new();
    static readonly HashSet<Type> InertTypes = new();
    static readonly HashSet<MethodBase> Patched = new();
    public static int InertMethods, InertFailed;
    public static long InertCalls;
    static readonly FieldInfo NativePtrField = typeof(Godot.GodotObject).GetField("NativePtr", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public)!;

    // One UI namespace is spelled with a lower-case "sts2" in the game (MegaCrit.sts2.Core.Nodes.TopBar).
    // A method another part of the host patches itself (so making its class inert must leave it alone).
    public static void Reserve(MethodBase m) => Patched.Add(m);

    static bool IsUi(Type t) => t?.Namespace != null && (t.Namespace.StartsWith("MegaCrit.Sts2.Core.Nodes", StringComparison.OrdinalIgnoreCase)
                                                        || t.Namespace.StartsWith("MegaCrit.Sts2.addons", StringComparison.OrdinalIgnoreCase));

    public static object InertInstance(Type t)
    {
        if (Inert.TryGetValue(t, out var o)) return o;
        if (t.IsAbstract || t.IsInterface || t.ContainsGenericParameters) return null;
        o = System.Runtime.CompilerServices.RuntimeHelpers.GetUninitializedObject(t);
        if (typeof(Godot.GodotObject).IsAssignableFrom(t)) { NativePtrField.SetValue(o, Marshal.AllocHGlobal(256)); GC.SuppressFinalize(o); }
        Inert[t] = o;
        MakeInert(t);
        return o;
    }

    public static void MakeInert(Type t)
    {
        var flags = BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
        var skipDefault = new HarmonyLib.HarmonyMethod(typeof(Stubs).GetMethod(nameof(InertDefault), BindingFlags.Static | BindingFlags.NonPublic));
        var skipRef = new HarmonyLib.HarmonyMethod(typeof(Stubs).GetMethod(nameof(InertRef), BindingFlags.Static | BindingFlags.NonPublic));
        for (var x = t; x != null && IsUi(x); x = x.BaseType)
        {
            if (!InertTypes.Add(x)) break;
            foreach (var m in x.GetMethods(flags))
            {
                if (m.IsAbstract || m.ContainsGenericParameters || m.GetMethodBody() == null || !Patched.Add(m)) continue;
                try { H.Patch(m, prefix: m.ReturnType == typeof(void) || m.ReturnType.IsValueType || m.ReturnType.IsByRef || m.ReturnType.IsPointer ? skipDefault : skipRef); InertMethods++; }
                catch { InertFailed++; }
            }
        }
    }

    static bool InertDefault() { InertCalls++; return false; }

    static bool InertRef(MethodBase __originalMethod, ref object __result)
    {
        InertCalls++;
        // Lookups answer "not found", as they would with no nodes on screen; everything else gets an inert value.
        var n = __originalMethod.Name;
        __result = n.StartsWith("Find") || n.StartsWith("TryGet") || n.Contains("OrNull") ? null : InertValue(((MethodInfo)__originalMethod).ReturnType);
        return false;
    }

    // UI helper classes that live outside the UI namespaces (extension methods on scene nodes).
    public static void MakeInertHelper(Type t)
    {
        var flags = BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
        var skipDefault = new HarmonyLib.HarmonyMethod(typeof(Stubs).GetMethod(nameof(InertDefault), BindingFlags.Static | BindingFlags.NonPublic));
        var skipRef = new HarmonyLib.HarmonyMethod(typeof(Stubs).GetMethod(nameof(InertRef), BindingFlags.Static | BindingFlags.NonPublic));
        InertTypes.Add(t);
        foreach (var m in t.GetMethods(flags))
        {
            if (m.IsAbstract || m.ContainsGenericParameters || m.GetMethodBody() == null || !Patched.Add(m)) continue;
            try { H.Patch(m, prefix: m.ReturnType == typeof(void) || m.ReturnType.IsValueType ? skipDefault : skipRef); InertMethods++; } catch { InertFailed++; }
        }
    }

    static readonly MethodInfo FromResult = typeof(Task).GetMethod(nameof(Task.FromResult))!;

    static object InertValue(Type rt)
    {
        if (rt == typeof(Task)) return Task.CompletedTask;
        if (rt.IsGenericType && rt.GetGenericTypeDefinition() == typeof(Task<>))
        {
            var a = rt.GetGenericArguments()[0];
            return FromResult.MakeGenericMethod(a).Invoke(null, new[] { a.IsValueType ? Activator.CreateInstance(a) : InertValue(a) });
        }
        if (rt == typeof(string)) return "";
        return IsUi(rt) ? InertInstance(rt) : null;
    }

    // Makes inert every UI class in the list (tools: data/asm/ui-types-from-logic.json, built from the call graph).
    public static int MakeInertAll(IEnumerable<string> typeNames)
    {
        var asm = typeof(MegaCrit.Sts2.Core.TestSupport.TestMode).Assembly;
        var n = 0;
        foreach (var name in typeNames)
        {
            var t = asm.GetType(name);
            if (t == null || !IsUi(t)) continue;
            MakeInert(t);
            n++;
        }
        return n;
    }

    // ---- Scoped test path. A few display helpers in game-logic classes check TestMode themselves and skip their
    // visuals when it is on (the developers' own headless path). TestMode must never be on globally (FI-1: 107 logic
    // methods read it). For the helpers listed by the host, the flag is switched on only for the duration of that one
    // call and restored after it, so the helper takes the game's own no-visuals branch and nothing else sees the flag.
    static readonly List<(string, string)> TestPathList = new();
    public static long TestPathCalls;

    public static void TestPath(Type type, string method, string reason)
    {
        var flags = BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
        var targets = type.GetMethods(flags).Where(m => m.Name == method).ToList();
        if (targets.Count == 0) throw new MissingMethodException(type.FullName, method);
        foreach (var m in targets)
            H.Patch(m, prefix: new HarmonyLib.HarmonyMethod(typeof(Stubs).GetMethod(nameof(TestOn), BindingFlags.Static | BindingFlags.NonPublic)),
                    finalizer: new HarmonyLib.HarmonyMethod(typeof(Stubs).GetMethod(nameof(TestOff), BindingFlags.Static | BindingFlags.NonPublic)));
        TestPathList.Add(($"{type.Name}.{method}", reason));
    }

    static void TestOn(out bool __state) { TestPathCalls++; __state = MegaCrit.Sts2.Core.TestSupport.TestMode.IsOn; MegaCrit.Sts2.Core.TestSupport.TestMode.IsOn = true; }
    static void TestOff(bool __state) { MegaCrit.Sts2.Core.TestSupport.TestMode.IsOn = __state; }

    // ---- Game log capture. Printing a log line goes to an engine stub and costs time, so the host drops log output.
    // Errors and warnings are kept (deduplicated, newest last) because they name the display code or prompt that an
    // unfinished action is stuck on.
    public static readonly List<string> Problems = new();
    static readonly HashSet<string> ProblemSet = new();

    public static void CaptureLog()
    {
        var flags = BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
        var prefix = new HarmonyLib.HarmonyMethod(typeof(Stubs).GetMethod(nameof(LogPrefix), BindingFlags.Static | BindingFlags.NonPublic));
        foreach (var m in typeof(MegaCrit.Sts2.Core.Logging.Logger).GetMethods(flags).Where(m => m.Name == "LogMessage")) H.Patch(m, prefix: prefix);
    }

    static bool LogPrefix(object[] __args)
    {
        var level = __args.FirstOrDefault(a => a is Enum)?.ToString() ?? "";
        if (level is "Error" or "Warn")
        {
            var text = __args.OfType<string>().FirstOrDefault() ?? "";
            var key = level + ": " + string.Join(" | ", text.Split('\n').Take(4).Select(l => l.Trim())).Replace("MegaCrit.Sts2.Core.", "");
            if (key.Length > 420) key = key[..420];
            if (ProblemSet.Add(key)) { Problems.Add(key); if (Problems.Count > 200) { ProblemSet.Remove(Problems[0]); Problems.RemoveAt(0); } }
        }
        return false;
    }

    // A getter answered with a fixed object the host owns (preferences and settings that the game reads from files).
    static readonly Dictionary<MethodBase, object> Fixed = new();

    public static void Return(Type type, string method, object value, string reason)
    {
        var flags = BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
        foreach (var m in type.GetMethods(flags).Where(m => m.Name == method))
        {
            Fixed[m] = value;
            H.Patch(m, prefix: new HarmonyLib.HarmonyMethod(typeof(Stubs).GetMethod(nameof(FixedPrefix), BindingFlags.Static | BindingFlags.NonPublic)));
        }
        SkipList.Add(($"{type.Name}.{method}", reason));
    }

    static bool FixedPrefix(MethodBase __originalMethod, ref object __result) { __result = Fixed[__originalMethod]; return false; }

    // Every game-logic method that returns an engine resource (a texture, scene, material, font ...) answers null. Those
    // resources only feed icons, hover tips and scenes; loading them needs the engine. Returns the number of methods.
    public static int NullEngineResources(Assembly asm)
    {
        var flags = BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
        var prefix = new HarmonyLib.HarmonyMethod(typeof(Stubs).GetMethod(nameof(NullResource), BindingFlags.Static | BindingFlags.NonPublic));
        var n = 0;
        foreach (var type in asm.GetTypes())
        {
            if (IsUi(type) || type.Namespace == null || !type.Namespace.StartsWith("MegaCrit.Sts2.Core")) continue;
            foreach (var m in type.GetMethods(flags))
            {
                if (m.IsAbstract || m.ContainsGenericParameters || m.GetMethodBody() == null || Patched.Contains(m)) continue;
                if (!typeof(Godot.Resource).IsAssignableFrom(m.ReturnType)) continue;
                try { H.Patch(m, prefix: prefix); Patched.Add(m); n++; } catch { InertFailed++; }
            }
        }
        return n;
    }

    static bool NullResource(ref object __result) { __result = null; return false; }

    // Hover tips (the text boxes shown when the mouse is over a card, relic or power) are display only. Every getter of
    // them answers an empty list; a single tip answers its default value.
    static readonly Dictionary<MethodBase, object> EmptyValue = new();

    public static int EmptyHoverTips(Assembly asm)
    {
        var flags = BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
        var prefix = new HarmonyLib.HarmonyMethod(typeof(Stubs).GetMethod(nameof(EmptyPrefix), BindingFlags.Static | BindingFlags.NonPublic));
        var n = 0;
        foreach (var type in asm.GetTypes())
        {
            if (IsUi(type) || type.Namespace == null || !type.Namespace.StartsWith("MegaCrit.Sts2.Core")) continue;
            foreach (var m in type.GetMethods(flags))
            {
                if (!m.Name.StartsWith("get_") || !m.Name.Contains("HoverTip") || m.IsAbstract || m.ContainsGenericParameters || m.GetMethodBody() == null || Patched.Contains(m)) continue;
                var rt = m.ReturnType;
                object value = null;
                var en = rt.IsGenericType && rt.GetGenericTypeDefinition() == typeof(IEnumerable<>) ? rt.GetGenericArguments()[0]
                       : rt.GetInterfaces().FirstOrDefault(i => i.IsGenericType && i.GetGenericTypeDefinition() == typeof(IEnumerable<>))?.GetGenericArguments()[0];
                if (rt == typeof(string)) value = "";
                else if (en != null && rt.IsAssignableFrom(en.MakeArrayType())) value = Array.CreateInstance(en, 0);
                else if (rt.IsValueType) value = Activator.CreateInstance(rt);
                else if (en != null) continue;   // a collection type an empty array cannot stand for: leave it
                EmptyValue[m] = value;
                try { H.Patch(m, prefix: prefix); Patched.Add(m); n++; } catch { InertFailed++; }
            }
        }
        return n;
    }

    static bool EmptyPrefix(MethodBase __originalMethod, ref object __result) { __result = EmptyValue[__originalMethod]; return false; }

    public static void ReportSkips()
    {
        Console.WriteLine($"-- game methods stubbed: {SkipList.Count}");
        foreach (var (name, reason) in SkipList) Console.WriteLine($"   {Skipped.GetValueOrDefault(name),6}x  {name}: {reason}");
        Console.WriteLine($"-- display helpers run on the game's own test path ({TestPathCalls} calls): {string.Join(", ", TestPathList.Select(x => x.Item1))}");
        Console.WriteLine($"-- inert UI: {InertMethods} methods of {InertTypes.Count} classes; {InertCalls} calls");
    }

    public static void Report(string title)
    {
        Console.WriteLine($"-- engine calls ({title}): {TotalCalls} calls to {Slots.Count(s => s.Count > 0)} of {Slots.Count} functions");
        foreach (var s in Slots.Where(s => s.Count > 0).OrderByDescending(s => s.Count))
            Console.WriteLine($"   {s.Count,7}  {s.Name}\n            first: {s.FirstStack}");
    }
}
