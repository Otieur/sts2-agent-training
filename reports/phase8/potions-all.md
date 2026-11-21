# Comparison: every usable potion as a search candidate

Written before the run (P8.E1.S3, ML-10), 2026-11-20 at 22:30. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** wide search in which every usable potion is a candidate (`mcw6pa`: one candidate per distinct potion and target, on top of the card candidates, judged by simulation and priced by room) gets a higher priced fight value than wide search without potions (`mcw6`).

Why: in `potions-wide.md` the search could drink only the potions proposed by the planner's potion model, which knows 17 potion types, covering 58% of the potions held across the history situations (unknown to it: Power Potion, Blessing of the Forge, Attack Potion, Fairy in a Bottle and others). That arm added +3.3 priced value (not significant). Judging every potion by simulation needs no potion model.

## 2. Fights
- Benchmark set `data/sim/benchmark-v1.json`, two seeds per fight, seed base 7000000: the same 120 jobs as before. Potions held are the history spec's (at most 3). Known limit of the benchmark, which applies to every arm: the situations lack card enchantments and relics removed earlier in the run.
- Simulator: game v0.111.1 (cc1f9462); host with the pending-choice fix; fight values ignore placeholder enemy HP above 10,000.

## 3. Policies and budgets
- `mcw6`: wide candidates (cap 8), 6 worlds each, planner rollouts, no potions.
- `mcw6pa`: the same card candidates plus every usable potion; rollouts may drink the potions the planner models; each rollout's value subtracts the room's price per potion spent (hallway 25, elite 6, boss 2 HP).
- Decisions use only what the player can see (FP-15).

## 4. Metrics and test
- Primary: priced fight value. Secondary: wins, potions used per room, boss fights on their own, search time.
- Test: paired by job, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval. 120 jobs, no early stop.
- What follows: if H1 holds, every-potion candidates join the default search and the teacher; if not, potion pricing (P8.E4) is the next question before potions are tried again.

## 5. Results
Pending.

## 6. Deviations and notes
None yet.
