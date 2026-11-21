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
Run 2026-11-21, 00:47–01:29 (`tools/learn/bench.py --report data/learn/bench/vsearch-5b --baseline mcw6`; manifest `data/learn/bench/vsearch-5b/manifest.json`).

Run `vsearch-5b`: 120 jobs, 6 workers, 2534 s wall, code `c64520a`, game v0.111.1 (cc1f9462), models `models/value-v5/model.pt` and `models/q-v5/model.pt`.

| Arm | Games | Errors | Won (Monster / Elite / Boss) | Mean value | HP left after wins | Search s per decision |
|---|---|---|---|---|---|---|
| planner | 120 | 0 | 75 (57 / 15 / 3) | -59.11 | 43.51 | 0.004 |
| mc6 | 120 | 0 | 86 (57 / 23 / 6) | -34.92 | 44.08 | 1.335 |
| mcw6 | 120 | 0 | 99 (59 / 33 / 7) | -7.67 | 44.45 | 2.585 |
| mcwq6 | 120 | 0 | 94 (59 / 28 / 7) | -17.94 | 44.91 | 1.805 |
| qpolicy | 120 | 0 | 74 (56 / 14 / 4) | -56.92 | 45.92 | 0.011 |
| vleaf2 | 120 | 0 | 70 (57 / 10 / 3) | -64.49 | 46.20 | 0.234 |

| Pair (B − A), fight value | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| mcwq6 − mcw6 | 120 | -10.28 | -18.52 to -3.41 | 23 | 39 | 58 | 0.985 |
| qpolicy − planner | 120 | 2.19 | -10.91 to 15.90 | 54 | 52 | 14 | 0.461 |
| vleaf2 − mc6 (tracked) | 120 | -29.57 | -41.15 to -18.88 | 29 | 72 | 19 | 1.000 |

- **H1** (lower bound of `mcwq6` − `mcw6` above −5 and time ratio at most 0.75): lower bound −18.52, time ratio 0.70: **does not hold**. The time target is met, the strength target is not.
- **H2** (`qpolicy` better than the planner, sign test p < 0.05): p = 0.461, mean difference +2.19: **does not hold**.
- Tracked: `vleaf2` stays well below `mc6` (−29.6), as in comparisons 1–4.

Where the filter loses: elites (40 pairs, mean −26.5; 7 better, 16 worse; 28 wins against 33) and bosses (20 pairs, mean −7.2; 7 wins each); hallway fights are equal (60 pairs, −0.5). On its own test split `q-v5` agrees with the teacher's choice less often than the planner's first candidate (62% against 73%), though its regret is lower (4.5 against 5.4 value points), which fits a filter that drops the moves that matter in hard fights.

**Verdict: neither hypothesis holds.** Full wide search (`mcw6`) stays the search for live play and the self-play teacher; the cut to 4 candidates by `q-v5` saves 30% of search time but gives up 10 value points per fight, mostly in elites. The fast policy is no better than the planner. Per decision 0004 combat work narrows to what whole runs need; the next speed lever is the search budget per room (fewer worlds in hallway fights, where every arm wins), not the learned filter.

## 6. Deviations and notes
- 2026-11-21 00:45, before any result: the first training of `q-v5` failed (the wide-teacher datasets have up to 9 candidates per decision, more than the network's limit of 6), so the first run `vsearch-5` started without `q-v5` and every worker stopped at once (0 jobs played). The limit was raised to 10 (decisions whose chosen candidate lies beyond it are skipped), `q-v5` retrained with the registered settings, and the run repeated as `vsearch-5b`. `value-v5` was not affected.
