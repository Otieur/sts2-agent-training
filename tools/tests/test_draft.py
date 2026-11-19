"""Offline tests for tools/draft.py (uses the extracted card data and the committed tier files)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import draft  # noqa: E402

STARTER = draft.expand_deck(["STRIKE_IRONCLAD:5", "DEFEND_IRONCLAD:4", "BASH"], "IRONCLAD")


def offer(*names):
    return ["CARD." + draft.resolve(n, "IRONCLAD")["id"] for n in names]


class TestDraft(unittest.TestCase):
    def test_resolve_and_expand(self):
        self.assertEqual(len(STARTER), 10)
        self.assertEqual(draft.resolve("shrug it off")["id"], "SHRUG_IT_OFF")
        self.assertEqual(draft.resolve("CARD.TWIN_STRIKE")["id"], "TWIN_STRIKE")
        self.assertEqual(draft.resolve("Strike", "IRONCLAD")["id"], "STRIKE_IRONCLAD")
        self.assertEqual(draft.expand_deck(["BASH*2"], "IRONCLAD"), ["CARD.BASH", "CARD.BASH"])
        with self.assertRaises(SystemExit):
            draft.expand_deck(["NOT_A_CARD"], "IRONCLAD")

    def test_simulation_skips_unmodelled_cards(self):
        saved = draft.simulated_boss_value
        draft.simulated_boss_value = lambda *a, **k: (0.1, {"CARD.HELLRAISER": -0.5, "CARD.TWIN_STRIKE": 0.05})
        try:
            deck = draft.expand_deck(["STRIKE_IRONCLAD:5", "DEFEND_IRONCLAD:4", "BASH"], "IRONCLAD")
            res = draft.score_offer(deck, ["CARD.HELLRAISER", "CARD.TWIN_STRIKE"], "IRONCLAD", 1, 5, "VANTOM_BOSS", simulate=True)
        finally:
            draft.simulated_boss_value = saved
        why = {r["id"]: " ".join(r["reasons"]) for r in res["rows"]}
        self.assertIn("simulation skipped", why["HELLRAISER"])   # an unmodelled Power is not marked down as a dead card
        self.assertIn("+0.5)", why["TWIN_STRIKE"])

    def test_vantom_fit(self):
        res = draft.score_offer(STARTER, offer("Twin Strike", "Breakthrough"), "IRONCLAD", 1, 3, "VANTOM_BOSS")
        rows = {r["id"]: r for r in res["rows"]}
        self.assertTrue(any("Slippery" in x for x in rows["TWIN_STRIKE"]["reasons"]))
        self.assertTrue(any("wasted" in x for x in rows["BREAKTHROUGH"]["reasons"]))
        self.assertGreater(rows["TWIN_STRIKE"]["score"], rows["BREAKTHROUGH"]["score"])

    def test_scaling_need_and_skip_bar(self):
        res = draft.score_offer(STARTER, offer("Demon Form"), "IRONCLAD", 1, 12, None)
        self.assertTrue(any("scaling 0 below" in x for x in res["rows"][0]["reasons"]))
        self.assertEqual(res["pick"]["id"], "DEMON_FORM")
        self.assertAlmostEqual(draft.skip_bar(25), 3.0)
        self.assertAlmostEqual(draft.skip_bar(10), 2.0)

    def test_skip_when_nothing_clears_the_bar(self):
        big = STARTER + draft.expand_deck(["IRON_WAVE:10", "ANGER:5"], "IRONCLAD")  # 25 cards, bar 3.0
        res = draft.score_offer(big, offer("Breakthrough"), "IRONCLAD", 2, 20, "KAISER_CRAB_BOSS")
        self.assertIsNone(res["pick"])

    def test_v0111_and_rework(self):
        res = draft.score_offer(STARTER, offer("Mangle", "Expect a Fight"), "IRONCLAD", 2, 20, None)
        rows = {r["id"]: r for r in res["rows"]}
        self.assertTrue(any("v0.111.1 buff" in x for x in rows["MANGLE"]["reasons"]))
        self.assertTrue(any("reworked" in x for x in rows["EXPECT_A_FIGHT"]["reasons"]))

    def test_engines(self):
        deck = STARTER + offer("Demon Form")
        self.assertTrue(draft.engines(deck)["strength"])
        res = draft.score_offer(deck, offer("Twin Strike"), "IRONCLAD", 2, 20, None)
        self.assertTrue(any("Strength engine" in x for x in res["rows"][0]["reasons"]))
        self.assertTrue(draft.engines(STARTER + offer("Feel No Pain"))["exhaust"])

    def test_from_state(self):
        st = {"ok": True, "data": {"run": {"floor": 7, "act_id": "0", "boss_id": "VANTOM_BOSS",
                                           "deck": [{"card_id": "STRIKE_IRONCLAD"}] * 5 + [{"card_id": "BASH"}]},
                                   "reward": {"card_options": [{"card_id": "TWIN_STRIKE"}, {"card_id": "INFLAME"}]}}}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(st, f)
        deck, off, act, floor, boss = draft.from_state(f.name)
        Path(f.name).unlink()
        self.assertEqual((len(deck), off, act, floor, boss), (6, ["CARD.TWIN_STRIKE", "CARD.INFLAME"], 1, 7, "VANTOM_BOSS"))
        self.assertEqual(draft.guess_character(deck), "IRONCLAD")

    def test_simulated_boss_value(self):
        deck = draft.expand_deck(["STRIKE_IRONCLAD:4", "DEFEND_IRONCLAD:4", "BASH", "POMMEL_STRIKE", "SHRUG_IT_OFF", "ANGER", "INFLAME"], "IRONCLAD")
        base, deltas = draft.simulated_boss_value(deck, ["CARD.TWIN_STRIKE", "CARD.BREAKTHROUGH"], "VANTOM_BOSS", runs=20)
        self.assertTrue(0 <= base <= 1)
        self.assertGreater(deltas["CARD.TWIN_STRIKE"], deltas["CARD.BREAKTHROUGH"])
        self.assertIsNone(draft.simulated_boss_value(deck, ["CARD.TWIN_STRIKE"], "KNOWLEDGE_DEMON_BOSS"))


if __name__ == "__main__":
    unittest.main()
