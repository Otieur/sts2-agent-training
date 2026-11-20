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
Pending.

## 6. Deviations and notes
None yet.
