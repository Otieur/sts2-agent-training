"""Offline tests for the shadowing tools (watch, record, reconstruct) with synthetic STS2MCP-style states."""
import copy
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import reconstruct  # noqa: E402
import record  # noqa: E402
import watch  # noqa: E402
from stsstate import compact, decision_point, parse_intent_damage  # noqa: E402

BASE = {
    "state_type": "elite",
    "run": {"act": 1, "floor": 9, "ascension": 0},
    "player": {"hp": 40, "max_hp": 80, "block": 0, "gold": 50, "energy": 3,
               "hand": [{"id": "STRIKE_IRONCLAD", "cost": "1"}, {"id": "BASH", "cost": "2"}, {"id": "DEFEND_IRONCLAD", "cost": "1"}],
               "potions": [{"id": "WEAK_POTION"}], "status": []},
    "battle": {"round": 1, "turn": "player", "is_play_phase": True,
               "enemies": [{"entity_id": "BYRDONIS_0", "hp": 92, "block": 0, "status": [], "intents": [{"label": "3x3"}]}]},
}


class FakeAdapter:
    def __init__(self, states):
        self.states = list(states)

    def state(self):
        return self.states.pop(0) if len(self.states) > 1 else self.states[0]


class TestState(unittest.TestCase):
    def test_intent_parse(self):
        self.assertEqual([parse_intent_damage(x) for x in ("11", "6x2", "3 x 3", "Buff", None)], [11, 12, 9, 0, 0])

    def test_elite_turn1_is_decision_point(self):
        self.assertIn("turn 1", decision_point(compact(BASE)))

    def test_high_incoming(self):
        s = copy.deepcopy(BASE)
        s["battle"]["round"] = 3
        s["battle"]["enemies"][0]["intents"] = [{"label": "16"}]
        s["player"]["hp"] = 30
        self.assertIn("high incoming", decision_point(compact(s)))


class TestWatch(unittest.TestCase):
    def test_fires_once_per_screen(self):
        with tempfile.TemporaryDirectory() as d:
            memo = Path(d) / "memo"
            r1, _ = watch.watch(FakeAdapter([BASE]), memo, interval=0, timeout=1, sleep=lambda s: None)
            self.assertIsNotNone(r1)
            ticks = iter(range(10))
            r2, _ = watch.watch(FakeAdapter([BASE]), memo, interval=0, timeout=3, clock=lambda: next(ticks), sleep=lambda s: None)
            self.assertIsNone(r2)


class TestRecordAndReconstruct(unittest.TestCase):
    def test_record_dedup_and_reconstruct_play(self):
        s1 = copy.deepcopy(BASE)
        s2 = copy.deepcopy(BASE)
        s2["player"]["hand"] = [h for h in s2["player"]["hand"] if h["id"] != "BASH"]
        s2["player"]["energy"] = 1
        s2["battle"]["enemies"][0]["hp"] = 84
        s3 = copy.deepcopy(s2)
        s3["player"]["potions"] = []
        s4 = copy.deepcopy(s3)
        s4["battle"]["turn"] = "enemy"
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "states.jsonl.gz"
            n = record.record(FakeAdapter([s1, s1, s2, s3, s4]), out, interval=0, combat_interval=0, max_seconds=10,
                              sleep=lambda s: None, max_snapshots=4)
            self.assertEqual(n, 4)
            with gzip.open(out, "rt") as f:
                snaps = [json.loads(x) for x in f]
        actions = reconstruct.reconstruct(snaps)
        kinds = [a["type"] for a in actions]
        self.assertEqual(kinds, ["play", "potion", "end_turn"])
        play = actions[0]
        self.assertEqual((play["card"], play["target"], play["confidence"]), ("BASH", "BYRDONIS_0", "high"))


class TestAgentFormat(unittest.TestCase):
    def test_compact_agent_combat(self):
        st = {"ok": True, "data": {"screen": "COMBAT", "turn": 1, "available_actions": ["play_card", "end_turn"],
              "run": {"floor": 17, "act_id": "1", "current_hp": 50, "max_hp": 80, "gold": 99, "boss_id": "VANTOM_BOSS",
                      "potions": [{"potion_id": "FIRE_POTION", "occupied": True}, {"potion_id": None, "occupied": False}]},
              "combat": {"player": {"current_hp": 50, "max_hp": 80, "block": 0, "energy": 3,
                                    "powers": [{"power_id": "STRENGTH_POWER", "amount": 2}]},
                         "hand": [{"card_id": "STRIKE_IRONCLAD", "name": "Strike", "energy_cost": 1, "upgraded": False}],
                         "enemies": [{"index": 0, "enemy_id": "VANTOM", "current_hp": 173, "block": 0, "is_alive": True,
                                      "powers": [{"power_id": "SLIPPERY_POWER", "amount": 9}],
                                      "intents": [{"intent_type": "Attack", "damage": 6, "hits": 2}]}]}}}
        c = compact(st)
        self.assertEqual((c["screen"], c["fight"], c["act"], c["floor"], c["hp"]), ("combat", "boss", 1, 17, 50))
        self.assertEqual(c["enemies"][0]["intents"], ["6x2"])
        self.assertEqual(c["potions"], ["FIRE_POTION"])
        self.assertEqual(parse_intent_damage(c["enemies"][0]["intents"][0]), 12)
        self.assertIn("turn 1 of boss fight", decision_point(c))

    def test_compact_agent_screens(self):
        c = compact({"screen": "REWARD", "run": {}, "reward": {"card_options": [{"card_id": "BASH"}]}})
        self.assertEqual((c["screen"], c["options"]), ("card_reward", ["BASH"]))
        c = compact({"screen": "MAP", "run": {}, "map": {"available_nodes": [{"node_type": "Elite"}]}})
        self.assertEqual((c["screen"], c["options"]), ("map", ["Elite"]))
        self.assertTrue(decision_point(c).startswith("decision screen"))


if __name__ == "__main__":
    unittest.main()
