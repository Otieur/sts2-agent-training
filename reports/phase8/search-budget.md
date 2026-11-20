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
Run 2026-11-20, 15:33–16:18 (`tools/learn/bench.py --report data/learn/bench/budget-1 --markdown`; manifest `data/learn/bench/budget-1/manifest.json`).

Run `budget-1`: 120 jobs, 6 workers, 2672 s wall, code `6a7d765`, game v0.111.1 (cc1f9462).

| Arm | Games | Errors | Won | Mean value | HP left after wins | Search s per decision |
|---|---|---|---|---|---|---|
| mc6 | 120 | 0 | 86 | -34.92 | 44.08 | 0.911 |
| mc12 | 120 | 0 | 85 | -32.58 | 44.65 | 1.824 |
| mc24 | 120 | 0 | 89 | -26.07 | 44.63 | 3.539 |

| Pair (B − A) | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| mc12 − mc6 | 120 | 2.33 | -5.04 to 8.77 | 33 | 21 | 66 | 0.0668 |
| mc24 − mc12 | 120 | 6.51 | 0.11 to 14.11 | 33 | 23 | 64 | 0.1144 |
| mc24 − mc6 | 120 | 8.84 | 1.15 to 16.94 | 43 | 20 | 57 | 0.0026 |

- **H1** (`mc12` better than `mc6`, sign test p < 0.025): p = 0.0668, mean difference 2.33: **does not hold**.
- **H2** (`mc24` better than `mc12`, sign test p < 0.025): p = 0.1144, mean difference 6.51: **does not hold**.

Errors: 0.

**Verdict: H1 and H2 do not hold.** Doubling the worlds per candidate buys little: 12 worlds +2.3 value per fight over 6 (interval −5.0 to 8.8), 24 worlds +6.5 over 12 (interval 0.1 to 14.1), each at twice the search time. By the rule in section 4, `mc6` stays the self-play teacher. Not a pre-registered hypothesis, so for information only: `mc24` against `mc6` is +8.8 (interval 1.2 to 16.9; 43 better, 20 worse, sign test p = 0.003) at four times the time, a reasonable setting for live play, where a few seconds per move are affordable. Wider candidate sets or better leaf evaluation look like better uses of time than more worlds.


## 6. Deviations and notes
None yet.
