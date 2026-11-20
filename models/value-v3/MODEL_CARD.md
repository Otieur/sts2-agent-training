# Model card: value-v3

Combat value network (P9.E2.S1). Trained 2026-11-20 15:32 at code commit `6a7d765` with PyTorch 2.15.0 on cpu; 227627 parameters; encoder enc-v1.1; vocabulary of game v0.111.1 (cc1f9462).

## What it predicts
From one combat observation: the chance to win the fight, the HP left if it wins, and the enemies' HP left if it loses, under the policy that generated the data (the search teacher below). `model.expected_value` combines them on the search's value scale (HP left after a win; -100 minus enemy HP left after a loss). The last two outputs are residuals on the current HP and the current enemy HP.

## Inputs (FP-10)
The observation encoder only (`tools/learn/encode.py`, `docs/observation-spec.md`): what a player can see. No seed, generator state, draw order or future intent is an input; the observation contains none. The training targets are fight outcomes, which are not inputs at play time.

## Data (ML-2)
- `data/learn/combat-v1`: 586 fights, created 2026-11-20 13:44, game v0.111.1, host `b2525a1`, teacher {"policy": "flat Monte Carlo over the rule planner's candidates (tools/sim.py search_action)", "k": 6, "top": 2, "rollout_policy": "plan_turn.py balanced", "privileged": false}.
- `data/learn/combat-v1s2`: 586 fights, created 2026-11-20 15:10, game v0.111.1, host `8459a9f-dirty`, teacher {"policy": "flat Monte Carlo over the rule planner's candidates (tools/sim.py search_action)", "k": 6, "top": 2, "rollout_policy": "plan_turn.py balanced", "privileged": false}.
- Split by source run of the Player's history (seed 7; 48 runs): states {'train': 14265, 'val': 2171, 'test': 3089, 'bench': 2443}, fights {'train': 756, 'val': 120, 'test': 176, 'bench': 120}. The benchmark's (source run, floor) pairs are a separate test split and never trained on.

## Training
- Settings: {"epochs": 80, "lr": 0.001, "wd": 0.0001, "bs": 256, "patience": 8, "hidden": 256, "card_dim": 32, "drop": 0.1, "split_seed": 7, "search_weight": 5.0}; epochs run 17 (early stopping on validation loss 0.6661); 126 s.

## Evaluation
Errors are on the search's value scale against the realized outcome of each state's fight. Baselines: the training mean; a linear model on the encoder's global features (stand-in for the hand-made leaf heuristic of P8.E3.S1, not built); the search's own estimate stored with each decision (6 planner rollouts of the chosen action, about 2 s per decision).

### val

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 2171 | 19.709 | 37.722 | 0.935 | 0.053 | 0.966 |
| linear | 2171 | 26.360 | 42.291 | 0.918 | 0.059 | 0.978 |
| mean | 2171 | 84.896 | 105.426 | – | 0.189 | 0.500 |
| network (states with a search estimate) | 1741 | 19.260 | 36.848 | 0.937 | – | – |
| search estimate | 1741 | 12.692 | 27.920 | 0.970 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae -10.17 to -3.04; network_minus_search_mae 1.41 to 12.49

Calibration of the win probability: 0.0-0.1: predicted 0.03, observed 0.04 (445); 0.1-0.2: predicted 0.14, observed 0.22 (9); 0.2-0.3: predicted 0.24, observed 0.71 (7); 0.3-0.4: predicted 0.35, observed 0.33 (3); 0.4-0.5: predicted 0.44, observed 0.70 (10); 0.5-0.6: predicted 0.55, observed 0.62 (21); 0.6-0.7: predicted 0.66, observed 0.53 (17); 0.7-0.8: predicted 0.77, observed 0.74 (54); 0.8-0.9: predicted 0.86, observed 0.80 (110); 0.9-1.0: predicted 0.99, observed 0.96 (1495)

### test

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 3089 | 64.037 | 98.131 | 0.787 | 0.228 | 0.854 |
| linear | 3089 | 36.491 | 62.924 | 0.903 | 0.082 | 0.956 |
| mean | 3089 | 98.318 | 139.451 | – | 0.183 | 0.500 |
| network (states with a search estimate) | 2453 | 65.934 | 100.145 | 0.778 | – | – |
| search estimate | 2453 | 18.352 | 40.223 | 0.962 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae 20.28 to 35.06; network_minus_search_mae 38.70 to 57.19

Calibration of the win probability: 0.0-0.1: predicted 0.02, observed 0.46 (979); 0.1-0.2: predicted 0.14, observed 0.76 (144); 0.2-0.3: predicted 0.25, observed 0.70 (89); 0.3-0.4: predicted 0.35, observed 0.85 (67); 0.4-0.5: predicted 0.45, observed 0.80 (64); 0.5-0.6: predicted 0.55, observed 0.94 (52); 0.6-0.7: predicted 0.65, observed 0.80 (40); 0.7-0.8: predicted 0.75, observed 0.76 (46); 0.8-0.9: predicted 0.86, observed 0.79 (107); 0.9-1.0: predicted 0.99, observed 0.95 (1501)

### bench

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 2443 | 59.772 | 91.371 | 0.806 | 0.201 | 0.802 |
| linear | 2443 | 55.742 | 81.034 | 0.847 | 0.136 | 0.875 |
| mean | 2443 | 107.615 | 155.713 | – | 0.232 | 0.500 |
| network (states with a search estimate) | 1957 | 59.544 | 91.585 | 0.801 | – | – |
| search estimate | 1957 | 25.419 | 50.879 | 0.943 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae -7.19 to 15.90; network_minus_search_mae 22.10 to 46.91

Calibration of the win probability: 0.0-0.1: predicted 0.02, observed 0.36 (671); 0.1-0.2: predicted 0.14, observed 0.41 (74); 0.2-0.3: predicted 0.25, observed 0.56 (48); 0.3-0.4: predicted 0.35, observed 0.43 (61); 0.4-0.5: predicted 0.45, observed 0.24 (46); 0.5-0.6: predicted 0.55, observed 0.52 (63); 0.6-0.7: predicted 0.65, observed 0.76 (75); 0.7-0.8: predicted 0.75, observed 0.72 (109); 0.8-0.9: predicted 0.86, observed 0.73 (167); 0.9-1.0: predicted 0.98, observed 0.90 (1129)

## Speed (P9.E2.S3)
CPU, one thread per process under load: one state 1.689 ms, a batch of 64 10.046 ms, turning one encoding into tensors 0.198 ms.

## Known limits
- It predicts outcomes under the teacher's play, not under perfect play; positions the teacher misplays are valued pessimistically.
- Trained on simulated fights only; the simulator's known differences (`docs/simulator-integrity.md`) carry over. Live use needs pile contents, which the live state does not list (`piles_known` = 0 there); not yet checked on live fights.
- Fight specs come from the Player's history (mostly v0.107.1 runs) replayed on v0.111.1: enchantments missing, relics removed before a fight missing, potions capped at 3.
- Ids added by a later patch map to the unknown entry until the vocabulary is rebuilt and the model retrained (P9.E7.S1).

