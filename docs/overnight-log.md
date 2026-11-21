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

- 01:00–01:33, stage 1 (save-based rebuild): three host faults found and fixed. (1) Setting up a saved run called the game's reload counter, which writes save bookkeeping: skipped like the other save writers (SA-1). (2) The rebuild entered the room before the act map existed: it now launches the run and generates the map first, as the game's own load does. (3) Restores during search failed after a few turns: the game's load keeps references into the recording's serializable run and changes them during play, so the recording is now read from its bytes on every rebuild and restore. The run driver also treated a card choice during a fight (Armaments) as the end of the fight; such choices now count as fight actions. Result: 28 of 28 direct rebuilds equal the run host's visible state (0.03 s each); two whole smoke runs with `mcw2` searched 247 decisions with 0 mismatches, 0 errors, 0 fallbacks (A0, `base` policy: floors 12 and 17).
- 01:29, stage 2: `vsearch-5b` finished (2534 s). Neither hypothesis holds: `mcwq6` − `mcw6` −10.3 (interval −18.5 to −3.4; time ratio 0.70), losses mostly in elites; `qpolicy` − planner +2.2 (p 0.46). Section 5 of `reports/phase9/value-search-comparison-5.md`; README findings and benchmark table refreshed.
- 01:36, stage 3: Release host rebuilt with tonight's host changes. Checks: clone 12/12, fair play 8/8, sandbox 3/3, fidelity 11/11, and the new `sim.py clone --from-save` (snapshot and restore on fights rebuilt from simulated runs) 11/11 exact, median restore 6.6 ms.

- 01:41, stage 5: run benchmark 2 pre-registered (`reports/phase9/run-bench-2.md`): `base` against `draft+shop+rest` (H1) and `draft+shop+rest+path` against `draft+shop+rest` (H2), 60 seeds at Ascension 5, `mcw6` in every fight, stop at 09:45. A timing pilot (3 other seeds) showed max HP falling from 80 to 1 in the Tablet of Truth event, because the shared first-option rule kept deciphering; every arm then died by floor 7 or 8. Before the run, the shared event rule became the Player's most frequent choice at that point in the history (section 6 of the registration); 30 seeds with planner combat then showed no max-HP collapse. Added `--deadline` to the run benchmark.
- 01:47: `run-bench-2` started (6 workers, Release host, output `data/learn/runs/run-bench-2/`).

- 01:50–02:10, extra stage 7 (run-level clones and sampler, P7.E8.S4; decision 0004 step 3), on the Debug host while stage 5 runs: the host keeps the save the game makes at room entry in memory (still nothing written; sandbox 3/3) and rebuilds a run from it plus the run actions since (`run_export`, `run_from_save`); with a sample seed `sim/RunSampler.cs` re-samples the hidden future (generators, later maps, unvisited room lists, later bosses and Ancients, relic queues; the current act's boss is visible and kept, and is now in the run observation as `act_boss`). `sim.py runclone`: 17/17 exact rebuilds with the same continuation; sampler keeps the visible state, same seed same future, other seeds and the truth differ, later maps re-sampled; leak canary 2/20. Clone, clone from saves, fair play and sandbox pass on the Debug host.
- 02:20, extra stage 8: `tools/run_eval.py` (card rewards by sampled rollouts: each option on the same 6 re-sampled futures to the end of the act, planner fighting) and the `rdraft` component in the run benchmark; run benchmark 3 pre-registered (`reports/phase9/run-bench-3.md`: `rdraft+shop+rest` against `draft+shop+rest`, 60 seeds at A5, `mcw6` in every fight, stop 09:45). Chain F waits for run benchmark 2, rebuilds the Release host, runs every check (clone, clone from saves, runclone, fair play, sandbox, fidelity) and starts run benchmark 3 only if all pass (log: scratchpad `chain-f.out`).

## Resume here
Stage 5 is running (`data/learn/runs/run-bench-2/`; the process writes `manifest.json` when all workers stop, at the latest shortly after 09:45). If this session restarts: do not start it again; wait for the manifest, then `python3 -I tools/run_bench.py --report data/learn/runs/run-bench-2` (H1) and `--baseline draft+shop+rest` (H2), and write section 5 of the registration. Chain F then starts run benchmark 3 (`data/learn/runs/run-bench-3/`, writes `manifest.json` when done or shortly after 09:45); its section 5 is written the same way with `--baseline draft+shop+rest`. Then stage 6 (morning report, README, push).
