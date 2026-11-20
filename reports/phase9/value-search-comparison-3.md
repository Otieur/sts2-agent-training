# Comparison 3: value-v3 in search against the flat Monte Carlo teacher

Written before the final training of `value-v3` and before the run (P8.E1.S3, ML-10), 2026-11-20 at 15:30. Sections 1–4 are not edited after the final training starts; corrections go in section 6 with the reason. Comparisons 1 and 2 used networks trained on data corrupted by the Waterfall Giant's placeholder HP (about 10^9, which reached the features and the search targets); this one uses the fixed encoder (enc-v1.1) and targets. The weight selection runs below were made on the validation split before this was written (their numbers: weight 0 → 21.2, 2 → 21.0, 5 → 19.7 validation error); the test splits and the benchmark have not been looked at with any enc-v1.1 network.

## 1. Hypotheses
- **H1 (equal restores):** `vleaf6` with `value-v3` gets a higher fight value than `mc6`.
- **H2 (cheaper):** `vleaf2` with `value-v3` is not worse than `mc6` by more than 5 value points per fight, at most 40% of `mc6`'s search time per decision.
- **H3 (network alone):** `vgreedy` with `value-v3` gets a higher fight value than the rule planner.
- **H4 (action values):** `qpolicy` with `q-v3` gets a higher fight value than the rule planner.

## 2. Fights
- The same 120 jobs as comparisons 1 and 2: `data/sim/benchmark-v1.json`, two sample seeds each, seed base 7000000 (`tools/learn/bench.py`), so the arms that did not change (`planner`, `mc6`) can be checked against run 1.
- Training data never includes the benchmark's (source run, floor) pairs.
- Simulator: game v0.111.1 (cc1f9462); host with the pending-choice fix (clone 12 of 12, fair-play 8 of 8, fidelity 11 of 11 on this build, 15:23); fight values ignore placeholder enemy HP above 10,000.

## 3. Policies, models and budgets
- Arms as in comparison 1 (`planner`, `mc6`, `vleaf6`, `vleaf2`, `vgreedy`, `qpolicy`).
- `value-v3`: trained on `combat-v1` and `combat-v1s2` (586 history fights with seeds 1 and 2, teacher `mc6`) with encoder enc-v1.1 and the corrected targets, configuration b (card embedding 32, hidden 256, dropout 0.1, weight decay 1e-4), split seed 7, auxiliary search-estimate loss with weight 5 (the lowest validation error of 0, 2 and 5). Test splits read once, in the final run.
- `q-v3`: `tools/learn/train_q.py` defaults on the same two datasets with enc-v1.1.
- Decisions use only what the player can see (FP-1, FP-15); networks read the observation encoder only (FP-10). No potions in any arm.

## 4. Metrics and test
- Primary: fight value (HP left after a win; -100 minus the enemies' HP left after a loss).
- H1, H3, H4: paired by job, one-sided sign test, significance 0.0167 each (Bonferroni over three directional tests); mean paired difference with a bootstrap 95% interval. H2: lower end of the bootstrap 95% interval of (`vleaf2` − `mc6`) above −5, and time ratio at most 0.4.
- Jobs with an error or a stuck state in an arm are left out of that arm's pairs and listed. 120 jobs, no early stop.
- What follows: if H1 holds, `vleaf6` becomes the next teacher; if only H2 holds, `vleaf2` does; if H4 holds, `qpolicy` becomes the fast fallback policy for live play and the candidate prior for search. Otherwise `mc6` stays the teacher.

## 5. Results
Run 2026-11-20, 16:18–16:32 (`tools/learn/bench.py --report data/learn/bench/vsearch-3 --markdown --alpha 0.0167 --h4`; manifest `data/learn/bench/vsearch-3/manifest.json`).

Run `vsearch-3`: 120 jobs, 6 workers, 845 s wall, code `a82897e`, game v0.111.1 (cc1f9462), model `models/value-v3/model.pt`, action-value model `models/q-v3/model.pt`.

| Arm | Games | Errors | Won | Mean value | HP left after wins | Search s per decision | Host restarts |
|---|---|---|---|---|---|---|---|
| planner | 120 | 0 | 75 | -59.11 | 43.51 | 0.003 | 0 |
| mc6 | 120 | 0 | 86 | -34.92 | 44.08 | 1.086 | 0 |
| vleaf6 | 120 | 0 | 64 | -80.40 | 44.44 | 0.598 | 0 |
| vleaf2 | 120 | 0 | 65 | -76.36 | 43.32 | 0.211 | 0 |
| vgreedy | 120 | 0 | 64 | -87.48 | 39.38 | 0.086 | 0 |
| qpolicy | 120 | 0 | 73 | -58.38 | 44.01 | 0.009 | 0 |

| Pair (B − A) | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| vleaf6 − mc6 | 120 | -45.48 | -59.43 to -32.07 | 25 | 86 | 9 | 1.0000 |
| vleaf2 − mc6 | 120 | -41.44 | -55.51 to -28.34 | 25 | 87 | 8 | 1.0000 |
| vgreedy − planner | 120 | -28.38 | -44.07 to -12.58 | 27 | 86 | 7 | 1.0000 |
| mc6 − planner | 120 | 24.19 | 13.70 to 35.92 | 75 | 21 | 24 | 0.0000 |
| vgreedy − mc6 | 120 | -52.57 | -67.59 to -37.69 | 19 | 98 | 3 | 1.0000 |
| qpolicy − planner | 120 | 0.73 | -13.11 to 14.51 | 52 | 53 | 15 | 0.5773 |
| qpolicy − mc6 | 120 | -23.46 | -35.79 to -12.22 | 29 | 76 | 15 | 1.0000 |

- **H1** (`vleaf6` better than `mc6`, sign test p < 0.0167): p = 1.0000, mean difference -45.48: **does not hold**.
- **H2** (`vleaf2` not worse than `mc6` by more than 5, lower bound > −5, time ratio ≤ 0.4): lower bound -55.51, time ratio 0.19: **does not hold**.
- **H3** (`vgreedy` better than `planner`, sign test p < 0.0167): p = 1.0000, mean difference -28.38: **does not hold**.
- **H4** (`qpolicy` better than `planner`, sign test p < 0.0167): p = 0.5773, mean difference 0.73: **does not hold**.

Jobs left out of pairs: 0 errors, 0 blocked.

Mean value by room type: Monster planner 33.9, mc6 40.1, vleaf6 26.4, vleaf2 25.1, vgreedy 7.4, qpolicy 37.0; Elite planner -100.2, mc6 -53.6, vleaf6 -128.3, vleaf2 -121.6, vgreedy -129.4, qpolicy -99.8; Boss planner -255.8, mc6 -222.8, vleaf6 -305.2, vleaf2 -290.1, vgreedy -288.3, qpolicy -261.4

**Verdict: H1–H4 all fail.** `mc6` stays the teacher. With the placeholder-HP fix the network improved a great deal (`vgreedy` −28 against the planner, from −115 with `value-v2`; `vleaf2` −41 against `mc6`, from −65), but leaves scored by the network still lose clearly to rollouts. `vleaf6` is no better than `vleaf2`: more sampled worlds do not help, so the leaf judgement itself is biased, which matches the cross-validation finding that the network does not generalize to unseen runs better than a linear model. `qpolicy` (`q-v3`) is level with the planner (+0.7).


## 6. Deviations and notes
None yet.
