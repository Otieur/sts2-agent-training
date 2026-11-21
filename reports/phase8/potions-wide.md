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
Run 2026-11-20, 20:50–21:30 (`tools/learn/bench.py --report data/learn/bench/potions-wide-1 --markdown --alpha 0.05`; manifest `data/learn/bench/potions-wide-1/manifest.json`).

Run `potions-wide-1`: 120 jobs, 6 workers, 2370 s wall, code `785305f`, game v0.111.1 (cc1f9462).

| Arm | Won | Mean priced value | Mean value | Potions used (Monster / Elite / Boss) | Search s per decision |
|---|---|---|---|---|---|
| mcw6 | 99 | -7.70 | -7.67 | 0 / 0 / 2 | 1.883 |
| mcw6p | 101 | -4.38 | -2.23 | 3 / 25 / 17 | 3.034 |

| Pair (B − A), priced value | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| mcw6p − mcw6 | 120 | 3.32 | -1.45 to 9.14 | 22 | 28 | 70 | 0.8389 |

- **H1** (`mcw6p` better on priced value, sign test p < 0.05): p = 0.8389, mean difference 3.32: **does not hold**.
- Boss fights only (20 pairs): `mcw6p` − `mcw6` 8.30 priced value (interval -8.90 to 27.45), wins 7 against 7.

Errors: 0.

At Ascension 8 and above: `mcw6p` wins 82% of fights (hallways 98%, elites 95%, bosses 35%) against 80% for `mcw6` (98%, 86%, 35%); the Player's own results on the same fights are 86% (100%, 100%, 40%).

**Verdict: H1 does not hold.** Potions add +3.3 priced value per fight (interval −1.5 to 9.1; 22 better, 28 worse, 70 equal) and two wins, mostly in elite fights, but nothing in boss fights (7 wins each). By the rule in section 4, potions stay out of the default search and the boss-fight gap is studied on its own.


## 6. Deviations and notes
None yet.
