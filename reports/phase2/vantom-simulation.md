# Boss Simulations (Vantom, Knowledge Demon)

Built by `tools/simulate_fight.py --report` (300 simulated fights per row and mode, from 80/80 HP). Each turn's plays are chosen by `tools/plan_turn.py`; Vantom follows its documented cycle (Ink Blot 7, Inky Lance 6x2, Dismember 27 + 3 Wounds, Prepare +2 Strength; 173 HP; 9 Slippery). Card values are v0.111.1. No relics, potions or upgrades. `[HYPOTHESIS]`: a model, useful for comparing additions to the same deck, not for absolute win rates.

| Base deck + two cards | Win (balanced) | HP lost (balanced) | Win (safe) | HP lost (safe) |
|---|---|---|---|---|
| base deck (15 cards) | 79% | 68.6 | 59% | 71.3 |
| + Twin Strike, Sword Boomerang (multi-hit) | 99% | 62.8 | 92% | 59.7 |
| + Pommel Strike, Battle Trance (draw) | 73% | 71.1 | 84% | 63.8 |
| + Shrug It Off, Flame Barrier (block) | 68% | 71.6 | 81% | 67.2 |
| + Demon Form, Shrug It Off (scaling) | 99% | 56.2 | 79% | 62.0 |
| + Strike x2 (control) | 70% | 72.8 | 47% | 75.0 |
| + Thunderclap, Breakthrough (single-hit hit-all) | 72% | 72.1 | 44% | 75.8 |
| + Breakthrough x2 (single-hit hit-all) | 64% | 73.8 | 32% | 77.5 |

## Reading (computed from the table above; seeds are fixed, so the run reproduces)

- **Best additions** (both plans together): Twin Strike, Sword Boomerang and Demon Form, Shrug It Off. Multi-hit: 99% balanced / 92% safe against the base deck's 79% / 59%; Demon Form with Shrug It Off 99% / 79%.
- **Two Breakthroughs against two plain Strikes**: 64% against 70% balanced, 32% against 47% safe (Breakthrough's 9 is capped to 1 while Slippery lasts, and it costs HP). Thunderclap with Breakthrough: 72% / 44%.
- **Draw and block**: draw 73% / 84%, block 68% / 81%, against the base 79% / 59%: their value depends on the plan.
- Plan choice: see the plan-mode section below.

## Calibration against the Player's record

The 15-card base deck for Act 1 bosses and the 22-card Act 2 deck for Knowledge Demon, at 60/80 HP, the better plan; the Player's Ironclad boss fights on v0.107.1 (real decks are bigger and have relics, potions and upgrades, so the model is expected to be pessimistic; what matters is the ratio between bosses). A boss marked **no** is not used by `tools/draft.py`.

| Boss | Model win | The Player survived | Used in drafting |
|---|---|---|---|
| Vantom | 24% | 4/10 (40%) | yes |
| Lagavulin Matriarch | 36% | 6/8 (75%) | yes |
| Ceremonial Beast | 2% | 5/6 (83%) | **no** |
| Knowledge Demon | 31% | 8/12 (67%) | **no** |
| Entomancer | 0% | 10/13 (77%) | **no** |

## Which plan to follow in a boss fight

Win rate when every turn follows the balanced plan, the safe plan below half HP and balanced above, or the safe plan. Plans that would leave you at 0 HP are ranked last in every mode (survival guard).

| Fight | Start HP | Balanced | Safe below 50% | Safe |
|---|---|---|---|---|
| Vantom, base deck | 80/80 | 76% | 75% | 57% |
| Vantom, base deck | 60/80 | 24% | 20% | 17% |
| Vantom, base + Twin Strike + Shrug It Off | 80/80 | 89% | 82% | 83% |
| Vantom, base + Twin Strike + Shrug It Off | 60/80 | 43% | 33% | 37% |
| Lagavulin Matriarch, base deck | 80/80 | 93% | 90% | 60% |
| Lagavulin Matriarch, base deck | 60/80 | 36% | 29% | 27% |

Reading: in these boss fights the balanced plan was best or level in every row; switching to safe at low HP did not help.

## Knowledge Demon: which curse to take

A 22-card end-of-Act-2 deck (two Inflames, Demon Form, two Twin Strikes, Impervious, Offering and others) at 80/80 HP; each row always takes the same curse when offered (the real choice is one of two each time). Cycle: Curse of Knowledge, Slap 17, Knowledge Overwhelming 8x3, Ponder 11 + heal 30 + 2 Strength (heal single-source); curses stack for the rest of the fight; Disintegration modelled as 6, then 7, then 8 at the end of each turn (not summed).

| Curse always taken | Win | HP lost | Median turns |
|---|---|---|---|
| Sloth | 46% | 67.3 | 11.0 |
| Mind Rot | 30% | 73.7 | 11.0 |
| Waste Away | 14% | 78.5 | 10.0 |
| Disintegration | 10% | 79.3 | 7.0 |

Reading: the order matches the playbook's choice rule (Sloth first, Disintegration last).
