// Run-level clones (decision 0004 step 3, P7.E8.S4). A run state is rebuilt from the save the game itself makes when a
// room is entered (kept in memory only: the host never writes saves, SA-1) plus the run actions taken since, in normal
// single-player mode, so any run-level decision point can be copied into another host and played forward. A sample
// seed then re-samples the hidden future (FP-16, RunSampler); without one the rebuild is exact (the true future), which
// is only for checks, never for decisions (FP-9).
using System.Reflection;
using System.Text.Json.Nodes;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Multiplayer.Serialization;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;

public sealed partial class Session
{
    public readonly List<JsonNode> RunActions = new();   // run actions since the run started or was rebuilt
    public byte[] LastRunSave;                            // the run as saved at the last room entry
    public int LastRunSaveAt;                             // RunActions.Count when that save was made
    public int RunSaves;
    bool _rebuildingRun;

    static bool _saveHooked;
    public static void HookRunSaves()
    {
        if (_saveHooked) return;
        _saveHooked = true;
        var m = typeof(MegaCrit.Sts2.Core.Saves.SaveManager).GetMethod("SaveRun")!;
        Stubs.H.Patch(m, prefix: new HarmonyLib.HarmonyMethod(typeof(Session).GetMethod(nameof(OnSaveRun), BindingFlags.Static | BindingFlags.NonPublic)));
    }

    // SaveManager.SaveRun(preFinishedRoom, saveProgress): the game saves at room entry, after a fight and when an event's
    // state changes. Nothing is written (SA-1). A save with no finished room (a room entry) is kept in memory.
    static bool OnSaveRun(AbstractRoom preFinishedRoom, ref Task __result)
    {
        __result = Task.CompletedTask;
        var s = _current;
        if (s != null && s.RunMode && preFinishedRoom == null && !s._rebuildingRun) s.CaptureRunSave();
        return false;
    }

    void CaptureRunSave()
    {
        var save = Rm.ToSave(null);
        var w = new PacketWriter();
        w.Write(save);
        w.ZeroByteRemainder();
        LastRunSave = w.Buffer.Take(w.BytePosition).ToArray();
        LastRunSaveAt = RunActions.Count;
        RunSaves++;
    }

    public JsonObject RunExport()
    {
        if (!RunMode || LastRunSave == null) throw new InvalidOperationException("no run save yet (a save is made when a room is entered)");
        return new JsonObject
        {
            ["save_b64"] = Convert.ToBase64String(LastRunSave),
            ["actions"] = new JsonArray(RunActions.Skip(LastRunSaveAt).Select(a => a.DeepClone()).ToArray()),
            ["saves"] = RunSaves,
            ["test_hp"] = TestHp,
        };
    }

    // A fight inside a run, rebuilt through the run clone (the room-entry save plus the run actions since, which may
    // include the event option that started the fight), then switched to fight decision mode and sanitized with the
    // sample seed. Unlike fight_from_save it also rebuilds fights started by events (the fight's own save re-enters the
    // event). Snapshots of it restore by the same recipe (origin "runsave").
    public void FightFromRun(byte[] bytes, JsonArray actions, ulong sampleSeed)
    {
        RunFromSave(bytes, actions, 0, false, false);
        if (!CombatManager.Instance.IsInProgress) throw new InvalidOperationException("the rebuilt run is not in a fight");
        RunMode = false;
        Choices.Intercept = true;
        Sanitizer.Apply(this, sampleSeed);
        Sanitized = true;
        NoteOriginRun(bytes, actions, sampleSeed);
    }

    // The run rebuilt from a room-entry save and the run actions since. With resample, the hidden future is re-sampled
    // from the sample seed afterwards (RunSampler).
    public void RunFromSave(byte[] bytes, JsonArray actions, ulong sampleSeed, bool resample, bool recordFights, bool testHp = false)
    {
        HookRewards();
        HookRunSaves();
        _current = this;
        SynchronizationContext.SetSynchronizationContext(Ctx);
        if (Run != null) { Unwind(); Rm.CleanUp(true); Ctx.Drain(); }
        Replay = null;
        _last = null; _pending = null; _eventTask = null; _rewards = null; _rewardsRoom = null; _doneRoom = null; _chestRoom = null; _proceededRoom = null;
        _failedRewards.Clear();
        Choices.Minigame = null; Choices.Current = null; Choices.Intercept = false;
        ForgetOrigin();
        Applied = 0; PlayerIndex = 0; Victory = false; Net = null; TestHp = testHp;
        var reader = new PacketReader();
        reader.Reset(bytes);
        var save = reader.Read<MegaCrit.Sts2.Core.Saves.SerializableRun>();
        Run = RunState.FromSerializable(save);
        RunSeed = Run.Rng.StringSeed;
        _rebuildingRun = true;
        try
        {
            Ctx.RunUntil(Rm.SetUpSavedSingleplayer(Run, save), "SetUpSavedSingleplayer");
            Rm.CombatStateSynchronizer.IsDisabled = true;
            Rm.ChecksumTracker.IsEnabled = false;
            Rm.CombatReplayWriter.IsEnabled = recordFights;
            Rm.Launch();
            Ctx.RunUntil(Rm.GenerateMap(), "GenerateMap");
            RunMode = true;
            Sanitized = true;
            Choices.Intercept = true;
            var pre = save.PreFinishedRoom == null ? null : AbstractRoom.FromSerializable(save.PreFinishedRoom, Run);
            Track(Rm.LoadIntoLatestMapCoord(pre));
            RunActions.Clear();
            foreach (var a in actions)
            {
                RunStep(a!);
                AfterRewardTaken();
                RunActions.Add(a!.DeepClone());
            }
        }
        finally { _rebuildingRun = false; }
        LastRunSave = bytes;
        LastRunSaveAt = 0;
        if (resample) RunSampler.Apply(this, sampleSeed);
    }
}
