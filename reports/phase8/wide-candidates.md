# Comparison: wider candidate sets for search

Written before the run (P8.E1.S3, ML-10), 2026-11-20 at 16:30. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** flat Monte Carlo over a wider candidate set (`mcw6`: the planner's candidates plus every other legal card play, one per distinct card and target, at most 8 candidates) gets a higher fight value than flat Monte Carlo over the planner's candidates alone (`mc6`).

The search-budget comparison (`search-budget.md`) found that more worlds per candidate add little; this tests whether the planner's candidate list, not the evaluation, is what limits search.

## 2. Fights
- Benchmark set `data/sim/benchmark-v1.json` (60 fights from real runs), two sample seeds per fight, seed base 7000000: the same 120 jobs as the earlier comparisons. Exam seeds excluded (ML-7).
- Simulator: game v0.111.1 (cc1f9462); host with the pending-choice fix (clone 12 of 12 exact, fair-play 8 of 8, fidelity 11 of 11 on this build); fight values ignore placeholder enemy HP above 10,000.

## 3. Policies and budgets
- `mc6`: candidates = first actions of the planner's top 2 plans in safe and balanced modes plus ending the turn; 6 re-sampled worlds each; planner rollouts to the end of the fight.
- `mcw6`: the same, with candidates from `tools/sim.py search_candidates_wide` (cap 8). Card choices and potions are handled as in `mc6` (choices by the planner, no potions).
- `planner`: reference only.
- Decisions use only what the player can see (FP-15).

## 4. Metrics and test
- Primary: fight value (HP left after a win; -100 minus the enemies' HP left after a loss).
- Secondary: wins, search seconds per decision (the cost ratio of `mcw6` to `mc6` is reported).
- Test: paired by job; one-sided sign test, significance 0.05; mean paired difference with a bootstrap 95% interval. 120 jobs, no early stop; errors and stuck states left out of pairs and listed.
- What follows: if H1 holds, wide candidates become the default for self-play and live search, and the action-value network is tried as a filter to keep their cost down; if not, the planner's candidates stay and effort goes to leaf evaluation.

## 5. Results
Run 2026-11-20, 16:32–16:56 (`data/learn/bench/wide-1/manifest.json`; paired statistics from `tools/learn/bench.py` `paired`).

Run `wide-1`: 120 jobs, 6 workers, 1404 s wall, code `80d9849`, game v0.111.1 (cc1f9462).

| Arm | Games | Errors | Won | Mean value | HP left after wins | Search s per decision |
|---|---|---|---|---|---|---|
| planner | 120 | 0 | 75 | -59.11 | 43.51 | 0.003 |
| mc6 | 120 | 0 | 86 | -34.92 | 44.08 | 1.051 |
| mcw6 | 120 | 0 | 99 | -7.67 | 44.45 | 2.049 |

| Pair (B − A) | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| mcw6 − mc6 | 120 | 27.25 | 17.23 to 38.32 | 68 | 20 | 32 | 1.4e-07 |
| mc6 − planner | 120 | 24.19 | 13.56 to 35.48 | 75 | 21 | 24 | 1.4e-08 |
| mcw6 − planner | 120 | 51.44 | 36.07 to 68.13 | 90 | 20 | 10 | 4.3e-12 |

- **H1** (`mcw6` better than `mc6`, sign test p < 0.05): p = 1.4e-07, mean difference 27.25: **holds**.

Mean value by room type: Monster planner 33.9, mc6 40.1, mcw6 50.0; Elite planner -100.2, mc6 -53.6, mcw6 -4.0; Boss planner -255.8, mc6 -222.8, mcw6 -187.9

Search time per decision: `mcw6` 2.05 s against `mc6` 1.05 s (ratio 1.95).

**Verdict: H1 holds, by a wide margin.** Searching every distinct legal card play instead of only the planner's own candidates adds 27 value points per fight (68 better, 20 worse) and 13 wins (99 against 86), for twice the search time. The gain is largest in elite fights (mean value −4.0 against −53.6). Compare the search-budget comparison: four times the worlds per candidate added only about 9. The planner's candidate list, not the rollout evaluation, was what limited search. By the rule in section 4, wide candidates become the default for self-play (`tools/selfplay.py --wide`) and live search, and the action-value network will be tried as a filter to keep the cost down.


## 6. Deviations and notes
None yet.
