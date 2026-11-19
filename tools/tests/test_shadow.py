"""Offline test for tools/shadow.py: a fake game where the Player takes a card and rests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import shadow  # noqa: E402

DECK = [{"card_id": "STRIKE_IRONCLAD", "upgraded": False}] * 5 + [{"card_id": "DEFEND_IRONCLAD", "upgraded": False}] * 4 + \
       [{"card_id": "BASH", "upgraded": False}]


def state(screen, deck=DECK, hp=50, **kw):
    return {"screen": screen, "run": {"floor": 3, "act_id": "0", "ascension": 0, "current_hp": hp, "max_hp": 80, "gold": 99,
                                      "boss_id": "VANTOM_BOSS", "deck": deck, "potions": []}, **kw}


class FakeAdapter:
    def __init__(self, states):
        self.states = list(states)

    def state(self):
        return self.states.pop(0) if len(self.states) > 1 else self.states[0]


class TestShadow(unittest.TestCase):
    def test_calls_and_resolution(self):
        reward = state("REWARD", reward={"card_options": [{"index": 0, "card_id": "TWIN_STRIKE"}, {"index": 1, "card_id": "BREAKTHROUGH"}]})
        after_pick = state("MAP", deck=DECK + [{"card_id": "TWIN_STRIKE", "upgraded": False}], map={})
        rest = state("REST", hp=20, rest={"options": [{"index": 0, "option_id": "HEAL"}, {"index": 1, "option_id": "SMITH"}]})
        after_rest = state("MAP", hp=44, map={})
        rest["run"]["floor"] = 4
        after_rest["run"]["floor"] = 5
        with tempfile.TemporaryDirectory() as d:
            n = shadow.shadow(FakeAdapter([reward, reward, after_pick, rest, after_rest, after_rest]), d, interval=0,
                              sleep=lambda s: None, max_states=6)
            rows = [json.loads(x) for x in (Path(d) / "calls.jsonl").read_text().splitlines()]
            self.assertEqual(n, 6)
            card = next(r for r in rows if r["kind"] == "card_reward")
            self.assertEqual(card["player_pick"], "TWIN_STRIKE")
            self.assertIn("agree", card)
            rest_row = next(r for r in rows if r["kind"] == "rest")
            self.assertEqual((rest_row["agent_pick"], rest_row["player_pick"], rest_row["agree"]), ("HEAL", "HEAL", True))
            self.assertIn("rest", shadow.summary(d))


class TestDeferredPicks(unittest.TestCase):
    """Live 2026-11-19: the map pick and the smith upgrade show up a few screens after the click."""

    def test_map_pick_waits_for_the_new_current_node(self):
        call = {"kind": "map", "floor": 25, "options": ["8,2", "8,3"], "agent_pick": "8,3"}
        before = {"run": {"floor": 25}, "map": {"current_node": {"row": 7, "col": 2}}}
        stale = {"run": {"floor": 26}, "map": {"current_node": {"row": 7, "col": 2}}}  # fight screen, old node
        shadow.resolve(call, before, stale)
        self.assertIsNone(call["player_pick"])
        self.assertFalse(shadow.final(call, stale))
        moved = {"run": {"floor": 26}, "map": {"current_node": {"row": 8, "col": 2}}}
        shadow.resolve(call, before, moved)
        self.assertEqual(call["player_pick"], "8,2")
        self.assertFalse(call["agree"])
        self.assertTrue(shadow.final(call, moved))

    def test_rest_smith_seen_on_a_later_screen(self):
        call = {"kind": "rest", "floor": 27, "agent_pick": "SMITH"}
        deck = [{"card_id": "BASH", "upgraded": False}]
        before = {"run": {"floor": 27, "current_hp": 50, "deck": deck}}
        selecting = {"run": {"floor": 27, "current_hp": 50, "deck": deck}}
        shadow.resolve(call, before, selecting)
        self.assertFalse(shadow.final(call, selecting))
        done = {"run": {"floor": 27, "current_hp": 50, "deck": [{"card_id": "BASH", "upgraded": True}]}}
        shadow.resolve(call, before, done)
        self.assertEqual(call["player_pick"], "SMITH")
        self.assertTrue(call["agree"])

    def test_rest_other_once_the_run_moves_on(self):
        call = {"kind": "rest", "floor": 27, "agent_pick": "SMITH"}
        st = {"run": {"floor": 27, "current_hp": 50, "deck": []}}
        shadow.resolve(call, st, st)
        self.assertTrue(shadow.final(call, {"run": {"floor": 28}}))
        self.assertEqual(call["player_pick"], "OTHER")
        self.assertFalse(call["agree"])


if __name__ == "__main__":
    unittest.main()
