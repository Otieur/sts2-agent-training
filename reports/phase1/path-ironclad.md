# Pathing, Rest, Shops, Events and Potions: Ironclad (v0.107.1)

Runs: 57 solo. Outcome comparisons use finished runs only.

> **Statistical cautions.** (1) Selection bias: what gets offered depends on earlier picks and relics.
> (2) Survivorship: late-floor numbers come only from runs that got there. (3) Ascension confounds
> everything; compare within bands. (4) Small samples: show n next to every rate; win correlations are
> hypotheses. (5) Multiple comparisons: with ~100 cards, some will look significant by chance.

## Room mix per completed act

Means per completed act. An act counts only if the run got past its boss.

| Act | Run outcome | Acts | Monsters | Elites | ? rooms | Shops | Rest sites | Treasure | Median HP% after boss |
|---|---|---|---|---|---|---|---|---|---|
| 1 | win | 12 | 5.0 | 1.2 | 2.8 | 0.9 | 4.0 | 1.0 | 37% |
| 1 | loss | 18 | 4.6 | 1.2 | 3.3 | 1.1 | 3.8 | 1.0 | 21% |
| 2 | win | 12 | 4.4 | 1.0 | 3.0 | 1.2 | 3.3 | 1.0 | 42% |
| 2 | loss | 4 | 3.2 | 0.8 | 4.5 | 1.0 | 3.5 | 1.0 | 29% |
| 3 | win | 12 | 4.3 | 0.7 | 2.2 | 1.5 | 3.2 | 1.0 | 32% |

## Elites fought in an act, against surviving it

| Act | Elites (3 = 3+) | Acts | Survived the act | Rate |
|---|---|---|---|---|
| 1 | 0 | 17 | 7 | 41% |
| 1 | 1 | 22 | 11 | 50% |
| 1 | 2 | 11 | 10 | 91% |
| 1 | 3 | 2 | 2 | 100% |
| 2 | 0 | 10 | 5 | 50% |
| 2 | 1 | 11 | 7 | 64% |
| 2 | 2 | 9 | 4 | 44% |
| 3 | 0 | 8 | 6 | 75% |
| 3 | 1 | 6 | 4 | 67% |
| 3 | 2 | 2 | 2 | 100% |

Survival here is confounded: strong decks both take more elites and survive. It does not show that elites are safe.

## Rest sites

| HP on arrival | Visits | Heal | Smith | Other | Before boss | Heal before boss |
|---|---|---|---|---|---|---|
| 0–30% | 40 | 65% | 35% | 0 | 15 | 87% |
| 30–50% | 63 | 22% | 78% | 0 | 23 | 39% |
| 50–70% | 88 | 5% | 92% | 3 | 23 | 9% |
| 70–90% | 103 | 2% | 90% | 8 | 21 | 0% |
| 90–100% | 33 | 9% | 91% | 0 | 5 | 20% |

- **Estimated threshold** (logistic fit, HEAL vs SMITH): the Player is equally likely to heal or smith at **27% HP** (n=316).
  - Right before a boss: 37% (n=85). Other rest sites: 18% (n=231).
- Other options used: DIG ×8, HATCH ×3.

## Shops

| Act | Visits | Median gold on arrival | Median spent | Bought nothing | Cards | Colorless | Relics | Potions | Removals |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 48 | 191 | 152 | 2% | 29 | 12 | 17 | 9 | 12 |
| 2 | 30 | 244 | 162 | 10% | 21 | 11 | 19 | 4 | 7 |
| 3 | 22 | 222 | 178 | 14% | 7 | 7 | 14 | 12 | 11 |

Most bought relics: BAG_OF_MARBLES ×3, MINIATURE_TENT ×3, VAJRA ×2, ODDLY_SMOOTH_STONE ×2, WING_CHARM ×2, MEMBERSHIP_CARD ×2, RUINED_HELMET ×2, BOOK_OF_FIVE_RINGS ×2, RED_SKULL ×2, VENERABLE_TEA_SET ×2.

Most bought potions: CURE_ALL ×3, ENERGY_POTION ×3, POWER_POTION ×2, DEXTERITY_POTION ×2, BLOCK_POTION ×2, WEAK_POTION ×2, FIRE_POTION ×1, FLEX_POTION ×1.

## Events

Choice names are the option keys from the game's localisation. The HP and gold columns are mean net changes over the floor.

| Event | Visits | Choices | Mean HP change | Mean gold change |
|---|---|---|---|---|
| SLIPPERY_BRIDGE | 23 | OVERCOME ×10; HOLD_ON_0 ×7; HOLD_ON_1 ×4; HOLD_ON_2 ×2 | -6.8 | 0 |
| THIS_OR_THAT | 12 | ORNATE ×8; PLAIN ×4 | -2.0 | 19 |
| ABYSSAL_BATHS | 9 | LINGER ×3; IMMERSE ×2; EXIT_BATHS ×2; ABSTAIN ×2 | -1.4 | 0 |
| DOLL_ROOM | 8 | RANDOM ×4; TAKE_SOME_TIME ×2; DAUGHTER_OF_THE_WIND ×2 | -2.5 | 0 |
| SYMBIOTE | 8 | KILL_WITH_FIRE ×5; APPROACH ×3 | 0.0 | 0 |
| AROMA_OF_CHAOS | 8 | MAINTAIN_CONTROL ×5; LET_GO ×3 | 0.0 | 0 |
| THE_LEGENDS_WERE_TRUE | 7 | NAB_THE_MAP ×7 | 0.0 | 0 |
| ROOM_FULL_OF_CHEESE | 7 | GORGE ×6; SEARCH ×1 | -2.0 | 0 |
| SUNKEN_STATUE | 7 | GRAB_SWORD ×5; DIVE_INTO_WATER ×2 | -2.0 | 31 |
| BYRDONIS_NEST | 7 | EAT ×4; TAKE ×3 | 4.0 | 0 |
| SELF_HELP_BOOK | 6 | READ_THE_BACK ×5; READ_ENTIRE_BOOK ×1 | 0.0 | 0 |
| BRAIN_LEECH | 6 | SHARE_KNOWLEDGE ×5; RIP ×1 | -0.8 | 2 |
| SUNKEN_TREASURY | 6 | SECOND_CHEST ×6 | 0.0 | 342 |
| WHISPERING_HOLLOW | 6 | HUG ×4; GOLD ×2 | -6.0 | -12 |
| THE_FUTURE_OF_POTIONS | 5 | POTION ×5 | 0.0 | 0 |
| DENSE_VEGETATION | 5 | TRUDGE_ON ×3; REST ×1; FIGHT ×1 | -0.6 | 52 |
| INFESTED_AUTOMATON | 5 | TOUCH_CORE ×3; STUDY ×2 | 0.0 | 3 |
| POTION_COURIER | 4 | GRAB_POTIONS ×2; RANSACK ×2 | 0.0 | 0 |
| THE_LANTERN_KEY | 4 | KEEP_THE_KEY ×2; FIGHT ×2 | -4.5 | 11 |
| BUGSLAYER | 4 | EXTERMINATION ×2; SQUASH ×2 | 0.0 | 0 |
| CRYSTAL_SPHERE | 4 | PAYMENT_PLAN ×3; UNCOVER_FUTURE ×1 | 2.8 | 42 |
| BATTLEWORN_DUMMY | 4 | SETTING_2 ×2; SETTING_3 ×1; SETTING_1 ×1 | 4.0 | -4 |
| WELLSPRING | 4 | BATHE ×4 | 0.0 | 0 |
| FIELD_OF_MAN_SIZED_HOLES | 4 | ENTER_YOUR_HOLE ×3; RESIST ×1 | 0.0 | 0 |
| SPIRIT_GRAFTER | 4 | LET_IT_IN ×4 | 11.8 | 0 |

## Ancients

Ancient visits by Ancient: NEOW ×55, PAEL ×11, TEZCATARA ×11, OROBAS ×7, VAKUU ×7, NONUPEIPE ×4, DARV ×4, TANX ×4.

Options offered 3+ times, by how often the Player took them:

| Option | Offered | Chosen | Rate |
|---|---|---|---|
| ARCANE_SCROLL | 5 | 5 | 100% |
| KALEIDOSCOPE | 5 | 5 | 100% |
| FIDDLE | 4 | 4 | 100% |
| PAELS_FLESH | 3 | 3 | 100% |
| SILVER_CRUCIBLE | 3 | 3 | 100% |
| HEFTY_TABLET | 3 | 3 | 100% |
| NEOWS_BONES | 5 | 4 | 80% |
| NUTRITIOUS_SOUP | 4 | 3 | 75% |
| STORYBOOK | 4 | 3 | 75% |
| PAELS_WING | 4 | 3 | 75% |
| ARCHAIC_TOOTH | 3 | 2 | 67% |
| BLESSED_ANTLER | 3 | 2 | 67% |
| POMANDER | 3 | 2 | 67% |
| FISHING_ROD | 7 | 4 | 57% |
| GOLDEN_PEARL | 8 | 4 | 50% |
| SCROLL_BOXES | 8 | 4 | 50% |
| PAELS_BLOOD | 4 | 2 | 50% |
| CURSED_PEARL | 13 | 6 | 46% |
| LEAFY_POULTICE | 7 | 3 | 43% |
| PAELS_TOOTH | 3 | 1 | 33% |
| YUMMY_COOKIE | 3 | 1 | 33% |
| PAELS_CLAW | 3 | 1 | 33% |
| TOY_BOX | 3 | 1 | 33% |
| LARGE_CAPSULE | 7 | 2 | 29% |
| LEAD_PAPERWEIGHT | 7 | 2 | 29% |
| WINGED_BOOTS | 7 | 2 | 29% |
| DISTINGUISHED_CAPE | 4 | 1 | 25% |
| TOUCH_OF_OROBAS | 4 | 1 | 25% |
| PHIAL_HOLSTER | 10 | 2 | 20% |
| PAELS_HORN | 5 | 1 | 20% |

## Potions

| Room type | Potions used | Fights | Potions per fight |
|---|---|---|---|
| monster | 146 | 509 | 0.29 |
| elite | 77 | 92 | 0.84 |
| boss | 99 | 87 | 1.14 |

- Potions still held at death: mean 0.1, and 4/40 deaths had at least one unused potion.
- Discarded: FLEX_POTION ×5, SPEED_POTION ×4, GAMBLERS_BREW ×3, SWIFT_POTION ×3, FIRE_POTION ×2, DEXTERITY_POTION ×2.

Potion rewards most often left behind (offered 4+ times):

| Potion | Offered | Taken | Rate |
|---|---|---|---|
| DUPLICATOR | 6 | 1 | 17% |
| SKILL_POTION | 21 | 4 | 19% |
| POTION_OF_BINDING | 16 | 4 | 25% |
| DISTILLED_CHAOS | 8 | 2 | 25% |
| DROPLET_OF_PRECOGNITION | 4 | 1 | 25% |
| HEART_OF_IRON | 11 | 4 | 36% |
| FIRE_POTION | 27 | 10 | 37% |
| LIQUID_BRONZE | 13 | 5 | 38% |
| FYSH_OIL | 5 | 2 | 40% |
| POWER_POTION | 31 | 14 | 45% |
