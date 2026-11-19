"""Runs the smoke checks on every saved live state (tools/tests/fixtures/live/*.json). Skips until Phase 0 saves some."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import smoke  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "live"


class TestLiveFixtures(unittest.TestCase):
    def test_fixtures(self):
        files = sorted(FIX.glob("*.json")) if FIX.exists() else []
        if not files:
            self.skipTest("no live fixtures yet (run tools/smoke.py --save in Phase 0)")
        for f in files:
            with self.subTest(fixture=f.name):
                scr, issues, notes = smoke.check_state(json.loads(f.read_text()))
                self.assertEqual(issues, [], f"{f.name}: {issues}")


if __name__ == "__main__":
    unittest.main()
