# Card Choices at the Decision Point (Ironclad)

Solo v0.107.1 runs, finished, card reward screens (shop offers excluded). Built by `tools/analyze_card_choices.py`. For each card offered 4+ times picked and 4+ times passed: act survival when picked against when passed. `[PLAYER-DATA, weak]`: confounded by why the Player picked; p is a two-sided Fisher exact test, and with 37 cards tested a few p < 0.05 results are expected by chance.

## Does the community tier predict the pick effect?

| Consensus tier | Cards | Mean effect (weighted by offers) | Mean effect (unweighted) |
|---|---|---|---|
| A | 4 | +16.6 pts | +13.3 pts |
| B | 11 | -0.3 pts | +0.9 pts |
| C | 8 | -16.2 pts | -21.1 pts |
| D | 14 | -13.4 pts | -11.0 pts |

## Per card (sorted by effect)

| Card | Tier | Picked | Passed | Survived act (picked) | Survived act (passed) | Difference | p | Won (picked) | Won (passed) |
|---|---|---|---|---|---|---|---|---|---|
| Battle Trance | A | 4 | 18 | 100% (4/4) | 50% (9/18) | +50 pts | 0.11 | 50% | 39% |
| Flame Barrier | B | 4 | 9 | 100% (4/4) | 67% (6/9) | +33 pts | 0.50 | 25% | 56% |
| Forgotten Ritual | B | 7 | 11 | 71% (5/7) | 45% (5/11) | +26 pts | 0.37 | 43% | 27% |
| True Grit | B | 23 | 31 | 78% (18/23) | 58% (18/31) | +20 pts | 0.15 | 48% | 42% |
| Molten Fist | D | 16 | 26 | 69% (11/16) | 50% (13/26) | +19 pts | 0.34 | 44% | 23% |
| Aggression | B | 4 | 7 | 100% (4/4) | 86% (6/7) | +14 pts | 1.00 | 50% | 14% |
| Crimson Mantle | A | 4 | 10 | 100% (4/4) | 90% (9/10) | +10 pts | 1.00 | 100% | 80% |
| Infernal Blade | D | 4 | 10 | 75% (3/4) | 70% (7/10) | +5 pts | 1.00 | 50% | 50% |
| Armaments | C | 25 | 42 | 64% (16/25) | 60% (25/42) | +4 pts | 0.80 | 36% | 29% |
| Bloodletting | B | 22 | 36 | 68% (15/22) | 64% (23/36) | +4 pts | 0.78 | 55% | 42% |
| Drum Of Battle | C | 9 | 11 | 56% (5/9) | 55% (6/11) | +1 pts | 1.00 | 44% | 18% |
| Evil Eye | D | 14 | 7 | 71% (10/14) | 71% (5/7) | +0 pts | 1.00 | 50% | 57% |
| One Two Punch | A | 5 | 7 | 100% (5/5) | 100% (7/7) | +0 pts | 1.00 | 20% | 71% |
| Tremble | D | 23 | 34 | 57% (13/23) | 59% (20/34) | -2 pts | 1.00 | 39% | 24% |
| Thunderclap | D | 7 | 40 | 43% (3/7) | 48% (19/40) | -5 pts | 1.00 | 0% | 18% |
| Shrug It Off | B | 20 | 51 | 50% (10/20) | 55% (28/51) | -5 pts | 0.79 | 25% | 27% |
| Colossus | A | 10 | 9 | 60% (6/10) | 67% (6/9) | -7 pts | 1.00 | 40% | 44% |
| Burning Pact | B | 12 | 6 | 58% (7/12) | 67% (4/6) | -8 pts | 1.00 | 25% | 33% |
| Vicious | C | 10 | 13 | 60% (6/10) | 69% (9/13) | -9 pts | 0.69 | 30% | 46% |
| Second Wind | B | 13 | 7 | 62% (8/13) | 71% (5/7) | -10 pts | 1.00 | 38% | 43% |
| Unrelenting | D | 5 | 10 | 60% (3/5) | 70% (7/10) | -10 pts | 1.00 | 0% | 60% |
| Feel No Pain | B | 6 | 13 | 67% (4/6) | 77% (10/13) | -10 pts | 1.00 | 67% | 31% |
| Havoc | D | 6 | 47 | 50% (3/6) | 64% (30/47) | -14 pts | 0.66 | 17% | 40% |
| Sword Boomerang | D | 12 | 50 | 58% (7/12) | 74% (37/50) | -16 pts | 0.31 | 33% | 48% |
| Headbutt | D | 7 | 48 | 57% (4/7) | 73% (35/48) | -16 pts | 0.40 | 14% | 44% |
| Cinder | D | 9 | 48 | 44% (4/9) | 60% (29/48) | -16 pts | 0.47 | 11% | 38% |
| Iron Wave | D | 7 | 61 | 43% (3/7) | 59% (36/61) | -16 pts | 0.45 | 0% | 39% |
| Pommel Strike | B | 7 | 42 | 57% (4/7) | 76% (32/42) | -19 pts | 0.36 | 43% | 60% |
| Twin Strike | D | 8 | 37 | 38% (3/8) | 62% (23/37) | -25 pts | 0.25 | 25% | 46% |
| Setup Strike | D | 5 | 50 | 40% (2/5) | 68% (34/50) | -28 pts | 0.33 | 0% | 48% |
| Uppercut | C | 4 | 11 | 25% (1/4) | 55% (6/11) | -30 pts | 0.57 | 25% | 27% |
| Ashen Strike | C | 5 | 6 | 20% (1/5) | 50% (3/6) | -30 pts | 0.55 | 20% | 50% |
| Breakthrough | D | 21 | 41 | 48% (10/21) | 78% (32/41) | -30 pts | 0.02 | 19% | 61% |
| Pillage | C | 4 | 12 | 25% (1/4) | 58% (7/12) | -33 pts | 0.57 | 25% | 50% |
| Body Slam | C | 4 | 42 | 25% (1/4) | 60% (25/42) | -35 pts | 0.30 | 25% | 14% |
| Stampede | B | 9 | 10 | 44% (4/9) | 80% (8/10) | -36 pts | 0.17 | 11% | 80% |
| Rage | C | 4 | 16 | 25% (1/4) | 62% (10/16) | -38 pts | 0.28 | 0% | 44% |
