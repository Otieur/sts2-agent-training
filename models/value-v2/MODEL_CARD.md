# Model card: value-v2

Combat value network (P9.E2.S1). Trained 2026-11-20 15:21 at code commit `ebb3921` with PyTorch 2.15.0 on cpu; 227627 parameters; encoder enc-v1; vocabulary of game v0.111.1 (cc1f9462).

## What it predicts
From one combat observation: the chance to win the fight, the HP left if it wins, and the enemies' HP left if it loses, under the policy that generated the data (the search teacher below). `model.expected_value` combines them on the search's value scale (HP left after a win; -100 minus enemy HP left after a loss). The last two outputs are residuals on the current HP and the current enemy HP.

## Inputs (FP-10)
The observation encoder only (`tools/learn/encode.py`, `docs/observation-spec.md`): what a player can see. No seed, generator state, draw order or future intent is an input; the observation contains none. The training targets are fight outcomes, which are not inputs at play time.

## Data (ML-2)
- `data/learn/combat-v1`: 586 fights, created 2026-11-20 13:44, game v0.111.1, host `b2525a1`, teacher {"policy": "flat Monte Carlo over the rule planner's candidates (tools/sim.py search_action)", "k": 6, "top": 2, "rollout_policy": "plan_turn.py balanced", "privileged": false}.
- `data/learn/combat-v1s2`: 586 fights, created 2026-11-20 15:10, game v0.111.1, host `8459a9f-dirty`, teacher {"policy": "flat Monte Carlo over the rule planner's candidates (tools/sim.py search_action)", "k": 6, "top": 2, "rollout_policy": "plan_turn.py balanced", "privileged": false}.
- Split by source run of the Player's history (seed 7; 48 runs): states {'train': 14265, 'val': 2171, 'test': 3089, 'bench': 2443}, fights {'train': 756, 'val': 120, 'test': 176, 'bench': 120}. The benchmark's (source run, floor) pairs are a separate test split and never trained on.

## Training
- Settings: {"epochs": 80, "lr": 0.001, "wd": 0.0001, "bs": 256, "patience": 8, "hidden": 256, "card_dim": 32, "drop": 0.1, "split_seed": 7, "search_weight": 5.0}; epochs run 20 (early stopping on validation loss 2.5835); 59 s.

## Evaluation
Errors are on the search's value scale against the realized outcome of each state's fight. Baselines: the training mean; a linear model on the encoder's global features (stand-in for the hand-made leaf heuristic of P8.E3.S1, not built); the search's own estimate stored with each decision (6 planner rollouts of the chosen action, about 2 s per decision).

### val

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 2171 | 48.010 | 70.394 | 0.779 | 0.127 | 0.868 |
| linear | 2171 | 59.956 | 85.042 | 0.609 | 0.130 | 0.859 |
| mean | 2171 | 84.896 | 105.426 | – | 0.189 | 0.500 |
| network (states with a search estimate) | 1741 | 46.848 | 70.831 | 0.786 | – | – |
| search estimate | 1741 | 12.692 | 27.920 | 0.970 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae -20.03 to -4.46; network_minus_search_mae 25.42 to 44.02

Calibration of the win probability: 0.0-0.1: predicted 0.10, observed 0.00 (1); 0.1-0.2: predicted 0.16, observed 0.24 (49); 0.2-0.3: predicted 0.25, observed 0.13 (150); 0.3-0.4: predicted 0.35, observed 0.26 (159); 0.4-0.5: predicted 0.45, observed 0.51 (177); 0.5-0.6: predicted 0.55, observed 0.79 (214); 0.6-0.7: predicted 0.65, observed 0.83 (261); 0.7-0.8: predicted 0.75, observed 0.85 (260); 0.8-0.9: predicted 0.85, observed 0.91 (431); 0.9-1.0: predicted 0.94, observed 0.99 (469)

### test

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 3089 | 59.493 | 82.924 | 0.808 | 0.168 | 0.807 |
| linear | 3089 | 75.173 | 110.811 | 0.612 | 0.146 | 0.823 |
| mean | 3089 | 98.318 | 139.451 | – | 0.183 | 0.500 |
| network (states with a search estimate) | 2453 | 58.175 | 82.469 | 0.804 | – | – |
| search estimate | 2453 | 18.352 | 40.223 | 0.962 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae -24.49 to -7.10; network_minus_search_mae 32.19 to 47.31

Calibration of the win probability: 0.1-0.2: predicted 0.17, observed 0.52 (121); 0.2-0.3: predicted 0.26, observed 0.40 (262); 0.3-0.4: predicted 0.35, observed 0.44 (318); 0.4-0.5: predicted 0.45, observed 0.61 (355); 0.5-0.6: predicted 0.55, observed 0.79 (414); 0.6-0.7: predicted 0.65, observed 0.85 (391); 0.7-0.8: predicted 0.75, observed 0.90 (321); 0.8-0.9: predicted 0.85, observed 0.94 (423); 0.9-1.0: predicted 0.94, observed 0.98 (484)

### bench

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 2443 | 73.921 | 98.972 | 0.771 | 0.194 | 0.782 |
| linear | 2443 | 87.195 | 128.975 | 0.529 | 0.173 | 0.795 |
| mean | 2443 | 107.615 | 155.713 | – | 0.232 | 0.500 |
| network (states with a search estimate) | 1957 | 72.368 | 97.583 | 0.769 | – | – |
| search estimate | 1957 | 25.419 | 50.879 | 0.943 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae -25.88 to -0.06; network_minus_search_mae 35.25 to 58.85

Calibration of the win probability: 0.0-0.1: predicted 0.09, observed 0.00 (9); 0.1-0.2: predicted 0.16, observed 0.29 (195); 0.2-0.3: predicted 0.25, observed 0.48 (329); 0.3-0.4: predicted 0.35, observed 0.43 (315); 0.4-0.5: predicted 0.45, observed 0.58 (302); 0.5-0.6: predicted 0.55, observed 0.76 (284); 0.6-0.7: predicted 0.65, observed 0.86 (288); 0.7-0.8: predicted 0.75, observed 0.88 (270); 0.8-0.9: predicted 0.85, observed 0.90 (259); 0.9-1.0: predicted 0.94, observed 0.96 (192)

## Speed (P9.E2.S3)
CPU, one thread per process under load: one state 0.708 ms, a batch of 64 4.06 ms, turning one encoding into tensors 0.115 ms.

## Known limits
- It predicts outcomes under the teacher's play, not under perfect play; positions the teacher misplays are valued pessimistically.
- Trained on simulated fights only; the simulator's known differences (`docs/simulator-integrity.md`) carry over. Live use needs pile contents, which the live state does not list (`piles_known` = 0 there); not yet checked on live fights.
- Fight specs come from the Player's history (mostly v0.107.1 runs) replayed on v0.111.1: enchantments missing, relics removed before a fight missing, potions capped at 3.
- Ids added by a later patch map to the unknown entry until the vocabulary is rebuilt and the model retrained (P9.E7.S1).

