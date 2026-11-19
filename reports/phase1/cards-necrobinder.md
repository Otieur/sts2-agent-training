# Card Analysis: Necrobinder (v0.107.1)

Runs: 59 solo (52 finished, 11 wins). Card reward screens: 718. Cards offered: 2166.

> **Statistical cautions.** (1) Selection bias: what gets offered depends on earlier picks and relics.
> (2) Survivorship: late-floor numbers come only from runs that got there. (3) Ascension confounds
> everything; compare within bands. (4) Small samples: show n next to every rate; win correlations are
> hypotheses. (5) Multiple comparisons: with ~100 cards, some will look significant by chance.

## Most-picked cards (offered 8+ times)

| Card | Offered | Picked | Pick rate | 95% CI |
|---|---|---|---|---|
| DEMESNE | 16 | 15 | 94% | 72%–99% |
| FETCH | 21 | 19 | 90% | 71%–97% |
| BORROWED_TIME | 14 | 12 | 86% | 60%–96% |
| NEUROSURGE | 13 | 11 | 85% | 58%–96% |
| ENFEEBLING_TOUCH | 22 | 17 | 77% | 57%–90% |
| FRIENDSHIP | 14 | 10 | 71% | 45%–88% |
| SENTRY_MODE | 10 | 7 | 70% | 40%–89% |
| DEATHS_DOOR | 18 | 12 | 67% | 44%–84% |
| MELANCHOLY | 18 | 12 | 67% | 44%–84% |
| SEANCE | 18 | 12 | 67% | 44%–84% |
| HANG | 9 | 6 | 67% | 35%–88% |
| DEATH_MARCH | 29 | 18 | 62% | 44%–77% |
| PUTREFY | 30 | 18 | 60% | 42%–75% |
| NO_ESCAPE | 14 | 8 | 57% | 33%–79% |
| RATTLE | 15 | 8 | 53% | 30%–75% |
| DIRGE | 21 | 11 | 52% | 32%–72% |
| END_OF_DAYS | 10 | 5 | 50% | 24%–76% |
| OBLIVION | 9 | 4 | 44% | 19%–73% |
| WISP | 66 | 28 | 42% | 31%–54% |
| PARSE | 27 | 11 | 41% | 24%–59% |

## Least-picked cards (offered 8+ times)

| Card | Offered | Picked | Pick rate | 95% CI |
|---|---|---|---|---|
| LETHALITY | 24 | 0 | 0% | 0%–14% |
| SPUR | 16 | 0 | 0% | 0%–19% |
| NECRO_MASTERY | 15 | 0 | 0% | 0%–20% |
| ERADICATE | 10 | 0 | 0% | 0%–28% |
| EIDOLON | 9 | 0 | 0% | 0%–30% |
| REAP | 70 | 1 | 1% | 0%–8% |
| SCULPTING_STRIKE | 61 | 2 | 3% | 1%–11% |
| REAVE | 59 | 2 | 3% | 1%–12% |
| DANSE_MACABRE | 22 | 1 | 4% | 1%–22% |
| BURY | 21 | 1 | 5% | 1%–23% |
| DEFILE | 51 | 3 | 6% | 2%–16% |
| DELAY | 17 | 1 | 6% | 1%–27% |
| MISERY | 13 | 1 | 8% | 1%–33% |
| SOW | 50 | 4 | 8% | 3%–19% |
| BANSHEES_CRY | 11 | 1 | 9% | 2%–38% |

Full table: `card-picks-necrobinder.csv`. Head-to-head ranking: `card-ranking-necrobinder.md`.

## Skips

| Act | Screens | Skipped | Skip rate |
|---|---|---|---|
| 1 | 391 | 49 | 13% |
| 2 | 210 | 65 | 31% |
| 3 | 117 | 52 | 44% |

| Deck size | Screens | Skipped | Skip rate |
|---|---|---|---|
| <15 | 164 | 19 | 12% |
| 15-19 | 231 | 38 | 16% |
| 20-24 | 176 | 50 | 28% |
| 25-29 | 102 | 40 | 39% |
| 30+ | 45 | 19 | 42% |

## Context effects

- **Upgraded offers:** picked 31% of the time (n=332), against 24% for base versions (n=1834).
- **Duplicates:** a card already in the deck is picked 31% of the time (n=229), against 25% for new cards (n=1937).

Cards whose pick rate changes most when a copy is already in the deck (5+ offers each way):

| Card | First copy: offered | First copy: pick rate | Already owned: offered | Already owned: pick rate |
|---|---|---|---|---|
| DRAIN_POWER | 45 | 44% | 23 | 9% |
| DEFY | 42 | 14% | 9 | 0% |
| FEAR | 55 | 24% | 10 | 10% |
| GRAVEBLAST | 46 | 22% | 10 | 10% |
| SOW | 45 | 9% | 5 | 0% |
| GRAVE_WARDEN | 58 | 19% | 8 | 12% |
| POKE | 49 | 16% | 7 | 14% |
| SNAP | 47 | 17% | 6 | 17% |
| FLATTEN | 50 | 28% | 20 | 40% |
| BLIGHT_STRIKE | 46 | 20% | 5 | 40% |
| WISP | 51 | 37% | 15 | 60% |
| DEATH_MARCH | 22 | 55% | 7 | 86% |

Card types (attack, skill, power) are not in the run files. Context rules by card type wait for the game data in Phase 2.

## Outcome association (weak evidence, `[PLAYER-DATA]`)

Win rate of finished runs whose **final deck** contains the card, against those that do not. Cards in 10+ finished runs. Per-band cells read wins/runs with the card vs wins/runs without it.

| Card | Runs with | Win rate with | Win rate without | A0-4 | A5-9 | A10 |
|---|---|---|---|---|---|---|
| NEUROSURGE | 11 | 55% | 12% | 3/5 vs 2/7 | 3/5 vs 2/23 | 0/1 vs 1/11 |
| DEMESNE | 13 | 46% | 13% | 3/5 vs 2/7 | 3/7 vs 2/21 | 0/1 vs 1/11 |
| MELANCHOLY | 14 | 43% | 13% | 3/3 vs 2/9 | 3/8 vs 2/20 | 0/3 vs 1/9 |
| WISP | 21 | 38% | 10% | 3/6 vs 2/6 | 4/13 vs 1/15 | 1/2 vs 0/10 |
| ENFEEBLING_TOUCH | 17 | 35% | 14% | 4/5 vs 1/7 | 1/8 vs 4/20 | 1/4 vs 0/8 |
| DEATH_MARCH | 14 | 36% | 16% | 4/5 vs 1/7 | 1/8 vs 4/20 | 0/1 vs 1/11 |
| FETCH | 19 | 32% | 15% | 3/6 vs 2/6 | 2/7 vs 3/21 | 1/6 vs 0/6 |
| GRAVEBLAST | 12 | 33% | 18% | 2/4 vs 3/8 | 1/5 vs 4/23 | 1/3 vs 0/9 |
| SEANCE | 12 | 33% | 18% | 2/2 vs 3/10 | 2/7 vs 3/21 | 0/3 vs 1/9 |
| FEAR | 13 | 31% | 18% | 2/6 vs 3/6 | 2/7 vs 3/21 | 0/0 vs 1/12 |
| PUTREFY | 18 | 28% | 18% | 4/7 vs 1/5 | 1/8 vs 4/20 | 0/3 vs 1/9 |
| FRIENDSHIP | 14 | 29% | 18% | 1/2 vs 4/10 | 3/10 vs 2/18 | 0/2 vs 1/10 |
| DIRGE | 14 | 29% | 18% | 3/5 vs 2/7 | 0/4 vs 5/24 | 1/5 vs 0/7 |
| FLATTEN | 19 | 26% | 18% | 0/3 vs 5/9 | 5/11 vs 0/17 | 0/5 vs 1/7 |
| DEFY | 11 | 27% | 20% | 1/5 vs 4/7 | 2/5 vs 3/23 | 0/1 vs 1/11 |

Survivorship warning: cards picked late only appear in runs that got far, so they look like winners. Treat every row as a hypothesis.

## Upgrade priorities (rest-site Smith)

| Card | Smith upgrades (all) | As 1st upgrade | As 2nd | As 3rd |
|---|---|---|---|---|
| DRAIN_POWER | 12 | 3 | 4 | 5 |
| WISP | 12 | 2 | 1 | 1 |
| DEMESNE | 11 | 0 | 0 | 1 |
| NEUROSURGE | 11 | 0 | 2 | 0 |
| BORROWED_TIME | 11 | 1 | 3 | 1 |
| SEANCE | 10 | 0 | 1 | 3 |
| FRIENDSHIP | 9 | 3 | 1 | 0 |
| MELANCHOLY | 9 | 1 | 1 | 2 |
| DEATH_MARCH | 8 | 0 | 2 | 2 |
| DIRGE | 8 | 1 | 1 | 1 |
| SCOURGE | 8 | 5 | 2 | 0 |
| ENFEEBLING_TOUCH | 8 | 0 | 1 | 4 |
| PUTREFY | 6 | 0 | 0 | 2 |
| NO_ESCAPE | 6 | 4 | 1 | 1 |
| FEAR | 5 | 3 | 1 | 1 |

Upgrades from other sources (events, relics, Ancients): 103.

## Removals

| Card | Removed |
|---|---|
| STRIKE_NECROBINDER | 39 |
| DEFEND_NECROBINDER | 24 |
| SPOILS_MAP | 8 |
| BONE_SHARDS | 3 |
| RATTLE | 3 |
| ENFEEBLING_TOUCH | 2 |
| CLUMSY | 2 |
| PUTREFY | 2 |
| SIC_EM | 2 |
| PRODUCTION | 2 |

Removal sources: monster 31, unknown 27, shop 25, ancient 12, treasure 8, rest_site 4, boss 1. Runs with at least one removal: 35/59; median floor of the first removal: 19.

## Shop card purchases

| Card | Seen in shop | Bought |
|---|---|---|
| FRIENDSHIP | 14 | 7 |
| AUTOMATION | 10 | 6 |
| COUNTDOWN | 19 | 6 |
| PRODUCTION | 9 | 5 |
| SCOURGE | 17 | 5 |
| BONE_SHARDS | 12 | 4 |
| BORROWED_TIME | 9 | 4 |
| DEFY | 32 | 4 |
| SHROUD | 16 | 4 |
| SECRET_TECHNIQUE | 12 | 4 |
| HIDDEN_GEM | 9 | 4 |
| CALCIFY | 11 | 4 |
