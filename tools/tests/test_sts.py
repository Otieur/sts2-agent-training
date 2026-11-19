"""Offline tests for tools/sts.py with a fake HTTP opener. Fixtures follow the examples in
vendor/STS2MCP/docs/raw-full.md; they are not captured from the live game (Phase 0 replaces them)."""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import sts  # noqa: E402

COMBAT = {
    "state_type": "boss",
    "run": {"act": 1, "floor": 17, "ascension": 0},
    "player": {"character": "The Ironclad", "hp": 58, "max_hp": 80, "block": 0, "gold": 120, "energy": 3, "max_energy": 3,
               "hand": [{"index": 0, "id": "STRIKE_IRONCLAD", "name": "Strike", "type": "Attack", "cost": "1",
                         "description": "Deal 6 damage.", "target_type": "AnyEnemy", "can_play": True, "is_upgraded": False},
                        {"index": 1, "id": "TWIN_STRIKE", "name": "Twin Strike", "type": "Attack", "cost": "1",
                         "description": "Deal 5 damage twice.", "target_type": "AnyEnemy", "can_play": True, "is_upgraded": True}],
               "draw_pile_count": 10, "discard_pile_count": 0, "exhaust_pile_count": 0,
               "status": [], "potions": [{"slot": 0, "name": "Weak Potion", "target_type": "AnyEnemy"}], "max_potion_slots": 3},
    "battle": {"round": 1, "turn": "player", "is_play_phase": True,
               "enemies": [{"entity_id": "VANTOM_0", "name": "Vantom", "hp": 173, "max_hp": 173, "block": 0,
                            "status": [{"id": "SLIPPERY", "name": "Slippery", "amount": 9}],
                            "intents": [{"type": "Attack", "label": "7"}]}]},
}
MAP = {"state_type": "map", "run": {"act": 1, "floor": 1, "ascension": 0},
       "player": {"hp": 80, "max_hp": 80, "gold": 99, "status": [], "potions": []},
       "map": {"current_position": {"col": 3, "row": 0, "type": "Start"},
               "next_options": [{"index": 0, "col": 2, "row": 1, "type": "Monster", "leads_to": [{"type": "Elite"}]}],
               "boss": {"id": "ENCOUNTER.VANTOM_BOSS", "name": "Vantom"}, "bosses": [{"name": "Vantom"}]}}


class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeOpener:
    def __init__(self, state):
        self.state = state
        self.requests = []

    def __call__(self, req, timeout=10):
        body = json.loads(req.data.decode()) if req.data else None
        self.requests.append((req.get_method(), req.full_url, body))
        if req.get_method() == "POST":
            return FakeResp(json.dumps({"status": "ok", "message": "done"}).encode())
        return FakeResp(json.dumps(self.state).encode())


class TestBrief(unittest.TestCase):
    def test_combat_brief_shows_targets_and_slippery(self):
        text = sts.brief_sts2mcp(COMBAT)
        self.assertIn("VANTOM_0", text)
        self.assertIn("Slippery 9", text)
        self.assertIn("[1] Twin Strike+", text)
        self.assertIn("energy 3/3", text)

    def test_map_brief_shows_boss(self):
        text = sts.brief_sts2mcp(MAP)
        self.assertIn("Boss: Vantom", text)
        self.assertIn("[0] Monster", text)


class TestCli(unittest.TestCase):
    def test_act_builds_request_and_logs(self):
        opener = FakeOpener(COMBAT)
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "decisions.jsonl"
            buf = io.StringIO()
            with redirect_stdout(buf):
                sts.main(["--log", str(log), "act", "play_card", "card_index=1", "target=VANTOM_0",
                          "--reason", "Strip two Slippery stacks"], opener=opener)
            post = [r for r in opener.requests if r[0] == "POST"][0]
            self.assertEqual(post[1], "http://localhost:15526/api/v1/singleplayer")
            self.assertEqual(post[2], {"action": "play_card", "card_index": 1, "target": "VANTOM_0"})
            rec = json.loads(log.read_text().splitlines()[0])
            self.assertEqual((rec["screen"], rec["floor"], rec["ok"]), ("boss", 17, True))
            self.assertEqual(rec["reason"], "Strip two Slippery stacks")

    def test_blocked_action_refused(self):
        with self.assertRaises(SystemExit):
            sts.main(["act", "delete_profile", "--reason", "no"], opener=FakeOpener(COMBAT))

    def test_non_local_host_refused(self):
        with self.assertRaises(sts.ModError):
            sts._http("GET", "http://example.com:15526/")

    def test_sts2agent_sends_reason(self):
        opener = FakeOpener({"ok": True, "data": {"session": {"screen": "COMBAT"}}})
        adapter = sts.Sts2AgentAdapter(opener=opener)
        ok, _ = adapter.act("end_turn", {}, "Nothing playable")
        post = [r for r in opener.requests if r[0] == "POST"][0]
        self.assertEqual(post[2]["client_context"]["decision_reason"], "Nothing playable")


if __name__ == "__main__":
    unittest.main()
