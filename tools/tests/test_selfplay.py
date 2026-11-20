"""Offline tests for the fight-spec generator of tools/selfplay.py (no host needed)."""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import selfplay as sp  # noqa: E402

ENCOUNTERS = [
    {"id": "A1_HALL", "room_type": "Monster", "weak": False, "acts": [1]},
    {"id": "A1_WEAK", "room_type": "Monster", "weak": True, "acts": [1]},
    {"id": "OTHER_ACT1_HALL", "room_type": "Monster", "weak": False, "acts": []},
    {"id": "A2_HALL", "room_type": "Monster", "weak": False, "acts": [2]},
    {"id": "A3_HALL", "room_type": "Monster", "weak": False, "acts": [3]},
    {"id": "A1_ELITE", "room_type": "Elite", "weak": False, "acts": [1]},
    {"id": "A2_ELITE", "room_type": "Elite", "weak": False, "acts": [2]},
    {"id": "A3_ELITE", "room_type": "Elite", "weak": False, "acts": [3]},
    {"id": "A1_BOSS", "room_type": "Boss", "weak": False, "acts": [1]},
    {"id": "A2_BOSS", "room_type": "Boss", "weak": False, "acts": [2]},
    {"id": "A3_BOSS", "room_type": "Boss", "weak": False, "acts": [3]},
]
POOL = [{"id": f"C{i}", "rarity": r, "type": "Attack"} for i, r in enumerate(["Common"] * 5 + ["Uncommon"] * 3 + ["Rare"] * 2 + ["Basic", "Ancient"])]


class TestSpecs(unittest.TestCase):
    def test_reproducible(self):
        a = sp.make_spec(random.Random(5), ENCOUNTERS, POOL)
        b = sp.make_spec(random.Random(5), ENCOUNTERS, POOL)
        self.assertEqual(a, b)

    def test_encounter_matches_act_and_room(self):
        for s in range(300):
            spec = sp.make_spec(random.Random(s), ENCOUNTERS, POOL)
            enc = next(e for e in ENCOUNTERS if e["id"] == spec["encounter"])
            self.assertFalse(enc["weak"])
            self.assertEqual(enc["room_type"], spec["room"])
            self.assertTrue(spec["act"] in enc["acts"] or (not enc["acts"] and spec["act"] == 1))

    def test_deck_size_and_contents(self):
        for s in range(300):
            spec = sp.make_spec(random.Random(s), ENCOUNTERS, POOL)
            lo, hi = sp.ADDED[spec["act"]]
            rlo, rhi = sp.REMOVED[spec["act"]]
            self.assertTrue(10 - rhi + lo <= len(spec["deck"]) <= 10 - rlo + hi)
            self.assertFalse(any(c.rstrip("+") in ("C10", "C11") for c in spec["deck"]))   # no Basic or Ancient draws
            self.assertTrue(32 <= spec["hp"] <= 80)
            self.assertTrue(0 <= spec["ascension"] <= 10)



class TestAugment(unittest.TestCase):
    def test_augment(self):
        spec = {"source": {"run": "R1", "floor": 5}, "act": 1, "room": "Monster", "encounter": "A1_HALL", "ascension": 3, "character": "IRONCLAD",
                "deck": ["STRIKE_IRONCLAD"] * 5 + ["DEFEND_IRONCLAD"] * 4 + ["BASH", "C1", "C2"], "relics": ["BURNING_BLOOD", "R1", "R2", "R3"],
                "potions": ["P1", "P2"], "hp": 60, "max_hp": 80}
        for seed in range(200):
            a = sp.augment(spec, random.Random(seed), POOL)
            self.assertEqual(a["source"], spec["source"])
            self.assertEqual(a["relics"][0], "BURNING_BLOOD")
            self.assertTrue(set(a["relics"]) <= set(spec["relics"]))
            self.assertTrue(8 <= len(a["deck"]) <= len(spec["deck"]) + 3)
            self.assertTrue(1 <= a["hp"] <= 80)
            self.assertFalse(any(c.rstrip("+") in ("C10", "C11") for c in a["augmented"]["added"]))
        self.assertEqual(sp.augment(spec, random.Random(3), POOL), sp.augment(spec, random.Random(3), POOL))
        self.assertEqual(spec["deck"][-1], "C2")                                   # the original is not modified


class TestBenchmark(unittest.TestCase):
    def test_stratified_selection(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        import fight_specs as fs
        specs = []
        for run in range(40):
            for (room, act) in fs.BENCHMARK_QUOTA:
                for floor in range(2):
                    specs.append({"room": room, "act": act, "valid": True, "source": {"run": f"R{run}", "floor": floor + act * 10}})
        picked = fs.benchmark(specs)
        self.assertEqual(len(picked), sum(fs.BENCHMARK_QUOTA.values()))
        for key, n in fs.BENCHMARK_QUOTA.items():
            self.assertEqual(sum(1 for s in picked if (s["room"], s["act"]) == key), n)
        per_run = {}
        for s in picked:
            per_run[s["source"]["run"]] = per_run.get(s["source"]["run"], 0) + 1
        self.assertLessEqual(max(per_run.values()), 2)
        self.assertEqual(picked, fs.benchmark(specs))          # fixed seed: the same set every time


if __name__ == "__main__":
    unittest.main()
