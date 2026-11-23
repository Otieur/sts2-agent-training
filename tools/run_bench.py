#!/usr/bin/env python3
"""Run-level benchmark for deck-building policies (P9.E4): whole runs in the simulator from fixed seeds, the same
combat policy throughout, only the strategic decisions changed. Policies meet the same seeds (paired).

    python3 -I tools/run_bench.py --out data/learn/runs/draft-1 --policies base draft --seeds 60 --ascension 0
    python3 -I tools/run_bench.py --report data/learn/runs/draft-1

A policy is a `+`-joined list of components; anything not named keeps the simple run policy of `tools/sim.py`
(first card of each reward, leave shops, rest below 60% HP else smith the first card, first map move):
- `base`: the simple run policy alone.
- `draft`: card rewards by the draft scorer (`tools/draft.py score_offer`, skipping below its bar).
- `shop`: in shops, buy the card removal first (curses, then Strikes, then Defends), then the best card the draft
  scorer would take if gold allows.
- `path`: map moves by the path planner (`tools/path.py`: expected loot against fatal risk over every route to the
  boss, room models from the history; the whole act map is visible to the player).
- `rest`: heal below 50% HP (below 70% before a boss), otherwise smith; the upgrade goes to the first card in an
  upgrade priority list (Bash, then the deck's highest-tier cards by the draft scorer's tiers, Strikes and Defends last).
- `rdraft`: card rewards by sampled rollouts (`tools/run_eval.py`), rollouts played by `draft+shop+rest`, ties and
  failures to the draft scorer (run benchmark 3).
- `rcard`: card rewards by sampled rollouts, ties and failures to the first card.
- `rpath`: map moves by sampled rollouts, ties and failures to the route planner (run benchmark 4).
- `ropt`: events (Neow and Ancients included), rest sites and card choices outside fights (upgrade, remove,
  transform, enchant) by sampled rollouts (`tools/run_opts.py`), ties and failures to this policy's rule (run benchmark 9).
- `rshop`: shop purchases (cards, relics, potions, card removal, leaving) by sampled rollouts, one purchase at a time,
  ties and failures to this policy's rule (run benchmark 10). Shops with more than 11 affordable items are left to
  the rule (which leaves).
- `rshop2`: `rshop` without that limit: every affordable item of a shop is judged, however many. When every option
  has the same rollout value, it buys the cheapest relic, else the card removal, instead of leaving. The card to
  remove follows the removal order (curses, Strikes, Defends) unless `ropt` judges it (run benchmark 15).
- `bshop`: the shop rule buys: the cheapest affordable relic until none is affordable, then the card removal (curses,
  then Strikes, then Defends) once, then it leaves. No card and no potion is bought: a rule cannot judge them. It is
  a rule component, so it also plays inside every rollout: a rollout that passes a shop spends its gold, and routes,
  cards and events are judged with what gold buys. With `rshop` or `rshop2` the run's own shops are still judged by
  rollouts, and this rule acts where they do not decide (ties, failures, more options than the limit) (run benchmark 16).
- `pot`: potions may be used in fights (they never are without it): search judges every usable potion by simulation
  in elite and boss fights and the planner's potion plans in hallways, a spent potion priced as lost HP by room
  (`tools/sim.py POTION_PRICE`); the planner (search fallbacks, fights inside rollouts) uses its potion plans too.
- `smith`: rest sites heal only below 35% HP (below 50% right before a boss) and otherwise smith; upgrades (at rest
  sites and elsewhere) go by the upgrade priority list (Bash, then the draft tiers, Strikes and Defends last). With
  `ropt`, rest sites and upgrade choices follow this rule instead of rollouts.
- `ctb`, `cth`: with `rcard`, card tiers as a prior in card rewards (run benchmark 20; the consensus scores of
  `knowledge/community/ironclad-tiers.md`, `[COMMUNITY]`; a card is of the lowest tier only where its sources agree and
  the Player does not pick it either). `ctb` (tie-break): among the options whose rollout value is
  within `CARD_TIER_MARGIN` of the best, the one with the highest tier score is taken (skipping counts as the boundary
  between the two lowest tiers, an unrated card as a middling one). `cth` (hard): from act 2 on, cards of the lowest
  tier are not candidates at all; if only skipping is left, the reward is skipped. Neither acts inside rollouts.
- `br`: with `smith`, the rest site right before a boss heals below 80% HP (`BOSS_REST_HP`) instead of below 50%
  (run benchmark 19).
- `el`: elites are fought while healthy, in acts 1 and 2 (`ELITE_ACTS`). At a map move where a next point is an
  elite and HP is at 60% of the maximum or more (`ELITE_DOOR_HP`), only the elite points are considered. Otherwise,
  with HP at 70% or more (`ELITE_HP`), next points from which no elite of this act can be reached any more are left
  out when another next point still reaches one. The policy's route choice (rollouts or the planner) decides among
  the points left, and alone in every other case. A rule component, so it also acts inside every rollout (run
  benchmark 19).
- `rfm`: the rollouts do not play fights: each fight is ended by the fight-outcome model (`FIGHT_MODEL`, how search
  fights such a fight), and a rollout's value is the expected floors climbed and bosses beaten (`tools/run_eval.py`).
  The run's own fights are played by search as before. Needs a host build with `resolve_fight`.
- `hz`: with `rfm`, rollouts play on to the end of the run instead of the end of the act.
- `bc`: the rollouts of `rdraft`, `rcard` and `rpath` credit progress against a boss (`tools/run_eval.py`
  `boss_credit`, weight `BOSS_CREDIT`): a rollout that dies in a boss fight gets that weight times the fraction of the
  boss fight's enemy HP it removed, and a won run counts as beating the act's boss (run benchmark 7).
`rcard` and `rpath` rollouts are played by this policy with every rollout component replaced by its rule counterpart
(`rpath` by `path`, `rdraft` by `draft`, `rcard`, `ropt`, `rshop` and `rshop2` by the rules, `bc` dropped; `Policy.rule_policy`),
so rollouts never nest. Every fight's starting situation is recorded as a fight spec (`spec` in the fight record, with
the potions left at its end), and every rollout decision with its options' values (`decisions` in the run record),
as data for learned models.

Combat is played by the rule planner by default (fast), or with `--combat mcwK` by wide search in a second host: the
run host exports each fight's start state (the run saved at room entry, from the game's own recording), the search
host rebuilds the fight from it plus the fight's actions so far (`fight_from_save`, normal single-player mode), re-samples
the hidden future, checks the visible state and searches; mismatches and failures fall back to the planner (counted). Every decision
uses only the observation; the seed's future (map, offers, encounters) is never read (FP-1).

Metrics per run: floor reached, act reached, act bosses beaten, won. Primary: floor reached, paired by seed.
"""
import argparse
import json
import math
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "tools"))
import plan_turn as pt  # noqa: E402
import sim as S  # noqa: E402

REMOVE_ORDER = ["CURSE", "STRIKE_IRONCLAD", "DEFEND_IRONCLAD"]
PLAIN_SHOP_BUYS = 6         # the `bshop` rule buys at most this many items in one shop (3 relics and a removal are for sale)
ELITE_HP = 0.7        # the `el` rule keeps an elite on the route at this HP fraction or more
ELITE_DOOR_HP = 0.6   # and enters an elite that is a next point at this HP fraction or more
ELITE_ACTS = 2        # in acts 1 to this one
BOSS_REST_HP = 0.8    # the `br` rule heals at the rest site before a boss below this HP fraction
CARD_TIER_MARGIN = 1.0      # `ctb`: rollout values this close to the best count as tied (a value is floors climbed plus 5 to 10 for a boss beaten)
CARD_TIER_SKIP = 2.0        # `ctb`: the tier score of skipping (the boundary between tiers C and D)
CARD_TIER_UNRATED = 2.4     # `ctb`: the tier score of a card the table does not rate (inside tier C)
CARD_TIER_LOWEST = 2.0      # `cth`: cards scored below this (tier D) are not candidates from act 2 on
_CARD_TIERS = None


def card_tier_scores():
    """Tier scores by card id from knowledge/community/ironclad-tiers.md: the community consensus score ([COMMUNITY];
    S about 4.25 and more, D below 2.0). A card counts as lowest tier only where the views agree: a card the
    consensus puts in tier D is scored as an unrated one (CARD_TIER_UNRATED) when its sources are two or more tiers
    apart, or when the Player's own picking of it is in tier C or better ([PLAYER-DATA], the table's habit column: the
    Player wins with Evil Eye, Fight Me and Tremble, which the consensus rates lowest). Names are matched by their
    letters (BLOOD_WALL and Blood Wall)."""
    global _CARD_TIERS
    if _CARD_TIERS is None:
        _CARD_TIERS = {}
        path = Path(__file__).resolve().parents[1] / "knowledge" / "community" / "ironclad-tiers.md"
        for line in path.read_text().splitlines():
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) >= 4 and re.fullmatch(r"[SABCDF]", c[2].strip("*")):
                try:
                    score = float(c[3])
                except ValueError:
                    continue
                spread = int(c[7]) if len(c) > 7 and c[7].isdigit() else 0
                habit = c[8].strip("*") if len(c) > 8 else "-"
                if score < CARD_TIER_LOWEST and (spread >= 2 or habit in ("S", "A", "B", "C")):
                    score = CARD_TIER_UNRATED
                _CARD_TIERS[re.sub(r"[^A-Z]", "", c[0].upper())] = score
    return _CARD_TIERS


def card_tier_score(option):
    """The tier score of a card-reward option: the card's consensus score, CARD_TIER_UNRATED for a card without one,
    CARD_TIER_SKIP for skipping."""
    if not option.get("cards"):
        return CARD_TIER_SKIP
    key = re.sub(r"[^A-Z]", "", str(option.get("card_id", "")).split(".")[-1].rstrip("+").upper())
    return card_tier_scores().get(key, CARD_TIER_UNRATED)
FIGHT_TURN_CAP = 100  # a fight past this turn is one neither side can end: the run is given up there (lost at that floor)


def is_curse(card_id):
    import draft
    c = draft.dm.CARDS.get(card_id.rstrip("+"))
    return bool(c) and c.get("type") == "Curse"


_EVENT_COUNTS = None
_EVALUATOR = None
_ROUTE_EVALUATOR = None
_CARD_EVALUATOR = None


def set_evaluator(ev, rollout_policy, boss_credit):
    """Give a worker's rollout evaluator the settings of the policy that is about to use it. An evaluator owns an
    evaluation host and is kept for the worker's whole life, across the policies it plays; the rollout policy and the
    boss credit belong to the policy, not to the host. Until 2026-11-21 an evaluator kept the settings of the first
    policy that used it, so in a benchmark whose arms differ in either, every arm's rollouts were played with the first
    arm's settings (run benchmarks 7, 11 and 12; see their section 6)."""
    ev.rollout_policy, ev.boss_credit = rollout_policy, boss_credit
    return ev


def evaluator_settings(ev):
    """What an evaluator was set to when it last ran (kept with every decision)."""
    return {"rollouts_by": getattr(ev, "rollout_policy", None), "boss_credit": getattr(ev, "boss_credit", None),
            "fight_model": Path(ev.fight_model).name if getattr(ev, "fight_model", None) else None, "horizon": getattr(ev, "horizon", None)}


def evaluate(policy, ev, rollout_policy, sim, obs, opts):
    """Evaluate options with an evaluator set to this policy's settings; rollouts that failed (a host error inside the
    rollout; the rollout is left out) are counted in the policy's stats, so that a run's record shows them."""
    set_evaluator(ev, rollout_policy, policy.boss_credit())
    ev.fight_model, ev.horizon = policy.fight_model(), "run" if "hz" in policy.parts else "act"
    # The futures a decision samples are numbered by the decision's place in this run. Until 2026-11-22 they were
    # numbered by the evaluator's count over the worker's whole life, so a run depended on what its worker had played
    # before it (found by replaying a seed of run benchmark 18 alone: a different run from the one in the benchmark).
    ev._n = policy.rollout_n.get(ev.seed_base, 0)
    before = ev.stats.get("errors", 0)
    vals = ev.evaluate(sim, obs, opts)
    policy.rollout_n[ev.seed_base] = ev._n
    if ev.stats.get("errors", 0) > before:
        policy.stats["rollout_errors"] = policy.stats.get("rollout_errors", 0) + ev.stats["errors"] - before
    return vals
ROLLOUTS_K = 6
FIGHT_MODEL = os.environ.get("SIM_FIGHT_MODEL", str(PROJECT / "models" / "fight-v2"))    # the `rfm` component's model folder
BOSS_CREDIT = 5.0           # the `bc` weight: dying with the boss at 0 HP is worth as much as beating it with 0 HP left


def event_pick(obs, acts):
    """Shared default for non-Ancient events in every arm (run benchmark 2, section 6): the option the Player chose most
    often at that point in the history (`data/runs.db` event_choices, matched by page and option key), if it was chosen
    at least twice; otherwise None (the run simulator's first option). Ancients, Neow included, keep the first option."""
    global _EVENT_COUNTS
    ev = obs.get("event") or {}
    if obs["screen"] != "event" or ev.get("ancient"):
        return None
    if _EVENT_COUNTS is None:
        import sqlite3
        db = PROJECT / "data" / "runs.db"
        _EVENT_COUNTS = {}
        if db.exists():
            con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
            for key, n in con.execute("SELECT choice_key, COUNT(*) FROM event_choices GROUP BY choice_key"):
                _EVENT_COUNTS[key.removesuffix(".title")] = n
            con.close()
    opts = [x for x in acts if x.get("type") == "event_option" and x.get("key")]
    scored = [(_EVENT_COUNTS.get(x["key"], 0), -i, x) for i, x in enumerate(opts)]
    if not scored:
        return None
    n, _, best = max(scored, key=lambda t: (t[0], t[1]))
    return best if n >= 2 else None


def draft_pick(obs, acts):
    import draft
    picks = [x for x in acts if x.get("type") == "choose" and x.get("cards")]
    offers = [(x, str(x.get("card_id", ""))) for x in picks if not str(x.get("card_id", "")).startswith("alt:")]
    if not offers:
        return None
    deck = [c.rstrip("+") for c in obs["player"]["deck"]]
    res = draft.score_offer(deck, [cid.rstrip("+") for _, cid in offers], "IRONCLAD", obs.get("act"), obs.get("floor"), None)
    if res["pick"]:
        return next(x for x, cid in offers if cid.rstrip("+") == res["pick"]["id"])
    skip = [x for x in acts if x.get("type") == "choose" and not x.get("cards")]
    return skip[0] if skip else None


class Policy:
    def __init__(self, name):
        self.name = name
        self.parts = set(name.split("+")) - {"base"}
        self.pending = None           # what a choice screen opened by our own action is for
        self.bought = set()
        self.stats = {}
        self.log = []                 # rollout decisions: situation, options, values, choice (data for learned models)
        self.rule_mode = False        # True while run_opts asks what the rules alone would do
        self.rollout_n = {}           # rollout decisions made in this run, per evaluator (they number the sampled futures)

    def act(self, obs, acts, rng, sim=None):
        scr = obs["screen"]
        ch = obs.get("choice") or {}
        if sim is not None and not self.rule_mode and self.parts & {"ropt", "rshop", "rshop2"}:
            import run_opts
            a = run_opts.pick(self, obs, acts, rng, sim)
            if a is not None:
                return a
        if scr == "event":
            a = event_pick(obs, acts)
            if a:
                return a
        if scr == "combat" and "pot" in self.parts:
            a = S.run_policy(pt, obs, acts, rng, potions=fight_room(obs))
            if a.get("type") == "potion":
                self.stats["potions_planner"] = self.stats.get("potions_planner", 0) + 1
            return a
        if scr == "rest" and "smith" in self.parts:
            hp, mx = obs["player"]["hp"], obs["player"]["max_hp"]
            before_boss = BOSS_REST_HP if "br" in self.parts else 0.5
            want = "HEAL" if hp < (before_boss if obs.get("act_floor", 0) >= 15 else 0.35) * mx else "SMITH"
            if obs.get("act_floor", 0) >= 15 and 0.5 * mx <= hp < before_boss * mx:
                self.stats["br_heals"] = self.stats.get("br_heals", 0) + 1
            for w in (want, "SMITH", "HEAL"):
                for x in acts:
                    if str(x.get("option", "")).upper() == w:
                        return x
        if scr == "map" and "el" in self.parts and sim is not None and not obs.get("at_boss"):
            keep = self.elite_moves(sim, obs, acts)
            if keep is not None:
                if len(keep) == 1:
                    return keep[0]
                acts = [x for x in acts if x.get("type") != "move" or any(x is k for k in keep)]
        if scr == "map" and "rpath" in self.parts and sim is not None and not obs.get("at_boss"):
            a = self.route_rollout_pick(sim, obs, acts)
            if a:
                return a
        if scr == "map" and ("path" in self.parts or "rpath" in self.parts) and sim is not None and not obs.get("at_boss"):
            a = self.route_pick(sim, obs, acts)
            if a:
                return a
        if scr == "choice" and ch.get("kind") == "CardReward" and "rcard" in self.parts and sim is not None:
            a = self.card_rollout_pick(sim, obs, acts)
            if a is not None:
                return a
        if scr == "choice" and ch.get("kind") == "CardReward" and "rdraft" in self.parts and sim is not None:
            a = self.rollout_pick(sim, obs, acts)
            if a is not None:
                return a
        if scr == "choice" and ch.get("kind") == "CardReward" and ("draft" in self.parts or "rdraft" in self.parts):
            a = draft_pick(obs, acts)
            if a is not None:
                return a
        if scr == "choice" and ch.get("kind") == "FromDeckForRemoval" and self.parts & {"shop", "rshop2", "bshop"}:
            opts = ch.get("options") or []
            for want in REMOVE_ORDER:
                for i, cid in enumerate(opts):
                    if (want == "CURSE" and is_curse(cid)) or cid.rstrip("+") == want:
                        a = next((x for x in acts if x.get("cards") == [i]), None)
                        if a:
                            return a
        if scr == "choice" and ch.get("kind", "").startswith("FromDeckForUpgrade") and self.parts & {"rest", "smith"}:
            a = self.upgrade_pick(obs, ch, acts)
            if a:
                return a
        if scr == "shop" and "shop" in self.parts:
            a = self.shop_pick(obs, acts)
            if a:
                return a
        if scr == "shop" and "bshop" in self.parts:
            a = self.plain_shop_pick(obs, acts)
            if a:
                return a
        if scr == "rest" and "rest" in self.parts:
            hp, mx = obs["player"]["hp"], obs["player"]["max_hp"]
            boss_next = obs.get("act_floor", 0) >= 15
            want = "HEAL" if hp < (0.7 if boss_next else 0.5) * mx else "SMITH"
            for x in acts:
                if str(x.get("option", "")).upper() == want:
                    return x
        return S.run_policy(pt, obs, acts, rng)

    def rollout_pick(self, sim, obs, acts):
        """Card rewards by sampled rollouts (tools/run_eval.py): each card and skip is played forward over the same
        re-sampled futures to the end of the act with the rule planner fighting; the best mean rollout value is taken,
        exact ties going to the draft scorer's choice."""
        global _EVALUATOR
        import run_eval
        if _EVALUATOR is None:
            _EVALUATOR = run_eval.RolloutEvaluator(k=ROLLOUTS_K, boss_credit=self.boss_credit())
        opts = run_eval.card_reward_options(acts)
        if len(opts) < 2:
            return None
        vals = evaluate(self, _EVALUATOR, _EVALUATOR.rollout_policy, sim, obs, opts)
        if any(v is None for v in vals):
            self.stats["rdraft_failed"] = self.stats.get("rdraft_failed", 0) + 1
            return None
        scorer = draft_pick(obs, acts)
        scorer = scorer if scorer in opts else opts[-1]
        best = max(range(len(opts)), key=lambda i: (vals[i], opts[i] is scorer))
        self.stats["rdraft_decisions"] = self.stats.get("rdraft_decisions", 0) + 1
        self.stats["rdraft_disagree"] = self.stats.get("rdraft_disagree", 0) + (opts[best] is not scorer)
        self.stats["rdraft_skips"] = self.stats.get("rdraft_skips", 0) + (not opts[best].get("cards"))
        return opts[best]

    def card_rollout_pick(self, sim, obs, acts):
        """Card rewards by sampled rollouts without the draft scorer: each card and skip is played forward over the same
        re-sampled futures to the end of the act by this policy with the first card in place of rollouts (e.g. `path`
        for `rcard+path`) and the rule planner fighting; the best mean rollout value is taken, exact ties going to the
        first card. If any rollout fails, the first card is taken (the `base` rule)."""
        global _CARD_EVALUATOR
        import run_eval
        opts = run_eval.card_reward_options(acts)
        if "cth" in self.parts and (obs.get("act") or 1) >= 2:
            kept = [o for o in opts if not o.get("cards") or card_tier_score(o) >= CARD_TIER_LOWEST]
            if len(kept) < len(opts):
                self.stats["cth_dropped"] = self.stats.get("cth_dropped", 0) + len(opts) - len(kept)
                opts = kept
                if len(opts) == 1 and not opts[0].get("cards"):      # every card was of the lowest tier: skip the reward
                    self.stats["cth_skips"] = self.stats.get("cth_skips", 0) + 1
                    return opts[0]
        if len(opts) < 2:
            return None
        if _CARD_EVALUATOR is None:
            _CARD_EVALUATOR = run_eval.RolloutEvaluator(k=ROLLOUTS_K, rollout_policy=self.card_rollout_policy(), seed_base=9_900_000,
                                                        boss_credit=self.boss_credit())
        vals = evaluate(self, _CARD_EVALUATOR, self.card_rollout_policy(), sim, obs, opts)
        if any(v is None for v in vals):
            self.stats["rcard_failed"] = self.stats.get("rcard_failed", 0) + 1
            return None
        best = max(range(len(opts)), key=lambda i: (vals[i], i == 0))
        if "ctb" in self.parts:
            near = [i for i in range(len(opts)) if vals[i] >= vals[best] - CARD_TIER_MARGIN]
            pick = max(near, key=lambda i: (card_tier_score(opts[i]), vals[i], i == 0))
            self.stats["ctb_ties"] = self.stats.get("ctb_ties", 0) + (len(near) > 1)
            self.stats["ctb_changed"] = self.stats.get("ctb_changed", 0) + (pick != best)
            best = pick
        self.note("card", obs, opts, vals, best, 0, _CARD_EVALUATOR)
        self.stats["rcard_decisions"] = self.stats.get("rcard_decisions", 0) + 1
        self.stats["rcard_disagree"] = self.stats.get("rcard_disagree", 0) + (best != 0)
        self.stats["rcard_skips"] = self.stats.get("rcard_skips", 0) + (not opts[best].get("cards"))
        return opts[best]

    def rule_policy(self):
        """This policy with every rollout component replaced by its rule counterpart (`rpath` by `path`, `rdraft` by
        `draft`, `rcard` by the first card, `bc` dropped), so that rollouts never start rollouts of their own."""
        swap = {"rpath": "path", "rdraft": "draft", "rcard": None, "bc": None, "ropt": None, "rshop": None, "rshop2": None,
                "rfm": None, "hz": None, "ctb": None, "cth": None}
        return "+".join(sorted({swap.get(x, x) for x in self.parts} - {None})) or "base"

    def boss_credit(self):
        return BOSS_CREDIT if "bc" in self.parts else 0.0

    def fight_model(self):
        return FIGHT_MODEL if "rfm" in self.parts else None

    def note(self, kind, obs, opts, vals, best, rule, ev=None):
        """Keep a rollout decision: the visible situation, each option with its mean rollout value, the choice, the rule's
        choice, and the settings the evaluator used (read from the evaluator after it ran: the check that an arm's rollouts
        were played with that arm's settings)."""
        p = obs["player"]
        self.log.append({"kind": kind, "act": obs.get("act"), "floor": obs.get("floor"), "screen": obs["screen"],
                         "choice_kind": (obs.get("choice") or {}).get("kind"), "event": obs.get("event_id"),
                         "hp": p["hp"], "max_hp": p["max_hp"], "gold": p.get("gold"), "deck": list(p.get("deck", [])),
                         "relics": list(p.get("relics", [])), "potions": [x for x in p.get("potions", []) if x], "act_boss": obs.get("act_boss"),
                         "options": opts, "values": [round(v, 3) for v in vals], "chosen": best, "rule": rule,
                         **evaluator_settings(ev)})

    def card_rollout_policy(self):
        return self.rule_policy()

    def route_rollout_pick(self, sim, obs, acts):
        """Map moves by sampled rollouts (tools/run_eval.py): each next point is played forward over the same
        re-sampled futures to the end of the act by this policy with the route planner in place of rollouts and the rule planner fighting; the best mean
        rollout value is taken, exact ties going to the route planner's choice."""
        global _ROUTE_EVALUATOR
        import run_eval
        moves = [x for x in acts if x.get("type") == "move"]
        if len(moves) < 2:
            return None
        if _ROUTE_EVALUATOR is None:
            _ROUTE_EVALUATOR = run_eval.RolloutEvaluator(k=ROLLOUTS_K, rollout_policy=self.route_rollout_policy(), seed_base=8_800_000,
                                                         boss_credit=self.boss_credit())
        vals = evaluate(self, _ROUTE_EVALUATOR, self.route_rollout_policy(), sim, obs, moves)
        if any(v is None for v in vals):
            self.stats["rpath_failed"] = self.stats.get("rpath_failed", 0) + 1
            return None
        planner = self.route_pick(sim, obs, acts)
        best = max(range(len(moves)), key=lambda i: (vals[i], moves[i] is planner))
        self.note("route", obs, moves, vals, best, next((i for i, m in enumerate(moves) if m is planner), None), _ROUTE_EVALUATOR)
        self.stats["rpath_decisions"] = self.stats.get("rpath_decisions", 0) + 1
        self.stats["rpath_disagree"] = self.stats.get("rpath_disagree", 0) + (moves[best] is not planner)
        return moves[best]

    def route_rollout_policy(self):
        return self.rule_policy()

    def elite_moves(self, sim, obs, acts):
        """The `el` rule, acts 1 to ELITE_ACTS: the map moves left for the route choice. With an elite among the next
        points and HP at ELITE_DOOR_HP of the maximum or more, the elite points; otherwise, with HP at ELITE_HP or more,
        the moves from which an elite of this act can still be reached. None when the rule does not narrow the choice.
        The whole act map is visible to the player."""
        moves = [x for x in acts if x.get("type") == "move"]
        hp, mx = obs["player"]["hp"], obs["player"]["max_hp"]
        if len(moves) < 2 or (obs.get("act") or 1) > ELITE_ACTS or hp < ELITE_DOOR_HP * mx:
            return None
        door = [x for x in moves if str(x.get("point")) == "Elite"]
        if door:
            self.stats["el_doors"] = self.stats.get("el_doors", 0) + 1
            if len(door) == len(moves):
                return None
            self.stats["el_entered"] = self.stats.get("el_entered", 0) + 1
            return door
        if hp < ELITE_HP * mx:
            return None
        pts = {(p["row"], p["col"]): p for p in sim.call(cmd="map")["map"]["points"]}
        most = {}

        def reach(rc):                          # is an elite on some way on from this point (the map has no cycles)
            if rc not in most:
                most[rc] = False
                p = pts.get(rc)
                if p is not None:
                    most[rc] = str(p.get("type")) == "Elite" or any(reach((c[1], c[0])) for c in p.get("children") or [])
            return most[rc]

        n = [reach((x.get("row"), x.get("col"))) for x in moves]
        self.stats["el_forks"] = self.stats.get("el_forks", 0) + 1
        if all(n) or not any(n):
            return None
        self.stats["el_narrowed"] = self.stats.get("el_narrowed", 0) + 1
        return [x for x, k in zip(moves, n) if k]

    def route_pick(self, sim, obs, acts):
        """Route by the path planner (`tools/path.py`: expected loot against fatal risk, room models from the history);
        the whole act map is visible to the player."""
        import path as P
        moves = [x for x in acts if x.get("type") == "move"]
        if len(moves) <= 1:
            return None
        m = sim.call(cmd="map")["map"]
        rc = lambda v: {"row": v[1], "col": v[0]} if v else None
        mp = {"nodes": [{"row": p["row"], "col": p["col"], "node_type": p["type"], "children": [{"row": c[1], "col": c[0]} for c in p["children"]]}
                        for p in m["points"]],
              "current_node": rc(m.get("here")), "starting_node": rc(m.get("start")), "boss_node": rc(m.get("boss"))}
        nodes, start, boss = P.load_map(mp)
        paths = P.enumerate_paths(nodes, start, boss)
        if not paths:
            return None
        act = obs.get("act") or 1
        if not hasattr(self, "_path_model"):
            self._path_model = P.get_model("IRONCLAD", obs.get("ascension", 0))
        hp, mx = obs["player"]["hp"], obs["player"]["max_hp"]
        res = P.rank(paths, nodes, self._path_model, act, hp, mx, None, P.DEFAULT_RISK_WEIGHT.get(act, 16.0),
                     P.deck_metrics_from([c.rstrip("+") for c in obs["player"]["deck"]]))
        for o in res:
            first = o.get("first")
            if first:
                a = next((x for x in moves if (x.get("row"), x.get("col")) == tuple(first)), None)
                if a:
                    return a
        return None

    def shop_pick(self, obs, acts):
        gold = obs["player"]["gold"]
        key = (obs.get("act"), obs.get("floor"))
        removal = [x for x in acts if x.get("type") == "buy" and "remov" in str(x.get("item", "")).lower() and x.get("cost", 1e9) <= gold]
        if removal and (key, "remove") not in self.bought:
            self.bought.add((key, "remove"))
            return removal[0]
        cards = [x for x in acts if x.get("type") == "buy" and str(x.get("item", "")).startswith("card:") and x.get("cost", 1e9) <= gold]
        if cards and (key, "card") not in self.bought:
            import draft
            deck = [c.rstrip("+") for c in obs["player"]["deck"]]
            ids = [x["item"].split(":", 1)[1] for x in cards]
            res = draft.score_offer(deck, ids, "IRONCLAD", obs.get("act"), obs.get("floor"), None)
            self.bought.add((key, "card"))
            if res["pick"]:
                return next(x for x in cards if x["item"].split(":", 1)[1] == res["pick"]["id"])
        return None

    def plain_shop_pick(self, obs, acts):
        """The `bshop` rule: the cheapest affordable relic while there is one, then the card removal once, then None
        (leave). At most `PLAIN_SHOP_BUYS` purchases in a shop, as a guard against an item that stays for sale."""
        gold = obs["player"].get("gold", 0)
        key = (obs.get("act"), obs.get("floor"))
        n = sum(1 for k in self.bought if k[0] == key and k[1] == "plain")
        if n >= PLAIN_SHOP_BUYS:
            return None
        buys = [x for x in acts if x.get("type") == "buy" and x.get("cost", 1e9) <= gold]
        relics = [x for x in buys if str(x.get("item", "")).startswith("relic:")]
        removal = [x for x in buys if "remov" in str(x.get("item", "")).lower()]
        if relics:
            a = min(relics, key=lambda x: x.get("cost", 0))
        elif removal and (key, "plain-remove") not in self.bought:
            a = removal[0]
            self.bought.add((key, "plain-remove"))
        else:
            return None
        self.bought.add((key, "plain", n))
        if not self.rule_mode:
            self.stats["bshop_buys"] = self.stats.get("bshop_buys", 0) + 1
        return a

    def upgrade_pick(self, obs, ch, acts):
        import draft
        opts = ch.get("options") or []
        tiers = draft.load_tiers("IRONCLAD")
        def rank(cid):
            base = cid.rstrip("+")
            if base == "BASH":
                return 100
            if base in ("STRIKE_IRONCLAD", "DEFEND_IRONCLAD"):
                return -10
            c = draft.dm.CARDS.get(base)
            t = tiers.get(draft.norm(c["name"])) if c else None
            return draft.TIER_SCORE.get(t[0], 0) if t else 0
        order = sorted(range(len(opts)), key=lambda i: -rank(opts[i]))
        for i in order:
            a = next((x for x in acts if x.get("cards") == [i]), None)
            if a:
                return a
        return None


def visible(o):
    c = o.get("combat") or {}
    p = c.get("player") or {}
    return (o.get("turn"), p.get("current_hp"), p.get("energy"), p.get("block"), [(h["card_id"], h["upgraded"]) for h in c.get("hand", [])],
            c.get("draw_pile"), c.get("discard_pile"), c.get("exhaust_pile"),
            [(e["enemy_id"], e["current_hp"], e["block"], [(x["power_id"], x["amount"]) for x in e["powers"]], [i["intent_type"] for i in e["intents"]]) for e in c.get("enemies", [])],
            [(x["power_id"], x["amount"]) for x in p.get("powers", [])], o.get("choice"))


def fight_room(obs):
    """Monster, Elite or Boss for the fight in an observation, from its encounter id (the potion price depends on it)."""
    enc = str(obs.get("encounter") or "")
    return "Boss" if enc.endswith("_BOSS") else "Elite" if enc.endswith("_ELITE") else "Monster"


def a_potion(action):
    return bool(action) and action.get("type") == "potion"


class SearchCombat:
    """Fights inside a whole run played by search in a second host. At a fight's first decision the run host exports
    the fight recording, whose start state (the run saved at room entry, with its true random state) is kept; at every
    decision the search host rebuilds the fight from that state plus the fight's actions so far in normal single-player
    mode (`fight_from_save`), re-samples the hidden future, checks that the visible state matches the run host's, and
    searches. Any mismatch or failure falls back to the planner for that decision (counted)."""
    def __init__(self, spec, rebuild="save"):
        import selfplay as SP
        self.SP = SP
        self.rebuild = rebuild          # "save": the fight's own save; "save+run": the run clone when that fails (event fights)
        m = __import__("re").fullmatch(r"mc(w?)(\d+)", spec)
        self.wide, self.k = bool(m.group(1)), int(m.group(2))
        self.host = SP.Host()
        self.potions = False            # set per run by the worker: the policy's `pot` component
        self.stats = {"searched": 0, "fallback": 0, "mismatch": 0, "errors": 0, "search_seconds": 0.0}
        self.start_state, self.fight_key = None, None

    def act(self, run_sim, obs, acts, d, fight_actions, fight_key):
        try:
            if fight_key != self.fight_key or self.start_state is None:
                if self.fight_key is not None:
                    print(f"  fight {self.fight_key}: {self.stats}", flush=True)
                self.start_state = run_sim.call(cmd="export_fight")["replay_b64"]
                self.fight_key = fight_key
            t0 = time.time()
            seed = 1_000_003 * (d + 1) + 17
            try:
                o = self.host.sim.call(cmd="fight_from_save", data=self.start_state, actions=fight_actions, sample_seed=seed, timeout=120)["obs"]
                if self.rebuild == "save+run" and visible(o) != visible(obs):
                    raise S.SimError("fight_from_save: visible state differs")
            except S.SimError:
                if self.rebuild != "save+run":
                    raise
                ex = run_sim.call(cmd="run_export")["export"]
                o = self.host.sim.call(cmd="fight_from_run", data=ex["save_b64"], actions=ex["actions"], sample_seed=seed, timeout=120)["obs"]
                self.stats["via_run"] = self.stats.get("via_run", 0) + 1
            if visible(o) != visible(obs):
                self.stats["mismatch"] += 1
                if self.stats["mismatch"] <= 3:
                    names = ("turn", "hp", "energy", "block", "hand", "draw", "discard", "exhaust", "enemies", "powers", "choice")
                    print(f"  mismatch {fight_key} decision {len(fight_actions)}: " + "; ".join(
                        f"{n}: search {x} / run {y}" for n, x, y in zip(names, visible(o), visible(obs)) if x != y)[:900], flush=True)
                return None
            room = fight_room(obs) if self.potions else None
            cands, values, best = self.SP.scored_search(self.host.sim, o, "balanced", self.k, 2, d, {}, potions=room, wide=self.wide,
                                                        all_potions=room in ("Elite", "Boss"))
            if a_potion(cands[best if values[0] is not None else 0]):
                self.stats["potions"] = self.stats.get("potions", 0) + 1
            self.stats["search_seconds"] += time.time() - t0
            a = cands[best if values[0] is not None else 0]
            if not any(all(x.get(k) == a.get(k) for k in ("type", "card", "target", "cards", "slot")) for x in acts):
                return None
            self.stats["searched"] += 1
            return a
        except (S.SimError, self.SP.Tainted) as e:
            self.stats["errors"] += 1
            if self.stats["errors"] <= 3:
                print(f"  search error {fight_key} decision {len(fight_actions)}: {str(e)[:400]}", flush=True)
            self.host.restart()
            return None

    def close(self):
        self.host.close()


class Deadline(Exception):
    pass


def end_turn_z():
    """The fight search's end-of-turn check as this process would play it (tools/selfplay.py END_TURN_Z; None is off)."""
    import selfplay as SP
    return SP.END_TURN_Z


def play_run(sim, seed, ascension, policy, rng, max_steps=6000, combat=None, deadline=None):
    spec = {"seed": seed, "character": "IRONCLAD", "ascension": ascension}
    if combat is not None:
        spec["record_fights"] = True
    obs = sim.call(cmd="new_run", spec=spec, timeout=120)["obs"]
    bosses, steps, last_act, d = 0, 0, 1, 0
    fight_actions, prev_fight, fight_no, fights, host_error, stalled = [], False, 0, [], None, None
    for steps in range(max_steps):
        if obs["screen"] == "game_over":
            break
        if deadline and time.time() > deadline:
            raise Deadline(seed)
        # a choice opened by a card during a fight (e.g. Armaments) is part of the fight: the observation keeps its combat block
        in_fight = obs["screen"] == "combat" or (obs["screen"] == "choice" and bool(obs.get("combat")))
        if prev_fight and not in_fight and fights:
            fights[-1]["hp_end"] = obs["player"]["hp"]
            fights[-1]["potions_end"] = len([x for x in obs["player"].get("potions", []) if x])
        if in_fight and not prev_fight:
            fight_actions, fight_no = [], fight_no + 1
            fights.append({"floor": obs.get("floor"), "room": obs.get("room"), "encounter": obs.get("encounter"), "hp_start": obs["player"]["hp"],
                           "max_hp": obs["player"]["max_hp"], "enemies": [e["enemy_id"] for e in (obs.get("combat") or {}).get("enemies", [])]})
            if obs.get("encounter"):
                p = obs["player"]          # the fight's starting situation as a fight spec (tools/fight_specs.py format)
                fights[-1]["spec"] = {"source": {"run": f"rb-{seed}", "floor": obs.get("floor"), "build": "simulated", "run_won": None},
                                      "act": obs.get("act"), "room": fight_room(obs), "encounter": obs["encounter"], "ascension": ascension,
                                      "character": "IRONCLAD", "deck": list(p.get("deck", [])), "relics": list(p.get("relics", [])),
                                      "potions": [x for x in p.get("potions", []) if x], "hp": p["hp"], "max_hp": p["max_hp"], "valid": True}
        if in_fight and (obs.get("turn") or 0) > FIGHT_TURN_CAP:
            # Seen in run benchmark 18: a deck left without a single attack blocked an enemy at full HP for 578 turns
            # and three hours, until the worker was ended. A player in that fight can only give the run up.
            stalled = {"floor": obs.get("floor"), "encounter": obs.get("encounter"), "turn": obs.get("turn"), "hp": obs["player"]["hp"]}
            break
        acts = sim.call(cmd="run_legal")["actions"]
        if not acts:
            break
        a = None
        if combat is not None and in_fight:
            a = combat.act(sim, obs, acts, d, fight_actions, (seed, fight_no))
            d += 1
            if a is None:
                combat.stats["fallback"] += 1
        action = a or policy.act(obs, acts, rng, sim)
        if in_fight:
            fight_actions.append(action)
        prev_fight = in_fight
        try:
            obs = sim.call(cmd="run_step", action=action, timeout=120)["obs"]
        except S.SimError as e:
            host_error = str(e)[:300]          # the run stops here; reported, not counted as a death in the details
            break
        if obs.get("act", 1) > last_act:
            bosses += obs["act"] - last_act
            last_act = obs["act"]
    won = obs["screen"] == "game_over" and obs["player"]["hp"] > 0
    if fights and "hp_end" not in fights[-1]:
        fights[-1]["hp_end"] = obs["player"]["hp"]
        fights[-1]["potions_end"] = len([x for x in obs["player"].get("potions", []) if x])
    return {"floor": obs.get("floor"), "act": obs.get("act"), "bosses": bosses + (1 if won else 0), "won": won, "steps": steps,
            "deck": len(obs["player"]["deck"]), "gold": obs["player"].get("gold"), "final_deck": list(obs["player"]["deck"]), "fights": fights,
            "policy_stats": dict(policy.stats), "decisions": list(policy.log), "host_error": host_error, "stalled_fight": stalled}


def deadline_ts(text):
    return time.mktime(time.strptime(text, "%Y-%m-%d %H:%M"))


DEADLINE_GRACE = 600   # seconds after --deadline at which the main process ends the workers that are still running


def wait_workers(procs, deadline=None, grace=DEADLINE_GRACE):
    """The workers' exit codes, and the workers the main process had to end. A worker stops itself at the deadline, but
    only between two steps of a run; one whose step does not return (run benchmark 18: a fight search that went on for
    hours in a fight the rollouts could not finish) would hold the manifest back for good. Such a worker is ended here
    `grace` seconds after the deadline, with its hosts; the seed it was playing is left out, as the stopping rule says."""
    ended = []
    while any(p.poll() is None for p in procs):
        if deadline is not None and time.time() > deadline + grace:
            for w, p in enumerate(procs):
                if p.poll() is None and w not in ended:
                    hosts = subprocess.run(["pgrep", "-P", str(p.pid)], capture_output=True, text=True).stdout.split()
                    print(f"w{w}: still running {grace} s after the deadline; ended by the main process, its seed is left out", flush=True)
                    p.kill()
                    for h in hosts:
                        try:
                            os.kill(int(h), 9)
                        except (ProcessLookupError, PermissionError):
                            pass
                    ended.append(w)
        time.sleep(2)
    return [p.returncode for p in procs], ended


def worker(a):
    out = Path(a.out)
    combat = SearchCombat(a.combat, a.fight_rebuild) if a.combat != "planner" else None
    # --resume: seeds already recorded in this folder (by any worker, before an interruption) are not played again
    done = {json.loads(l)["seed"] for f in out.glob("shard-*.jsonl") for l in f.open()} if a.resume else set()
    with S.Sim() as sim:
        # static: worker w plays seeds w, w+W, ...; dynamic: a free worker claims the next unclaimed seed in index order
        for k in (range(a.seeds) if a.dynamic else range(a.worker, a.seeds, a.workers)):
            if a.deadline and time.time() > deadline_ts(a.deadline):
                print(f"w{a.worker}: deadline {a.deadline} reached before seed {k}", flush=True)
                break
            if f"RB{a.seed_base:03d}{k:05d}" in done:
                continue
            if a.dynamic:
                try:
                    os.close(os.open(out / "claims" / str(k), os.O_CREAT | os.O_EXCL))
                except FileExistsError:
                    continue
            seed = f"RB{a.seed_base:03d}{k:05d}"
            rec = {"seed": seed, "ascension": a.ascension, "combat": a.combat, "policies": {}}
            for name in a.policies:
                t0 = time.time()
                if combat:
                    combat.stats = {"searched": 0, "fallback": 0, "mismatch": 0, "errors": 0, "search_seconds": 0.0}
                    combat.potions = "pot" in name.split("+")
                try:
                    r = play_run(sim, seed, a.ascension, Policy(name), random.Random(k), combat=combat,
                                 deadline=deadline_ts(a.deadline) if a.deadline else None)
                except S.SimError as e:
                    r = {"error": str(e)[:200]}
                except Deadline:
                    rec = None
                    print(f"w{a.worker} {seed}: deadline {a.deadline} reached during {name}; seed left out", flush=True)
                    break
                r["seconds"] = round(time.time() - t0, 1)
                if combat:
                    r["combat_stats"] = dict(combat.stats)
                rec["policies"][name] = r
            if rec is None:
                break
            with (out / f"shard-{a.worker:02d}.jsonl").open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(f"w{a.worker} {seed}: " + ", ".join(f"{n} floor {v.get('floor')}{' WON' if v.get('won') else ''}" for n, v in rec["policies"].items()), flush=True)
    if combat:
        combat.close()
    if _EVALUATOR is not None:
        _EVALUATOR.close()
    if _ROUTE_EVALUATOR is not None:
        _ROUTE_EVALUATOR.close()
    if _CARD_EVALUATOR is not None:
        _CARD_EVALUATOR.close()
    if "run_opts" in sys.modules:
        sys.modules["run_opts"].close()
    return 0


def sign_p(better, worse):
    n = better + worse
    return sum(math.comb(n, i) for i in range(better, n + 1)) / 2 ** n if n else 1.0


_ROOM_OF = None


def room_type(fight):
    """Monster, Elite or Boss for a recorded fight: from its encounter id when recorded, else from its starting enemies
    matched against the encounters of the Player's history (`data/runs.db` floors); '?' when unknown."""
    global _ROOM_OF
    enc = fight.get("encounter") or ""
    for suffix, t in (("_BOSS", "Boss"), ("_ELITE", "Elite"), ("_NORMAL", "Monster"), ("_WEAK", "Monster")):
        if enc.endswith(suffix):
            return t
    if _ROOM_OF is None:
        import sqlite3
        _ROOM_OF = {}
        db = PROJECT / "data" / "runs.db"
        if db.exists():
            con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
            for rt, ids in con.execute("SELECT room_type, monster_ids FROM floors WHERE room_type IN ('monster', 'elite', 'boss') AND monster_ids != ''"):
                _ROOM_OF.setdefault(tuple(sorted(x.removeprefix("MONSTER.") for x in json.loads(ids))), rt.capitalize())
            con.close()
    known = _ROOM_OF.get(tuple(sorted(fight.get("enemies", []))))
    if known:
        return known
    # encounters new since the history's game version: an encounter whose name stem appears in an enemy's id
    for f in sorted((PROJECT / "data" / "sim").glob("encounters-*.json")):
        for e in json.loads(f.read_text())["encounters"]:
            stem = re.sub(r"_(NORMAL|WEAK|ELITE|BOSS)$", "", e["id"])
            stem = stem[:-1] if stem.endswith("S") else stem
            if any(stem in x for x in fight.get("enemies", [])):
                return e["room_type"]
    return "?"


def details(rs):
    """Where runs die, HP lost per fight by room type, and search statistics, for one policy's finished runs."""
    import collections
    died, lost, n = collections.Counter(), collections.defaultdict(list), collections.Counter()
    stats, pstats = collections.Counter(), collections.Counter()
    for x in rs:
        for k, v in (x.get("policy_stats") or {}).items():
            pstats[k] += v
        fs = x.get("fights", [])
        for f in fs:
            t = room_type(f)
            n[t] += 1
            if f.get("hp_end", 0) > 0:
                lost[t].append(f["hp_start"] - f["hp_end"])
        if x.get("host_error"):
            died["stopped by a host error"] += 1
        elif x.get("stalled_fight"):
            died["given up in a fight that did not end"] += 1
        elif not x["won"]:
            died[room_type(fs[-1]) if fs and fs[-1].get("hp_end", 1) == 0 else "outside a fight"] += 1
        for k, v in (x.get("combat_stats") or {}).items():
            stats[k] += v
    return {"died_in": dict(died), "fights": dict(n), "mean_hp_lost_in_won_fights": {t: round(sum(v) / len(v), 1) for t, v in lost.items() if v},
            "search": {k: round(v, 1) for k, v in stats.items()}, "policy": dict(pstats), "mean_seconds": round(sum(x.get("seconds", 0) for x in rs) / max(len(rs), 1), 1)}


def report(folder, baseline):
    recs = [json.loads(l) for f in sorted(Path(folder).glob("shard-*.jsonl")) for l in f.open()]
    names = list(recs[0]["policies"]) if recs else []
    out = {"runs": len(recs), "policies": {}}
    for n in names:
        rs = [r["policies"][n] for r in recs if "floor" in r["policies"][n]]
        out["policies"][n] = {"runs": len(rs), "mean_floor": round(sum(x["floor"] for x in rs) / max(len(rs), 1), 2),
                              "act1_boss": sum(1 for x in rs if x["bosses"] >= 1), "act2_boss": sum(1 for x in rs if x["bosses"] >= 2),
                              "won": sum(1 for x in rs if x["won"])} | details(rs)
    for n in names:
        if n == baseline:
            continue
        d = [r["policies"][n]["floor"] - r["policies"][baseline]["floor"] for r in recs
             if "floor" in r["policies"][n] and "floor" in r["policies"][baseline]]
        b, w = sum(1 for x in d if x > 0), sum(1 for x in d if x < 0)
        rng = random.Random(0)
        boots = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(4000)) if d else [0]
        out["policies"][n]["vs_" + baseline] = {"pairs": len(d), "mean_floor_diff": round(sum(d) / max(len(d), 1), 2), "better": b, "worse": w,
                                                "equal": len(d) - b - w, "sign_p_one_sided": sign_p(b, w), "boot95": [boots[100], boots[3899]]}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out")
    ap.add_argument("--policies", nargs="+", default=["base", "draft"])
    ap.add_argument("--seeds", type=int, default=60)
    ap.add_argument("--seed-base", type=int, default=1)
    ap.add_argument("--ascension", type=int, default=0)
    ap.add_argument("--combat", default="planner", help="planner, or a search spec such as mcw2 or mcw6 played in a second host (needs a host with export_fight)")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--worker", type=int, help=argparse.SUPPRESS)
    ap.add_argument("--report")
    ap.add_argument("--baseline", default="base")
    ap.add_argument("--fight-rebuild", default="save", choices=["save", "save+run"],
                    help="how search hosts rebuild a fight: its own save, or also the run clone when that fails (fights started by events)")
    ap.add_argument("--deadline", help='"YYYY-MM-DD HH:MM" local time: no new seed starts after it, and a seed cut off by it is left out')
    ap.add_argument("--dynamic", action="store_true", help="a free worker claims the next seed in index order (no idle workers at the end)")
    ap.add_argument("--resume", action="store_true", help="continue an interrupted run in --out: recorded seeds are kept, the others played")
    a = ap.parse_args(argv)
    if a.report:
        print(json.dumps(report(a.report, a.baseline), indent=1))
        return 0
    if a.worker is not None:
        return worker(a)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.dynamic:
        (out / "claims").mkdir(exist_ok=True)
        for f in (out / "claims").iterdir():
            f.unlink()
    t0 = time.time()
    # the code the workers start from (later commits during the run do not change the running processes)
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT, capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--untracked-files=no", "--", "tools", "sim"], cwd=PROJECT,
                                capture_output=True, text=True).stdout.strip())
    started = time.strftime("%Y-%m-%d %H:%M")
    procs = [subprocess.Popen([sys.executable, "-I", __file__, "--worker", str(w), "--workers", str(a.workers), "--seeds", str(a.seeds),
                               "--seed-base", str(a.seed_base), "--ascension", str(a.ascension), "--out", str(out), "--combat", a.combat,
                               *(["--deadline", a.deadline] if a.deadline else []), *(["--dynamic"] if a.dynamic else []),
                               *(["--resume"] if a.resume else []),
                               "--fight-rebuild", a.fight_rebuild, "--policies", *a.policies])
             for w in range(a.workers)]
    codes, ended = wait_workers(procs, deadline_ts(a.deadline) if a.deadline else None)
    man = {"name": out.name, "started": started, "created": time.strftime("%Y-%m-%d %H:%M"), "code_commit": head,
           "code_uncommitted_changes": dirty, "host": os.environ.get("SIM_CONFIG", "Release"), "fight_rebuild": a.fight_rebuild,
           "shared_eval_host": os.environ.get("SIM_SHARED_EVAL_HOST", "1") != "0",    # as tools/run_eval.py SHARED_EVAL_HOST
           "workers": a.workers, "seed_order": "dynamic" if a.dynamic else "static", "resumed": bool(a.resume),
           "policies": a.policies, "seeds": a.seeds,
           "seed_base": a.seed_base, "ascension": a.ascension, "combat": a.combat, "loss_value": {"forms": S.LOSS_COUNTS_FORMS, "minions": S.LOSS_SKIPS_MINIONS}, "end_turn_z": end_turn_z(), "search_choices": S.SEARCH_CHOICES, "deadline": a.deadline, "worker_exit_codes": codes,
           "workers_ended_after_deadline": ended,
           "wall_seconds": round(time.time() - t0), "report": report(out, a.baseline)}
    (out / "manifest.json").write_text(json.dumps(man, indent=1))
    print(json.dumps(man["report"], indent=1))
    return 0 if all(c == 0 for c in codes) else 1


if __name__ == "__main__":
    sys.exit(main())
