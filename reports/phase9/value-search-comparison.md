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
Pending.

## 6. Deviations and notes
Written before the run started (2026-11-20, 13:40):
- The simulator host changed after sections 1–4 were written, in two ways that leave every fight trajectory unchanged: fights from nothing no longer generate the map (190 history fights, 3,330 states identical with and without it), and Rolling Boulder's power runs on the scoped test path (before, any deck with it hung the host; such fights were errors, not data). Restores now cost 13–60 ms instead of about 100–250 ms, so rollout steps weigh more in search time than when H2's time ratio was set; the ratio is still measured in the run and judged as written.
- One exploratory arm is added to the same jobs: `qpolicy` (the action-value network `q-v1` scores the planner's candidates; no restore). It is not part of H1–H3 and decides nothing; it is reported for information.
