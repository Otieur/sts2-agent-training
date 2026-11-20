# Comparison: search and planner with potions against without

Written before the run (P8.E1.S3, ML-10) on 2026-11-20 at 14:52. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

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
Pending.

## 6. Deviations and notes
None yet.
