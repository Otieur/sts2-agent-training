#!/usr/bin/env python3
"""One fight set played twice with the same arm and sample seeds, once as the runs reached it and once changed (boss replay 7).

    python3 -I tools/variant_compare.py --base data/learn/bench/boss-replay-5 --variant data/learn/bench/boss-replay-7-full \
        --specs data/sim/boss-replay-5.json --variant-specs data/sim/boss-replay-7-full.json

The variant folder played the same situations in the same order with something changed in their specs (the HP at the
start of the fight). A situation's value is the share of its fights won. Prints fights won in both folders, in all and
by encounter; the situations that win a larger and a smaller share in the variant, with a one-sided sign test over the
situations whose shares differ; the same by thirds of the HP fraction the situations had in the base set; over the
fights won in both folders (the same situation and sample seed), the mean difference in HP left. Situations whose spec
is the same in both sets are replays of the same fights: how many of them end the same way is printed as a check. A
fight with an error in either folder is left out of both and counted."""
import argparse
import json
import random
import sys
from collections import defaultdict
from math import comb
from pathlib import Path


def load(folder):
    return [json.loads(line) for f in sorted(Path(folder).glob("shard-*.jsonl")) for line in f.read_text().splitlines() if line.strip()]


def sign_test(better, worse):
    """One-sided: the chance of at least `better` of `better + worse` when each is as likely as not."""
    n = better + worse
    return 1.0 if n == 0 else sum(comb(n, i) for i in range(better, n + 1)) / 2 ** n


def bootstrap(diffs, reps=4000, seed=0):
    if not diffs:
        return None
    rng = random.Random(seed)
    means = sorted(sum(rng.choice(diffs) for _ in diffs) / len(diffs) for _ in range(reps))
    return sum(diffs) / len(diffs), means[int(0.025 * reps)], means[int(0.975 * reps) - 1]


def paired(base, variant, arm):
    """{(fight, sample): (base arm record, variant arm record)} for the fights with an outcome in both folders, and the
    number of fights left out for an error in either."""
    a = {(r["fight"], r["sample"]): r["arms"].get(arm) or {} for r in base}
    b = {(r["fight"], r["sample"]): r["arms"].get(arm) or {} for r in variant}
    keys = sorted(set(a) & set(b))
    ok = {k: (a[k], b[k]) for k in keys if "status" in a[k] and "status" in b[k]}
    return ok, len(set(a) | set(b)) - len(ok)


def shares(ok):
    """Per situation: (share of fights won in the base folder, in the variant folder, fights)."""
    won = defaultdict(lambda: [0, 0, 0])
    for (fight, _), (x, y) in ok.items():
        w = won[fight]
        w[0] += x["status"] == "won"
        w[1] += y["status"] == "won"
        w[2] += 1
    return {f: (x / n, y / n, n) for f, (x, y, n) in won.items()}


def thirds(values):
    """Each key's third (0, 1, 2) by its value, the keys in order of value split into three groups as equal as can be."""
    order = sorted(values, key=lambda k: (values[k], k))
    return {k: min(2, i * 3 // len(order)) for i, k in enumerate(order)}


def report(base_dir, variant_dir, specs_path, variant_specs_path, arm):
    specs = json.loads(Path(specs_path).read_text())["fights"]
    vspecs = json.loads(Path(variant_specs_path).read_text())["fights"] if variant_specs_path else None
    ok, left_out = paired(load(base_dir), load(variant_dir), arm)
    if not ok:
        print("no fight with an outcome in both folders")
        return 1
    sh = shares(ok)
    wa, wb = sum(x["status"] == "won" for x, _ in ok.values()), sum(y["status"] == "won" for _, y in ok.values())
    print(f"{base_dir} against {variant_dir}: {len(sh)} situations, {len(ok)} fights of {arm} in both; left out for an error: {left_out}")
    print(f"  fights won: base {wa} of {len(ok)} ({wa / len(ok):.1%}), variant {wb} of {len(ok)} ({wb / len(ok):.1%})")
    enc = defaultdict(lambda: [0, 0, 0])
    for (fight, _), (x, y) in ok.items():
        e = enc[specs[fight]["encounter"]]
        e[0] += 1
        e[1] += x["status"] == "won"
        e[2] += y["status"] == "won"
    for name, (n, x, y) in sorted(enc.items()):
        print(f"    {name}: {x} and {y} of {n}")

    def line(label, keys):
        better, worse = sum(sh[f][1] > sh[f][0] for f in keys), sum(sh[f][1] < sh[f][0] for f in keys)
        n = sum(sh[f][2] for f in keys)
        print(f"  {label}: {len(keys)} situations; base {sum(sh[f][0] * sh[f][2] for f in keys):.0f} and variant {sum(sh[f][1] * sh[f][2] for f in keys):.0f} of {n} fights; "
              f"larger share in {better}, smaller in {worse}; one-sided sign test p = {sign_test(better, worse):.3f}")
    line("all situations", sorted(sh))
    frac = {f: specs[f]["hp"] / specs[f]["max_hp"] for f in sh}
    third = thirds(frac)
    for t, name in enumerate(("lowest third of HP at arrival", "middle third", "highest third")):
        keys = sorted(f for f in sh if third[f] == t)
        if keys:
            line(f"{name} ({min(frac[f] for f in keys):.2f} to {max(frac[f] for f in keys):.2f} of max HP)", keys)
    if vspecs:
        changed = sorted(f for f in sh if vspecs[f].get("hp") != specs[f].get("hp"))
        line("situations whose HP the variant changes", changed)
        same = [k for k in ok if k[0] not in changed]
        if same:
            agree = sum(ok[k][0]["status"] == ok[k][1]["status"] and ok[k][0].get("hp") == ok[k][1].get("hp") for k in same)
            print(f"  fights of situations the variant does not change: {len(same)}; the same outcome and HP left in {agree}")
        gain = [vspecs[f]["hp"] - specs[f]["hp"] for f in changed]
        if gain:
            print(f"  HP added where changed: mean {sum(gain) / len(gain):.1f}, from {min(gain)} to {max(gain)}")
    both = [y["hp"] - x["hp"] for x, y in ok.values() if x["status"] == "won" and y["status"] == "won"]
    bs = bootstrap(both)
    if bs:
        print(f"  HP left where both are won ({len(both)} fights): variant minus base mean {bs[0]:+.2f} (bootstrap 95% {bs[1]:+.2f} to {bs[2]:+.2f})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--base", required=True, help="the folder that played the situations as the runs reached them")
    ap.add_argument("--variant", required=True, help="the folder that played them changed")
    ap.add_argument("--specs", required=True, help="the fight set of the base folder")
    ap.add_argument("--variant-specs", help="the fight set of the variant folder: also reports the situations it changes and those it does not")
    ap.add_argument("--arm", default="mcw6paf")
    a = ap.parse_args(argv)
    return report(a.base, a.variant, a.specs, a.variant_specs, a.arm)


if __name__ == "__main__":
    sys.exit(main())
