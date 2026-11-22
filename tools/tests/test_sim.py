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

    def test_loss_value_counts_the_forms_to_come_and_can_leave_minions_out(self):
        def lost(*enemies):
            return {"status": "lost", "combat": {"player": {"current_hp": 0}, "enemies": list(enemies)}}
        ts = lambda hp, mx: {"enemy_id": "TEST_SUBJECT", "current_hp": hp, "max_hp": mx}
        was = sim.LOSS_COUNTS_FORMS, sim.LOSS_SKIPS_MINIONS
        try:
            sim.LOSS_COUNTS_FORMS, sim.LOSS_SKIPS_MINIONS = True, False
            # dying later is never valued below dying earlier, across the three forms (100, 200, 300 HP)
            values = [sim._value(lost(ts(hp, mx))) for hp, mx in ((100, 100), (30, 100), (0, 100), (200, 200), (10, 200), (300, 300), (5, 300))]
            self.assertEqual(values, [-700, -630, -600, -600, -410, -400, -105])
            self.assertEqual(values, sorted(values))
            self.assertEqual(sim._value(lost(ts(50, 111))), -100 - 50 - 212 - 313)        # the forms at Ascension 8 and above
            self.assertEqual(sim._value(lost({"enemy_id": "QUEEN", "current_hp": 300, "max_hp": 400})), -400)     # no forms: unchanged
            self.assertEqual(sim._value(lost({"current_hp": 12}, {"current_hp": 0})), -112)
            sim.LOSS_COUNTS_FORMS = False
            self.assertEqual(sim._value(lost(ts(30, 100))), -130)                         # the form alive only
            minion = {"enemy_id": "TORCH_HEAD_AMALGAM", "current_hp": 150, "max_hp": 199, "powers": [{"power_id": "MINION_POWER", "amount": 1}]}
            queen = {"enemy_id": "QUEEN", "current_hp": 300, "max_hp": 400, "powers": []}
            self.assertEqual(sim._value(lost(queen, minion)), -550)
            sim.LOSS_SKIPS_MINIONS = True
            self.assertEqual(sim._value(lost(queen, minion)), -400)                       # the minion is not between the player and the win
            self.assertEqual(sim._value(lost(minion)), -250)                              # alone it counts
        finally:
            sim.LOSS_COUNTS_FORMS, sim.LOSS_SKIPS_MINIONS = was

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
