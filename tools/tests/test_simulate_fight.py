"""Tests for tools/simulate_fight.py (small, deterministic runs)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import simulate_fight as sf  # noqa: E402
from draft import expand_deck  # noqa: E402


class TestSimulateFight(unittest.TestCase):
    def test_deterministic_and_bounded(self):
        deck = expand_deck(sf.EXPERIMENT_BASE, "IRONCLAD")
        a = sf.run_fight(deck, seed=3)
        b = sf.run_fight(deck, seed=3)
        self.assertEqual(a, b)
        self.assertTrue(a["won"] or a["hp"] == 0 or a.get("timeout"))
        self.assertLessEqual(a["turns"], 25)

    def test_multi_hit_beats_breakthrough_against_vantom(self):
        base = sf.EXPERIMENT_BASE
        multi = sf.evaluate(expand_deck(base + ["TWIN_STRIKE", "SWORD_BOOMERANG"], "IRONCLAD"), "VANTOM", 80, 80, 40)
        brk = sf.evaluate(expand_deck(base + ["BREAKTHROUGH:2"], "IRONCLAD"), "VANTOM", 80, 80, 40)
        self.assertGreater(multi["win_rate"], brk["win_rate"])

    def test_draw_cards_helper(self):
        import random
        draw, discard = [], ["A", "B"]
        out = sf.draw_cards(3, draw, discard, random.Random(0))
        self.assertEqual(sorted(out), ["A", "B"])  # reshuffles the discard, stops when empty

    def test_knowledge_demon_curses(self):
        deck = expand_deck(["STRIKE_IRONCLAD:2", "DEFEND_IRONCLAD:3", "BASH", "POMMEL_STRIKE", "SHRUG_IT_OFF:2", "UPPERCUT", "ANGER",
                            "INFLAME:2", "TWIN_STRIKE:2", "FLAME_BARRIER", "BATTLE_TRANCE", "BLUDGEON", "DEMON_FORM",
                            "SWORD_BOOMERANG", "IMPERVIOUS", "OFFERING"], "IRONCLAD")
        sloth = sf.evaluate(deck, "KNOWLEDGE_DEMON", 80, 80, 20, "safe", "SLOTH")
        disint = sf.evaluate(deck, "KNOWLEDGE_DEMON", 80, 80, 20, "safe", "DISINTEGRATION")
        self.assertGreaterEqual(sloth["win_rate"], disint["win_rate"])
        self.assertLess(disint["hp_lost"] - 1e-9, 80.0 + 1e-9)


if __name__ == "__main__":
    unittest.main()
