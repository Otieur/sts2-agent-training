// Decision mode (docs/simulator-integrity.md FP-3, FP-15): a fight positioned at a decision point, sanitized so that
// nothing a player could not know survives, then explored one action at a time.
//
// Reaching the position uses the recorded fight and its true random state: the past is what the player saw. Before any
// exploration the Sanitizer replaces every random generator and shuffles the draw pile; from then on the future is a
// sample, not the real one. Observations contain only what the live API shows (ML-1): no draw order, no seed, no move
// names for intents (FP-7).
using System.Text.Json.Nodes;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;
using MegaCrit.Sts2.Core.Multiplayer.Replay;
using MegaCrit.Sts2.Core.Runs;

public sealed partial class Session
{
    public CombatReplay Replay;
    public RunState Run;
    public readonly SimContext Ctx = new();
    public int Applied;          // recorded events applied since the last reset
    public bool Sanitized;
    bool _hasRun;

    static RunManager Rm => RunManager.Instance;
    // Co-op readiness: the acting player is an index into the run's players, never a fixed "the player".
    public int PlayerIndex;
    Player Me => Run.Players[PlayerIndex];
    CombatState Combat => CombatManager.Instance.DebugOnlyGetState();

    public void Load(string path) { Replay = global::Replay.Load(path); _hasRun = _hasRun && false; }

    // A fight recorded in this session (a whole run with "record_fights"): the game's own in-memory replay of the current
    // fight, its start state and every action so far, serialized in the replay file format. A search host loads it
    // (LoadBytes) and rebuilds the fight with the hidden future re-sampled, which is how search plays fights inside
    // simulated runs, and the same path a live fight takes once it is rebuilt from a save (docs/proposals/live-search.md).
    public byte[] ExportFight()
    {
        var field = HarmonyLib.AccessTools.Field(typeof(MegaCrit.Sts2.Core.Multiplayer.Replay.CombatReplayWriter), "_replay");
        var replay = field.GetValue(Rm.CombatReplayWriter) as MegaCrit.Sts2.Core.Multiplayer.Replay.CombatReplay
                     ?? throw new InvalidOperationException("no fight is being recorded (start the run with record_fights)");
        var w = new MegaCrit.Sts2.Core.Multiplayer.Serialization.PacketWriter();
        w.Write(replay);
        w.ZeroByteRemainder();
        LastExportEvents = replay.events.Count;
        return w.Buffer.Take(w.BytePosition).ToArray();
    }

    public int LastExportEvents;
    bool _rebuilding;

    // A fight rebuilt from the run state saved at its start (the serializable run of an exported fight recording, or
    // a save file) in normal single-player mode, then the fight's actions so far applied with the true random state,
    // then sanitized with the sample seed. Unlike a replay set-up, choices are answered locally, so search works as on
    // a fight from nothing. Used to search fights inside simulated runs, and the route for live fights
    // (docs/proposals/live-search.md).
    public void FightFromSave(MegaCrit.Sts2.Core.Multiplayer.Replay.CombatReplay recording, JsonArray actions, ulong sampleSeed)
    {
        SynchronizationContext.SetSynchronizationContext(Ctx);
        if (Run != null) { Unwind(); Rm.CleanUp(true); Ctx.Drain(); }
        Replay = null;
        RunMode = false;
        Choices.Intercept = false;
        Choices.Current = null;
        _last = null;
        Applied = 0;
        Sanitized = false;
        PlayerIndex = 0;
        var save = recording.serializableRun;
        Run = RunState.FromSerializable(save);
        Ctx.RunUntil(Rm.SetUpSavedSingleplayer(Run, save), "SetUpSavedSingleplayer");
        Rm.CombatStateSynchronizer.IsDisabled = true;
        Rm.ChecksumTracker.IsEnabled = false;
        Rm.CombatReplayWriter.IsEnabled = false;
        // as the game's own load (NGame.LoadRun): launch the run and generate the act map before entering the room
        Rm.Launch();
        Ctx.RunUntil(Rm.GenerateMap(), "GenerateMap");
        var pre = save.PreFinishedRoom == null ? null : MegaCrit.Sts2.Core.Rooms.AbstractRoom.FromSerializable(save.PreFinishedRoom, Run);
        Ctx.RunUntil(Rm.LoadIntoLatestMapCoord(pre), "LoadIntoLatestMapCoord");
        Ctx.Drain();
        Choices.Intercept = true;
        _rebuilding = true;
        try
        {
            foreach (var a in actions)
                Step(a!);
        }
        finally { _rebuilding = false; }
        Sanitizer.Apply(this, sampleSeed);
        Sanitized = true;
        NoteOriginSave(recording, actions, sampleSeed);
    }

    public void LoadBytes(byte[] bytes)
    {
        var reader = new MegaCrit.Sts2.Core.Multiplayer.Serialization.PacketReader();
        reader.Reset(bytes);
        Replay = reader.Read<MegaCrit.Sts2.Core.Multiplayer.Replay.CombatReplay>();
        _hasRun = false;
    }

    // A choice left unanswered (search scoring the position right after an action that opens one, such as the Knowledge
    // Demon's curse offer during the enemy turn) keeps its game action waiting; clean-up does not cancel it, and the next
    // fight would queue behind it and never start (found 2026-11-20). Answer it with the smallest allowed pick first.
    void Unwind()
    {
        for (var i = 0; i < 20 && Choices.Current is { } ch; i++)
        {
            Choices.Answer(Enumerable.Range(0, ch.Min).ToList());
            Ctx.Drain();
        }
        Choices.Current = null;
    }

    // Rebuilds the fight and applies the first `events` recorded events (rounded up to the next decision point).
    // With a sample seed the state is sanitized; without one it keeps the true random state (fidelity use only).
    public void Reset(int events, ulong? sampleSeed)
    {
        if (Replay == null) throw new InvalidOperationException("no replay loaded");
        SynchronizationContext.SetSynchronizationContext(Ctx);
        if (Run != null) { Unwind(); Rm.CleanUp(true); Ctx.Drain(); }
        RunMode = false;
        Run = RunState.FromSerializable(Replay.serializableRun);
        Rm.SetUpReplay(Run, Replay, Me.NetId);
        Rm.CombatStateSynchronizer.IsDisabled = true;
        Rm.ChecksumTracker.IsEnabled = false;
        Rm.Launch();
        Ctx.RunUntil(Rm.GenerateMap(), "GenerateMap");
        Rm.ActionQueueSet.FastForwardNextActionId(Replay.nextActionId);
        Rm.ActionQueueSynchronizer.FastForwardHookId(Replay.nextHookId);
        Rm.PlayerChoiceSynchronizer.FastForwardChoiceIds(Replay.choiceIds);
        Rm.RewardsSetSynchronizer.FastForwardRewardIds(Replay.rewardIds);
        Ctx.RunUntil(Rm.LoadIntoLatestMapCoord(null), "enter the room");
        Applied = 0;
        Sanitized = false;
        _last = null;
        Choices.Intercept = false;      // recorded choices are replayed as recorded
        Choices.Current = null;
        while (Applied < Replay.events.Count && (Applied < events || !IsDecision(Replay.events[Applied])))
            ApplyRecorded(Replay.events[Applied]);
        if (sampleSeed.HasValue) { Sanitizer.Apply(this, sampleSeed.Value); Sanitized = true; Choices.Intercept = true; NoteOrigin("replay", null, events, sampleSeed.Value); }
        else ForgetOrigin();
    }

    static T ById<T>(IEnumerable<T> all, string id, string what) where T : AbstractModel
        => all.FirstOrDefault(m => m.Id.Entry == id) ?? throw new ArgumentException($"unknown {what} '{id}'");

    // A fight from nothing (P7.E4.S1): a new run for the given seed, character and ascension, the starting deck and
    // relics unless the request replaces them, then straight into the chosen encounter. No recording is involved.
    // The state is sanitized with the sample seed before it is returned, so the request's run seed fixes the set-up
    // (which monsters, their HP rolls) and the sample seed fixes everything random after it.
    // Time of each part of the last NewFight, in ms (restores call NewFight; `stats` reports it).
    public static readonly Dictionary<string, double> NewFightMs = new();
    System.Diagnostics.Stopwatch _phase;
    void Mark(string name) { NewFightMs[name] = _phase.Elapsed.TotalMilliseconds; _phase.Restart(); }

    public void NewFight(JsonNode spec, ulong sampleSeed)
    {
        _phase = System.Diagnostics.Stopwatch.StartNew();
        NewFightMs.Clear();
        SynchronizationContext.SetSynchronizationContext(Ctx);
        if (Run != null) { Unwind(); Rm.CleanUp(true); Ctx.Drain(); }
        Mark("clean_up");
        Replay = null;
        RunMode = false;
        Choices.Intercept = false;
        Choices.Current = null;
        _last = null;
        Applied = 0;
        Sanitized = false;
        PlayerIndex = 0;
        var character = ById(ModelDb.AllCharacters, (string)spec["character"] ?? "IRONCLAD", "character");
        var players = new List<Player> { Player.CreateForNewRun(character, MegaCrit.Sts2.Core.Unlocks.UnlockState.all, 1UL) };
        var acts = ActModel.GetDefaultList().Select(a => a.ToMutable()).ToList();
        Run = RunState.CreateForNewRun(players, acts, Array.Empty<ModifierModel>(), GameMode.Standard,
                                       (int?)spec["ascension"] ?? 0, (string)spec["seed"] ?? "SIMSEED00001");
        Rm.SetUpNewSingleplayer(Run, false, null);
        Rm.CombatStateSynchronizer.IsDisabled = true;
        Rm.ChecksumTracker.IsEnabled = false;
        // the game records every fight in memory (initial run state, then every action) whenever TestMode is off; the
        // host never writes the file (WriteReplay is stubbed), so the recording is pure cost
        Rm.CombatReplayWriter.IsEnabled = false;
        Mark("create_run");
        Ctx.RunUntil(Rm.FinalizeStartingRelics(), "FinalizeStartingRelics");
        Mark("starting_relics");
        Rm.Launch();
        Mark("launch");
        Rm.GenerateRooms();
        Mark("generate_rooms");
        // A fight from nothing needs no map, and generating it was most of a restore (90-240 ms under load of about
        // 110-260 ms). Checked 2026-11-20: 40 history fights, 673 states, identical with and without the map
        // (SIM_FIGHT_MAP=1 generates it again for such checks). Whole runs (Session.Run.cs) still generate it.
        if (Environment.GetEnvironmentVariable("SIM_FIGHT_MAP") == "1") Ctx.RunUntil(Rm.GenerateMap(), "GenerateMap");
        Mark("generate_map");
        var me = Me;
        if (spec["deck"] is JsonArray deck)
        {
            Ctx.RunUntil(MegaCrit.Sts2.Core.Commands.CardPileCmd.RemoveFromDeck(me.Deck.Cards.ToList(), false), "clear deck");
            foreach (var entry in deck.Select(x => (string)x))
            {
                var card = Run.CreateCard(ById(ModelDb.AllCards, entry.TrimEnd('+'), "card"), me);
                if (entry.EndsWith("+")) MegaCrit.Sts2.Core.Commands.CardCmd.Upgrade(card, default);
                Ctx.RunUntil(MegaCrit.Sts2.Core.Commands.CardPileCmd.Add(card, PileType.Deck, CardPilePosition.Bottom, null, true), "add card");
            }
        }
        Mark("deck");
        if (spec["relics"] is JsonArray relics)
        {
            // "relic_pickup": false adds each relic without its pickup effect: for situations taken from a recorded run,
            // whose deck and max HP already include those effects (tools/fight_specs.py)
            var pickup = (bool?)spec["relic_pickup"] ?? true;
            var have = me.Relics.Select(r => r.Id.Entry).ToHashSet();
            foreach (var id in relics.Select(x => (string)x))
            {
                if (!pickup && have.Contains(id)) continue;       // the starting relic is already there
                var relic = ById(ModelDb.AllRelics, id, "relic").ToMutable();
                if (pickup) Ctx.RunUntil(MegaCrit.Sts2.Core.Commands.RelicCmd.Obtain(relic, me, me.Relics.Count), "add relic");
                else me.AddRelicInternal(relic, me.Relics.Count, true);
            }
        }
        if (spec["potions"] is JsonArray potions)
            foreach (var id in potions.Select(x => (string)x))
                Ctx.RunUntil(MegaCrit.Sts2.Core.Commands.PotionCmd.TryToProcure(ById(ModelDb.AllPotions, id, "potion").ToMutable(), me, -1), "add potion");
        if (spec["max_hp"] != null) Ctx.RunUntil(MegaCrit.Sts2.Core.Commands.CreatureCmd.SetMaxHp(me.Creature, (int)spec["max_hp"]), "set max HP");
        if (spec["hp"] != null) Ctx.RunUntil(MegaCrit.Sts2.Core.Commands.CreatureCmd.SetCurrentHp(me.Creature, (int)spec["hp"]), "set HP");
        Mark("relics_potions_hp");
        var encounter = ById(ModelDb.AllEncounters, (string)spec["encounter"], "encounter").ToMutable();
        var point = encounter.RoomType switch
        {
            MegaCrit.Sts2.Core.Rooms.RoomType.Elite => MegaCrit.Sts2.Core.Map.MapPointType.Elite,
            MegaCrit.Sts2.Core.Rooms.RoomType.Boss => MegaCrit.Sts2.Core.Map.MapPointType.Boss,
            _ => MegaCrit.Sts2.Core.Map.MapPointType.Monster,
        };
        Ctx.RunUntil(Rm.EnterRoomDebug(encounter.RoomType, point, encounter, false), "enter the encounter");
        Ctx.Drain();
        Mark("enter_room");
        Sanitizer.Apply(this, sampleSeed);
        Mark("sanitize");
        Sanitized = true;
        Choices.Intercept = true;
        NoteOrigin("fight", spec, 0, sampleSeed);
    }

    // A recorded event the player decided: a card, a potion or ending the turn. Choice answers, resumes and the
    // "ready for the enemy turn" signal follow from those and are applied with them.
    bool IsDecision(CombatReplayEvent ev)
    {
        if (ev.eventType.ToString() != "GameAction") return false;
        var name = ev.action.ToGameAction(Run.GetPlayer(ev.playerId.Value)).GetType().Name;
        return name != "ReadyToBeginEnemyTurnAction";
    }

    void ApplyRecorded(CombatReplayEvent ev)
    {
        Ctx.Drain();
        switch (ev.eventType.ToString())
        {
            case "GameAction": Rm.ActionQueueSet.EnqueueWithoutSynchronizing(ev.action.ToGameAction(Run.GetPlayer(ev.playerId.Value))); break;
            case "HookAction": Rm.ActionQueueSet.EnqueueWithoutSynchronizing(Rm.ActionQueueSynchronizer.GetHookActionForId(ev.hookId.Value, ev.playerId.Value, ev.gameActionType.Value)); break;
            case "ResumeAction": Rm.ActionQueueSet.ResumeActionWithoutSynchronizing(ev.actionId.Value); break;
            case "PlayerChoice": Rm.PlayerChoiceSynchronizer.ReceiveReplayChoice(Run.GetPlayer(ev.playerId.Value), ev.choiceId.Value, ev.playerChoiceResult.Value); break;
        }
        Ctx.Drain();
        Applied++;
    }

    // Test of the stepping path (not a decision): replays the recorded fight with its true random state, but builds the
    // card plays and end-of-turn actions the way Step does instead of using the recorded action objects. The result
    // must equal the recorded fight's. Recorded potions, choices and resumes are applied as recorded.
    public JsonObject OwnActionsReplay()
    {
        Reset(0, null);
        static T Find<T>(object o) where T : class
        {
            for (var t = o.GetType(); t != null && t != typeof(object); t = t.BaseType)
                foreach (var f in t.GetFields(System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.DeclaredOnly))
                    if (typeof(T).IsAssignableFrom(f.FieldType) && f.GetValue(o) is T v) return v;
            foreach (var pr in o.GetType().GetProperties(System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic))
                if (typeof(T).IsAssignableFrom(pr.PropertyType) && pr.GetIndexParameters().Length == 0 && pr.GetValue(o) is T v2) return v2;
            return null;
        }
        // a recorded play names its card by a combat-wide card reference; turn it back into the card object
        CardModel ResolveCard(PlayCardAction a)
        {
            if (Find<CardModel>(a) is { } direct) return direct;
            object reference = a.NetCombatCard;
            var m = reference.GetType().GetMethods(System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic)
                .FirstOrDefault(x => x.ReturnType == typeof(CardModel) && x.GetParameters().Length == 0);
            return m?.Invoke(reference, null) as CardModel;
        }
        int own = 0, recorded = 0;
        while (Applied < Replay.events.Count)
        {
            var ev = Replay.events[Applied];
            var ga = ev.eventType.ToString() == "GameAction" ? ev.action.ToGameAction(Run.GetPlayer(ev.playerId.Value)) : null;
            Ctx.Drain();
            if (ga is PlayCardAction pca && ResolveCard(pca) is { } card)
            {
                Enqueue(new PlayCardAction(card, pca.Target));
                Applied++; own++;
            }
            else if (ga is EndPlayerTurnAction)
            {
                Enqueue(new EndPlayerTurnAction(Me, Me.PlayerCombatState.TurnNumber));
                Applied++; own++;
                if (Applied < Replay.events.Count && Replay.events[Applied].eventType.ToString() == "GameAction"
                    && Replay.events[Applied].action.ToGameAction(Me) is ReadyToBeginEnemyTurnAction)
                {
                    if (Status() == "in_progress") Enqueue(new ReadyToBeginEnemyTurnAction(Me, null));
                    Applied++; own++;
                }
            }
            else { ApplyRecorded(ev); recorded++; }
        }
        Ctx.Drain();
        return new JsonObject { ["status"] = Status(), ["hp"] = Me.Creature.CurrentHp, ["own_actions"] = own, ["recorded_events"] = recorded };
    }

    public List<int> DecisionPoints()
    {
        var points = new List<int>();
        for (var i = 0; i < Replay.events.Count; i++) if (IsDecision(Replay.events[i])) points.Add(i);
        return points;
    }

    public string Status()
    {
        if (Me.Creature.IsDead) return "lost";
        return CombatManager.Instance.IsInProgress ? "in_progress" : "won";
    }

    // True while an action is waiting for something only the player can give (a card choice prompt).
    public bool Waiting => Choices.Current != null;

    // True when the last action did not finish and no card choice explains it (a prompt the host does not handle yet).
    GameAction _last;
    public bool Blocked => Choices.Current == null && _last != null && _last.State.ToString() is not ("Finished" or "Canceled");

    List<Creature> Enemies => Combat.Enemies.ToList();

    public JsonArray Legal()
    {
        var acts = new JsonArray();
        if (Choices.Current is { } ch)   // a pending card, relic or bundle choice: in a fight or anywhere in the run
        {
            // one card: every option (and "none" if allowed); several: the first combinations of exactly Max cards
            if (ch.Min == 0) acts.Add(new JsonObject { ["type"] = "choose", ["cards"] = new JsonArray() });
            var labels = ch.Labels().ToList();
            if (ch.Max <= 1 || ch.Min != ch.Max)
                for (var i = 0; i < ch.Count; i++) acts.Add(new JsonObject { ["type"] = "choose", ["cards"] = new JsonArray(i), ["card_id"] = labels[i] });
            else
                foreach (var combo in Combinations(ch.Count, ch.Max).Take(40))
                    acts.Add(new JsonObject { ["type"] = "choose", ["cards"] = new JsonArray(combo.Select(i => (JsonNode)i).ToArray()) });
            return acts;
        }
        if (Status() != "in_progress" || Blocked) return acts;
        var hand = Me.PlayerCombatState.Hand.Cards.ToList();
        var enemies = Enemies;
        for (var i = 0; i < hand.Count; i++)
        {
            var c = hand[i];
            if (!c.CanPlay()) continue;
            if (c.TargetType == TargetType.AnyEnemy)
            {
                for (var j = 0; j < enemies.Count; j++)
                    if (enemies[j].IsAlive && enemies[j].IsHittable && c.IsValidTarget(enemies[j]))
                        acts.Add(new JsonObject { ["type"] = "play", ["card"] = i, ["target"] = j, ["card_id"] = c.Id.Entry });
            }
            else acts.Add(new JsonObject { ["type"] = "play", ["card"] = i, ["card_id"] = c.Id.Entry });
        }
        var slots = Me.PotionSlots;
        for (var k = 0; k < slots.Count; k++)
        {
            var p = slots[k];
            if (p == null || p.Usage.ToString() == "Automatic" || !p.PassesCustomUsabilityCheck) continue;
            if (p.TargetType == TargetType.AnyEnemy)
            {
                for (var j = 0; j < enemies.Count; j++)
                    if (enemies[j].IsAlive && enemies[j].IsHittable && p.IsValidTarget(enemies[j]))
                        acts.Add(new JsonObject { ["type"] = "potion", ["slot"] = k, ["target"] = j, ["potion_id"] = p.Id.Entry });
            }
            else acts.Add(new JsonObject { ["type"] = "potion", ["slot"] = k, ["potion_id"] = p.Id.Entry });
        }
        acts.Add(new JsonObject { ["type"] = "end_turn" });
        return acts;
    }

    static IEnumerable<int[]> Combinations(int n, int k)
    {
        var idx = Enumerable.Range(0, k).ToArray();
        while (true)
        {
            yield return (int[])idx.Clone();
            var i = k - 1;
            while (i >= 0 && idx[i] == n - k + i) i--;
            if (i < 0) yield break;
            idx[i]++;
            for (var j = i + 1; j < k; j++) idx[j] = idx[j - 1] + 1;
        }
    }

    void Enqueue(GameAction a) { _last = a; Rm.ActionQueueSet.EnqueueWithoutSynchronizing(a); Ctx.Drain(); }

    public void Step(JsonNode action)
    {
        if (!Sanitized && !_rebuilding) throw new InvalidOperationException("decision mode needs a sanitized state: reset with a sample seed (FP-3, FP-15)");
        if (Status() != "in_progress") throw new InvalidOperationException("the fight is over");
        Ctx.Drain();
        var type = (string)action["type"];
        if (type == "choose")
        {
            Choices.Answer(action["cards"]!.AsArray().Select(x => (int)x).ToList());
            Ctx.Drain();
            // an end of turn interrupted by a choice continues with the enemy turn once the choice is made
            if (_last is EndPlayerTurnAction && _last.State.ToString() == "Finished" && Choices.Current == null && Status() == "in_progress")
                Enqueue(new ReadyToBeginEnemyTurnAction(Me, null));
            return;
        }
        if (Choices.Current != null) throw new InvalidOperationException("a card choice is pending: answer it first");
        if (type == "play")
        {
            var hand = Me.PlayerCombatState.Hand.Cards.ToList();
            var card = hand[(int)action["card"]];
            Creature target = action["target"] != null ? Enemies[(int)action["target"]] : null;
            Enqueue(new PlayCardAction(card, target));
        }
        else if (type == "potion")
        {
            var potion = Me.PotionSlots[(int)action["slot"]] ?? throw new ArgumentException("that potion slot is empty");
            // an enemy for targeted potions; the drinker for potions aimed at a player; nothing for the rest
            Creature target = potion.TargetType == TargetType.AnyEnemy ? Enemies[(int)action["target"]]
                : potion.TargetType is TargetType.Self or TargetType.AnyPlayer or TargetType.AnyAlly ? Me.Creature : null;
            Enqueue(new UsePotionAction(potion, target, true));
        }
        else if (type == "end_turn")
        {
            Enqueue(new EndPlayerTurnAction(Me, Me.PlayerCombatState.TurnNumber));
            if (Status() == "in_progress" && Choices.Current == null) Enqueue(new ReadyToBeginEnemyTurnAction(Me, null));
        }
        else throw new ArgumentException("unknown action type " + type);
    }

    static JsonArray Powers(Creature c)
    {
        var a = new JsonArray();
        foreach (var p in c.Powers) a.Add(new JsonObject { ["power_id"] = p.Id.Entry, ["amount"] = p.Amount });
        return a;
    }

    // The observation, in the shape of the live API's state (the fields tools/plan_turn.py reads), so the same code
    // reads live and simulated fights (ML-1).
    public JsonObject Observe()
    {
        var pcs = Me.PlayerCombatState;
        var me = Me.Creature;
        var players = Combat.Players.Select(p => p.Creature).ToArray();
        var hand = new JsonArray();
        var cards = pcs.Hand.Cards.ToList();
        for (var i = 0; i < cards.Count; i++)
        {
            var c = cards[i];
            var values = new JsonArray();
            var preview = c.DynamicVars.Clone(c);
            c.UpdateDynamicVarPreview(CardPreviewMode.Normal, c.CurrentTarget, preview);
            foreach (var v in preview.Values) values.Add(new JsonObject { ["name"] = v.Name, ["current_value"] = (int)v.PreviewValue, ["base_value"] = (int)v.BaseValue });
            hand.Add(new JsonObject
            {
                ["index"] = i, ["card_id"] = c.Id.Entry, ["upgraded"] = c.IsUpgraded, ["target_type"] = c.TargetType.ToString(),
                ["energy_cost"] = c.EnergyCost.GetWithModifiers(CostModifiers.All), ["playable"] = c.CanPlay(), ["dynamic_values"] = values,
            });
        }
        var enemies = new JsonArray();
        var list = Enemies;
        for (var j = 0; j < list.Count; j++)
        {
            var e = list[j];
            var intents = new JsonArray();
            foreach (var intent in e.Monster?.NextMove?.Intents ?? Array.Empty<AbstractIntent>())
            {
                var o = new JsonObject { ["intent_type"] = intent.IntentType.ToString() };
                if (intent is AttackIntent a)
                {
                    o["damage"] = a.GetSingleDamage(players, e);
                    o["hits"] = Math.Max(1, a.Repeats);
                    o["total_damage"] = a.GetTotalDamage(players, e);
                }
                intents.Add(o);
            }
            enemies.Add(new JsonObject
            {
                ["index"] = j, ["enemy_id"] = e.ModelId.Entry, ["name"] = e.ModelId.Entry, ["current_hp"] = e.CurrentHp, ["max_hp"] = e.MaxHp,
                ["block"] = e.Block, ["is_alive"] = e.IsAlive, ["is_hittable"] = e.IsHittable, ["powers"] = Powers(e), ["intents"] = intents,
            });
        }
        JsonArray Ids(IEnumerable<CardModel> pile) => new(pile.Select(c => c.Id.Entry + (c.IsUpgraded ? "+" : "")).OrderBy(s => s, StringComparer.Ordinal).Select(s => (JsonNode)s).ToArray());
        var relics = new JsonArray(Me.Relics.Select(r => (JsonNode)new JsonObject { ["relic_id"] = r.Id.Entry }).ToArray());
        var potions = new JsonArray();
        var slots = Me.PotionSlots;
        for (var k = 0; k < slots.Count; k++)
            potions.Add(new JsonObject { ["index"] = k, ["occupied"] = slots[k] != null, ["potion_id"] = slots[k]?.Id.Entry });
        return new JsonObject
        {
            ["screen"] = "COMBAT", ["status"] = Status(), ["turn"] = pcs.TurnNumber, ["waiting_for_choice"] = Waiting, ["blocked"] = Blocked,
            ["choice"] = Choices.Current is { } pc ? new JsonObject { ["kind"] = pc.Kind, ["min"] = pc.Min, ["max"] = pc.Max,
                ["options"] = new JsonArray(pc.Labels().Select(x => (JsonNode)x).ToArray()) } : null,
            ["applied_events"] = Applied, ["sanitized"] = Sanitized, ["player_index"] = PlayerIndex, ["players"] = Run.Players.Count,
            ["run"] = new JsonObject { ["ascension"] = Run.AscensionLevel, ["max_hp"] = me.MaxHp, ["current_hp"] = me.CurrentHp, ["relics"] = relics, ["potions"] = potions },
            ["combat"] = new JsonObject
            {
                ["player"] = new JsonObject { ["current_hp"] = me.CurrentHp, ["max_hp"] = me.MaxHp, ["block"] = me.Block, ["energy"] = pcs.Energy, ["powers"] = Powers(me) },
                ["hand"] = hand, ["enemies"] = enemies,
                ["draw_pile_count"] = pcs.DrawPile.Cards.Count, ["discard_pile_count"] = pcs.DiscardPile.Cards.Count, ["exhaust_pile_count"] = pcs.ExhaustPile.Cards.Count,
                // contents only, sorted: the order of the draw pile is hidden information (FP-1)
                ["draw_pile"] = Ids(pcs.DrawPile.Cards), ["discard_pile"] = Ids(pcs.DiscardPile.Cards), ["exhaust_pile"] = Ids(pcs.ExhaustPile.Cards),
            },
        };
    }

    // For tests only: the true draw order and generator states, to prove that sanitizing changes them and that
    // observations do not depend on them. Never part of an observation.
    public JsonObject Hidden()
    {
        var order = new JsonArray(Me.PlayerCombatState.DrawPile.Cards.Select(c => (JsonNode)(c.Id.Entry + (c.IsUpgraded ? "+" : ""))).ToArray());
        return new JsonObject { ["draw_order"] = order, ["generators"] = Sanitizer.Fingerprint(this), ["known"] = DrawKnowledge.Known(Me.PlayerCombatState.DrawPile) };
    }

    public object[] Roots() => new object[] { Run, Combat };

    public string LastAction() => _last == null ? "none" : $"{_last.GetType().Name} in state {_last.State}";
}
