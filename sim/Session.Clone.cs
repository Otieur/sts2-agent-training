// State cloning for search (P7.E4.S4). The game has no mid-combat save and restore (EN-2), so a clone is the state's
// recipe: its origin (a fight from nothing with its spec, or a recorded fight up to an event, plus the sample seed) and
// the decision-mode operations applied since (steps and re-samples). Restoring rebuilds the origin and re-applies the
// operations. In decision mode everything random is a pure function of the sample seed and the operations, so the
// rebuilt state equals the snapshot (tools/sim.py clone checks observation, draw order and every generator's state).
//
// Run-level states are not cloned: a run-level search must first re-sample the pre-rolled run content (FP-16), which the
// host does not do yet. Fidelity-mode states (no sample seed) are not cloned either (FP-3).
using System.Text.Json.Nodes;

public sealed partial class Session
{
    sealed record Origin(string Kind, JsonNode Spec, int Events, ulong Seed, MegaCrit.Sts2.Core.Multiplayer.Replay.CombatReplay Recording, byte[] Bytes = null);
    Origin _origin;
    readonly List<JsonNode> _ops = new();
    readonly List<(Origin Origin, JsonNode[] Ops)> _snapshots = new();
    public double LastRestoreMs;

    void NoteOrigin(string kind, JsonNode spec, int events, ulong seed)
    {
        _origin = new Origin(kind, spec?.DeepClone(), events, seed, Replay);
        _ops.Clear();
    }

    void ForgetOrigin() { _origin = null; _ops.Clear(); }

    void NoteOriginSave(byte[] bytes, JsonArray actions, ulong seed)
    {
        _origin = new Origin("save", new JsonObject { ["actions"] = actions.DeepClone() }, 0, seed, null, bytes);
        _ops.Clear();
    }

    public void NoteStep(JsonNode action) { if (_origin != null) _ops.Add(new JsonObject { ["step"] = action.DeepClone() }); }
    public void NoteResample(ulong seed) { if (_origin != null) _ops.Add(new JsonObject { ["resample"] = (long)seed }); }

    public int Snapshot()
    {
        if (RunMode) throw new InvalidOperationException("run-level states are not cloned until the pre-rolled run content is re-sampled (FP-16)");
        if (_origin == null) throw new InvalidOperationException("only a decision-mode fight (new_fight, or reset with a sample seed) can be cloned (FP-3)");
        _snapshots.Add((_origin, _ops.ToArray()));
        return _snapshots.Count - 1;
    }

    public void Restore(int id)
    {
        if (id < 0 || id >= _snapshots.Count) throw new ArgumentException("unknown snapshot " + id);
        var sw = System.Diagnostics.Stopwatch.StartNew();
        var (o, ops) = _snapshots[id];
        if (o.Kind == "fight") NewFight(o.Spec, o.Seed);
        else if (o.Kind == "save") FightFromSave(o.Bytes, o.Spec["actions"]!.AsArray(), o.Seed);
        else { Replay = o.Recording; Reset(o.Events, o.Seed); }
        var replay = System.Diagnostics.Stopwatch.StartNew();
        foreach (var op in ops)
        {
            if (op["step"] is { } a) { Step(a); NoteStep(a); }
            else { Sanitizer.Apply(this, (ulong)(long)op["resample"]!); NoteResample((ulong)(long)op["resample"]!); }
        }
        LastRestoreMs = sw.Elapsed.TotalMilliseconds;
        NewFightMs["replay_ops"] = replay.Elapsed.TotalMilliseconds;
        NewFightMs["ops"] = ops.Length;
    }
}
