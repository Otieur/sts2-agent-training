# Silent Cards

Source: `knowledge/data/extract-2026-09-21/cards.json` `[GAME-EXTRACT]` (decompiled game data, build not stated, possibly newer than v0.107.1). Numbers are base values; `?` is computed at play time. Picked/offered and the head-to-head score come from the Player's card reward screens (Phase 1, v0.107.1) `[PLAYER-DATA]` and describe habit, not strength. ▲ = scored above skipping, ▼ = below.

Tags are derived from the effect text by `tools/import_extract.py` (multi-hit, aoe, zero-cost, x-cost, draw, energy, block, strength, vulnerable, weak, self-damage, exhaust-other, power, upgrade).

## Basic (4)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Neutralize | 0 | Attack | Basic | Deal 3 damage; Apply 1 Weak to the target | damage, weak, zero-cost | - | - | - |
| Strike Silent | 1 | Attack | Basic | Deal 6 damage | damage | - | - | - |
| Defend Silent | 1 | Skill | Basic | Gain 5 Block | block | - | - | - |
| Survivor | 1 | Skill | Basic | Gain 8 Block; Discard 1 card from your hand; Discard a card | block | - | - | - |

## Common (20)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Dagger Spray | 1 | Attack | Common | Deal 4 damage 2 times to ALL enemies | aoe, damage, multi-hit | 10/40 | 25% | -0.27 ▲ |
| Dagger Throw | 1 | Attack | Common | Deal 9 damage; Draw 1 card; Discard 1 card from your hand; Discard a card | damage, draw | 24/49 | 49% | +0.84 ▲ |
| Flick Flack | 1 | Attack | Common | Deal 7 damage to ALL enemies; keywords: Sly | aoe, damage | 17/54 | 31% | +0.24 ▲ |
| Leading Strike | 1 | Attack | Common | Deal 7 damage; Add 1 Shiv to your hand | damage | 9/54 | 17% | -1.08 ▼ |
| Poisoned Stab | 1 | Attack | Common | Deal 6 damage; Apply 3 Poison to the target | damage | 4/65 | 6% | -1.87 ▼ |
| Ricochet | 2 | Attack | Common | Deal 3 damage 4 times to a random enemy; keywords: Sly | damage, multi-hit, random-target | 24/47 | 51% | +1.07 ▲ |
| Slice | 0 | Attack | Common | Deal 6 damage | damage, zero-cost | 3/48 | 6% | -2.00 ▼ |
| Sucker Punch | 1 | Attack | Common | Deal 8 damage; Apply 1 Weak to the target | damage, weak | 8/58 | 14% | -1.31 ▼ |
| Acrobatics | 1 | Skill | Common | Draw 3 cards; Discard 1 card from your hand; Discard a card | draw | 21/29 | 72% | +2.13 ▲ |
| Anticipate | 0 | Skill | Common | Gain 3 Anticipate | zero-cost | 3/46 | 7% | -1.58 ▼ |
| Backflip | 1 | Skill | Common | Gain 5 Block; Draw 2 cards | block, draw | 8/46 | 17% | -0.86 ▼ |
| Blade Dance | 1 | Skill | Common | Add 3 Shivs to your hand; keywords: Exhaust | - | 14/46 | 30% | -0.07 ▲ |
| Cloak And Dagger | 1 | Skill | Common | Gain 6 Block; Add 1 Shiv to your hand | block | 5/53 | 9% | -1.59 ▼ |
| Deadly Poison | 1 | Skill | Common | Apply 5 Poison to the target | - | 4/52 | 8% | -1.99 ▼ |
| Deflect | 0 | Skill | Common | Gain 4 Block | block, zero-cost | 1/54 | 2% | -2.99 ▼ |
| Dodge And Roll | 1 | Skill | Common | Gain 4 Block; Gain ? Block Next Turn | block | 1/39 | 3% | -2.41 ▼ |
| Piercing Wail | 1 | Skill | Common | Apply 6 Piercing Wail to the target; keywords: Exhaust | aoe | 24/56 | 43% | +0.49 ▲ |
| Prepared | 0 | Skill | Common | Draw 1 card; Discard a card | draw, zero-cost | 23/44 | 52% | +0.77 ▲ |
| Snakebite | 2 | Skill | Common | Apply 7 Poison to the target; keywords: Retain | - | 0/43 | 0% | -4.11 ▼ |
| Untouchable | 2 | Skill | Common | Gain 9 Block; keywords: Sly | block | 19/40 | 48% | +1.04 ▲ |

## Uncommon (36)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Backstab | 0 | Attack | Uncommon | Deal 11 damage; keywords: Exhaust, Innate | damage, zero-cost | 6/19 | 32% | -0.21 ▲ |
| Dash | 2 | Attack | Uncommon | Gain 10 Block; Deal 10 damage | block, damage | 5/27 | 19% | -0.88 ▼ |
| Finisher | 1 | Attack | Uncommon | Deal 6 damage ? times | damage, multi-hit | 3/16 | 19% | -0.63 ▲ |
| Flechettes | 1 | Attack | Uncommon | Deal 5 damage ? times | damage, multi-hit | 2/15 | 13% | -1.40 ▼ |
| Follow Through | 1 | Attack | Uncommon | Deal 6 damage to ALL enemies; Apply 1 Weak to the target | aoe, damage, weak | - | - | - |
| Memento Mori | 1 | Attack | Uncommon | Deal ? damage | damage | 9/16 | 56% | +0.91 ▲ |
| Pinpoint | 3 | Attack | Uncommon | Deal 17 damage | damage | 7/13 | 54% | +0.75 ▲ |
| Pounce | 2 | Attack | Uncommon | Deal 12 damage; Gain 1 Free Skill | damage | 8/16 | 50% | +0.71 ▲ |
| Precise Cut | 0 | Attack | Uncommon | Deal ? damage | damage, zero-cost | 6/16 | 38% | +0.29 ▲ |
| Predator | 2 | Attack | Uncommon | Deal 15 damage; Gain 2 Draw Cards Next Turn | damage | 5/44 | 11% | -1.35 ▼ |
| Skewer | 0 | Attack | Uncommon | Deal 7 damage ? times | damage, multi-hit, zero-cost | 0/19 | 0% | -3.38 ▼ |
| Strangle | 1 | Attack | Uncommon | Deal 8 damage; Apply 2 Strangle to the target | damage | 0/15 | 0% | -3.00 ▼ |
| Accuracy | 1 | Power | Uncommon | Gain 4 Accuracy | power | 3/20 | 15% | -0.70 ▲ |
| Footwork | 1 | Power | Uncommon | Gain 2 Dexterity | power | 7/20 | 35% | +0.28 ▲ |
| Infinite Blades | 1 | Power | Uncommon | Gain 1 Infinite Blades | power | 3/20 | 15% | -0.68 ▲ |
| Noxious Fumes | 1 | Power | Uncommon | Gain 2 Noxious Fumes | power | 1/10 | 10% | -0.89 ▼ |
| Outbreak | 1 | Power | Uncommon | Gain 11 Outbreak | power | 4/14 | 29% | -0.26 ▲ |
| Phantom Blades | 1 | Power | Uncommon | Gain 9 Phantom Blades | power | 2/17 | 12% | -0.99 ▼ |
| Speedster | 2 | Power | Uncommon | Gain 2 Speedster | power | 2/16 | 12% | -0.91 ▼ |
| Well Laid Plans | 1 | Power | Uncommon | Gain 1 Well Laid Plans | power | 3/23 | 13% | -1.23 ▼ |
| Blur | 1 | Skill | Uncommon | Gain 5 Block; Gain 1 Blur | block | 1/16 | 6% | -2.13 ▼ |
| Bouncing Flask | 2 | Skill | Uncommon | Apply 3 Poison to the target | random-target | 0/12 | 0% | -2.58 ▼ |
| Bubble Bubble | 1 | Skill | Uncommon | Apply 9 Poison to the target | - | 4/16 | 25% | -0.09 ▲ |
| Calculated Gamble | 0 | Skill | Uncommon | Discard your hand and draw that many cards; keywords: Exhaust | zero-cost | 14/28 | 50% | +0.96 ▲ |
| Escape Plan | 0 | Skill | Uncommon | Draw 1 card; Gain 3 Block | block, draw, zero-cost | 18/23 | 78% | +2.01 ▲ |
| Expertise | 1 | Skill | Uncommon | Draw ? cards | draw | 6/19 | 32% | +0.08 ▲ |
| Expose | 0 | Skill | Uncommon | Lose all Block; Remove Artifact from the target; Apply 2 Vulnerable to the target; keywords: Exhaust | block, vulnerable, zero-cost | 14/18 | 78% | +2.20 ▲ |
| Flanking | 2 | Skill | Uncommon | Apply 2 Flanking to the target | - | - | - | - |
| Hand Trick | 1 | Skill | Uncommon | Gain 7 Block; Choose a card in your hand; apply Single Turn Sly | block | 4/10 | 40% | +0.90 ▲ |
| Haze | 3 | Skill | Uncommon | Apply 4 Poison to the target; keywords: Sly | aoe | 10/16 | 62% | +1.29 ▲ |
| Hidden Daggers | 0 | Skill | Uncommon | Discard a card; Add 2 Shivs to your hand; Upgrade a card | upgrade, zero-cost | 4/9 | 44% | +0.84 ▲ |
| Leg Sweep | 2 | Skill | Uncommon | Gain 11 Block; Apply 2 Weak to the target | block, weak | 11/26 | 42% | +0.54 ▲ |
| Mirage | 1 | Skill | Uncommon | Gain ? Block; keywords: Exhaust | block | 0/7 | 0% | -2.28 ▼ |
| Reflex | 3 | Skill | Uncommon | Draw 2 cards; keywords: Sly | draw | 6/7 | 86% | +2.27 ▲ |
| Tactician | 3 | Skill | Uncommon | Gain 1 Energy; keywords: Sly | energy | 16/17 | 94% | +2.68 ▲ |
| Up My Sleeve | 2 | Skill | Uncommon | Add 3 Shivs to your hand | - | 2/19 | 11% | -1.41 ▼ |

## Rare (26)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Assassinate | 0 | Attack | Rare | Deal 10 damage; Apply 1 Vulnerable to the target; keywords: Innate, Exhaust | damage, vulnerable, zero-cost | 3/10 | 30% | +0.77 ▲ |
| Echoing Slash | 1 | Attack | Rare | Deal 10 damage to the target | aoe, damage | 3/9 | 33% | +0.87 ▲ |
| Grand Finale | 0 | Attack | Rare | Deal 50 damage to ALL enemies | aoe, damage, zero-cost | 1/9 | 11% | -0.39 ▲ |
| Murder | 3 | Attack | Rare | Deal ? damage | damage | 5/8 | 62% | +1.96 ▲ |
| The Hunt | 1 | Attack | Rare | Deal 10 damage; Gain 1 The Hunt; keywords: Exhaust | damage | 3/11 | 27% | +0.39 ▲ |
| Abrasive | 3 | Power | Rare | Gain 1 Dexterity; Gain 4 Thorns; keywords: Sly | power | 9/10 | 90% | +3.27 ▲ |
| Accelerant | 1 | Power | Rare | Gain 1 Accelerant | power | 4/11 | 36% | +0.97 ▲ |
| Afterimage | 1 | Power | Rare | Gain 1 Afterimage | power | 5/9 | 56% | +1.55 ▲ |
| Envenom | 2 | Power | Rare | Gain 1 Envenom | power | 2/8 | 25% | +0.32 ▲ |
| Fan Of Knives | 2 | Power | Rare | Gain 1 Fan Of Knives; Add 4 Shivs to your hand | power | 0/8 | 0% | -1.57 ▼ |
| Master Planner | 2 | Power | Rare | Gain 1 Master Planner | power | 3/8 | 38% | +1.00 ▲ |
| Serpent Form | 3 | Power | Rare | Gain 4 Serpent Form | power | 5/9 | 56% | +1.55 ▲ |
| Sneaky | 2 | Power | Rare | Gain 1 Sneaky; keywords: Sly | power | - | - | - |
| Tools Of The Trade | 1 | Power | Rare | Gain 1 Tools Of The Trade | power | 8/10 | 80% | +2.69 ▲ |
| Tracking | 2 | Power | Rare | Gain 1 Tracking; Gain 2 Tracking | power | 6/9 | 67% | +2.28 ▲ |
| Adrenaline | 0 | Skill | Rare | Gain 1 Energy; Draw 2 cards; keywords: Exhaust | draw, energy, zero-cost | 4/9 | 44% | +1.29 ▲ |
| Blade Of Ink | 1 | Skill | Rare | Gain 2 Blade Of Ink | - | 4/10 | 40% | +1.20 ▲ |
| Bullet Time | 3 | Skill | Rare | Gain 1 No Draw | - | 0/11 | 0% | -2.11 ▼ |
| Burst | 1 | Skill | Rare | Gain 1 Burst | - | 2/4 | 50% | +1.65 ▲ |
| Corrosive Wave | 1 | Skill | Rare | Gain 3 Corrosive Wave | - | 4/9 | 44% | +0.52 ▲ |
| Knife Trap | 2 | Skill | Rare | if upgraded: Upgrade a card; Auto-play a card | upgrade | 2/13 | 15% | -0.41 ▲ |
| Malaise | X | Skill | Rare | Apply -X (energy spent) Strength to the target; Apply X (energy spent) Weak to the target; keywords: Exhaust | strength, weak, x-cost | 3/8 | 38% | +0.57 ▲ |
| Nightmare | 3 | Skill | Rare | Choose a card in your hand; Gain 3 Nightmare; keywords: Exhaust | - | 2/10 | 20% | +0.07 ▲ |
| Shadow Step | 1 | Skill | Rare | Discard a card; Gain 1 Shadow Step | - | 4/4 | 100% | +3.25 ▲ |
| Shadowmeld | 1 | Skill | Rare | Gain 1 Shadowmeld | - | 5/12 | 42% | +1.41 ▲ |
| Storm Of Steel | 1 | Skill | Rare | Discard a card; Add ? Shivs to your hand; Upgrade a card | upgrade | 5/8 | 62% | +2.01 ▲ |

## Ancient (2)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Suppress | 0 | Attack | Ancient | Deal 11 damage; Apply 3 Weak to the target; keywords: Innate | damage, weak, zero-cost | - | - | - |
| Wraith Form | 3 | Power | Ancient | Gain 2 Intangible; Gain 1 Wraith Form | power | - | - | - |

## Role index

- **Multi-hit attacks:** Dagger Spray (10/40), Ricochet (24/47), Finisher (3/16), Flechettes (2/15), Skewer (0/19)
- **Hits all enemies:** Dagger Spray (10/40), Flick Flack (17/54), Piercing Wail (24/56), Follow Through, Haze (10/16), Echoing Slash (3/9), Grand Finale (1/9)
- **0-cost cards:** Slice (3/48), Anticipate (3/46), Deflect (1/54), Prepared (23/44), Backstab (6/19), Precise Cut (6/16), Skewer (0/19), Calculated Gamble (14/28), Escape Plan (18/23), Expose (14/18), Hidden Daggers (4/9), Assassinate (3/10), Grand Finale (1/9), Adrenaline (4/9), Suppress
- **X-cost cards:** Malaise (3/8)
- **Card draw:** Dagger Throw (24/49), Acrobatics (21/29), Backflip (8/46), Prepared (23/44), Escape Plan (18/23), Expertise (6/19), Reflex (6/7), Adrenaline (4/9)
- **Energy:** Tactician (16/17), Adrenaline (4/9)
- **Strength:** Malaise (3/8)
- **Applies Vulnerable:** Expose (14/18), Assassinate (3/10)
- **Applies Weak:** Sucker Punch (8/58), Follow Through, Leg Sweep (11/26), Malaise (3/8), Suppress
- **Powers:** Accuracy (3/20), Footwork (7/20), Infinite Blades (3/20), Noxious Fumes (1/10), Outbreak (4/14), Phantom Blades (2/17), Speedster (2/16), Well Laid Plans (3/23), Abrasive (9/10), Accelerant (4/11), Afterimage (5/9), Envenom (2/8), Fan Of Knives (0/8), Master Planner (3/8), Serpent Form (5/9), Sneaky, Tools Of The Trade (8/10), Tracking (6/9), Wraith Form
