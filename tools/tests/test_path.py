"""Tests for tools/path.py on a synthetic map (the model reads data/runs.db)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import path as pathmod  # noqa: E402


def make_map():
    nodes = []

    def node(r, c, t, kids):
        nodes.append({"row": r, "col": c, "node_type": t, "children": [{"row": a, "col": b} for a, b in kids]})
    node(0, 1, "Start", [(1, 0), (1, 2)])
    node(1, 0, "Monster", [(2, 0)]); node(1, 2, "Unknown", [(2, 2)])
    node(2, 0, "Elite", [(3, 0)]); node(2, 2, "Monster", [(3, 1), (3, 2)])
    node(3, 0, "Elite", [(4, 0)]); node(3, 1, "Shop", [(4, 1)]); node(3, 2, "Unknown", [(4, 1)])
    node(4, 0, "RestSite", [(5, 1)]); node(4, 1, "RestSite", [(5, 1)])
    node(5, 1, "Boss", [])
    return {"nodes": nodes, "current_node": None, "starting_node": {"row": 0, "col": 1}, "boss_node": {"row": 5, "col": 1}}


class TestPath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = pathmod.get_model("IRONCLAD", 0)
        cls.nodes, cls.start, cls.boss = pathmod.load_map(make_map())

    def test_enumerate(self):
        paths = pathmod.enumerate_paths(self.nodes, self.start, self.boss)
        self.assertEqual(len(paths), 3)
        self.assertTrue(all(p[0] == (0, 1) and p[-1] == (5, 1) for p in paths))

    def test_types(self):
        self.assertEqual(pathmod.norm_type("RestSite"), "rest_site")
        self.assertEqual(pathmod.norm_type("Event"), "unknown")
        self.assertEqual(self.nodes[(4, 0)]["type"], "rest_site")

    def test_model_sane(self):
        self.assertLess(self.model.room[(1, "elite")]["hp"], self.model.room[(1, "monster")]["hp"])
        self.assertGreater(self.model.room[(1, "elite")]["relic"], 0.5)
        self.assertGreater(self.model.fight_risk("elite", 0.4), self.model.fight_risk("elite", 0.8))
        self.assertGreater(self.model.boss_curve[3](0.4), self.model.boss_curve[3](0.9))

    def test_low_hp_avoids_elites_and_flags(self):
        paths = pathmod.enumerate_paths(self.nodes, self.start, self.boss)
        res = pathmod.rank(paths, self.nodes, self.model, 1, 30, 80, "VANTOM_BOSS", 12)
        self.assertEqual(res[0]["elites"], 0)
        elite_route = next(o for o in res if o["elites"] == 2)
        self.assertTrue(elite_route["notes"])
        self.assertGreater(elite_route["p_end"], res[0]["p_end"])

    def test_rest_rule(self):
        # HP 20/80 reaching a rest site before the boss: must rest (under 35%)
        o = pathmod.simulate([(3, 1), (4, 1), (5, 1)], self.nodes, self.model, 1, 20, 80, "VANTOM_BOSS")
        self.assertEqual(o["loot"]["rest"], 1)
        o = pathmod.simulate([(3, 1), (4, 1), (5, 1)], self.nodes, self.model, 1, 80, 80, "VANTOM_BOSS")
        self.assertEqual(o["loot"]["upgrade"], 1)

    def test_state_input(self):
        st = {"data": {"map": make_map(), "run": {"current_hp": 60, "max_hp": 80, "act_id": "0", "ascension": 0,
                                                  "boss_id": "VANTOM_BOSS"}}}
        import json
        import tempfile
        import io
        from contextlib import redirect_stdout
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(st, f)
        buf = io.StringIO()
        with redirect_stdout(buf):
            pathmod.main(["--state", f.name, "--top", "1"])
        Path(f.name).unlink()
        self.assertIn("3 routes", buf.getvalue())
        self.assertIn("risk weight 12", buf.getvalue())

    def test_large_map_is_fast(self):
        import random
        import time
        rng = random.Random(9)
        types = ["Monster"] * 5 + ["Unknown"] * 3 + ["Elite", "RestSite", "Shop", "Treasure"]
        nodes, layer = [], {0: [3]}
        for r in range(15):
            nxt = set()
            for c in sorted(set(layer[r])):
                kids = sorted({max(0, min(6, c + d)) for d in rng.sample([-1, 0, 1], rng.choice([2, 2, 3]))})
                nxt |= set(kids)
                nodes.append({"row": r, "col": c, "node_type": "Start" if r == 0 else rng.choice(types),
                              "children": [{"row": r + 1, "col": k} for k in kids] if r < 14 else [{"row": 15, "col": 3}]})
            layer[r + 1] = sorted(nxt)
        nodes.append({"row": 15, "col": 3, "node_type": "Boss", "children": []})
        n, s, b = pathmod.load_map({"nodes": nodes, "current_node": None, "starting_node": {"row": 0, "col": 3}, "boss_node": {"row": 15, "col": 3}})
        t0 = time.time()
        paths = pathmod.enumerate_paths(n, s, b)
        res = pathmod.rank(paths, n, self.model, 1, 70, 80, "VANTOM_BOSS", 12)
        self.assertGreater(len(paths), 1000)
        self.assertLess(time.time() - t0, 5.0)
        self.assertTrue(res)


if __name__ == "__main__":
    unittest.main()
