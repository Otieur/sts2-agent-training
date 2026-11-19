# Implied Card Priority: Ironclad (v0.107.1)

From 632 card reward screens in 57 runs. Each screen counts as head-to-head wins for the picked card over each card left behind, plus a win over **SKIP**. A skipped screen counts as SKIP beating every card. Strength comes from a Bradley-Terry model (log scale, 0 = average, regularised with one virtual win and loss per card).

This describes **what the Player picks**, not what wins.

> **Statistical cautions.** (1) Selection bias: what gets offered depends on earlier picks and relics.
> (2) Survivorship: late-floor numbers come only from runs that got there. (3) Ascension confounds
> everything; compare within bands. (4) Small samples: show n next to every rate; win correlations are
> hypotheses. (5) Multiple comparisons: with ~100 cards, some will look significant by chance.

**SKIP sits at -0.50.** Cards below SKIP are ones the Player would rather skip than take.

## Ranking (5 or more comparisons)

| # | Card | Strength | Comparisons | Picked | Offered | Pick rate | vs SKIP |
|---|---|---|---|---|---|---|---|
| 1 | PYRE | +3.12 | 35 | 11 | 13 | 85% | above |
| 2 | DOMINATE | +3.05 | 58 | 19 | 20 | 95% | above |
| 3 | THRASH | +2.99 | 19 | 6 | 7 | 86% | above |
| 4 | OFFERING | +2.69 | 12 | 4 | 4 | 100% | above |
| 5 | DARK_EMBRACE | +2.68 | 13 | 4 | 5 | 80% | above |
| 6 | FIEND_FIRE | +2.60 | 14 | 4 | 5 | 80% | above |
| 7 | CRUELTY | +2.51 | 13 | 4 | 5 | 80% | above |
| 8 | BRAND | +2.47 | 14 | 4 | 6 | 67% | above |
| 9 | CONFLAGRATION | +2.24 | 16 | 4 | 7 | 57% | above |
| 10 | FIGHT_ME | +2.06 | 36 | 11 | 14 | 79% | above |
| 11 | EVIL_EYE | +1.76 | 49 | 14 | 21 | 67% | above |
| 12 | ONE_TWO_PUNCH | +1.70 | 19 | 4 | 11 | 36% | above |
| 13 | SECOND_WIND | +1.56 | 46 | 13 | 19 | 68% | above |
| 14 | IMPERVIOUS | +1.52 | 15 | 4 | 7 | 57% | above |
| 15 | AGGRESSION | +1.49 | 17 | 4 | 9 | 44% | above |
| 16 | PACTS_END | +1.43 | 11 | 3 | 5 | 60% | above |
| 17 | STOKE | +1.18 | 13 | 3 | 7 | 43% | above |
| 18 | BURNING_PACT | +1.10 | 40 | 11 | 18 | 61% | above |
| 19 | MANGLE | +0.88 | 15 | 3 | 9 | 33% | above |
| 20 | STAMPEDE | +0.83 | 35 | 9 | 17 | 53% | above |
| 21 | VICIOUS | +0.80 | 49 | 12 | 25 | 48% | above |
| 22 | HELLRAISER | +0.78 | 10 | 2 | 6 | 33% | above |
| 23 | COLOSSUS | +0.75 | 39 | 10 | 19 | 53% | above |
| 24 | TRUE_GRIT | +0.66 | 96 | 23 | 49 | 47% | above |
| 25 | PRIMAL_FORCE | +0.59 | 6 | 1 | 4 | 25% | above |
| 26 | CRIMSON_MANTLE | +0.54 | 20 | 4 | 12 | 33% | above |
| 27 | FEED | +0.53 | 11 | 2 | 7 | 29% | above |
| 28 | TEAR_ASUNDER | +0.52 | 11 | 2 | 7 | 29% | above |
| 29 | DRUM_OF_BATTLE | +0.51 | 39 | 9 | 21 | 43% | above |
| 30 | TREMBLE | +0.47 | 102 | 24 | 54 | 44% | above |
| 31 | ASHEN_STRIKE | +0.46 | 20 | 5 | 10 | 50% | above |
| 32 | MOLTEN_FIST | +0.39 | 79 | 18 | 43 | 42% | above |
| 33 | ARMAMENTS | +0.36 | 116 | 25 | 65 | 38% | above |
| 34 | BLOODLETTING | +0.35 | 99 | 22 | 55 | 40% | above |
| 35 | FORGOTTEN_RITUAL | +0.22 | 32 | 7 | 18 | 39% | above |
| 36 | INFERNAL_BLADE | +0.21 | 19 | 4 | 11 | 36% | above |
| 37 | DEMON_FORM | +0.21 | 14 | 2 | 10 | 20% | above |
| 38 | CASCADE | +0.14 | 17 | 2 | 13 | 15% | above |
| 39 | BARRICADE | +0.12 | 21 | 3 | 15 | 20% | above |
| 40 | UNRELENTING | +0.11 | 26 | 5 | 16 | 31% | above |
| 41 | NOT_YET | +0.10 | 10 | 1 | 8 | 12% | above |
| 42 | BREAKTHROUGH | -0.02 | 104 | 21 | 62 | 34% | above |
| 43 | FEEL_NO_PAIN | -0.06 | 26 | 5 | 15 | 33% | above |
| 44 | BATTLE_TRANCE | -0.07 | 22 | 3 | 16 | 19% | above |
| 45 | INFERNO | -0.19 | 18 | 3 | 12 | 25% | above |
| 46 | FLAME_BARRIER | -0.19 | 20 | 4 | 12 | 33% | above |
| 47 | UPPERCUT | -0.20 | 24 | 4 | 15 | 27% | above |
| 48 | SHRUG_IT_OFF | -0.23 | 115 | 21 | 73 | 29% | above |
| 49 | TAUNT | -0.26 | 18 | 3 | 12 | 25% | above |
| 50 | DISMANTLE | -0.37 | 20 | 3 | 14 | 21% | above |
| 51 | **SKIP** | -0.50 | 892 | 129 | 632 | 20% | — |
| 52 | PILLAGE | -0.54 | 24 | 4 | 16 | 25% | below |
| 53 | BULLY | -0.58 | 19 | 3 | 13 | 23% | below |
| 54 | TWIN_STRIKE | -0.61 | 65 | 9 | 47 | 19% | below |
| 55 | STOMP | -0.61 | 22 | 3 | 16 | 19% | below |
| 56 | RAGE | -0.72 | 27 | 4 | 19 | 21% | below |
| 57 | HOWL_FROM_BEYOND | -0.79 | 25 | 3 | 19 | 16% | below |
| 58 | SWORD_BOOMERANG | -0.87 | 79 | 10 | 58 | 17% | below |
| 59 | RUPTURE | -0.97 | 16 | 2 | 12 | 17% | below |
| 60 | CINDER | -0.99 | 70 | 8 | 54 | 15% | below |
| 61 | POMMEL_STRIKE | -1.07 | 61 | 7 | 47 | 15% | below |
| 62 | THUNDERCLAP | -1.07 | 60 | 7 | 46 | 15% | below |
| 63 | HAVOC | -1.07 | 60 | 6 | 48 | 12% | below |
| 64 | RAMPAGE | -1.11 | 32 | 3 | 26 | 12% | below |
| 65 | INFLAME | -1.19 | 18 | 2 | 14 | 14% | below |
| 66 | IRON_WAVE | -1.26 | 82 | 8 | 66 | 12% | below |
| 67 | HEADBUTT | -1.34 | 72 | 7 | 57 | 12% | below |
| 68 | JUGGERNAUT | -1.35 | 6 | 0 | 6 | 0% | below |
| 69 | SETUP_STRIKE | -1.37 | 61 | 5 | 51 | 10% | below |
| 70 | UNMOVABLE | -1.50 | 9 | 0 | 9 | 0% | below |
| 71 | BODY_SLAM | -1.63 | 53 | 4 | 45 | 9% | below |
| 72 | SPITE | -1.65 | 30 | 2 | 26 | 8% | below |
| 73 | BLUDGEON | -1.69 | 23 | 1 | 21 | 5% | below |
| 74 | STONE_ARMOR | -1.94 | 24 | 1 | 22 | 5% | below |
| 75 | HEMOKINESIS | -2.17 | 27 | 1 | 25 | 4% | below |
| 76 | ANGER | -2.23 | 57 | 2 | 53 | 4% | below |
| 77 | PERFECTED_STRIKE | -2.32 | 56 | 2 | 52 | 4% | below |
| 78 | WHIRLWIND | -2.54 | 13 | 0 | 13 | 0% | below |
| 79 | JUGGLING | -2.90 | 15 | 0 | 15 | 0% | below |
| 80 | BLOOD_WALL | -2.98 | 57 | 1 | 55 | 2% | below |
| 81 | EXPECT_A_FIGHT | -3.15 | 14 | 0 | 14 | 0% | below |

## Insufficient data (fewer than 5 comparisons)

DEATH_MARCH (3), AFTERIMAGE (3), BEAT_DOWN (3), OVERCLOCK (3), ROLLING_BOULDER (3), BEAM_CELL (3), CHARGE (3), ENFEEBLING_TOUCH (3), DAGGER_SPRAY (4), PREDATOR (1), BANSHEES_CRY (1), FLASH_OF_STEEL (1), GOLD_AXE (1), JACKPOT (1), NOXIOUS_FUMES (1), PAGESTORM (1), PROWESS (1), REBOOT (1), LIGHTNING_ROD (1), SHINING_STRIKE (1), RESTLESSNESS (1), TESLA_COIL (1), CHARGE_BATTERY (2), FOCUSED_STRIKE (2), ERADICATE (1), FEAR (1), GLITTERSTREAM (1), HEIRLOOM_HAMMER (1), RAINBOW (1), REFINE_BLADE (1), TERRAFORMING (1)
