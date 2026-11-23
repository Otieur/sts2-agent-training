# Comparison: the Knowledge Demon's curse searched alone, and a second look at every choice searched (boss replay 6)

Written before the run (ML-10, decision 0006 item 2), 2026-11-23 at 11:34, after boss replay 4 was read (`reports/phase9/boss-replay-4.md` section 5) and before any fight of this comparison is played. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Question and hypotheses
Boss replay 4 searched the answers to every card choice inside a fight. It won more Knowledge Demon fights (125 against 106 of 176; its H1 holds) and more of the other boss fights (65 against 59 of 93), and it lost two benchmark fights more than the first-option search (50 against 52 of 60), one more than its registered guard allowed. By its rule the option stays off in general and a version limited to the Knowledge Demon's curse is registered on its own. This is that registration.

It asks two things.

**The curse alone (`k`).** The search compares the answers at the Knowledge Demon's Curse of Knowledge (Disintegration beside Mind Rot, Sloth or Waste Away) and takes the first option at every other card choice, as before (`tools/sim.py SEARCH_CHOICES = "curse"`). In every fight without that curse the search is the first-option search, decision for decision, so the benchmark fights are not at stake. In boss replay 4 the curse and the other choices were searched together, and it does not say how much of the Demon's gain is the curse.

- **H1 (the curse alone, wins):** on the Knowledge Demon situations, with sample seeds not played before, the search with the curse searched wins more fights than the search that takes the first option.

**Every choice (`c`), a second look.** The guard failed on 60 fights played once each: four fights ended differently, three against the option. Two of the three were traced (boss replay 4, section 6): in both the choice fell in a turn whose candidates were all lost in every rollout, so the answer was picked by the enemies' HP left at death. That is thin ground for keeping the option on or off, and the other two sets speak for it. The conditions under which it replaces the curse-only version are fixed here, before more fights are played, and the 30 fights that failed are counted in.

- Conditions and not hypotheses (section 4): on the Demon's new seeds, on the benchmark's elite and boss fights with four more sample seeds, and on the other boss situations with one more.
- Described and not tested: the curse taken at each offer by each arm; how the Demon's gain splits between the curse and the other choices.

Choices made before the run and not tuned on it: the curse is recognised by its options (Disintegration with Mind Rot, Sloth or Waste Away), not by the encounter; the cap of ten candidates and the rollouts' own choices are as in boss replay 4; hallway fights are not played again (29 against 29 of 30 there, and 0.3 HP more where both win).

## 2. Runs
- **Set D:** `data/sim/boss-replay-4-d.json`, the 59 Knowledge Demon situations of run benchmarks 16 and 17. Sample indexes 3, 4 and 5 (fight seed 7000000 + 10 × situation + index; boss replay 4 played 0, 1 and 2): 177 fights an arm. Arms `mcw6paf`, `mcw6pafk`, `mcw6pafc`. Folders `data/learn/bench/boss-replay-6-d3`, `-d4`, `-d5`, read as one set (`tools/choices_compare.py --pool`).
- **Set B, elite and boss rooms:** the 30 elite and boss fights of `data/sim/benchmark-v1.json`, sample indexes 6, 7, 8 and 9 (120 fights an arm; index 3 is boss replay 4's, and no comparison has played 6 to 9). Arms `mcw6paf`, `mcw6pafc`. Folder `data/learn/bench/boss-replay-6-b-eb`.
- **Set O:** `data/sim/boss-replay-4-o.json`, the 93 other boss situations of run benchmark 17, sample index 1 (index 0 is boss replay 4's). Arms `mcw6paf`, `mcw6pafc`. Folder `data/learn/bench/boss-replay-6-o1`.
- Each fight is started fresh from its spec; all arms of a fight play it with the same sample seed. Host: the Release5 build. Order: D (indexes 3, 4, 5), B, O. After boss replay 5; four workers at the lowest priority while run benchmark 19's second sitting is playing, nine once it has ended (the number of workers does not enter a fight). No deadline: every fight is played.
- Tested before registration: unit cases (`tools/tests/test_sim.py`, `test_choices_compare.py`); what each arm sets while it searches; one traced fight of a Set D situation with a seed outside every set (section 6).

## 3. Policies
- `mcw6paf`: the fight search as the run benchmarks play boss and elite rooms today (the first option at a card choice).
- `mcw6pafk`: the same with the answers to the Knowledge Demon's curse searched and the first option at every other choice.
- `mcw6pafc`: the same with the answers to every card choice searched (boss replay 4's arm).

## 4. Metrics and tests
- **H1:** fights won per situation of Set D, the mean over its three sample seeds, `mcw6pafk` against `mcw6paf`: one-sided sign test at 0.05 over the situations whose two arms differ. Reported with it: fights won per arm (of 177) and by source benchmark, the curse taken at each offer per arm, HP left where both win.
- **The conditions for every choice searched (`mcw6pafc`):**
  - **G1, Set D's new seeds:** it wins more fights than `mcw6paf`, and at least as many as `mcw6pafk` less two at most.
  - **G2, Set B's elite and boss fights over sample indexes 3 and 6 to 9** (150 fights an arm; boss replay 4's 30 fights of index 3 counted in, where it won 21 against 23): it wins at least as many fights as `mcw6paf`.
  - **G3, the same 150 fights:** on the fights both arms win its mean HP left is not lower by more than 1.0.
  - **G4, Set O's index 1:** it wins at least as many fights as `mcw6paf`, less two at most.
- Per arm and set as in boss replay 4: choices per fight, how many were searched, how many took another answer than the first option, by kind of choice; search errors; seconds per fight. A fight with a host error in an arm is left out of that arm's paired figures and reported.
- **What follows.**
  - If G1 to G4 all hold: every choice searched becomes the default of the fight search (`SIM_SEARCH_CHOICES=1`), in all room types, for everything started afterwards.
  - If one of them fails and H1 holds: the curse searched alone becomes the default (`SIM_SEARCH_CHOICES=curse`), and the other choices keep the first option until a registration of their own.
  - If one of them fails and H1 does not hold: the default stays the first option, and Set D's two readings are put side by side in section 6.
  - A run benchmark begun before the default changes is finished with the setting it began with (run benchmark 19 keeps `SIM_SEARCH_CHOICES=0`). The next run benchmark registered after it carries the new default in every arm, so what the default is worth in runs won is read against the earlier benchmarks and not inside it.

## 5. Results
### Set D, the Knowledge Demon on new sample seeds (read 2026-11-23 14:15)
Played 12:29–13:52 (`data/learn/bench/boss-replay-6-d3`, `-d4`, `-d5`; four workers for the first two indexes, nine for the third; `python3 -I tools/choices_compare.py --pool --a mcw6paf --b mcw6pafk --specs data/sim/boss-replay-4-d.json` on the three folders, and the same with `--b mcw6pafc` and with `--a mcw6pafk --b mcw6pafc`). 177 fights an arm; two fights had host trouble (section 6).

| | First option (`mcw6paf`) | The curse alone (`mcw6pafk`) | Every choice (`mcw6pafc`) |
|---|---|---|---|
| **Fights won** (the 175 fights all three arms finished) | **103 (59%)** | **114 (65%)** | **115 (66%)** |
| on run benchmark 16's situations | 86 of 124 | 91 of 124 | 94 of 125 |
| on run benchmark 17's situations | 17 of 51 | 23 of 51 | 22 of 51 |
| Card choices a fight | 3.2 | 3.4 | 3.5 |
| searched | 0 | 380 of 601 | 601 of 610 |
| another answer than the first option | 0 | 213 | 322 |
| First curse offer: Mind Rot, Disintegration | 0, 175 | 120, 55 | 113, 63 |
| Second offer: Sloth, Disintegration | 0, 152 | 78, 87 | 70, 96 |
| Third offer: Waste Away, Disintegration | 0, 6 | 15, 25 | 15, 30 |
| Seconds a fight | 43 | 44 | 45 |

- **H1 does not hold at the registered level.** The curse searched alone wins more of a situation's fights in 15 of the 59 situations and fewer in 7: one-sided sign test p = 0.067. It wins 114 fights against 103 on the 175 fights both arms finished, and keeps 4.1 HP more where both win (bootstrap 95% 1.4 to 7.0).
- **G1 holds.** Every choice searched wins 116 fights against 103 on the 176 fights both arms finished (17 situations against 8; where both win 3.6 HP more, 0.6 to 6.5), and 115 against the curse-only arm's 114 (6 situations against 5; no difference in HP left).
- **How the gain splits.** Nearly all of it is the curse: the other choices searched as well add one fight in 176 at this boss.
- Beside boss replay 4's Set D (125 against 106 of 176): the same direction and about the same size on new seeds, 241 against 209 of 352 over both.

### Set B, the benchmark's elite and boss fights on four more sample seeds (read 2026-11-23 14:26)
Played 13:52–14:25 (`data/learn/bench/boss-replay-6-b-eb`, nine workers; no error, no restart). 120 fights an arm.

| | First option (`mcw6paf`) | Every choice (`mcw6pafc`) |
|---|---|---|
| **Fights won, sample seeds 6 to 9** | **87 of 120** | **92 of 120** |
| boss rooms | 17 of 40 | 22 of 40 |
| elite rooms | 70 of 80 | 70 of 80 |
| **With boss replay 4's seed 3 (G2)** | **110 of 150** | **113 of 150** |
| boss rooms | 22 of 50 | 26 of 50 |
| elite rooms | 88 of 100 | 87 of 100 |
| Card choices on seeds 6 to 9 | 155 | 153 (149 searched, 75 another answer) |
| Seconds a fight | 66 | 70 |

- **G2 holds:** 113 against 110. On the four new seeds alone the arm with the choices searched wins more of a situation's fights in 3 situations and fewer in 1.
- **G3 holds:** where both arms win (105 fights over the five seeds) its mean HP left is 0.3 higher (bootstrap 95% −0.8 to +1.4).
- The two fights it lost on seed 3 by its answer to a draw-pile choice (the Test Subject, 1 against 0; Mecha Knight, 1 against 0) read on the new seeds: the Test Subject 4 of 4 against 1 of 4, Mecha Knight 6 of 8 each. Seed 3's deficit does not repeat.

### Set O, the other bosses on one more sample seed (read 2026-11-23 14:58)
Played 14:25–14:57 with a pause of four minutes (section 6; `data/learn/bench/boss-replay-6-o1`, nine workers; no error, no restart). 93 fights an arm.

| | First option (`mcw6paf`) | Every choice (`mcw6pafc`) |
|---|---|---|
| **Fights won, sample seed 1** | **58 of 93** | **60 of 93** |
| act 1: Ceremonial Beast, The Kin, Vantom | 17 of 18, 19 of 22, 10 of 12 | 17 of 18, 19 of 22, 11 of 12 |
| act 2: Kaiser Crab, The Insatiable | 4 of 18, 6 of 8 | 5 of 18, 5 of 8 |
| act 3: Test Subject, Queen, Aeonglass | 1 of 8, 0 of 4, 1 of 3 | 1 of 8, 1 of 4, 1 of 3 |
| With boss replay 4's seed 0 | 117 of 186 | 125 of 186 |
| Card choices on seed 1 | 124 | 119 (116 searched, 54 another answer) |
| Seconds a fight | 82 | 91 |

- **G4 holds:** 60 against 58 (56 at least was asked). More of a situation's fights in 4 situations, fewer in 2; where both win (56 fights) 4.8 HP more (bootstrap 95% 2.5 to 7.4).
- Over both seeds of this set: 125 against 117 of 186, more in 8 situations and fewer in 2, 3.5 HP more where both win (2.0 to 5.1).

### What follows (2026-11-23 14:58)
G1, G2, G3 and G4 hold. By section 4 **every choice searched is the default of the fight search from now on**, in all room types: `tools/sim.py SEARCH_CHOICES` reads `SIM_SEARCH_CHOICES` with a default of 1 (changed at 14:58, in the commit that carries this reading). H1 for the curse searched alone did not hold at its level (p = 0.067) and is not needed: the general option replaces that version. Run benchmark 19, if it is played further, keeps `SIM_SEARCH_CHOICES=0`. A fight-benchmark arm states its own setting by its name, so earlier arms replay as they were.

Over boss replays 4 and 6 together the arm with every choice searched wins 508 of 718 fights against 465: the Knowledge Demon 241 against 209 of 352, the other bosses 125 against 117 of 186, the benchmark's elite and boss fights 113 against 110 of 150, its hallway fights 29 each of 30. The gain is in boss rooms; elite and hallway rooms are level. The guard that failed on one sample seed of 60 fights did what it was there for and cost about four hours.

What it is worth in runs won has not been measured and is not claimed: the search that plays the fights of a run now uses it, and the next whole runs show it.

## 6. Deviations and notes
- 2026-11-23 11:34, before the run. **One fight of a Set D situation was played with the curse searched alone while the code was tested** (situation 20, fight seed 7600020, outside every set, `tools/fight_trace.py --choices curse`): the two curse offers were searched with two candidates each and Disintegration was taken at both (20 against −40 at the first, 54 against 39 at the second), the one other choice of the fight took the first option without a search; won on turn 7 with 43 HP. Not a result.
- 2026-11-23 11:34, before the run. The sample seeds were checked against every folder of `data/learn/bench` that played the three sets: of the benchmark set, indexes 0 to 5 were played by an earlier comparison of search budgets (`boss-budget-1`, arms `mcw6` and `mcw24`, without potions), 0 and 1 by seven others, 3 by boss replay 4; 6 to 9 by none. Of Set D only boss replay 4's 0 to 2, of Set O only its 0. So boss replay 4's note that index 3 of the benchmark set had not been played was wrong for arms other than its own; its two arms had not played it, and nothing in its reading depends on the earlier arms.
- 2026-11-23 14:32, Set D: two fights had host trouble, both in situations 1 and 2, the two that had it in boss replay 4. Situation 2, sample seed 4: the first-option arm's fight ended blocked (counted as not won where it is paired; with it left out every choice searched wins 115 against 103 of 175 and the count of situations is the same), and the curse-only arm's fight ended in `no choice is pending` at a restore (left out). Situation 1, sample seed 5: the first-option arm's fight ended in the game exception of boss replay 4's Set D (`NullReferenceException`; left out). Three more fights of those two situations were finished after one or two restarts and are counted. These errors come with the situations and not with an arm (FI-7h).
- 2026-11-23 14:32, **the queue was paused at the Player's request from 14:27 to 14:31** (`kill -STOP` on the process group), two minutes into Set O's seed 1, and that set alone was resumed at the Player's word; what the queue held after it (boss replay 7, run benchmark 19's third sitting) stays paused. A fight in flight at the pause may show a host restart.
