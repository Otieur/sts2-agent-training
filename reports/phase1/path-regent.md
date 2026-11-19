# Pathing, Rest, Shops, Events and Potions: Regent (v0.107.1)

Runs: 53 solo. Outcome comparisons use finished runs only.

> **Statistical cautions.** (1) Selection bias: what gets offered depends on earlier picks and relics.
> (2) Survivorship: late-floor numbers come only from runs that got there. (3) Ascension confounds
> everything; compare within bands. (4) Small samples: show n next to every rate; win correlations are
> hypotheses. (5) Multiple comparisons: with ~100 cards, some will look significant by chance.

## Room mix per completed act

Means per completed act. An act counts only if the run got past its boss.

| Act | Run outcome | Acts | Monsters | Elites | ? rooms | Shops | Rest sites | Treasure | Median HP% after boss |
|---|---|---|---|---|---|---|---|---|---|
| 1 | win | 10 | 4.5 | 1.2 | 2.7 | 1.5 | 4.1 | 1.0 | 25% |
| 1 | loss | 21 | 5.1 | 0.9 | 3.5 | 0.8 | 3.7 | 1.0 | 20% |
| 2 | win | 10 | 3.6 | 1.6 | 3.1 | 1.1 | 3.6 | 1.0 | 43% |
| 2 | loss | 7 | 4.6 | 0.9 | 2.7 | 1.3 | 3.6 | 1.0 | 24% |
| 3 | win | 10 | 4.1 | 0.9 | 2.5 | 1.3 | 3.2 | 1.0 | 58% |

## Elites fought in an act, against surviving it

| Act | Elites (3 = 3+) | Acts | Survived the act | Rate |
|---|---|---|---|---|
| 1 | 0 | 15 | 11 | 73% |
| 1 | 1 | 20 | 13 | 65% |
| 1 | 2 | 8 | 5 | 62% |
| 1 | 3 | 2 | 2 | 100% |
| 2 | 0 | 10 | 5 | 50% |
| 2 | 1 | 11 | 5 | 45% |
| 2 | 2 | 7 | 4 | 57% |
| 2 | 3 | 3 | 3 | 100% |
| 3 | 0 | 5 | 3 | 60% |
| 3 | 1 | 9 | 5 | 56% |
| 3 | 2 | 3 | 2 | 67% |

Survival here is confounded: strong decks both take more elites and survive. It does not show that elites are safe.

## Rest sites

| HP on arrival | Visits | Heal | Smith | Other | Before boss | Heal before boss |
|---|---|---|---|---|---|---|
| 0–30% | 45 | 84% | 13% | 1 | 19 | 95% |
| 30–50% | 76 | 28% | 68% | 3 | 21 | 33% |
| 50–70% | 111 | 7% | 88% | 5 | 20 | 20% |
| 70–90% | 58 | 12% | 83% | 3 | 15 | 20% |
| 90–100% | 22 | 18% | 77% | 1 | 7 | 29% |

- **Estimated threshold** (logistic fit, HEAL vs SMITH): the Player is equally likely to heal or smith at **31% HP** (n=299).
  - Right before a boss: 42% (n=82). Other rest sites: 27% (n=217).
- Other options used: COOK ×5, KINDLE ×4, LIFT ×3, CLONE ×1.

## Shops

| Act | Visits | Median gold on arrival | Median spent | Bought nothing | Cards | Colorless | Relics | Potions | Removals |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 49 | 134 | 121 | 16% | 45 | 16 | 9 | 5 | 7 |
| 2 | 32 | 210 | 152 | 6% | 18 | 9 | 17 | 5 | 16 |
| 3 | 20 | 272 | 242 | 15% | 4 | 7 | 10 | 7 | 7 |

Most bought relics: MINIATURE_TENT ×3, LANTERN ×2, BAG_OF_PREPARATION ×2, HAPPY_FLOWER ×2, PENDULUM ×2, CANDELABRA ×2, FENCING_MANUAL ×2, BELT_BUCKLE ×2, SLING_OF_COURAGE ×1, STRAWBERRY ×1.

Most bought potions: ENERGY_POTION ×3, SKILL_POTION ×3, STAR_POTION ×2, FLEX_POTION ×1, SWIFT_POTION ×1, COLORLESS_POTION ×1, COSMIC_CONCOCTION ×1, HEART_OF_IRON ×1.

## Events

Choice names are the option keys from the game's localisation. The HP and gold columns are mean net changes over the floor.

| Event | Visits | Choices | Mean HP change | Mean gold change |
|---|---|---|---|---|
| ENDLESS_CONVEYOR | 30 | CAVIAR ×5; OBSERVE_CHEF ×4; SPICY_SNAPPY ×4; CLAM_ROLL ×4 | 19.8 | -289 |
| BRAIN_LEECH | 12 | SHARE_KNOWLEDGE ×7; RIP ×5 | -2.1 | 0 |
| THE_LEGENDS_WERE_TRUE | 12 | NAB_THE_MAP ×12 | 0.0 | 1 |
| SELF_HELP_BOOK | 12 | READ_THE_BACK ×8; READ_PASSAGE ×3; READ_ENTIRE_BOOK ×1 | 0.0 | 0 |
| THIS_OR_THAT | 12 | ORNATE ×10; PLAIN ×2 | -1.0 | 7 |
| SLIPPERY_BRIDGE | 9 | OVERCOME ×5; HOLD_ON_0 ×2; HOLD_ON_1 ×1; HOLD_ON_2 ×1 | -6.0 | 0 |
| TINKER_TIME | 9 | CHOOSE_CARD_TYPE ×3; SKILL ×2; ENERGIZED ×2; POWER ×1 | 0.0 | 0 |
| ROOM_FULL_OF_CHEESE | 8 | GORGE ×8 | 0.0 | 4 |
| TRIAL | 7 | ACCEPT ×3; INNOCENT ×2; REJECT ×1; GUILTY ×1 | 9.7 | 129 |
| DROWNING_BEACON | 6 | CLIMB ×6 | 0.0 | 0 |
| SUNKEN_STATUE | 6 | GRAB_SWORD ×4; DIVE_INTO_WATER ×2 | -2.3 | 36 |
| SPIRALING_WHIRLPOOL | 6 | OBSERVE ×5; DRINK ×1 | 3.3 | 0 |
| ABYSSAL_BATHS | 5 | LINGER ×2; IMMERSE ×1; EXIT_BATHS ×1; ABSTAIN ×1 | -2.8 | 0 |
| MORPHIC_GROVE | 5 | GROUP ×3; LONER ×2 | 2.0 | -78 |
| STONE_OF_ALL_TIME | 5 | PUSH ×4; LIFT ×1 | -2.8 | 0 |
| BUGSLAYER | 5 | SQUASH ×3; EXTERMINATION ×2 | 0.0 | 0 |
| SUNKEN_TREASURY | 5 | SECOND_CHEST ×5 | 0.0 | 333 |
| RANWID_THE_ELDER | 4 | RELIC ×2; GOLD ×2 | 0.0 | -50 |
| DOORS_OF_LIGHT_AND_DARK | 4 | LIGHT ×4 | 0.0 | 0 |
| DENSE_VEGETATION | 4 | TRUDGE_ON ×2; REST ×1; FIGHT ×1 | 6.5 | 42 |
| THE_FUTURE_OF_POTIONS | 4 | POTION ×4 | 0.0 | 0 |
| DOLL_ROOM | 4 | RANDOM ×4 | 0.0 | 0 |
| POTION_COURIER | 4 | GRAB_POTIONS ×2; RANSACK ×2 | 0.0 | 0 |
| REFLECTIONS | 4 | TOUCH_A_MIRROR ×3; SHATTER ×1 | 9.8 | 0 |
| CRYSTAL_SPHERE | 4 | PAYMENT_PLAN ×4 | 0.0 | 32 |

## Ancients

Ancient visits by Ancient: NEOW ×52, TEZCATARA ×10, PAEL ×9, DARV ×7, OROBAS ×7, TANX ×6, VAKUU ×5, NONUPEIPE ×4.

Options offered 3+ times, by how often the Player took them:

| Option | Offered | Chosen | Rate |
|---|---|---|---|
| PAELS_FLESH | 4 | 4 | 100% |
| ARCHAIC_TOOTH | 4 | 4 | 100% |
| SEAL_OF_GOLD | 3 | 3 | 100% |
| FISHING_ROD | 7 | 6 | 86% |
| HEFTY_TABLET | 6 | 5 | 83% |
| ARCANE_SCROLL | 5 | 4 | 80% |
| NUTRITIOUS_SOUP | 5 | 4 | 80% |
| SILVER_CRUCIBLE | 9 | 7 | 78% |
| CURSED_PEARL | 8 | 6 | 75% |
| ASTROLABE | 4 | 3 | 75% |
| DISTINGUISHED_CAPE | 3 | 2 | 67% |
| PAELS_TEARS | 3 | 2 | 67% |
| PUMPKIN_CANDLE | 3 | 2 | 67% |
| SPIKED_GAUNTLETS | 3 | 2 | 67% |
| SCROLL_BOXES | 8 | 5 | 62% |
| GOLDEN_PEARL | 4 | 2 | 50% |
| DUSTY_TOME | 4 | 2 | 50% |
| SILKEN_TRESS | 10 | 4 | 40% |
| KALEIDOSCOPE | 5 | 2 | 40% |
| LEAD_PAPERWEIGHT | 9 | 3 | 33% |
| VERY_HOT_COCOA | 3 | 1 | 33% |
| PANDORAS_BOX | 3 | 1 | 33% |
| PRECARIOUS_SHEARS | 3 | 1 | 33% |
| SAI | 3 | 1 | 33% |
| TOUCH_OF_OROBAS | 3 | 1 | 33% |
| LAVA_ROCK | 3 | 1 | 33% |
| NEOWS_BONES | 7 | 2 | 29% |
| POMANDER | 5 | 1 | 20% |
| NEW_LEAF | 6 | 1 | 17% |
| PRECISE_SCISSORS | 9 | 0 | 0% |

## Potions

| Room type | Potions used | Fights | Potions per fight |
|---|---|---|---|
| monster | 99 | 471 | 0.21 |
| elite | 69 | 93 | 0.74 |
| boss | 99 | 79 | 1.25 |

- Potions still held at death: mean 0.4, and 12/35 deaths had at least one unused potion.
- Discarded: EXPLOSIVE_AMPOULE ×6, SPEED_POTION ×4, FORTIFIER ×3, VULNERABLE_POTION ×2, FIRE_POTION ×2, DEXTERITY_POTION ×2.

Potion rewards most often left behind (offered 4+ times):

| Potion | Offered | Taken | Rate |
|---|---|---|---|
| LUCKY_TONIC | 4 | 0 | 0% |
| FYSH_OIL | 8 | 1 | 12% |
| FAIRY_IN_A_BOTTLE | 6 | 1 | 17% |
| SHIP_IN_A_BOTTLE | 4 | 1 | 25% |
| STRENGTH_POTION | 20 | 6 | 30% |
| GAMBLERS_BREW | 15 | 5 | 33% |
| BLESSING_OF_THE_FORGE | 14 | 5 | 36% |
| FLEX_POTION | 22 | 9 | 41% |
| ATTACK_POTION | 22 | 9 | 41% |
| HEART_OF_IRON | 12 | 5 | 42% |
