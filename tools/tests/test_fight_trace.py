"""Offline tests for the planner's view in tools/fight_trace.py (playing a fight needs the simulator host)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fight_trace as FT  # noqa: E402
from test_sim import ENEMY, obs  # noqa: E402

BIG = dict(ENEMY, current_hp=100, max_hp=100)
STRIKE, DEFEND, ANGER = ("STRIKE_IRONCLAD", 1, {"Damage": 6}), ("DEFEND_IRONCLAD", 1, {"Block": 5}), ("ANGER", 0, {"Damage": 6})


class TestPlannerView(unittest.TestCase):
    def test_a_free_attack_with_no_energy_is_played_and_ending_ranks_behind_it(self):
        v = FT.planner_view(obs([DEFEND, STRIKE, ANGER], [dict(BIG)], energy=0), "balanced", "Boss")
        self.assertEqual(v["action"], {"type": "play", "card": 2, "target": 0})
        self.assertEqual((v["plans"], v["end_rank"]), (2, 1))
        self.assertEqual(len(v["best_play"]["plays"]), 1)
        self.assertEqual((v["best_play"]["dealt"], v["end"]["dealt"], v["end"]["plays"]), (6, 0, []))
        self.assertEqual([c[:2] for c in v["cards"]], [[0, "DEFEND_IRONCLAD"], [1, "STRIKE_IRONCLAD"], [2, "ANGER"]])

    def test_nothing_to_play(self):
        v = FT.planner_view(obs([], [dict(BIG)]), "balanced", "Boss")
        self.assertEqual((v["action"], v["plans"], v["top"], v["best_play"], v["end_rank"]), ({"type": "end_turn"}, 0, None, None, None))
        v = FT.planner_view(obs([STRIKE], [dict(BIG)], energy=0), "balanced", "Boss")       # a card the energy does not pay for
        self.assertEqual((v["action"], v["end_rank"], v["best_play"]), ({"type": "end_turn"}, 0, None))

    def test_no_view_at_a_card_choice(self):
        o = obs([STRIKE], [dict(BIG)], choice={"kind": "FromCombatPile", "min": 1, "max": 1, "options": ["BASH", "DEFEND_IRONCLAD"]})
        self.assertIsNone(FT.planner_view(o, "balanced", "Boss"))

    def test_a_card_the_host_cannot_simulate_is_named_and_left_out(self):
        v = FT.planner_view(obs([STRIKE, ("BODYGUARD", 1, {})], [dict(BIG)]), "balanced", "Boss")
        self.assertEqual(v["unsimulated"], ["BODYGUARD"])
        self.assertEqual([c[1] for c in v["cards"]], ["STRIKE_IRONCLAD"])

    def test_same_action(self):
        hand = [{"card_id": "STRIKE_IRONCLAD", "upgraded": False}, {"card_id": "STRIKE_IRONCLAD", "upgraded": False}, {"card_id": "STRIKE_IRONCLAD", "upgraded": True}]
        play = lambda i, t=0: {"type": "play", "card": i, "target": t}  # noqa: E731
        self.assertTrue(FT.same_action({"type": "end_turn"}, {"type": "end_turn"}, hand))
        self.assertTrue(FT.same_action(play(0), play(1), hand))             # a second copy of the card
        self.assertFalse(FT.same_action(play(0), play(2), hand))            # the upgraded copy is another card
        self.assertFalse(FT.same_action(play(0), play(0, 1), hand))         # another target
        self.assertFalse(FT.same_action(play(0), {"type": "end_turn"}, hand))
        self.assertTrue(FT.same_action({"type": "potion", "slot": 1, "target": 0}, {"type": "potion", "slot": 1, "target": 0}, hand))
        self.assertFalse(FT.same_action({"type": "potion", "slot": 1}, {"type": "potion", "slot": 0}, hand))

    def test_plan_line(self):
        v = FT.planner_view(obs([ANGER], [dict(BIG)], energy=0), "balanced", "Boss")
        self.assertIn("dealt 6", FT.plan_line(v["best_play"]))
        self.assertTrue(FT.plan_line(v["end"]).startswith("no card: dealt 0"))


if __name__ == "__main__":
    unittest.main()
