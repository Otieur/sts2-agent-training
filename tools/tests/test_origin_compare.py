"""Offline tests for tools/origin_compare.py."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import origin_compare as oc  # noqa: E402

SPECS = [{"source": {"policy": p, "run": seed, "won_in_run": w}} for p, seed, w in
         [("C", "s1", False), ("C+t", "s1", True), ("C+u", "s1", False), ("C", "s2", False), ("C+t", "s3", False), ("C", "s4", True), ("C+u", "s4", False)]]


def rec(fight, sample, won):
    return {"fight": fight, "sample": sample, "encounter": "QUEEN_BOSS", "arms": {"x": {"status": "won" if won else "lost"}}}


class TestOriginCompare(unittest.TestCase):
    def test_situations_and_pairs_by_seed(self):
        recs = [rec(0, 0, False), rec(0, 1, False), rec(1, 0, True), rec(1, 1, False), rec(2, 0, True), rec(2, 1, True), rec(3, 0, False),
                rec(4, 0, True), rec(5, 0, True), rec(5, 1, True), rec(6, 0, False), rec(6, 1, True),
                {"fight": 3, "sample": 1, "encounter": "QUEEN_BOSS", "arms": {"x": {"error": "host"}}}]
        sits, errors = oc.situations(recs, SPECS, "x")
        self.assertEqual((len(sits), errors), (7, 1))
        self.assertEqual((sits[1]["policy"], sits[1]["seed"], sits[1]["n"], sits[1]["won"], sits[1]["won_in_run"]), ("C+t", "s1", 2, 1, True))
        self.assertEqual(sits[3]["n"], 1)                                   # the fight with an error is left out
        both = oc.paired(sits, "C", ["C+t", "C+u"])
        self.assertEqual(both, {"s1": (0.0, 0.75), "s4": (1.0, 0.5)})       # s2 has only the control, s3 only another policy
        self.assertEqual(oc.paired(sits, "C", ["C+t"]), {"s1": (0.0, 0.5)})

    def test_sign_test(self):
        self.assertEqual(oc.sign_test(4, 0), 0.0625)
        self.assertEqual(oc.sign_test(0, 0), 1.0)


if __name__ == "__main__":
    unittest.main()
