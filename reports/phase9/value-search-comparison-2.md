# Comparison 2: value-v2 in search against the flat Monte Carlo teacher

Written before training `value-v2` and before the run (P8.E1.S3, ML-10), 2026-11-20 at 15:05. Sections 1–4 are not edited after training starts; corrections go in section 6 with the reason. The first comparison (`value-search-comparison.md`) failed all three hypotheses; this one tests the network trained with the fix found after it.

## 1. Hypotheses
- **H1 (equal restores):** `vleaf6` with `value-v2` gets a higher fight value than `mc6`.
- **H2 (cheaper):** `vleaf2` with `value-v2` is not worse than `mc6` by more than 5 value points per fight, at most 40% of `mc6`'s search time per decision.
- **H3 (network alone):** `vgreedy` with `value-v2` gets a higher fight value than the rule planner.
- **H4 (action values):** `qpolicy` with `q-v2` gets a higher fight value than the rule planner.

## 2. Fights
- The same 120 jobs as comparison 1: `data/sim/benchmark-v1.json`, two sample seeds each, seed base 7000000 (`tools/learn/bench.py`), so the arms that did not change (`planner`, `mc6`) can be checked against run 1.
- Training data never includes the benchmark's (source run, floor) pairs.
- Simulator: game v0.111.1 (cc1f9462); host rebuilt with the pending-choice fix (`Session.Unwind`) before the run; commit in the manifest; fidelity, clone and fair-play checks rerun on that build before the run.

## 3. Policies, models and budgets
- Arms as in comparison 1 (`planner`, `mc6`, `vleaf6`, `vleaf2`, `vgreedy`, `qpolicy`).
- `value-v2`: trained on `combat-v1` and `combat-v1s2` (the same 586 history fights with seeds 1 and 2, teacher `mc6`), configuration b (card embedding 32, hidden 256, dropout 0.1, weight decay 1e-4), split seed 7. Auxiliary loss toward the stored search estimate with weight chosen among 1, 2 and 5 by the validation value error against realized outcomes (the validation loss is not comparable across weights). Test splits read once, after the choice.
- `q-v2`: `tools/learn/train_q.py` defaults on the same two datasets.
- Decisions use only what the player can see (FP-1, FP-15); networks read the observation encoder only (FP-10). No potions in any arm.

## 4. Metrics and test
- Primary: fight value (HP left after a win; -100 minus the enemies' HP left after a loss).
- H1, H3, H4: paired by job, one-sided sign test, significance 0.0167 each (Bonferroni over three directional tests); mean paired difference with a bootstrap 95% interval. H2: lower end of the bootstrap 95% interval of (`vleaf2` − `mc6`) above −5, and time ratio at most 0.4.
- Jobs with an error or a stuck state in an arm are left out of that arm's pairs and listed. 120 jobs, no early stop.
- What follows: if H1 holds, `vleaf6` becomes the next teacher; if only H2 holds, `vleaf2` does; if H4 holds, `qpolicy` becomes the fast fallback policy for live play and the candidate prior for search. Otherwise `mc6` stays the teacher.

## 5. Results
Run 2026-11-20, 15:23–15:33 (`tools/learn/bench.py --report data/learn/bench/vsearch-2 --markdown --alpha 0.0167 --h4`; manifest `data/learn/bench/vsearch-2/manifest.json`).

Run `vsearch-2`: 120 jobs, 6 workers, 594 s wall, code `aa6805c`, game v0.111.1 (cc1f9462), model `models/value-v2/model.pt`, action-value model `models/q-v2/model.pt`.

| Arm | Games | Errors | Won | Mean value | HP left after wins | Search s per decision | Host restarts |
|---|---|---|---|---|---|---|---|
| planner | 120 | 0 | 75 | -59.11 | 43.51 | 0.003 | 0 |
| mc6 | 120 | 0 | 86 | -34.92 | 44.08 | 0.783 | 0 |
| vleaf6 | 120 | 0 | 63 | -88.81 | 36.40 | 0.384 | 0 |
| vleaf2 | 120 | 0 | 58 | -99.59 | 34.21 | 0.148 | 0 |
| vgreedy | 120 | 0 | 24 | -174.19 | 26.21 | 0.060 | 0 |
| qpolicy | 120 | 0 | 78 | -53.11 | 41.78 | 0.007 | 0 |

| Pair (B − A) | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| vleaf6 − mc6 | 120 | -53.89 | -68.28 to -40.12 | 14 | 95 | 11 | 1.0000 |
| vleaf2 − mc6 | 120 | -64.67 | -80.34 to -49.83 | 17 | 91 | 12 | 1.0000 |
| vgreedy − planner | 120 | -115.08 | -131.72 to -98.35 | 9 | 110 | 1 | 1.0000 |
| mc6 − planner | 120 | 24.19 | 13.48 to 35.52 | 75 | 21 | 24 | 0.0000 |
| vgreedy − mc6 | 120 | -139.28 | -157.59 to -121.27 | 5 | 113 | 2 | 1.0000 |
| qpolicy − planner | 120 | 6.00 | -5.58 to 18.05 | 53 | 57 | 10 | 0.6831 |
| qpolicy − mc6 | 120 | -18.19 | -27.61 to -9.03 | 24 | 79 | 17 | 1.0000 |

- **H1** (`vleaf6` better than `mc6`, sign test p < 0.0167): p = 1.0000, mean difference -53.89: **does not hold**.
- **H2** (`vleaf2` not worse than `mc6` by more than 5, lower bound > −5, time ratio ≤ 0.4): lower bound -80.34, time ratio 0.19: **does not hold**.
- **H3** (`vgreedy` better than `planner`, sign test p < 0.0167): p = 1.0000, mean difference -115.08: **does not hold**.
- **H4** (`qpolicy` better than `planner`, sign test p < 0.0167): p = 0.6831, mean difference 6.00: **does not hold**.

Jobs left out of pairs: 0 errors, 0 blocked.

Mean value by room type: Monster planner 33.9, mc6 40.1, vleaf6 10.2, vleaf2 -6.0, vgreedy -85.3, qpolicy 33.8; Elite planner -100.2, mc6 -53.6, vleaf6 -130.6, vleaf2 -129.5, vgreedy -209.2, qpolicy -87.6; Boss planner -255.8, mc6 -222.8, vleaf6 -302.4, vleaf2 -320.5, vgreedy -370.6, qpolicy -244.7

**Verdict: H1–H4 all fail.** `mc6` stays the teacher. `value-v2` did worse than `value-v1` (`vgreedy` −115 against the planner). As found while this run was going (section 6), its training data carried the Waterfall Giant's placeholder HP into features and targets, so this comparison mostly measures that defect; comparison 3 repeats it with the fixed data.


## 6. Deviations and notes
- Found during the run (15:23): the Waterfall Giant's HP becomes about 10^9 once its 240 HP are gone; the encoder passed that into the features and the search values stored with the data reached −10^8, which made `value-v2`'s training unstable (the erratic selection errors 62.6, 101.3, 48.0). The run was not stopped; the model was fixed by the pre-registered procedure before the defect was known.
