# Event Choices at the Decision Point

All characters, solo, v0.107.1, finished runs. Built by `tools/analyze_event_choices.py`. For each event option chosen 4+ times: act survival when the Player chose it against when the Player chose another option at the same event, with the option's mean HP, gold and max HP change. Sorted by p (two-sided Fisher). `[PLAYER-DATA, weak]`: with 85 options tested, a few p < 0.05 results are expected by chance.

| Event | Option | Chosen | Other options | Survived act (this) | Survived act (others) | Difference | p | HP | Gold | Max HP |
|---|---|---|---|---|---|---|---|---|---|---|
| Endless Conveyor | Observe Chef | 5 | 46 | 60% (3/5) | 100% (46/46) | -40 pts | 0.01 | +0.0 | +0 | +0.0 |
| Reflections | Touch A Mirror | 7 | 3 | 14% (1/7) | 67% (2/3) | -52 pts | 0.18 | +0.0 | +0 | +0.0 |
| Lost Wisp | Claim | 5 | 7 | 80% (4/5) | 29% (2/7) | +51 pts | 0.24 | +4.0 | +0 | +0.0 |
| Lost Wisp | Search | 7 | 5 | 29% (2/7) | 80% (4/5) | -51 pts | 0.24 | +0.0 | +58 | +0.0 |
| Brain Leech | Share Knowledge | 19 | 13 | 74% (14/19) | 54% (7/13) | +20 pts | 0.28 | +0.3 | +1 | +0.0 |
| Brain Leech | Rip | 13 | 19 | 54% (7/13) | 74% (14/19) | -20 pts | 0.28 | -5.0 | +0 | +0.0 |
| Trial | Accept | 8 | 14 | 62% (5/8) | 36% (5/14) | +27 pts | 0.38 | +3.1 | +38 | +0.0 |
| Tea Master | Ember Tea | 4 | 2 | 75% (3/4) | 0% (0/2) | +75 pts | 0.40 | +0.0 | -150 | +0.0 |
| Colorful Philosophers | Defect | 4 | 3 | 100% (4/4) | 67% (2/3) | +33 pts | 0.43 | +0.0 | +0 | +0.0 |
| Waterlogged Scriptorium | Prickly Sponge | 4 | 4 | 50% (2/4) | 100% (4/4) | -50 pts | 0.43 | +0.0 | -99 | +0.0 |
| Waterlogged Scriptorium | Bloody Ink | 4 | 4 | 100% (4/4) | 50% (2/4) | +50 pts | 0.43 | +6.0 | +0 | +6.0 |
| This Or That | Ornate | 40 | 8 | 45% (18/40) | 62% (5/8) | -18 pts | 0.45 | +0.6 | +0 | +0.3 |
| This Or That | Plain | 8 | 40 | 62% (5/8) | 45% (18/40) | +18 pts | 0.45 | -6.0 | +53 | +0.0 |
| Morphic Grove | Loner | 9 | 3 | 89% (8/9) | 67% (2/3) | +22 pts | 0.45 | +5.0 | +0 | +5.0 |
| Colossal Flower | Extract Current Prize 1 | 7 | 2 | 57% (4/7) | 100% (2/2) | -43 pts | 0.50 | +0.7 | +35 | +0.0 |
| Ranwid The Elder | Relic | 5 | 11 | 60% (3/5) | 82% (9/11) | -22 pts | 0.55 | +0.0 | +0 | +0.0 |
| Crystal Sphere | Payment Plan | 9 | 4 | 56% (5/9) | 25% (1/4) | +31 pts | 0.56 | +1.2 | +50 | +0.0 |
| Crystal Sphere | Uncover Future | 4 | 9 | 25% (1/4) | 56% (5/9) | -31 pts | 0.56 | +0.0 | -57 | +0.0 |
| The Lantern Key | Keep The Key | 4 | 7 | 50% (2/4) | 71% (5/7) | -21 pts | 0.58 | -12.5 | +15 | +0.0 |
| The Lantern Key | Fight | 4 | 7 | 50% (2/4) | 71% (5/7) | -21 pts | 0.58 | -12.5 | +15 | +0.0 |
| Ranwid The Elder | Gold | 7 | 9 | 86% (6/7) | 67% (6/9) | +19 pts | 0.58 | +0.7 | -57 | +0.0 |
| Battleworn Dummy | Setting 1 | 6 | 11 | 50% (3/6) | 64% (7/11) | -14 pts | 0.64 | +0.8 | +0 | +0.0 |
| Abyssal Baths | Immerse | 7 | 33 | 71% (5/7) | 79% (26/33) | -7 pts | 0.64 | -6.9 | +0 | +6.0 |
| Abyssal Baths | Exit Baths | 7 | 33 | 71% (5/7) | 79% (26/33) | -7 pts | 0.64 | -6.9 | +0 | +6.0 |
| Tinker Time | Skill | 7 | 26 | 57% (4/7) | 65% (17/26) | -8 pts | 0.69 | +0.0 | +0 | +0.0 |
| Abyssal Baths | Abstain | 12 | 28 | 83% (10/12) | 75% (21/28) | +8 pts | 0.70 | +9.6 | +0 | +0.0 |
| Slippery Bridge | Hold On 0 | 28 | 52 | 75% (21/28) | 69% (36/52) | +6 pts | 0.80 | -4.9 | +0 | +0.0 |
| Zen Weaver | Emotional Awareness | 4 | 4 | 50% (2/4) | 50% (2/4) | +0 pts | 1.00 | +0.0 | -125 | +0.0 |
| Zen Weaver | Breathing Techniques | 4 | 4 | 50% (2/4) | 50% (2/4) | +0 pts | 1.00 | +0.0 | -50 | +0.0 |
| Abyssal Baths | Linger | 14 | 26 | 79% (11/14) | 77% (20/26) | +2 pts | 1.00 | -10.7 | +0 | +7.7 |
| Amalgamator | Combine Strikes | 6 | 4 | 67% (4/6) | 75% (3/4) | -8 pts | 1.00 | +0.8 | +0 | +0.0 |
| Amalgamator | Combine Defends | 4 | 6 | 75% (3/4) | 67% (4/6) | +8 pts | 1.00 | +0.0 | +0 | +0.0 |
| Aroma Of Chaos | Maintain Control | 14 | 3 | 50% (7/14) | 67% (2/3) | -17 pts | 1.00 | +0.0 | +0 | +0.0 |
| Battleworn Dummy | Setting 2 | 8 | 9 | 62% (5/8) | 56% (5/9) | +7 pts | 1.00 | +2.9 | -2 | +0.0 |
| Bugslayer | Squash | 9 | 8 | 56% (5/9) | 50% (4/8) | +6 pts | 1.00 | +0.0 | +0 | +0.0 |
| Bugslayer | Extermination | 8 | 9 | 50% (4/8) | 56% (5/9) | -6 pts | 1.00 | +0.0 | +0 | +0.0 |
| Byrdonis Nest | Take | 7 | 10 | 57% (4/7) | 60% (6/10) | -3 pts | 1.00 | +0.0 | +0 | +0.0 |
| Byrdonis Nest | Eat | 10 | 7 | 60% (6/10) | 57% (4/7) | +3 pts | 1.00 | +7.0 | +0 | +7.0 |
| Dense Vegetation | Trudge On | 7 | 6 | 57% (4/7) | 67% (4/6) | -10 pts | 1.00 | -7.9 | +83 | +0.1 |
| Doll Room | Random | 12 | 6 | 67% (8/12) | 67% (4/6) | +0 pts | 1.00 | +0.0 | +0 | +0.0 |
| Doors Of Light And Dark | Light | 10 | 3 | 60% (6/10) | 67% (2/3) | -7 pts | 1.00 | +0.0 | +0 | +0.0 |
| Drowning Beacon | Climb | 13 | 3 | 46% (6/13) | 67% (2/3) | -21 pts | 1.00 | +0.0 | +0 | -13.0 |
| Endless Conveyor | Caviar | 9 | 42 | 100% (9/9) | 95% (40/42) | +5 pts | 1.00 | +16.7 | -242 | +6.7 |
| Endless Conveyor | Suspicious Condiment | 4 | 47 | 100% (4/4) | 96% (45/47) | +4 pts | 1.00 | +13.5 | -261 | +6.0 |
| Endless Conveyor | Seapunk Salad | 6 | 45 | 100% (6/6) | 96% (43/45) | +4 pts | 1.00 | +17.7 | -276 | +6.0 |
| Endless Conveyor | Leave | 6 | 45 | 100% (6/6) | 96% (43/45) | +4 pts | 1.00 | +16.0 | -228 | +6.0 |
| Endless Conveyor | Spicy Snappy | 5 | 46 | 100% (5/5) | 96% (44/46) | +4 pts | 1.00 | +24.4 | -340 | +6.4 |
| Endless Conveyor | Clam Roll | 6 | 45 | 100% (6/6) | 96% (43/45) | +4 pts | 1.00 | +22.7 | -263 | +6.0 |
| Endless Conveyor | Fried Eel | 5 | 46 | 100% (5/5) | 96% (44/46) | +4 pts | 1.00 | +17.6 | -291 | +5.6 |
| Field Of Man Sized Holes | Enter Your Hole | 11 | 2 | 36% (4/11) | 50% (1/2) | -14 pts | 1.00 | +0.0 | +0 | +0.0 |
| Grave Of The Forgotten | Accept | 4 | 3 | 25% (1/4) | 33% (1/3) | -8 pts | 1.00 | +0.0 | +0 | +0.0 |
| Infested Automaton | Touch Core | 6 | 10 | 50% (3/6) | 50% (5/10) | +0 pts | 1.00 | +0.0 | +2 | +0.0 |
| Infested Automaton | Study | 10 | 6 | 50% (5/10) | 50% (3/6) | +0 pts | 1.00 | +0.0 | +0 | +0.0 |
| Jungle Maze Adventure | Solo Quest | 5 | 6 | 60% (3/5) | 50% (3/6) | +10 pts | 1.00 | -18.0 | +154 | +0.0 |
| Jungle Maze Adventure | Join Forces | 6 | 5 | 50% (3/6) | 60% (3/5) | -10 pts | 1.00 | +0.0 | +41 | +0.0 |
| Potion Courier | Grab Potions | 8 | 18 | 62% (5/8) | 67% (12/18) | -4 pts | 1.00 | +0.0 | +0 | +0.0 |
| Potion Courier | Ransack | 18 | 8 | 67% (12/18) | 62% (5/8) | +4 pts | 1.00 | +0.6 | +0 | +0.0 |
| Ranwid The Elder | Potion | 4 | 12 | 75% (3/4) | 75% (9/12) | +0 pts | 1.00 | +1.2 | +0 | +0.0 |
| Relic Trader | Middle | 7 | 9 | 71% (5/7) | 67% (6/9) | +5 pts | 1.00 | +0.7 | +0 | +0.0 |
| Relic Trader | Top | 6 | 10 | 67% (4/6) | 70% (7/10) | -3 pts | 1.00 | +0.0 | +0 | +0.0 |
| Room Full Of Cheese | Gorge | 27 | 5 | 78% (21/27) | 80% (4/5) | -2 pts | 1.00 | +0.0 | +1 | +0.0 |
| Room Full Of Cheese | Search | 5 | 27 | 80% (4/5) | 78% (21/27) | +2 pts | 1.00 | -12.8 | +0 | +0.0 |
| Self Help Book | Read The Back | 23 | 14 | 74% (17/23) | 79% (11/14) | -5 pts | 1.00 | +0.2 | +0 | +0.0 |
| Self Help Book | Read Entire Book | 6 | 31 | 83% (5/6) | 74% (23/31) | +9 pts | 1.00 | +0.0 | +0 | +0.0 |
| Self Help Book | Read Passage | 8 | 29 | 75% (6/8) | 76% (22/29) | -1 pts | 1.00 | +0.0 | +0 | +0.0 |
| Slippery Bridge | Overcome | 38 | 42 | 71% (27/38) | 71% (30/42) | -0 pts | 1.00 | -3.6 | +0 | +0.0 |
| Slippery Bridge | Hold On 1 | 11 | 69 | 73% (8/11) | 71% (49/69) | +2 pts | 1.00 | -8.4 | +0 | +0.0 |
| Spiraling Whirlpool | Observe | 11 | 4 | 91% (10/11) | 100% (4/4) | -9 pts | 1.00 | +0.5 | +0 | +0.0 |
| Spiraling Whirlpool | Drink | 4 | 11 | 100% (4/4) | 91% (10/11) | +9 pts | 1.00 | +22.2 | +0 | +0.0 |
| Stone Of All Time | Push | 7 | 3 | 71% (5/7) | 67% (2/3) | +5 pts | 1.00 | -6.0 | +0 | +0.0 |
| Sunken Statue | Grab Sword | 16 | 10 | 56% (9/16) | 60% (6/10) | -4 pts | 1.00 | +0.0 | +0 | +0.0 |
| Sunken Statue | Dive Into Water | 10 | 16 | 60% (6/10) | 56% (9/16) | +4 pts | 1.00 | -7.0 | +110 | +0.0 |
| Symbiote | Approach | 9 | 21 | 56% (5/9) | 52% (11/21) | +3 pts | 1.00 | +0.0 | +0 | +0.0 |
| Symbiote | Kill With Fire | 21 | 9 | 52% (11/21) | 56% (5/9) | -3 pts | 1.00 | +0.2 | +1 | +0.0 |
| Tablet Of Truth | Smash | 7 | 3 | 86% (6/7) | 100% (3/3) | -14 pts | 1.00 | +16.6 | +0 | +0.0 |
| Tinker Time | Choose Card Type | 11 | 22 | 64% (7/11) | 64% (14/22) | +0 pts | 1.00 | +0.0 | +0 | +0.0 |
| Tinker Time | Power | 4 | 29 | 75% (3/4) | 62% (18/29) | +13 pts | 1.00 | +0.0 | +0 | +0.0 |
| Tinker Time | Energized | 5 | 28 | 60% (3/5) | 64% (18/28) | -4 pts | 1.00 | +0.0 | +0 | +0.0 |
| Trash Heap | Grab | 4 | 3 | 75% (3/4) | 67% (2/3) | +8 pts | 1.00 | +0.0 | +100 | +0.0 |
| Wellspring | Bathe | 11 | 4 | 82% (9/11) | 100% (4/4) | -18 pts | 1.00 | +0.0 | +0 | +0.0 |
| Wellspring | Bottle | 4 | 11 | 100% (4/4) | 82% (9/11) | +18 pts | 1.00 | +0.0 | +0 | +0.0 |
| Whispering Hollow | Hug | 6 | 5 | 50% (3/6) | 40% (2/5) | +10 pts | 1.00 | -9.0 | +0 | +0.0 |
| Whispering Hollow | Gold | 5 | 6 | 40% (2/5) | 50% (3/6) | -10 pts | 1.00 | +0.0 | -35 | +0.0 |
| Wood Carvings | Bird | 7 | 6 | 57% (4/7) | 67% (4/6) | -10 pts | 1.00 | +0.0 | +0 | +0.0 |
| Wood Carvings | Snake | 6 | 7 | 67% (4/6) | 57% (4/7) | +10 pts | 1.00 | +0.0 | +0 | +0.0 |
