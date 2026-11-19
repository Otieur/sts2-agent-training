# Card Analysis: Silent (v0.107.1)

Runs: 51 solo (43 finished, 10 wins). Card reward screens: 604. Cards offered: 1816.

> **Statistical cautions.** (1) Selection bias: what gets offered depends on earlier picks and relics.
> (2) Survivorship: late-floor numbers come only from runs that got there. (3) Ascension confounds
> everything; compare within bands. (4) Small samples: show n next to every rate; win correlations are
> hypotheses. (5) Multiple comparisons: with ~100 cards, some will look significant by chance.

## Most-picked cards (offered 8+ times)

| Card | Offered | Picked | Pick rate | 95% CI |
|---|---|---|---|---|
| TACTICIAN | 17 | 16 | 94% | 73%–99% |
| ABRASIVE | 10 | 9 | 90% | 60%–98% |
| TOOLS_OF_THE_TRADE | 10 | 8 | 80% | 49%–94% |
| ESCAPE_PLAN | 23 | 18 | 78% | 58%–90% |
| EXPOSE | 18 | 14 | 78% | 55%–91% |
| ACROBATICS | 29 | 21 | 72% | 54%–85% |
| TRACKING | 9 | 6 | 67% | 35%–88% |
| HAZE | 16 | 10 | 62% | 39%–82% |
| MURDER | 8 | 5 | 62% | 31%–86% |
| STORM_OF_STEEL | 8 | 5 | 62% | 31%–86% |
| MEMENTO_MORI | 16 | 9 | 56% | 33%–77% |
| SERPENT_FORM | 9 | 5 | 56% | 27%–81% |
| AFTERIMAGE | 9 | 5 | 56% | 27%–81% |
| PINPOINT | 13 | 7 | 54% | 29%–77% |
| PREPARED | 44 | 23 | 52% | 38%–66% |
| RICOCHET | 47 | 24 | 51% | 37%–65% |
| CALCULATED_GAMBLE | 28 | 14 | 50% | 33%–67% |
| POUNCE | 16 | 8 | 50% | 28%–72% |
| DAGGER_THROW | 49 | 24 | 49% | 36%–62% |
| UNTOUCHABLE | 40 | 19 | 48% | 33%–62% |

## Least-picked cards (offered 8+ times)

| Card | Offered | Picked | Pick rate | 95% CI |
|---|---|---|---|---|
| SNAKEBITE | 43 | 0 | 0% | 0%–8% |
| SKEWER | 19 | 0 | 0% | 0%–17% |
| STRANGLE | 15 | 0 | 0% | 0%–20% |
| BOUNCING_FLASK | 12 | 0 | 0% | 0%–24% |
| BULLET_TIME | 11 | 0 | 0% | 0%–26% |
| FAN_OF_KNIVES | 8 | 0 | 0% | 0%–32% |
| DEFLECT | 54 | 1 | 2% | 0%–10% |
| DODGE_AND_ROLL | 39 | 1 | 3% | 0%–13% |
| POISONED_STAB | 65 | 4 | 6% | 2%–15% |
| SLICE | 48 | 3 | 6% | 2%–17% |
| BLUR | 16 | 1 | 6% | 1%–28% |
| ANTICIPATE | 46 | 3 | 6% | 2%–18% |
| DEADLY_POISON | 52 | 4 | 8% | 3%–18% |
| CLOAK_AND_DAGGER | 53 | 5 | 9% | 4%–20% |
| NOXIOUS_FUMES | 10 | 1 | 10% | 2%–40% |

Full table: `card-picks-silent.csv`. Head-to-head ranking: `card-ranking-silent.md`.

## Skips

| Act | Screens | Skipped | Skip rate |
|---|---|---|---|
| 1 | 313 | 24 | 8% |
| 2 | 177 | 35 | 20% |
| 3 | 114 | 40 | 35% |

| Deck size | Screens | Skipped | Skip rate |
|---|---|---|---|
| <15 | 53 | 1 | 2% |
| 15-19 | 172 | 15 | 9% |
| 20-24 | 151 | 17 | 11% |
| 25-29 | 123 | 34 | 28% |
| 30+ | 105 | 32 | 30% |

## Context effects

- **Upgraded offers:** picked 33% of the time (n=243), against 27% for base versions (n=1573).
- **Duplicates:** a card already in the deck is picked 29% of the time (n=242), against 28% for new cards (n=1574).

Cards whose pick rate changes most when a copy is already in the deck (5+ offers each way):

| Card | First copy: offered | First copy: pick rate | Already owned: offered | Already owned: pick rate |
|---|---|---|---|---|
| RICOCHET | 26 | 77% | 21 | 19% |
| EXPERTISE | 14 | 43% | 5 | 0% |
| ACROBATICS | 16 | 88% | 13 | 54% |
| LEG_SWEEP | 20 | 50% | 6 | 17% |
| DAGGER_THROW | 29 | 62% | 20 | 30% |
| PREPARED | 27 | 63% | 17 | 35% |
| CALCULATED_GAMBLE | 22 | 55% | 6 | 33% |
| BACKFLIP | 40 | 20% | 6 | 0% |
| FLICK_FLACK | 38 | 37% | 16 | 19% |
| PIERCING_WAIL | 37 | 49% | 19 | 32% |
| ESCAPE_PLAN | 17 | 82% | 6 | 67% |
| DAGGER_SPRAY | 34 | 26% | 6 | 17% |

Card types (attack, skill, power) are not in the run files. Context rules by card type wait for the game data in Phase 2.

## Outcome association (weak evidence, `[PLAYER-DATA]`)

Win rate of finished runs whose **final deck** contains the card, against those that do not. Cards in 10+ finished runs. Per-band cells read wins/runs with the card vs wins/runs without it.

| Card | Runs with | Win rate with | Win rate without | A0-4 | A5-9 | A10 |
|---|---|---|---|---|---|---|
| ACROBATICS | 17 | 47% | 8% | 4/7 vs 1/4 | 4/5 vs 1/11 | 0/5 vs 0/11 |
| LEG_SWEEP | 12 | 50% | 13% | 2/2 vs 3/9 | 4/5 vs 1/11 | 0/5 vs 0/11 |
| CALCULATED_GAMBLE | 15 | 40% | 14% | 2/3 vs 3/8 | 4/7 vs 1/9 | 0/5 vs 0/11 |
| ABRASIVE | 11 | 36% | 19% | 3/4 vs 2/7 | 1/4 vs 4/12 | 0/3 vs 0/13 |
| DAGGER_SPRAY | 11 | 36% | 19% | 1/1 vs 4/10 | 3/8 vs 2/8 | 0/2 vs 0/14 |
| POUNCE | 11 | 36% | 19% | 1/1 vs 4/10 | 3/4 vs 2/12 | 0/6 vs 0/10 |
| ESCAPE_PLAN | 18 | 33% | 16% | 4/7 vs 1/4 | 2/6 vs 3/10 | 0/5 vs 0/11 |
| UNTOUCHABLE | 18 | 33% | 16% | 3/6 vs 2/5 | 3/6 vs 2/10 | 0/6 vs 0/10 |
| TACTICIAN | 15 | 33% | 18% | 3/5 vs 2/6 | 2/5 vs 3/11 | 0/5 vs 0/11 |
| PREPARED | 23 | 30% | 15% | 3/5 vs 2/6 | 4/8 vs 1/8 | 0/10 vs 0/6 |
| EXPOSE | 13 | 31% | 20% | 1/3 vs 4/8 | 3/7 vs 2/9 | 0/3 vs 0/13 |
| RICOCHET | 21 | 29% | 18% | 3/6 vs 2/5 | 3/10 vs 2/6 | 0/5 vs 0/11 |
| PIERCING_WAIL | 21 | 29% | 18% | 2/6 vs 3/5 | 4/10 vs 1/6 | 0/5 vs 0/11 |
| BACKFLIP | 10 | 30% | 21% | 2/4 vs 3/7 | 1/2 vs 4/14 | 0/4 vs 0/12 |
| DAGGER_THROW | 19 | 26% | 21% | 3/5 vs 2/6 | 2/8 vs 3/8 | 0/6 vs 0/10 |

Survivorship warning: cards picked late only appear in runs that got far, so they look like winners. Treat every row as a hypothesis.

## Upgrade priorities (rest-site Smith)

| Card | Smith upgrades (all) | As 1st upgrade | As 2nd | As 3rd |
|---|---|---|---|---|
| NEUTRALIZE | 19 | 9 | 6 | 2 |
| PREPARED | 18 | 6 | 4 | 1 |
| RICOCHET | 14 | 0 | 4 | 4 |
| SURVIVOR | 10 | 2 | 3 | 2 |
| TOOLS_OF_THE_TRADE | 9 | 3 | 1 | 0 |
| ACROBATICS | 9 | 2 | 1 | 0 |
| TACTICIAN | 8 | 0 | 1 | 3 |
| MURDER | 7 | 2 | 0 | 1 |
| ABRASIVE | 6 | 2 | 1 | 0 |
| SHADOWMELD | 6 | 2 | 0 | 0 |
| CALCULATED_GAMBLE | 6 | 2 | 0 | 1 |
| SHADOW_STEP | 5 | 0 | 0 | 0 |
| MEMENTO_MORI | 5 | 1 | 0 | 0 |
| LEG_SWEEP | 5 | 0 | 0 | 2 |
| DAGGER_SPRAY | 5 | 2 | 2 | 1 |

Upgrades from other sources (events, relics, Ancients): 77.

## Removals

| Card | Removed |
|---|---|
| STRIKE_SILENT | 26 |
| DEFEND_SILENT | 19 |
| SPOILS_MAP | 4 |
| TACTICIAN | 3 |
| DECAY | 3 |
| GUILTY | 3 |
| INJURY | 3 |
| CLUMSY | 2 |
| SPORE_MIND | 2 |
| HAZE | 2 |

Removal sources: unknown 29, shop 23, monster 13, rest_site 6, ancient 5, treasure 4, elite 1. Runs with at least one removal: 29/51; median floor of the first removal: 15.

## Shop card purchases

| Card | Seen in shop | Bought |
|---|---|---|
| PREPARED | 12 | 7 |
| ACROBATICS | 9 | 6 |
| HIDDEN_GEM | 10 | 5 |
| UNTOUCHABLE | 9 | 5 |
| PIERCING_WAIL | 12 | 4 |
| ESCAPE_PLAN | 7 | 4 |
| NOXIOUS_FUMES | 14 | 4 |
| CALCULATED_GAMBLE | 8 | 4 |
| POUNCE | 8 | 4 |
| RICOCHET | 14 | 3 |
| PRODUCTION | 6 | 3 |
| PINPOINT | 10 | 3 |
