# Card Analysis: Regent (v0.107.1)

Runs: 53 solo (45 finished, 10 wins). Card reward screens: 599. Cards offered: 1798.

> **Statistical cautions.** (1) Selection bias: what gets offered depends on earlier picks and relics.
> (2) Survivorship: late-floor numbers come only from runs that got there. (3) Ascension confounds
> everything; compare within bands. (4) Small samples: show n next to every rate; win correlations are
> hypotheses. (5) Multiple comparisons: with ~100 cards, some will look significant by chance.

## Most-picked cards (offered 8+ times)

| Card | Offered | Picked | Pick rate | 95% CI |
|---|---|---|---|---|
| DYING_STAR | 9 | 9 | 100% | 70%–100% |
| PARRY | 10 | 9 | 90% | 60%–98% |
| VOID_FORM | 11 | 9 | 82% | 52%–95% |
| BULWARK | 19 | 15 | 79% | 57%–92% |
| FOREGONE_CONCLUSION | 9 | 7 | 78% | 45%–94% |
| SWORD_SAGE | 9 | 7 | 78% | 45%–94% |
| SEVEN_STARS | 9 | 7 | 78% | 45%–94% |
| CHARGE | 16 | 12 | 75% | 50%–90% |
| ALIGNMENT | 19 | 14 | 74% | 51%–88% |
| SUMMON_FORTH | 15 | 11 | 73% | 48%–89% |
| ORBIT | 20 | 13 | 65% | 43%–82% |
| BIG_BANG | 8 | 5 | 62% | 31%–86% |
| SEEKING_EDGE | 12 | 7 | 58% | 32%–81% |
| ROYAL_GAMBLE | 19 | 11 | 58% | 36%–77% |
| MAKE_IT_SO | 9 | 5 | 56% | 27%–81% |
| CHILD_OF_THE_STARS | 18 | 9 | 50% | 29%–71% |
| FURNACE | 16 | 8 | 50% | 28%–72% |
| DECISIONS_DECISIONS | 12 | 6 | 50% | 25%–75% |
| NEUTRON_AEGIS | 8 | 4 | 50% | 22%–78% |
| COSMIC_INDIFFERENCE | 62 | 30 | 48% | 36%–61% |

## Least-picked cards (offered 8+ times)

| Card | Offered | Picked | Pick rate | 95% CI |
|---|---|---|---|---|
| SPECTRUM_SHIFT | 18 | 0 | 0% | 0%–18% |
| ROYALTIES | 8 | 0 | 0% | 0%–32% |
| COLLISION_COURSE | 52 | 1 | 2% | 0%–10% |
| PATTER | 36 | 1 | 3% | 0%–14% |
| CELESTIAL_MIGHT | 61 | 2 | 3% | 1%–11% |
| MONOLOGUE | 23 | 1 | 4% | 1%–21% |
| PILLAR_OF_CREATION | 22 | 1 | 4% | 1%–22% |
| TERRAFORMING | 15 | 1 | 7% | 1%–30% |
| TYRANNY | 11 | 1 | 9% | 2%–38% |
| GUIDING_STAR | 52 | 5 | 10% | 4%–21% |
| BOMBARDMENT | 10 | 1 | 10% | 2%–40% |
| KNOCKOUT_BLOW | 19 | 2 | 10% | 3%–31% |
| GLITTERSTREAM | 45 | 5 | 11% | 5%–24% |
| SOLAR_STRIKE | 53 | 6 | 11% | 5%–23% |
| STARDUST | 16 | 2 | 12% | 4%–36% |

Full table: `card-picks-regent.csv`. Head-to-head ranking: `card-ranking-regent.md`.

## Skips

| Act | Screens | Skipped | Skip rate |
|---|---|---|---|
| 1 | 343 | 27 | 8% |
| 2 | 176 | 48 | 27% |
| 3 | 80 | 37 | 46% |

| Deck size | Screens | Skipped | Skip rate |
|---|---|---|---|
| <15 | 155 | 7 | 5% |
| 15-19 | 187 | 27 | 14% |
| 20-24 | 128 | 32 | 25% |
| 25-29 | 88 | 24 | 27% |
| 30+ | 41 | 22 | 54% |

## Context effects

- **Upgraded offers:** picked 33% of the time (n=265), against 26% for base versions (n=1533).
- **Duplicates:** a card already in the deck is picked 20% of the time (n=203), against 28% for new cards (n=1595).

Cards whose pick rate changes most when a copy is already in the deck (5+ offers each way):

| Card | First copy: offered | First copy: pick rate | Already owned: offered | Already owned: pick rate |
|---|---|---|---|---|
| ALIGNMENT | 14 | 86% | 5 | 40% |
| GATHER_LIGHT | 30 | 37% | 16 | 6% |
| REFINE_BLADE | 41 | 29% | 15 | 0% |
| PHOTON_CUT | 31 | 29% | 8 | 0% |
| ASTRAL_PULSE | 28 | 25% | 5 | 0% |
| HIDDEN_CACHE | 35 | 46% | 18 | 22% |
| WROUGHT_IN_WAR | 41 | 20% | 8 | 0% |
| GLITTERSTREAM | 37 | 14% | 8 | 0% |
| COSMIC_INDIFFERENCE | 40 | 52% | 22 | 41% |
| GUIDING_STAR | 44 | 11% | 8 | 0% |
| CLOAK_OF_STARS | 40 | 28% | 10 | 20% |
| KNOW_THY_PLACE | 48 | 27% | 8 | 25% |

Card types (attack, skill, power) are not in the run files. Context rules by card type wait for the game data in Phase 2.

## Outcome association (weak evidence, `[PLAYER-DATA]`)

Win rate of finished runs whose **final deck** contains the card, against those that do not. Cards in 10+ finished runs. Per-band cells read wins/runs with the card vs wins/runs without it.

| Card | Runs with | Win rate with | Win rate without | A0-4 | A5-9 | A10 |
|---|---|---|---|---|---|---|
| SUMMON_FORTH | 11 | 64% | 9% | 3/5 vs 2/12 | 4/4 vs 1/14 | 0/2 vs 0/8 |
| HIDDEN_CACHE | 21 | 38% | 8% | 3/5 vs 2/12 | 5/10 vs 0/8 | 0/6 vs 0/4 |
| CLOAK_OF_STARS | 13 | 38% | 16% | 1/4 vs 4/13 | 4/7 vs 1/11 | 0/2 vs 0/8 |
| REFINE_BLADE | 13 | 38% | 16% | 2/3 vs 3/14 | 3/6 vs 2/12 | 0/4 vs 0/6 |
| ALIGNMENT | 14 | 36% | 16% | 3/6 vs 2/11 | 2/7 vs 3/11 | 0/1 vs 0/9 |
| PALE_BLUE_DOT | 11 | 36% | 18% | 3/6 vs 2/11 | 1/4 vs 4/14 | 0/1 vs 0/9 |
| COSMIC_INDIFFERENCE | 23 | 30% | 14% | 2/6 vs 3/11 | 5/11 vs 0/7 | 0/6 vs 0/4 |
| ROYAL_GAMBLE | 12 | 33% | 18% | 3/6 vs 2/11 | 1/5 vs 4/13 | 0/1 vs 0/9 |
| PARRY | 12 | 33% | 18% | 3/4 vs 2/13 | 1/3 vs 4/15 | 0/5 vs 0/5 |
| BULWARK | 12 | 33% | 18% | 1/3 vs 4/14 | 3/7 vs 2/11 | 0/2 vs 0/8 |
| GATHER_LIGHT | 16 | 31% | 17% | 3/9 vs 2/8 | 2/5 vs 3/13 | 0/2 vs 0/8 |
| KNOW_THY_PLACE | 17 | 29% | 18% | 5/14 vs 0/3 | 0/3 vs 5/15 | 0/0 vs 0/10 |
| FURNACE | 10 | 30% | 20% | 0/1 vs 5/16 | 3/6 vs 2/12 | 0/3 vs 0/7 |
| CHARGE | 12 | 25% | 21% | 1/2 vs 4/15 | 2/7 vs 3/11 | 0/3 vs 0/7 |
| PHOTON_CUT | 13 | 23% | 22% | 0/0 vs 5/17 | 3/8 vs 2/10 | 0/5 vs 0/5 |

Survivorship warning: cards picked late only appear in runs that got far, so they look like winners. Treat every row as a hypothesis.

## Upgrade priorities (rest-site Smith)

| Card | Smith upgrades (all) | As 1st upgrade | As 2nd | As 3rd |
|---|---|---|---|---|
| ORBIT | 14 | 3 | 2 | 2 |
| BULWARK | 11 | 0 | 3 | 2 |
| VENERATE | 8 | 3 | 1 | 4 |
| GLOW | 8 | 2 | 2 | 2 |
| PHOTON_CUT | 7 | 3 | 2 | 0 |
| ALIGNMENT | 6 | 1 | 0 | 1 |
| SWORD_SAGE | 6 | 2 | 0 | 1 |
| ROYAL_GAMBLE | 6 | 1 | 2 | 0 |
| PALE_BLUE_DOT | 5 | 0 | 1 | 1 |
| KNOW_THY_PLACE | 5 | 0 | 1 | 2 |
| BIG_BANG | 5 | 1 | 0 | 2 |
| FURNACE | 5 | 1 | 2 | 0 |
| APPARITION | 5 | 0 | 0 | 0 |
| SEVEN_STARS | 5 | 0 | 1 | 2 |
| HIDDEN_CACHE | 5 | 0 | 2 | 1 |

Upgrades from other sources (events, relics, Ancients): 83.

## Removals

| Card | Removed |
|---|---|
| STRIKE_REGENT | 25 |
| DEFEND_REGENT | 13 |
| SPOILS_MAP | 5 |
| CLUMSY | 5 |
| PARTICLE_WALL | 3 |
| DECAY | 2 |
| GUILTY | 2 |
| CONQUEROR | 2 |
| SUPERMASSIVE | 2 |
| DEBT | 2 |

Removal sources: shop 30, monster 17, unknown 13, rest_site 10, ancient 7, treasure 5. Runs with at least one removal: 30/53; median floor of the first removal: 19.

## Shop card purchases

| Card | Seen in shop | Bought |
|---|---|---|
| ORBIT | 12 | 6 |
| HIDDEN_CACHE | 19 | 5 |
| HIDDEN_GEM | 7 | 5 |
| PARRY | 9 | 4 |
| WROUGHT_IN_WAR | 20 | 4 |
| PRODUCTION | 5 | 4 |
| GAMMA_BLAST | 5 | 3 |
| DARK_SHACKLES | 7 | 3 |
| CONQUEROR | 8 | 3 |
| SPOILS_OF_BATTLE | 9 | 3 |
| THINKING_AHEAD | 5 | 3 |
| ALIGNMENT | 5 | 3 |
