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
Run 2026-11-20, 22:30–23:32 (`tools/learn/bench.py --report data/learn/bench/potions-all-1 --markdown --alpha 0.05`; manifest `data/learn/bench/potions-all-1/manifest.json`).

Run `potions-all-1`: 120 jobs, 6 workers, 4150 s wall, code `2e829d0`, game v0.111.1 (cc1f9462).

| Arm | Won | Mean priced value | Mean value | Potions used (Monster / Elite / Boss) | Search s per decision |
|---|---|---|---|---|---|
| mcw6 | 99 | -7.70 | -7.67 | 0 / 0 / 2 | 3.386 |
| mcw6pa | 97 | -12.22 | -7.33 | 11 / 45 / 21 | 5.601 |

| Pair (B − A), priced value | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| mcw6pa − mcw6 | 120 | -4.53 | -12.04 to 2.98 | 24 | 37 | 59 | 0.9639 |

- **H1** (`mcw6pa` better on priced value, sign test p < 0.05): p = 0.9639, mean difference -4.53: **does not hold**.
- Boss fights only (20 pairs): `mcw6pa` − `mcw6` 6.35 priced value (interval -9.90 to 24.10), wins 7 against 7.

Errors: 0.

At Ascension 8 and above: `mcw6pa` wins 65 of 84 fights (hallways 40/42, elites 18/22, bosses 7/20) against 67 for `mcw6` (41, 19, 7).

**Verdict: H1 does not hold; the difference leans the other way.** With every potion on offer, search drinks far more (77 potions in 120 fights, 45 of them in elites) and ends 4.5 priced value points lower (interval −12.0 to 3.0; 24 better, 37 worse); boss fights are unchanged (7 wins each). At the planner's prices (elite 6 HP, boss 2 HP per potion) the fight value rewards spending potions that a run would rather keep. By the rule in section 4, potions stay out of the default search; when to drink and when to keep is a run-level question (potion slots and prices, decision 0004), not a fight-level one.


## 6. Deviations and notes
None yet.
