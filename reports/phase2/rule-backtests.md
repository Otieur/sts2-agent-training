# Rule Backtests

All characters, solo, v0.107.1, finished runs. Built by `tools/backtest_rules.py`. `[PLAYER-DATA]`, observational.

## H4: remove a basic card in Act 1

Only runs that reached an Act 1 shop with at least 75 gold (they had the chance). Outcome: survived Act 1.

| Band | Removed a Strike/Defend in Act 1 | Did not |
|---|---|---|
| A0-4 | 12/16 (75%) | 16/22 (73%) |
| A5-9 | 16/18 (89%) | 33/47 (70%) |
| A10 | 7/10 (70%) | 19/32 (59%) |
| All | 35/44 (80%) | 68/101 (67%) |

Reading: a clear gap at A5–9 and A10, none at A0–4. Remaining confounders: gold amount and shop timing (richer runs can both remove and buy), and the Player's choice to remove when the deck already looked good. Supports testing H4 at A5 and above.

## H5: elites under 50% HP

| Band | Entered under 50% HP: fatal | Entered at 50% or more: fatal |
|---|---|---|
| A0-4 | 2/20 (10%) | 2/71 (3%) |
| A5-9 | 8/25 (32%) | 6/105 (6%) |
| A10 | 6/21 (29%) | 6/66 (9%) |
| All | 16/66 (24%) | 14/242 (6%) |

Reading: the danger holds in every band and is strongest at A5 and above (about 3–5 times the fatal rate). Kept as a rule.
