"""End-to-end offline test of the run toolchain: journal -> advise -> act (decision log) -> journal fight rows ->
summary -> post-mortem facts, in a temporary run folder. Uses one of the Player's run files as the finished run."""
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import advise  # noqa: E402
import journal  # noqa: E402
import postmortem  # noqa: E402
import sts  # noqa: E402
from stslib import DATA  # noqa: E402
from test_advise import st as state  # noqa: E402
from test_sts import RoutingOpener  # noqa: E402

COMBAT = state("COMBAT", session={"mode": "singleplayer"}, combat={
    "player": {"current_hp": 50, "energy": 3, "block": 0, "powers": []}, "end_turn_will_kill_player": False,
    "hand": [{"index": 0, "card_id": "STRIKE_IRONCLAD", "energy_cost": 1, "playable": True},
             {"index": 1, "card_id": "BASH", "energy_cost": 2, "playable": True}],
    "enemies": [{"index": 0, "name": "Louse", "current_hp": 14, "block": 0, "is_alive": True, "powers": [],
                 "intents": [{"damage": 6, "hits": 1}]}]})["data"]


class TestIntegration(unittest.TestCase):
    def test_run_toolchain(self):
        with tempfile.TemporaryDirectory() as d:
            runs = Path(d) / "runs"
            jpath = journal.new_journal("IRONCLAD", 0, "TESTSEED0001", runs_dir=runs, now=datetime(2026, 11, 20, 10, 0))
            folder = jpath.parent
            self.assertEqual(journal.active_journals(runs), [jpath])

            # advise on a combat state, then act through sts.py (STS2-Agent, fake game) with a logged reason
            advice = advise.advise(COMBAT)
            self.assertIn("LETHAL", advice)
            op = RoutingOpener({8080: {"health": {"instance_role": "human", "companion": None}, "state": COMBAT}})
            log = folder / "decisions.jsonl"
            with redirect_stdout(io.StringIO()):
                sts.main(["--mod", "sts2agent", "--log", str(log), "act", "play_card", "card_index=1", "target_index=0",
                          "--reason", "Bash first for Vulnerable, then Strike is lethal"], opener=op)
                sts.main(["--mod", "sts2agent", "--log", str(log), "act", "play_card", "card_index=0", "target_index=0",
                          "--reason", "Strike for lethal", "--tool-pick", "play_card card_index=0 target_index=0"], opener=op)
            recs = [json.loads(x) for x in log.read_text().splitlines()]
            self.assertEqual([r["screen"] for r in recs], ["COMBAT", "COMBAT"])
            self.assertTrue(all(r["reason"] for r in recs))

            # journal: floor and fight rows, summary
            text = jpath.read_text()
            text = journal.append_row(text, "Floor log", [2, "monster", "won", "-3", "Bash then Strike"])
            bench = journal.load_benchmarks("IRONCLAD", 0)
            _, row, _ = journal.fight_row(journal.parse_header(text), 2, "NIBBITS_WEAK", 3, 3, [], bench)
            text = journal.append_row(text, "Fight log", row)
            jpath.write_text(text)
            s = journal.summarize(text, bench)
            self.assertEqual(s["fights"], 1)

            # finish: a real run file as run.run, then the facts sheet reads the decision log
            src = sorted((DATA / "raw").glob("*.run"))[0]
            shutil.copy(src, folder / "run.run")
            with redirect_stdout(io.StringIO()):
                postmortem.main([str(folder)])
            facts = (folder / "facts.md").read_text()
            self.assertIn("Decisions logged", facts)
            self.assertIn("COMBAT", facts)
            self.assertIn("Tool recommendations: followed 1, overridden 0", facts)
            self.assertTrue(recs[1]["followed_tool"])
            (folder / "postmortem.md").write_text("done")
            self.assertEqual(journal.active_journals(runs), [])


if __name__ == "__main__":
    unittest.main()
