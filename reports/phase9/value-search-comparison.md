# Comparison: value network in search against the flat Monte Carlo teacher

Written before the run (P8.E1.S3, ML-10) on 2026-11-20 at 13:15, while the training data was still being generated. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypotheses
- **H1 (equal cost):** search with value-network leaves and 6 worlds per candidate (`vleaf6`) gets a higher fight value than the current teacher (`mc6`, 6 worlds per candidate, planner rollouts to the end of the fight). Both make the same number of restores per decision, which is what search time is driven by (restore about 100 ms under load, rollout steps about 2 ms).
- **H2 (a third of the cost):** `vleaf2` (2 worlds per candidate) is not worse than `mc6` by more than 5 value points per fight, at most 40% of `mc6`'s search time per decision.
- **H3 (network alone):** the one-ply policy `vgreedy` (each candidate played once on a re-sampled world, the position right after it scored by the network) gets a higher fight value than the rule planner.

## 2. Fights
- Benchmark set: `data/sim/benchmark-v1.json` (60 fights from the Player's history: 30 hallway, 20 elite, 10 boss over three acts; exam seeds excluded, ML-7).
- Two sample seeds per fight (`tools/learn/bench.py`, seed base 7000000): 120 jobs. Every arm plays the same fight with the same run seed and sample seed, in the same worker one after the other, so machine load is shared.
- Training data never includes the benchmark's (source run, floor) pairs (`tools/learn/train_value.py` puts them in a separate split).
- Simulator header: game v0.111.1 (cc1f9462); host commit recorded in the run's manifest; fidelity at the time of writing: 11 of 11 recorded fights reproduce exactly (`reports/phase7/fidelity.md`).

## 3. Policies and budgets
- `planner`: rule planner, balanced mode.
- `mc6`: flat Monte Carlo over the planner's candidates (top 2 plans per mode plus ending the turn), 6 re-sampled worlds each, planner rollouts to the end of the fight, shared sample seeds across candidates (the self-play teacher of `combat-v1`).
- `vleaf6`, `vleaf2`: the same candidates and worlds (6 or 2); each rollout stops when the next player turn starts and the value network scores that position (finished fights are scored exactly).
- `vgreedy`: the same candidates; one re-sampled world each; the network scores the position right after the candidate.
- Value network: `value-v1`, trained on `combat-v1` only (history specs, teacher `mc6`). Settings chosen by validation loss among three configurations fixed in advance: (card embedding 16, hidden 128, dropout 0.2, weight decay 1e-3), (32, 256, 0.1, 1e-4), (32, 128, 0.2, 1e-3); test splits read once afterwards.
- Decisions use only what the player can see: restores bring back the past, the hidden future is re-sampled (FP-15); the network reads the observation encoder only (FP-10). Potions are not used by any arm (the planner's candidates exclude them).

## 4. Metrics and test
- Primary: fight value as in search: HP left after a win; after a loss, -100 minus the enemies' HP left.
- Secondary: wins, HP left after wins, search seconds per decision, host restarts.
- Test: paired by job. H1 and H3: one-sided sign test on better/worse pairs, significance 0.025 each (Bonferroni over the two directional tests); mean paired difference with a bootstrap 95% interval. H2: the lower end of the bootstrap 95% interval of (`vleaf2` − `mc6`) above −5, and the time ratio at most 0.4.
- Jobs where an arm hits a host error or a stuck state are left out of that arm's pairs and listed.
- Number of jobs fixed in advance: 120; no early stop.
- What follows from the result (expert iteration, P9.E3.S2): if H1 holds, `vleaf6` becomes the teacher for the next data batch; if only H2 holds, `vleaf2` does (three times the data per hour at teacher strength); otherwise `mc6` stays the teacher and more data is collected before retraining.

## 5. Results
Run 2026-11-20, 14:47–14:59 (`tools/learn/bench.py --report data/learn/bench/vsearch-1 --markdown`; manifest `data/learn/bench/vsearch-1/manifest.json`).

Run `vsearch-1`: 120 jobs, 6 workers, 753 s wall, code `203f7c2`, game v0.111.1 (cc1f9462), model `models/value-v1/model.pt`, action-value model `models/q-v1/model.pt`.

| Arm | Games | Errors | Won | Mean value | HP left after wins | Search s per decision | Host restarts |
|---|---|---|---|---|---|---|---|
| planner | 120 | 0 | 75 | -59.11 | 43.51 | 0.002 | 0 |
| mc6 | 120 | 0 | 86 | -34.92 | 44.08 | 0.896 | 0 |
| vleaf6 | 120 | 0 | 64 | -83.02 | 38.59 | 0.469 | 0 |
| vleaf2 | 120 | 0 | 61 | -91.42 | 37.93 | 0.186 | 0 |
| vgreedy | 120 | 4 | 51 | -108.27 | 39.35 | 0.072 | 0 |
| qpolicy | 120 | 0 | 73 | -56.31 | 42.70 | 0.007 | 0 |

| Pair (B − A) | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| vleaf6 − mc6 | 120 | -48.10 | -62.15 to -35.43 | 20 | 92 | 8 | 1.0000 |
| vleaf2 − mc6 | 120 | -56.50 | -71.78 to -42.26 | 21 | 93 | 6 | 1.0000 |
| vgreedy − planner | 116 | -59.72 | -75.55 to -43.86 | 20 | 91 | 5 | 1.0000 |
| mc6 − planner | 120 | 24.19 | 13.30 to 35.17 | 75 | 21 | 24 | 0.0000 |
| vgreedy − mc6 | 116 | -84.09 | -101.41 to -67.19 | 6 | 105 | 5 | 1.0000 |
| qpolicy − planner | 120 | 2.80 | -8.97 to 14.98 | 46 | 54 | 20 | 0.8159 |
| qpolicy − mc6 | 120 | -21.39 | -31.48 to -11.29 | 26 | 83 | 11 | 1.0000 |

- **H1** (`vleaf6` better than `mc6`, sign test p < 0.025): p = 1.0000, mean difference -48.10: **does not hold**.
- **H2** (`vleaf2` not worse than `mc6` by more than 5, lower bound > −5, time ratio ≤ 0.4): lower bound -71.78, time ratio 0.21: **does not hold**.
- **H3** (`vgreedy` better than `planner`, sign test p < 0.025): p = 1.0000, mean difference -59.72: **does not hold**.

Jobs left out of pairs: 4 errors, 0 blocked. fight 23 sample 0 vgreedy: too many host restarts (restore did not give back the decision state); fight 22 sample 0 vgreedy: too many host restarts (restore did not give back the decision state); fight 22 sample 1 vgreedy: too many host restarts (restore did not give back the decision state); fight 23 sample 1 vgreedy: too many host restarts (restore did not give back the decision state)

Mean value by room type: Monster planner 33.9, mc6 40.1, vleaf6 10.4, vleaf2 10.2, vgreedy -9.6, qpolicy 33.1; Elite planner -100.2, mc6 -53.6, vleaf6 -124.8, vleaf2 -145.2, vgreedy -162.3, qpolicy -96.0; Boss planner -255.8, mc6 -222.8, vleaf6 -279.7, vleaf2 -288.9, vgreedy -343.1, qpolicy -245.1

**Verdict: H1, H2 and H3 all fail, by wide margins.** `value-v1` at search leaves loses about 48 value points per fight against the rollout teacher at half its search time, and the one-ply policy loses about 60 against the rule planner. By the rule in section 4, `mc6` stays the teacher and more data is collected before retraining. The exploratory `qpolicy` (no restore, 7 ms per decision) is level with the planner (+2.8, interval −9.0 to +15.0).

Why, as far as the data shows: `value-v1`'s error against realized outcomes is 53.8 on held-out runs, against 17.7 for the search's own six-rollout estimate on the same states (`models/value-v1/MODEL_CARD.md`); a leaf judge that much noisier than a rollout misranks candidates. A development run made after this comparison (validation split only) shows the main fix: an auxiliary loss pulling the network's value toward the stored search estimate brings the validation error from 47.2 to 24.3 and the win AUC from 0.90 to 0.99 (`--search-weight 2`). That network has not been tested in search; it needs its own comparison.


## 6. Deviations and notes
Written before the run started (2026-11-20, 13:40):
- The simulator host changed after sections 1–4 were written, in two ways that leave every fight trajectory unchanged: fights from nothing no longer generate the map (190 history fights, 3,330 states identical with and without it), and Rolling Boulder's power runs on the scoped test path (before, any deck with it hung the host; such fights were errors, not data). Restores now cost 13–60 ms instead of about 100–250 ms, so rollout steps weigh more in search time than when H2's time ratio was set; the ratio is still measured in the run and judged as written.
- One exploratory arm is added to the same jobs: `qpolicy` (the action-value network `q-v1` scores the planner's candidates; no restore). It is not part of H1–H3 and decides nothing; it is reported for information.

After the run:
- `vgreedy` failed on fights 22 and 23 (both samples): after a restore the fight was no longer in progress, three host restarts in a row. Not yet explained; those four jobs are left out of `vgreedy`'s pairs as section 4 says. The other arms played these fights without error.
