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
Pending.

## 6. Deviations and notes
None yet.
