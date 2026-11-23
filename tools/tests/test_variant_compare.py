"""Offline tests for tools/variant_compare.py."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import variant_compare as vc  # noqa: E402


def rec(fight, sample, won, hp=None, arm="x"):
    return {"fight": fight, "sample": sample, "arms": {arm: {"status": "won" if won else "lost", "hp": (30 if hp is None else hp) if won else 0}}}


class TestVariantCompare(unittest.TestCase):
    def test_fights_are_paired_by_situation_and_sample_seed(self):
        base = [rec(0, 0, False), rec(0, 1, False), rec(1, 0, True), rec(1, 1, False), rec(2, 0, True),
                {"fight": 3, "sample": 0, "arms": {"x": {"error": "host"}}}]
        variant = [rec(0, 0, True), rec(0, 1, False), rec(1, 0, True, 50), rec(1, 1, False), rec(2, 0, False), rec(3, 0, True), rec(4, 0, True)]
        ok, left_out = vc.paired(base, variant, "x")
        self.assertEqual((sorted(ok), left_out), ([(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)], 2))      # an error and a fight played once: out
        self.assertEqual(vc.shares(ok), {0: (0.0, 0.5, 2), 1: (0.5, 0.5, 2), 2: (1.0, 0.0, 1)})

    def test_the_sign_test_and_thirds(self):
        self.assertEqual(vc.sign_test(3, 0), 0.125)
        self.assertEqual(vc.sign_test(0, 0), 1.0)
        self.assertEqual(vc.thirds({"a": 0.4, "b": 0.9, "c": 0.5, "d": 0.6, "e": 1.0, "f": 0.45}), {"a": 0, "f": 0, "c": 1, "d": 1, "b": 2, "e": 2})
        self.assertEqual(vc.thirds({"a": 0.4, "b": 0.9, "c": 0.5, "d": 0.6}), {"a": 0, "c": 0, "d": 1, "b": 2})

    def test_the_report_runs_on_folders(self):
        import contextlib
        import io
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            specs = [{"encounter": "E", "hp": 40, "max_hp": 80}, {"encounter": "E", "hp": 80, "max_hp": 80}]
            full = [dict(s, hp=s["max_hp"]) for s in specs]
            (d / "specs.json").write_text(json.dumps({"fights": specs}))
            (d / "full.json").write_text(json.dumps({"fights": full}))
            for name, recs in (("base", [rec(0, 0, False, arm="mcw6paf"), rec(1, 0, True, arm="mcw6paf")]),
                               ("variant", [rec(0, 0, True, arm="mcw6paf"), rec(1, 0, True, arm="mcw6paf")])):
                (d / name).mkdir()
                (d / name / "shard-00.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = vc.report(d / "base", d / "variant", d / "specs.json", d / "full.json", "mcw6paf")
            text = out.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("fights won: base 1 of 2 (50.0%), variant 2 of 2 (100.0%)", text)
            self.assertIn("situations whose HP the variant changes: 1 situations; base 0 and variant 1 of 1 fights; larger share in 1, smaller in 0", text)
            self.assertIn("fights of situations the variant does not change: 1; the same outcome and HP left in 1", text)
            self.assertIn("HP added where changed: mean 40.0, from 40 to 40", text)


if __name__ == "__main__":
    unittest.main()
