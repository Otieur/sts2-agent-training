#!/usr/bin/env python3
"""Fight situations compared by the run policy that reached them (boss replay 5).

    python3 -I tools/origin_compare.py data/learn/bench/boss-replay-5 --specs data/sim/boss-replay-5.json --control <policy>

The fight set (`tools/boss_specs.py`) keeps, for every situation, the policy and the seed of the run it comes from. One
fight-search arm plays every situation with several sample seeds (`tools/learn/bench.py`); a situation's value is the
share of its fights won. Prints, per policy of origin: situations, fights won, the mean share, by encounter, and how the
runs themselves ended these fights. Then the seeds on which the control policy and another policy both reached the
fight: the other policies' value (their mean where several are there) against the control's, a one-sided sign test over
the seeds whose two values differ, and the same for each other policy alone. A fight with an error is left out and
counted."""
import argparse
import json
import sys
from collections import defaultdict
from math import comb
from pathlib import Path


def load(folder):
    return [json.loads(line) for f in sorted(Path(folder).glob("shard-*.jsonl")) for line in f.open()]


def sign_test(better, worse):
    """One-sided: the chance of at least `better` of `better + worse` when each is as likely as not."""
    n = better + worse
    return 1.0 if n == 0 else sum(comb(n, i) for i in range(better, n + 1)) / 2 ** n


def situations(recs, specs, arm):
    """Per fight spec played: its policy and seed of origin, encounter, fights played and won, and the run's own outcome."""
    out, errors = {}, 0
    for r in recs:
        a = r["arms"].get(arm) or {}
        if "status" not in a:
            errors += 1
            continue
        src = specs[r["fight"]]["source"]
        s = out.setdefault(r["fight"], {"policy": src.get("policy"), "seed": src.get("run"), "encounter": r["encounter"], "n": 0, "won": 0, "won_in_run": bool(src.get("won_in_run"))})
        s["n"] += 1
        s["won"] += a["status"] == "won"
    return out, errors


def paired(sits, control, others):
    """Per seed with the control's situation and at least one of `others`: (control share, mean share of the others)."""
    by = defaultdict(dict)
    for s in sits.values():
        by[s["seed"]][s["policy"]] = s["won"] / s["n"]
    return {seed: (d[control], sum(d[o] for o in others if o in d) / sum(o in d for o in others))
            for seed, d in by.items() if control in d and any(o in d for o in others)}


def report(folder, specs_path, arm, control):
    specs = json.loads(Path(specs_path).read_text())["fights"]
    sits, errors = situations(load(folder), specs, arm)
    if not sits:
        print(f"{folder}: no fights of {arm}")
        return 1
    policies = sorted({s["policy"] for s in sits.values()}, key=lambda p: (p != control, p))
    print(f"{folder}: {len(sits)} situations, {sum(s['n'] for s in sits.values())} fights of {arm}" + (f"; {errors} left out for an error" if errors else ""))
    for p in policies:
        mine = [s for s in sits.values() if s["policy"] == p]
        enc = defaultdict(lambda: [0, 0])
        for s in mine:
            enc[s["encounter"]][0] += s["n"]
            enc[s["encounter"]][1] += s["won"]
        print(f"  {p}{' (control)' if p == control else ''}: {len(mine)} situations, {sum(s['won'] for s in mine)} of {sum(s['n'] for s in mine)} fights won, "
              f"mean share {sum(s['won'] / s['n'] for s in mine) / len(mine):.3f}; situations with a fight won {sum(s['won'] > 0 for s in mine)}; won in the runs {sum(s['won_in_run'] for s in mine)}")
        print("      " + "; ".join(f"{e} {w} of {n}" for e, (n, w) in sorted(enc.items())))
    others = [p for p in policies if p != control]
    for label, group in [("the other policies together", others)] + [(o, [o]) for o in others if len(others) > 1]:
        pairs = paired(sits, control, group)
        better, worse = sum(y > x for x, y in pairs.values()), sum(y < x for x, y in pairs.values())
        if pairs:
            print(f"  seeds with the control and {label}: {len(pairs)}; mean share {sum(y for _, y in pairs.values()) / len(pairs):.3f} against {sum(x for x, _ in pairs.values()) / len(pairs):.3f}; "
                  f"more fights won on {better}, fewer on {worse}; one-sided sign test p = {sign_test(better, worse):.3f}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("folder")
    ap.add_argument("--specs", required=True, help="the fight set the folder played")
    ap.add_argument("--arm", default="mcw6paf", help="the fight-search arm read")
    ap.add_argument("--control", required=True, help="the run policy the others are compared with")
    a = ap.parse_args(argv)
    return report(a.folder, a.specs, a.arm, a.control)


if __name__ == "__main__":
    sys.exit(main())
