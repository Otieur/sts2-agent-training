# Pathing, Rest, Shops, Events and Potions: Silent (v0.107.1)

Runs: 51 solo. Outcome comparisons use finished runs only.

> **Statistical cautions.** (1) Selection bias: what gets offered depends on earlier picks and relics.
> (2) Survivorship: late-floor numbers come only from runs that got there. (3) Ascension confounds
> everything; compare within bands. (4) Small samples: show n next to every rate; win correlations are
> hypotheses. (5) Multiple comparisons: with ~100 cards, some will look significant by chance.

## Room mix per completed act

Means per completed act. An act counts only if the run got past its boss.

| Act | Run outcome | Acts | Monsters | Elites | ? rooms | Shops | Rest sites | Treasure | Median HP% after boss |
|---|---|---|---|---|---|---|---|---|---|
| 1 | win | 10 | 4.9 | 1.0 | 3.2 | 1.2 | 3.7 | 1.0 | 39% |
| 1 | loss | 18 | 4.3 | 1.3 | 3.4 | 1.1 | 3.8 | 1.0 | 31% |
| 2 | win | 10 | 4.8 | 0.8 | 2.4 | 1.3 | 3.7 | 1.0 | 38% |
| 2 | loss | 10 | 3.9 | 0.9 | 3.4 | 1.2 | 3.7 | 1.1 | 24% |
| 3 | win | 10 | 4.2 | 0.6 | 3.2 | 0.7 | 3.3 | 1.0 | 48% |

## Elites fought in an act, against surviving it

| Act | Elites (3 = 3+) | Acts | Survived the act | Rate |
|---|---|---|---|---|
| 1 | 0 | 11 | 6 | 55% |
| 1 | 1 | 19 | 12 | 63% |
| 1 | 2 | 11 | 9 | 82% |
| 1 | 3 | 2 | 1 | 50% |
| 2 | 0 | 9 | 8 | 89% |
| 2 | 1 | 13 | 7 | 54% |
| 2 | 2 | 6 | 5 | 83% |
| 3 | 0 | 7 | 5 | 71% |
| 3 | 1 | 9 | 4 | 44% |
| 3 | 2 | 3 | 1 | 33% |
| 3 | 3 | 1 | 0 | 0% |

Survival here is confounded: strong decks both take more elites and survive. It does not show that elites are safe.

## Rest sites

| HP on arrival | Visits | Heal | Smith | Other | Before boss | Heal before boss |
|---|---|---|---|---|---|---|
| 0–30% | 30 | 93% | 7% | 0 | 12 | 92% |
| 30–50% | 75 | 43% | 55% | 2 | 23 | 57% |
| 50–70% | 115 | 13% | 83% | 5 | 29 | 17% |
| 70–90% | 71 | 6% | 89% | 4 | 14 | 14% |
| 90–100% | 38 | 13% | 82% | 2 | 12 | 17% |

- **Estimated threshold** (logistic fit, HEAL vs SMITH): the Player is equally likely to heal or smith at **40% HP** (n=316).
  - Right before a boss: 45% (n=86). Other rest sites: 38% (n=230).
- Other options used: COOK ×3, HATCH ×3, DIG ×3, LIFT ×3, KINDLE ×1.

## Shops

| Act | Visits | Median gold on arrival | Median spent | Bought nothing | Cards | Colorless | Relics | Potions | Removals |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 49 | 140 | 103 | 8% | 45 | 12 | 11 | 6 | 8 |
| 2 | 34 | 226 | 177 | 3% | 25 | 13 | 17 | 9 | 9 |
| 3 | 18 | 246 | 236 | 11% | 12 | 4 | 12 | 5 | 6 |

Most bought relics: MINIATURE_TENT ×4, LANTERN ×4, MEMBERSHIP_CARD ×3, JUZU_BRACELET ×2, LEES_WAFFLE ×2, WAR_PAINT ×2, GREMLIN_HORN ×1, ANCHOR ×1, TINGSHA ×1, VAJRA ×1.

Most bought potions: CURE_ALL ×3, FLEX_POTION ×3, ATTACK_POTION ×3, POWER_POTION ×2, SWIFT_POTION ×2, FIRE_POTION ×1, DUPLICATOR ×1, WEAK_POTION ×1.

## Events

Choice names are the option keys from the game's localisation. The HP and gold columns are mean net changes over the floor.

| Event | Visits | Choices | Mean HP change | Mean gold change |
|---|---|---|---|---|
| SLIPPERY_BRIDGE | 25 | OVERCOME ×11; HOLD_ON_0 ×9; HOLD_ON_1 ×5 | -5.2 | 0 |
| THIS_OR_THAT | 15 | ORNATE ×13; PLAIN ×2 | -0.1 | 8 |
| TINKER_TIME | 12 | CHOOSE_CARD_TYPE ×4; POWER ×3; CURIOUS ×2; IMPROVEMENT ×1 | 0.0 | 0 |
| SELF_HELP_BOOK | 10 | READ_THE_BACK ×8; READ_ENTIRE_BOOK ×1; READ_PASSAGE ×1 | 0.0 | 0 |
| ABYSSAL_BATHS | 10 | LINGER ×5; ABSTAIN ×3; IMMERSE ×1; EXIT_BATHS ×1 | -11.7 | 0 |
| POTION_COURIER | 10 | RANSACK ×8; GRAB_POTIONS ×2 | 0.5 | 0 |
| THE_LEGENDS_WERE_TRUE | 10 | NAB_THE_MAP ×10 | 0.0 | 0 |
| SUNKEN_STATUE | 8 | GRAB_SWORD ×5; DIVE_INTO_WATER ×3 | -2.6 | 41 |
| SYMBIOTE | 8 | KILL_WITH_FIRE ×6; APPROACH ×2 | 0.0 | 0 |
| AROMA_OF_CHAOS | 7 | MAINTAIN_CONTROL ×6; LET_GO ×1 | 0.0 | 0 |
| BRAIN_LEECH | 7 | SHARE_KNOWLEDGE ×4; RIP ×3 | -2.1 | 0 |
| ROOM_FULL_OF_CHEESE | 7 | GORGE ×6; SEARCH ×1 | -2.0 | 0 |
| ENDLESS_CONVEYOR | 7 | FRIED_EEL ×2; OBSERVE_CHEF ×1; CAVIAR ×1; SUSPICIOUS_CONDIMENT ×1 | 3.4 | -171 |
| RELIC_TRADER | 6 | MIDDLE ×3; TOP ×2; BOTTOM ×1 | 0.8 | 0 |
| BATTLEWORN_DUMMY | 6 | SETTING_2 ×2; SETTING_3 ×2; SETTING_1 ×2 | 0.0 | 0 |
| BYRDONIS_NEST | 6 | EAT ×3; TAKE ×3 | 3.5 | 0 |
| THE_FUTURE_OF_POTIONS | 5 | POTION ×5 | 0.0 | 0 |
| WELLSPRING | 5 | BATHE ×3; BOTTLE ×2 | 0.0 | 0 |
| LOST_WISP | 5 | CLAIM ×4; SEARCH ×1 | 0.0 | 15 |
| SPIRIT_GRAFTER | 5 | LET_IT_IN ×5 | 22.4 | 0 |
| SUNKEN_TREASURY | 5 | SECOND_CHEST ×5 | 0.0 | 338 |
| ROUND_TEA_PARTY | 4 | PICK_FIGHT ×4 | -11.0 | 0 |
| JUNGLE_MAZE_ADVENTURE | 4 | SOLO_QUEST ×3; JOIN_FORCES ×1 | -13.5 | 132 |
| INFESTED_AUTOMATON | 4 | TOUCH_CORE ×2; STUDY ×2 | 0.0 | 0 |
| SPIRALING_WHIRLPOOL | 4 | DRINK ×4 | 23.0 | 0 |

## Ancients

Ancient visits by Ancient: NEOW ×49, TEZCATARA ×10, OROBAS ×8, TANX ×7, PAEL ×7, VAKUU ×6, NONUPEIPE ×5, DARV ×5.

Options offered 3+ times, by how often the Player took them:

| Option | Offered | Chosen | Rate |
|---|---|---|---|
| SEAL_OF_GOLD | 3 | 3 | 100% |
| HEFTY_TABLET | 11 | 9 | 82% |
| GOLDEN_PEARL | 11 | 9 | 82% |
| BLOOD_SOAKED_ROSE | 5 | 4 | 80% |
| PAELS_BLOOD | 4 | 3 | 75% |
| ARCANE_SCROLL | 7 | 5 | 71% |
| LEAD_PAPERWEIGHT | 6 | 4 | 67% |
| NEOWS_TORMENT | 3 | 2 | 67% |
| CURSED_PEARL | 3 | 2 | 67% |
| NUTRITIOUS_SOUP | 3 | 2 | 67% |
| TOUCH_OF_OROBAS | 7 | 4 | 57% |
| NEOWS_BONES | 6 | 3 | 50% |
| YUMMY_COOKIE | 4 | 2 | 50% |
| CLAWS | 4 | 2 | 50% |
| WINGED_BOOTS | 7 | 3 | 43% |
| LARGE_CAPSULE | 8 | 3 | 38% |
| PRESERVED_FOG | 3 | 1 | 33% |
| VERY_HOT_COCOA | 3 | 1 | 33% |
| MEAT_CLEAVER | 3 | 1 | 33% |
| SAND_CASTLE | 3 | 1 | 33% |
| SIGNET_RING | 3 | 1 | 33% |
| LOOMING_FRUIT | 3 | 1 | 33% |
| PAELS_HORN | 3 | 1 | 33% |
| SAI | 3 | 1 | 33% |
| SILVER_CRUCIBLE | 4 | 1 | 25% |
| SILKEN_TRESS | 6 | 1 | 17% |
| SCROLL_BOXES | 6 | 1 | 17% |
| POMANDER | 6 | 1 | 17% |
| FISHING_ROD | 7 | 1 | 14% |
| LOST_COFFER | 8 | 1 | 12% |

## Potions

| Room type | Potions used | Fights | Potions per fight |
|---|---|---|---|
| monster | 125 | 456 | 0.27 |
| elite | 75 | 91 | 0.82 |
| boss | 117 | 86 | 1.36 |

- Potions still held at death: mean 0.1, and 2/33 deaths had at least one unused potion.
- Discarded: STABLE_SERUM ×4, BLOCK_POTION ×4, POTION_OF_BINDING ×2, LIQUID_BRONZE ×2, ATTACK_POTION ×2, FIRE_POTION ×2.

Potion rewards most often left behind (offered 4+ times):

| Potion | Offered | Taken | Rate |
|---|---|---|---|
| MAZALETHS_GIFT | 7 | 1 | 14% |
| REGEN_POTION | 10 | 2 | 20% |
| CUNNING_POTION | 9 | 3 | 33% |
| BEETLE_JUICE | 6 | 2 | 33% |
| RADIANT_TINCTURE | 8 | 3 | 38% |
| LIQUID_BRONZE | 15 | 6 | 40% |
| POTION_OF_BINDING | 12 | 5 | 42% |
| STABLE_SERUM | 12 | 5 | 42% |
| SWIFT_POTION | 30 | 13 | 43% |
| DEXTERITY_POTION | 32 | 14 | 44% |
