# Comparison: returns to search budget (worlds per candidate)

Written before the run (P8.E1.S3, ML-10), 2026-11-20 at 15:26. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypotheses
- **H1:** flat Monte Carlo with 12 re-sampled worlds per candidate (`mc12`) gets a higher fight value than with 6 (`mc6`, the current self-play teacher).
- **H2:** 24 worlds (`mc24`) gets a higher fight value than 12 (`mc12`).

## 2. Fights
- Benchmark set `data/sim/benchmark-v1.json`, two sample seeds per fight, seed base 7000000: the same 120 jobs as the value-search comparisons, so `mc6` can be checked against those runs.
- Simulator: game v0.111.1 (cc1f9462); host with the pending-choice fix (clone 12 of 12 exact, fair-play 8 of 8, fidelity 11 of 11 on this build, 2026-11-20 15:23); fight values ignore placeholder enemy HP above 10,000 (Waterfall Giant).

## 3. Policies and budgets
- `mc6`, `mc12`, `mc24`: flat Monte Carlo over the planner's candidates (top 2 plans per mode plus ending the turn), k re-sampled worlds each, planner rollouts to the end of the fight, shared sample seeds across candidates. No potions. Decisions use only what the player can see (FP-15).

## 4. Metrics and test
- Primary: fight value (HP left after a win; -100 minus the enemies' HP left after a loss).
- Secondary: wins, search seconds per decision.
- Test: paired by job; one-sided sign test, significance 0.025 each (two directional tests); mean paired difference with a bootstrap 95% interval. 120 jobs, no early stop; errors and stuck states left out of pairs and listed.
- What follows: if H1 holds, the next self-play teacher is `mc12` (about twice the cost per decision); if H2 also holds, `mc24` is considered for the benchmark's reference policy and for live play, where time is less tight than in data generation.

## 5. Results
Pending.

## 6. Deviations and notes
None yet.
