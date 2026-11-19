# Card Analysis: Ironclad (v0.107.1)

Runs: 57 solo (52 finished, 12 wins). Card reward screens: 632. Cards offered: 1907.

> **Statistical cautions.** (1) Selection bias: what gets offered depends on earlier picks and relics.
> (2) Survivorship: late-floor numbers come only from runs that got there. (3) Ascension confounds
> everything; compare within bands. (4) Small samples: show n next to every rate; win correlations are
> hypotheses. (5) Multiple comparisons: with ~100 cards, some will look significant by chance.

## Most-picked cards (offered 8+ times)

| Card | Offered | Picked | Pick rate | 95% CI |
|---|---|---|---|---|
| DOMINATE | 20 | 19 | 95% | 76%–99% |
| PYRE | 13 | 11 | 85% | 58%–96% |
| FIGHT_ME | 14 | 11 | 79% | 52%–92% |
| SECOND_WIND | 19 | 13 | 68% | 46%–85% |
| EVIL_EYE | 21 | 14 | 67% | 45%–83% |
| BURNING_PACT | 18 | 11 | 61% | 39%–80% |
| STAMPEDE | 17 | 9 | 53% | 31%–74% |
| COLOSSUS | 19 | 10 | 53% | 32%–73% |
| ASHEN_STRIKE | 10 | 5 | 50% | 24%–76% |
| VICIOUS | 25 | 12 | 48% | 30%–66% |
| TRUE_GRIT | 49 | 23 | 47% | 34%–61% |
| TREMBLE | 54 | 24 | 44% | 32%–58% |
| AGGRESSION | 9 | 4 | 44% | 19%–73% |
| DRUM_OF_BATTLE | 21 | 9 | 43% | 24%–64% |
| MOLTEN_FIST | 43 | 18 | 42% | 28%–57% |
| BLOODLETTING | 55 | 22 | 40% | 28%–53% |
| FORGOTTEN_RITUAL | 18 | 7 | 39% | 20%–61% |
| ARMAMENTS | 65 | 25 | 38% | 28%–51% |
| INFERNAL_BLADE | 11 | 4 | 36% | 15%–65% |
| ONE_TWO_PUNCH | 11 | 4 | 36% | 15%–65% |

## Least-picked cards (offered 8+ times)

| Card | Offered | Picked | Pick rate | 95% CI |
|---|---|---|---|---|
| JUGGLING | 15 | 0 | 0% | 0%–20% |
| EXPECT_A_FIGHT | 14 | 0 | 0% | 0%–22% |
| WHIRLWIND | 13 | 0 | 0% | 0%–23% |
| UNMOVABLE | 9 | 0 | 0% | 0%–30% |
| BLOOD_WALL | 55 | 1 | 2% | 0%–10% |
| ANGER | 53 | 2 | 4% | 1%–13% |
| PERFECTED_STRIKE | 52 | 2 | 4% | 1%–13% |
| HEMOKINESIS | 25 | 1 | 4% | 1%–20% |
| STONE_ARMOR | 22 | 1 | 4% | 1%–22% |
| BLUDGEON | 21 | 1 | 5% | 1%–23% |
| SPITE | 26 | 2 | 8% | 2%–24% |
| BODY_SLAM | 45 | 4 | 9% | 4%–21% |
| SETUP_STRIKE | 51 | 5 | 10% | 4%–21% |
| RAMPAGE | 26 | 3 | 12% | 4%–29% |
| IRON_WAVE | 66 | 8 | 12% | 6%–22% |

Full table: `card-picks-ironclad.csv`. Head-to-head ranking: `card-ranking-ironclad.md`.

## Skips

| Act | Screens | Skipped | Skip rate |
|---|---|---|---|
| 1 | 374 | 36 | 10% |
| 2 | 182 | 56 | 31% |
| 3 | 76 | 37 | 49% |

| Deck size | Screens | Skipped | Skip rate |
|---|---|---|---|
| <15 | 153 | 7 | 5% |
| 15-19 | 220 | 34 | 15% |
| 20-24 | 140 | 37 | 26% |
| 25-29 | 83 | 33 | 40% |
| 30+ | 36 | 18 | 50% |

## Context effects

- **Upgraded offers:** picked 34% of the time (n=217), against 25% for base versions (n=1690).
- **Duplicates:** a card already in the deck is picked 21% of the time (n=216), against 27% for new cards (n=1691).

Cards whose pick rate changes most when a copy is already in the deck (5+ offers each way):

| Card | First copy: offered | First copy: pick rate | Already owned: offered | Already owned: pick rate |
|---|---|---|---|---|
| ARMAMENTS | 38 | 66% | 27 | 0% |
| BREAKTHROUGH | 39 | 51% | 23 | 4% |
| SHRUG_IT_OFF | 59 | 36% | 14 | 0% |
| TREMBLE | 37 | 54% | 17 | 24% |
| EVIL_EYE | 15 | 73% | 6 | 50% |
| POMMEL_STRIKE | 37 | 19% | 10 | 0% |
| MOLTEN_FIST | 33 | 45% | 10 | 30% |
| BODY_SLAM | 40 | 10% | 5 | 0% |
| TRUE_GRIT | 34 | 50% | 15 | 40% |
| SWORD_BOOMERANG | 53 | 17% | 5 | 20% |
| BLOODLETTING | 41 | 39% | 14 | 43% |
| DOMINATE | 15 | 93% | 5 | 100% |

Card types (attack, skill, power) are not in the run files. Context rules by card type wait for the game data in Phase 2.

## Outcome association (weak evidence, `[PLAYER-DATA]`)

Win rate of finished runs whose **final deck** contains the card, against those that do not. Cards in 10+ finished runs. Per-band cells read wins/runs with the card vs wins/runs without it.

| Card | Runs with | Win rate with | Win rate without | A0-4 | A5-9 | A10 |
|---|---|---|---|---|---|---|
| DOMINATE | 15 | 53% | 11% | 3/3 vs 2/5 | 4/7 vs 1/13 | 1/5 vs 1/19 |
| TRUE_GRIT | 24 | 42% | 7% | 5/6 vs 0/2 | 5/13 vs 0/7 | 0/5 vs 2/19 |
| FIGHT_ME | 15 | 47% | 14% | 5/5 vs 0/3 | 2/7 vs 3/13 | 0/3 vs 2/21 |
| MOLTEN_FIST | 19 | 42% | 12% | 4/4 vs 1/4 | 3/9 vs 2/11 | 1/6 vs 1/18 |
| TREMBLE | 25 | 36% | 11% | 3/5 vs 2/3 | 5/12 vs 0/8 | 1/8 vs 1/16 |
| SECOND_WIND | 12 | 42% | 18% | 1/2 vs 4/6 | 3/6 vs 2/14 | 1/4 vs 1/20 |
| BLOODLETTING | 19 | 37% | 15% | 3/5 vs 2/3 | 3/7 vs 2/13 | 1/7 vs 1/17 |
| COLOSSUS | 10 | 40% | 19% | 3/4 vs 2/4 | 0/3 vs 5/17 | 1/3 vs 1/21 |
| PYRE | 11 | 36% | 20% | 2/3 vs 3/5 | 2/5 vs 3/15 | 0/3 vs 2/21 |
| ARMAMENTS | 31 | 29% | 14% | 4/6 vs 1/2 | 3/12 vs 2/8 | 2/13 vs 0/11 |
| EVIL_EYE | 15 | 33% | 19% | 1/3 vs 4/5 | 2/4 vs 3/16 | 2/8 vs 0/16 |
| BURNING_PACT | 12 | 33% | 20% | 1/2 vs 4/6 | 3/7 vs 2/13 | 0/3 vs 2/21 |
| SWORD_BOOMERANG | 11 | 27% | 22% | 2/3 vs 3/5 | 1/5 vs 4/15 | 0/3 vs 2/21 |
| GREED | 11 | 27% | 22% | 1/2 vs 4/6 | 2/4 vs 3/16 | 0/5 vs 2/19 |
| STAMPEDE | 11 | 27% | 22% | 0/0 vs 5/8 | 1/2 vs 4/18 | 2/9 vs 0/15 |

Survivorship warning: cards picked late only appear in runs that got far, so they look like winners. Treat every row as a hypothesis.

## Upgrade priorities (rest-site Smith)

| Card | Smith upgrades (all) | As 1st upgrade | As 2nd | As 3rd |
|---|---|---|---|---|
| ARMAMENTS | 26 | 18 | 1 | 5 |
| TRUE_GRIT | 16 | 2 | 5 | 1 |
| BASH | 16 | 2 | 5 | 6 |
| DOMINATE | 11 | 3 | 1 | 1 |
| VICIOUS | 10 | 1 | 0 | 1 |
| STAMPEDE | 10 | 2 | 1 | 2 |
| PYRE | 9 | 0 | 0 | 0 |
| FIGHT_ME | 8 | 2 | 1 | 1 |
| BREAKTHROUGH | 6 | 1 | 3 | 1 |
| BLOODLETTING | 6 | 1 | 0 | 1 |
| SHRUG_IT_OFF | 6 | 2 | 1 | 1 |
| ONE_TWO_PUNCH | 6 | 1 | 1 | 2 |
| EVIL_EYE | 5 | 0 | 1 | 1 |
| STOKE | 5 | 0 | 1 | 2 |
| DARK_EMBRACE | 4 | 0 | 0 | 1 |

Upgrades from other sources (events, relics, Ancients): 88.

## Removals

| Card | Removed |
|---|---|
| STRIKE_IRONCLAD | 23 |
| DEFEND_IRONCLAD | 20 |
| SPOILS_MAP | 4 |
| CLUMSY | 3 |
| INJURY | 3 |
| DEBT | 2 |
| GUILTY | 2 |
| EVIL_EYE | 2 |
| VICIOUS | 2 |
| REGRET | 2 |

Removal sources: shop 30, unknown 26, ancient 11, monster 11, treasure 4, boss 1. Runs with at least one removal: 34/57; median floor of the first removal: 14.

## Shop card purchases

| Card | Seen in shop | Bought |
|---|---|---|
| TREMBLE | 17 | 5 |
| EVIL_EYE | 13 | 5 |
| PRODUCTION | 6 | 5 |
| ARMAMENTS | 24 | 4 |
| TRUE_GRIT | 18 | 4 |
| FIGHT_ME | 7 | 3 |
| VICIOUS | 12 | 3 |
| TAUNT | 10 | 3 |
| MASTER_OF_STRATEGY | 5 | 3 |
| FINESSE | 4 | 3 |
| DOMINATE | 6 | 3 |
| FLASH_OF_STEEL | 3 | 3 |
