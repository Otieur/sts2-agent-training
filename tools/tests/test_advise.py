"""Tests for tools/advise.py: one fixture per screen, in the STS2-Agent documented format."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import advise  # noqa: E402

DECK = [{"card_id": "STRIKE_IRONCLAD", "upgraded": False}] * 5 + [{"card_id": "DEFEND_IRONCLAD", "upgraded": False}] * 4 + \
       [{"card_id": "BASH", "upgraded": False}, {"card_id": "FEEL_NO_PAIN", "upgraded": False}]
RUN = {"floor": 8, "act_id": "0", "ascension": 0, "current_hp": 50, "max_hp": 80, "gold": 160, "boss_id": "VANTOM_BOSS",
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

    def test_ancient_record(self):
        s = st("EVENT", event={"event_id": "NEOW", "title": "Neow", "options": [
            {"index": 0, "text_key": "NEOW.pages.INITIAL.options.HEFTY_TABLET", "title": "Hefty Tablet"},
            {"index": 1, "text_key": "NEOW.pages.INITIAL.options.FISHING_ROD", "title": "Fishing Rod"}]})
        out = advise.advise(s)
        self.assertIn("Ancient record", out)
        self.assertIn("p=0.016", out)

    def test_fight_type(self):
        def combat_with(enemy_id):
            return {"run": {"boss_id": "VANTOM_BOSS"}, "combat": {"enemies": [{"enemy_id": enemy_id}]}}
        self.assertEqual(advise.fight_type(combat_with("VANTOM")), "boss")
        self.assertEqual(advise.fight_type(combat_with("BYRDONIS")), "elite")
        self.assertEqual(advise.fight_type(combat_with("NIBBIT")), "hallway")
        self.assertEqual(advise.fight_type(combat_with("SOMETHING_NEW")), "unknown")

    def test_selection(self):
        cards = [{"index": 0, "card_id": "STRIKE_IRONCLAD", "name": "Strike"},
                 {"index": 1, "card_id": "INJURY", "name": "Injury", "card_type": "Curse"},
                 {"index": 2, "card_id": "ASCENDERS_BANE", "name": "Ascender's Bane", "card_type": "Curse"},
                 {"index": 3, "card_id": "FEEL_NO_PAIN", "name": "Feel No Pain"}]
        out = advise.advise(st("CARD_SELECTION", selection={"kind": "deck_card_select", "prompt": "Choose a card to remove", "cards": cards}))
        lines = [l for l in out.splitlines() if "select_deck_card" in l]
        self.assertIn("Injury", lines[0])
        self.assertIn("Strike", lines[1])
        self.assertIn("Ascender", lines[-1])
        out = advise.advise(st("CARD_SELECTION", selection={"kind": "deck_upgrade_select", "prompt": "Choose a card to upgrade", "cards": cards}))
        self.assertIn("Feel No Pain", [l for l in out.splitlines() if "select_deck_card" in l][0])

    def test_act_number(self):
        from stslib import act_number
        self.assertEqual(act_number("0"), 1)     # the mod's act_id is 0-based
        self.assertEqual(act_number("2"), 3)
        self.assertEqual(act_number("ACT_1"), 1)
        self.assertEqual(act_number(None), 1)
        self.assertEqual(advise._act({"run": {"act_id": "1"}}), 2)

    def test_action_names_exist(self):
        import re
        actions = set("resolve_rewards end_turn play_card choose_map_node claim_reward choose_reward_card skip_reward_cards "
                      "select_deck_card confirm_selection proceed open_chest choose_treasure_relic choose_event_option "
                      "choose_rest_option buy_card buy_relic buy_potion remove_card_at_shop use_potion discard_potion".split())
        outs = [advise.advise(st("REWARD", reward={"card_options": [{"index": 0, "card_id": "BREAKTHROUGH"}]})),
                advise.advise(st("REWARD", reward={"rewards": [{"index": 0, "reward_type": "Gold", "description": "g"}]})),
                advise.advise(st("REST", rest={"options": [{"index": 0, "option_id": "HEAL"}, {"index": 1, "option_id": "SMITH"}]})),
                advise.advise(st("SHOP", shop={"cards": [{"index": 0, "card_id": "SHRUG_IT_OFF", "price": 50, "enough_gold": True}],
                                               "relics": [], "potions": [], "card_removal": {"price": 75, "enough_gold": True}}))]
        for out in outs:
            for name in re.findall(r"\b([a-z]+(?:_[a-z]+)+)\b(?= option_index|, then|$| \()", out):
                if name.endswith(("_select", "_tool")):
                    continue
                self.assertIn(name, actions, f"unknown action {name} in: {out}")

    def test_scaling_enemy_recommends_balanced(self):
        s = st("COMBAT", combat={"player": {"current_hp": 30, "energy": 3, "block": 0, "powers": []},
                                 "hand": [{"index": 0, "card_id": "STRIKE_IRONCLAD", "energy_cost": 1, "playable": True}],
                                 "enemies": [{"index": 0, "enemy_id": "BYRDONIS", "name": "Byrdonis", "current_hp": 80, "block": 0,
                                              "is_alive": True, "powers": [{"power_id": "TERRITORIAL_POWER", "amount": 1}],
                                              "intents": [{"damage": 16, "hits": 1}]}]})
        self.assertIn("recommended: the balanced plan (an enemy gains Strength", advise.advise(s))

    def test_curse_of_knowledge_choice(self):
        s = st("CARD_SELECTION", selection={"kind": "combat_card_select", "prompt": "Choose a card",
                                            "cards": [{"index": 0, "card_id": "DISINTEGRATION"}, {"index": 1, "card_id": "MIND_ROT"}]})
        out = advise.advise(s)
        self.assertIn("Curse of Knowledge: offer 1: take Mind Rot", out)
        picks = [l.strip() for l in out.splitlines() if l.strip().startswith("select_deck_card")]
        self.assertEqual(picks[0], "select_deck_card option_index=1: MIND_ROT")

    def test_sandpit_warning(self):
        s = st("COMBAT", combat={"player": {"current_hp": 40, "energy": 3, "block": 0,
                                            "powers": [{"power_id": "SANDPIT_POWER", "amount": 2}]},
                                 "hand": [{"index": 0, "card_id": "FRANTIC_ESCAPE", "energy_cost": 1, "playable": True},
                                          {"index": 1, "card_id": "STRIKE_IRONCLAD", "energy_cost": 1, "playable": True}],
                                 "enemies": [{"index": 0, "enemy_id": "THE_INSATIABLE", "name": "The Insatiable", "current_hp": 300,
                                              "block": 0, "is_alive": True, "powers": [], "intents": [{"damage": 8, "hits": 2}]}]})
        out = advise.advise(s)
        self.assertIn("Sandpit 2:", out)

    def test_coop_party_line(self):
        s = st("COMBAT", combat={"player": {"current_hp": 40, "energy": 3, "block": 0, "powers": []},
                                 "players": [{"player_id": "1", "is_local": False, "character_name": "Necrobinder", "current_hp": 12,
                                              "max_hp": 66, "block": 0, "is_alive": True},
                                             {"player_id": "2", "is_local": True, "character_name": "Ironclad", "current_hp": 40,
                                              "max_hp": 80, "block": 0, "is_alive": True}],
                                 "hand": [{"index": 0, "card_id": "DEFEND_IRONCLAD", "energy_cost": 1, "playable": True}],
                                 "enemies": [{"index": 0, "enemy_id": "NIBBIT", "name": "Nibbit", "current_hp": 40, "block": 0,
                                              "is_alive": True, "powers": [], "intents": [{"damage": 12, "hits": 1}]}]})
        out = advise.advise(s)
        self.assertIn("party: [0] Necrobinder HP 12/66 block 0 LOW | [1] Ironclad (you) HP 40/80", out)

    def test_waterfall_giant_safe_and_steam(self):
        s = st("COMBAT", combat={"player": {"current_hp": 40, "energy": 3, "block": 0, "powers": []},
                                 "hand": [{"index": 0, "card_id": "DEFEND_IRONCLAD", "energy_cost": 1, "playable": True}],
                                 "enemies": [{"index": 0, "enemy_id": "WATERFALL_GIANT", "name": "Waterfall Giant", "current_hp": 30,
                                              "block": 0, "is_alive": True, "powers": [{"power_id": "STEAM_ERUPTION_POWER", "amount": 33}],
                                              "intents": [{"damage": 10, "hits": 1}]}]})
        out = advise.advise(s)
        self.assertIn("recommended: the safe plan (Waterfall Giant", out)
        self.assertIn("Steam Eruption 33", out)


if __name__ == "__main__":
    unittest.main()
