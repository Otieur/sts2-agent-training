"""Offline tests for tools/plan_turn.py (base values from the extract)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import plan_turn as pt  # noqa: E402


def hand(*names):
    return [pt.card_from_extract(i, pt.resolve_card(n)) for i, n in enumerate(names)]


def best(h, player, enemies, mode="safe"):
    return pt.rank(pt.plans(h, player, enemies), mode)[0]


class TestPlanTurn(unittest.TestCase):
    def test_parse(self):
        bash = hand("Bash")[0]
        self.assertEqual((bash.dmg, bash.vuln, bash.cost, bash.target), (8, 2, 2, "AnyEnemy"))
        tw = hand("Twin Strike")[0]
        self.assertEqual((tw.dmg, tw.hits), (5, 2))
        off = hand("Offering")[0]
        self.assertEqual((off.energy, off.draw, off.hp_cost), (2, 3, 6))
        e = pt.parse_enemy("Vantom:173:0:7:slippery=9", 0)
        self.assertEqual((e.hp, e.intent_per_hit, e.intent_hits, e.slippery), (173, 7, 1, 9))
        e = pt.parse_enemy("Louse:12:3:5x2:weak", 1)
        self.assertEqual((e.block, e.intent_per_hit, e.intent_hits, e.weak), (3, 5, 2, True))

    def test_vulnerable_ordering(self):
        o = best(hand("Bash", "Strike"), pt.Player(energy=3), [pt.parse_enemy("Worm:40:0:11", 0)], "balanced")
        self.assertEqual(o["dealt"], 17)  # 8, then Strike 6 x 1.5 = 9
        self.assertEqual(o["plays"][0].split(" →")[0], "Bash")

    def test_lethal_first(self):
        o = best(hand("Strike", "Strike", "Defend"), pt.Player(energy=3), [pt.parse_enemy("Louse:12:0:20", 0)])
        self.assertTrue(o["all_dead"])
        self.assertEqual(o["hp_lost"], 0)

    def test_kill_removes_intent_and_focus(self):
        enemies = [pt.parse_enemy("A:10:0:6", 0), pt.parse_enemy("B:12:3:5x2", 1)]
        o = best(hand("Twin Strike", "Strike", "Defend"), pt.Player(energy=3), enemies)
        self.assertEqual(o["enemy_hp"][1], 0)
        self.assertEqual(o["hp_lost"], 1)  # A's 6 against 5 block

    def test_weak_reduces_intent(self):
        o = pt.simulate(hand("Uppercut"), [0], pt.Player(energy=3), [pt.parse_enemy("A:50:0:12", 0)])
        self.assertEqual(o["incoming"], 9)  # 12 x 0.75
        self.assertEqual(o["dealt"], 13)    # own Vulnerable lands after the hit

    def test_slippery(self):
        o = pt.simulate(hand("Twin Strike", "Strike"), [0, 0], pt.Player(energy=3),
                        [pt.parse_enemy("Vantom:173:0:7:slippery=9", 0)])
        self.assertEqual(o["dealt"], 3)
        o = pt.simulate(hand("Strike"), [0], pt.Player(energy=3), [pt.parse_enemy("Vantom:173:0:7:slippery=1", 0)])
        self.assertEqual(o["dealt"], 1)

    def test_strength_and_energy(self):
        o = pt.simulate(hand("Inflame", "Twin Strike"), [None, 0], pt.Player(energy=2), [pt.parse_enemy("A:50:0:0", 0)])
        self.assertEqual(o["dealt"], 14)  # (5 + 2) x 2
        o = pt.simulate(hand("Bloodletting", "Bash", "Bash"), [None, 0, 0], pt.Player(energy=3), [pt.parse_enemy("A:80:0:0", 0)])
        self.assertIsNotNone(o)
        self.assertEqual(o["hp_lost"], 3)
        self.assertIsNone(pt.simulate(hand("Bash", "Bash"), [0, 0], pt.Player(energy=3), [pt.parse_enemy("A:80:0:0", 0)]))

    def test_live_values_from_state(self):
        st = {"data": {"combat": {
            "player": {"current_hp": 50, "energy": 3, "block": 0, "powers": [{"power_id": "STRENGTH_POWER", "amount": 2}]},
            "hand": [{"index": 0, "card_id": "STRIKE_IRONCLAD", "energy_cost": 1, "playable": True,
                      "dynamic_values": [{"name": "Damage", "current_value": 8}]},
                     {"index": 1, "card_id": "DEFEND_IRONCLAD", "energy_cost": 1, "playable": True,
                      "dynamic_values": [{"name": "Block", "current_value": 5}]}],
            "enemies": [{"index": 0, "name": "Cultist", "current_hp": 50, "block": 0, "is_alive": True,
                         "powers": [{"power_id": "VULNERABLE_POWER", "amount": 1}],
                         "intents": [{"intent_type": "Attack", "damage": 6, "hits": 1, "total_damage": 6}]}]}}}
        h, player, enemies = pt.from_state(st)
        self.assertEqual(player.strength, 2)
        self.assertTrue(enemies[0].vuln)
        o = pt.simulate(h[:1], [0], player, enemies)
        self.assertEqual(o["dealt"], 12)  # live 8 already has Strength; x1.5 Vulnerable

    def test_hit_all_and_x_cost(self):
        enemies = [pt.parse_enemy("A:30:0:0", 0), pt.parse_enemy("B:30:0:0", 1)]
        o = pt.simulate(hand("Whirlwind"), [None], pt.Player(energy=3), enemies)
        self.assertEqual(o["dealt"], 30)  # 5 x 3 hits x 2 enemies
        self.assertEqual(o["energy_left"], 0)

    def test_potions(self):
        enemies = [pt.parse_enemy("Byrdonis:30:0:18", 0)]
        h = hand("Strike", "Strike", "Defend") + [pt.card_from_potion(0, "FIRE_POTION")]
        o = best(h, pt.Player(energy=3), enemies)
        self.assertTrue(o["all_dead"])
        self.assertEqual(o["potions"], 1)
        # not needed for lethal -> lethal without the potion ranks first
        h = hand("Bash", "Strike") + [pt.card_from_potion(0, "FIRE_POTION")]
        o = best(h, pt.Player(energy=3), [pt.parse_enemy("Louse:15:0:5", 0)])
        self.assertTrue(o["all_dead"])
        self.assertEqual(o["potions"], 0)
        # flat damage ignores Vulnerable and Strength, but Slippery still caps it
        o = pt.simulate([pt.card_from_potion(0, "FIRE_POTION")], [0], pt.Player(energy=3, strength=3),
                        [pt.parse_enemy("A:50:0:0:vuln", 0)])
        self.assertEqual(o["dealt"], 20)
        o = pt.simulate([pt.card_from_potion(0, "FIRE_POTION")], [0], pt.Player(energy=3), [pt.parse_enemy("V:173:0:7:slippery=9", 0)])
        self.assertEqual(o["dealt"], 1)
        # Dexterity potion raises later block cards
        o = pt.simulate([pt.card_from_potion(0, "DEXTERITY_POTION")] + hand("Defend"), [None, None], pt.Player(energy=3),
                        [pt.parse_enemy("A:50:0:10", 0)])
        self.assertEqual(o["block"], 7)
        self.assertFalse(pt.card_from_potion(0, "MYSTERY_POTION").playable)

    def test_potions_from_state(self):
        st = {"data": {"combat": {"player": {"current_hp": 30, "energy": 1, "block": 0, "powers": []},
                                  "hand": [{"index": 0, "card_id": "STRIKE_IRONCLAD", "energy_cost": 1, "playable": True}],
                                  "enemies": [{"index": 0, "name": "A", "current_hp": 25, "block": 0, "is_alive": True,
                                               "powers": [], "intents": [{"damage": 10, "hits": 1}]}]},
                       "run": {"potions": [{"index": 0, "potion_id": "FIRE_POTION", "occupied": True},
                                           {"index": 1, "potion_id": None, "occupied": False}]}}}
        h, player, enemies = pt.from_state(st)
        self.assertEqual([c.potion for c in h], [False, True])
        o = best(h, player, enemies)
        self.assertTrue(o["all_dead"])


if __name__ == "__main__":
    unittest.main()
