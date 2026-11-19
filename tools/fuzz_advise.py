#!/usr/bin/env python3
"""Wide robustness fuzz of tools/advise.py: damaged copies of the advisor's own screen fixtures (from
tools/tests/test_advise.py), with keys dropped, values set to null, list items dropped, or values replaced by a
value of the wrong type. Counts the answers that come back as [ADVICE FAILED] by error site, so the commonest
sites can be guarded next. The advisor must never raise; tools/tests/test_advise_fuzz.py enforces that.

Usage: python3 -I tools/fuzz_advise.py [--rounds 3] [--per-round 700] [--top 25]
"""
import argparse
import collections
import copy
import io
import random
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "tests"))
import advise  # noqa: E402
import draft  # noqa: E402
import test_advise  # noqa: E402
import test_advise_fuzz as fz  # noqa: E402


def fixtures():
    """Every state test_advise.py passes to advise(), captured by running that test module once."""
    seen, orig = [], advise.advise
    advise.advise = lambda s, *a, **k: (seen.append(copy.deepcopy(s)), orig(s, *a, **k))[1]
    try:
        with redirect_stdout(io.StringIO()):
            unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromModule(test_advise))
    finally:
        advise.advise = orig
    return seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--per-round", type=int, default=700)
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()
    draft.simulated_boss_value = lambda *a, **k: None  # speed: the fight simulation is tested elsewhere
    seen = fixtures()
    print(f"fixtures {len(seen)}")
    sites = collections.Counter()
    total = 0
    for r in range(args.rounds):
        rng = random.Random(100 + r)
        for i in range(args.per_round):
            base = rng.choice(seen)
            m = fz._mutate(base, rng) if i % 2 else fz._retype(base, rng)
            with redirect_stdout(io.StringIO()):
                out = advise.advise(m)  # raises only on a bug in the wrapper itself
            total += 1
            if out.startswith("[ADVICE FAILED]"):
                sites[out.splitlines()[0].split(". Act by judgment")[0]] += 1
    print(f"states {total}, wrapped failures {sum(sites.values())}")
    for k, v in sites.most_common(args.top):
        print(f"{v:4d}  {k}")


if __name__ == "__main__":
    main()
