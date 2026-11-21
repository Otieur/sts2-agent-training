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
Run 2026-11-20, 21:35–22:18 (`data/learn/bench/boss-budget-1/manifest.json`; paired statistics from `tools/learn/bench.py` `paired`).

Run `boss-budget-1`: 60 jobs (10 boss fights × 6 seeds), 6 workers, 2785 s wall, code `11aff51`, game v0.111.1 (cc1f9462).

| Arm | Games | Errors | Won | Mean value | HP left after wins | Search s per decision |
|---|---|---|---|---|---|---|
| mcw6 | 60 | 0 | 21 | -165.73 | 30.90 | 1.883 |
| mcw24 | 60 | 0 | 25 | -146.77 | 33.88 | 7.191 |

| Pair (B − A) | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| mcw24 − mcw6 | 60 | 18.97 | 4.63 to 35.62 | 30 | 22 | 8 | 0.1659 |

- **H1** (`mcw24` better than `mcw6`, sign test p < 0.05): p = 0.1659, mean difference 18.97: **does not hold**.

Per boss fight, with the Player's own result in the recorded run (one try, with the potions held):

| Boss | Act | Asc. | HP at start | Potions held | Player (one try) | `mcw6` | `mcw24` |
|---|---|---|---|---|---|---|---|
| CEREMONIAL_BEAST_BOSS | 1 | 10 | 68/80 | 2 | won | 6/6 | 6/6 |
| LAGAVULIN_MATRIARCH_BOSS | 1 | 8 | 37/67 | 0 | lost | 0/6 | 0/6 |
| LAGAVULIN_MATRIARCH_BOSS | 1 | 10 | 75/90 | 0 | won | 6/6 | 6/6 |
| VANTOM_BOSS | 1 | 9 | 52/87 | 1 | lost | 3/6 | 4/6 |
| KNOWLEDGE_DEMON_BOSS | 2 | 10 | 59/80 | 2 | lost | 0/6 | 0/6 |
| KNOWLEDGE_DEMON_BOSS | 2 | 10 | 80/80 | 3 | won | 0/6 | 3/6 |
| THE_INSATIABLE_BOSS | 2 | 10 | 85/85 | 0 | lost | 6/6 | 6/6 |
| QUEEN_BOSS | 3 | 8 | 64/101 | 3 | lost | 0/6 | 0/6 |
| QUEEN_BOSS | 3 | 10 | 42/80 | 1 | lost | 0/6 | 0/6 |
| TEST_SUBJECT_BOSS | 3 | 10 | 53/80 | 3 | won | 0/6 | 0/6 |

**Verdict: H1 does not hold** by the pre-registered sign test (30 better, 22 worse, p = 0.17), although the mean difference is +19 value per fight with a bootstrap interval of 4.6 to 35.6 that excludes zero: more worlds help somewhat, mostly by losing closer and winning with more HP, not by turning losses into wins (25 wins against 21).

What the per-fight table shows: boss outcomes are decided mostly by the situation, not by the search budget. Six of ten fights go the same way in every seed for both arms. Over the ten fights, `mcw24` wins 4.2 on average and `mcw6` 3.5, against 4 for the Player. Wide search wins two fights the Player lost (The Insatiable 6 of 6, Vantom 4 of 6) and loses two the Player won, both with three potions in hand (Knowledge Demon at full HP 3 of 6, Test Subject 0 of 6); both sides lose both Queen fights, the low-HP Lagavulin Matriarch and the low-HP Knowledge Demon. The earlier "35% against 40%" at A8+ came from two seeds per fight and was too coarse. The gap is potion use in the boss fights where the Player had a full belt; the planner's potion model (which potions it understands and when it drinks them) is the next thing to examine.


## 6. Deviations and notes
None yet.
