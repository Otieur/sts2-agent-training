# Implied Card Priority: Regent (v0.107.1)

From 599 card reward screens in 53 runs. Each screen counts as head-to-head wins for the picked card over each card left behind, plus a win over **SKIP**. A skipped screen counts as SKIP beating every card. Strength comes from a Bradley-Terry model (log scale, 0 = average, regularised with one virtual win and loss per card).

This describes **what the Player picks**, not what wins.

> **Statistical cautions.** (1) Selection bias: what gets offered depends on earlier picks and relics.
> (2) Survivorship: late-floor numbers come only from runs that got there. (3) Ascension confounds
> everything; compare within bands. (4) Small samples: show n next to every rate; win correlations are
> hypotheses. (5) Multiple comparisons: with ~100 cards, some will look significant by chance.

**SKIP sits at -0.70.** Cards below SKIP are ones the Player would rather skip than take.

## Ranking (5 or more comparisons)

| # | Card | Strength | Comparisons | Picked | Offered | Pick rate | vs SKIP |
|---|---|---|---|---|---|---|---|
| 1 | DYING_STAR | +3.92 | 27 | 9 | 9 | 100% | above |
| 2 | SEVEN_STARS | +2.87 | 23 | 7 | 9 | 78% | above |
| 3 | FOREGONE_CONCLUSION | +2.68 | 23 | 7 | 9 | 78% | above |
| 4 | VOID_FORM | +2.66 | 29 | 9 | 11 | 82% | above |
| 5 | SWORD_SAGE | +2.65 | 23 | 7 | 9 | 78% | above |
| 6 | SEEKING_EDGE | +2.22 | 26 | 7 | 12 | 58% | above |
| 7 | PARRY | +2.08 | 28 | 9 | 10 | 90% | above |
| 8 | BEAT_INTO_SHAPE | +2.00 | 7 | 2 | 3 | 67% | above |
| 9 | SUMMON_FORTH | +1.97 | 37 | 11 | 15 | 73% | above |
| 10 | ALIGNMENT | +1.97 | 47 | 14 | 19 | 74% | above |
| 11 | MAKE_IT_SO | +1.93 | 19 | 5 | 9 | 56% | above |
| 12 | BIG_BANG | +1.86 | 18 | 5 | 8 | 62% | above |
| 13 | CHARGE | +1.83 | 40 | 12 | 16 | 75% | above |
| 14 | BULWARK | +1.71 | 49 | 15 | 19 | 79% | above |
| 15 | HEIRLOOM_HAMMER | +1.65 | 12 | 3 | 6 | 50% | above |
| 16 | THE_SMITH | +1.65 | 14 | 4 | 6 | 67% | above |
| 17 | DECISIONS_DECISIONS | +1.62 | 24 | 6 | 12 | 50% | above |
| 18 | ORBIT | +1.60 | 46 | 13 | 20 | 65% | above |
| 19 | NEUTRON_AEGIS | +1.53 | 16 | 4 | 8 | 50% | above |
| 20 | FURNACE | +0.86 | 32 | 8 | 16 | 50% | above |
| 21 | ROYAL_GAMBLE | +0.71 | 41 | 11 | 19 | 58% | above |
| 22 | SPOILS_OF_BATTLE | +0.67 | 58 | 14 | 30 | 47% | above |
| 23 | GUARDS | +0.63 | 12 | 2 | 8 | 25% | above |
| 24 | COSMIC_INDIFFERENCE | +0.61 | 122 | 30 | 62 | 48% | above |
| 25 | CHILD_OF_THE_STARS | +0.53 | 36 | 9 | 18 | 50% | above |
| 26 | GAMMA_BLAST | +0.53 | 21 | 5 | 11 | 45% | above |
| 27 | ARSENAL | +0.40 | 11 | 2 | 7 | 29% | above |
| 28 | HEGEMONY | +0.36 | 34 | 7 | 20 | 35% | above |
| 29 | BUNDLE_OF_JOY | +0.26 | 13 | 2 | 9 | 22% | above |
| 30 | SHINING_STRIKE | +0.25 | 31 | 7 | 17 | 41% | above |
| 31 | QUASAR | +0.22 | 28 | 6 | 16 | 38% | above |
| 32 | I_AM_INVINCIBLE | +0.20 | 12 | 2 | 8 | 25% | above |
| 33 | MONARCHS_GAZE | +0.20 | 12 | 2 | 8 | 25% | above |
| 34 | HIDDEN_CACHE | +0.13 | 93 | 20 | 53 | 38% | above |
| 35 | GENESIS | +0.09 | 9 | 1 | 7 | 14% | above |
| 36 | GLIMMER | +0.08 | 35 | 7 | 21 | 33% | above |
| 37 | PALE_BLUE_DOT | +0.02 | 34 | 7 | 19 | 37% | above |
| 38 | CONQUEROR | -0.03 | 24 | 5 | 14 | 36% | above |
| 39 | DEVASTATE | -0.14 | 30 | 5 | 20 | 25% | above |
| 40 | GLOW | -0.19 | 100 | 18 | 64 | 28% | above |
| 41 | PARTICLE_WALL | -0.25 | 38 | 7 | 24 | 29% | above |
| 42 | COMET | -0.36 | 7 | 1 | 5 | 20% | above |
| 43 | BOMBARDMENT | -0.41 | 12 | 1 | 10 | 10% | above |
| 44 | CLOAK_OF_STARS | -0.41 | 76 | 13 | 50 | 26% | above |
| 45 | KNOW_THY_PLACE | -0.44 | 86 | 15 | 56 | 27% | above |
| 46 | GATHER_LIGHT | -0.45 | 70 | 12 | 46 | 26% | above |
| 47 | CONVERGENCE | -0.46 | 24 | 4 | 16 | 25% | above |
| 48 | PROPHESIZE | -0.52 | 26 | 4 | 18 | 22% | above |
| 49 | TYRANNY | -0.55 | 13 | 1 | 11 | 9% | above |
| 50 | PHOTON_CUT | -0.56 | 57 | 9 | 39 | 23% | above |
| 51 | ASTRAL_PULSE | -0.60 | 47 | 7 | 33 | 21% | above |
| 52 | HEAVENLY_DRILL | -0.60 | 6 | 0 | 6 | 0% | above |
| 53 | REFINE_BLADE | -0.66 | 80 | 12 | 56 | 21% | above |
| 54 | **SKIP** | -0.70 | 823 | 112 | 599 | 19% | — |
| 55 | KINGLY_PUNCH | -0.80 | 14 | 2 | 10 | 20% | below |
| 56 | LUNAR_BLAST | -0.83 | 18 | 2 | 14 | 14% | below |
| 57 | BLACK_HOLE | -0.87 | 29 | 4 | 21 | 19% | below |
| 58 | ROYALTIES | -0.92 | 8 | 0 | 8 | 0% | below |
| 59 | REFLECT | -0.98 | 22 | 3 | 16 | 19% | below |
| 60 | MANIFEST_AUTHORITY | -1.01 | 18 | 2 | 14 | 14% | below |
| 61 | CRUSH_UNDER | -1.01 | 74 | 9 | 56 | 16% | below |
| 62 | KNOCKOUT_BLOW | -1.02 | 23 | 2 | 19 | 11% | below |
| 63 | RADIATE | -1.02 | 26 | 3 | 20 | 15% | below |
| 64 | BEGONE | -1.05 | 59 | 7 | 45 | 16% | below |
| 65 | WROUGHT_IN_WAR | -1.11 | 65 | 8 | 49 | 16% | below |
| 66 | RESONANCE | -1.12 | 31 | 4 | 23 | 17% | below |
| 67 | CRESCENT_SPEAR | -1.13 | 63 | 7 | 49 | 14% | below |
| 68 | STARDUST | -1.16 | 20 | 2 | 16 | 12% | below |
| 69 | GLITTERSTREAM | -1.43 | 55 | 5 | 45 | 11% | below |
| 70 | SOLAR_STRIKE | -1.44 | 65 | 6 | 53 | 11% | below |
| 71 | KINGLY_KICK | -1.47 | 29 | 3 | 23 | 13% | below |
| 72 | SUPERMASSIVE | -1.48 | 9 | 1 | 7 | 14% | below |
| 73 | GUIDING_STAR | -1.48 | 62 | 5 | 52 | 10% | below |
| 74 | PILLAR_OF_CREATION | -1.97 | 24 | 1 | 22 | 5% | below |
| 75 | TERRAFORMING | -2.01 | 17 | 1 | 15 | 7% | below |
| 76 | MONOLOGUE | -2.07 | 25 | 1 | 23 | 4% | below |
| 77 | CELESTIAL_MIGHT | -2.57 | 65 | 2 | 61 | 3% | below |
| 78 | PATTER | -2.75 | 38 | 1 | 36 | 3% | below |
| 79 | COLLISION_COURSE | -3.05 | 54 | 1 | 52 | 2% | below |
| 80 | SPECTRUM_SHIFT | -3.33 | 18 | 0 | 18 | 0% | below |

## Insufficient data (fewer than 5 comparisons)

CRASH_LANDING (4)
