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

    def test_main_menu_without_run(self):
        # live STS2-Agent main menu (2026-11-19): run is null outside a run, so run fields are not required
        st = {"ok": True, "data": {"screen": "MAIN_MENU", "run": None, "run_id": None,
                                   "session": {"mode": "singleplayer", "phase": "menu", "control_scope": "local_player"},
                                   "available_actions": ["switch_profile", "open_character_select", "open_timeline"]}}
        scr, issues, notes = smoke.check_state(st)
        self.assertEqual(scr, "MAIN_MENU")
        self.assertEqual(issues, [])
        self.assertTrue(any("no active run" in n for n in notes))

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

    def test_dropped_connection_is_a_mod_error(self):
        # live 2026-11-19: quitting the game closed the connection mid-request (RemoteDisconnected)
        import http.client
        import sts

        def drop(req, timeout=None):
            raise http.client.RemoteDisconnected("Remote end closed connection without response")
        with self.assertRaises(sts.ModError) as get_err:
            sts._http("GET", "http://127.0.0.1:8080/state", opener=drop)
        self.assertNotIn("may or may not", str(get_err.exception))
        with self.assertRaises(sts.ModError) as post_err:
            sts._http("POST", "http://127.0.0.1:8080/action", body={"action": "end_turn"}, opener=drop)
        self.assertIn("may or may not have been applied", str(post_err.exception))

    def test_watch_waits_for_the_game(self):
        import sts
        calls = {"n": 0}
        clock = iter(range(0, 10_000, 100))

        class Ad(sts.Sts2AgentAdapter):  # keeps the class's static helpers (screen) that advise.py uses
            def __init__(self, *a, **k):
                pass

            def health(self):
                return {"data": {"service": "sts2-ai-agent", "game_version": "v0.111.1", "status": "ready"}}

            def state(self):
                calls["n"] += 1
                if calls["n"] == 2:
                    raise sts.ModError("connection failed")
                return {"data": {"screen": "MAIN_MENU", "run": None, "session": {"mode": "singleplayer"}}}
        orig = sts.Sts2AgentAdapter
        sts.Sts2AgentAdapter = Ad
        try:
            out = io.StringIO()
            with redirect_stdout(out):
                rc = smoke.main(["--watch", "--minutes", "5"], sleep=lambda s: None, clock=lambda: next(clock))
        finally:
            sts.Sts2AgentAdapter = orig
        self.assertEqual(rc, 0)
        self.assertIn("waiting for the game", out.getvalue())
        self.assertIn("mod reachable again", out.getvalue())


if __name__ == "__main__":
    unittest.main()
