"""Test for tools/replay_run.py on one of the Player's runs (reads data/runs.db)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import replay_run  # noqa: E402


class TestReplay(unittest.TestCase):
    def test_replay_example_run(self):
        run, rows, death = replay_run.replay("GK21D6LA3U")
        self.assertEqual(run["character"], "IRONCLAD")
        kinds = {r[1] for r in rows}
        self.assertTrue({"card reward", "rest site", "Ancient"} <= kinds)
        self.assertEqual(death["floor"], 17)
        self.assertTrue(all(r[5] in ("same", "**differs**", "no conflict") for r in rows))


if __name__ == "__main__":
    unittest.main()
