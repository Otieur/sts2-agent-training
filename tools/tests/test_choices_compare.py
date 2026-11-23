"""Offline tests for tools/choices_compare.py."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import choices_compare as cc  # noqa: E402


def rec(fight, sample, a, b, choices_b=(), enc="KNOWLEDGE_DEMON_BOSS"):
    arm = lambda won, ch: {"status": "won" if won else "lost", "hp": 30 if won else 0, "value_priced": 30 if won else -200, "seconds": 40, "choices": list(ch)}
    return {"fight": fight, "sample": sample, "encounter": enc, "arms": {"x": arm(a, ()), "y": arm(b, choices_b)}}


class TestChoicesCompare(unittest.TestCase):
    def test_situations_and_the_sign_test(self):
        recs = [rec(0, 0, False, True), rec(0, 1, False, False), rec(1, 0, True, True), rec(1, 1, True, False), rec(2, 0, False, False),
                {"fight": 3, "sample": 0, "encounter": "E", "arms": {"x": {"error": "host"}, "y": {"status": "won"}}}]
        ok, out = cc.pairs(recs, "x", "y")
        self.assertEqual((len(ok), [(r["fight"], r["sample"]) for r in out]), (5, [(3, 0)]))
        self.assertEqual(cc.by_situation(ok, "x", "y"), {0: (0.0, 0.5), 1: (1.0, 0.5), 2: (0.0, 0.0)})
        self.assertEqual(cc.sign_test(3, 0), 0.125)
        self.assertEqual(cc.sign_test(0, 0), 1.0)
        self.assertEqual(cc.sign_test(1, 1), 0.75)

    def test_choices_are_counted_by_kind_and_curse_offer(self):
        curse = lambda other, taken, n: {"kind": "FromChooseACardScreen", "options": ["DISINTEGRATION", other], "taken": [taken], "candidates": n, "first": taken == "DISINTEGRATION"}
        ch = [curse("MIND_ROT", "MIND_ROT", 2), curse("SLOTH", "DISINTEGRATION", 2), curse("WASTE_AWAY", "DISINTEGRATION", 1),
              {"kind": "FromHand", "options": ["BASH", "ANGER"], "taken": ["ANGER"], "candidates": 2, "first": False}]
        c = cc.choice_summary([rec(0, 0, False, True, ch)], "y")
        self.assertEqual((c["choices"], c["searched"], c["not_first"]), (4, 3, 2))
        self.assertEqual({k: dict(v) for k, v in c["curse"].items()}, {1: {"MIND_ROT": 1}, 2: {"DISINTEGRATION": 1}, 3: {"DISINTEGRATION": 1}})
        self.assertEqual(cc.choice_summary([rec(0, 0, False, True, ch)], "x")["choices"], 0)

    def test_fights_won_by_the_benchmark_of_origin(self):
        specs = [{"source": {"benchmark": "run-bench-16"}}, {"source": {"benchmark": "run-bench-17"}}, {}]
        ok = [rec(0, 0, False, True), rec(0, 1, True, True), rec(1, 0, True, False), rec(2, 0, False, False)]
        self.assertEqual(cc.by_origin(ok, specs, "x", "y"), {"run-bench-16": [2, 1, 2], "run-bench-17": [1, 1, 0], "?": [1, 0, 0]})

    def test_bootstrap_of_nothing(self):
        self.assertIsNone(cc.bootstrap([]))
        m, lo, hi = cc.bootstrap([2.0, 2.0, 2.0])
        self.assertEqual((m, lo, hi), (2.0, 2.0, 2.0))

    def test_folders_pooled_as_one_set(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for name, sample, won in (("a", 0, True), ("b", 1, False)):
                (Path(d) / name).mkdir()
                (Path(d) / name / "shard-00.jsonl").write_text(json.dumps(rec(0, sample, False, won)) + "\n")
            recs = cc.pooled([Path(d) / "a", Path(d) / "b"])
            ok, _ = cc.pairs(recs, "x", "y")
            self.assertEqual(cc.by_situation(ok, "x", "y"), {0: (0.0, 0.5)})        # one situation, two sample seeds
            with self.assertRaises(ValueError):
                cc.pooled([Path(d) / "a", Path(d) / "a"])                        # the same fights twice


if __name__ == "__main__":
    unittest.main()
