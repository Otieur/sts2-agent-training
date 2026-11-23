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



class TestEndOfTurnCheck(unittest.TestCase):
    """tools/selfplay.py end_turn_checked: ending the turn against the planner's next card (no host needed)."""
    HAND = [{"card_id": "STRIKE_IRONCLAD", "upgraded": False}, {"card_id": "DEFEND_IRONCLAD", "upgraded": False},
            {"card_id": "STRIKE_IRONCLAD", "upgraded": False}, {"card_id": "STRIKE_IRONCLAD", "upgraded": True}]
    CANDS = [{"type": "play", "card": 0, "target": 0}, {"type": "play", "card": 1}, {"type": "end_turn"}]

    def done(self, strike, defend, end):
        return {(ci, j): v for ci, vals in enumerate((strike, defend, end)) for j, v in enumerate(vals)}

    def check(self, done, planned, best=2, z=2.0, k=6):
        counts = {"asked": 0, "kept": 0, "played": 0, "absent": 0}
        return sp.end_turn_checked(self.CANDS, done, k, best, planned, self.HAND, z, counts), counts

    def test_inside_the_noise_the_planners_card_is_played(self):
        end = [-300, -180, -420, -250, -310, -200]                 # mean about -277
        strike = [-250, -330, -300, -380, -200, -320]              # mean about -297: 20 points behind, differences spread widely
        pick, counts = self.check(self.done(strike, [-900] * 6, end), {"type": "play", "card": 0, "target": 0})
        self.assertEqual(pick, 0)
        self.assertEqual(counts, {"asked": 1, "kept": 0, "played": 1, "absent": 0})

    def test_a_clear_end_of_turn_is_kept(self):
        end = [-200, -210, -190, -205, -195, -200]
        strike = [-400, -390, -410, -395, -405, -400]              # 200 points behind in every world
        pick, counts = self.check(self.done(strike, [-900] * 6, end), {"type": "play", "card": 0, "target": 0})
        self.assertEqual(pick, 2)
        self.assertEqual(counts["kept"], 1)

    def test_where_every_world_is_won_the_search_stands(self):
        end = [60, 40, 58, 71, 47, 59]                             # a fight being won: HP left
        strike = [57, 62, 35, 58, 64, 56]                          # 0.5 HP behind on average, inside the noise
        pick, counts = self.check(self.done(strike, [0] * 6, end), {"type": "play", "card": 0, "target": 0})
        self.assertEqual((pick, counts["asked"]), (2, 0))

    def test_one_lost_world_is_enough_for_the_check(self):
        end = [60, 40, 58, 71, 47, 59]
        strike = [57, 62, 35, 58, -260, 56]                        # one world lost: ending is clearly ahead on average, by one world
        pick, counts = self.check(self.done(strike, [0] * 6, end), {"type": "play", "card": 0, "target": 0})
        self.assertEqual((pick, counts["asked"], counts["played"]), (0, 1, 1))
        end = [60, 40, 58, -300, 47, 59]                           # the lost world on the side of ending the turn
        strike = [50, 30, 48, -330, 37, 49]                        # 10 or 30 behind in every world: a steady edge is kept
        pick, counts = self.check(self.done(strike, [0] * 6, end), {"type": "play", "card": 0, "target": 0})
        self.assertEqual((pick, counts["kept"]), (2, 1))

    def test_unchanged_when_the_best_is_a_card_or_the_planner_ends_the_turn_or_the_check_is_off(self):
        d = self.done([-250] * 6, [-900] * 6, [-300, -180, -420, -250, -310, -200])
        planned = {"type": "play", "card": 0, "target": 0}
        self.assertEqual(self.check(d, planned, best=0)[0], 0)
        self.assertEqual(self.check(d, {"type": "end_turn"})[0], 2)
        self.assertEqual(self.check(d, {"type": "potion", "slot": 0})[0], 2)
        self.assertEqual(self.check(d, planned, z=None)[0], 2)
        self.assertEqual(self.check(d, planned, z=None)[1]["asked"], 0)

    def test_a_copy_of_the_planners_card_counts_and_another_card_or_target_does_not(self):
        d = self.done([-290, -330, -300, -380, -200, -320], [-900] * 6, [-300, -180, -420, -250, -310, -200])
        self.assertEqual(self.check(d, {"type": "play", "card": 2, "target": 0})[0], 0)        # the second plain Strike
        pick, counts = self.check(d, {"type": "play", "card": 3, "target": 0})                 # the upgraded one is another card
        self.assertEqual((pick, counts["absent"]), (2, 1))
        self.assertEqual(self.check(d, {"type": "play", "card": 0, "target": 1})[0], 2)        # another target

    def test_rollouts_that_did_not_finish_are_left_out_and_three_worlds_are_needed(self):
        end = [-300, None, -420, None, -310, None]
        strike = [-250, -330, None, -380, -200, None]
        d = self.done(strike, [-900] * 6, end)                     # two worlds scored both
        pick, counts = self.check(d, {"type": "play", "card": 0, "target": 0})
        self.assertEqual((pick, counts["kept"]), (2, 1))
        d = self.done([-250, -330, -300, None, -200, -320], [-900] * 6, [-300, -180, -420, -250, None, -200])   # four
        self.assertEqual(self.check(d, {"type": "play", "card": 0, "target": 0})[0], 0)

    def test_a_card_whose_step_failed_is_not_played(self):
        d = self.done([-1000.0] * 6, [-900] * 6, [-300, -180, -420, -250, -310, -200])
        self.assertEqual(self.check(d, {"type": "play", "card": 0, "target": 0})[0], 2)


class TestChoiceNotes(unittest.TestCase):
    def test_a_choice_is_noted_with_what_was_taken(self):
        del sp.CHOICES[:]
        o = {"choice": {"kind": "FromChooseACardScreen", "min": 0, "max": 1, "options": ["DISINTEGRATION", "MIND_ROT"]}}
        both = [{"type": "choose", "cards": [0]}, {"type": "choose", "cards": [1]}]
        sp.note_choice(o, both, 1)
        sp.note_choice(o, both[:1], 0)
        self.assertEqual(sp.CHOICES, [
            {"kind": "FromChooseACardScreen", "options": ["DISINTEGRATION", "MIND_ROT"], "taken": ["MIND_ROT"], "candidates": 2, "first": False},
            {"kind": "FromChooseACardScreen", "options": ["DISINTEGRATION", "MIND_ROT"], "taken": ["DISINTEGRATION"], "candidates": 1, "first": True}])
        del sp.CHOICES[:]

    def test_a_search_with_one_answer_notes_it_and_scores_nothing(self):
        class OneAnswer:
            def legal(self):
                return [{"type": "choose", "cards": [0]}]
        del sp.CHOICES[:]
        o = {"choice": {"kind": "FromHand", "min": 1, "max": 1, "options": ["BASH"]}, "combat": {"hand": []}}
        cands, values, best = sp.scored_search(OneAnswer(), o, "balanced", 6, 2, 0)
        self.assertEqual((cands, values, best), ([{"type": "choose", "cards": [0]}], [None], 0))
        self.assertEqual([(c["taken"], c["candidates"]) for c in sp.CHOICES], [(["BASH"], 1)])
        del sp.CHOICES[:]


if __name__ == "__main__":
    unittest.main()
