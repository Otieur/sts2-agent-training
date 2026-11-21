// Run-level sampler (docs/simulator-integrity.md FP-9, FP-16; decision 0004 step 3; P7.E8.S4). After a run has been
// rebuilt at a decision point, everything about its future that a player could not know is re-sampled from the sample
// seed:
//   1. every random generator reachable from the run gets a fresh state (Sanitizer: rewards, shops, unknown rooms, the
//      monsters' AI, the combat streams, event and relic generators);
//   2. the seed that later acts' maps are generated from (RunRngSet.Seed), so acts not yet entered get new maps;
//   3. each act's pre-generated rooms (RoomSet): a fresh room set is generated for every act by the game's own procedure
//      (as RunManager.GenerateRooms, on fresh copies of the acts) from a generator derived from the sample seed. Acts not
//      yet entered take it whole (events, encounters, Ancient, bosses); the current act keeps what has been visited and
//      its boss, which the player sees on the map from the act's start (knowledge/gaps.md gap 5), and takes the rest (the
//      unvisited events, normal and elite encounters);
//   4. the relic queues (each player's RelicGrabBag and the shared one): the remaining relics of each rarity reshuffled.
// Kept: everything the player has seen (deck, relics, potions, gold, HP, the current act's map, visited rooms) and the
// pity counters (Odds), which a player can track from what happened. An event already under way keeps its rolled values.
using System.Collections;
using System.Reflection;
using System.Text.Json.Nodes;
using MegaCrit.Sts2.Core.Extensions;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;

public static class RunSampler
{
    const BindingFlags Inst = BindingFlags.Instance | BindingFlags.NonPublic;
    static readonly FieldInfo RoomsField = typeof(ActModel).GetField("_rooms", Inst)!;
    static readonly FieldInfo SharedAncientsField = typeof(ActModel).GetField("_sharedAncientSubset", Inst)!;
    static readonly FieldInfo AncientField = typeof(RoomSet).GetField("_ancient", Inst)!;
    static readonly FieldInfo BossField = typeof(RoomSet).GetField("_boss", Inst)!;
    static readonly FieldInfo SecondBossField = typeof(RoomSet).GetField("<SecondBoss>k__BackingField", Inst)!;
    static readonly FieldInfo SeedField = typeof(RunRngSet).GetField("<Seed>k__BackingField", Inst)!;
    static readonly FieldInfo DequesField = typeof(RelicGrabBag).GetField("_deques", Inst)!;
    public static JsonObject LastReport = new();

    public static void Apply(Session s, ulong sampleSeed)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        var run = s.Run;
        Sanitizer.Apply(s, sampleSeed);                                                   // 1
        SeedField.SetValue(run.Rng, (uint)Sanitizer.Mix(sampleSeed, 0x5EEDUL));          // 2

        var rng = new Rng((uint)Sanitizer.Mix(sampleSeed, 0xACE5UL));                    // 3
        var fresh = run.Acts.Select(a => (ActModel)a.CanonicalInstance.ToMutable()).ToList();
        var shared = run.UnlockState.SharedAncients.ToList().UnstableShuffle(rng);
        foreach (var act in fresh.Skip(1))
        {
            var n = rng.NextInt(shared.Count + 1);
            var subset = shared.Take(n).ToList();
            shared = shared.Except(subset).ToList();
            act.SetSharedAncientSubset(subset);
        }
        for (var i = 0; i < fresh.Count; i++)
        {
            fresh[i].GenerateRooms(rng, run.UnlockState, run.Players.Count > 1);
            if (i == fresh.Count - 1 && run.AscensionLevel >= 10)
            {
                var first = fresh[i].BossEncounter;
                fresh[i].SetSecondBossEncounter(rng.NextItem(fresh[i].AllBossEncounters.Where(e => e.Id != first.Id)));
            }
        }
        var cur = run.CurrentActIndex;
        var replaced = 0;
        for (var i = cur; i < run.Acts.Count; i++)
        {
            var live = (RoomSet)RoomsField.GetValue(run.Acts[i])!;
            var neu = (RoomSet)RoomsField.GetValue(fresh[i])!;
            var entered = i == cur;
            replaced += Splice(live.events, neu.events, entered ? live.eventsVisited : 0);
            replaced += Splice(live.normalEncounters, neu.normalEncounters, entered ? live.normalEncountersVisited : 0);
            replaced += Splice(live.eliteEncounters, neu.eliteEncounters, entered ? live.eliteEncountersVisited : 0);
            if (!entered)
            {
                AncientField.SetValue(live, AncientField.GetValue(neu));
                SharedAncientsField.SetValue(run.Acts[i], SharedAncientsField.GetValue(fresh[i]));
                BossField.SetValue(live, BossField.GetValue(neu));
                SecondBossField.SetValue(live, SecondBossField.GetValue(neu));
            }
        }

        var bags = run.Players.Select(p => p.RelicGrabBag).Append(run.SharedRelicGrabBag).Where(b => b != null).ToList();   // 4
        var shuffled = 0;
        for (var b = 0; b < bags.Count; b++)
            if (DequesField.GetValue(bags[b]) is IDictionary d)
            {
                var k = 0;
                foreach (var v in d.Values)
                    if (v is IList list) { Shuffle(list, Sanitizer.Mix(sampleSeed, 0xBA6000UL + (ulong)(b * 64 + k++))); shuffled += list.Count; }
            }
        LastReport = new JsonObject
        {
            ["generators"] = Sanitizer.LastCount, ["acts"] = run.Acts.Count - cur, ["room_entries_replaced"] = replaced,
            ["relics_reshuffled"] = shuffled, ["ms"] = Math.Round(sw.Elapsed.TotalMilliseconds, 2),
        };
    }

    // Keeps the first `keep` entries of the live list and takes the rest from the freshly generated one.
    static int Splice(IList live, IList neu, int keep)
    {
        keep = Math.Min(keep, live.Count);
        while (live.Count > keep) live.RemoveAt(live.Count - 1);
        var n = 0;
        for (var i = keep; i < neu.Count; i++) { live.Add(neu[i]); n++; }
        return n;
    }

    static void Shuffle(IList list, ulong seed)
    {
        var r = new System.Random((int)(seed ^ (seed >> 32)));
        for (var i = list.Count - 1; i > 0; i--)
        {
            var j = r.Next(i + 1);
            (list[i], list[j]) = (list[j], list[i]);
        }
    }
}
