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


def is_curse(card_id):
    import draft
    c = draft.dm.CARDS.get(card_id.rstrip("+"))
    return bool(c) and c.get("type") == "Curse"


_EVENT_COUNTS = None
_EVALUATOR = None
ROLLOUTS_K = 6


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

    def act(self, obs, acts, rng, sim=None):
        scr = obs["screen"]
        ch = obs.get("choice") or {}
        if scr == "event":
            a = event_pick(obs, acts)
            if a:
                return a
        if scr == "map" and "path" in self.parts and sim is not None and not obs.get("at_boss"):
            a = self.route_pick(sim, obs, acts)
            if a:
                return a
        if scr == "choice" and ch.get("kind") == "CardReward" and "rdraft" in self.parts and sim is not None:
            a = self.rollout_pick(sim, obs, acts)
            if a is not None:
                return a
        if scr == "choice" and ch.get("kind") == "CardReward" and ("draft" in self.parts or "rdraft" in self.parts):
            a = draft_pick(obs, acts)
            if a is not None:
                return a
        if scr == "choice" and ch.get("kind") == "FromDeckForRemoval" and "shop" in self.parts:
            opts = ch.get("options") or []
            for want in REMOVE_ORDER:
                for i, cid in enumerate(opts):
                    if (want == "CURSE" and is_curse(cid)) or cid.rstrip("+") == want:
                        a = next((x for x in acts if x.get("cards") == [i]), None)
                        if a:
                            return a
        if scr == "choice" and ch.get("kind", "").startswith("FromDeckForUpgrade") and "rest" in self.parts:
            a = self.upgrade_pick(obs, ch, acts)
            if a:
                return a
        if scr == "shop" and "shop" in self.parts:
            a = self.shop_pick(obs, acts)
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
            _EVALUATOR = run_eval.RolloutEvaluator(k=ROLLOUTS_K)
        opts = run_eval.card_reward_options(acts)
        if len(opts) < 2:
            return None
        vals = _EVALUATOR.evaluate(sim, obs, opts)
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


class SearchCombat:
    """Fights inside a whole run played by search in a second host. At a fight's first decision the run host exports
    the fight recording, whose start state (the run saved at room entry, with its true random state) is kept; at every
    decision the search host rebuilds the fight from that state plus the fight's actions so far in normal single-player
    mode (`fight_from_save`), re-samples the hidden future, checks that the visible state matches the run host's, and
    searches. Any mismatch or failure falls back to the planner for that decision (counted)."""
    def __init__(self, spec):
        import selfplay as SP
        self.SP = SP
        m = __import__("re").fullmatch(r"mc(w?)(\d+)", spec)
        self.wide, self.k = bool(m.group(1)), int(m.group(2))
        self.host = SP.Host()
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
            o = self.host.sim.call(cmd="fight_from_save", data=self.start_state, actions=fight_actions,
                                   sample_seed=1_000_003 * (d + 1) + 17, timeout=120)["obs"]
            if visible(o) != visible(obs):
                self.stats["mismatch"] += 1
                if self.stats["mismatch"] <= 3:
                    names = ("turn", "hp", "energy", "block", "hand", "draw", "discard", "exhaust", "enemies", "powers", "choice")
                    print(f"  mismatch {fight_key} decision {len(fight_actions)}: " + "; ".join(
                        f"{n}: search {x} / run {y}" for n, x, y in zip(names, visible(o), visible(obs)) if x != y)[:900], flush=True)
                return None
            cands, values, best = self.SP.scored_search(self.host.sim, o, "balanced", self.k, 2, d, {}, wide=self.wide)
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


def play_run(sim, seed, ascension, policy, rng, max_steps=6000, combat=None, deadline=None):
    spec = {"seed": seed, "character": "IRONCLAD", "ascension": ascension}
    if combat is not None:
        spec["record_fights"] = True
    obs = sim.call(cmd="new_run", spec=spec, timeout=120)["obs"]
    bosses, steps, last_act, d = 0, 0, 1, 0
    fight_actions, prev_fight, fight_no, fights, host_error = [], False, 0, [], None
    for steps in range(max_steps):
        if obs["screen"] == "game_over":
            break
        if deadline and time.time() > deadline:
            raise Deadline(seed)
        # a choice opened by a card during a fight (e.g. Armaments) is part of the fight: the observation keeps its combat block
        in_fight = obs["screen"] == "combat" or (obs["screen"] == "choice" and bool(obs.get("combat")))
        if prev_fight and not in_fight and fights:
            fights[-1]["hp_end"] = obs["player"]["hp"]
        if in_fight and not prev_fight:
            fight_actions, fight_no = [], fight_no + 1
            fights.append({"floor": obs.get("floor"), "room": obs.get("room"), "encounter": obs.get("encounter"), "hp_start": obs["player"]["hp"],
                           "max_hp": obs["player"]["max_hp"], "enemies": [e["enemy_id"] for e in (obs.get("combat") or {}).get("enemies", [])]})
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
    return {"floor": obs.get("floor"), "act": obs.get("act"), "bosses": bosses + (1 if won else 0), "won": won, "steps": steps,
            "deck": len(obs["player"]["deck"]), "gold": obs["player"].get("gold"), "final_deck": list(obs["player"]["deck"]), "fights": fights,
            "policy_stats": dict(policy.stats), "host_error": host_error}


def deadline_ts(text):
    return time.mktime(time.strptime(text, "%Y-%m-%d %H:%M"))


def worker(a):
    out = Path(a.out)
    combat = SearchCombat(a.combat) if a.combat != "planner" else None
    with S.Sim() as sim:
        for k in range(a.worker, a.seeds, a.workers):
            if a.deadline and time.time() > deadline_ts(a.deadline):
                print(f"w{a.worker}: deadline {a.deadline} reached before seed {k}", flush=True)
                break
            seed = f"RB{a.seed_base:03d}{k:05d}"
            rec = {"seed": seed, "ascension": a.ascension, "combat": a.combat, "policies": {}}
            for name in a.policies:
                t0 = time.time()
                if combat:
                    combat.stats = {"searched": 0, "fallback": 0, "mismatch": 0, "errors": 0, "search_seconds": 0.0}
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
    ap.add_argument("--deadline", help='"YYYY-MM-DD HH:MM" local time: no new seed starts after it, and a seed cut off by it is left out')
    a = ap.parse_args(argv)
    if a.report:
        print(json.dumps(report(a.report, a.baseline), indent=1))
        return 0
    if a.worker is not None:
        return worker(a)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    procs = [subprocess.Popen([sys.executable, "-I", __file__, "--worker", str(w), "--workers", str(a.workers), "--seeds", str(a.seeds),
                               "--seed-base", str(a.seed_base), "--ascension", str(a.ascension), "--out", str(out), "--combat", a.combat,
                               *(["--deadline", a.deadline] if a.deadline else []), "--policies", *a.policies])
             for w in range(a.workers)]
    codes = [p.wait() for p in procs]
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT, capture_output=True, text=True).stdout.strip()
    man = {"name": out.name, "created": time.strftime("%Y-%m-%d %H:%M"), "code_commit": head, "policies": a.policies, "seeds": a.seeds,
           "seed_base": a.seed_base, "ascension": a.ascension, "combat": a.combat, "deadline": a.deadline, "worker_exit_codes": codes,
           "wall_seconds": round(time.time() - t0), "report": report(out, a.baseline)}
    (out / "manifest.json").write_text(json.dumps(man, indent=1))
    print(json.dumps(man["report"], indent=1))
    return 0 if all(c == 0 for c in codes) else 1


if __name__ == "__main__":
    sys.exit(main())
