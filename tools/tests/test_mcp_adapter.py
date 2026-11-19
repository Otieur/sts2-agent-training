"""Tests for tools/mcp_adapter.py using the STS2MCP documentation examples (tools/tests/test_sts.py fixtures)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import advise  # noqa: E402
import mcp_adapter  # noqa: E402
from test_sts import COMBAT, MAP  # noqa: E402

PILES = json.loads(json.dumps(COMBAT))
PILES["player"]["draw_pile"] = [{"id": "STRIKE_IRONCLAD"}] * 3 + [{"id": "DEFEND_IRONCLAD"}] * 4
PILES["player"]["discard_pile"] = [{"id": "BASH"}]
PILES["player"]["exhaust_pile"] = []


class TestMcpAdapter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = Path(self.tmp.name) / "deck.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_combat(self):
        a = mcp_adapter.mcp_to_agent(PILES, self.cache)
        self.assertEqual(a["screen"], "COMBAT")
        self.assertEqual(a["room_type"], "boss")
        h = a["combat"]["hand"]
        self.assertEqual(h[1]["card_id"], "TWIN_STRIKE")
        self.assertEqual(h[0]["dynamic_values"][0], {"name": "Damage", "current_value": 6})
        e = a["combat"]["enemies"][0]
        self.assertEqual((e["index"], e["enemy_id"], e["intents"][0]["damage"]), ("VANTOM_0", "VANTOM", 7))
        self.assertEqual(e["powers"][0]["power_id"], "SLIPPERY")
        self.assertEqual(len(a["run"]["deck"]), 2 + 7 + 1)   # hand + draw + discard
        self.assertTrue(self.cache.exists())

    def test_deck_cache_and_map(self):
        mcp_adapter.mcp_to_agent(PILES, self.cache)
        a = mcp_adapter.mcp_to_agent(MAP, self.cache)
        self.assertEqual(a["screen"], "MAP")
        self.assertEqual(len(a["run"]["deck"]), 10)           # from the cache
        self.assertEqual(a["run"]["boss_id"], "VANTOM_BOSS")
        self.assertEqual(a["map"]["available_nodes"][0]["node_type"], "Monster")

    def test_advise_on_mcp_combat(self):
        out = advise.advise(PILES, deck_cache=str(self.cache))
        self.assertIn("[COMBAT]", out)
        self.assertIn("fight type: boss", out)
        self.assertIn("--mod sts2mcp", out)
        self.assertIn("target=VANTOM_0", out)


if __name__ == "__main__":
    unittest.main()
