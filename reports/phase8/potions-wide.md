# Comparison: potions in wide search

Written before the run (P8.E1.S3, ML-10), 2026-11-20 at 17:30. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** wide search that may drink potions (`mcw6p`) gets a higher priced fight value than the same search without potions (`mcw6`).

Why now: on the 60 benchmark fights the Player's own recorded results at Ascension 8 and above are 86% fights won (elites 100%, bosses 40%) against 80% for `mcw6` (elites 86%, bosses 35%), and the Player used potions while no search arm does. The first potion comparison (`potions-in-search.md`, planner candidates) was favourable but not significant (+7.1 priced value, interval −0.2 to 15.8).

## 2. Fights
- Benchmark set `data/sim/benchmark-v1.json`, two sample seeds per fight, seed base 7000000: the same 120 jobs as the earlier comparisons. Potions held are the history spec's (at most 3). Exam seeds excluded (ML-7).
- Simulator: game v0.111.1 (cc1f9462); host with the pending-choice fix; fight values ignore placeholder enemy HP above 10,000.

## 3. Policies and budgets
- `mcw6`: flat Monte Carlo over the wide candidate set (the planner's candidates plus every other distinct legal card play, cap 8), 6 re-sampled worlds each, planner rollouts.
- `mcw6p`: the same, with the planner's potion-using candidates and potion use in rollouts; each rollout's value subtracts the room's potion price per potion spent (planner potion cost: hallway 25, elite 6, boss 2 HP, [HYPOTHESIS]). Wide candidates add card plays only; potion candidates come from the planner's plans.
- Decisions use only what the player can see (FP-15).

## 4. Metrics and test
- Primary: priced fight value (fight value minus the room's price per potion used in the fight).
- Secondary: wins, unpriced value, potions used per room, the boss fights on their own (20 pairs), search time.
- Test: paired by job, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval. 120 jobs, no early stop; errors and stuck states left out of pairs and listed.
- What follows: if H1 holds, potions join the default search (teacher and live play) at these prices, and the price itself becomes the next question (P8.E4); if not, potions stay out and the boss-fight gap is studied on its own.

## 5. Results
Pending.

## 6. Deviations and notes
None yet.
