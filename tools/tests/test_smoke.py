"""Offline tests for tools/smoke.py with documented-format states and a fake opener."""
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import smoke  # noqa: E402
from test_advise import st as advise_state  # noqa: E402
from test_sts import FakeResp  # noqa: E402

COMBAT = advise_state("COMBAT", session={"mode": "singleplayer"}, combat={
    "player": {"current_hp": 50, "energy": 3, "block": 0, "powers": []}, "end_turn_will_kill_player": False,
    "hand": [{"index": 0, "card_id": "STRIKE_IRONCLAD", "energy_cost": 1, "playable": True,
              "dynamic_values": [{"name": "Damage", "current_value": 6}]}],
    "enemies": [{"index": 0, "name": "Louse", "current_hp": 12, "block": 0, "powers": [], "intents": [{"damage": 5, "hits": 1}]}]})


class Opener:
    def __init__(self, health, state):
        self.health, self.state, self.posts = health, state, 0

    def __call__(self, req, timeout=10):
        if req.get_method() == "POST":
            self.posts += 1
        body = self.health if req.full_url.endswith("/health") else self.state
        return FakeResp(json.dumps({"ok": True, "data": body}).encode())


class TestSmoke(unittest.TestCase):
    def test_get_path(self):
        self.assertEqual(smoke.get_path({"a": [{"b": 1}, {"b": 2}]}, "a[].b"), (True, [1, 2]))
        self.assertFalse(smoke.get_path({"a": {}}, "a.b")[0])

    def test_combat_ok(self):
        scr, issues, notes = smoke.check_state(COMBAT)
        self.assertEqual(scr, "COMBAT")
        self.assertEqual(issues, [])

    def test_advice_failure_is_a_problem(self):
        import advise
        saved = advise._advise
        advise._advise = lambda *a, **k: 1 / 0  # any handler failure
        try:
            scr, issues, notes = smoke.check_state(COMBAT)
        finally:
            advise._advise = saved
        self.assertTrue(any("advise.py failed: [ADVICE FAILED]" in i for i in issues))

    def test_missing_field_and_unknown_card(self):
        bad = json.loads(json.dumps(COMBAT))
        del bad["data"]["combat"]["hand"][0]["energy_cost"]
        bad["data"]["run"]["deck"].append({"card_id": "MIDNIGHT", "upgraded": False})
        scr, issues, notes = smoke.check_state(bad)
        self.assertTrue(any("combat.hand[].energy_cost" in i for i in issues))
        self.assertTrue(any("MIDNIGHT" in n for n in notes))

    def test_health_and_read_only(self):
        op = Opener({"service": "sts2-ai-agent", "game_version": "v0.107.1", "status": "degraded",
                     "compatibility": {"missing_members": [{"member": "X.y", "feature": "hand"}]}}, COMBAT["data"])
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = smoke.main(["--port", "8080"], opener=op)
        out = buf.getvalue()
        self.assertIn("game_version v0.107.1", out)
        self.assertIn("X.y (hand)", out)
        self.assertEqual(code, 1)
        self.assertEqual(op.posts, 0)

    def test_mcp_state(self):
        from test_sts import COMBAT as MCP_COMBAT, MAP as MCP_MAP
        import copy
        st = copy.deepcopy(MCP_COMBAT)
        st["player"]["draw_pile"], st["player"]["discard_pile"] = [], []
        import tempfile
        tmp = tempfile.TemporaryDirectory()
        cache = str(Path(tmp.name) / "deck.json")
        scr, issues, notes = smoke.check_mcp_state(st, cache)
        self.assertEqual(scr, "boss")
        self.assertEqual(issues, [])
        bad = copy.deepcopy(MCP_MAP)
        del bad["map"]["next_options"]
        scr, issues, notes = smoke.check_mcp_state(bad, cache)
        self.assertTrue(any("next_options" in i for i in issues))
        tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
