# Card Choices at the Decision Point (Necrobinder)

Solo v0.107.1 runs, finished, card reward screens (shop offers excluded). Built by `tools/analyze_card_choices.py`. For each card offered 4+ times picked and 4+ times passed: act survival when picked against when passed. `[PLAYER-DATA, weak]`: confounded by why the Player picked; p is a two-sided Fisher exact test, and with 44 cards tested a few p < 0.05 results are expected by chance.

## Does the community tier predict the pick effect?

| Consensus tier | Cards | Mean effect (weighted by offers) | Mean effect (unweighted) |
|---|---|---|---|
| S | 1 | -6.7 pts | -6.7 pts |
| A | 3 | +5.5 pts | +4.6 pts |
| B | 14 | -9.4 pts | -9.5 pts |
| C | 10 | -9.0 pts | -4.4 pts |
| D | 16 | +8.1 pts | +8.4 pts |

## Per card (sorted by effect)

| Card | Tier | Picked | Passed | Survived act (picked) | Survived act (passed) | Difference | p | Won (picked) | Won (passed) |
|---|---|---|---|---|---|---|---|---|---|
| Death March | C | 17 | 11 | 76% (13/17) | 36% (4/11) | +40 pts | 0.05 | 65% | 27% |
| Cleanse | D | 8 | 18 | 100% (8/8) | 61% (11/18) | +39 pts | 0.06 | 50% | 39% |
| Melancholy | D | 12 | 7 | 92% (11/12) | 57% (4/7) | +35 pts | 0.12 | 42% | 29% |
| Soul Storm | C | 4 | 10 | 100% (4/4) | 70% (7/10) | +30 pts | 0.51 | 25% | 50% |
| Drain Power | D | 19 | 46 | 79% (15/19) | 52% (24/46) | +27 pts | 0.06 | 11% | 24% |
| Poke | D | 9 | 48 | 89% (8/9) | 69% (33/48) | +20 pts | 0.42 | 33% | 35% |
| Rattle | B | 8 | 7 | 62% (5/8) | 43% (3/7) | +20 pts | 0.62 | 12% | 0% |
| Sow | D | 4 | 47 | 75% (3/4) | 60% (28/47) | +15 pts | 1.00 | 0% | 23% |
| Pull Aggro | D | 5 | 50 | 80% (4/5) | 66% (33/50) | +14 pts | 1.00 | 40% | 32% |
| Afterlife | D | 4 | 36 | 75% (3/4) | 61% (22/36) | +14 pts | 1.00 | 25% | 19% |
| High Five | B | 4 | 14 | 75% (3/4) | 64% (9/14) | +11 pts | 1.00 | 50% | 43% |
| Enfeebling Touch | A | 17 | 5 | 71% (12/17) | 60% (3/5) | +11 pts | 1.00 | 41% | 20% |
| Wisp | D | 27 | 33 | 70% (19/27) | 61% (20/33) | +10 pts | 0.59 | 41% | 21% |
| Right Hand Hand | D | 4 | 14 | 50% (2/4) | 43% (6/14) | +7 pts | 1.00 | 25% | 14% |
| Fear | D | 15 | 52 | 67% (10/15) | 60% (31/52) | +7 pts | 0.77 | 27% | 33% |
| Hang | A | 6 | 5 | 83% (5/6) | 80% (4/5) | +3 pts | 1.00 | 67% | 20% |
| Capture Spirit | C | 8 | 14 | 88% (7/8) | 86% (12/14) | +2 pts | 1.00 | 38% | 36% |
| Bone Shards | C | 5 | 19 | 80% (4/5) | 79% (15/19) | +1 pts | 1.00 | 80% | 37% |
| Deaths Door | B | 12 | 6 | 83% (10/12) | 83% (5/6) | +0 pts | 1.00 | 25% | 17% |
| Squeeze | A | 6 | 10 | 100% (6/6) | 100% (10/10) | +0 pts | 1.00 | 67% | 30% |
| Negative Pulse | D | 17 | 53 | 76% (13/17) | 77% (41/53) | -1 pts | 1.00 | 18% | 47% |
| Blight Strike | D | 10 | 41 | 60% (6/10) | 61% (25/41) | -1 pts | 1.00 | 10% | 24% |
| Deathbringer | B | 5 | 11 | 80% (4/5) | 82% (9/11) | -2 pts | 1.00 | 0% | 36% |
| Scourge | D | 11 | 41 | 64% (7/11) | 66% (27/41) | -2 pts | 1.00 | 27% | 29% |
| Dirge | B | 11 | 10 | 64% (7/11) | 70% (7/10) | -6 pts | 1.00 | 27% | 40% |
| Friendship | S | 10 | 6 | 60% (6/10) | 67% (4/6) | -7 pts | 1.00 | 20% | 0% |
| Seance | B | 12 | 6 | 92% (11/12) | 100% (6/6) | -8 pts | 1.00 | 33% | 67% |
| Graveblast | C | 11 | 47 | 64% (7/11) | 72% (34/47) | -9 pts | 0.71 | 27% | 43% |
| Parse | C | 10 | 16 | 60% (6/10) | 69% (11/16) | -9 pts | 0.69 | 40% | 31% |
| Defy | B | 7 | 44 | 71% (5/7) | 82% (36/44) | -10 pts | 0.61 | 29% | 34% |
| Shroud | B | 6 | 18 | 50% (3/6) | 61% (11/18) | -11 pts | 0.67 | 0% | 50% |
| Severance | D | 6 | 18 | 67% (4/6) | 78% (14/18) | -11 pts | 0.62 | 50% | 28% |
| Flatten | D | 22 | 48 | 41% (9/22) | 52% (25/48) | -11 pts | 0.45 | 18% | 25% |
| Putrefy | B | 18 | 11 | 78% (14/18) | 91% (10/11) | -13 pts | 0.62 | 28% | 27% |
| Snap | C | 10 | 45 | 60% (6/10) | 73% (33/45) | -13 pts | 0.45 | 30% | 31% |
| Invoke | C | 8 | 45 | 38% (3/8) | 51% (23/45) | -14 pts | 0.70 | 25% | 24% |
| End Of Days | B | 5 | 5 | 80% (4/5) | 100% (5/5) | -20 pts | 1.00 | 20% | 60% |
| Oblivion | B | 5 | 5 | 80% (4/5) | 100% (5/5) | -20 pts | 1.00 | 20% | 60% |
| Grave Warden | C | 13 | 56 | 54% (7/13) | 77% (43/56) | -23 pts | 0.16 | 31% | 46% |
| No Escape | B | 8 | 7 | 62% (5/8) | 86% (6/7) | -23 pts | 0.57 | 38% | 57% |
| Countdown | B | 5 | 14 | 40% (2/5) | 64% (9/14) | -24 pts | 0.60 | 0% | 50% |
| Sleight Of Flesh | B | 6 | 12 | 67% (4/6) | 92% (11/12) | -25 pts | 0.25 | 50% | 58% |
| Sic Em | D | 7 | 13 | 43% (3/7) | 69% (9/13) | -26 pts | 0.36 | 14% | 23% |
| Haunt | C | 6 | 18 | 17% (1/6) | 67% (12/18) | -50 pts | 0.06 | 17% | 33% |
