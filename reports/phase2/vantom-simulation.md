# Boss Simulations (Vantom, Knowledge Demon)

Built by `tools/simulate_fight.py --report` (300 simulated fights per row and mode, from 80/80 HP). Each turn's plays are chosen by `tools/plan_turn.py`; Vantom follows its documented cycle (Ink Blot 7, Inky Lance 6x2, Dismember 27 + 3 Wounds, Prepare +2 Strength; 173 HP; 9 Slippery). Card values are v0.111.1. No relics, potions or upgrades. `[HYPOTHESIS]`: a model, useful for comparing additions to the same deck, not for absolute win rates.

Calibration: a typical 16-card floor-17 deck starting at 60/80 HP wins 33–39% of simulated fights; the Player's Ironclad decks survived 5 of 11 real Vantom fights, so the model is in range and somewhat pessimistic.

| Base deck + two cards | Win (balanced) | HP lost (balanced) | Win (safe) | HP lost (safe) |
|---|---|---|---|---|
| base deck (15 cards) | 78% | 68.6 | 59% | 71.3 |
| + Twin Strike, Sword Boomerang (multi-hit) | 98% | 62.8 | 92% | 59.7 |
| + Pommel Strike, Battle Trance (draw) | 70% | 71.2 | 84% | 63.8 |
| + Shrug It Off, Flame Barrier (block) | 63% | 71.7 | 81% | 67.2 |
| + Demon Form, Shrug It Off (scaling) | 99% | 56.2 | 79% | 62.0 |
| + Strike x2 (control) | 66% | 73.0 | 47% | 75.0 |
| + Thunderclap, Breakthrough (single-hit hit-all) | 67% | 72.3 | 44% | 75.8 |
| + Breakthrough x2 (single-hit hit-all) | 58% | 74.0 | 32% | 77.5 |

## Reading (from the table above; seeds are fixed, so the run reproduces)

- **Multi-hit attacks and Demon Form are the best additions** in both plans (multi-hit 98% balanced / 92% safe; Demon Form with Shrug It Off 99% / 79%). Supports H6 and the playbook's Vantom override for multi-hit attacks.
- **Breakthrough is worse than a plain Strike here**: two Breakthroughs fall below the two-Strike control in both plans (58% against 66% balanced, 32% against 47% safe); its 9 damage is capped to 1 while Slippery lasts, and it costs HP. Thunderclap with Breakthrough is level with the control under the balanced plan and below it under the safe plan. Consistent with H2 and with Breakthrough's decision-point record.
- **Draw and block help only under the safe plan** (above the base there, below it under the balanced plan): the planner's mode interacts with the deck, so treat those rows as policy-dependent.
- The balanced plan beats the safe plan from full HP for most decks; from 60 HP the safe plan did better in a separate check. This matches the playbook: safe when HP is below plan, balanced when ahead.

## Calibration against the Player's record

The 15-card base deck for Act 1 bosses and the 22-card Act 2 deck for Knowledge Demon, at 60/80 HP, the better plan; the Player's Ironclad boss fights on v0.107.1 (real decks are bigger and have relics, potions and upgrades, so the model is expected to be pessimistic; what matters is the ratio between bosses). A boss marked **no** is not used by `tools/draft.py`.

| Boss | Model win | The Player survived | Used in drafting |
|---|---|---|---|
| Vantom | 20% | 4/10 (40%) | yes |
| Lagavulin Matriarch | 35% | 6/8 (75%) | yes |
| Ceremonial Beast | 2% | 5/6 (83%) | **no** |
| Knowledge Demon | 31% | 8/12 (67%) | **no** |

## Knowledge Demon: which curse to take

A 22-card end-of-Act-2 deck (two Inflames, Demon Form, two Twin Strikes, Impervious, Offering and others) at 80/80 HP; each row always takes the same curse when offered (the real choice is one of two each time). Cycle: Curse of Knowledge, Slap 17, Knowledge Overwhelming 8x3, Ponder 11 + heal 30 + 2 Strength (heal single-source); curses stack for the rest of the fight; Disintegration modelled as 6, then 7, then 8 at the end of each turn (not summed).

| Curse always taken | Win | HP lost | Median turns |
|---|---|---|---|
| Sloth | 46% | 67.3 | 11.0 |
| Mind Rot | 30% | 73.7 | 11.0 |
| Waste Away | 14% | 78.5 | 10.0 |
| Disintegration | 10% | 79.3 | 7.0 |

Reading: the order matches the playbook's choice rule (Sloth first, Disintegration last).
