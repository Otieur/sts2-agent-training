# Necrobinder Cards

Source: `knowledge/data/extract-2026-09-21/cards.json` `[GAME-EXTRACT]` (decompiled game data, build not stated, possibly newer than v0.107.1). Numbers are base values; `?` is computed at play time. Picked/offered and the head-to-head score come from the Player's card reward screens (Phase 1, v0.107.1) `[PLAYER-DATA]` and describe habit, not strength. ▲ = scored above skipping, ▼ = below.

Tags are derived from the effect text by `tools/import_extract.py` (multi-hit, aoe, zero-cost, x-cost, draw, energy, block, strength, vulnerable, weak, self-damage, exhaust-other, power, upgrade).

## Basic (4)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Strike Necrobinder | 1 | Attack | Basic | Deal 6 damage | damage | - | - | - |
| Unleash | 1 | Attack | Basic | Deal ? damage | damage | - | - | - |
| Bodyguard | 1 | Skill | Basic | Summon 5 | - | - | - | - |
| Defend Necrobinder | 1 | Skill | Basic | Gain 5 Block | block | - | - | - |

## Common (20)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Blight Strike | 1 | Attack | Common | Deal 8 damage; Apply ? Doom to the target | damage | 11/51 | 22% | -0.34 ▼ |
| Defile | 1 | Attack | Common | Deal 13 damage; keywords: Ethereal | damage | 3/51 | 6% | -1.62 ▼ |
| Drain Power | 1 | Attack | Common | Deal 10 damage; Upgrade a card | damage, upgrade | 22/68 | 32% | +0.30 ▲ |
| Fear | 1 | Attack | Common | Deal 7 damage; Apply 1 Vulnerable to the target; keywords: Ethereal | damage, vulnerable | 14/65 | 22% | -0.31 ▼ |
| Flatten | 2 | Attack | Common | Your Osty deals 12 damage | - | 22/70 | 31% | +0.25 ▲ |
| Graveblast | 1 | Attack | Common | Deal 4 damage; Choose a card from a pile; Put a card into your hand; keywords: Exhaust | damage, draw | 11/56 | 20% | -0.38 ▼ |
| Poke | 0 | Attack | Common | Your Osty deals 6 damage | zero-cost | 9/56 | 16% | -0.54 ▼ |
| Reap | 3 | Attack | Common | Deal 27 damage; keywords: Retain | damage | 1/70 | 1% | -2.96 ▼ |
| Reave | 1 | Attack | Common | Deal 9 damage; if upgraded: Upgrade a card; Add a generated card to your draw pile | damage, upgrade | 2/59 | 3% | -2.29 ▼ |
| Sculpting Strike | 1 | Attack | Common | Deal 8 damage; Choose a card in your hand; Give a card Ethereal | damage | 2/61 | 3% | -2.12 ▼ |
| Snap | 1 | Attack | Common | Your Osty deals 7 damage; Choose a card in your hand; Give a card Retain | - | 9/53 | 17% | -0.52 ▼ |
| Sow | 1 | Attack | Common | Deal 8 damage to ALL enemies; keywords: Retain | aoe, damage | 4/50 | 8% | -1.48 ▼ |
| Afterlife | 1 | Skill | Common | Summon 6; keywords: Exhaust | - | 5/40 | 12% | -0.95 ▼ |
| Defy | 1 | Skill | Common | Gain 6 Block; Apply 1 Weak to the target; keywords: Ethereal | block, weak | 6/51 | 12% | -1.16 ▼ |
| Grave Warden | 1 | Skill | Common | Gain 8 Block; if upgraded: Upgrade a card; Add a generated card to your draw pile | block, upgrade | 12/66 | 18% | -0.55 ▼ |
| Invoke | 1 | Skill | Common | Gain 2 Summon Next Turn; Gain 2 Energy Next Turn | energy | 8/50 | 16% | -0.58 ▼ |
| Negative Pulse | 1 | Skill | Common | Gain 5 Block; Apply 7 Doom to the target | aoe, block | 17/68 | 25% | -0.17 ▼ |
| Pull Aggro | 2 | Skill | Common | Summon 4; Gain 7 Block | block | 5/54 | 9% | -1.19 ▼ |
| Scourge | 1 | Skill | Common | Apply 13 Doom to the target; Draw 1 card | draw | 13/52 | 25% | -0.09 ▲ |
| Wisp | 0 | Skill | Common | Gain 1 Energy; keywords: Exhaust | energy, zero-cost | 28/66 | 42% | +0.72 ▲ |

## Uncommon (36)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Bone Shards | 1 | Attack | Uncommon | Your Osty deals 9 damage to ALL enemies; Gain 9 Block; Kill your own Osty | aoe, block | 5/25 | 20% | -0.14 ▼ |
| Bury | 4 | Attack | Uncommon | Deal 52 damage | damage | 1/21 | 5% | -1.65 ▼ |
| Death March | 1 | Attack | Uncommon | Deal ? damage | damage | 18/29 | 62% | +1.51 ▲ |
| Debilitate | 1 | Attack | Uncommon | Deal 7 damage; Apply 3 Debilitate to the target | damage | 3/27 | 11% | -1.14 ▼ |
| Fetch | 0 | Attack | Uncommon | Your Osty deals 3 damage; Draw 1 card | draw, zero-cost | 19/21 | 90% | +2.87 ▲ |
| High Five | 2 | Attack | Uncommon | Your Osty deals 11 damage to ALL enemies; Apply 2 Vulnerable to the target | aoe, vulnerable | 4/19 | 21% | -0.34 ▼ |
| Pull From Below | 1 | Attack | Uncommon | Deal 5 damage ? times | damage, multi-hit | 3/20 | 15% | -0.68 ▼ |
| Rattle | 1 | Attack | Uncommon | Your Osty deals 7 damage ? times | multi-hit | 8/15 | 53% | +1.23 ▲ |
| Right Hand Hand | 0 | Attack | Uncommon | Your Osty deals 4 damage | zero-cost | 4/18 | 22% | -0.14 ▼ |
| Severance | 2 | Attack | Uncommon | Deal 13 damage; Add a generated card to your draw pile; Add a generated card to your discard pile; Add a generated card to your hand | damage | 6/23 | 26% | +0.05 ▲ |
| Sic Em | 1 | Attack | Uncommon | Your Osty deals 5 damage; Apply 2 Sic Em to the target | - | 7/19 | 37% | +0.60 ▲ |
| Veilpiercer | 1 | Attack | Uncommon | Deal 10 damage; Gain 1 Veilpiercer | damage | 2/16 | 12% | -0.79 ▼ |
| Calcify | 1 | Power | Uncommon | Gain 4 Calcify | power | 4/17 | 24% | -0.20 ▼ |
| Countdown | 1 | Power | Uncommon | Gain 6 Countdown | power | 5/18 | 28% | -0.05 ▲ |
| Danse Macabre | 1 | Power | Uncommon | Gain 3 Danse Macabre | power | 1/22 | 5% | -1.69 ▼ |
| Friendship | 1 | Power | Uncommon | Gain -2 Strength; Gain 1 Friendship | power, strength | 10/14 | 71% | +1.84 ▲ |
| Haunt | 1 | Power | Uncommon | Gain 6 Haunt | power | 6/25 | 24% | -0.12 ▲ |
| Lethality | 1 | Power | Uncommon | Gain 50 Lethality; keywords: Ethereal | power | 0/24 | 0% | -2.99 ▼ |
| Pagestorm | 1 | Power | Uncommon | Gain 1 Pagestorm | power | 2/19 | 11% | -0.99 ▼ |
| Shroud | 1 | Power | Uncommon | Gain 2 Shroud | power | 6/22 | 27% | +0.07 ▲ |
| Sleight Of Flesh | 2 | Power | Uncommon | Gain 9 Sleight Of Flesh | power | 6/18 | 33% | +0.02 ▲ |
| Borrowed Time | 0 | Skill | Uncommon | Gain 3 Doom; Gain 1 Energy | energy, zero-cost | 12/14 | 86% | +2.58 ▲ |
| Capture Spirit | 1 | Skill | Uncommon | Deal 3 damage to the target; Add a generated card to your draw pile | damage | 8/22 | 36% | +0.49 ▲ |
| Cleanse | 1 | Skill | Uncommon | Summon 3; Choose a card from a pile; Exhaust a card | exhaust-other | 9/27 | 33% | +0.20 ▲ |
| Deathbringer | 2 | Skill | Uncommon | Apply 21 Doom to the target; Apply 1 Weak to the target | aoe, weak | 5/15 | 33% | +0.39 ▲ |
| Deaths Door | 1 | Skill | Uncommon | Gain 6 Block | block | 12/18 | 67% | +1.72 ▲ |
| Delay | 2 | Skill | Uncommon | Gain 11 Block; Gain 1 Energy Next Turn | block, energy | 1/17 | 6% | -1.51 ▼ |
| Dirge | 0 | Skill | Uncommon | Summon 3; if upgraded: Upgrade a card; Add a generated card to your draw pile | upgrade, zero-cost | 11/21 | 52% | +1.17 ▲ |
| Dredge | 1 | Skill | Uncommon | Put a card into your hand; keywords: Exhaust | draw | 3/12 | 25% | -0.03 ▲ |
| Enfeebling Touch | 1 | Skill | Uncommon | Apply 8 Enfeebling Touch to the target; keywords: Ethereal | - | 17/22 | 77% | +1.97 ▲ |
| Legion Of Bone | 2 | Skill | Uncommon | Summon 6; keywords: Exhaust | - | - | - | - |
| Melancholy | 3 | Skill | Uncommon | Gain 13 Block | block | 12/18 | 67% | +1.86 ▲ |
| No Escape | 1 | Skill | Uncommon | Apply ? Doom to the target | - | 8/14 | 57% | +1.30 ▲ |
| Parse | 1 | Skill | Uncommon | Draw 3 cards; keywords: Ethereal | draw | 11/27 | 41% | +0.95 ▲ |
| Putrefy | 1 | Skill | Uncommon | Apply 2 Weak to the target; Apply 2 Vulnerable to the target; keywords: Exhaust | vulnerable, weak | 18/30 | 60% | +1.31 ▲ |
| Spur | 1 | Skill | Uncommon | Summon 3; Heal 5 HP; keywords: Retain | heal | 0/16 | 0% | -2.91 ▼ |

## Rare (26)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Banshees Cry | 6 | Attack | Rare | Deal 33 damage to ALL enemies | aoe, damage | 1/11 | 9% | -0.42 ▼ |
| Eradicate | 0 | Attack | Rare | Deal 11 damage ? times; keywords: Retain | damage, multi-hit, zero-cost | 0/10 | 0% | -1.64 ▼ |
| Hang | 1 | Attack | Rare | Deal 10 damage; Apply ? Hang to the target | damage | 6/9 | 67% | +1.78 ▲ |
| Misery | 0 | Attack | Rare | Deal 7 damage; Increase a power already on the target; Apply a power to the target | damage, zero-cost | 1/13 | 8% | -0.68 ▼ |
| Soul Storm | 1 | Attack | Rare | Deal ? damage | damage | 4/12 | 33% | +1.44 ▲ |
| Squeeze | 3 | Attack | Rare | Deal ? damage | damage | 6/15 | 40% | +1.46 ▲ |
| The Scythe | 2 | Attack | Rare | Deal ? damage; keywords: Exhaust | damage | 2/15 | 13% | -0.25 ▼ |
| Times Up | 2 | Attack | Rare | Deal ? damage; keywords: Exhaust | damage | 2/7 | 29% | +0.25 ▲ |
| Call Of The Void | 1 | Power | Rare | Gain 1 Call Of The Void | power | 3/15 | 20% | +0.29 ▲ |
| Demesne | 3 | Power | Rare | Gain 1 Demesne; keywords: Ethereal | power | 15/16 | 94% | +3.83 ▲ |
| Devour Life | 1 | Power | Rare | Gain 1 Devour Life | power | 3/9 | 33% | +0.68 ▲ |
| Necro Mastery | 2 | Power | Rare | Summon 5; Gain 1 Necro Mastery | power | 0/15 | 0% | -2.00 ▼ |
| Neurosurge | 0 | Power | Rare | Gain 3 Energy; Draw 2 cards; Gain 3 Neurosurge | draw, energy, power, zero-cost | 11/13 | 85% | +2.77 ▲ |
| Reaper Form | 3 | Power | Rare | Gain 1 Reaper Form | power | 3/9 | 33% | +0.36 ▲ |
| Sentry Mode | 2 | Power | Rare | Gain 1 Sentry Mode | power | 7/10 | 70% | +1.87 ▲ |
| Spirit Of Ash | 1 | Power | Rare | Gain 4 Spirit Of Ash | power | 2/11 | 18% | +0.07 ▲ |
| Eidolon | 2 | Skill | Rare | Exhaust a card; Gain 1 Intangible | exhaust-other | 0/9 | 0% | -1.89 ▼ |
| End Of Days | 3 | Skill | Rare | Apply 29 Doom to the target | aoe | 5/10 | 50% | +1.67 ▲ |
| Glimpse Beyond | 1 | Skill | Rare | Add a generated card to your draw pile; keywords: Exhaust | - | - | - | - |
| Oblivion | 0 | Skill | Rare | Apply 3 Oblivion to the target | zero-cost | 4/9 | 44% | +1.01 ▲ |
| Reanimate | 3 | Skill | Rare | Summon 20; keywords: Exhaust | - | 2/11 | 18% | +0.26 ▲ |
| Sacrifice | 1 | Skill | Rare | Kill your own Osty; Gain ? Block; keywords: Retain | block | 2/10 | 20% | +0.67 ▲ |
| Seance | 0 | Skill | Rare | Choose a card from a pile; Transform a card into Soul; Upgrade a card; keywords: Ethereal | upgrade, zero-cost | 12/18 | 67% | +2.32 ▲ |
| Shared Fate | 0 | Skill | Rare | Gain -2 Strength; Apply -2 Strength to the target; keywords: Exhaust | strength, zero-cost | 2/7 | 29% | +0.15 ▲ |
| Transfigure | 1 | Skill | Rare | Choose a card in your hand; keywords: Exhaust | - | 3/9 | 33% | +0.78 ▲ |
| Undeath | 0 | Skill | Rare | Gain 7 Block; Add a generated card to your discard pile | block, zero-cost | 1/10 | 10% | -0.31 ▼ |

## Ancient (2)

| Card | Cost | Type | Rarity | Effect (base) | Roles | Picked | Pick rate | Player score |
|---|---|---|---|---|---|---|---|---|
| Protector | 1 | Attack | Ancient | Deal ? damage | damage | - | - | - |
| Forbidden Grimoire | 2 | Power | Ancient | Gain 1 Forbidden Grimoire; keywords: Eternal | power | - | - | - |

## Role index

- **Multi-hit attacks:** Pull From Below (3/20), Rattle (8/15), Eradicate (0/10)
- **Hits all enemies:** Sow (4/50), Negative Pulse (17/68), Bone Shards (5/25), High Five (4/19), Deathbringer (5/15), Banshees Cry (1/11), End Of Days (5/10)
- **0-cost cards:** Poke (9/56), Wisp (28/66), Fetch (19/21), Right Hand Hand (4/18), Borrowed Time (12/14), Dirge (11/21), Eradicate (0/10), Misery (1/13), Neurosurge (11/13), Oblivion (4/9), Seance (12/18), Shared Fate (2/7), Undeath (1/10)
- **Card draw:** Graveblast (11/56), Scourge (13/52), Fetch (19/21), Dredge (3/12), Parse (11/27), Neurosurge (11/13)
- **Energy:** Invoke (8/50), Wisp (28/66), Borrowed Time (12/14), Delay (1/17), Neurosurge (11/13)
- **Strength:** Friendship (10/14), Shared Fate (2/7)
- **Applies Vulnerable:** Fear (14/65), High Five (4/19), Putrefy (18/30)
- **Applies Weak:** Defy (6/51), Deathbringer (5/15), Putrefy (18/30)
- **Powers:** Calcify (4/17), Countdown (5/18), Danse Macabre (1/22), Friendship (10/14), Haunt (6/25), Lethality (0/24), Pagestorm (2/19), Shroud (6/22), Sleight Of Flesh (6/18), Call Of The Void (3/15), Demesne (15/16), Devour Life (3/9), Necro Mastery (0/15), Neurosurge (11/13), Reaper Form (3/9), Sentry Mode (7/10), Spirit Of Ash (2/11), Forbidden Grimoire
