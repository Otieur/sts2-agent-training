# Pathing, Rest, Shops, Events and Potions: Necrobinder (v0.107.1)

Runs: 59 solo. Outcome comparisons use finished runs only.

> **Statistical cautions.** (1) Selection bias: what gets offered depends on earlier picks and relics.
> (2) Survivorship: late-floor numbers come only from runs that got there. (3) Ascension confounds
> everything; compare within bands. (4) Small samples: show n next to every rate; win correlations are
> hypotheses. (5) Multiple comparisons: with ~100 cards, some will look significant by chance.

## Room mix per completed act

Means per completed act. An act counts only if the run got past its boss.

| Act | Run outcome | Acts | Monsters | Elites | ? rooms | Shops | Rest sites | Treasure | Median HP% after boss |
|---|---|---|---|---|---|---|---|---|---|
| 1 | win | 11 | 5.4 | 1.0 | 2.5 | 1.3 | 3.9 | 1.0 | 44% |
| 1 | loss | 26 | 5.0 | 0.7 | 3.5 | 1.2 | 3.7 | 1.0 | 23% |
| 2 | win | 11 | 4.0 | 1.2 | 2.6 | 1.8 | 3.5 | 1.1 | 44% |
| 2 | loss | 11 | 4.5 | 1.0 | 2.5 | 1.3 | 3.7 | 1.0 | 35% |
| 3 | win | 11 | 4.6 | 0.8 | 2.1 | 1.2 | 3.3 | 1.0 | 63% |

## Elites fought in an act, against surviving it

| Act | Elites (3 = 3+) | Acts | Survived the act | Rate |
|---|---|---|---|---|
| 1 | 0 | 23 | 18 | 78% |
| 1 | 1 | 19 | 11 | 58% |
| 1 | 2 | 9 | 7 | 78% |
| 1 | 3 | 1 | 1 | 100% |
| 2 | 0 | 15 | 6 | 40% |
| 2 | 1 | 13 | 9 | 69% |
| 2 | 2 | 8 | 6 | 75% |
| 2 | 3 | 1 | 1 | 100% |
| 3 | 0 | 7 | 3 | 43% |
| 3 | 1 | 12 | 7 | 58% |
| 3 | 2 | 2 | 1 | 50% |
| 3 | 3 | 1 | 0 | 0% |

Survival here is confounded: strong decks both take more elites and survive. It does not show that elites are safe.

## Rest sites

| HP on arrival | Visits | Heal | Smith | Other | Before boss | Heal before boss |
|---|---|---|---|---|---|---|
| 0–30% | 41 | 85% | 15% | 0 | 12 | 100% |
| 30–50% | 80 | 40% | 57% | 2 | 34 | 50% |
| 50–70% | 97 | 12% | 87% | 1 | 23 | 30% |
| 70–90% | 103 | 1% | 96% | 3 | 16 | 0% |
| 90–100% | 36 | 0% | 94% | 2 | 11 | 0% |

- **Estimated threshold** (logistic fit, HEAL vs SMITH): the Player is equally likely to heal or smith at **37% HP** (n=349).
  - Right before a boss: 45% (n=96). Other rest sites: 32% (n=253).
- Other options used: KINDLE ×5, COOK ×2, HATCH ×1.

## Shops

| Act | Visits | Median gold on arrival | Median spent | Bought nothing | Cards | Colorless | Relics | Potions | Removals |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 62 | 130 | 94 | 6% | 49 | 12 | 22 | 9 | 8 |
| 2 | 47 | 201 | 166 | 11% | 32 | 15 | 22 | 9 | 12 |
| 3 | 24 | 147 | 87 | 21% | 7 | 6 | 8 | 5 | 5 |

Most bought relics: FAKE_VENERABLE_TEA_SET ×4, ETERNAL_FEATHER ×3, BREAD ×3, BAG_OF_PREPARATION ×3, LANTERN ×3, ORRERY ×2, VENERABLE_TEA_SET ×2, ANCHOR ×2, MINIATURE_TENT ×2, LEES_WAFFLE ×2.

Most bought potions: ENERGY_POTION ×4, SKILL_POTION ×3, REGEN_POTION ×3, BLOCK_POTION ×2, DEXTERITY_POTION ×2, ATTACK_POTION ×2, TOUCH_OF_INSANITY ×2, COLORLESS_POTION ×1.

## Events

Choice names are the option keys from the game's localisation. The HP and gold columns are mean net changes over the floor.

| Event | Visits | Choices | Mean HP change | Mean gold change |
|---|---|---|---|---|
| SLIPPERY_BRIDGE | 19 | OVERCOME ×10; HOLD_ON_0 ×8; HOLD_ON_1 ×1 | -3.3 | 0 |
| ENDLESS_CONVEYOR | 18 | CAVIAR ×4; LEAVE ×3; SEAPUNK_SALAD ×2; SPICY_SNAPPY ×2 | 14.2 | -167 |
| ABYSSAL_BATHS | 16 | ABSTAIN ×6; LINGER ×4; IMMERSE ×3; EXIT_BATHS ×3 | 0.8 | 0 |
| THIS_OR_THAT | 11 | ORNATE ×10; PLAIN ×1 | 0.7 | 6 |
| SELF_HELP_BOOK | 11 | READ_PASSAGE ×5; READ_ENTIRE_BOOK ×3; READ_THE_BACK ×3 | 0.5 | 0 |
| SYMBIOTE | 9 | KILL_WITH_FIRE ×6; APPROACH ×3 | 0.0 | 0 |
| ROOM_FULL_OF_CHEESE | 9 | GORGE ×7; SEARCH ×2 | -3.1 | 0 |
| THE_LEGENDS_WERE_TRUE | 8 | NAB_THE_MAP ×8 | 0.0 | 0 |
| BRAIN_LEECH | 8 | SHARE_KNOWLEDGE ×5; RIP ×3 | -1.2 | 0 |
| DROWNING_BEACON | 8 | CLIMB ×5; BOTTLE ×3 | 0.0 | 0 |
| SUNKEN_STATUE | 8 | GRAB_SWORD ×4; DIVE_INTO_WATER ×4 | -3.5 | 56 |
| POTION_COURIER | 7 | RANSACK ×5; GRAB_POTIONS ×2 | 0.0 | 0 |
| SUNKEN_TREASURY | 7 | SECOND_CHEST ×7 | 0.0 | 334 |
| THE_FUTURE_OF_POTIONS | 6 | POTION ×6 | 0.0 | 2 |
| BATTLEWORN_DUMMY | 6 | SETTING_2 ×4; SETTING_1 ×2 | 2.8 | 0 |
| DOORS_OF_LIGHT_AND_DARK | 6 | DARK ×3; LIGHT ×3 | 0.0 | 0 |
| TINKER_TIME | 6 | CHOOSE_CARD_TYPE ×2; SKILL ×2; WISDOM ×1; CHAOS ×1 | 0.0 | 0 |
| RANWID_THE_ELDER | 5 | GOLD ×3; POTION ×2 | 1.0 | 0 |
| SPIRIT_GRAFTER | 5 | LET_IT_IN ×5 | 23.4 | 0 |
| SAPPHIRE_SEED | 5 | EAT ×5 | 9.0 | 0 |
| BUGSLAYER | 5 | EXTERMINATION ×4; SQUASH ×1 | 0.0 | 0 |
| BYRDONIS_NEST | 5 | EAT ×3; TAKE ×2 | 4.2 | 3 |
| WOOD_CARVINGS | 5 | BIRD ×3; SNAKE ×2 | 0.0 | 0 |
| TRIAL | 5 | ACCEPT ×2; INNOCENT ×2; REJECT ×1 | 0.0 | 0 |
| WHISPERING_HOLLOW | 4 | HUG ×2; GOLD ×2 | -4.5 | -16 |

## Ancients

Ancient visits by Ancient: NEOW ×58, TEZCATARA ×13, OROBAS ×13, NONUPEIPE ×9, VAKUU ×7, PAEL ×7, DARV ×6, TANX ×4.

Options offered 3+ times, by how often the Player took them:

| Option | Offered | Chosen | Rate |
|---|---|---|---|
| ASTROLABE | 3 | 3 | 100% |
| BRILLIANT_SCARF | 3 | 3 | 100% |
| GOLDEN_PEARL | 7 | 6 | 86% |
| ARCANE_SCROLL | 5 | 4 | 80% |
| SAND_CASTLE | 4 | 3 | 75% |
| ARCHAIC_TOOTH | 4 | 3 | 75% |
| FISHING_ROD | 9 | 6 | 67% |
| SERE_TALON | 3 | 2 | 67% |
| VERY_HOT_COCOA | 3 | 2 | 67% |
| BLOOD_SOAKED_ROSE | 3 | 2 | 67% |
| DUSTY_TOME | 3 | 2 | 67% |
| KALEIDOSCOPE | 11 | 7 | 64% |
| HEFTY_TABLET | 8 | 5 | 62% |
| PUMPKIN_CANDLE | 5 | 3 | 60% |
| WINGED_BOOTS | 9 | 5 | 56% |
| SCROLL_BOXES | 10 | 5 | 50% |
| NUTRITIOUS_SOUP | 8 | 4 | 50% |
| PAELS_TEARS | 6 | 3 | 50% |
| FUR_COAT | 4 | 2 | 50% |
| BLESSED_ANTLER | 4 | 2 | 50% |
| LARGE_CAPSULE | 4 | 2 | 50% |
| LAVA_ROCK | 4 | 2 | 50% |
| ELECTRIC_SHRYMP | 4 | 2 | 50% |
| TOUCH_OF_OROBAS | 9 | 4 | 44% |
| NEOWS_BONES | 5 | 2 | 40% |
| SILVER_CRUCIBLE | 8 | 3 | 38% |
| CURSED_PEARL | 8 | 3 | 38% |
| LOST_COFFER | 12 | 4 | 33% |
| TOY_BOX | 3 | 1 | 33% |
| GOLDEN_COMPASS | 4 | 1 | 25% |

## Potions

| Room type | Potions used | Fights | Potions per fight |
|---|---|---|---|
| monster | 177 | 581 | 0.30 |
| elite | 73 | 93 | 0.78 |
| boss | 102 | 96 | 1.06 |

- Potions still held at death: mean 0.3, and 9/41 deaths had at least one unused potion.
- Discarded: EXPLOSIVE_AMPOULE ×5, SPEED_POTION ×4, SWIFT_POTION ×4, WEAK_POTION ×3, ATTACK_POTION ×3, GLOWWATER_POTION ×2.

Potion rewards most often left behind (offered 4+ times):

| Potion | Offered | Taken | Rate |
|---|---|---|---|
| BLOCK_POTION | 26 | 8 | 31% |
| LIQUID_BRONZE | 15 | 5 | 33% |
| OROBIC_ACID | 6 | 2 | 33% |
| SHIP_IN_A_BOTTLE | 6 | 2 | 33% |
| DISTILLED_CHAOS | 6 | 2 | 33% |
| FAIRY_IN_A_BOTTLE | 11 | 4 | 36% |
| DUPLICATOR | 8 | 3 | 38% |
| FLEX_POTION | 33 | 13 | 39% |
| MAZALETHS_GIFT | 5 | 2 | 40% |
| GIGANTIFICATION_POTION | 5 | 2 | 40% |
