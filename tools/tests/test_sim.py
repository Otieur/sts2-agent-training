"""Offline tests for the pure parts of tools/sim.py (the host itself needs the game and the .NET SDK: tools/sim.py
smoke, fidelity and fairplay are its tests)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import plan_turn as pt  # noqa: E402
import sim  # noqa: E402


def obs(hand, enemies, energy=3, choice=None):
    return {"screen": "COMBAT", "status": "in_progress", "turn": 1, "waiting_for_choice": bool(choice), "blocked": False, "choice": choice,
            "run": {"ascension": 0, "relics": [], "potions": []},
            "combat": {"player": {"current_hp": 60, "max_hp": 80, "block": 0, "energy": energy, "powers": []},
                       "hand": [{"index": i, "card_id": c, "upgraded": False, "target_type": "AnyEnemy", "energy_cost": cost, "playable": True,
                                 "dynamic_values": [{"name": k, "current_value": v} for k, v in vals.items()]} for i, (c, cost, vals) in enumerate(hand)],
                       "enemies": enemies, "draw_pile_count": 5, "discard_pile_count": 0, "exhaust_pile_count": 0}}


ENEMY = {"index": 0, "enemy_id": "LOUSE", "name": "LOUSE", "current_hp": 10, "max_hp": 10, "block": 0, "is_alive": True, "is_hittable": True,
         "powers": [], "intents": [{"intent_type": "Attack", "damage": 5, "hits": 1, "total_damage": 5}]}


class TestSimBridge(unittest.TestCase):
    def test_planner_action_from_a_simulated_observation(self):
        o = obs([("DEFEND_IRONCLAD", 1, {"Block": 5}), ("STRIKE_IRONCLAD", 1, {"Damage": 6}), ("STRIKE_IRONCLAD", 1, {"Damage": 6})], [dict(ENEMY)])
        act = sim.planner_action(pt, o, "safe")
        self.assertEqual(act, {"type": "play", "card": 1, "target": 0})      # lethal with two Strikes: attack first
        self.assertEqual(sim.planner_action(pt, obs([], [dict(ENEMY)]), "safe"), {"type": "end_turn"})

    def test_choice_is_answered_before_anything_else(self):
        o = obs([("STRIKE_IRONCLAD", 1, {"Damage": 6})], [dict(ENEMY)], choice={"kind": "FromCombatPile", "min": 1, "max": 1, "options": ["BASH", "DEFEND_IRONCLAD"]})
        self.assertEqual(sim.planner_action(pt, o, "safe"), {"type": "choose", "cards": [0]})

    def test_search_value_and_action_matching(self):
        won = {"status": "won", "combat": {"player": {"current_hp": 40}, "enemies": []}}
        lost = {"status": "lost", "combat": {"player": {"current_hp": 0}, "enemies": [{"current_hp": 12}, {"current_hp": 0}]}}
        self.assertEqual(sim._value(won), 40)
        self.assertEqual(sim._value(lost), -112)        # closer losses score higher; dead enemies do not count
        self.assertTrue(sim._same_action({"type": "play", "card": 1, "target": 0}, {"type": "play", "card": 1, "target": 0, "card_id": "X"}))
        self.assertFalse(sim._same_action({"type": "play", "card": 1, "target": 0}, {"type": "play", "card": 1, "target": 1}))

    def test_greedy_baseline_maps_targets_by_combat_index(self):
        class FakeSim:
            def legal(self):
                return [{"type": "play", "card": 0, "target": 3}, {"type": "end_turn"}]
        dead_first = [dict(ENEMY, index=2, current_hp=0, is_alive=False), dict(ENEMY, index=3)]
        o = obs([("STRIKE_IRONCLAD", 1, {"Damage": 6})], dead_first)
        self.assertEqual(sim.baseline_action(FakeSim(), pt, o, "greedy", None), {"type": "play", "card": 0, "target": 3})

    def test_brief(self):
        text = sim.brief(obs([("STRIKE_IRONCLAD", 1, {"Damage": 6})], [dict(ENEMY)]))
        self.assertIn("STRIKE_IRONCLAD(1)", text)
        self.assertIn("LOUSE 10/10 [Attack 5x1]", text)


if __name__ == "__main__":
    unittest.main()
