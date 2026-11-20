// Known draw-pile positions (FP-5, P7.E6.S3). A player remembers what their own effects put on top or at the bottom
// of the draw pile, and sees which card each draw takes from the top. The sampler keeps exactly that knowledge and
// randomises the rest.
//
// For each draw pile the host logs the visible operations since the last full shuffle:
//   Base(cards)   the pile was shuffled: order unknown (combat start, CardPile.RandomizeOrderInternal)
//   Top(c)        c was put on top (CardPileCmd.Add with CardPilePosition.Top, or moved to the top)
//   Bottom(c)     c was put at the bottom
//   Random(c)     c was shuffled in at a random position (CardPilePosition.Random, or any add whose position the
//                 host cannot see, which is treated the same way: conservative)
//   Group(c, g)   c arrived with the discard pile shuffled in (CardPileCmd.Shuffle): a block of unknown order
//   Reveal(c)     c left from the top as a draw (or "play the top card"): the player saw it was on top
//   Remove(c)     c left from a position the player did not see (a chosen or random card)
// The position used for Top/Bottom/Random comes from the command's position argument, never from the index the card
// landed on (a random insert that lands on index 0 is not "known on top").
//
// To sample a world, the log is replayed with fresh randomness: unknown slots are drawn from pools, random inserts
// choose a slot uniformly, and a Reveal that contradicts the sampled slot rejects the sample (rejection sampling).
// The result is a uniform draw from the orders consistent with what the player saw.
//
// Approximations, all toward knowing less: a transformed card in the draw pile counts as a random insert; a card
// revealed by an effect other than drawing or playing the top card counts as an unseen removal.
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;

public static class DrawKnowledge
{
    enum K { Base, Top, Bottom, Random, Group, Reveal, Remove }
    readonly record struct Op(K Kind, CardModel Card, int Group = 0, bool AtTop = false, CardModel[] Cards = null);

    sealed class Log { public readonly List<Op> Ops = new(); public int Groups; }

    static readonly ConditionalWeakTable<CardPile, Log> Logs = new();
    static readonly HashSet<CardModel> Drawing = new(ReferenceEqualityComparer.Instance);
    static readonly Dictionary<CardModel, int> Shuffling = new(ReferenceEqualityComparer.Instance);
    static CardPilePosition? _position;           // set by AddAt immediately before the AddInternal call it wraps
    static readonly FieldInfo CardsField = typeof(CardPile).GetField("_cards", BindingFlags.Instance | BindingFlags.NonPublic)!;
    public static int Samples, Rejections, Fallbacks;
    public static string LastFallback = "", LastReject = "";

    static Log For(CardPile p) => Logs.GetValue(p, _ => new Log());
    static bool IsDraw(CardPile p) => p.Type == PileType.Draw;

    public static void Install()
    {
        var h = Stubs.H;
        var flags = BindingFlags.Static | BindingFlags.NonPublic;
        HarmonyLib.HarmonyMethod M(string name) => new(typeof(DrawKnowledge).GetMethod(name, flags));
        h.Patch(typeof(CardPile).GetMethod("AddInternal")!, prefix: M(nameof(AddPrefix)));
        h.Patch(typeof(CardPile).GetMethod("RemoveInternal")!, prefix: M(nameof(RemovePrefix)));
        h.Patch(typeof(CardPile).GetMethod("RandomizeOrderInternal")!, postfix: M(nameof(RandomizedPostfix)));
        h.Patch(typeof(CardPile).GetMethod("MoveToTopInternal")!, prefix: M(nameof(MoveTopPrefix)));
        h.Patch(typeof(CardPile).GetMethod("MoveToBottomInternal")!, prefix: M(nameof(MoveBottomPrefix)));
        h.Patch(typeof(CardPileCmd).GetMethod("Shuffle", BindingFlags.Static | BindingFlags.Public)!, prefix: M(nameof(ShufflePrefix)));
        // CardPileCmd.Add (the list overload's state machine) knows the position; pass it on with the insert
        Transpile(typeof(CardPileCmd), "Add", nameof(PositionTranspiler), mustReplace: 1);
        // a draw and "play the top card" take the first card of the draw pile: mark it as seen on top
        Transpile(typeof(CardPileCmd), "DrawInternal", nameof(TopTranspiler), mustReplace: 1);
        Transpile(typeof(CardPileCmd), "AutoPlayFromDrawPile", nameof(TopTranspiler), mustReplace: 1);
    }

    static int _replaced;
    static void Transpile(Type owner, string asyncMethod, string transpiler, int mustReplace)
    {
        _replaced = 0;
        var tr = new HarmonyLib.HarmonyMethod(typeof(DrawKnowledge).GetMethod(transpiler, BindingFlags.Static | BindingFlags.NonPublic));
        foreach (var sm in owner.GetNestedTypes(BindingFlags.NonPublic).Where(t => t.Name.StartsWith("<" + asyncMethod + ">")))
            Stubs.H.Patch(sm.GetMethod("MoveNext", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public)!, transpiler: tr);
        if (_replaced != mustReplace)
            throw new InvalidOperationException($"{owner.Name}.{asyncMethod}: expected {mustReplace} call site(s) to rewrite, found {_replaced} (game changed?)");
    }

    static IEnumerable<HarmonyLib.CodeInstruction> PositionTranspiler(IEnumerable<HarmonyLib.CodeInstruction> code, MethodBase original)
    {
        var position = original.DeclaringType!.GetField("position", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
        var addAt = typeof(DrawKnowledge).GetMethod(nameof(AddAt), BindingFlags.Static | BindingFlags.Public)!;
        foreach (var ins in code)
        {
            if (position != null && ins.operand is MethodInfo m && m.DeclaringType == typeof(CardPile) && m.Name == "AddInternal")
            {
                yield return new HarmonyLib.CodeInstruction(OpCodes.Ldarg_0);
                yield return new HarmonyLib.CodeInstruction(OpCodes.Ldfld, position);
                ins.opcode = OpCodes.Call;
                ins.operand = addAt;
                _replaced++;
            }
            yield return ins;
        }
    }

    static IEnumerable<HarmonyLib.CodeInstruction> TopTranspiler(IEnumerable<HarmonyLib.CodeInstruction> code)
    {
        var takeTop = typeof(DrawKnowledge).GetMethod(nameof(TakeTop), BindingFlags.Static | BindingFlags.Public)!;
        foreach (var ins in code)
        {
            if (ins.operand is MethodInfo m && m.Name == "FirstOrDefault" && m.DeclaringType == typeof(Enumerable) && m.IsGenericMethod
                && m.GetGenericArguments()[0] == typeof(CardModel) && m.GetParameters().Length == 1)
            {
                ins.operand = takeTop;
                _replaced++;
            }
            yield return ins;
        }
    }

    public static void AddAt(CardPile pile, CardModel card, int index, bool silent, CardPilePosition position)
    {
        _position = position;
        try { pile.AddInternal(card, index, silent); } finally { _position = null; }
    }

    public static CardModel TakeTop(IEnumerable<CardModel> cards)
    {
        var c = cards.FirstOrDefault();
        if (c != null) Drawing.Add(c);
        return c;
    }

    static void AddPrefix(CardPile __instance, CardModel card, int index)
    {
        var pos = _position;
        _position = null;
        if (!IsDraw(__instance)) return;
        var log = For(__instance);
        if (Shuffling.Remove(card, out var g)) { log.Ops.Add(new Op(K.Group, card, g, index == 0)); return; }
        log.Ops.Add(pos switch
        {
            CardPilePosition.Top => new Op(K.Top, card),
            CardPilePosition.Bottom => new Op(K.Bottom, card),
            _ => new Op(K.Random, card),
        });
    }

    static void RemovePrefix(CardPile __instance, CardModel card)
    {
        if (!IsDraw(__instance)) { Drawing.Remove(card); return; }
        var top = __instance.Cards.Count > 0 && ReferenceEquals(__instance.Cards[0], card);
        var seen = Drawing.Remove(card) && top;
        For(__instance).Ops.Add(new Op(seen ? K.Reveal : K.Remove, card));
    }

    static void RandomizedPostfix(CardPile __instance)
    {
        if (!IsDraw(__instance)) return;
        var log = For(__instance);
        log.Ops.Clear();
        log.Ops.Add(new Op(K.Base, null, Cards: __instance.Cards.ToArray()));
        Drawing.Clear();
    }

    static void MoveTopPrefix(CardPile __instance, CardModel card)
    {
        if (!IsDraw(__instance)) return;
        var log = For(__instance);
        log.Ops.Add(new Op(K.Remove, card));
        log.Ops.Add(new Op(K.Top, card));
    }

    static void MoveBottomPrefix(CardPile __instance, CardModel card)
    {
        if (!IsDraw(__instance)) return;
        var log = For(__instance);
        log.Ops.Add(new Op(K.Remove, card));
        log.Ops.Add(new Op(K.Bottom, card));
    }

    static void ShufflePrefix(object[] __args)
    {
        var player = __args.OfType<Player>().FirstOrDefault();
        if (player?.PlayerCombatState == null) return;
        var log = For(player.PlayerCombatState.DrawPile);
        var g = ++log.Groups;
        foreach (var c in player.PlayerCombatState.DiscardPile.Cards) Shuffling[c] = g;
    }

    // ---- Sampling.

    // Replays the log with fresh randomness until it is consistent with every reveal. Null when no sample fits.
    static List<CardModel> TrySample(Log log, Random rng)
    {
        var slots = new List<(CardModel Card, int Pool)>();
        var pools = new Dictionary<int, List<CardModel>>();
        var groupPool = new Dictionary<int, int>();
        var next = 1;
        foreach (var op in log.Ops)
        {
            switch (op.Kind)
            {
                case K.Base:
                    slots.Clear(); pools.Clear(); groupPool.Clear();
                    pools[0] = op.Cards!.ToList();
                    foreach (var _ in op.Cards!) slots.Add((null, 0));
                    break;
                case K.Top: slots.Insert(0, (op.Card, -1)); break;
                case K.Bottom: slots.Add((op.Card, -1)); break;
                case K.Random:
                {
                    // A uniform insert into a block of unknown order is the same as adding the card to that block's
                    // pool (the block stays a uniform permutation), so its exact place is decided only when the pool is
                    // filled, consistent with every later reveal. Only an insert between known cards gets a fixed place.
                    // (Gaps are assigned to the block of the slot after them, else before them: exact for a single
                    // block, close to uniform where two blocks or a block and a known card meet.)
                    var g = rng.Next(slots.Count + 1);
                    var p = g < slots.Count && slots[g].Card == null ? slots[g].Pool : g > 0 && slots[g - 1].Card == null ? slots[g - 1].Pool : -1;
                    if (p >= 0) { pools[p].Add(op.Card); slots.Insert(g, (null, p)); }
                    else slots.Insert(g, (op.Card, -1));
                    break;
                }
                case K.Group:
                {
                    if (!groupPool.TryGetValue(op.Group, out var p)) { p = next++; groupPool[op.Group] = p; pools[p] = new List<CardModel>(); }
                    pools[p].Add(op.Card);
                    if (op.AtTop) slots.Insert(0, (null, p)); else slots.Add((null, p));
                    break;
                }
                case K.Reveal:
                {
                    if (slots.Count == 0) return Reject(op, "reveal from an empty pile");
                    var s = slots[0];
                    if (s.Card != null) { if (!ReferenceEquals(s.Card, op.Card)) return Reject(op, "top slot holds " + s.Card.Id.Entry); }
                    else if (!pools[s.Pool].Remove(op.Card)) return Reject(op, $"top slot's pool {s.Pool} lacks the card");
                    slots.RemoveAt(0);
                    break;
                }
                case K.Remove:
                {
                    var i = slots.FindIndex(s => ReferenceEquals(s.Card, op.Card));
                    if (i >= 0) { slots.RemoveAt(i); break; }
                    var p = pools.FirstOrDefault(kv => kv.Value.Contains(op.Card, ReferenceEqualityComparer.Instance)).Key;
                    if (!pools.TryGetValue(p, out var pool) || !pool.Remove(op.Card)) return Reject(op, "removed card not in the pile");
                    var free = Enumerable.Range(0, slots.Count).Where(k => slots[k].Card == null && slots[k].Pool == p).ToList();
                    if (free.Count == 0) return Reject(op, "no free slot of its pool");
                    slots.RemoveAt(free[rng.Next(free.Count)]);
                    break;
                }
            }
        }
        foreach (var pool in pools.Values)
            for (var i = pool.Count - 1; i > 0; i--) { var j = rng.Next(i + 1); (pool[i], pool[j]) = (pool[j], pool[i]); }
        var taken = pools.ToDictionary(kv => kv.Key, _ => 0);
        var order = new List<CardModel>(slots.Count);
        foreach (var s in slots)
        {
            if (s.Card != null) { order.Add(s.Card); continue; }
            var pool = pools[s.Pool];
            if (taken[s.Pool] >= pool.Count) { LastReject = "more slots than cards in pool " + s.Pool; return null; }
            order.Add(pool[taken[s.Pool]++]);
        }
        return order;
    }

    static List<CardModel> Reject(Op op, string why) { LastReject = $"{op.Kind} {op.Card?.Id.Entry}: {why}"; return null; }

    // Reorders the draw pile to a sample consistent with what the player knows. Falls back to a full shuffle (knowing
    // less, never more) when the log does not match the pile.
    public static void Resample(CardPile pile, ulong seed)
    {
        var rng = new Random(unchecked((int)(seed ^ (seed >> 32))));
        var cards = (List<CardModel>)CardsField.GetValue(pile)!;
        if (cards.Count < 2) return;
        Samples++;
        List<CardModel> order = null;
        if (Logs.TryGetValue(pile, out var log) && log.Ops.Count > 0 && log.Ops[0].Kind == K.Base)
        {
            for (var attempt = 0; attempt < 500 && order == null; attempt++)
            {
                order = TrySample(log, rng);
                if (order == null) Rejections++;
            }
            if (order != null && !SameCards(order, cards)) { LastFallback = "log does not match the pile"; order = null; }
            else if (order == null) LastFallback = "no consistent sample in 500 tries; last rejection: " + LastReject;
        }
        else LastFallback = "no log since the last shuffle";
        if (order == null)
        {
            Fallbacks++;
            order = cards.ToList();
            for (var i = order.Count - 1; i > 0; i--) { var j = rng.Next(i + 1); (order[i], order[j]) = (order[j], order[i]); }
        }
        cards.Clear();
        cards.AddRange(order);
    }

    static bool SameCards(List<CardModel> a, List<CardModel> b)
    {
        if (a.Count != b.Count) return false;
        var set = new HashSet<CardModel>(b, ReferenceEqualityComparer.Instance);
        return a.All(set.Remove) && set.Count == 0;
    }

    // For tests: what the player knows about the pile (cards known at the top and the bottom, in order).
    public static System.Text.Json.Nodes.JsonObject Known(CardPile pile)
    {
        var top = new List<string>();
        var bottom = new List<string>();
        if (Logs.TryGetValue(pile, out var log))
        {
            // certain knowledge only: a random insert after the last top (bottom) placement may sit above (below) it
            var slots = new List<CardModel>();
            bool topUnsure = false, bottomUnsure = false;
            foreach (var op in log.Ops)
                switch (op.Kind)
                {
                    case K.Base: slots = op.Cards!.Select(_ => (CardModel)null).ToList(); topUnsure = bottomUnsure = false; break;
                    case K.Top: slots.Insert(0, op.Card); topUnsure = false; break;
                    case K.Bottom: slots.Add(op.Card); bottomUnsure = false; break;
                    case K.Random: slots.Insert(slots.Count / 2, null); topUnsure = bottomUnsure = true; break;
                    case K.Group: if (op.AtTop) slots.Insert(0, null); else slots.Add(null); break;
                    case K.Reveal: if (slots.Count > 0) slots.RemoveAt(0); break;
                    case K.Remove:
                    {
                        var i = slots.FindIndex(c => ReferenceEquals(c, op.Card));
                        if (i < 0) i = slots.FindIndex(c => c == null);
                        if (i >= 0) slots.RemoveAt(i);
                        break;
                    }
                }
            if (!topUnsure) foreach (var c in slots) { if (c == null) break; top.Add(c.Id.Entry); }
            if (!bottomUnsure) for (var i = slots.Count - 1; i >= 0 && slots[i] != null; i--) bottom.Add(slots[i].Id.Entry);
        }
        return new System.Text.Json.Nodes.JsonObject
        {
            ["known_top"] = new System.Text.Json.Nodes.JsonArray(top.Select(x => (System.Text.Json.Nodes.JsonNode)x).ToArray()),
            ["known_bottom"] = new System.Text.Json.Nodes.JsonArray(bottom.Select(x => (System.Text.Json.Nodes.JsonNode)x).ToArray()),
            ["ops"] = log?.Ops.Count ?? 0,
            ["log"] = new System.Text.Json.Nodes.JsonArray((log?.Ops ?? new List<Op>()).Select(o => (System.Text.Json.Nodes.JsonNode)(o.Kind + (o.Card != null ? ":" + o.Card.Id.Entry : o.Cards != null ? ":" + o.Cards.Length : "") + (o.Kind == K.Group ? "#" + o.Group : ""))).ToArray()),
        };
    }
}
