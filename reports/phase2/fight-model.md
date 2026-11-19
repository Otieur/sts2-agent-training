# Fight Model: Deck Strength against HP Lost

All characters, solo, v0.107.1, finished runs. Built by `tools/fight_model.py`. Ordinary least squares per act and room type: HP lost in the fight (percent of max HP) on the deck's damage per turn, block per turn and scaling count at the start of the fight (deck_metrics proxies, v0.107.1 card values) and the ascension level. Coefficients are percentage points of max HP per unit; * marks |coefficient| at least twice its standard error. `[PLAYER-DATA, observational]`.

| Act | Room | Fights | Mean HP lost | per damage/turn | per block/turn | per scaling card | per ascension level | R² |
|---|---|---|---|---|---|---|---|---|
| 1 | monster | 1069 | 7.7% | +0.11 | -0.11 | +2.25* | +0.46* | 0.07 |
| 1 | elite | 186 | 24.7% | +0.60 | -1.25* | -0.54 | +0.87* | 0.06 |
| 1 | boss | 173 | 40.1% | +0.93* | +0.68 | -1.33 | +0.81 | 0.06 |
| 2 | monster | 572 | 12.5% | -0.05 | -0.11 | +0.26 | +0.54* | 0.02 |
| 2 | elite | 122 | 31.2% | -0.12 | -0.30 | +0.22 | +1.77* | 0.09 |
| 2 | boss | 102 | 44.0% | +0.69 | +0.84 | -3.76* | +1.64* | 0.17 |
| 3 | monster | 344 | 9.4% | -0.04 | -0.37 | +0.81 | +0.34 | 0.02 |
| 3 | elite | 65 | 28.6% | +0.70 | -0.51 | -2.22 | +1.36 | 0.09 |
| 3 | boss | 81 | 51.3% | +1.38 | -0.75 | -1.58 | +0.08 | 0.06 |

## Reading

- A negative coefficient means more of that feature went with less HP lost. Block per turn is the feature to watch: the corner targets (H9) say block matters at bosses.
- R² is low in every cell: most of a fight's HP loss is the draw, the enemy roll and decisions, not the deck proxies. Use the coefficients for small adjustments (tools/path.py applies them relative to the average deck), not as predictions for one fight.
