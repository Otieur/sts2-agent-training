# Ironclad Cards

Source: `knowledge/data/extract-2026-09-21/cards.json` `[GAME-EXTRACT]` (decompiled game data, build not stated, possibly newer than v0.107.1). Numbers are base values; `?` is computed at play time. Picked/offered and the head-to-head score come from the Player's card reward screens (Phase 1, v0.107.1) `[PLAYER-DATA]` and describe habit, not strength. ▲ = scored above skipping, ▼ = below.

Tags are derived from the effect text by `tools/import_extract.py` (multi-hit, aoe, zero-cost, x-cost, draw, energy, block, strength, vulnerable, weak, self-damage, exhaust-other, power, upgrade).

## Basic (3)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Bash | 2 | Attack | Basic | Deal 8 damage; Apply 2 Vulnerable to the target | damage, vulnerable | - | - | - |
| Strike Ironclad | 1 | Attack | Basic | Deal 6 damage | damage | - | - | - |
| Defend Ironclad | 1 | Skill | Basic | Gain 5 Block | block | - | - | - |

## Common (20)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Anger | 0 | Attack | Common | Deal 6 damage; Add a generated card to your discard pile | damage, zero-cost | 2/53 | 4% | -2.23 ▼ |
| Body Slam | 1 | Attack | Common | Deal ? damage | damage | 4/45 | 9% | -1.63 ▼ |
| Breakthrough | 1 | Attack | Common | Lose 1 HP; Deal 9 damage to ALL enemies | aoe, damage, self-damage | 21/62 | 34% | -0.02 ▲ |
| Cinder | 2 | Attack | Common | Deal 17 damage; Shuffle your draw pile; Exhaust a card | damage, exhaust-other | 8/54 | 15% | -0.99 ▼ |
| Headbutt | 1 | Attack | Common | Deal 9 damage; Choose a card from a pile; Put a card into your draw pile | damage | 7/57 | 12% | -1.34 ▼ |
| Iron Wave | 1 | Attack | Common | Gain 5 Block; Deal 5 damage | block, damage | 8/66 | 12% | -1.26 ▼ |
| Molten Fist | 1 | Attack | Common | Deal 10 damage; Apply ? Vulnerable to the target; keywords: Exhaust | damage, vulnerable | 18/43 | 42% | +0.39 ▲ |
| Perfected Strike | 2 | Attack | Common | Deal ? damage | damage | 2/52 | 4% | -2.32 ▼ |
| Pommel Strike | 1 | Attack | Common | Deal 9 damage; Draw 1 card | damage, draw | 7/47 | 15% | -1.07 ▼ |
| Setup Strike | 1 | Attack | Common | Deal 7 damage; Gain 2 Setup Strike | damage | 5/51 | 10% | -1.37 ▼ |
| Sword Boomerang | 1 | Attack | Common | Deal 3 damage 3 times to a random enemy | damage, multi-hit, random-target | 10/58 | 17% | -0.87 ▼ |
| Thunderclap | 1 | Attack | Common | Deal 4 damage to ALL enemies; Apply 1 Vulnerable to the target | aoe, damage, vulnerable | 7/46 | 15% | -1.07 ▼ |
| Twin Strike | 1 | Attack | Common | Deal 5 damage 2 times | damage, multi-hit | 9/47 | 19% | -0.61 ▼ |
| Armaments | 1 | Skill | Common | Gain 5 Block; if upgraded: Upgrade a card; Upgrade a card in your hand; Upgrade a card | block, upgrade | 25/65 | 38% | +0.36 ▲ |
| Blood Wall | 2 | Skill | Common | Lose 2 HP; Gain 16 Block | block, self-damage | 1/55 | 2% | -2.98 ▼ |
| Bloodletting | 0 | Skill | Common | Lose 3 HP; Gain 2 Energy | energy, self-damage, zero-cost | 22/55 | 40% | +0.35 ▲ |
| Havoc | 1 | Skill | Common | Auto-play a card from your draw pile | - | 6/48 | 12% | -1.07 ▼ |
| Shrug It Off | 1 | Skill | Common | Gain 8 Block; Draw 1 card | block, draw | 21/73 | 29% | -0.23 ▲ |
| Tremble | 1 | Skill | Common | Apply 2 Vulnerable to the target | vulnerable | 24/54 | 44% | +0.47 ▲ |
| True Grit | 1 | Skill | Common | Gain 7 Block; if upgraded: Choose a card in your hand; if upgraded: Exhaust a card; Exhaust a card | block, exhaust-other | 23/49 | 47% | +0.66 ▲ |

## Uncommon (36)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Ashen Strike | 1 | Attack | Uncommon | Deal ? damage | damage | 5/10 | 50% | +0.46 ▲ |
| Bludgeon | 3 | Attack | Uncommon | Deal 32 damage | damage | 1/21 | 5% | -1.69 ▼ |
| Bully | 0 | Attack | Uncommon | Deal ? damage | damage, zero-cost | 3/13 | 23% | -0.58 ▼ |
| Dismantle | 1 | Attack | Uncommon | Deal 8 damage ? times | damage, multi-hit | 3/14 | 21% | -0.36 ▲ |
| Fight Me | 2 | Attack | Uncommon | Deal 5 damage 2 times; Gain 2 Strength; Apply 1 Strength to the target | damage, multi-hit, strength | 11/14 | 79% | +2.06 ▲ |
| Grapple | 1 | Attack | Uncommon | Deal 7 damage; Apply 5 Grapple to the target | damage | - | - | - |
| Hemokinesis | 1 | Attack | Uncommon | Lose 2 HP; Deal 14 damage | damage, self-damage | 1/25 | 4% | -2.17 ▼ |
| Howl From Beyond | 3 | Attack | Uncommon | Deal 16 damage to ALL enemies | aoe, damage | 3/19 | 16% | -0.79 ▼ |
| Pillage | 1 | Attack | Uncommon | Deal 6 damage; Draw 1 card | damage, draw | 4/16 | 25% | -0.54 ▼ |
| Rampage | 1 | Attack | Uncommon | Deal 9 damage | damage | 3/26 | 12% | -1.11 ▼ |
| Spite | 0 | Attack | Uncommon | Deal 6 damage; Draw 1 card | damage, draw, zero-cost | 2/26 | 8% | -1.65 ▼ |
| Stomp | 3 | Attack | Uncommon | Deal 12 damage to ALL enemies | aoe, damage | 3/16 | 19% | -0.61 ▼ |
| Unrelenting | 2 | Attack | Uncommon | Deal 12 damage; Gain 1 Free Attack | damage | 5/16 | 31% | +0.11 ▲ |
| Uppercut | 2 | Attack | Uncommon | Deal 13 damage; Apply 1 Weak to the target; Apply 1 Vulnerable to the target | damage, vulnerable, weak | 4/15 | 27% | -0.20 ▲ |
| Whirlwind | X | Attack | Uncommon | Deal 5 damage X (energy spent) times to ALL enemies | aoe, damage, multi-hit, x-cost | 0/13 | 0% | -2.54 ▼ |
| Drum Of Battle | 0 | Power | Uncommon | Draw 2 cards; Gain 1 Drum Of Battle | draw, power, zero-cost | 9/21 | 43% | +0.51 ▲ |
| Feel No Pain | 1 | Power | Uncommon | Gain 3 Feel No Pain | power | 5/15 | 33% | -0.06 ▲ |
| Inferno | 1 | Power | Uncommon | Gain 6 Inferno | power | 3/12 | 25% | -0.19 ▲ |
| Inflame | 1 | Power | Uncommon | Gain 2 Strength | power, strength | 2/14 | 14% | -1.19 ▼ |
| Juggling | 1 | Power | Uncommon | Gain 1 Juggling | power | 0/15 | 0% | -2.90 ▼ |
| Rupture | 1 | Power | Uncommon | Gain 1 Rupture | power | 2/12 | 17% | -0.97 ▼ |
| Stampede | 2 | Power | Uncommon | Gain 1 Stampede | power | 9/17 | 53% | +0.83 ▲ |
| Stone Armor | 1 | Power | Uncommon | Gain 4 Plating | power | 1/22 | 5% | -1.94 ▼ |
| Vicious | 1 | Power | Uncommon | Gain 1 Vicious | power | 12/25 | 48% | +0.80 ▲ |
| Battle Trance | 0 | Skill | Uncommon | Draw 3 cards; Gain 1 No Draw | draw, zero-cost | 3/16 | 19% | -0.07 ▲ |
| Burning Pact | 1 | Skill | Uncommon | Choose a card in your hand; Exhaust a card; Draw 2 cards | draw, exhaust-other | 11/18 | 61% | +1.10 ▲ |
| Demonic Shield | 0 | Skill | Uncommon | Lose 1 HP; Give the target ? Block; keywords: Exhaust | block, self-damage, zero-cost | - | - | - |
| Dominate | 1 | Skill | Uncommon | Gain ? Strength; keywords: Exhaust | strength | 19/20 | 95% | +3.05 ▲ |
| Evil Eye | 1 | Skill | Uncommon | Gain 8 Block | block | 14/21 | 67% | +1.76 ▲ |
| Expect A Fight | 2 | Skill | Uncommon | Gain ? Energy | energy | 0/14 | 0% | -3.15 ▼ |
| Flame Barrier | 2 | Skill | Uncommon | Gain 12 Block; Gain 4 Flame Barrier | block | 4/12 | 33% | -0.19 ▲ |
| Forgotten Ritual | 1 | Skill | Uncommon | Gain 3 Energy | energy | 7/18 | 39% | +0.22 ▲ |
| Infernal Blade | 1 | Skill | Uncommon | get Distinct For Combat; Add a generated card to your hand; keywords: Exhaust | - | 4/11 | 36% | +0.21 ▲ |
| Rage | 0 | Skill | Uncommon | Gain 3 Rage | zero-cost | 4/19 | 21% | -0.72 ▼ |
| Second Wind | 1 | Skill | Uncommon | Exhaust a card; Gain 5 Block | block, exhaust-other | 13/19 | 68% | +1.56 ▲ |
| Taunt | 1 | Skill | Uncommon | Gain 7 Block; Apply 1 Vulnerable to the target | block, vulnerable | 3/12 | 25% | -0.26 ▲ |

## Rare (26)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Conflagration | 1 | Attack | Rare | Deal ? damage to ALL enemies | aoe, damage | 4/7 | 57% | +2.24 ▲ |
| Feed | 1 | Attack | Rare | Deal 10 damage; Gain 3 Max HP; keywords: Exhaust | damage | 2/7 | 29% | +0.54 ▲ |
| Fiend Fire | 2 | Attack | Rare | Exhaust a card; Deal 7 damage ? times; keywords: Exhaust | damage, exhaust-other, multi-hit | 4/5 | 80% | +2.60 ▲ |
| Mangle | 3 | Attack | Rare | Deal 15 damage; Apply 10 Mangle to the target | damage | 3/9 | 33% | +0.88 ▲ |
| Pacts End | 0 | Attack | Rare | Deal 17 damage to ALL enemies | aoe, damage, zero-cost | 3/5 | 60% | +1.43 ▲ |
| Tear Asunder | 2 | Attack | Rare | Deal 5 damage ? times | damage, multi-hit | 2/7 | 29% | +0.52 ▲ |
| Thrash | 1 | Attack | Rare | Deal 4 damage 2 times; Exhaust a card | damage, exhaust-other, multi-hit | 6/7 | 86% | +2.99 ▲ |
| Aggression | 1 | Power | Rare | Gain 1 Aggression | power | 4/9 | 44% | +1.49 ▲ |
| Barricade | 3 | Power | Rare | Gain 1 Barricade | power | 3/15 | 20% | +0.12 ▲ |
| Crimson Mantle | 1 | Power | Rare | Gain 8 Crimson Mantle | power | 4/12 | 33% | +0.54 ▲ |
| Cruelty | 1 | Power | Rare | Gain 25 Cruelty | power | 4/5 | 80% | +2.51 ▲ |
| Dark Embrace | 2 | Power | Rare | Gain 1 Dark Embrace | power | 4/5 | 80% | +2.68 ▲ |
| Demon Form | 3 | Power | Rare | Gain 2 Demon Form | power | 2/10 | 20% | +0.21 ▲ |
| Hellraiser | 2 | Power | Rare | Gain 1 Hellraiser | power | 2/6 | 33% | +0.78 ▲ |
| Juggernaut | 2 | Power | Rare | Gain 5 Juggernaut | power | 0/6 | 0% | -1.35 ▼ |
| Pyre | 2 | Power | Rare | Gain 1 Pyre | power | 11/13 | 85% | +3.12 ▲ |
| Tank | 1 | Power | Rare | Gain 1 Tank | power | - | - | - |
| Unmovable | 2 | Power | Rare | Gain 1 Unmovable | power | 0/9 | 0% | -1.50 ▼ |
| Brand | 0 | Skill | Rare | Lose 1 HP; Choose a card in your hand; Exhaust a card; Gain 1 Strength | exhaust-other, self-damage, strength, zero-cost | 4/6 | 67% | +2.47 ▲ |
| Cascade | X | Skill | Rare | Auto-play a card from your draw pile | x-cost | 2/13 | 15% | +0.14 ▲ |
| Colossus | 1 | Skill | Rare | Gain 5 Block; Gain 1 Colossus | block | 10/19 | 53% | +0.75 ▲ |
| Impervious | 2 | Skill | Rare | Gain 30 Block; keywords: Exhaust | block | 4/7 | 57% | +1.52 ▲ |
| Offering | 0 | Skill | Rare | Lose 6 HP; Gain 2 Energy; Draw 3 cards; keywords: Exhaust | draw, energy, self-damage, zero-cost | 4/4 | 100% | +2.69 ▲ |
| One Two Punch | 1 | Skill | Rare | Gain 1 One Two Punch | - | 4/11 | 36% | +1.70 ▲ |
| Primal Force | 0 | Skill | Rare | if upgraded: Upgrade a card; Transform a card | upgrade, zero-cost | 1/4 | 25% | +0.59 ▲ |
| Stoke | 1 | Skill | Rare | Exhaust a card; Draw ? cards; keywords: Exhaust | draw, exhaust-other | 3/7 | 43% | +1.18 ▲ |

## Ancient (2)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Break | 2 | Attack | Ancient | Deal 20 damage; Apply 5 Vulnerable to the target | damage, vulnerable | - | - | - |
| Corruption | 3 | Power | Ancient | Gain 1 Corruption | power | - | - | - |

## Role index

- **Multi-hit attacks:** Sword Boomerang (10/58), Twin Strike (9/47), Dismantle (3/14), Fight Me (11/14), Whirlwind (0/13), Fiend Fire (4/5), Tear Asunder (2/7), Thrash (6/7)
- **Hits all enemies:** Breakthrough (21/62), Thunderclap (7/46), Howl From Beyond (3/19), Stomp (3/16), Whirlwind (0/13), Conflagration (4/7), Pacts End (3/5)
- **0-cost cards:** Anger (2/53), Bloodletting (22/55), Bully (3/13), Spite (2/26), Drum Of Battle (9/21), Battle Trance (3/16), Demonic Shield, Rage (4/19), Pacts End (3/5), Brand (4/6), Offering (4/4), Primal Force (1/4)
- **X-cost cards:** Whirlwind (0/13), Cascade (2/13)
- **Card draw:** Pommel Strike (7/47), Shrug It Off (21/73), Pillage (4/16), Spite (2/26), Drum Of Battle (9/21), Battle Trance (3/16), Burning Pact (11/18), Offering (4/4), Stoke (3/7)
- **Energy:** Bloodletting (22/55), Expect A Fight (0/14), Forgotten Ritual (7/18), Offering (4/4)
- **Strength:** Fight Me (11/14), Inflame (2/14), Dominate (19/20), Brand (4/6)
- **Applies Vulnerable:** Molten Fist (18/43), Thunderclap (7/46), Tremble (24/54), Uppercut (4/15), Taunt (3/12), Break
- **Applies Weak:** Uppercut (4/15)
- **Costs HP:** Breakthrough (21/62), Blood Wall (1/55), Bloodletting (22/55), Hemokinesis (1/25), Demonic Shield, Brand (4/6), Offering (4/4)
- **Powers:** Drum Of Battle (9/21), Feel No Pain (5/15), Inferno (3/12), Inflame (2/14), Juggling (0/15), Rupture (2/12), Stampede (9/17), Stone Armor (1/22), Vicious (12/25), Aggression (4/9), Barricade (3/15), Crimson Mantle (4/12), Cruelty (4/5), Dark Embrace (4/5), Demon Form (2/10), Hellraiser (2/6), Juggernaut (0/6), Pyre (11/13), Tank, Unmovable (0/9), Corruption
