"""Read boss replay 2 (reports/phase9/boss-replay-2.md): the registered tests and the tables of its section 5.

    python3 -I tools/boss_replay_read.py [--bench data/learn/bench/boss-replay-2-] [--specs data/sim/boss-replay-2-]

Reads the nine fight-benchmark folders <bench>{p0,p,g}-{ts,queen,aeon} and their spec files (the Player's are
local files). Prints, per set, boss and arm, the fights won and the secondary measures; H1 (the first sample seeds
of Set P0 against the Agent's 8 of 42 in the runs, one-sided Fisher exact test; all seeds with a bootstrap
interval over situations); Set G beside the outcome of each fight in its run; H3 (the Queen situations with and
without minions in the value of a lost rollout, one-sided sign test); Set P by situation beside the Player's result.
"""
import argparse
import glob
import json
import random
from math import comb

SETS = ("p0", "p", "g")
BOSS = ("ts", "queen", "aeon")
NAME = {"ts": "Test Subject", "queen": "Queen", "aeon": "Aeonglass"}
RUNS_WON, RUNS_FIGHTS = 8, 42          # the Agent's act 3 boss fights in run benchmark 16


def won(x):
    return 1 if x and x.get("status") == "won" else 0


def ended(x):
    return x is not None and x.get("status") in ("won", "lost")


def mean(v):
    return sum(v) / len(v) if v else float("nan")


def fisher_greater(a, n1, b, n2):
    """One-sided Fisher exact test: the probability of a or more wins in the first group, margins fixed."""
    k = a + b
    return sum(comb(n1, x) * comb(n2, k - x) for x in range(a, min(n1, k) + 1)) / comb(n1 + n2, k)


def sign_greater(plus, minus):
    n = plus + minus
    return sum(comb(n, x) for x in range(plus, n + 1)) / 2 ** n if n else 1.0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--bench", default="data/learn/bench/boss-replay-2-")
    ap.add_argument("--specs", default="data/sim/boss-replay-2-")
    a = ap.parse_args()

    data = {}
    for s in SETS:
        for b in BOSS:
            n = f"{s}-{b}"
            rows = [json.loads(l) for f in sorted(glob.glob(a.bench + n + "/shard-*.jsonl")) for l in open(f)]
            data[n] = {"rows": rows, "arms": json.load(open(a.bench + n + "/manifest.json"))["arms"],
                       "specs": json.load(open(a.specs + n + ".json"))["fights"]}

    def table(n, arm):
        t = {}
        for r in data[n]["rows"]:
            t.setdefault(r["fight"], {})[r["sample"]] = r["arms"].get(arm)
        return t

    print("Per set, boss and arm")
    for s in SETS:
        for b in BOSS:
            n = f"{s}-{b}"
            for arm in data[n]["arms"]:
                recs = [x for t in table(n, arm).values() for x in t.values() if x is not None]
                fin = [x for x in recs if ended(x)]
                w = [x for x in fin if won(x)]
                lo = [x for x in fin if not won(x)]
                dec = sum(x.get("decisions", 0) for x in fin)
                sec = sum(x.get("search_seconds", x.get("seconds", 0)) for x in fin)
                print(f"  {s} {NAME[b]} {arm}: won {len(w)} of {len(fin)}" + (f" (+{len(recs) - len(fin)} host error)" if len(recs) > len(fin) else "")
                      + f"; turns {mean([x['turns'] for x in fin]):.1f}; HP left after a win {mean([x['hp'] for x in w]):.1f}; "
                      f"enemies' HP left after a loss {mean([x['enemy_hp_left'] for x in lo]):.1f}; potions used {mean([x.get('potions_used', 0) for x in fin]):.2f}; "
                      f"seconds a decision {sec / max(dec, 1):.2f}")

    print("\nH1: Set P0, mcw6pa, against the Agent's situations in their runs")
    first, alls = [], []
    for b in BOSS:
        t = table("p0-" + b, "mcw6pa")
        for i in sorted(t):
            first.append((b, won(t[i][0])))
            alls.append((b, [won(t[i][s]) for s in sorted(t[i])]))
    w1 = sum(x[1] for x in first)
    print(f"  first sample seeds: {w1} of {len(first)}; " + ", ".join(f"{NAME[b]} {sum(x[1] for x in first if x[0] == b)} of {sum(1 for x in first if x[0] == b)}" for b in BOSS))
    print(f"  one-sided Fisher exact test against {RUNS_WON} of {RUNS_FIGHTS}: p = {fisher_greater(w1, len(first), RUNS_WON, RUNS_FIGHTS):.4f}")
    rng = random.Random(20261123)
    boots = sorted(sum(sum(x[1]) for x in smp) / sum(len(x[1]) for x in smp)
                   for smp in ([alls[rng.randrange(len(alls))] for _ in alls] for _ in range(20000)))
    tot, nf = sum(sum(x[1]) for x in alls), sum(len(x[1]) for x in alls)
    print(f"  all sample seeds: {tot} of {nf} ({100 * tot / nf:.1f}%), bootstrap 95% over situations {100 * boots[500]:.0f}% to {100 * boots[19499]:.0f}%; "
          + ", ".join(f"{NAME[b]} {sum(sum(x[1]) for x in alls if x[0] == b)} of {sum(len(x[1]) for x in alls if x[0] == b)}" for b in BOSS))
    print("  wins of three by situation: " + "; ".join(f"{NAME[b]} " + " ".join(str(sum(x[1])) for x in alls if x[0] == b) for b in BOSS))
    tf = table("p0-ts", "mcw6paf")
    f1 = sum(won(tf[i][0]) for i in tf) + sum(x[1] for x in first if x[0] != "ts")
    fa = sum(won(x) for i in tf for x in tf[i].values()) + sum(sum(x[1]) for x in alls if x[0] != "ts")
    print(f"  with the forms counted at the Test Subject (mcw6paf there): first seeds {f1} of {len(first)}, all seeds {fa} of {nf}; "
          f"Fisher against {RUNS_WON} of {RUNS_FIGHTS}: p = {fisher_greater(f1, len(first), RUNS_WON, RUNS_FIGHTS):.4f}")

    print("\nSet G (mcw6pa, one sample seed) beside each fight's outcome in its run")
    gw = gn = 0
    for b in BOSS:
        t = table("g-" + b, "mcw6pa")
        specs = data["g-" + b]["specs"]
        cells = {"won in both": 0, "won in the run only": 0, "won in the replay only": 0, "lost in both": 0, "host error": 0}
        for i in sorted(t):
            x, inrun = t[i][0], bool(specs[i]["source"].get("won_in_run"))
            if not ended(x):
                cells["host error"] += 1
                continue
            gn += 1
            gw += won(x)
            cells[("won in both" if inrun else "won in the replay only") if won(x) else ("won in the run only" if inrun else "lost in both")] += 1
        print(f"  {NAME[b]}: {len(t)} situations, {sum(bool(f['source'].get('won_in_run')) for f in specs)} won in the runs; " + ", ".join(f"{k} {v}" for k, v in cells.items()))
    print(f"  replay {gw} of {gn} played to an end; in the runs {RUNS_WON} of {RUNS_FIGHTS}")

    print("\nH3: the Queen situations, mcw6pam against mcw6pa")
    plus = minus = equal = wa = wm = 0
    for n in ("g-queen", "p0-queen"):
        ta, tm = table(n, "mcw6pa"), table(n, "mcw6pam")
        for i in sorted(ta):
            ss = [s for s in ta[i] if ended(ta[i][s]) and ended(tm[i].get(s))]
            x, y = sum(won(ta[i][s]) for s in ss), sum(won(tm[i][s]) for s in ss)
            wa, wm = wa + x, wm + y
            plus, minus, equal = plus + (y > x), minus + (y < x), equal + (y == x)
    print(f"  fights won {wa} (mcw6pa) and {wm} (mcw6pam); situations with more {plus}, fewer {minus}, equal {equal}; one-sided sign test p = {sign_greater(plus, minus):.3f}")
    for n in ("g-queen", "p0-queen", "p-queen"):
        for arm in ("mcw6pa", "mcw6pam"):
            lo = [x for t in table(n, arm).values() for x in t.values() if ended(x) and not won(x)]
            q = [next((e[1] for e in x["enemies"] if e[0] == "QUEEN"), 0) for x in lo]
            alive = sum(1 for x in lo if any(e[0] != "QUEEN" and e[1] > 0 for e in x["enemies"]))
            print(f"  {n} {arm}: {len(lo)} lost, the Queen's HP left {mean(q):.0f} on average, the minion alive at the end in {alive}")

    print("\nSet P (the ascension the Player played), wins of three by situation")
    last = {}
    for b in BOSS:
        for f in data["p-" + b]["specs"]:
            last[f["source"]["run"]] = max(last.get(f["source"]["run"], 0), f["source"]["floor"])
    tp = pw = 0
    for b in BOSS:
        for i, f in enumerate(data["p-" + b]["specs"]):
            src = f["source"]
            player = bool(src["run_won"]) or src["floor"] < last[src["run"]]      # a lost run's last boss fight is the lost one
            res = {arm: sum(won(x) for x in table("p-" + b, arm)[i].values()) for arm in data["p-" + b]["arms"]}
            tp, pw = tp + res["mcw6pa"], pw + player
            print(f"  {NAME[b]} {i}: A{f['ascension']}, HP {f['hp']}/{f['max_hp']}, the Player {'won' if player else 'lost'}; " + ", ".join(f"{k} {v}" for k, v in res.items()))
    print(f"  mcw6pa {tp} of 45; the Player {pw} of 15")


if __name__ == "__main__":
    main()
