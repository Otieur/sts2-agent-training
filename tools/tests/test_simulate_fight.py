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

    def test_curse_offers_and_stacking(self):
        b = {}
        kinds = [sf.demon_move(b, t)["kind"] for t in range(1, 17)]
        self.assertEqual([i + 1 for i, k in enumerate(kinds) if k == "curse"], [1, 5, 9])  # three offers, then no more
        self.assertEqual([sf.demon_move(b, t)["dmg"] for t in (13, 14, 15, 16)], [17, 8, 11, 17])  # three-move loop
        deck = expand_deck(["STRIKE_IRONCLAD:5", "DEFEND_IRONCLAD:5"], "IRONCLAD")
        # Disintegration twice: 6 then 6 + 7 at the end of each turn, so the fight is shorter and costlier than Mind Rot + Sloth
        dd = sf.evaluate(deck, "KNOWLEDGE_DEMON", 80, 80, 10, "safe", ("DISINTEGRATION", "DISINTEGRATION", "WASTE_AWAY"))
        ms = sf.evaluate(deck, "KNOWLEDGE_DEMON", 80, 80, 10, "safe", ("MIND_ROT", "SLOTH", "WASTE_AWAY"))
        self.assertLessEqual(dd["turns"], ms["turns"])

    def test_relics_and_upgrades_help(self):
        deck = expand_deck(sf.EXPERIMENT_BASE, "IRONCLAD")
        plain = sf.evaluate(deck, "VANTOM", 60, 80, 20, "balanced")
        relic = sf.evaluate(deck, "VANTOM", 60, 80, 20, "balanced", relics=("RELIC.VAJRA", "ANCHOR", "LIZARD_TAIL"))
        upgraded = sf.evaluate([c + "+" for c in deck], "VANTOM", 60, 80, 20, "balanced")
        self.assertGreaterEqual(relic["win_rate"], plain["win_rate"])
        self.assertGreater(upgraded["win_rate"], plain["win_rate"])

    def test_potions(self):
        deck = expand_deck(sf.EXPERIMENT_BASE, "IRONCLAD")
        plain = sf.evaluate(deck, "VANTOM", 60, 80, 20, "balanced")
        pots = sf.evaluate(deck, "VANTOM", 60, 80, 20, "balanced", potions=("POTION.STRENGTH_POTION", "WEAK_POTION", "BLOOD_POTION"))
        self.assertGreater(pots["win_rate"], plain["win_rate"])
        from stslib import connect
        con = connect()
        rid = con.execute("SELECT run_id FROM potion_events WHERE kind = 'used' LIMIT 1").fetchone()["run_id"]
        held = sf.potions_at(con, rid, 999)
        con.close()
        self.assertIsInstance(held, list)

    def test_boss_with_adds(self):
        self.assertEqual([sf.kin_follower_move({}, t)["kind"] for t in (1, 2, 3, 4)], ["attack", "attack", "buff", "attack"])
        deck = expand_deck(sf.EXPERIMENT_BASE + ["THUNDERCLAP"], "IRONCLAD")
        for focus in (False, True):
            r = sf.run_fight(deck, "THE_KIN", 80, 80, seed=4, focus_boss=focus)
            self.assertTrue(r["won"] or r["hp"] == 0 or r.get("timeout"))
        # a win can come with followers alive: they are Minions and the Priest's death ends the fight
        wins = [sf.run_fight(deck, "THE_KIN", 80, 80, seed=s, focus_boss=True) for s in range(8)]
        self.assertTrue(any(w["won"] for w in wins))

    def test_soul_fysh_cycle_and_beckon(self):
        b = {}
        moves = [sf.fysh_move(b, t) for t in range(1, 11)]
        self.assertEqual([m["kind"] for m in moves[:5]], ["status", "attack", "attack", "buff", "attack"])
        self.assertEqual((moves[0]["status"], moves[0]["status_draw"]), (1, 1))
        self.assertEqual((moves[3]["intangible"], moves[4]["p_vuln"], moves[4]["dmg"]), (1, 3, 13))
        self.assertEqual(moves[5], moves[0])
        r = sf.run_fight(expand_deck(sf.EXPERIMENT_BASE, "IRONCLAD"), "SOUL_FYSH", 60, 80, seed=2)
        self.assertTrue(r["won"] or r["hp"] == 0 or r.get("timeout"))

    def test_waterfall_giant_explosion(self):
        b = {}
        self.assertEqual(sf.giant_move(b, 1)["steam"], 15)
        self.assertEqual([sf.giant_move(b, t)["dmg"] for t in range(2, 13)], [15, 10, 0, 20, 13, 15, 10, 0, 25, 13, 15])
        b["exploding"], b["steam"] = 2, 42
        self.assertEqual(sf.giant_move(b, 9)["dmg"], 42)
        # a win needs surviving the explosion: every recorded win ends after a stun turn and the explosion turn
        deck = expand_deck(sf.EXPERIMENT_BASE, "IRONCLAD")
        rs = [sf.run_fight(deck, "WATERFALL_GIANT", 80, 80, seed=s, mode="safe") for s in range(6)]
        self.assertTrue(all(r["won"] or r["hp"] == 0 for r in rs))
        self.assertTrue(all(r["turns"] >= 3 for r in rs))


if __name__ == "__main__":
    unittest.main()
