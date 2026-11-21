# Overnight Log (2026-11-21): Whole Runs with Search in Every Fight

**Status: IN PROGRESS.** A new session reads "Resume here" first, then continues from the first unfinished stage. Previous logs: `docs/overnight-log-2026-11-20.md` (finished), `docs/day-log-2026-11-20.md` (the day before this night).

## Instructions from the Player (2026-11-21, about 00:50, before sleeping)
Work alone for about ten hours with no help; branch and push in time. Standing permissions from earlier still apply: work on branches and push them; fast-forward `master` for the front page only; update the README on major results. The repository is public with the Player as its only author (no attribution lines; neutral wording; no personal paths).

## Safety and housekeeping
- The machine: lid open, on mains power; `caffeinate -is` holds off sleep for 11 hours (started 00:50). If the log shows a long gap, check `pmset -g log` for sleep.
- Branch: `overnight/2026-11-21-whole-runs` (from `overnight/2026-11-20-full-run-sim`). Push after every stage. `master` only by fast-forward, for README updates.
- Never rebuild the Release host (`sim/bin/Release`) while a Release host runs; develop on the Debug build (`SIM_CONFIG=Debug`).
- Comparisons that decide anything are pre-registered before they run (ML-10); results go into the registered file's section 5, changes into section 6.
- Fair play (FP-1, FP-15): decisions only from what a player can see; search re-samples the hidden future.

## Plan (decision 0004: whole runs first)
| Stage | Work | Done when |
|---|---|---|
| 1 | Verify the save-based fight rebuild (`fight_from_save`): visible state equal to the run host's, rollouts not stuck | Test numbers logged; fixes made if needed |
| 2 | Record comparison 5 (`vsearch-5b`: action-value filter `mcwq6`, fast policy `qpolicy`) | Section 5 written; README if a hypothesis holds |
| 3 | Rebuild the Release host with today's host changes (fight export, local choices, save rebuild); run clone, fair-play, sandbox and fidelity checks | All checks pass, logged |
| 4 | Search combat inside the run benchmark through `fight_from_save` (the run driver keeps each fight's actions); smoke test; measure minutes per run | One run plays every fight by search with few fallbacks |
| 5 | Pre-registered whole-run comparison with search combat (deck-building components), sized to finish by about 09:00 | Results recorded |
| 6 | Morning report (`docs/overnight-report-2026-11-21.md`), README, push | Report written and pushed |

## Log
- 00:50: Set up: caffeinate for 11 hours, branch `overnight/2026-11-21-whole-runs` pushed, this log. Running: q-v5 training then `vsearch-5b` (comparison 5 rerun); the save-based rebuild test (3 seeds).

## Resume here
Stage 1 is running (`fight_from_save` test). Stage 2 waits for `vsearch-5b` (`data/learn/bench/vsearch-5b/manifest.json`).
