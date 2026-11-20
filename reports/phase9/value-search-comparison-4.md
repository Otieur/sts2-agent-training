# Comparison 4: value-v4 (augmented data, set dropout) in search

Written before training `value-v4` and before the run (P8.E1.S3, ML-10), 2026-11-20 at 16:30. Sections 1–4 are not edited after training starts; corrections go in section 6 with the reason. Comparison 3 tests the network trained on the two plain history passes; cross-validation over runs showed that such networks memorize their training runs (mean fold error 41.8 without set dropout, 39.6 with 0.3, against 39.0 for a linear model). This comparison tests the network trained with augmented situations and set dropout.

## 1. Hypotheses
- **H1 (equal restores):** `vleaf6` with `value-v4` gets a higher fight value than `mc6`.
- **H2 (cheaper):** `vleaf2` with `value-v4` is not worse than `mc6` by more than 5 value points per fight, at most 40% of `mc6`'s search time per decision.
- **H3 (network alone):** `vgreedy` with `value-v4` gets a higher fight value than the rule planner.
- **H4 (action values):** `qpolicy` with `q-v4` gets a higher fight value than the rule planner.

## 2. Fights
- The same 120 jobs as comparisons 1 to 3: `data/sim/benchmark-v1.json`, two sample seeds each, seed base 7000000 (`tools/learn/bench.py`), so the arms that did not change (`planner`, `mc6`) can be checked against run 1.
- Training data never includes the benchmark's (source run, floor) pairs.
- Simulator: game v0.111.1 (cc1f9462); host with the pending-choice fix (clone 12 of 12, fair-play 8 of 8, fidelity 11 of 11 on this build, 15:23); fight values ignore placeholder enemy HP above 10,000.

## 3. Policies, models and budgets
- Arms as in comparison 1 (`planner`, `mc6`, `vleaf6`, `vleaf2`, `vgreedy`, `qpolicy`).
- `value-v4`: trained on `combat-v1`, `combat-v1s2` and `combat-a1s4` (the 586 history situations with seeds 1 and 2, and two augmented variants of each, a1; teacher `mc6`), encoder enc-v1.1, configuration b (card embedding 32, hidden 256, dropout 0.1, weight decay 1e-4) with set dropout 0.3 (chosen by 4-fold cross-validation over runs among 0, 0.3 and 0.5 and a smaller network), auxiliary search-estimate loss weight 5, split seed 7. Test splits read once, in the final run.
- `q-v4`: `tools/learn/train_q.py` defaults with set dropout 0.3 on the same three datasets.
- Decisions use only what the player can see (FP-1, FP-15); networks read the observation encoder only (FP-10). No potions in any arm.

## 4. Metrics and test
- Primary: fight value (HP left after a win; -100 minus the enemies' HP left after a loss).
- H1, H3, H4: paired by job, one-sided sign test, significance 0.0167 each (Bonferroni over three directional tests); mean paired difference with a bootstrap 95% interval. H2: lower end of the bootstrap 95% interval of (`vleaf2` − `mc6`) above −5, and time ratio at most 0.4.
- Jobs with an error or a stuck state in an arm are left out of that arm's pairs and listed. 120 jobs, no early stop.
- What follows: if H1 holds, `vleaf6` becomes the next teacher; if only H2 holds, `vleaf2` does; if H4 holds, `qpolicy` becomes the fast fallback policy for live play and the candidate prior for search. Otherwise `mc6` stays the teacher.

## 5. Results
Run 2026-11-20, 17:04–17:16 (`tools/learn/bench.py --report data/learn/bench/vsearch-4 --markdown --alpha 0.0167 --h4`; manifest `data/learn/bench/vsearch-4/manifest.json`).

Run `vsearch-4`: 120 jobs, 6 workers, 715 s wall, code `d5fb903`, game v0.111.1 (cc1f9462), model `models/value-v4/model.pt`, action-value model `models/q-v4/model.pt`.

| Arm | Games | Errors | Won | Mean value | HP left after wins | Search s per decision | Host restarts |
|---|---|---|---|---|---|---|---|
| planner | 120 | 0 | 75 | -59.11 | 43.51 | 0.003 | 0 |
| mc6 | 120 | 0 | 86 | -34.92 | 44.08 | 0.917 | 0 |
| vleaf6 | 120 | 0 | 68 | -67.03 | 43.57 | 0.469 | 0 |
| vleaf2 | 120 | 0 | 73 | -62.97 | 41.89 | 0.181 | 0 |
| vgreedy | 120 | 0 | 66 | -77.19 | 44.27 | 0.068 | 0 |
| qpolicy | 120 | 0 | 81 | -50.34 | 42.49 | 0.010 | 0 |

| Pair (B − A) | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| vleaf6 − mc6 | 120 | -32.11 | -45.02 to -19.65 | 27 | 75 | 18 | 1.0000 |
| vleaf2 − mc6 | 120 | -28.05 | -40.43 to -15.82 | 31 | 78 | 11 | 1.0000 |
| vgreedy − planner | 120 | -18.08 | -31.93 to -4.13 | 43 | 65 | 12 | 0.9868 |
| mc6 − planner | 120 | 24.19 | 13.58 to 35.62 | 75 | 21 | 24 | 0.0000 |
| vgreedy − mc6 | 120 | -42.27 | -56.21 to -28.92 | 23 | 88 | 9 | 1.0000 |
| qpolicy − planner | 120 | 8.77 | -4.86 to 22.71 | 58 | 50 | 12 | 0.2504 |
| qpolicy − mc6 | 120 | -15.43 | -27.12 to -4.75 | 38 | 66 | 16 | 0.9979 |

- **H1** (`vleaf6` better than `mc6`, sign test p < 0.0167): p = 1.0000, mean difference -32.11: **does not hold**.
- **H2** (`vleaf2` not worse than `mc6` by more than 5, lower bound > −5, time ratio ≤ 0.4): lower bound -40.43, time ratio 0.20: **does not hold**.
- **H3** (`vgreedy` better than `planner`, sign test p < 0.0167): p = 0.9868, mean difference -18.08: **does not hold**.
- **H4** (`qpolicy` better than `planner`, sign test p < 0.0167): p = 0.2504, mean difference 8.77: **does not hold**.

Jobs left out of pairs: 0 errors, 0 blocked.

Mean value by room type: Monster planner 33.9, mc6 40.1, vleaf6 29.6, vleaf2 29.8, vgreedy 32.0, qpolicy 37.6; Elite planner -100.2, mc6 -53.6, vleaf6 -107.7, vleaf2 -101.3, vgreedy -134.1, qpolicy -88.0; Boss planner -255.8, mc6 -222.8, vleaf6 -275.4, vleaf2 -264.4, vgreedy -290.8, qpolicy -238.8

**Verdict: H1–H4 all fail**, but every arm moved the right way against comparison 3: `vleaf6` −32 against `mc6` (was −45), `vleaf2` −28 (was −41), `vgreedy` −18 against the planner (was −28), `qpolicy` +8.8 against the planner with 81 wins (was +0.7 with 73), at 10 ms per move. On held-out runs `value-v4` now matches the linear model (value error 39.9 against 38.1; `value-v3` was 64.0 against 36.5), so augmentation and set dropout largely cured the memorization; the network is still well short of six rollouts (18.6). `mc6` stays the teacher for the plain line; the wide-candidate result (`reports/phase8/wide-candidates.md`) already made `mcw6` the teacher for new data.


## 6. Deviations and notes
None yet.
