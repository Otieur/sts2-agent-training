# Comparison 5: action-value filter for wide search, and the fast policy (v5 networks)

Written before training `value-v5` and `q-v5` and before the run (P8.E1.S3, ML-10), 2026-11-20 at 21:00. Sections 1–4 are not edited after training starts; corrections go in section 6 with the reason.

## 1. Hypotheses
- **H1 (filter keeps strength at lower cost):** wide search whose candidates are cut to 4 by `q-v5` (`mcwq6`: the planner's own candidates and ending the turn always kept) is not worse than full wide search (`mcw6`) by more than 5 value points per fight, at most 75% of `mcw6`'s search time per decision.
- **H2 (fast policy):** `qpolicy` with `q-v5` gets a higher fight value than the rule planner.

Tracked, not tested: `vleaf2` with `value-v5` against `mc6` (the value-network line of comparisons 1–4).

## 2. Fights
- Benchmark set `data/sim/benchmark-v1.json`, two sample seeds per fight, seed base 7000000: the same 120 jobs as before. Exam seeds excluded (ML-7); training never includes the benchmark's (source run, floor) pairs.
- Simulator: game v0.111.1 (cc1f9462); host with the pending-choice fix; fight values ignore placeholder enemy HP above 10,000.

## 3. Policies, models and budgets
- `mcw6`: flat Monte Carlo over the wide candidate set (cap 8), 6 worlds each, planner rollouts.
- `mcwq6`: the same search over at most 4 candidates chosen as described in H1, by `q-v5`.
- `qpolicy`: `q-v5` scores the planner's candidates; no simulation.
- `planner`, `mc6`: references; `vleaf2`: tracked.
- Data for both networks: `combat-v1`, `combat-v1s2`, `combat-a1s4` (teacher `mc6`, planner candidates) and `combat-r1w` (situations from simulated runs) and `combat-a2w` (augmented history situations), both with the wide teacher `mcw6`, each completed and with failed fights replayed before training. Simulated-run sources stay in the training split; held-out splits are the Player's history runs.
- `value-v5`: configuration b with set dropout 0.3 and auxiliary search-estimate weight 5 (as `value-v4`). `q-v5`: `tools/learn/train_q.py` defaults with set dropout 0.3. Test splits read once.
- Decisions use only what the player can see (FP-15); networks read the observation encoder only (FP-10). No potions in any arm (potions are tested separately in `reports/phase8/potions-wide.md`).

## 4. Metrics and test
- Primary: fight value (HP left after a win; -100 minus the enemies' HP left after a loss).
- H1: lower end of the bootstrap 95% interval of (`mcwq6` − `mcw6`) above −5, and the time ratio at most 0.75. H2: one-sided sign test at 0.05.
- Jobs with an error or a stuck state are left out of that arm's pairs and listed. 120 jobs, no early stop.
- What follows: if H1 holds, `mcwq6` becomes the live-play search (it fits the latency budget better) and the self-play teacher; if H2 holds, `qpolicy` is the fallback when time is short and the rollout policy to try inside search.

## 5. Results
Pending.

## 6. Deviations and notes
None yet.
