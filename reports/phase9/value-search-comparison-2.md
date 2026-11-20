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
Pending.

## 6. Deviations and notes
None yet.
