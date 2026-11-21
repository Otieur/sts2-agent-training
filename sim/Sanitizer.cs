// State sanitizer (docs/simulator-integrity.md FP-2, FP-5, FP-15). After a fight has been rebuilt up to the present
// with its true random state, this removes everything about the future that a player could not know:
//   1. every random generator reachable from the run and the combat gets a fresh state derived from the sample seed
//      (found by walking the objects, not from a fixed list: the 12 run streams, the 3 player streams, each monster's
//      own generator, event and relic generators);
//   2. the draw pile is shuffled (its contents are public, its order is not).
// Known limits, stated in the phase document: draw-pile positions the player knows (a card put on top) are not kept
// yet, so the sampler forgets them; hidden state pre-rolled into other objects has not been inventoried (OQ7.3).
using System.Collections;
using System.Reflection;
using System.Text.Json.Nodes;
using MegaCrit.Sts2.Core.Random;

public static class Sanitizer
{
    static readonly FieldInfo RandomField = typeof(Rng).GetField("_random", BindingFlags.Instance | BindingFlags.NonPublic)!;
    static readonly FieldInfo CounterField = typeof(Rng).GetField("_counter", BindingFlags.Instance | BindingFlags.NonPublic)!;
    static readonly FieldInfo[] StateFields = new[] { "_s0", "_s1", "_s2", "_s3" }
        .Select(n => typeof(MegaRandom).GetField(n, BindingFlags.Instance | BindingFlags.NonPublic)!).ToArray();
    static readonly Dictionary<Type, FieldInfo[]> FieldCache = new();
    public static int LastCount;
    public static double LastMs;

    // Every Rng reachable from the roots, in a deterministic order (field declaration order, list order).
    public static List<Rng> FindGenerators(IEnumerable<object> roots)
    {
        var found = new List<Rng>();
        var seen = new HashSet<object>(ReferenceEqualityComparer.Instance);
        var stack = new Stack<object>(roots.Where(r => r != null).Reverse());
        while (stack.Count > 0)
        {
            var o = stack.Pop();
            if (o == null || !seen.Add(o)) continue;
            if (o is Rng rng) { found.Add(rng); continue; }
            var t = o.GetType();
            if (t.IsPrimitive || t.IsEnum || o is string || o is Type || o is Delegate || o is Pointer || o is MemberInfo || o is Task) continue;
            if (o is Godot.GodotObject) continue;                       // UI and engine objects hold no game state in the host
            if (o is IEnumerable en && (t.Namespace ?? "").StartsWith("System."))
            {
                var items = new List<object>();
                try { foreach (var x in en) if (x != null && !x.GetType().IsPrimitive && x is not string) items.Add(x); } catch (InvalidOperationException) { }
                for (var i = items.Count - 1; i >= 0; i--) stack.Push(items[i]);
                continue;
            }
            if (!(t.Namespace ?? "").StartsWith("MegaCrit", StringComparison.OrdinalIgnoreCase) && !t.IsValueType && !t.IsArray
                && !(t.Namespace ?? "").StartsWith("System.Collections")) continue;
            if (t.IsArray) { if (t.GetElementType()!.IsPrimitive) continue; foreach (var x in (Array)o) if (x != null) stack.Push(x); continue; }
            if (!FieldCache.TryGetValue(t, out var fields))
            {
                var all = new List<FieldInfo>();
                for (var b = t; b != null && b != typeof(object); b = b.BaseType)
                    all.AddRange(b.GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly)
                        .Where(f => !f.FieldType.IsPrimitive && !f.FieldType.IsEnum && f.FieldType != typeof(string) && !f.FieldType.IsPointer));
                FieldCache[t] = fields = all.ToArray();
            }
            for (var i = fields.Length - 1; i >= 0; i--)
            {
                object v;
                try { v = fields[i].GetValue(o); } catch { continue; }
                if (v != null) stack.Push(v);
            }
        }
        return found;
    }

    public static void Apply(Session s, ulong sampleSeed)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        var gens = FindGenerators(s.Roots());
        for (var i = 0; i < gens.Count; i++)
        {
            // an independent fresh state per generator, a pure function of the sample seed and its position
            RandomField.SetValue(gens[i], new MegaRandom(Mix(sampleSeed, (ulong)i + 1)));
            CounterField.SetValue(gens[i], 0);
        }
        // every player's draw order is hidden: re-sampled, keeping only the positions the player knows (FP-5)
        for (var k = 0; k < s.Run.Players.Count; k++)
            if (s.Run.Players[k].PlayerCombatState?.DrawPile is { } draw)
                DrawKnowledge.Resample(draw, Mix(sampleSeed, 0xD1CEUL + (ulong)k));
        LastCount = gens.Count;
        LastMs = sw.Elapsed.TotalMilliseconds;
    }

    // SplitMix64: spreads the sample seed and an index into an independent 64-bit seed.
    internal static ulong Mix(ulong seed, ulong index)
    {
        var z = seed + index * 0x9E3779B97F4A7C15UL;
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBUL;
        return z ^ (z >> 31);
    }

    // A text fingerprint of every reachable generator's state, for tests.
    public static JsonArray Fingerprint(Session s)
    {
        var a = new JsonArray();
        foreach (var g in FindGenerators(s.Roots()))
        {
            var r = RandomField.GetValue(g);
            a.Add(string.Join(":", StateFields.Select(f => ((ulong)f.GetValue(r)!).ToString("x"))) + "#" + CounterField.GetValue(g));
        }
        return a;
    }
}
