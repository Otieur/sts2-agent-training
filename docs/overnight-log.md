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

- 01:10–01:50, stage 1 (save-based rebuild): three host faults found and fixed. (1) Setting up a saved run called the game's reload counter, which writes save bookkeeping: skipped like the other save writers (SA-1). (2) The rebuild entered the room before the act map existed: it now launches the run and generates the map first, as the game's own load does. (3) Restores during search failed after a few turns: the game's load keeps references into the recording's serializable run and changes them during play, so the recording is now read from its bytes on every rebuild and restore. The run driver also treated a card choice during a fight (Armaments) as the end of the fight; such choices now count as fight actions. Result: 28 of 28 direct rebuilds equal the run host's visible state (0.03 s each); two whole smoke runs with `mcw2` searched 247 decisions with 0 mismatches, 0 errors, 0 fallbacks (A0, `base` policy: floors 12 and 17).
- 01:29, stage 2: `vsearch-5b` finished (2534 s). Neither hypothesis holds: `mcwq6` − `mcw6` −10.3 (interval −18.5 to −3.4; time ratio 0.70), losses mostly in elites; `qpolicy` − planner +2.2 (p 0.46). Section 5 of `reports/phase9/value-search-comparison-5.md`; README findings and benchmark table refreshed.
- 01:55, stage 3: Release host rebuilt with tonight's host changes. Checks: clone 12/12, fair play 8/8, sandbox 3/3, fidelity 11/11, and the new `sim.py clone --from-save` (snapshot and restore on fights rebuilt from simulated runs) 11/11 exact, median restore 6.6 ms.

## Resume here
Stages 1–3 done. Next: stage 5 (pre-register the whole-run comparison with search combat, then run it on the Release host). Stage 4's smoke test is covered by the stage 1 smoke runs.
