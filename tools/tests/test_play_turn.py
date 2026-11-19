"""Offline tests for tools/play_turn.py: parsing the plan commands printed by tools/advise.py."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import play_turn  # noqa: E402

ADVICE = """[COMBAT]
safe:
  Strike → Slime[0] + Defend
      deal 6, kills 0, block 5 vs incoming 4, HP lost 0, HP after 80, energy left 1, enemy HP [5]
balanced:
  Pommel Strike → Slime[0] + Strike → Slime[0]
      deal 15, kills 1, block 0 vs incoming 4, HP lost 4, HP after 76, energy left 0, enemy HP [0]
commands for the top safe plan (indexes already adjusted):
  python3 -I tools/sts.py --mod sts2agent --log runs/<run>/decisions.jsonl act play_card card_index=2 target_index=0 --reason "Turn plan (safe): Strike on enemy 0"
  python3 -I tools/sts.py --mod sts2agent --log runs/<run>/decisions.jsonl act play_card card_index=1 --reason "Turn plan (safe): Defend"
  python3 -I tools/sts.py --mod sts2agent --log runs/<run>/decisions.jsonl act end_turn --reason "Turn plan (safe) complete"
commands for the top balanced plan (indexes already adjusted):
  python3 -I tools/sts.py --mod sts2agent --log runs/<run>/decisions.jsonl act play_card card_index=3 target_index=0 --reason "Turn plan (balanced): Pommel Strike on enemy 0"
  # after re-planning: python3 -I tools/sts.py --mod sts2agent --log runs/<run>/decisions.jsonl act play_card card_index=1 target_index=0 --reason "x"
"""


class TestPlanCommands(unittest.TestCase):
    def test_safe_plan_commands_and_summary(self):
        summary, cmds = play_turn.plan_commands(ADVICE, "safe")
        self.assertEqual(len(cmds), 3)
        self.assertIn("card_index=2 target_index=0", cmds[0])
        self.assertTrue(summary.startswith("Strike → Slime[0] + Defend (deal 6"))
        self.assertNotIn("energy left", summary)

    def test_stops_at_a_hand_changing_card(self):
        _, cmds = play_turn.plan_commands(ADVICE, "balanced")
        self.assertEqual(len(cmds), 1)  # the play after Pommel Strike's draw waits for a re-plan

    def test_ready_rules(self):
        self.assertTrue(play_turn.ready({"screen": "COMBAT", "available_actions": ["play_card", "end_turn"], "combat": {}}))
        self.assertFalse(play_turn.ready({"screen": "COMBAT", "available_actions": ["save_and_quit"], "combat": {}}))
        self.assertFalse(play_turn.ready({"screen": "COMBAT", "available_actions": ["play_card"],
                                          "combat": {"action_readiness": {"can_use_combat_actions": False}}}))
        self.assertTrue(play_turn.ready({"screen": "MAP", "available_actions": ["choose_map_node", "save_and_quit"]}))


if __name__ == "__main__":
    unittest.main()
