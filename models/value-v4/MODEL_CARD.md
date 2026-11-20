# Model card: value-v4

Combat value network (P9.E2.S1). Trained 2026-11-20 17:02 at code commit `d5fb903` with PyTorch 2.15.0 on cpu; 227627 parameters; encoder enc-v1.1; vocabulary of game v0.111.1 (cc1f9462).

## What it predicts
From one combat observation: the chance to win the fight, the HP left if it wins, and the enemies' HP left if it loses, under the policy that generated the data (the search teacher below). `model.expected_value` combines them on the search's value scale (HP left after a win; -100 minus enemy HP left after a loss). The last two outputs are residuals on the current HP and the current enemy HP.

## Inputs (FP-10)
The observation encoder only (`tools/learn/encode.py`, `docs/observation-spec.md`): what a player can see. No seed, generator state, draw order or future intent is an input; the observation contains none. The training targets are fight outcomes, which are not inputs at play time.

## Data (ML-2)
- `data/learn/combat-v1`: 586 fights, created 2026-11-20 13:44, game v0.111.1, host `b2525a1`, teacher {"policy": "flat Monte Carlo over the rule planner's candidates (tools/sim.py search_action)", "k": 6, "top": 2, "rollout_policy": "plan_turn.py balanced", "privileged": false}.
- `data/learn/combat-v1s2`: 586 fights, created 2026-11-20 15:10, game v0.111.1, host `8459a9f-dirty`, teacher {"policy": "flat Monte Carlo over the rule planner's candidates (tools/sim.py search_action)", "k": 6, "top": 2, "rollout_policy": "plan_turn.py balanced", "privileged": false}.
- `data/learn/combat-a1s4`: 1172 fights, created 2026-11-20 16:59, game v0.111.1, host `c984046`, teacher {"policy": "flat Monte Carlo over the rule planner's candidates (tools/sim.py search_action)", "k": 6, "top": 2, "rollout_policy": "plan_turn.py balanced", "privileged": false}.
- Split by source run of the Player's history (seed 7; 48 runs): states {'train': 27950, 'val': 4310, 'test': 6116, 'bench': 4752}, fights {'train': 1512, 'val': 240, 'test': 352, 'bench': 240}. The benchmark's (source run, floor) pairs are a separate test split and never trained on.

## Training
- Settings: {"epochs": 80, "lr": 0.001, "wd": 0.0001, "bs": 256, "patience": 8, "hidden": 256, "card_dim": 32, "drop": 0.1, "set_drop": 0.3, "split_seed": 7, "search_weight": 5.0}; epochs run 16 (early stopping on validation loss 0.4575); 118 s.

## Evaluation
Errors are on the search's value scale against the realized outcome of each state's fight. Baselines: the training mean; a linear model on the encoder's global features (stand-in for the hand-made leaf heuristic of P8.E3.S1, not built); the search's own estimate stored with each decision (6 planner rollouts of the chosen action, about 2 s per decision).

### val

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 4310 | 18.374 | 33.647 | 0.950 | 0.039 | 0.988 |
| linear | 4310 | 28.578 | 47.010 | 0.900 | 0.065 | 0.971 |
| mean | 4310 | 88.571 | 107.157 | – | 0.188 | 0.500 |
| network (states with a search estimate) | 3457 | 18.026 | 33.089 | 0.951 | – | – |
| search estimate | 3457 | 12.527 | 27.616 | 0.970 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae -13.60 to -6.93; network_minus_search_mae 2.97 to 8.58

Calibration of the win probability: 0.0-0.1: predicted 0.02, observed 0.02 (812); 0.1-0.2: predicted 0.15, observed 0.29 (79); 0.2-0.3: predicted 0.25, observed 0.30 (56); 0.3-0.4: predicted 0.35, observed 0.40 (57); 0.4-0.5: predicted 0.44, observed 0.48 (63); 0.5-0.6: predicted 0.55, observed 0.54 (70); 0.6-0.7: predicted 0.65, observed 0.69 (77); 0.7-0.8: predicted 0.75, observed 0.84 (80); 0.8-0.9: predicted 0.86, observed 0.76 (129); 0.9-1.0: predicted 0.99, observed 0.99 (2887)

### test

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 6116 | 39.862 | 70.577 | 0.879 | 0.107 | 0.942 |
| linear | 6116 | 38.134 | 65.962 | 0.893 | 0.091 | 0.942 |
| mean | 6116 | 101.699 | 139.720 | – | 0.182 | 0.500 |
| network (states with a search estimate) | 4824 | 40.547 | 71.709 | 0.876 | – | – |
| search estimate | 4824 | 18.607 | 41.541 | 0.960 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae -1.63 to 4.85; network_minus_search_mae 17.24 to 26.84

Calibration of the win probability: 0.0-0.1: predicted 0.02, observed 0.24 (1323); 0.1-0.2: predicted 0.15, observed 0.50 (232); 0.2-0.3: predicted 0.25, observed 0.61 (177); 0.3-0.4: predicted 0.35, observed 0.58 (125); 0.4-0.5: predicted 0.45, observed 0.62 (103); 0.5-0.6: predicted 0.55, observed 0.69 (137); 0.6-0.7: predicted 0.65, observed 0.77 (138); 0.7-0.8: predicted 0.75, observed 0.77 (191); 0.8-0.9: predicted 0.85, observed 0.89 (230); 0.9-1.0: predicted 0.99, observed 0.99 (3460)

### bench

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 4752 | 52.757 | 81.404 | 0.851 | 0.151 | 0.887 |
| linear | 4752 | 54.682 | 79.281 | 0.857 | 0.133 | 0.889 |
| mean | 4752 | 115.148 | 158.978 | – | 0.251 | 0.500 |
| network (states with a search estimate) | 3811 | 52.686 | 81.674 | 0.848 | – | – |
| search estimate | 3811 | 25.004 | 52.591 | 0.942 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae -7.99 to 4.15; network_minus_search_mae 21.03 to 34.56

Calibration of the win probability: 0.0-0.1: predicted 0.02, observed 0.21 (1289); 0.1-0.2: predicted 0.15, observed 0.35 (265); 0.2-0.3: predicted 0.25, observed 0.36 (180); 0.3-0.4: predicted 0.35, observed 0.51 (131); 0.4-0.5: predicted 0.45, observed 0.51 (118); 0.5-0.6: predicted 0.55, observed 0.51 (142); 0.6-0.7: predicted 0.65, observed 0.61 (147); 0.7-0.8: predicted 0.76, observed 0.60 (147); 0.8-0.9: predicted 0.85, observed 0.80 (285); 0.9-1.0: predicted 0.98, observed 0.93 (2048)

## Speed (P9.E2.S3)
CPU, one thread per process under load: one state 1.796 ms, a batch of 64 9.288 ms, turning one encoding into tensors 0.189 ms.

## Known limits
- It predicts outcomes under the teacher's play, not under perfect play; positions the teacher misplays are valued pessimistically.
- Trained on simulated fights only; the simulator's known differences (`docs/simulator-integrity.md`) carry over. Live use needs pile contents, which the live state does not list (`piles_known` = 0 there); not yet checked on live fights.
- Fight specs come from the Player's history (mostly v0.107.1 runs) replayed on v0.111.1: enchantments missing, relics removed before a fight missing, potions capped at 3.
- Ids added by a later patch map to the unknown entry until the vocabulary is rebuilt and the model retrained (P9.E7.S1).

