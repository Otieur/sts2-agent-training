"""Offline tests for tools/trace_read.py (made-up traces in a temporary folder)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import trace_read as tr  # noqa: E402

ENEMY = {"is_alive": True, "is_hittable": True, "powers": []}


def dec(turn, chosen, cands, values, hand=("STRIKE_IRONCLAD",), energy=1, enemies=(ENEMY,), choice=None, named=None, planner=None, obs=True):
    d = {"turn": turn, "hp": 50, "energy": energy, "hand": list(hand), "hand_cost": [1] * len(hand), "hand_playable": [True] * len(hand), "enemy_powers": [[]],
         "chosen": chosen, "chosen_named": named or chosen["type"], "candidates": cands, "values": values, "planner": planner}
    if obs:
        d["obs"] = {"choice": choice, "combat": {"enemies": list(enemies)}}
    return d


END, STRIKE = {"type": "end_turn"}, {"type": "play", "card": 0, "target": 0}


class TestTraceRead(unittest.TestCase):
    def write(self, folder, i, status, decisions):
        json.dump({"outcome": {"status": status, "enemies": []}, "decisions": decisions}, open(f"{folder}/trace-{i}.json", "w"))
        return f"{folder}/trace-{i}.json"

    def test_a_turn_ended_between_two_forms_is_not_an_early_end_of_the_planners(self):
        with tempfile.TemporaryDirectory() as f:
            view = {"action": END, "same": True, "cards": [[0, "STRIKE_IRONCLAD", 1, True, False]], "best_play": None, "end": None, "named": "end_turn"}
            path = self.write(f, 0, "lost", [
                dec(1, END, [STRIKE, END], [-300.0, -280.0], planner=view),                                             # an enemy to hit: the planner ended it too
                dec(2, END, [STRIKE, END], [-300.0, -280.0], enemies=(dict(ENEMY, is_hittable=False),), planner=view)])  # no enemy to hit
            r = tr.read_fight(path)
            self.assertEqual((len(r["early"]), [e["no_target"] for e in r["early"]]), (2, [False, True]))
            self.assertEqual(sum(e["no_target"] for e in r["with"]), 1)
            self.assertEqual((r["lost_all"], r["scored"], r["first_turn_lost"]), (2, 2, True))

    def test_first_turn_lost_needs_every_decision_of_that_turn(self):
        with tempfile.TemporaryDirectory() as f:
            r = tr.read_fight(self.write(f, 0, "won", [dec(1, STRIKE, [STRIKE, END], [-300.0, -310.0]), dec(1, END, [STRIKE, END], [20.0, 30.0]), dec(2, END, [STRIKE, END], [-200.0, -150.0])]))
            self.assertEqual((r["first_turn_lost"], r["lost_all"]), (False, 2))

    def test_card_choices_and_the_curse_offers(self):
        first, second = {"type": "choose", "cards": [0]}, {"type": "choose", "cards": [1]}
        curse = lambda other: {"kind": "FromChooseACardScreen", "min": 0, "max": 1, "options": ["DISINTEGRATION", other]}
        with tempfile.TemporaryDirectory() as f:
            r = tr.read_fight(self.write(f, 0, "lost", [
                dec(1, END, [END], [None], hand=(), named="end_turn"),
                dec(1, first, [first], [None], hand=(), choice=curse("MIND_ROT"), named="choose (FromChooseACardScreen) DISINTEGRATION"),
                dec(2, STRIKE, [STRIKE], [None], named="play HEADBUTT+ -> 0"),
                dec(2, second, [first, second], [-300.0, -250.0], hand=(), choice={"kind": "FromCombatPile", "min": 1, "max": 1, "options": ["DEFEND_IRONCLAD", "BASH"]}, named="choose BASH"),
                dec(5, second, [first, second], [-300.0, -250.0], hand=(), choice=curse("SLOTH"), named="choose SLOTH")]))
            self.assertEqual([(c["asked"], c["searched"], c["other"], c["taken"], c["offer"]) for c in r["choices"]],
                             [("end of turn", False, False, ["DISINTEGRATION"], 1), ("HEADBUTT", True, True, ["BASH"], None), ("choose BASH", True, True, ["SLOTH"], 2)])
            self.assertEqual(tr.report(f, False), 0)

    def test_a_trace_without_observations_reads_as_before(self):
        with tempfile.TemporaryDirectory() as f:
            r = tr.read_fight(self.write(f, 0, "lost", [dec(1, END, [STRIKE, END], [-300.0, -280.0], obs=False)]))
            self.assertEqual((len(r["early"]), r["early"][0]["no_target"], r["choices"]), (1, False, []))


if __name__ == "__main__":
    unittest.main()
