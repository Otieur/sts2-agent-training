#!/usr/bin/env python3
"""Details of a run benchmark folder for its report (section 5), and paired comparisons across folders.

    python3 -I tools/run_details.py data/learn/runs/run-bench-11
    python3 -I tools/run_details.py data/learn/runs/run-bench-11 --wins-vs rcard+rpath
    python3 -I tools/run_details.py --pair data/learn/runs/run-bench-11:A data/learn/runs/run-bench-12:B   # A - B by seed

Per policy: floors, wins with a Wilson interval, act bosses reached and beaten (by boss), where runs die, the state at
each act's boss fight (deck, upgrades, relics, potions, HP), potions used by room type, shop purchases, gold left,
rollout decisions. Reads the fight specs and decisions that `tools/run_bench.py` records (older folders have fewer).
"""
import argparse
import collections
import json
import math
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_bench  # noqa: E402

BASICS = ("STRIKE_IRONCLAD", "DEFEND_IRONCLAD")


def load(folder):
    return [json.loads(l) for f in sorted(Path(folder).glob("shard-*.jsonl")) for l in f.open() if l.strip()]


def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def mean(xs, nd=2):
    xs = list(xs)
    return round(statistics.mean(xs), nd) if xs else None


def act_of(fight):
    return (fight.get("spec") or {}).get("act") or (1 if fight["floor"] <= 17 else 2 if fight["floor"] <= 33 else 3)


def policy_details(rs):
    out = {"runs": len(rs), "mean_floor": mean(x["floor"] for x in rs), "median_floor": statistics.median(x["floor"] for x in rs),
           "won": sum(x["won"] for x in rs)}
    lo, hi = wilson(out["won"], len(rs))
    out["win_rate_wilson95"] = [round(lo, 3), round(hi, 3)]
    reach, beat, by_boss, died = collections.Counter(), collections.Counter(), {}, collections.Counter()
    state = collections.defaultdict(list)
    pots = collections.Counter()
    fights_by_room = collections.Counter()
    for x in rs:
        fights = x.get("fights", [])
        bosses = [f for f in fights if run_bench.room_type(f) == "Boss"]
        for i, f in enumerate(bosses):
            won = f.get("hp_end", 0) > 0
            reach[i + 1] += 1
            beat[i + 1] += won
            k = f"{act_of(f)}:{f.get('encounter')}"
            w, n = by_boss.get(k, (0, 0))
            by_boss[k] = (w + won, n + 1)
            sp = f.get("spec")
            if sp:
                state[sp["act"]].append({"deck": len(sp["deck"]), "upgrades": sum(c.endswith("+") for c in sp["deck"]),
                                         "upgrades_basics": sum(c.endswith("+") and c.rstrip("+") in BASICS for c in sp["deck"]),
                                         "basics": sum(c.rstrip("+") in BASICS for c in sp["deck"]), "relics": len(sp["relics"]),
                                         "potions": len(sp["potions"]), "hp_frac": sp["hp"] / max(1, sp["max_hp"]), "won": won})
        for f in fights:
            room = run_bench.room_type(f)
            fights_by_room[room] += 1
            sp = f.get("spec")
            if sp and "potions_end" in f:
                pots[room] += max(0, len(sp["potions"]) - f["potions_end"])
        if not x["won"] and fights and fights[-1].get("hp_end", 1) <= 0:
            died[f"act {act_of(fights[-1])} {run_bench.room_type(fights[-1])}"] += 1
    out["boss_reached"], out["boss_beaten"] = dict(sorted(reach.items())), dict(sorted(beat.items()))
    out["by_boss"] = {k: f"{w}/{n}" for k, (w, n) in sorted(by_boss.items())}
    out["died_in"] = dict(died.most_common())
    out["at_boss"] = {act: {k: mean((s[k] for s in v), 2) for k in ("deck", "upgrades", "upgrades_basics", "basics", "relics", "potions", "hp_frac")}
                      | {"n": len(v), "won": sum(s["won"] for s in v)} for act, v in sorted(state.items())}
    out["elites_per_run"] = mean(sum(1 for f in x.get("fights", []) if run_bench.room_type(f) == "Elite") for x in rs)
    out["potions_used_per_run"] = {room: round(n / len(rs), 2) for room, n in pots.items()} | {"all": round(sum(pots.values()) / len(rs), 2)}
    out["fights"] = dict(fights_by_room)
    buys = collections.Counter()
    for x in rs:
        for d in x.get("decisions", []):
            if d["kind"] == "shop":
                o = d["options"][d["chosen"]]
                if o.get("type") == "buy":
                    item = str(o.get("item", ""))
                    buys["removal" if "remov" in item.lower() else item.split(":", 1)[0]] += 1
    out["purchases_per_run"] = {k: round(n / len(rs), 2) for k, n in buys.items()}
    out["gold_left"] = mean((x.get("gold") or 0 for x in rs), 0)
    out["deck_size"] = mean((len(x.get("final_deck", [])) for x in rs), 1)
    out["seconds_per_run"] = mean((x.get("seconds", 0) for x in rs), 0)
    st = collections.Counter()
    for x in rs:
        st.update(x.get("policy_stats") or {})
        for k in ("fallback", "mismatch", "errors", "searched", "potions", "via_run"):
            st["search_" + k] += (x.get("combat_stats") or {}).get(k, 0)
    out["stats"] = dict(st)
    cards = collections.Counter(c.rstrip("+") for x in rs for c in x.get("final_deck", []) if c.rstrip("+") not in BASICS + ("BASH", "ASCENDERS_BANE"))
    out["top_cards"] = cards.most_common(10)
    ups = collections.Counter(c for x in rs for c in x.get("final_deck", []) if c.endswith("+"))
    out["top_upgrades"] = ups.most_common(8)
    return out


def paired(a, b):
    """a, b: {seed: run record}. Floors: mean a - b, bootstrap interval, sign test (a better). Wins: discordant seeds."""
    seeds = sorted(set(a) & set(b))
    d = [a[s]["floor"] - b[s]["floor"] for s in seeds]
    better, worse = sum(x > 0 for x in d), sum(x < 0 for x in d)
    rng = random.Random(0)
    boots = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(4000)) if d else [0]
    wa, wb = sum(a[s]["won"] and not b[s]["won"] for s in seeds), sum(b[s]["won"] and not a[s]["won"] for s in seeds)
    return {"pairs": len(d), "mean_floor_diff": mean(d), "boot95": [round(boots[int(0.025 * len(boots))], 2), round(boots[int(0.975 * len(boots)) - 1], 2)],
            "better": better, "worse": worse, "equal": len(d) - better - worse, "sign_p_one_sided": run_bench.sign_p(better, worse),
            "wins_a": sum(a[s]["won"] for s in seeds), "wins_b": sum(b[s]["won"] for s in seeds), "only_a_wins": wa, "only_b_wins": wb,
            "wins_sign_p_one_sided": run_bench.sign_p(wa, wb)}


def by_seed(folder, policy):
    return {r["seed"]: r["policies"][policy] for r in load(folder) if policy in r["policies"] and "floor" in r["policies"][policy]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", nargs="?")
    ap.add_argument("--wins-vs", help="baseline policy in the folder: paired floors and wins of every other policy against it")
    ap.add_argument("--pair", nargs=2, metavar="FOLDER:POLICY", help="paired comparison A - B across folders, by seed")
    a = ap.parse_args(argv)
    if a.pair:
        (fa, pa), (fb, pb) = (x.rsplit(":", 1) for x in a.pair)
        print(json.dumps({"a": a.pair[0], "b": a.pair[1]} | paired(by_seed(fa, pa), by_seed(fb, pb)), indent=1))
        return 0
    recs = load(a.folder)
    names = list(recs[0]["policies"]) if recs else []
    out = {"records": len(recs), "policies": {}}
    for n in names:
        out["policies"][n] = policy_details([r["policies"][n] for r in recs if "floor" in r["policies"].get(n, {})])
    if a.wins_vs:
        out["paired_vs_" + a.wins_vs] = {n: paired(by_seed(a.folder, n), by_seed(a.folder, a.wins_vs)) for n in names if n != a.wins_vs}
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
