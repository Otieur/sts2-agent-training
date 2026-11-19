# Implied Card Priority: Necrobinder (v0.107.1)

From 718 card reward screens in 59 runs. Each screen counts as head-to-head wins for the picked card over each card left behind, plus a win over **SKIP**. A skipped screen counts as SKIP beating every card. Strength comes from a Bradley-Terry model (log scale, 0 = average, regularised with one virtual win and loss per card).

This describes **what the Player picks**, not what wins.

> **Statistical cautions.** (1) Selection bias: what gets offered depends on earlier picks and relics.
> (2) Survivorship: late-floor numbers come only from runs that got there. (3) Ascension confounds
> everything; compare within bands. (4) Small samples: show n next to every rate; win correlations are
> hypotheses. (5) Multiple comparisons: with ~100 cards, some will look significant by chance.

**SKIP sits at -0.12.** Cards below SKIP are ones the Player would rather skip than take.

## Ranking (5 or more comparisons)

| # | Card | Strength | Comparisons | Picked | Offered | Pick rate | vs SKIP |
|---|---|---|---|---|---|---|---|
| 1 | DEMESNE | +3.83 | 47 | 15 | 16 | 94% | above |
| 2 | FETCH | +2.87 | 59 | 19 | 21 | 90% | above |
| 3 | NEUROSURGE | +2.77 | 38 | 11 | 13 | 85% | above |
| 4 | BORROWED_TIME | +2.59 | 38 | 12 | 14 | 86% | above |
| 5 | SEANCE | +2.32 | 42 | 12 | 18 | 67% | above |
| 6 | ENFEEBLING_TOUCH | +1.97 | 56 | 17 | 22 | 77% | above |
| 7 | SENTRY_MODE | +1.87 | 24 | 7 | 10 | 70% | above |
| 8 | MELANCHOLY | +1.86 | 42 | 12 | 18 | 67% | above |
| 9 | FRIENDSHIP | +1.84 | 34 | 10 | 14 | 71% | above |
| 10 | HANG | +1.79 | 21 | 6 | 9 | 67% | above |
| 11 | DEATHS_DOOR | +1.72 | 42 | 12 | 18 | 67% | above |
| 12 | END_OF_DAYS | +1.67 | 20 | 5 | 10 | 50% | above |
| 13 | DEATH_MARCH | +1.51 | 66 | 18 | 29 | 62% | above |
| 14 | SQUEEZE | +1.46 | 27 | 6 | 15 | 40% | above |
| 15 | SOUL_STORM | +1.44 | 20 | 4 | 12 | 33% | above |
| 16 | PUTREFY | +1.32 | 66 | 18 | 30 | 60% | above |
| 17 | NO_ESCAPE | +1.30 | 30 | 8 | 14 | 57% | above |
| 18 | RATTLE | +1.22 | 31 | 8 | 15 | 53% | above |
| 19 | DIRGE | +1.17 | 43 | 11 | 21 | 52% | above |
| 20 | OBLIVION | +1.01 | 17 | 4 | 9 | 44% | above |
| 21 | PARSE | +0.95 | 49 | 11 | 27 | 41% | above |
| 22 | TRANSFIGURE | +0.78 | 15 | 3 | 9 | 33% | above |
| 23 | WISP | +0.72 | 122 | 28 | 66 | 42% | above |
| 24 | DEVOUR_LIFE | +0.68 | 15 | 3 | 9 | 33% | above |
| 25 | SACRIFICE | +0.67 | 14 | 2 | 10 | 20% | above |
| 26 | SIC_EM | +0.60 | 33 | 7 | 19 | 37% | above |
| 27 | CAPTURE_SPIRIT | +0.49 | 38 | 8 | 22 | 36% | above |
| 28 | DEATHBRINGER | +0.39 | 25 | 5 | 15 | 33% | above |
| 29 | REAPER_FORM | +0.36 | 15 | 3 | 9 | 33% | above |
| 30 | DRAIN_POWER | +0.30 | 112 | 22 | 68 | 32% | above |
| 31 | CALL_OF_THE_VOID | +0.29 | 21 | 3 | 15 | 20% | above |
| 32 | REANIMATE | +0.26 | 15 | 2 | 11 | 18% | above |
| 33 | FLATTEN | +0.25 | 114 | 22 | 70 | 31% | above |
| 34 | TIMES_UP | +0.25 | 11 | 2 | 7 | 29% | above |
| 35 | CLEANSE | +0.20 | 45 | 9 | 27 | 33% | above |
| 36 | SHARED_FATE | +0.16 | 11 | 2 | 7 | 29% | above |
| 37 | SPIRIT_OF_ASH | +0.08 | 15 | 2 | 11 | 18% | above |
| 38 | SHROUD | +0.07 | 34 | 6 | 22 | 27% | above |
| 39 | SEVERANCE | +0.05 | 35 | 6 | 23 | 26% | above |
| 40 | SLEIGHT_OF_FLESH | +0.02 | 30 | 6 | 18 | 33% | above |
| 41 | DREDGE | -0.02 | 18 | 3 | 12 | 25% | above |
| 42 | COUNTDOWN | -0.05 | 28 | 5 | 18 | 28% | above |
| 43 | SCOURGE | -0.09 | 78 | 13 | 52 | 25% | above |
| 44 | HAUNT | -0.12 | 38 | 6 | 25 | 24% | above |
| 45 | **SKIP** | -0.12 | 1055 | 166 | 718 | 23% | — |
| 46 | RIGHT_HAND_HAND | -0.14 | 26 | 4 | 18 | 22% | below |
| 47 | BONE_SHARDS | -0.15 | 36 | 5 | 25 | 20% | below |
| 48 | NEGATIVE_PULSE | -0.16 | 102 | 17 | 68 | 25% | below |
| 49 | CALCIFY | -0.20 | 25 | 4 | 17 | 24% | below |
| 50 | THE_SCYTHE | -0.25 | 19 | 2 | 15 | 13% | below |
| 51 | UNDEATH | -0.31 | 12 | 1 | 10 | 10% | below |
| 52 | FEAR | -0.31 | 93 | 14 | 65 | 22% | below |
| 53 | HIGH_FIVE | -0.34 | 27 | 4 | 19 | 21% | below |
| 54 | BLIGHT_STRIKE | -0.34 | 73 | 11 | 51 | 22% | below |
| 55 | GRAVEBLAST | -0.38 | 78 | 11 | 56 | 20% | below |
| 56 | BANSHEES_CRY | -0.42 | 13 | 1 | 11 | 9% | below |
| 57 | SNAP | -0.52 | 71 | 9 | 53 | 17% | below |
| 58 | POKE | -0.54 | 74 | 9 | 56 | 16% | below |
| 59 | GRAVE_WARDEN | -0.55 | 90 | 12 | 66 | 18% | below |
| 60 | INVOKE | -0.58 | 66 | 8 | 50 | 16% | below |
| 61 | PULL_FROM_BELOW | -0.68 | 26 | 3 | 20 | 15% | below |
| 62 | MISERY | -0.68 | 15 | 1 | 13 | 8% | below |
| 63 | VEILPIERCER | -0.79 | 20 | 2 | 16 | 12% | below |
| 64 | AFTERLIFE | -0.96 | 50 | 5 | 40 | 12% | below |
| 65 | PAGESTORM | -0.99 | 23 | 2 | 19 | 11% | below |
| 66 | DEBILITATE | -1.14 | 33 | 3 | 27 | 11% | below |
| 67 | DEFY | -1.16 | 63 | 6 | 51 | 12% | below |
| 68 | PULL_AGGRO | -1.19 | 64 | 5 | 54 | 9% | below |
| 69 | SOW | -1.48 | 58 | 4 | 50 | 8% | below |
| 70 | DELAY | -1.51 | 19 | 1 | 17 | 6% | below |
| 71 | DEFILE | -1.62 | 57 | 3 | 51 | 6% | below |
| 72 | ERADICATE | -1.64 | 10 | 0 | 10 | 0% | below |
| 73 | BURY | -1.65 | 23 | 1 | 21 | 5% | below |
| 74 | DANSE_MACABRE | -1.69 | 24 | 1 | 22 | 5% | below |
| 75 | EIDOLON | -1.89 | 9 | 0 | 9 | 0% | below |
| 76 | NECRO_MASTERY | -2.00 | 15 | 0 | 15 | 0% | below |
| 77 | SCULPTING_STRIKE | -2.12 | 65 | 2 | 61 | 3% | below |
| 78 | REAVE | -2.29 | 63 | 2 | 59 | 3% | below |
| 79 | SPUR | -2.91 | 16 | 0 | 16 | 0% | below |
| 80 | REAP | -2.96 | 72 | 1 | 70 | 1% | below |
| 81 | LETHALITY | -2.99 | 24 | 0 | 24 | 0% | below |

## Insufficient data (fewer than 5 comparisons)

CRUSH_UNDER (3), MAKE_IT_SO (3), SCRAPE (3), TURBO (3), DECISIONS_DECISIONS (1), HIDDEN_DAGGERS (1), IRON_WAVE (1), KNOCKOUT_BLOW (1), PREDATOR (1), STOKE (1), BOOST_AWAY (1), COMPILE_DRIVER (1), COSMIC_INDIFFERENCE (1), FINISHER (1), FLAME_BARRIER (1), GLITTERSTREAM (1), HOTFIX (1), LOOP (1), PINPOINT (1), RESONANCE (1), SOLAR_STRIKE (1)
