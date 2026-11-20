# Model card: value-v1

Combat value network (P9.E2.S1). Trained 2026-11-20 13:55 at code commit `b3e9933` with PyTorch 2.15.0 on cpu; 227627 parameters; encoder enc-v1; vocabulary of game v0.111.1 (cc1f9462).

## What it predicts
From one combat observation: the chance to win the fight, the HP left if it wins, and the enemies' HP left if it loses, under the policy that generated the data (the search teacher below). `model.expected_value` combines them on the search's value scale (HP left after a win; -100 minus enemy HP left after a loss). The last two outputs are residuals on the current HP and the current enemy HP.

## Inputs (FP-10)
The observation encoder only (`tools/learn/encode.py`, `docs/observation-spec.md`): what a player can see. No seed, generator state, draw order or future intent is an input; the observation contains none. The training targets are fight outcomes, which are not inputs at play time.

## Data (ML-2)
- `data/learn/combat-v1`: 586 fights, created 2026-11-20 13:44, game v0.111.1, host `b2525a1`, teacher {"policy": "flat Monte Carlo over the rule planner's candidates (tools/sim.py search_action)", "k": 6, "top": 2, "rollout_policy": "plan_turn.py balanced", "privileged": false}.
- Split by source run of the Player's history (seed 7; 48 runs): states {'train': 7069, 'val': 1072, 'test': 1523, 'bench': 1231}, fights {'train': 378, 'val': 60, 'test': 88, 'bench': 60}. The benchmark's (source run, floor) pairs are a separate test split and never trained on.

## Training
- Settings: {"epochs": 80, "lr": 0.001, "wd": 0.0001, "bs": 256, "patience": 8, "hidden": 256, "card_dim": 32, "drop": 0.1, "split_seed": 7}; epochs run 32 (early stopping on validation loss 0.5509); 479 s.

## Evaluation
Errors are on the search's value scale against the realized outcome of each state's fight. Baselines: the training mean; a linear model on the encoder's global features (stand-in for the hand-made leaf heuristic of P8.E3.S1, not built); the search's own estimate stored with each decision (6 planner rollouts of the chosen action, about 2 s per decision).

### val

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 1072 | 47.219 | 73.557 | 0.834 | 0.127 | 0.898 |
| linear | 1072 | 74.849 | 91.772 | 0.516 | 0.135 | 0.838 |
| mean | 1072 | 84.078 | 105.712 | – | 0.184 | 0.500 |
| network (states with a search estimate) | 867 | 46.859 | 73.664 | 0.831 | – | – |
| search estimate | 867 | 13.480 | 30.466 | 0.962 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae -39.45 to -16.17; network_minus_search_mae 18.31 to 48.61

Calibration of the win probability: 0.2-0.3: predicted 0.29, observed 0.00 (2); 0.3-0.4: predicted 0.35, observed 0.07 (30); 0.4-0.5: predicted 0.45, observed 0.22 (41); 0.5-0.6: predicted 0.55, observed 0.14 (44); 0.6-0.7: predicted 0.65, observed 0.20 (55); 0.7-0.8: predicted 0.76, observed 0.53 (81); 0.8-0.9: predicted 0.86, observed 0.72 (189); 0.9-1.0: predicted 0.95, observed 0.96 (630)

### test

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 1523 | 53.811 | 78.937 | 0.825 | 0.130 | 0.854 |
| linear | 1523 | 85.710 | 110.149 | 0.578 | 0.140 | 0.837 |
| mean | 1523 | 97.006 | 133.288 | – | 0.183 | 0.500 |
| network (states with a search estimate) | 1213 | 53.803 | 78.987 | 0.825 | – | – |
| search estimate | 1213 | 17.681 | 40.429 | 0.961 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae -42.59 to -21.00; network_minus_search_mae 25.48 to 46.48

Calibration of the win probability: 0.1-0.2: predicted 0.20, observed 0.00 (2); 0.2-0.3: predicted 0.25, observed 0.35 (57); 0.3-0.4: predicted 0.35, observed 0.42 (86); 0.4-0.5: predicted 0.45, observed 0.24 (84); 0.5-0.6: predicted 0.55, observed 0.48 (99); 0.6-0.7: predicted 0.65, observed 0.56 (101); 0.7-0.8: predicted 0.75, observed 0.65 (124); 0.8-0.9: predicted 0.86, observed 0.83 (255); 0.9-1.0: predicted 0.95, observed 0.96 (715)

### bench

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 1231 | 72.147 | 101.363 | 0.807 | 0.160 | 0.810 |
| linear | 1231 | 96.489 | 136.989 | 0.466 | 0.175 | 0.776 |
| mean | 1231 | 107.523 | 159.064 | – | 0.231 | 0.500 |
| network (states with a search estimate) | 988 | 70.830 | 100.233 | 0.800 | – | – |
| search estimate | 988 | 24.920 | 48.686 | 0.950 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae -39.57 to -9.93; network_minus_search_mae 30.95 to 65.14

Calibration of the win probability: 0.1-0.2: predicted 0.19, observed 0.00 (18); 0.2-0.3: predicted 0.25, observed 0.10 (70); 0.3-0.4: predicted 0.36, observed 0.25 (72); 0.4-0.5: predicted 0.45, observed 0.50 (139); 0.5-0.6: predicted 0.55, observed 0.57 (183); 0.6-0.7: predicted 0.65, observed 0.67 (134); 0.7-0.8: predicted 0.75, observed 0.75 (92); 0.8-0.9: predicted 0.86, observed 0.85 (193); 0.9-1.0: predicted 0.95, observed 0.92 (330)

## Speed (P9.E2.S3)
CPU, one thread per process under load: one state 1.706 ms, a batch of 64 22.576 ms, turning one encoding into tensors 0.325 ms.

## Known limits
- It predicts outcomes under the teacher's play, not under perfect play; positions the teacher misplays are valued pessimistically.
- Trained on simulated fights only; the simulator's known differences (`docs/simulator-integrity.md`) carry over. Live use needs pile contents, which the live state does not list (`piles_known` = 0 there); not yet checked on live fights.
- Fight specs come from the Player's history (mostly v0.107.1 runs) replayed on v0.111.1: enchantments missing, relics removed before a fight missing, potions capped at 3.
- Ids added by a later patch map to the unknown entry until the vocabulary is rebuilt and the model retrained (P9.E7.S1).

