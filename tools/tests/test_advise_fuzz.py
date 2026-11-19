"""Robustness: tools/advise.py on damaged copies of its own screen fixtures (keys dropped, values set to null, list items
dropped). Live states may lack fields the documentation promises; the advisor must still answer, never raise or fail.
With values of the wrong type it may answer [ADVICE FAILED], but it must still answer and never raise."""
import copy
import io
import random
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import advise  # noqa: E402
import draft  # noqa: E402
import journal  # noqa: E402
import sts  # noqa: E402
import stsstate  # noqa: E402
import test_advise  # noqa: E402


def _paths(o, pre=()):
    if isinstance(o, dict):
        for k, v in o.items():
            yield pre + (k,)
            yield from _paths(v, pre + (k,))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield pre + (i,)
            yield from _paths(v, pre + (i,))


def _mutate(s, rng):
    s = copy.deepcopy(s)
    for _ in range(rng.randint(1, 3)):
        ps = list(_paths(s))
        if not ps:
            break
        p = rng.choice(ps)
        parent = s
        for k in p[:-1]:
            parent = parent[k]
        k = p[-1]
        if isinstance(parent, dict):
            if rng.random() < 0.5:
                parent.pop(k, None)
            else:
                parent[k] = None
        elif isinstance(parent, list) and k < len(parent):
            parent.pop(k)
    return s


WRONG_TYPES = ["", "x", 0, -1, 1.5, [], {}, True]


def _retype(s, rng):
    """A copy of s with one or two values (any depth) replaced by a value of a wrong type."""
    s = copy.deepcopy(s)
    for _ in range(rng.randint(1, 2)):
        ps = list(_paths(s))
        if not ps:
            break
        p = rng.choice(ps)
        parent = s
        for k in p[:-1]:
            parent = parent[k]
        k = p[-1]
        if isinstance(parent, dict) or (isinstance(parent, list) and k < len(parent)):
            parent[k] = rng.choice(WRONG_TYPES)
    return s


class TestAdviseFuzz(unittest.TestCase):
    def test_damaged_states(self):
        seen = []
        orig, sim = advise.advise, draft.simulated_boss_value
        advise.advise = lambda s, *a, **k: (seen.append(copy.deepcopy(s)), orig(s, *a, **k))[1]
        draft.simulated_boss_value = lambda *a, **k: None  # speed: the fight simulation is tested elsewhere
        try:
            with redirect_stdout(io.StringIO()):
                unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromModule(test_advise))
            advise.advise = orig
            self.assertGreater(len(seen), 10)
            rng = random.Random(5)
            failures = []
            for _ in range(300):
                m = _mutate(rng.choice(seen), rng)
                with redirect_stdout(io.StringIO()):
                    out = advise.advise(m)
                if out.startswith("[ADVICE FAILED]"):
                    failures.append(out)
            self.assertEqual(failures, [])
        finally:
            advise.advise, draft.simulated_boss_value = orig, sim
        self.assertTrue(advise.advise(None).startswith("no state"))
        # the other helpers that read live states must not raise on them either
        for m in [_mutate(rng.choice(seen), rng) for _ in range(150)]:
            journal.status_from_state(m)
            sts.brief_sts2agent(m.get("data", m))
            stsstate.decision_point(stsstate.compact(m))
        # wrong-type values: the advisor may answer [ADVICE FAILED], but must still answer with text, never raise
        draft.simulated_boss_value = lambda *a, **k: None
        try:
            for _ in range(200):
                with redirect_stdout(io.StringIO()):
                    out = advise.advise(_retype(rng.choice(seen), rng))
                self.assertIsInstance(out, str)
        finally:
            draft.simulated_boss_value = sim


if __name__ == "__main__":
    unittest.main()
