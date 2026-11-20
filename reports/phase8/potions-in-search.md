# Comparison: search and planner with potions against without

Written before the run (P8.E1.S3, ML-10) on 2026-11-20 at 14:49. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypotheses
- **H1:** flat Monte Carlo search whose candidates and rollouts may drink potions (`mc6p`) gets a higher priced fight value than the same search without potions (`mc6`).
- **H2:** the rule planner with potions (`plannerp`) gets a higher priced fight value than without (`planner`).

## 2. Fights
- Benchmark set `data/sim/benchmark-v1.json` (60 fights from the Player's history; exam seeds excluded, ML-7), two sample seeds each: 120 jobs (`tools/learn/bench.py`, seed base 7000000). Potions held are those of the history spec (at most 3); fights with no usable potion play identically with and without and count as equal pairs.
- All arms play the same fight with the same run seed and sample seed in the same worker.
- Simulator header: game v0.111.1 (cc1f9462); host commit in the run's manifest; fidelity 11 of 11 recorded fights exact (`reports/phase7/fidelity.md`, 2026-11-20 13:41).

## 3. Policies and budgets
- `planner` / `plannerp`: rule planner, balanced mode; `plannerp` keeps potion slots in its hand and ranks plans with the potion cost of the room (`tools/plan_turn.py` POTION_COST: hallway 25, elite 6, boss 2 HP, [HYPOTHESIS]). Potions the planner does not model are never used.
- `mc6` / `mc6p`: flat Monte Carlo over the planner's candidates, 6 re-sampled worlds each, planner rollouts to the end of the fight; in `mc6p` candidates and rollouts may use potions, and each rollout's value subtracts the room's price per potion spent.
- Decisions use only what the player can see (FP-1, FP-15).

## 4. Metrics and test
- Primary: priced fight value = fight value (HP left after a win; -100 minus the enemies' HP left after a loss) minus the room's price for each potion used in the fight.
- Secondary: unpriced fight value, wins, potions used per room type, search time.
- Test: paired by job; one-sided sign test on better/worse pairs, significance 0.025 each (Bonferroni over H1 and H2); mean paired difference with a bootstrap 95% interval.
- Number of jobs fixed in advance: 120; no early stop. Jobs with an error or a stuck state in either arm of a pair are left out of that pair and listed.
- What follows: if H1 holds, the next self-play teacher may drink potions at these prices (and the potion price becomes its own tuning question); if not, potions stay out of search until the price or the planner's potion model is improved.

## 5. Results
Run 2026-11-20, 14:59–15:21 (`tools/learn/bench.py --report data/learn/bench/potions-1 --markdown`; manifest `data/learn/bench/potions-1/manifest.json`).

Run `potions-1`: 120 jobs, 6 workers, 1288 s wall, code `c5c54e5`, game v0.111.1 (cc1f9462).

| Arm | Won | Mean priced value | Mean value | Potions used (Monster / Elite / Boss) | Search s per decision |
|---|---|---|---|---|---|
| planner | 75 | -59.14 | -59.11 | 0 / 0 / 2 | 0.003 |
| plannerp | 81 | -55.57 | -50.67 | 16 / 26 / 16 | 0.009 |
| mc6 | 86 | -34.95 | -34.92 | 0 / 0 / 2 | 1.004 |
| mc6p | 91 | -27.89 | -24.68 | 8 / 26 / 15 | 1.640 |

| Pair (B − A), priced value | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| mc6p − mc6 | 120 | 7.06 | -0.24 to 15.78 | 26 | 24 | 70 | 0.4439 |
| plannerp − planner | 120 | 3.58 | -4.52 to 11.70 | 16 | 22 | 82 | 0.8721 |

- **H1** (`mc6p` better on priced value, sign test p < 0.025): p = 0.4439, mean difference 7.06: **does not hold**.
- **H2** (`plannerp` better on priced value, sign test p < 0.025): p = 0.8721, mean difference 3.58: **does not hold**.

Errors: 0.

**Verdict: H1 and H2 do not hold.** By the rule in section 4, potions stay out of search for now. The direction is favourable but not established: `mc6p` wins 5 more fights and gains 7.1 priced value points per fight on average (interval −0.2 to 15.8), with 70 of 120 pairs equal (fights with no usable potion or where it changed nothing); the sign test sees 26 better and 24 worse. Without the price, `mc6p` gains 10.2 value points. Worth a second test once the potion price is set from data (P8.E4) rather than the planner's hypothesis, or with more jobs.

The 2 potions "used" in boss fights by the arms without potions are automatic potions (the count is potions held at the start minus at the end).


## 6. Deviations and notes
None yet.
