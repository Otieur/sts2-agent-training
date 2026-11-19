# Implied Card Priority: Silent (v0.107.1)

From 604 card reward screens in 51 runs. Each screen counts as head-to-head wins for the picked card over each card left behind, plus a win over **SKIP**. A skipped screen counts as SKIP beating every card. Strength comes from a Bradley-Terry model (log scale, 0 = average, regularised with one virtual win and loss per card).

This describes **what the Player picks**, not what wins.

> **Statistical cautions.** (1) Selection bias: what gets offered depends on earlier picks and relics.
> (2) Survivorship: late-floor numbers come only from runs that got there. (3) Ascension confounds
> everything; compare within bands. (4) Small samples: show n next to every rate; win correlations are
> hypotheses. (5) Multiple comparisons: with ~100 cards, some will look significant by chance.

**SKIP sits at -0.74.** Cards below SKIP are ones the Player would rather skip than take.

## Ranking (5 or more comparisons)

| # | Card | Strength | Comparisons | Picked | Offered | Pick rate | vs SKIP |
|---|---|---|---|---|---|---|---|
| 1 | ABRASIVE | +3.27 | 28 | 9 | 10 | 90% | above |
| 2 | SHADOW_STEP | +3.25 | 12 | 4 | 4 | 100% | above |
| 3 | TOOLS_OF_THE_TRADE | +2.69 | 26 | 8 | 10 | 80% | above |
| 4 | TACTICIAN | +2.68 | 49 | 16 | 17 | 94% | above |
| 5 | TRACKING | +2.28 | 21 | 6 | 9 | 67% | above |
| 6 | REFLEX | +2.27 | 19 | 6 | 7 | 86% | above |
| 7 | EXPOSE | +2.20 | 46 | 14 | 18 | 78% | above |
| 8 | ACROBATICS | +2.13 | 71 | 21 | 29 | 72% | above |
| 9 | STORM_OF_STEEL | +2.01 | 18 | 5 | 8 | 62% | above |
| 10 | ESCAPE_PLAN | +2.01 | 59 | 18 | 23 | 78% | above |
| 11 | MURDER | +1.95 | 18 | 5 | 8 | 62% | above |
| 12 | BURST | +1.64 | 8 | 2 | 4 | 50% | above |
| 13 | SERPENT_FORM | +1.55 | 19 | 5 | 9 | 56% | above |
| 14 | AFTERIMAGE | +1.55 | 19 | 5 | 9 | 56% | above |
| 15 | SHADOWMELD | +1.41 | 22 | 5 | 12 | 42% | above |
| 16 | ADRENALINE | +1.29 | 17 | 4 | 9 | 44% | above |
| 17 | HAZE | +1.29 | 36 | 10 | 16 | 62% | above |
| 18 | BLADE_OF_INK | +1.20 | 18 | 4 | 10 | 40% | above |
| 19 | RICOCHET | +1.07 | 95 | 24 | 47 | 51% | above |
| 20 | UNTOUCHABLE | +1.04 | 78 | 19 | 40 | 48% | above |
| 21 | MASTER_PLANNER | +1.00 | 14 | 3 | 8 | 38% | above |
| 22 | ACCELERANT | +0.97 | 19 | 4 | 11 | 36% | above |
| 23 | CALCULATED_GAMBLE | +0.96 | 56 | 14 | 28 | 50% | above |
| 24 | MEMENTO_MORI | +0.91 | 34 | 9 | 16 | 56% | above |
| 25 | HAND_TRICK | +0.90 | 18 | 4 | 10 | 40% | above |
| 26 | ECHOING_SLASH | +0.87 | 15 | 3 | 9 | 33% | above |
| 27 | HIDDEN_DAGGERS | +0.84 | 17 | 4 | 9 | 44% | above |
| 28 | DAGGER_THROW | +0.84 | 97 | 24 | 49 | 49% | above |
| 29 | ASSASSINATE | +0.77 | 16 | 3 | 10 | 30% | above |
| 30 | PREPARED | +0.77 | 90 | 23 | 44 | 52% | above |
| 31 | PINPOINT | +0.75 | 27 | 7 | 13 | 54% | above |
| 32 | POUNCE | +0.71 | 33 | 8 | 16 | 50% | above |
| 33 | MALAISE | +0.57 | 14 | 3 | 8 | 38% | above |
| 34 | LEG_SWEEP | +0.54 | 49 | 11 | 26 | 42% | above |
| 35 | CORROSIVE_WAVE | +0.52 | 17 | 4 | 9 | 44% | above |
| 36 | PIERCING_WAIL | +0.49 | 104 | 24 | 56 | 43% | above |
| 37 | THE_HUNT | +0.39 | 17 | 3 | 11 | 27% | above |
| 38 | ENVENOM | +0.32 | 12 | 2 | 8 | 25% | above |
| 39 | PRECISE_CUT | +0.29 | 28 | 6 | 16 | 38% | above |
| 40 | FOOTWORK | +0.28 | 34 | 7 | 20 | 35% | above |
| 41 | FLICK_FLACK | +0.24 | 88 | 17 | 54 | 31% | above |
| 42 | EXPERTISE | +0.08 | 31 | 6 | 19 | 32% | above |
| 43 | NIGHTMARE | +0.07 | 14 | 2 | 10 | 20% | above |
| 44 | BLADE_DANCE | -0.07 | 74 | 14 | 46 | 30% | above |
| 45 | BUBBLE_BUBBLE | -0.09 | 24 | 4 | 16 | 25% | above |
| 46 | BACKSTAB | -0.21 | 31 | 6 | 19 | 32% | above |
| 47 | OUTBREAK | -0.26 | 22 | 4 | 14 | 29% | above |
| 48 | DAGGER_SPRAY | -0.27 | 60 | 10 | 40 | 25% | above |
| 49 | GRAND_FINALE | -0.39 | 11 | 1 | 9 | 11% | above |
| 50 | KNIFE_TRAP | -0.41 | 17 | 2 | 13 | 15% | above |
| 51 | FINISHER | -0.63 | 22 | 3 | 16 | 19% | above |
| 52 | INFINITE_BLADES | -0.68 | 26 | 3 | 20 | 15% | above |
| 53 | ACCURACY | -0.70 | 26 | 3 | 20 | 15% | above |
| 54 | **SKIP** | -0.74 | 803 | 99 | 604 | 16% | — |
| 55 | BACKFLIP | -0.86 | 62 | 8 | 46 | 17% | below |
| 56 | DASH | -0.88 | 37 | 5 | 27 | 19% | below |
| 57 | NOXIOUS_FUMES | -0.89 | 12 | 1 | 10 | 10% | below |
| 58 | SPEEDSTER | -0.91 | 20 | 2 | 16 | 12% | below |
| 59 | PHANTOM_BLADES | -0.99 | 21 | 2 | 17 | 12% | below |
| 60 | LEADING_STRIKE | -1.08 | 72 | 9 | 54 | 17% | below |
| 61 | WELL_LAID_PLANS | -1.23 | 29 | 3 | 23 | 13% | below |
| 62 | SUCKER_PUNCH | -1.31 | 74 | 8 | 58 | 14% | below |
| 63 | PREDATOR | -1.35 | 54 | 5 | 44 | 11% | below |
| 64 | FLECHETTES | -1.40 | 19 | 2 | 15 | 13% | below |
| 65 | UP_MY_SLEEVE | -1.41 | 23 | 2 | 19 | 11% | below |
| 66 | SCARE | -1.42 | 23 | 2 | 19 | 11% | below |
| 67 | FAN_OF_KNIVES | -1.57 | 8 | 0 | 8 | 0% | below |
| 68 | ANTICIPATE | -1.58 | 52 | 3 | 46 | 7% | below |
| 69 | CLOAK_AND_DAGGER | -1.59 | 63 | 5 | 53 | 9% | below |
| 70 | POISONED_STAB | -1.87 | 73 | 4 | 65 | 6% | below |
| 71 | DEADLY_POISON | -1.98 | 60 | 4 | 52 | 8% | below |
| 72 | SLICE | -2.00 | 54 | 3 | 48 | 6% | below |
| 73 | BULLET_TIME | -2.11 | 11 | 0 | 11 | 0% | below |
| 74 | BLUR | -2.14 | 18 | 1 | 16 | 6% | below |
| 75 | MIRAGE | -2.28 | 7 | 0 | 7 | 0% | below |
| 76 | DODGE_AND_ROLL | -2.41 | 42 | 1 | 39 | 3% | below |
| 77 | BOUNCING_FLASK | -2.58 | 12 | 0 | 12 | 0% | below |
| 78 | DEFLECT | -2.99 | 56 | 1 | 54 | 2% | below |
| 79 | STRANGLE | -3.00 | 15 | 0 | 15 | 0% | below |
| 80 | SKEWER | -3.38 | 19 | 0 | 19 | 0% | below |
| 81 | SNAKEBITE | -4.11 | 43 | 0 | 43 | 0% | below |

## Insufficient data (fewer than 5 comparisons)

PROWESS (3), DRAMATIC_ENTRANCE (3), ULTIMATE_DEFEND (3), DISCOVERY (1), REND (1), SPLASH (1), EQUILIBRIUM (1), ULTIMATE_STRIKE (1)
