"""Tests for the observation encoder (P9.E1.S1): simulator states and live fixtures encode, shapes are consistent,
numeric fields round-trip, unknown ids fall back to the unknown entry. Standard library only (no torch needed)."""
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "learn"))
import encode as E  # noqa: E402

SIM = sorted((HERE / "fixtures" / "sim").glob("obs-*.json"))
LIVE = sorted((HERE / "fixtures" / "live").glob("combat-*.json"))


def check_shapes(t, enc):
    t.assertEqual(len(enc["glob"]), len(E.GLOBAL_FIELDS))
    t.assertEqual(len(enc["hand_ids"]), len(enc["hand_feats"]))
    for row in enc["hand_feats"]:
        t.assertEqual(len(row), len(E.HAND_FEATS))
    t.assertEqual(len(enc["enemy_ids"]), len(enc["enemy_feats"]))
    for row in enc["enemy_feats"]:
        t.assertEqual(len(row), len(E.ENEMY_FEATS))
    for p in ("draw", "discard", "exhaust", "choice"):
        t.assertEqual(len(enc[p + "_ids"]), len(enc[p + "_upg"]))
    t.assertEqual(len(enc["epow_ids"]), len(enc["epow_amt"]))
    t.assertEqual(len(enc["epow_ids"]), len(enc["epow_owner"]))
    t.assertTrue(all(0 <= o < len(enc["enemy_ids"]) for o in enc["epow_owner"]))
    for row in enc["mates"]:
        t.assertEqual(len(row), len(E.MATE_FEATS))
    for v in enc["glob"] + [x for r in enc["hand_feats"] + enc["enemy_feats"] for x in r]:
        t.assertIsInstance(v, float)
        t.assertTrue(-10 <= v <= 10, v)


class TestEncoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.enc = E.Encoder()

    def test_fixtures_present(self):
        self.assertGreaterEqual(len(SIM), 3)
        self.assertGreaterEqual(len(LIVE), 1)

    def test_sim_states(self):
        for f in SIM:
            obs = json.loads(f.read_text())
            enc = self.enc.encode(obs)
            check_shapes(self, enc)
            c = obs["combat"]
            self.assertEqual(len(enc["hand_ids"]), len(c["hand"]))
            self.assertEqual(len(enc["draw_ids"]), len(c["draw_pile"]))
            self.assertEqual(sum(enc["draw_upg"]), sum(1 for x in c["draw_pile"] if x.endswith("+")))
            self.assertNotIn(1, enc["hand_ids"] + enc["draw_ids"] + enc["enemy_ids"] + enc["relic_ids"], f.name)   # all ids known
            self.assertEqual(len(enc["mates"]), 0)

    def test_round_trip(self):
        for f in SIM:
            obs = json.loads(f.read_text())
            g = E.decode_global(self.enc.encode(obs)["glob"])
            p, c = obs["combat"]["player"], obs["combat"]
            self.assertAlmostEqual(g["hp"], p["current_hp"])
            self.assertAlmostEqual(g["max_hp"], p["max_hp"])
            self.assertAlmostEqual(g["block"], p["block"])
            self.assertAlmostEqual(g["energy"], p["energy"])
            self.assertAlmostEqual(g["turn"], obs["turn"])
            self.assertAlmostEqual(g["ascension"], obs["run"]["ascension"])
            self.assertAlmostEqual(g["draw_count"], c["draw_pile_count"])
            self.assertAlmostEqual(g["hand_count"], len(c["hand"]))
            alive = [e for e in c["enemies"] if e["is_alive"] and e["current_hp"] > 0]
            self.assertAlmostEqual(g["enemy_hp_total"], sum(e["current_hp"] for e in alive))
            self.assertAlmostEqual(g["enemies_alive"], len(alive))
            self.assertAlmostEqual(g["piles_known"], 1.0)

    def test_choice(self):
        obs = json.loads((HERE / "fixtures" / "sim" / "obs-choice.json").read_text())
        enc = self.enc.encode(obs)
        self.assertEqual(len(enc["choice_ids"]), len(obs["choice"]["options"]))
        self.assertEqual(E.decode_global(enc["glob"])["choice_pending"], 1.0)

    def test_unknown_ids(self):
        obs = copy.deepcopy(json.loads(SIM[0].read_text()))
        obs["combat"]["hand"][0]["card_id"] = "CARD_FROM_A_FUTURE_PATCH"
        obs["combat"]["enemies"][0]["enemy_id"] = "MONSTER_FROM_A_FUTURE_PATCH"
        enc = self.enc.encode(obs)
        self.assertEqual(enc["hand_ids"][0], 1)
        self.assertEqual(enc["enemy_ids"][0], 1)
        self.assertIn(("cards", "CARD_FROM_A_FUTURE_PATCH"), self.enc.unknown)

    def test_live_fixtures(self):
        for f in LIVE:
            state = json.loads(f.read_text())
            obs = E.from_live(state)
            enc = self.enc.encode(obs)
            check_shapes(self, enc)
            g = E.decode_global(enc["glob"])
            self.assertEqual(g["piles_known"], 0.0)
            self.assertEqual(len(enc["hand_ids"]), len(state["combat"]["hand"]))
            self.assertEqual(len(enc["enemy_ids"]), len(state["combat"]["enemies"]))
            self.assertNotIn(1, enc["hand_ids"] + enc["enemy_ids"] + enc["relic_ids"], f.name)

    def test_seat_axis(self):
        """A co-op observation (teammates present) encodes without a format change."""
        obs = copy.deepcopy(json.loads(SIM[0].read_text()))
        obs["players"] = 2
        obs["combat"]["teammates"] = [{"current_hp": 50, "max_hp": 70, "block": 5, "energy": 3, "is_alive": True}]
        enc = self.enc.encode(obs)
        check_shapes(self, enc)
        self.assertEqual(len(enc["mates"]), 1)
        self.assertAlmostEqual(E.decode_global(enc["glob"])["players"], 2)

    def test_placeholder_hp(self):
        """An unkillable phase's placeholder HP (about 10^9) is clipped and left out of the enemy HP total."""
        obs = copy.deepcopy(json.loads(SIM[0].read_text()))
        before = E.decode_global(self.enc.encode(obs)["glob"])["enemy_hp_total"]
        obs["combat"]["enemies"].append(dict(obs["combat"]["enemies"][0], current_hp=999999953, max_hp=999999999, index=len(obs["combat"]["enemies"])))
        enc = self.enc.encode(obs)
        self.assertLessEqual(max(r[0] for r in enc["enemy_feats"]), E.HP_CLIP / E.HP_SCALE)
        self.assertAlmostEqual(E.decode_global(enc["glob"])["enemy_hp_total"], before)

    def test_vocab_rules(self):
        for kind, names in self.enc.vocab.items():
            self.assertEqual(names[:2], ["<pad>", "<unk>"], kind)
            self.assertEqual(len(names), len(set(names)), kind)


if __name__ == "__main__":
    unittest.main()
