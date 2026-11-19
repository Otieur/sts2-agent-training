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


if __name__ == "__main__":
    unittest.main()
