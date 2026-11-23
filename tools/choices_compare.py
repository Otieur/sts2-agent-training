#!/usr/bin/env python3
"""Two fight-benchmark arms compared by situation, with the card choices answered inside the fights (boss replay 4).

    python3 -I tools/choices_compare.py --a mcw6paf --b mcw6pafc data/learn/bench/boss-replay-4-d [more folders]

A situation is one fight spec of a folder (`tools/learn/bench.py --benchmark`); its value is the mean over its sample
seeds. Per folder: fights won per arm, in all and by encounter; the situations where `--b` wins more and fewer of its
fights than `--a`, with a one-sided sign test for `--b` over the situations whose arms differ; over the fights both
arms win, the mean difference in HP left with a bootstrap 95% interval; the mean difference in priced value over all
fights; seconds per fight. Then the choices per arm (`choices` in the fight records, `tools/selfplay.py CHOICES`): how
many, how many were searched (more than one answer was a candidate), how many of those took another answer than the
first option, by kind of screen, and at the Knowledge Demon's curse what was taken at each offer. A fight with an error
in either arm is left out and listed. With `--specs` (the fight set played) the fights won are also split by the
run benchmark a situation comes from."""
import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

OFFER = {"MIND_ROT": 1, "SLOTH": 2, "WASTE_AWAY": 3}      # the card offered beside Disintegration at each Curse of Knowledge


def load(folder):
    return [json.loads(line) for f in sorted(Path(folder).glob("shard-*.jsonl")) for line in f.open()]


def sign_test(better, worse):
    """One-sided: the chance of at least `better` of `better + worse` when each is as likely as not."""
    n = better + worse
    return 1.0 if n == 0 else sum(comb(n, i) for i in range(better, n + 1)) / 2 ** n


def pairs(recs, a, b):
    """(records with both arms played, records left out for an error in either arm)."""
    ok = [r for r in recs if "status" in r["arms"].get(a, {}) and "status" in r["arms"].get(b, {})]
    return ok, [r for r in recs if r not in ok]


def by_situation(ok, a, b):
    """Per fight spec: (mean wins of a, mean wins of b) over its sample seeds."""
    won = defaultdict(lambda: [[], []])
    for r in ok:
        won[r["fight"]][0].append(r["arms"][a]["status"] == "won")
        won[r["fight"]][1].append(r["arms"][b]["status"] == "won")
    return {i: (sum(x) / len(x), sum(y) / len(y)) for i, (x, y) in won.items()}


def bootstrap(diffs, reps=4000, seed=0):
    if not diffs:
        return None
    rng = random.Random(seed)
    means = sorted(sum(rng.choice(diffs) for _ in diffs) / len(diffs) for _ in range(reps))
    return sum(diffs) / len(diffs), means[int(0.025 * reps)], means[int(0.975 * reps) - 1]


def choice_summary(ok, arm):
    c = {"choices": 0, "searched": 0, "not_first": 0, "kinds": Counter(), "curse": defaultdict(Counter)}
    for r in ok:
        for ch in r["arms"][arm].get("choices") or []:
            c["choices"] += 1
            searched = ch.get("candidates", 1) > 1
            c["searched"] += searched
            c["not_first"] += searched and not ch.get("first", True)
            c["kinds"][(ch.get("kind"), "searched" if searched else "first option", "other answer" if not ch.get("first", True) else "first")] += 1
            offered = [o for o in ch.get("options") or [] if o in OFFER]
            if "DISINTEGRATION" in (ch.get("options") or []) and offered:
                c["curse"][OFFER[offered[0]]]["+".join(ch.get("taken") or ["nothing"])] += 1
    return c


def by_origin(ok, specs, a, b):
    """Fights and fights won per arm, by the run benchmark a situation comes from (`source.benchmark` in the fight set)."""
    out = defaultdict(lambda: [0, 0, 0])
    for r in ok:
        e = out[(specs[r["fight"]].get("source") or {}).get("benchmark") or "?"]
        e[0] += 1
        e[1] += r["arms"][a]["status"] == "won"
        e[2] += r["arms"][b]["status"] == "won"
    return dict(out)


def report(folder, a, b, specs=None):
    recs = load(folder)
    ok, out = pairs(recs, a, b)
    print(f"{folder}: {len(recs)} fights recorded, {len(ok)} with both arms" + (f"; left out for an error: {[(r['fight'], r['sample']) for r in out]}" if out else ""))
    if not ok:
        return 1
    wa, wb = sum(r["arms"][a]["status"] == "won" for r in ok), sum(r["arms"][b]["status"] == "won" for r in ok)
    print(f"  fights won: {a} {wa} of {len(ok)}, {b} {wb} of {len(ok)}")
    enc = defaultdict(lambda: [0, 0, 0])
    for r in ok:
        e = enc[r["encounter"]]
        e[0] += 1
        e[1] += r["arms"][a]["status"] == "won"
        e[2] += r["arms"][b]["status"] == "won"
    for name, (n, x, y) in sorted(enc.items()):
        print(f"    {name}: {x} and {y} of {n}")
    if specs:
        for name, (n, x, y) in sorted(by_origin(ok, specs, a, b).items()):
            print(f"    situations of {name}: {x} and {y} of {n}")
    sit = by_situation(ok, a, b)
    better, worse = sum(y > x for x, y in sit.values()), sum(y < x for x, y in sit.values())
    print(f"  situations: {len(sit)}; {b} wins more of its fights in {better}, fewer in {worse}; one-sided sign test p = {sign_test(better, worse):.3f}")
    both = [r["arms"][b]["hp"] - r["arms"][a]["hp"] for r in ok if r["arms"][a]["status"] == "won" and r["arms"][b]["status"] == "won"]
    bs = bootstrap(both)
    if bs:
        print(f"  HP left where both win ({len(both)} fights): {b} minus {a} mean {bs[0]:+.2f} (bootstrap 95% {bs[1]:+.2f} to {bs[2]:+.2f})")
    pv = bootstrap([r["arms"][b]["value_priced"] - r["arms"][a]["value_priced"] for r in ok])
    print(f"  priced value over all fights: {b} minus {a} mean {pv[0]:+.2f} (bootstrap 95% {pv[1]:+.2f} to {pv[2]:+.2f})")
    for arm in (a, b):
        secs = [r["arms"][arm].get("seconds", 0) for r in ok]
        c = choice_summary(ok, arm)
        print(f"  {arm}: {sum(secs) / len(secs):.0f} s a fight; choices {c['choices']} ({c['choices'] / len(ok):.1f} a fight), searched {c['searched']}, "
              f"another answer than the first option {c['not_first']}")
        for k, v in sorted(c["kinds"].items(), key=lambda kv: (str(kv[0][0]), kv[0][1], kv[0][2])):
            print(f"      {k[0]}, {k[1]}, {k[2]}: {v}")
        for offer in sorted(c["curse"]):
            print(f"      Curse of Knowledge, offer {offer}: {dict(c['curse'][offer])}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("folders", nargs="+")
    ap.add_argument("--a", default="mcw6paf", help="the arm compared with")
    ap.add_argument("--b", default="mcw6pafc", help="the arm tested")
    ap.add_argument("--specs", help="the fight set the folders played: also splits the fights won by the run benchmark a situation comes from")
    a = ap.parse_args(argv)
    specs = json.loads(Path(a.specs).read_text())["fights"] if a.specs else None
    return max(report(f, a.a, a.b, specs) for f in a.folders)


if __name__ == "__main__":
    sys.exit(main())
