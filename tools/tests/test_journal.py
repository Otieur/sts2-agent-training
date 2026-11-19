"""Offline tests for tools/journal.py."""
import csv
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import journal  # noqa: E402


def write_bench(d):
    b = Path(d) / "benchmarks"
    b.mkdir(parents=True)
    hdr = ["band", "encounter", "n", "median_dmg", "p75_dmg", "p90_dmg", "median_turns", "benchmark_grade"]
    with open(b / "ironclad-encounters-by-band-v0.107.1.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(hdr)
        w.writerow(["A0-4", "ENCOUNTER.VANTOM_BOSS", 6, 30, 40, 50, 6, "yes"])
        w.writerow(["A0-4", "ENCOUNTER.QUEEN_BOSS", 2, 99, 99, 99, 9, "no"])  # n < 5: ignored
        w.writerow(["A10", "ENCOUNTER.VANTOM_BOSS", 9, 45, 55, 60, 7, "yes"])
    with open(b / "allchars-encounters-by-band-v0.107.1.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(hdr)
        w.writerow(["A0-4", "ENCOUNTER.QUEEN_BOSS", 7, 50, 60, 70, 8, "yes"])
    with open(b / "ironclad-encounters-v0.107.1.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["encounter", "n", "median_dmg", "p75_dmg", "p90_dmg", "median_turns", "benchmark_grade"])
        w.writerow(["ENCOUNTER.NIBBITS_WEAK", 20, 5, 8, 10, 3, "yes"])


class TestJournal(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        write_bench(self.d / "data")
        self.bench = journal.load_benchmarks("IRONCLAD", 2, data_dir=self.d / "data")
        self.path = journal.new_journal("IRONCLAD", 2, "ABCDEF123456", exam=True, runs_dir=self.d / "runs",
                                        now=datetime(2026, 11, 20, 14, 5))

    def tearDown(self):
        self.tmp.cleanup()

    def test_benchmark_layers(self):
        self.assertEqual(self.bench["ENCOUNTER.VANTOM_BOSS"]["median_dmg"], "30")  # own band, not A10
        self.assertEqual(self.bench["ENCOUNTER.QUEEN_BOSS"]["source"], "all characters A0-4")  # own band n < 5
        self.assertEqual(self.bench["ENCOUNTER.NIBBITS_WEAK"]["source"], "Ironclad pooled")
        self.assertEqual(journal.band_of(10), "A10")

    def test_new_header(self):
        text = self.path.read_text()
        h = journal.parse_header(text)
        self.assertEqual((h["seed"], h["character"], h["ascension"]), ("ABCDEF123456", "IRONCLAD", 2))
        self.assertIn("Exam seed: yes", text)
        self.assertIn("Started: 2026-11-20 14:05", text)
        with self.assertRaises(SystemExit):
            journal.new_journal("IRONCLAD", 2, "ABCDEF123456", runs_dir=self.d / "runs", now=datetime(2026, 11, 20))

    def test_active(self):
        self.assertEqual(journal.active_journals(self.d / "runs"), [self.path])
        (self.path.parent / "postmortem.md").write_text("done")
        self.assertEqual(journal.active_journals(self.d / "runs"), [])

    def test_normalize(self):
        known = self.bench.keys() | journal.CHANGED_V0111.keys()
        self.assertEqual(journal.normalize_encounter("vantom", known), "ENCOUNTER.VANTOM_BOSS")
        self.assertEqual(journal.normalize_encounter("ENCOUNTER.QUEEN_BOSS", known), "ENCOUNTER.QUEEN_BOSS")
        self.assertEqual(journal.normalize_encounter("queen_boss", known), "ENCOUNTER.QUEEN_BOSS")
        with self.assertRaises(SystemExit):
            journal.normalize_encounter("EXOSKELETONS", known)  # NORMAL and WEAK

    def test_floor_and_fight_rows(self):
        text = self.path.read_text()
        text = journal.append_row(text, "Floor log", [1, "ancient", "took relic", "0", "pipe | in note"])
        text = journal.append_row(text, "Floor log", [2, "monster", "won", "-6", ""])
        rows = journal.table_rows(text, "Floor log")
        self.assertEqual([r[0] for r in rows], ["1", "2"])
        self.assertEqual(rows[0][4], "pipe / in note")
        hdr = journal.parse_header(text)
        enc, row, flags = journal.fight_row(hdr, 17, "vantom", 6, 45, ["BLOCK_POTION"], self.bench)
        self.assertEqual(enc, "ENCOUNTER.VANTOM_BOSS")
        self.assertTrue(any("above p75" in f for f in flags))
        text = journal.append_row(text, "Fight log", row)
        _, row, flags = journal.fight_row(hdr, 48, "QUEEN_BOSS", 8, 40, [], self.bench)
        self.assertIn("changed on v0.111.1", flags)
        text = journal.append_row(text, "Fight log", row)
        s = journal.summarize(text, self.bench)
        self.assertEqual((s["fights"], s["damage"], s["benchmark_median_total"]), (2, 85.0, 80.0))
        self.assertEqual(len(s["above_p75"]), 1)
        self.assertEqual(s["changed_v0111"], ["QUEEN_BOSS"])
        # The floor log is untouched by fight rows.
        self.assertEqual(len(journal.table_rows(text, "Floor log")), 2)

    def test_status(self):
        text = journal.set_status(self.path.read_text(), {"floor": 9, "act": 1, "hp": 40, "max_hp": 80, "gold": 120,
                                                          "potions": ["WEAK_POTION"]})
        self.assertIn("Floor 9, act 1, HP 40/80, gold 120, potions WEAK_POTION", text)
        self.assertNotIn("<hp>", text)
        text = journal.set_status(text, journal.status_from_state(
            {"run": {"floor": 10, "act": 1}, "player": {"hp": 35, "max_hp": 80, "gold": 130, "potions": []}}))
        self.assertIn("Floor 10, act 1, HP 35/80, gold 130, potions none", text)
        self.assertNotIn("Floor 9,", text)
        s = journal.status_from_state({"floor": 3, "act": 1, "hp": 70, "max_hp": 80, "gold": 99, "potions": ["X"]})
        self.assertEqual(s["potions"], ["X"])

    def test_status_from_agent_state(self):
        st = {"ok": True, "data": {"screen": "MAP", "run": {"floor": 12, "act_id": "0", "current_hp": 41, "max_hp": 80, "gold": 150,
                                                            "potions": [{"potion_id": "FIRE_POTION", "occupied": True}]}}}
        s = journal.status_from_state(st)
        self.assertEqual((s["floor"], s["act"], s["hp"], s["max_hp"], s["gold"], s["potions"]), (12, 1, 41, 80, 150, ["FIRE_POTION"]))


if __name__ == "__main__":
    unittest.main()
