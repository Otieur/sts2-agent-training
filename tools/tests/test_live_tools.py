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


if __name__ == "__main__":
    unittest.main()
