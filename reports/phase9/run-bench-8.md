# Measurement: win rate of whole new runs at Ascension 0 (run benchmark 8)

Written before the run (ML-10), 2026-11-21 at 09:36, after the results of run benchmarks 2–6 and before any result of run benchmark 7. This is a measurement, not a comparison: one policy, to see where the whole decision stack stands at Ascension 0. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Question
- How often does the current best whole-run policy win a new Ironclad run at Ascension 0 in the simulator, making every decision itself (Neow, map moves, card rewards, events, shops, rest sites, every fight)?

Why: every run benchmark so far was at A5 or A10, where no simulated run has won, so the metric there is floors. At A0, wins become measurable and comparable with the lowest band of milestone M8. The Player suggested this measurement on 2026-11-21.

## 2. Runs
- 30 seeds (`RB008` + index 00000–00029), Ironclad, **Ascension 0**, new runs from Neow to death or victory, in the simulator (`tools/run_bench.py`). One policy, no second arm.
- Policy: the better rollout policy by run benchmark 7's registered test. `rcard+rpath+bc` if its H1 holds (one-sided sign test p < 0.05 with a positive mean difference), otherwise `rcard+rpath`. The choice is made by the starting script from run benchmark 7's manifest, before any result of this run.
- Combat: `mcw6` in every fight, through the save-based fight rebuild and the run-clone rebuild (`--fight-rebuild save+run`); mismatches and failures fall back to the planner (counted).
- Host: the Release2 build used by run benchmarks 5–7 (`sim/bin/Release2`), unchanged. No smoke test: the code path is that of run benchmarks 6 and 7, with only the ascension number changed.
- Starts when run benchmark 7 has finished, and not after 14:00. Stopping rule, fixed in advance and independent of outcomes: 6 workers take seeds in index order (worker w: seeds w, w+6, …). At 16:30 unfinished runs stop; the analysis uses the finished runs.

## 3. Policy
- Card rewards and map moves (before the boss): sampled rollouts as in run benchmarks 6 and 7, played by `path` with the rule planner fighting; with `bc`, the rollout value credits progress against bosses.
- Every fight: wide search (`mcw6`).
- Still by rules: Neow, Ancients, boss relics and potion rewards by the first option; non-Ancient events by the Player's most frequent choice; shops left without buying; rest below 60% HP, else smith the first card.

The measurement covers this whole stack, rules included.

## 4. Metrics
- Primary: wins out of finished runs, with a Wilson 95% interval.
- Secondary: mean and median floor, act bosses reached and beaten per act, where runs die (room type and act), elites fought per run, seconds per run, search fallbacks, how often rollouts differ from the rules.
- Reference, not a test (different seeds and game version, and a small sample): the Player's finished Ironclad runs at A0–4 on v0.107.1 (`data/runs.db`): 8 runs, 5 wins (63%), mean floor 38.4; at A0 alone, 2 runs and 1 win. A1–4 is harder than A0, so matching 63% at A0 alone does not yet match the band.
- With 30 runs the interval is wide (about ±17 points at a 50% rate). What follows: if the win rate is at or above 63%, the next measurement moves up within the band (A4); if it is well below, where the runs die decides which decision is improved next (fights, the remaining rule decisions, or the rollout value).

## 5. Results
Pending.

## 6. Deviations and notes
- 2026-11-21 10:14, before the run (stopping rule, not outcomes): 7 workers instead of 6, and the seeds are claimed in index order by whichever worker is free (`--dynamic`) instead of fixed seeds per worker. Reason: the Player asked for full use of the CPU and stopped the other project's processes, which frees memory; with fixed seeds the workers that finish early sit idle at the end of each benchmark (32% of the CPU idle in run benchmark 7's tail). Each seed is played the same whichever worker plays it (the same random generator per seed, search by fixed counts of sampled worlds), so the change affects only the wall time and, if the deadline stops the run, which seeds are cut, and neither depends on outcomes.
