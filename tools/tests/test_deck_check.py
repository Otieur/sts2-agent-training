"""Tests for tools/deck_check.py."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import deck_check  # noqa: E402
import draft  # noqa: E402


def deck(*items):
    return draft.expand_deck(list(items), "IRONCLAD")


class TestDeckCheck(unittest.TestCase):
    def test_vantom(self):
        out = deck_check.check(deck("STRIKE_IRONCLAD:4", "DEFEND_IRONCLAD:4", "BASH", "TWIN_STRIKE", "BREAKTHROUGH", "THUNDERCLAP"), 1, "VANTOM_BOSS")
        self.assertIn("GAP  single-hit hit-all attacks: 2", out)
        self.assertIn("OK   cheap (0-1 cost) or multi-hit attack cards", out)

    def test_targets_and_knowledge_demon(self):
        out = deck_check.check(deck("STRIKE_IRONCLAD:5", "DEFEND_IRONCLAD:4", "BASH", "DEMON_FORM"), 2, "KNOWLEDGE_DEMON_BOSS")
        self.assertIn("GAP  scaling 1", out)
        self.assertIn("GAP  scaling cards (powers, Strength, energy): 1", out)

    def test_unknown_boss(self):
        out = deck_check.check(deck("STRIKE_IRONCLAD:5"), 3, "MYSTERY_BOSS")
        self.assertIn("No countable checklist", out)
        self.assertIn("block", out)


if __name__ == "__main__":
    unittest.main()
