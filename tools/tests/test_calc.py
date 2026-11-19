"""Tests for tools/calc.py. Expected values encode the rules in knowledge/mechanics.md; cases marked
UNVERIFIED depend on order and rounding conventions still to be checked in a v0.107.1 fight."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from calc import attack, block_gain, hit_damage, incoming_hp_loss, strip_slippery  # noqa: E402


class TestDamage(unittest.TestCase):
    def test_plain_strike(self):
        self.assertEqual(hit_damage(6), 6)

    def test_vulnerable_checklist_1(self):
        self.assertEqual(hit_damage(6, target_vulnerable=True), 9)

    def test_odd_rounding_checklist_2_unverified(self):
        self.assertEqual(attack(5, hits=2, target_vulnerable=True).per_hit, [7, 7])

    def test_strength_before_multiplier_checklist_4_unverified(self):
        self.assertEqual(hit_damage(6, strength=2, target_vulnerable=True), 12)

    def test_weak_attacker(self):
        self.assertEqual(hit_damage(10, attacker_weak=True), 7)

    def test_weak_and_vulnerable(self):
        self.assertEqual(hit_damage(10, attacker_weak=True, target_vulnerable=True), 11)  # floor(11.25)

    def test_negative_strength_floors_at_zero(self):
        self.assertEqual(hit_damage(3, strength=-5), 0)

    def test_vigor_first_hit_only(self):
        self.assertEqual(attack(4, hits=2, vigor=7).per_hit, [11, 4])

    def test_cap_slippery(self):
        self.assertEqual(attack(32, cap=1).total, 1)

    def test_block_absorbs_first_checklist_7(self):
        r = attack(10, target_block=6)
        self.assertEqual((r.hp_lost, r.block_left), (4, 0))

    def test_multi_hit_through_block(self):
        r = attack(5, hits=3, target_block=7)
        self.assertEqual((r.hp_lost, r.block_left), (8, 0))


class TestBlock(unittest.TestCase):
    def test_frail_checklist_5(self):
        self.assertEqual(block_gain(5, frail=True), 3)

    def test_dexterity(self):
        self.assertEqual(block_gain(5, dexterity=2), 7)

    def test_unmovable_doubles(self):
        self.assertEqual(block_gain(8, unmovable=True), 16)


class TestIncoming(unittest.TestCase):
    def test_dismember_with_weak(self):
        r = incoming_hp_loss([(27, 1)], player_block=0, weak_enemies=[True])
        self.assertEqual(r.total, 20)

    def test_entomancer_bees_against_block(self):
        r = incoming_hp_loss([(3, 7)], player_block=12)
        self.assertEqual((r.total, r.hp_lost), (21, 9))


class TestSlippery(unittest.TestCase):
    def test_starter_strikes_do_not_clear_nine(self):
        r = strip_slippery(9, [1, 1, 1, 1, 1, 1])
        self.assertEqual((r["stacks_left"], r["cleared"]), (3, False))

    def test_multi_hit_clears(self):
        r = strip_slippery(9, [2, 3, 1, 1, 2])
        self.assertTrue(r["cleared"])
        self.assertEqual(r["cards_played"], 5)


if __name__ == "__main__":
    unittest.main()
