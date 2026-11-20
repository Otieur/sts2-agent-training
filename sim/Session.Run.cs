// Run mode: a whole run in the host, from a seed to its end (stage 2 of the 2026-11-20 night).
//
// The run is created the way the game creates a new single-player run (NGame.StartNewSingleplayerRun, NGame.StartRun):
// Player.CreateForNewRun, RunState.CreateForNewRun, RunManager.SetUpNewSingleplayer, FinalizeStartingRelics, Launch,
// EnterAct(0). After that the host never touches game state directly: every step goes through the same game calls the
// interface would make (the event, rest-site, rewards and treasure synchronizers, which are also the co-op paths).
//
// Screens: combat, choice (any card, relic or bundle pick), rewards, event (the Ancient is an event), rest, shop,
// treasure, map, game_over. The policy sees the screen, its options and the observation; it answers with an action.
using System.Text.Json.Nodes;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Merchant;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;

public sealed partial class Session
{
    public bool RunMode;
    public string RunSeed = "";
    RewardsSet _rewards;                       // the rewards set on offer, captured from the synchronizer
    object _rewardsRoom;                       // the room whose end-of-room rewards were offered already
    object _doneRoom;                          // the rest site, shop or treasure room that has been finished
    object _chestRoom;                         // the treasure room whose chest has been opened
    Task _pending;                             // a game task still running from the last run-level action
    readonly HashSet<Reward> _failedRewards = new();   // rewards a take attempt did not claim (no room, refused, declined)
    Reward _lastReward;                                // the reward whose selection is in progress
    public int Floor => Run?.TotalFloor ?? 0;
    public bool Victory;
    public bool TestHp;                        // the run used the test-only max-HP switch: flow test, not play
    public string UnlockSource = "all";        // where the run's unlock state came from

    static bool _hooked;

    // Catches every rewards set the game offers (RewardsSetSynchronizer.BeginRewardsSet), so the host can show it.
    static Session _current;
    public static void HookRewards()
    {
        if (_hooked) return;
        _hooked = true;
        var m = typeof(MegaCrit.Sts2.Core.Multiplayer.Game.RewardsSetSynchronizer).GetMethod("BeginRewardsSet")!;
        Stubs.H.Patch(m, postfix: new HarmonyLib.HarmonyMethod(typeof(Session).GetMethod(nameof(OnRewardsBegun), System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic)));
    }

    static void OnRewardsBegun(RewardsSet set) { if (_current != null) _current._rewards = set; }

    public void NewRun(JsonNode spec, ulong sampleSeed)
    {
        HookRewards();
        _current = this;
        SynchronizationContext.SetSynchronizationContext(Ctx);
        if (Run != null) { Rm.CleanUp(true); Ctx.Drain(); }
        Replay = null;
        Choices.Current = null;
        _last = null; _pending = null; _rewards = null; _rewardsRoom = null; _doneRoom = null; _chestRoom = null;
        _failedRewards.Clear();
        Applied = 0; PlayerIndex = 0; Victory = false;
        var character = ById(ModelDb.AllCharacters, (string)spec["character"] ?? "IRONCLAD", "character");
        // Unlocks decide which cards, relics and potions can appear (FI-5). Default: everything. With "unlocks_from":
        // the unlock state stored in a recorded fight of the profile (the replay's run carries the player's unlocks).
        var unlocks = MegaCrit.Sts2.Core.Unlocks.UnlockState.all;
        UnlockSource = "all";
        if (spec["unlocks_from"] != null)
        {
            var rec = global::Replay.Load((string)spec["unlocks_from"]);
            unlocks = MegaCrit.Sts2.Core.Unlocks.UnlockState.FromSerializable(rec.serializableRun.Players[0].UnlockState);
            UnlockSource = Path.GetFileName((string)spec["unlocks_from"]);
        }
        var players = new List<Player> { Player.CreateForNewRun(character, unlocks, 1UL) };
        var acts = ActModel.GetDefaultList().Select(a => a.ToMutable()).ToList();
        RunSeed = (string)spec["seed"] ?? "SIMRUN000001";
        Run = RunState.CreateForNewRun(players, acts, Array.Empty<ModifierModel>(), GameMode.Standard, (int?)spec["ascension"] ?? 0, RunSeed);
        Rm.SetUpNewSingleplayer(Run, false, null);
        Rm.CombatStateSynchronizer.IsDisabled = true;
        Rm.ChecksumTracker.IsEnabled = false;
        Ctx.RunUntil(Rm.FinalizeStartingRelics(), "FinalizeStartingRelics");
        Rm.Launch();
        // Test-only switch for exercising the whole flow (rest sites, treasure, bosses, act changes) with a weak driver:
        // a very large max HP. Never used for learning, evaluation or any reported play result.
        if (spec["test_max_hp"] != null)
        {
            Ctx.RunUntil(MegaCrit.Sts2.Core.Commands.CreatureCmd.SetMaxHp(Me.Creature, (int)spec["test_max_hp"]), "test max HP");
            Ctx.RunUntil(MegaCrit.Sts2.Core.Commands.CreatureCmd.SetCurrentHp(Me.Creature, (int)spec["test_max_hp"]), "test HP");
            TestHp = true;
        }
        RunMode = true;
        // Decision mode from the first floor: the run's own seed shapes the map, encounters and rewards exactly as in
        // the real game (FP-9 forbids reading them; nothing in the observation shows them before they happen). A
        // sample seed re-seeds the generators only when the policy asks for a sampled future (search), not here.
        Sanitized = true;
        Choices.Intercept = true;
        Track(Rm.EnterAct(0, false));
    }

    void Track(Task t) { _pending = t; Ctx.Drain(); Settle(); }

    // Runs queued game work until nothing more happens without a decision.
    void Settle()
    {
        for (var i = 0; i < 200; i++)
        {
            var progressed = Ctx.Drain() > 0;
            if (_pending != null && _pending.IsCompleted)
            {
                if (_pending.IsFaulted) { var e = _pending.Exception!.GetBaseException(); _pending = null; throw new InvalidOperationException("game task failed: " + e.GetType().Name + ": " + e.Message); }
                _pending = null;
                progressed = true;
            }
            if (!progressed) break;
        }
    }

    public string Screen()
    {
        if (!RunMode) return "combat";
        if (Victory) return "game_over";
        if (Me.Creature.IsDead || Rm.IsGameOver || Run.IsGameOver) return "game_over";
        if (Choices.Current != null) return "choice";
        var room = Run.CurrentRoom;
        if (room is CombatRoom && CombatManager.Instance.IsInProgress) return "combat";
        if (_rewards != null && !Rm.RewardsSetSynchronizer.IsRewardsSetCompleted(_rewards)) return "rewards";
        if (room is CombatRoom cr && _rewardsRoom != room && !CombatManager.Instance.IsInProgress)
        {
            _rewardsRoom = room;
            _rewards = null;
            Track(MegaCrit.Sts2.Core.Commands.RewardsCmd.OfferForRoomEnd(Me, cr));
            return Screen();
        }
        if (room is EventRoom && Rm.EventSynchronizer.GetLocalEvent() is { IsFinished: false }) return "event";
        if (room is RestSiteRoom && _doneRoom != room) return "rest";
        if (room is MerchantRoom && _doneRoom != room) return "shop";
        if (room is TreasureRoom && _doneRoom != room) return "treasure";
        return "map";
    }

    // Next map points the player may move to. At the boss point, the next act.
    List<MapPoint> NextPoints()
    {
        var here = Run.CurrentMapPoint;
        // At the start of acts 2 and 3 the player stands on the map before the act's first point, the Ancient.
        // (Act 1 enters Neow directly.)
        if (here == null) return new List<MapPoint> { Run.Map.StartingMapPoint };
        return here.Children.OrderBy(p => p.coord.col).ToList();
    }

    bool AtBoss => Run.CurrentMapPoint != null && (Run.CurrentMapPoint == Run.Map.BossMapPoint || Run.CurrentMapPoint == Run.Map.SecondBossMapPoint)
                   && Run.CurrentMapPoint.Children.Count == 0;

    public JsonArray RunLegal()
    {
        var acts = new JsonArray();
        switch (Screen())
        {
            case "combat": case "choice": return Legal();
            case "rewards":
            {
                var list = _rewards.Rewards;
                for (var i = 0; i < list.Count; i++)
                {
                    if (list[i].SuccessfullySelected || _failedRewards.Contains(list[i])) continue;
                    if (list[i] is PotionReward && !Me.HasOpenPotionSlots) continue;   // no room: discard a potion first
                    acts.Add(new JsonObject { ["type"] = "take_reward", ["index"] = i, ["reward"] = list[i].GetType().Name });
                }
                if (list.Any(r => r is PotionReward && !r.SuccessfullySelected) && !Me.HasOpenPotionSlots)
                    AddDiscards(acts);
                if (!_rewards.DisallowSkipping) acts.Add(new JsonObject { ["type"] = "skip_rewards" });
                break;
            }
            case "event":
            {
                var opts = Rm.EventSynchronizer.GetLocalEvent()!.CurrentOptions;
                for (var i = 0; i < opts.Count; i++)
                    if (!opts[i].IsLocked) acts.Add(new JsonObject { ["type"] = "event_option", ["index"] = i, ["key"] = opts[i].TextKey });
                break;
            }
            case "rest":
            {
                var opts = Rm.RestSiteSynchronizer.GetLocalOptions();
                for (var i = 0; i < opts.Count; i++)
                    if (opts[i].IsEnabled) acts.Add(new JsonObject { ["type"] = "rest_option", ["index"] = i, ["option"] = opts[i].OptionId });
                acts.Add(new JsonObject { ["type"] = "leave" });
                break;
            }
            case "shop":
            {
                var inv = ((MerchantRoom)Run.CurrentRoom).GetLocalInventory();
                var entries = inv.AllEntries.ToList();
                for (var i = 0; i < entries.Count; i++)
                    if (entries[i].IsStocked && entries[i].EnoughGold) acts.Add(new JsonObject { ["type"] = "buy", ["index"] = i, ["item"] = ShopLabel(entries[i]), ["cost"] = entries[i].Cost });
                acts.Add(new JsonObject { ["type"] = "leave" });
                break;
            }
            case "treasure":
                if (_chestRoom != Run.CurrentRoom) acts.Add(new JsonObject { ["type"] = "open_chest" });
                else
                {
                    var relics = Rm.TreasureRoomRelicSynchronizer.CurrentRelics;
                    for (var i = 0; i < (relics?.Count ?? 0); i++) acts.Add(new JsonObject { ["type"] = "pick_relic", ["index"] = i, ["relic"] = relics[i].Id.Entry });
                    acts.Add(new JsonObject { ["type"] = "leave" });
                }
                break;
            case "map":
                if (AtBoss) acts.Add(new JsonObject { ["type"] = "next_act" });
                else
                {
                    var pts = NextPoints();
                    for (var i = 0; i < pts.Count; i++)
                        acts.Add(new JsonObject { ["type"] = "move", ["index"] = i, ["point"] = pts[i].PointType.ToString(), ["col"] = pts[i].coord.col, ["row"] = pts[i].coord.row });
                }
                break;
        }
        return acts;
    }

    void AddDiscards(JsonArray acts)
    {
        var slots = Me.PotionSlots;
        for (var k = 0; k < slots.Count; k++)
            if (slots[k] != null) acts.Add(new JsonObject { ["type"] = "discard_potion", ["slot"] = k, ["potion_id"] = slots[k].Id.Entry });
    }

    static string ShopLabel(MerchantEntry e) => e switch
    {
        MerchantCardEntry c => "card:" + (c.CreationResult?.Card?.Id.Entry ?? "sold"),
        MerchantRelicEntry r => "relic:" + (r.Model?.Id.Entry ?? "sold"),
        MerchantPotionEntry p => "potion:" + (p.Model?.Id.Entry ?? "sold"),
        _ => "removal",
    };

    public void RunStep(JsonNode action)
    {
        var type = (string)action["type"];
        var screen = Screen();
        if (type is "play" or "end_turn" or "potion" or "choose")
        {
            if (screen is not ("combat" or "choice")) throw new InvalidOperationException($"'{type}' is not possible on the {screen} screen");
            if (screen == "choice" || type == "choose")
            {
                var kind = Choices.Current?.Kind;
                var picks = action["cards"]!.AsArray().Select(x => (int)x).ToList();
                Choices.Answer(picks);
                Ctx.Drain(); Settle();
                // a card reward closed without a pick is declined: it is not offered again
                if (kind == "CardReward" && picks.Count == 0 && _lastReward != null) _failedRewards.Add(_lastReward);
                return;
            }
            Step(action);
            Settle();
            return;
        }
        switch (type)
        {
            case "take_reward":
            {
                var reward = _rewards.Rewards[(int)action["index"]];
                _lastReward = reward;
                Track(Rm.RewardsSetSynchronizer.SelectLocalReward(reward));
                if (!reward.SuccessfullySelected && Choices.Current == null) _failedRewards.Add(reward);
                break;
            }
            case "discard_potion":
                Enqueue(new MegaCrit.Sts2.Core.GameActions.DiscardPotionGameAction(Me, (uint)(int)action["slot"], CombatManager.Instance.IsInProgress));
                Settle();
                break;
            case "skip_rewards":
                Rm.RewardsSetSynchronizer.SkipLocalRewardsSet();
                Ctx.Drain();
                FinishRewards();
                break;
            case "event_option":
                Rm.EventSynchronizer.ChooseLocalOption((int)action["index"]);
                Ctx.Drain();
                Track(Rm.EventSynchronizer.AwaitPendingOptionTasks());
                break;
            case "rest_option":
                Track(Rm.RestSiteSynchronizer.ChooseLocalOption((int)action["index"]));
                if (Choices.Current == null) _doneRoom = Run.CurrentRoom;
                break;
            case "buy":
            {
                var inv = ((MerchantRoom)Run.CurrentRoom).GetLocalInventory();
                Track(inv.AllEntries.ToList()[(int)action["index"]].OnTryPurchaseWrapper(inv, false));
                break;
            }
            case "open_chest":
                _chestRoom = Run.CurrentRoom;
                Track(((TreasureRoom)Run.CurrentRoom).DoNormalRewards());
                break;
            case "pick_relic":
                Rm.TreasureRoomRelicSynchronizer.PickRelicLocally((int)action["index"]);
                Ctx.Drain(); Settle();
                _doneRoom = Run.CurrentRoom;
                break;
            case "leave":
                if (screen == "treasure") { Rm.TreasureRoomRelicSynchronizer.SkipRelicLocally(); Ctx.Drain(); }
                _doneRoom = Run.CurrentRoom;
                Settle();
                break;
            case "move":
            {
                var pt = NextPoints()[(int)action["index"]];
                _rewards = null;
                Track(Rm.EnterMapCoord(pt.coord));
                break;
            }
            case "next_act":
                _rewards = null;
                if (Run.CurrentActIndex >= Run.Acts.Count - 1) { Victory = true; break; }
                Track(Rm.EnterNextAct());
                break;
            default: throw new ArgumentException("unknown action type " + type);
        }
    }

    // After the last reward is taken or the set is skipped, the interface's proceed button calls this.
    void FinishRewards()
    {
        _rewards = null;
        Track(Rm.ProceedFromTerminalRewardsScreen());
    }

    public void AfterRewardTaken()
    {
        if (_rewards != null && Rm.RewardsSetSynchronizer.IsRewardsSetCompleted(_rewards) && Choices.Current == null) FinishRewards();
    }

    public JsonObject RunObserve()
    {
        var screen = Screen();
        var o = screen == "combat" || screen == "choice" && Run.CurrentRoom is CombatRoom && CombatManager.Instance.IsInProgress ? Observe() : new JsonObject();
        o["screen"] = screen;
        o["run_seed_hidden"] = true;
        o["act"] = Run.CurrentActIndex + 1;
        o["floor"] = Run.TotalFloor;
        o["act_floor"] = Run.ActFloor;
        o["room"] = Run.CurrentRoom?.GetType().Name;
        var me = Me;
        o["player"] = new JsonObject
        {
            ["hp"] = me.Creature.CurrentHp, ["max_hp"] = me.Creature.MaxHp, ["gold"] = me.Gold,
            ["deck"] = new JsonArray(me.Deck.Cards.Select(c => (JsonNode)(c.Id.Entry + (c.IsUpgraded ? "+" : ""))).ToArray()),
            ["relics"] = new JsonArray(me.Relics.Select(r => (JsonNode)r.Id.Entry).ToArray()),
            ["potions"] = new JsonArray(me.PotionSlots.Select(p => (JsonNode)(p?.Id.Entry)).ToArray()),
        };
        o["test_hp"] = TestHp;
        o["unlocks"] = UnlockSource;
        o["player_index"] = PlayerIndex;
        o["players"] = Run.Players.Count;
        if (Choices.Current is { } pc)
            o["choice"] = new JsonObject { ["kind"] = pc.Kind, ["min"] = pc.Min, ["max"] = pc.Max, ["options"] = new JsonArray(pc.Labels().Select(x => (JsonNode)x).ToArray()) };
        switch (screen)
        {
            case "rewards":
                o["rewards"] = new JsonArray(_rewards.Rewards.Select(r => (JsonNode)new JsonObject
                {
                    ["type"] = r.GetType().Name, ["taken"] = r.SuccessfullySelected,
                    ["detail"] = r switch
                    {
                        GoldReward => null, CardReward cr => string.Join(",", cr.Cards.Select(c => c.Id.Entry)),
                        RelicReward rr => rr.ClaimedRelic?.Id.Entry, PotionReward pr => pr.Potion?.Id.Entry, _ => null,
                    },
                }).ToArray());
                break;
            case "event":
            {
                var ev = Rm.EventSynchronizer.GetLocalEvent()!;
                o["event"] = new JsonObject
                {
                    ["id"] = ev.Id.Entry, ["ancient"] = ev is AncientEventModel,
                    ["options"] = new JsonArray(ev.CurrentOptions.Select(x => (JsonNode)new JsonObject { ["key"] = x.TextKey, ["locked"] = x.IsLocked, ["relic"] = x.Relic?.Id.Entry, ["proceed"] = x.IsProceed }).ToArray()),
                };
                break;
            }
            case "map":
                o["next"] = new JsonArray(NextPoints().Select(p => (JsonNode)new JsonObject { ["type"] = p.PointType.ToString(), ["col"] = p.coord.col, ["row"] = p.coord.row }).ToArray());
                o["at_boss"] = AtBoss;
                break;
            case "shop":
            {
                var inv = ((MerchantRoom)Run.CurrentRoom).GetLocalInventory();
                o["shop"] = new JsonArray(inv.AllEntries.Select(e => (JsonNode)new JsonObject { ["item"] = ShopLabel(e), ["cost"] = e.Cost, ["stocked"] = e.IsStocked }).ToArray());
                break;
            }
            case "treasure":
                o["chest"] = new JsonArray((Rm.TreasureRoomRelicSynchronizer.CurrentRelics ?? Array.Empty<RelicModel>()).Select(r => (JsonNode)r.Id.Entry).ToArray());
                break;
        }
        // what the player sees on entering a fight: the encounter and its monsters
        if (Run.CurrentRoom is CombatRoom room)
        {
            o["encounter"] = room.Encounter?.Id.Entry;
            o["monsters"] = new JsonArray((room.CombatState?.Enemies ?? Enumerable.Empty<MegaCrit.Sts2.Core.Entities.Creatures.Creature>()).Select(c => (JsonNode)c.ModelId.Entry).ToArray());
        }
        if (Run.CurrentRoom is EventRoom er) o["event_id"] = er.CanonicalEvent?.Id.Entry;
        return o;
    }

    // Fidelity tests only (never a decision, docs/simulator-integrity.md FP-2): how many numbers each named random
    // stream has produced so far, to find where a replay's random state drifts from the recorded run.
    public JsonObject DebugRngCounters()
    {
        var f = typeof(MegaCrit.Sts2.Core.Random.Rng).GetField("_counter", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic)!;
        var o = new JsonObject();
        foreach (var set in new object[] { Run.Rng, Me.PlayerRng })
            foreach (var pr in set.GetType().GetProperties().Where(x => x.PropertyType == typeof(MegaCrit.Sts2.Core.Random.Rng)))
                o[pr.Name] = (int)f.GetValue(pr.GetValue(set))!;
        return o;
    }

    // The act map, as the player sees it on the map screen: every point, its type and the points it leads to.
    public JsonObject MapView()
    {
        var map = Run.Map;
        var pts = new JsonArray();
        var all = map.GetAllMapPoints().ToList();
        foreach (var extra in new[] { map.StartingMapPoint, map.BossMapPoint, map.SecondBossMapPoint })
            if (extra != null && !all.Contains(extra)) all.Add(extra);   // the start (Ancient) and boss points sit outside the grid
        foreach (var p in all)
            pts.Add(new JsonObject { ["col"] = p.coord.col, ["row"] = p.coord.row, ["type"] = p.PointType.ToString(),
                                     ["children"] = new JsonArray(p.Children.Select(c => (JsonNode)new JsonArray(c.coord.col, c.coord.row)).ToArray()) });
        var start = map.StartingMapPoint;
        return new JsonObject { ["act"] = Run.CurrentActIndex + 1, ["points"] = pts, ["start"] = new JsonArray(start.coord.col, start.coord.row),
                                ["boss"] = new JsonArray(map.BossMapPoint.coord.col, map.BossMapPoint.coord.row),
                                ["here"] = Run.CurrentMapPoint == null ? null : new JsonArray(Run.CurrentMapPoint.coord.col, Run.CurrentMapPoint.coord.row) };
    }

    // Moves to a given map point (used by the fidelity replay, which follows a recorded path).
    public void MoveTo(int col, int row)
    {
        var pt = NextPoints().FirstOrDefault(p => p.coord.col == col && p.coord.row == row) ?? throw new ArgumentException($"({col},{row}) is not reachable from here");
        _rewards = null;
        Track(Rm.EnterMapCoord(pt.coord));
    }
}
