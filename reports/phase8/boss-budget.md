# Comparison: a larger search budget for boss fights

Written before the run (P8.E1.S3, ML-10), 2026-11-20 at 21:35. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** in boss fights, wide search with 24 re-sampled worlds per candidate (`mcw24`) gets a higher fight value than with 6 (`mcw6`).

Why: boss fights are the remaining gap. At Ascension 8+ on the benchmark, `mcw6` wins 35% of boss fights (with or without potions), against 40% for the Player on the same fights, while hallways and elites are near or at the Player's level. A run has only three or four boss fights, so a few seconds more per boss decision are affordable in live play. The earlier budget comparison (all fights, planner candidates) found +8.8 for four times the worlds; boss fights are long, so more worlds may matter more there.

## 2. Fights
- The 10 boss fights of `data/sim/benchmark-v1.json` (acts 1–3, Ascension 1–10), six sample seeds each (seed base 7000000, seeds 0–5): 60 jobs (`tools/learn/bench.py --rooms Boss --seeds 6`). Seeds 0 and 1 are the jobs of the earlier comparisons; 2–5 are new. Exam seeds excluded (ML-7).
- Simulator: game v0.111.1 (cc1f9462); host with the pending-choice fix; fight values ignore placeholder enemy HP above 10,000.

## 3. Policies and budgets
- `mcw6`, `mcw24`: flat Monte Carlo over the wide candidate set (cap 8), 6 or 24 worlds per candidate, planner rollouts to the end of the fight. No potions.
- Decisions use only what the player can see (FP-15).

## 4. Metrics and test
- Primary: fight value (HP left after a win; -100 minus the enemies' HP left after a loss).
- Secondary: boss wins for each arm (also at Ascension 8+), search time per decision.
- Test: paired by job, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval. 60 jobs, no early stop; errors and stuck states left out of pairs and listed.
- What follows: if H1 holds, live play uses `mcw24` in boss fights (and the latency budget for boss decisions is set accordingly); if not, the boss gap needs something other than more samples (boss-specific rollout policy, deeper candidate sets, or learned evaluation), and the next study looks at where the boss losses happen.

## 5. Results
Pending.

## 6. Deviations and notes
None yet.
