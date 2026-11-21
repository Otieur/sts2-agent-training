# Model card: value-v5

Combat value network (P9.E2.S1). Trained 2026-11-21 00:43 at code commit `55bbbd9` with PyTorch 2.15.0 on cpu; 227627 parameters; encoder enc-v1.1; vocabulary of game v0.111.1 (cc1f9462).

## What it predicts
From one combat observation: the chance to win the fight, the HP left if it wins, and the enemies' HP left if it loses, under the policy that generated the data (the search teacher below). `model.expected_value` combines them on the search's value scale (HP left after a win; -100 minus enemy HP left after a loss). The last two outputs are residuals on the current HP and the current enemy HP.

## Inputs (FP-10)
The observation encoder only (`tools/learn/encode.py`, `docs/observation-spec.md`): what a player can see. No seed, generator state, draw order or future intent is an input; the observation contains none. The training targets are fight outcomes, which are not inputs at play time.

## Data (ML-2)
- `data/learn/combat-v1`: 586 fights, created 2026-11-20 13:44, game v0.111.1, host `b2525a1`, teacher {"policy": "flat Monte Carlo over the rule planner's candidates (tools/sim.py search_action)", "k": 6, "top": 2, "rollout_policy": "plan_turn.py balanced", "privileged": false}.
- `data/learn/combat-v1s2`: 586 fights, created 2026-11-20 15:10, game v0.111.1, host `8459a9f-dirty`, teacher {"policy": "flat Monte Carlo over the rule planner's candidates (tools/sim.py search_action)", "k": 6, "top": 2, "rollout_policy": "plan_turn.py balanced", "privileged": false}.
- `data/learn/combat-a1s4`: 1172 fights, created 2026-11-20 16:59, game v0.111.1, host `c984046`, teacher {"policy": "flat Monte Carlo over the rule planner's candidates (tools/sim.py search_action)", "k": 6, "top": 2, "rollout_policy": "plan_turn.py balanced", "privileged": false}.
- `data/learn/combat-r1w`: 919 fights, created 2026-11-21 00:37, game v0.111.1, host `55bbbd9`, teacher {"policy": "flat Monte Carlo over the wide candidate set (tools/sim.py search_candidates_wide)", "k": 6, "top": 2, "rollout_policy": "plan_turn.py balanced", "privileged": false}.
- `data/learn/combat-a2w`: 1172 fights, created 2026-11-21 00:40, game v0.111.1, host `55bbbd9`, teacher {"policy": "flat Monte Carlo over the wide candidate set (tools/sim.py search_candidates_wide)", "k": 6, "top": 2, "rollout_policy": "plan_turn.py balanced", "privileged": false}.
- Split by source run of the Player's history (seed 7; 48 runs): states {'train': 61337, 'val': 6302, 'test': 9381, 'bench': 7185}, fights {'train': 3174, 'val': 360, 'test': 528, 'bench': 359}. The benchmark's (source run, floor) pairs are a separate test split and never trained on.

## Training
- Settings: {"epochs": 80, "lr": 0.001, "wd": 0.0001, "bs": 256, "patience": 8, "hidden": 256, "card_dim": 32, "drop": 0.1, "set_drop": 0.3, "split_seed": 7, "search_weight": 5.0}; epochs run 12 (early stopping on validation loss 0.5131); 165 s.

## Evaluation
Errors are on the search's value scale against the realized outcome of each state's fight. Baselines: the training mean; a linear model on the encoder's global features (stand-in for the hand-made leaf heuristic of P8.E3.S1, not built); the search's own estimate stored with each decision (6 planner rollouts of the chosen action, about 2 s per decision).

### val

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 6302 | 19.406 | 35.543 | 0.939 | 0.039 | 0.986 |
| linear | 6302 | 26.300 | 46.468 | 0.892 | 0.061 | 0.973 |
| mean | 6302 | 84.708 | 102.923 | -0.000 | 0.184 | 0.500 |
| network (states with a search estimate) | 5035 | 19.327 | 35.403 | 0.940 | – | – |
| search estimate | 5035 | 12.810 | 29.177 | 0.966 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae -9.23 to -4.60; network_minus_search_mae 4.12 to 9.01

Calibration of the win probability: 0.0-0.1: predicted 0.02, observed 0.03 (1108); 0.1-0.2: predicted 0.14, observed 0.19 (149); 0.2-0.3: predicted 0.25, observed 0.22 (74); 0.3-0.4: predicted 0.35, observed 0.38 (74); 0.4-0.5: predicted 0.45, observed 0.60 (65); 0.5-0.6: predicted 0.55, observed 0.56 (77); 0.6-0.7: predicted 0.65, observed 0.57 (92); 0.7-0.8: predicted 0.75, observed 0.69 (122); 0.8-0.9: predicted 0.86, observed 0.88 (191); 0.9-1.0: predicted 0.99, observed 0.99 (4350)

### test

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 9381 | 45.680 | 78.642 | 0.843 | 0.122 | 0.928 |
| linear | 9381 | 41.704 | 75.065 | 0.856 | 0.095 | 0.940 |
| mean | 9381 | 93.275 | 129.538 | – | 0.168 | 0.500 |
| network (states with a search estimate) | 7346 | 46.279 | 79.472 | 0.841 | – | – |
| search estimate | 7346 | 21.686 | 49.487 | 0.938 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae 0.67 to 7.33; network_minus_search_mae 20.38 to 29.15

Calibration of the win probability: 0.0-0.1: predicted 0.03, observed 0.29 (1917); 0.1-0.2: predicted 0.14, observed 0.54 (413); 0.2-0.3: predicted 0.25, observed 0.65 (266); 0.3-0.4: predicted 0.35, observed 0.71 (223); 0.4-0.5: predicted 0.45, observed 0.74 (198); 0.5-0.6: predicted 0.55, observed 0.80 (173); 0.6-0.7: predicted 0.65, observed 0.86 (221); 0.7-0.8: predicted 0.75, observed 0.85 (278); 0.8-0.9: predicted 0.85, observed 0.87 (426); 0.9-1.0: predicted 0.99, observed 0.99 (5266)

### bench

| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |
|---|---|---|---|---|---|---|
| network | 7185 | 48.118 | 74.224 | 0.872 | 0.124 | 0.913 |
| linear | 7185 | 53.787 | 79.469 | 0.846 | 0.133 | 0.886 |
| mean | 7185 | 108.362 | 152.121 | – | 0.237 | 0.500 |
| network (states with a search estimate) | 5715 | 48.186 | 74.589 | 0.870 | – | – |
| search estimate | 5715 | 25.149 | 52.525 | 0.940 | – | – |

Bootstrap 95% intervals (fights resampled): network_minus_linear_mae -9.73 to -1.59; network_minus_search_mae 18.67 to 27.43

Calibration of the win probability: 0.0-0.1: predicted 0.03, observed 0.16 (1497); 0.1-0.2: predicted 0.15, observed 0.41 (501); 0.2-0.3: predicted 0.25, observed 0.37 (349); 0.3-0.4: predicted 0.35, observed 0.39 (265); 0.4-0.5: predicted 0.45, observed 0.50 (256); 0.5-0.6: predicted 0.55, observed 0.58 (260); 0.6-0.7: predicted 0.65, observed 0.64 (255); 0.7-0.8: predicted 0.75, observed 0.70 (332); 0.8-0.9: predicted 0.85, observed 0.81 (406); 0.9-1.0: predicted 0.99, observed 0.99 (3064)

## Speed (P9.E2.S3)
CPU, one thread per process under load: one state 1.347 ms, a batch of 64 6.379 ms, turning one encoding into tensors 0.158 ms.

## Known limits
- It predicts outcomes under the teacher's play, not under perfect play; positions the teacher misplays are valued pessimistically.
- Trained on simulated fights only; the simulator's known differences (`docs/simulator-integrity.md`) carry over. Live use needs pile contents, which the live state does not list (`piles_known` = 0 there); not yet checked on live fights.
- Fight specs come from the Player's history (mostly v0.107.1 runs) replayed on v0.111.1: enchantments missing, relics removed before a fight missing, potions capped at 3.
- Ids added by a later patch map to the unknown entry until the vocabulary is rebuilt and the model retrained (P9.E7.S1).

