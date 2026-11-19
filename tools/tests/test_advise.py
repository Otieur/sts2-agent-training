"""Tests for tools/advise.py: one fixture per screen, in the STS2-Agent documented format."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import advise  # noqa: E402

DECK = [{"card_id": "STRIKE_IRONCLAD", "upgraded": False}] * 5 + [{"card_id": "DEFEND_IRONCLAD", "upgraded": False}] * 4 + \
       [{"card_id": "BASH", "upgraded": False}, {"card_id": "FEEL_NO_PAIN", "upgraded": False}]
RUN = {"floor": 8, "act_id": "1", "ascension": 0, "current_hp": 50, "max_hp": 80, "gold": 160, "boss_id": "VANTOM_BOSS",
       "deck": DECK, "potions": [{"potion_id": "FIRE_POTION", "name": "Fire Potion", "occupied": True},
                                 {"potion_id": None, "name": None, "occupied": False}]}


def st(screen, **kw):
    return {"ok": True, "data": dict({"screen": screen, "run": RUN}, **kw)}


class TestAdvise(unittest.TestCase):
    def test_combat(self):
        s = st("COMBAT", combat={"player": {"current_hp": 50, "energy": 3, "block": 0, "powers": []},
                                 "hand": [{"index": 0, "card_id": "STRIKE_IRONCLAD", "energy_cost": 1, "playable": True},
                                          {"index": 1, "card_id": "DEFEND_IRONCLAD", "energy_cost": 1, "playable": True}],
                                 "enemies": [{"index": 0, "name": "Louse", "current_hp": 6, "block": 0, "is_alive": True,
                                              "powers": [], "intents": [{"damage": 7, "hits": 1, "total_damage": 7}]}]})
        out = advise.advise(s)
        self.assertIn("[COMBAT]", out)
        self.assertIn("LETHAL", out)

    def test_card_reward(self):
        s = st("REWARD", reward={"pending_card_choice": True, "card_options": [
            {"index": 0, "card_id": "TWIN_STRIKE"}, {"index": 1, "card_id": "BREAKTHROUGH"}]})
        out = advise.advise(s)
        self.assertIn("[CARD REWARD]", out)
        self.assertIn("Vantom", out)
        self.assertIn("Recommendation:", out)

    def test_reward_main(self):
        s = st("REWARD", reward={"rewards": [{"index": 0, "reward_type": "Gold", "description": "25 Gold"},
                                             {"index": 1, "reward_type": "Card", "description": "Add a card"}]})
        out = advise.advise(s)
        self.assertLess(out.index("option_index=1"), out.index("option_index=0"))

    def test_rest(self):
        s = st("REST", rest={"options": [{"index": 0, "option_id": "HEAL"}, {"index": 1, "option_id": "SMITH"}]})
        out = advise.advise(s)
        self.assertIn("next fight boss", out)
        self.assertIn("next fight elite", out)
        self.assertIn("FEEL_NO_PAIN", out)  # engine piece first in upgrade candidates
        out = advise.advise(s, "other")
        self.assertNotIn("next fight boss", out)

    def test_rest_rule_values(self):
        r = advise.rest_rule(20, 80, 1, 0, "VANTOM_BOSS", "IRONCLAD")
        self.assertEqual(r["other"][0], "rest")  # 25% < 35%
        r = advise.rest_rule(70, 80, 3, 0, None, "IRONCLAD")
        self.assertEqual(r["boss"][0], "smith")  # 87.5% >= 70% in Act 3

    def test_event(self):
        s = st("EVENT", event={"event_id": "ABYSSAL_BATHS", "title": "Abyssal Baths", "options": [
            {"index": 0, "text_key": "ABYSSAL_BATHS.pages.INITIAL.options.IMMERSE", "title": "Immerse"},
            {"index": 1, "text_key": "ABYSSAL_BATHS.pages.INITIAL.options.ABSTAIN", "title": "Abstain"}]})
        out = advise.advise(s)
        self.assertIn("Gain 2 Max HP", out)
        self.assertIn("lethal-possible", out)
        self.assertIn("Heal 10 HP", out)

    def test_shop(self):
        s = st("SHOP", shop={"cards": [{"index": 0, "card_id": "SHRUG_IT_OFF", "price": 50, "is_stocked": True, "enough_gold": True}],
                             "relics": [{"index": 0, "name": "Vajra", "price": 150, "is_stocked": True, "enough_gold": True}],
                             "potions": [], "card_removal": {"price": 75, "available": True, "enough_gold": True}})
        out = advise.advise(s)
        self.assertIn("buy_card option_index=0", out)
        self.assertIn("remove a Strike", out)
        self.assertIn("Vajra", out)

    def test_map(self):
        nodes = [{"row": 0, "col": 0, "node_type": "Start", "children": [{"row": 1, "col": 0}, {"row": 1, "col": 1}]},
                 {"row": 1, "col": 0, "node_type": "Elite", "children": [{"row": 2, "col": 0}]},
                 {"row": 1, "col": 1, "node_type": "Monster", "children": [{"row": 2, "col": 0}]},
                 {"row": 2, "col": 0, "node_type": "Boss", "children": []}]
        s = st("MAP", map={"nodes": nodes, "current_node": {"row": 0, "col": 0}, "boss_node": {"row": 2, "col": 0},
                           "available_nodes": [{"index": 0, "row": 1, "col": 0}, {"index": 1, "row": 1, "col": 1}]})
        out = advise.advise(s)
        self.assertIn("[MAP]", out)
        self.assertIn("option_index=", out)

    def test_fallback(self):
        out = advise.advise(st("MAIN_MENU"))
        self.assertIn("MAIN_MENU", out)


if __name__ == "__main__":
    unittest.main()
