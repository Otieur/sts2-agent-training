# Fight Model: Deck Strength against HP Lost

All characters, solo, v0.107.1, finished runs. Built by `tools/fight_model.py`. Ordinary least squares per act and room type: HP lost in the fight (percent of max HP) on the deck's damage per turn, block per turn and scaling count at the start of the fight (deck_metrics proxies, v0.107.1 card values) and the ascension level. Coefficients are percentage points of max HP per unit; * marks |coefficient| at least twice its standard error. `[PLAYER-DATA, observational]`.

| Act | Room | Fights | Mean HP lost | per damage/turn | per block/turn | per scaling card | per ascension level | R² |
|---|---|---|---|---|---|---|---|---|
| 1 | monster | 1069 | 7.7% | +0.18* | -0.11 | +2.32* | +0.47* | 0.08 |
| 1 | elite | 186 | 24.7% | +0.27 | -1.32* | -0.90 | +0.86* | 0.05 |
| 1 | boss | 173 | 40.1% | +1.01* | +0.52 | -1.32 | +0.84 | 0.07 |
| 2 | monster | 572 | 12.5% | -0.02 | -0.11 | +0.28 | +0.54* | 0.02 |
| 2 | elite | 122 | 31.2% | -0.06 | -0.28 | +0.25 | +1.77* | 0.09 |
| 2 | boss | 102 | 44.0% | +0.54 | +0.73 | -3.87* | +1.63* | 0.16 |
| 3 | monster | 344 | 9.4% | +0.14 | -0.43 | +0.95* | +0.38 | 0.02 |
| 3 | elite | 65 | 28.6% | +0.62 | -0.63 | -2.15 | +1.31 | 0.09 |
| 3 | boss | 81 | 51.3% | +0.86 | -0.91 | -1.79 | +0.08 | 0.04 |

## Reading

- A negative coefficient means more of that feature went with less HP lost. Block per turn is the feature to watch: the corner targets (H9) say block matters at bosses.
- R² is low in every cell: most of a fight's HP loss is the draw, the enemy roll and decisions, not the deck proxies. Use the coefficients for small adjustments (tools/path.py applies them relative to the average deck), not as predictions for one fight.
