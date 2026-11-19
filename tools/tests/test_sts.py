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


# --------------------------------------------------------------------------------------------- co-op (STS2-Agent)
def agent_state(local_slot, hand_name, mp=True):
    players = [{"player_id": "1", "slot_index": 0, "is_local": local_slot == 0, "character_name": "Ironclad",
                "current_hp": 50, "max_hp": 80, "block": 5, "energy": 2, "is_alive": True},
               {"player_id": "2", "slot_index": 1, "is_local": local_slot == 1, "character_name": "Silent",
                "current_hp": 60, "max_hp": 70, "block": 0, "energy": 3, "is_alive": True}]
    return {"run_id": "ABCDEF123456", "screen": "COMBAT", "turn": 2,
            "session": {"mode": "multiplayer" if mp else "singleplayer", "phase": "run"},
            "multiplayer": {"is_multiplayer": mp},
            "available_actions": ["play_card", "end_turn"],
            "run": {"floor": 6, "ascension": 0, "current_hp": 60, "max_hp": 70, "gold": 99, "potions": []},
            "combat": {"player": {"current_hp": 60, "max_hp": 70, "block": 0, "energy": 3, "powers": []},
                       "players": players,
                       "hand": [{"index": 0, "name": hand_name, "energy_cost": 1, "playable": True, "requires_target": True,
                                 "valid_target_indices": [0], "resolved_rules_text": "Deal 6 damage."}],
                       "enemies": [{"index": 0, "enemy_id": "CULTIST", "name": "Cultist", "current_hp": 40, "max_hp": 50,
                                    "block": 0, "is_alive": True, "powers": [],
                                    "intents": [{"intent_type": "Attack", "damage": 6, "hits": 2, "total_damage": 12}]}],
                       "end_turn_will_kill_player": False}}


class RoutingOpener:
    """Fake opener keyed by port: each port is one game window."""
    def __init__(self, windows):
        self.windows = windows  # port -> {"health": {...}, "state": {...}}
        self.requests = []

    def __call__(self, req, timeout=10):
        port = int(req.full_url.split("/")[2].split(":")[1])
        path = "/" + req.full_url.split("/", 3)[3]
        body = json.loads(req.data.decode()) if req.data else None
        self.requests.append((req.get_method(), port, path, body))
        w = self.windows[port]
        if req.get_method() == "POST":
            return FakeResp(json.dumps({"ok": True, "data": {"status": "completed"}}).encode())
        key = "health" if path.startswith("/health") else "state"
        return FakeResp(json.dumps({"ok": True, "data": w[key]}).encode())


def coop_windows(companion=True, mate_role="companion"):
    return {8080: {"health": {"instance_role": "human",
                              "companion": {"api_host": "127.0.0.1", "api_port": 18081, "auto_play": False} if companion else None},
                   "state": agent_state(0, "Bash")},
            18081: {"health": {"instance_role": mate_role, "companion": None}, "state": agent_state(1, "Neutralize")}}


class TestCoop(unittest.TestCase):
    def run_cli(self, argv, opener):
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, redirect_stdout(buf):
            sts.main(["--mod", "sts2agent", "--log", str(Path(d) / "log.jsonl")] + argv, opener=opener)
        return buf.getvalue()

    def test_teammate_port_discovered_and_act_sent_there(self):
        op = RoutingOpener(coop_windows())
        self.run_cli(["--instance", "teammate", "act", "play_card", "card_index=0", "target_index=0",
                      "--reason", "Hit the Cultist"], op)
        posts = [r for r in op.requests if r[0] == "POST"]
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0][1], 18081)
        self.assertEqual(posts[0][3]["client_context"]["decision_reason"], "Hit the Cultist")

    def test_host_act_refused(self):
        op = RoutingOpener(coop_windows())
        with self.assertRaises(SystemExit):
            self.run_cli(["--instance", "host", "act", "end_turn", "--reason", "x"], op)
        self.assertFalse([r for r in op.requests if r[0] == "POST"])

    def test_solo_act_on_multiplayer_run_refused(self):
        op = RoutingOpener(coop_windows())
        with self.assertRaises(SystemExit):
            self.run_cli(["act", "end_turn", "--reason", "x"], op)
        self.assertFalse([r for r in op.requests if r[0] == "POST"])

    def test_teammate_with_wrong_role_refused(self):
        op = RoutingOpener(coop_windows(mate_role="human"))
        with self.assertRaises(SystemExit):
            self.run_cli(["--instance", "teammate", "act", "end_turn", "--reason", "x"], op)
        self.assertFalse([r for r in op.requests if r[0] == "POST"])

    def test_no_companion_is_an_error(self):
        op = RoutingOpener(coop_windows(companion=False))
        with self.assertRaises(SystemExit) as cm:
            self.run_cli(["--instance", "teammate", "state"], op)
        self.assertEqual(cm.exception.code, 1)

    def test_party_view(self):
        op = RoutingOpener(coop_windows())
        out = self.run_cli(["party"], op)
        self.assertIn("Ironclad (Player) HP 50/80", out)
        self.assertIn("Silent (Agent) HP 60/70", out)
        self.assertIn("Player's hand (read-only):", out)
        self.assertIn("Bash", out)
        self.assertIn("Neutralize", out)
        self.assertIn("Attack 6x2 (=12)", out)
        self.assertIn("Consistency: ok", out)
        self.assertFalse([r for r in op.requests if r[0] == "POST"])

    def test_consistency_flags_mismatch(self):
        host, mate = agent_state(0, "Bash"), agent_state(1, "Neutralize")
        mate["combat"]["enemies"][0]["current_hp"] = 35
        mate["run"]["floor"] = 7
        issues = sts.consistency(host, mate)
        self.assertEqual(len(issues), 2)

    def test_brief_sts2agent_combat(self):
        text = sts.brief_sts2agent(agent_state(1, "Neutralize"))
        self.assertIn("[COMBAT] co-op floor 6", text)
        self.assertIn("[0] Neutralize (1) targets [0]: Deal 6 damage.", text)
        self.assertIn("Party:", text)

    def test_solo_sts2agent_act_allowed(self):
        st = agent_state(0, "Bash", mp=False)
        op = RoutingOpener({8080: {"health": {"instance_role": "human", "companion": None}, "state": st}})
        self.run_cli(["act", "end_turn", "--reason", "Nothing useful left"], op)
        self.assertEqual(len([r for r in op.requests if r[0] == "POST"]), 1)

    def test_sts2mcp_teammate_needs_port(self):
        with self.assertRaises(SystemExit):
            sts.main(["--instance", "teammate", "state"], opener=FakeOpener(COMBAT))


if __name__ == "__main__":
    unittest.main()
