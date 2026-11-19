# Boss Simulations (Vantom, Knowledge Demon)

Built by `tools/simulate_fight.py --report` (300 simulated fights per row and mode, from 80/80 HP). Each turn's plays are chosen by `tools/plan_turn.py`; Vantom follows its documented cycle (Ink Blot 7, Inky Lance 6x2, Dismember 27 + 3 Wounds, Prepare +2 Strength; 173 HP; 9 Slippery). Card values are v0.111.1. No relics, potions or upgrades. `[HYPOTHESIS]`: a model, useful for comparing additions to the same deck, not for absolute win rates.

| Base deck + two cards | Win (balanced) | HP lost (balanced) | Win (safe) | HP lost (safe) |
|---|---|---|---|---|
| base deck (15 cards) | 84% | 67.1 | 59% | 71.3 |
| + Twin Strike, Sword Boomerang (multi-hit) | 98% | 65.2 | 92% | 59.7 |
| + Pommel Strike, Battle Trance (draw) | 78% | 70.9 | 84% | 63.8 |
| + Shrug It Off, Flame Barrier (block) | 76% | 68.6 | 90% | 64.6 |
| + Demon Form, Shrug It Off (scaling) | 100% | 57.0 | 79% | 62.0 |
| + Strike x2 (control) | 73% | 72.3 | 47% | 75.0 |
| + Thunderclap, Breakthrough (single-hit hit-all) | 85% | 70.8 | 44% | 75.8 |
| + Breakthrough x2 (single-hit hit-all) | 77% | 72.4 | 32% | 77.5 |

## Reading (computed from the table above; seeds are fixed, so the run reproduces)

- **Best additions** (both plans together): Twin Strike, Sword Boomerang and Demon Form, Shrug It Off. Multi-hit: 98% balanced / 92% safe against the base deck's 84% / 59%; Demon Form with Shrug It Off 100% / 79%.
- **Two Breakthroughs against two plain Strikes**: 77% against 73% balanced, 32% against 47% safe (Breakthrough's 9 is capped to 1 while Slippery lasts, and it costs HP). Thunderclap with Breakthrough: 85% / 44%.
- **Draw and block**: draw 78% / 84%, block 76% / 90%, against the base 84% / 59%: their value depends on the plan.
- Plan choice: see the plan-mode section below.

## Calibration against the Player's record

The 15-card base deck for Act 1 fights and the 22-card Act 2 deck for Act 2 fights (Knowledge Demon, Entomancer), at 60/80 HP, the better plan; the Player's Ironclad boss fights on v0.107.1 (real decks are bigger and have relics, potions and upgrades, so the model is expected to be pessimistic; what matters is the ratio between bosses). A boss marked **no** is not used by `tools/draft.py`.

| Boss | Model win | The Player survived | Used in drafting |
|---|---|---|---|
| Vantom | 31% | 4/10 (40%) | yes |
| Lagavulin Matriarch | 36% | 6/8 (75%) | yes |
| Ceremonial Beast | 9% | 5/6 (83%) | **no** |
| Knowledge Demon | 19% | 8/12 (67%) | **no** |
| Entomancer | 10% | 10/13 (77%) | **no** |
| Byrdonis | 100% | 7/10 (70%) | yes |
| Soul Fysh | 50% | 4/7 (57%) | yes |
| Waterfall Giant | 14% | 3/5 (60%) | **no** |
| The Kin | 1% | 8/8 (100%) | **no** |

## Calibration with the Player's own decks

Each of the Player's Ironclad fights against a modelled boss or elite (v0.107.1, solo, finished runs), replayed with the deck the run had on arrival (with its upgrades), its arrival HP, the potions it held and the relics the simulator applies (`SIM_RELICS`: Vajra, Anchor, Gorget and others), the better of the two plans. It has no other relics and only the card effects `tools/plan_turn.py` reads (Powers other than Strength, Dexterity, Demon Form, Pyre and Feel No Pain do nothing), and the planner looks one turn ahead, so its boss win rates for real decks are far too low; the share of the boss's HP removed is the more useful comparison between bosses. The short elite fight (Byrdonis) comes out close to the record, so the gap grows with fight length, as missing scaling effects would make it.

| Fight | Fights | Model win | Boss HP removed (model) | The Player survived |
|---|---|---|---|---|
| Vantom | 10 | 2% | 0.46 | 4/10 (40%) |
| Lagavulin Matriarch | 8 | 6% | 0.75 | 6/8 (75%) |
| Ceremonial Beast | 6 | 0% | 0.41 | 5/6 (83%) |
| Knowledge Demon | 12 | 3% | 0.36 | 8/12 (67%) |
| Entomancer | 13 | 0% | 0.26 | 10/13 (77%) |
| Byrdonis | 10 | 65% | 0.93 | 7/10 (70%) |
| Soul Fysh | 7 | 0% | 0.57 | 4/7 (57%) |
| Waterfall Giant | 5 | 2% | 0.69 | 3/5 (60%) |
| The Kin | 8 | 0% | 0.53 | 8/8 (100%) |

Reading: absolute win rates from the simulator mean little for real decks; use it to compare additions to the same deck. A boss whose share removed is low while the Player usually survived (Ceremonial Beast, Entomancer, Knowledge Demon) is modelled too hard.

## Which plan to follow in a boss fight

Win rate when every turn follows the balanced plan, the safe plan below half HP and balanced above, or the safe plan. Plans that would leave you at 0 HP are ranked last in every mode (survival guard).

| Fight | Start HP | Balanced | Safe below 50% | Safe |
|---|---|---|---|---|
| Vantom, base deck | 80/80 | 83% | 81% | 57% |
| Vantom, base deck | 60/80 | 31% | 23% | 17% |
| Vantom, base + Twin Strike + Shrug It Off | 80/80 | 94% | 91% | 83% |
| Vantom, base + Twin Strike + Shrug It Off | 60/80 | 50% | 43% | 37% |
| Lagavulin Matriarch, base deck | 80/80 | 93% | 90% | 60% |
| Lagavulin Matriarch, base deck | 60/80 | 36% | 29% | 27% |
| Soul Fysh, base deck | 80/80 | 91% | 88% | 94% |
| Soul Fysh, base deck | 60/80 | 27% | 47% | 50% |
| Waterfall Giant, base deck | 80/80 | 51% | 69% | 69% |
| Waterfall Giant, base deck | 60/80 | 1% | 8% | 14% |

Reading (computed): the safe plan beat the balanced plan by 10 points or more in 3 rows (Soul Fysh, Waterfall Giant); in the other 7 rows the balanced plan was better, level, or within 10 points.

## Soul Fysh and Waterfall Giant: which additions help

From 60/80 HP, the better of the balanced and safe plans per row. Soul Fysh: Beckon (a 6 HP Beckon into the draw and discard piles), De-Gas 16, Gaze 7 + Beckon, Fade (Intangible for your next turn), Scream 13 + 3 Vulnerable on you; a held Beckon costs 6 HP at the end of your turn and can be played for 1 energy. Waterfall Giant: Pressurize (+15 Steam Eruption), then Stomp 15 + Weak, Ram 10, Siphon (heal 10), Pressure Gun 20 (+5 a use), Pressure Up 13, each +3 Steam; at 0 HP a stun turn, then an explosion for its Steam Eruption. Cycles `[COMMUNITY]` (Waterfall Giant: one guide for the full cycle). Exhaust cards remove a held Beckon (or another status or curse) first.

| Base deck + two cards | Soul Fysh win | HP lost | Waterfall Giant win | HP lost |
|---|---|---|---|---|
| base deck (15 cards) | 51% | 53.4 | 14% | 59.1 |
| + Twin Strike, Sword Boomerang (multi-hit) | 57% | 52.8 | 11% | 59.3 |
| + Pommel Strike, Battle Trance (draw) | 47% | 53.8 | 22% | 58.2 |
| + Shrug It Off, Flame Barrier (block) | 47% | 54.5 | 25% | 58.7 |
| + Demon Form, Shrug It Off (scaling) | 87% | 47.9 | 51% | 49.7 |
| + Strike x2 (control) | 28% | 57.0 | 0% | 60.0 |
| + Thunderclap, Breakthrough (single-hit hit-all) | 24% | 57.8 | 1% | 60.0 |
| + Breakthrough x2 (single-hit hit-all) | 22% | 59.4 | 0% | 60.0 |
| + True Grit, Burning Pact (exhaust) | 33% | 58.0 | 7% | 59.6 |
| + Pyre, Feel No Pain (powers) | 63% | 50.3 | 31% | 57.0 |

## Byrdonis: which plan against an elite that scales

Byrdonis (91 HP; Peck 3x3 and Swoop 16 alternating; +1 Strength each turn, order and amount `[HYPOTHESIS]`). Calibration: the base deck loses about 26–29 HP here; the Player's Ironclad decks lost 25.8 on average (10 fights).

| Deck | Start HP | Balanced: win (HP lost) | Safe below 50% | Safe |
|---|---|---|---|---|
| starter + Twin Strike + Pommel Strike (12 cards) | 56/80 | 96% (50 HP) | 34% (53 HP) | 6% (56 HP) |
| starter + Twin Strike + Pommel Strike (12 cards) | 70/80 | 100% (51 HP) | 98% (50 HP) | 36% (66 HP) |
| base deck (15 cards) | 56/80 | 100% (29 HP) | 100% (26 HP) | 100% (26 HP) |
| base deck (15 cards) | 70/80 | 100% (29 HP) | 100% (29 HP) | 100% (26 HP) |

Reading: blocking instead of attacking lets the Strength snowball. With a weak deck the safe plan collapses; with a strong deck it saves a few HP. Against enemies that scale every turn, follow the balanced plan.

## The Kin: race the Priest or clear the followers

Kin Priest (190 HP; Orb of Frailty 8 + Frail, Orb of Weakness 8 + Weak, Beam 3x3, Ritual +2 Strength) with two Minion followers (58 HP; Quick Slash 5, Boomerang 2x2, Power Dance +2 Strength); killing the Priest ends the fight. Cycles `[HYPOTHESIS]`; the model is far too hard for this boss (the Player survived 8 of 8), so read only the comparison. From full HP, the better plan per row.

| Deck | Every single-target card at the Priest | The planner's own targets |
|---|---|---|
| base deck (15 cards) | 38% (77 HP) | 31% (78 HP) |
| + Thunderclap, Conflagration (hit-all) | 63% (75 HP) | 77% (73 HP) |

Reading (computed): single-target deck: racing the Priest 38% against 31%; with two hit-all cards: the planner's targets (clearing followers) 77% against racing 63%.

## Knowledge Demon: which curse to take

A 22-card end-of-Act-2 deck (two Inflames, Demon Form, two Twin Strikes, Impervious, Offering and others) at 80/80 HP. Each Curse of Knowledge offers Disintegration or one other card: Mind Rot, then Sloth, then Waste Away (one guide); the table tries all eight combinations. Disintegration deals 6, 7 or 8 at the end of each turn depending on the offer, and the amounts add up if taken more than once. Cycle (two guides): Curse of Knowledge, Slap 17, Knowledge Overwhelming 8x3, Ponder 11 + heal 30 + 2 Strength, three times, then the last three repeating.

| Offer 1 / offer 2 / offer 3 | Win | HP lost | Median turns |
|---|---|---|---|
| Mind Rot / Sloth / Waste Away | 35% | 71.9 | 11.0 |
| Mind Rot / Sloth / Disintegration | 31% | 73.4 | 10.0 |
| Mind Rot / Disintegration / Waste Away | 16% | 78.4 | 9.0 |
| Mind Rot / Disintegration / Disintegration | 15% | 78.7 | 9.0 |
| Disintegration / Sloth / Waste Away | 5% | 79.8 | 7.0 |
| Disintegration / Sloth / Disintegration | 5% | 79.8 | 7.0 |
| Disintegration / Disintegration / Waste Away | 2% | 79.8 | 7.0 |
| Disintegration / Disintegration / Disintegration | 2% | 79.8 | 7.0 |

Reading (computed): best combination Mind Rot / Sloth / Waste Away; offer 1: Mind Rot (35%) over Disintegration (5%); offer 2: Sloth (35%) over Disintegration (16%); offer 3: Waste Away (35%) over Disintegration (31%).
