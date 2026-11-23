#!/usr/bin/env python3
"""Two fight-benchmark arms compared on Test Subject files, by situation (boss replays 2 and 3).

    python3 -I tools/forms_compare.py data/learn/bench/boss-replay-2-g-ts data/learn/bench/boss-replay-2-p0-ts
    python3 -I tools/forms_compare.py --a mcw6paf --b mcw6pafe data/learn/bench/boss-replay-3-t1 data/learn/bench/boss-replay-3-t2

A situation is one fight spec of a folder; its value is the mean over its sample seeds. Share of the three forms' HP
removed: a win counts as all of it; a loss counts the forms killed plus the damage to the form alive at the end (the form
is read from the max HP of the enemy alive). Tests: one-sided sign tests over the situations whose two arms differ, for
`--b` against `--a`. A fight with a host error in either arm is left out and listed. With `end_checks` in the records
(arms with the end-of-turn check, `tools/selfplay.py END_TURN_Z`), the counts are summed per arm."""
import argparse
import glob
import json
import sys
from math import comb

FORMS = ((100, 200, 300), (111, 212, 313))      # [GAME] v0.111.1, base and A8+ (tools/sim.py FORMS)


def removed(arm):
    if arm.get("status") == "won":
        return 1.0
    ts = [e for e in (arm.get("enemies") or []) if e[0] == "TEST_SUBJECT"]
    if not ts:
        return None
    _, cur, mx = ts[0]
    for forms in FORMS:
        if mx in forms:
            i = forms.index(mx)
            return 1 - (cur + sum(forms[i + 1:])) / sum(forms)
    return None


def form_of(arm):
    if arm.get("status") == "won":
        return 4
    ts = [e for e in (arm.get("enemies") or []) if e[0] == "TEST_SUBJECT"]
    for forms in FORMS:
        if ts and ts[0][2] in forms:
            return forms.index(ts[0][2]) + 1
    return None


def sign_p(up, dn):
    n = up + dn
    return sum(comb(n, k) for k in range(up, n + 1)) / 2 ** n if n else 1.0


def read(folders, a, b):
    sit, errors = {}, []
    for folder in folders:
        label = folder.rstrip("/").rsplit("/", 1)[-1]
        for path in sorted(glob.glob(f"{folder}/shard-*.jsonl")):
            for line in open(path):
                if not line.strip():
                    continue
                r = json.loads(line)
                x, y = r["arms"].get(a) or {}, r["arms"].get(b) or {}
                if "error" in x or "error" in y or not x or not y:
                    errors.append((label, r["fight"], r["sample"], a if ("error" in x or not x) else b))
                    continue
                sit.setdefault((label, r["fight"]), []).append((x, y))
    return sit, errors


def compare(sit, keys, a, b):
    n = sum(len(sit[k]) for k in keys)
    mean = lambda f, side: [sum(f(p[side]) for p in sit[k]) / len(sit[k]) for k in keys]
    won = lambda arm: arm["status"] == "won"
    ra, rb, va, vb = mean(removed, 0), mean(removed, 1), mean(won, 0), mean(won, 1)
    up, dn = sum(q > p for p, q in zip(ra, rb)), sum(q < p for p, q in zip(ra, rb))
    wup, wdn = sum(q > p for p, q in zip(va, vb)), sum(q < p for p, q in zip(va, vb))
    fa = [form_of(x) for k in keys for x, _ in sit[k]]
    fb = [form_of(y) for k in keys for _, y in sit[k]]
    checks = {}
    for side, name in ((0, a), (1, b)):
        tot = {}
        for k in keys:
            for p in sit[k]:
                for key, v in (p[side].get("end_checks") or {}).items():
                    tot[key] = tot.get(key, 0) + v
        checks[name] = tot
    return {"situations": len(keys), "fights": n,
            "won": {a: sum(won(x) for k in keys for x, _ in sit[k]), b: sum(won(y) for k in keys for _, y in sit[k])},
            "situations_won_more": wup, "situations_won_fewer": wdn, "wins_sign_p": sign_p(wup, wdn),
            "share_removed": {a: sum(ra) / len(ra), b: sum(rb) / len(rb)}, "removed_more": up, "removed_less": dn,
            "removed_equal": len(keys) - up - dn, "removed_sign_p": sign_p(up, dn),
            "ended_in_form_1_2_3_won": {a: [fa.count(i) for i in (1, 2, 3, 4)], b: [fb.count(i) for i in (1, 2, 3, 4)]},
            "turns": {a: sum(x["turns"] for k in keys for x, _ in sit[k]) / n, b: sum(y["turns"] for k in keys for _, y in sit[k]) / n},
            "end_checks": checks}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("folders", nargs="+")
    ap.add_argument("--a", default="mcw6pa", help="the arm compared against")
    ap.add_argument("--b", default="mcw6paf", help="the arm tested")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    sit, errors = read(a.folders, a.a, a.b)
    if not sit:
        print("no fight with both arms")
        return 1
    labels = sorted({k[0] for k in sit})
    out = {"errors_left_out": errors, "all": compare(sit, list(sit), a.a, a.b)}
    for lab in labels if len(labels) > 1 else []:
        out[lab] = compare(sit, [k for k in sit if k[0] == lab], a.a, a.b)
    if a.json:
        print(json.dumps(out, indent=1))
        return 0
    print("left out for a host error or a missing arm:", errors)
    for lab, c in out.items():
        if lab == "errors_left_out":
            continue
        print(f"{lab}: {c['situations']} situations, {c['fights']} fights")
        print(f"  won: {a.a} {c['won'][a.a]}, {a.b} {c['won'][a.b]}; situations where {a.b} wins more {c['situations_won_more']}, fewer {c['situations_won_fewer']}, sign p {c['wins_sign_p']:.3f}")
        print(f"  share of the forms' HP removed: {a.a} {c['share_removed'][a.a]:.3f}, {a.b} {c['share_removed'][a.b]:.3f}; "
              f"more {c['removed_more']}, less {c['removed_less']}, equal {c['removed_equal']}, sign p {c['removed_sign_p']:.2g}")
        print(f"  ended in form 1/2/3/won: {a.a} {c['ended_in_form_1_2_3_won'][a.a]}, {a.b} {c['ended_in_form_1_2_3_won'][a.b]}; "
              f"turns {c['turns'][a.a]:.1f} / {c['turns'][a.b]:.1f}")
        if any(c["end_checks"].values()):
            print(f"  end-of-turn checks: {c['end_checks']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
