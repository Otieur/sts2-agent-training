# Regent Cards

Source: `knowledge/data/extract-2026-09-21/cards.json` `[GAME-EXTRACT]` (decompiled game data, build not stated, possibly newer than v0.107.1). Numbers are base values; `?` is computed at play time. Picked/offered and the head-to-head score come from the Player's card reward screens (Phase 1, v0.107.1) `[PLAYER-DATA]` and describe habit, not strength. ▲ = scored above skipping, ▼ = below.

Tags are derived from the effect text by `tools/import_extract.py` (multi-hit, aoe, zero-cost, x-cost, draw, energy, block, strength, vulnerable, weak, self-damage, exhaust-other, power, upgrade).

## Basic (4)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Falling Star | 0 | Attack | Basic | Deal 7 damage; Apply 1 Weak to the target; Apply 1 Vulnerable to the target | damage, vulnerable, weak, zero-cost | - | - | - |
| Strike Regent | 1 | Attack | Basic | Deal 6 damage | damage | - | - | - |
| Defend Regent | 1 | Skill | Basic | Gain 5 Block | block | - | - | - |
| Venerate | 1 | Skill | Basic | Gain 2 Stars | - | - | - | - |

## Common (20)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Astral Pulse | 0 | Attack | Common | Deal 14 damage to ALL enemies | aoe, damage, zero-cost | 7/33 | 21% | -0.60 ▲ |
| Begone | 1 | Attack | Common | Deal 4 damage; Choose a card in your hand; if upgraded: Upgrade a card; Transform a card | damage, upgrade | 7/45 | 16% | -1.05 ▼ |
| Celestial Might | 2 | Attack | Common | Deal 6 damage 3 times | damage, multi-hit | 2/61 | 3% | -2.57 ▼ |
| Collision Course | 0 | Attack | Common | Deal 9 damage; Add a generated card to your hand | damage, zero-cost | 1/52 | 2% | -3.05 ▼ |
| Crescent Spear | 1 | Attack | Common | Deal ? damage | damage | 7/49 | 14% | -1.13 ▼ |
| Crush Under | 1 | Attack | Common | Deal 7 damage to ALL enemies; Apply 1 Crush Under to the target | aoe, damage | 9/56 | 16% | -1.01 ▼ |
| Guiding Star | 1 | Attack | Common | Deal 12 damage; Gain 2 Draw Cards Next Turn | damage | 5/52 | 10% | -1.48 ▼ |
| Photon Cut | 1 | Attack | Common | Deal 10 damage; Draw 1 card; Put a card into your draw pile | damage, draw | 9/39 | 23% | -0.56 ▲ |
| Solar Strike | 1 | Attack | Common | Deal 8 damage; Gain 1 Stars | damage | 6/53 | 11% | -1.44 ▼ |
| Wrought In War | 1 | Attack | Common | Deal 7 damage; Forge 5 | damage | 8/49 | 16% | -1.11 ▼ |
| Cloak Of Stars | 0 | Skill | Common | Gain 7 Block | block, zero-cost | 13/50 | 26% | -0.41 ▲ |
| Cosmic Indifference | 1 | Skill | Common | Gain 6 Block; Choose a card from a pile; Put a card into your draw pile | block | 30/62 | 48% | +0.61 ▲ |
| Gather Light | 1 | Skill | Common | Gain 7 Block; Gain 1 Stars | block | 12/46 | 26% | -0.45 ▲ |
| Glitterstream | 2 | Skill | Common | Gain 11 Block; Gain ? Block Next Turn | block | 5/45 | 11% | -1.43 ▼ |
| Glow | 1 | Skill | Common | Gain 1 Stars; Draw 2 cards | draw | 18/64 | 28% | -0.19 ▲ |
| Hidden Cache | 1 | Skill | Common | Gain 1 Stars; Gain 3 Star Next Turn | - | 20/53 | 38% | +0.13 ▲ |
| Know Thy Place | 0 | Skill | Common | Apply 1 Weak to the target; Apply 1 Vulnerable to the target; keywords: Exhaust | vulnerable, weak, zero-cost | 15/56 | 27% | -0.44 ▲ |
| Patter | 1 | Skill | Common | Gain 8 Block; Gain 2 Vigor | block | 1/36 | 3% | -2.75 ▼ |
| Refine Blade | 1 | Skill | Common | Forge 6; Gain 1 Energy Next Turn | energy | 12/56 | 21% | -0.66 ▲ |
| Spoils Of Battle | 1 | Skill | Common | Forge 10 | - | 14/30 | 47% | +0.67 ▲ |

## Uncommon (36)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Devastate | 1 | Attack | Uncommon | Deal 30 damage | damage | 5/20 | 25% | -0.14 ▲ |
| Gamma Blast | 0 | Attack | Uncommon | Deal 13 damage; Apply 2 Weak to the target; Apply 2 Vulnerable to the target | damage, vulnerable, weak, zero-cost | 5/11 | 45% | +0.53 ▲ |
| Hegemony | 2 | Attack | Uncommon | Deal 15 damage; Gain 2 Energy Next Turn | damage, energy | 7/20 | 35% | +0.36 ▲ |
| Kingly Kick | 4 | Attack | Uncommon | Deal 24 damage | damage | 3/23 | 13% | -1.47 ▼ |
| Kingly Punch | 1 | Attack | Uncommon | Deal 8 damage | damage | 2/10 | 20% | -0.80 ▼ |
| Knockout Blow | 3 | Attack | Uncommon | Deal 30 damage; Gain 5 Stars | damage | 2/19 | 11% | -1.02 ▼ |
| Lunar Blast | 0 | Attack | Uncommon | Deal 4 damage ? times | damage, multi-hit, zero-cost | 2/14 | 14% | -0.83 ▼ |
| Radiate | 0 | Attack | Uncommon | Deal 3 damage ? times to ALL enemies | aoe, damage, multi-hit, zero-cost | 3/20 | 15% | -1.02 ▼ |
| Shining Strike | 1 | Attack | Uncommon | Deal 8 damage; Gain 2 Stars; Put a card into your draw pile | damage | 7/17 | 41% | +0.25 ▲ |
| Stardust | 0 | Attack | Uncommon | Deal 5 damage ? times to a random enemy | damage, multi-hit, random-target, zero-cost | 2/16 | 12% | -1.16 ▼ |
| Supermassive | 1 | Attack | Uncommon | Deal ? damage | damage | 1/7 | 14% | -1.48 ▼ |
| Black Hole | 1 | Power | Uncommon | Gain 3 Black Hole | power | 4/21 | 19% | -0.87 ▼ |
| Child Of The Stars | 1 | Power | Uncommon | Gain 2 Child Of The Stars | power | 9/18 | 50% | +0.53 ▲ |
| Furnace | 1 | Power | Uncommon | Gain 4 Furnace | power | 8/16 | 50% | +0.86 ▲ |
| Orbit | 2 | Power | Uncommon | Gain 1 Orbit | power | 13/20 | 65% | +1.60 ▲ |
| Pale Blue Dot | 1 | Power | Uncommon | Gain 1 Pale Blue Dot | power | 7/19 | 37% | +0.02 ▲ |
| Parry | 1 | Power | Uncommon | Gain 6 Parry | power | 9/10 | 90% | +2.08 ▲ |
| Pillar Of Creation | 1 | Power | Uncommon | Gain 3 Pillar Of Creation | power | 1/22 | 5% | -1.97 ▼ |
| Spectrum Shift | 2 | Power | Uncommon | Gain 1 Spectrum Shift | power | 0/18 | 0% | -3.33 ▼ |
| Alignment | 0 | Skill | Uncommon | Gain 2 Energy | energy, zero-cost | 14/19 | 74% | +1.97 ▲ |
| Bulwark | 2 | Skill | Uncommon | Gain 13 Block; Forge 10 | block | 15/19 | 79% | +1.71 ▲ |
| Charge | 1 | Skill | Uncommon | Choose a card from a pile; Transform a card into Minion Strike; Upgrade a card | upgrade | 12/16 | 75% | +1.83 ▲ |
| Conqueror | 1 | Skill | Uncommon | Forge 3; Apply 1 Conqueror to the target | - | 5/14 | 36% | -0.03 ▲ |
| Convergence | 1 | Skill | Uncommon | Gain 1 Retain Hand; Gain 1 Energy Next Turn; Gain 1 Star Next Turn | energy | 4/16 | 25% | -0.46 ▲ |
| Glimmer | 1 | Skill | Uncommon | Draw 3 cards; Choose a card in your hand; Put a card into your draw pile | draw | 7/21 | 33% | +0.08 ▲ |
| Largesse | 0 | Skill | Uncommon | get Distinct For Combat; if upgraded: Upgrade a card; Add a generated card to your hand | upgrade, zero-cost | - | - | - |
| Manifest Authority | 1 | Skill | Uncommon | Gain 7 Block; get Distinct For Combat; if upgraded: Upgrade a card; Add a generated card to your hand | block, upgrade | 2/14 | 14% | -1.01 ▼ |
| Monologue | 0 | Skill | Uncommon | Gain 1 Monologue | zero-cost | 1/23 | 4% | -2.07 ▼ |
| Particle Wall | 0 | Skill | Uncommon | Gain 9 Block | block, zero-cost | 7/24 | 29% | -0.25 ▲ |
| Prophesize | 2 | Skill | Uncommon | Draw 6 cards | draw | 4/18 | 22% | -0.52 ▲ |
| Quasar | 0 | Skill | Uncommon | get Distinct For Combat; if upgraded: Upgrade a card; Choose a card from an offered set; Add a generated card to your hand | upgrade, zero-cost | 6/16 | 38% | +0.22 ▲ |
| Reflect | 1 | Skill | Uncommon | Gain 17 Block; Gain 1 Reflect | block | 3/16 | 19% | -0.98 ▼ |
| Resonance | 1 | Skill | Uncommon | Gain 1 Strength; Apply -1 Strength to the target | aoe, strength | 4/23 | 17% | -1.12 ▼ |
| Royal Gamble | 0 | Skill | Uncommon | Gain 9 Stars; keywords: Exhaust | zero-cost | 11/19 | 58% | +0.71 ▲ |
| Summon Forth | 1 | Skill | Uncommon | Forge 8; Put a card into your hand | draw | 11/15 | 73% | +1.97 ▲ |
| Terraforming | 1 | Skill | Uncommon | Gain 6 Vigor | - | 1/15 | 7% | -2.01 ▼ |

## Rare (26)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Beat Into Shape | 1 | Attack | Rare | Deal 5 damage; Forge ? | damage | 2/3 | 67% | +2.00 ▲ |
| Bombardment | 3 | Attack | Rare | Deal 18 damage; keywords: Exhaust | damage | 1/10 | 10% | -0.41 ▲ |
| Comet | 0 | Attack | Rare | Deal 33 damage; Apply 3 Weak to the target; Apply 3 Vulnerable to the target | damage, vulnerable, weak, zero-cost | 1/5 | 20% | -0.36 ▲ |
| Crash Landing | 1 | Attack | Rare | Deal 21 damage to ALL enemies; Add a generated card to your hand | aoe, damage | 0/4 | 0% | - |
| Dying Star | 1 | Attack | Rare | Deal 9 damage to ALL enemies; Apply 9 Dying Star to the target; keywords: Ethereal | aoe, damage | 9/9 | 100% | +3.92 ▲ |
| Heavenly Drill | X | Attack | Rare | Deal 8 damage X (energy spent) times | damage, multi-hit, x-cost | 0/6 | 0% | -0.60 ▲ |
| Heirloom Hammer | 2 | Attack | Rare | Deal 17 damage; Choose a card in your hand; Add a generated card to your hand | damage | 3/6 | 50% | +1.65 ▲ |
| Make It So | 0 | Attack | Rare | Deal 6 damage | damage, zero-cost | 5/9 | 56% | +1.93 ▲ |
| Seven Stars | 2 | Attack | Rare | Deal 7 damage 7 times to ALL enemies | aoe, damage, multi-hit | 7/9 | 78% | +2.87 ▲ |
| Arsenal | 1 | Power | Rare | Gain 1 Arsenal | power | 2/7 | 29% | +0.40 ▲ |
| Genesis | 2 | Power | Rare | Gain 2 Genesis | power | 1/7 | 14% | +0.09 ▲ |
| Hammer Time | 2 | Power | Rare | Gain 1 Hammer Time | power | - | - | - |
| Monarchs Gaze | 3 | Power | Rare | Gain 1 Monarchs Gaze | power | 2/8 | 25% | +0.20 ▲ |
| Neutron Aegis | 1 | Power | Rare | Gain 8 Plating | power | 4/8 | 50% | +1.53 ▲ |
| Royalties | 1 | Power | Rare | Gain 30 Royalties | power | 0/8 | 0% | -0.92 ▼ |
| Seeking Edge | 1 | Power | Rare | Forge 7; Gain 1 Seeking Edge | power | 7/12 | 58% | +2.22 ▲ |
| Sword Sage | 2 | Power | Rare | Gain 1 Sword Sage | power | 7/9 | 78% | +2.65 ▲ |
| Tyranny | 1 | Power | Rare | Gain 1 Tyranny | power | 1/11 | 9% | -0.55 ▲ |
| Void Form | 3 | Power | Rare | Gain 2 Void Form; End your turn | power | 9/11 | 82% | +2.66 ▲ |
| Big Bang | 0 | Skill | Rare | Draw 1 card; Gain 1 Stars; Gain 1 Energy; Forge 5; keywords: Exhaust | draw, energy, zero-cost | 5/8 | 62% | +1.86 ▲ |
| Bundle Of Joy | 2 | Skill | Rare | get Distinct For Combat; Add a generated card to your hand; keywords: Exhaust | - | 2/9 | 22% | +0.26 ▲ |
| Decisions Decisions | 0 | Skill | Rare | Draw 3 cards; Choose a card in your hand; Auto-play a card; keywords: Exhaust | draw, zero-cost | 6/12 | 50% | +1.62 ▲ |
| Foregone Conclusion | 1 | Skill | Rare | Gain 2 Foregone Conclusion | - | 7/9 | 78% | +2.68 ▲ |
| Guards | 2 | Skill | Rare | Choose a card in your hand; if upgraded: Upgrade a card; Transform a card; keywords: Exhaust | upgrade | 2/8 | 25% | +0.63 ▲ |
| I Am Invincible | 1 | Skill | Rare | Gain 9 Block | block | 2/8 | 25% | +0.20 ▲ |
| The Smith | 1 | Skill | Rare | Forge 30 | - | 4/6 | 67% | +1.65 ▲ |

## Ancient (2)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Meteor Shower | 0 | Attack | Ancient | Deal 14 damage to ALL enemies; Apply 2 Weak to the target; Apply 2 Vulnerable to the target | aoe, damage, vulnerable, weak, zero-cost | - | - | - |
| The Sealed Throne | 1 | Power | Ancient | Gain 1 The Sealed Throne | power | - | - | - |

## Role index

- **Multi-hit attacks:** Celestial Might (2/61), Lunar Blast (2/14), Radiate (3/20), Stardust (2/16), Heavenly Drill (0/6), Seven Stars (7/9)
- **Hits all enemies:** Astral Pulse (7/33), Crush Under (9/56), Radiate (3/20), Resonance (4/23), Crash Landing (0/4), Dying Star (9/9), Seven Stars (7/9), Meteor Shower
- **0-cost cards:** Astral Pulse (7/33), Collision Course (1/52), Cloak Of Stars (13/50), Know Thy Place (15/56), Gamma Blast (5/11), Lunar Blast (2/14), Radiate (3/20), Stardust (2/16), Alignment (14/19), Largesse, Monologue (1/23), Particle Wall (7/24), Quasar (6/16), Royal Gamble (11/19), Comet (1/5), Make It So (5/9), Big Bang (5/8), Decisions Decisions (6/12), Meteor Shower
- **X-cost cards:** Heavenly Drill (0/6)
- **Card draw:** Photon Cut (9/39), Glow (18/64), Glimmer (7/21), Prophesize (4/18), Summon Forth (11/15), Big Bang (5/8), Decisions Decisions (6/12)
- **Energy:** Refine Blade (12/56), Hegemony (7/20), Alignment (14/19), Convergence (4/16), Big Bang (5/8)
- **Strength:** Resonance (4/23)
- **Applies Vulnerable:** Know Thy Place (15/56), Gamma Blast (5/11), Comet (1/5), Meteor Shower
- **Applies Weak:** Know Thy Place (15/56), Gamma Blast (5/11), Comet (1/5), Meteor Shower
- **Powers:** Black Hole (4/21), Child Of The Stars (9/18), Furnace (8/16), Orbit (13/20), Pale Blue Dot (7/19), Parry (9/10), Pillar Of Creation (1/22), Spectrum Shift (0/18), Arsenal (2/7), Genesis (1/7), Hammer Time, Monarchs Gaze (2/8), Neutron Aegis (4/8), Royalties (0/8), Seeking Edge (7/12), Sword Sage (7/9), Tyranny (1/11), Void Form (9/11), The Sealed Throne
