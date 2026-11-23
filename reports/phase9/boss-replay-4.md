# Comparison: the answers to a card choice searched inside a fight (boss replay 4)

Written before the run (ML-10, decision 0006 item 2), 2026-11-23 at 08:07, after trace sweep 2 was read (`reports/phase9/boss-replay-3.md` section 6) and before any fight of this comparison is played. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Question and hypotheses
Some cards, potions and enemy moves ask the player to pick a card in the middle of a fight: the card Headbutt puts back on the draw pile, the card True Grit+, Brand or Burning Pact exhausts, the card Armaments upgrades, one of the three cards a potion offers, and the Knowledge Demon's Curse of Knowledge. The fight search has never compared the answers. The rule planner has no view on card choices and takes the first option, and at a choice its one answer was the search's only candidate (`tools/sim.py search_candidates`, in place since the first search experiment), so the first option was taken every time, in the fight and in every rollout.

Trace sweep 2 shows what that means in boss fights: 143 card choices in 68 fights (2.1 a fight), every one with more than one distinct option, every one answered with the first. By what asked: the end of a turn 43 (the Knowledge Demon's curse and cards that act on the hand at the end of the turn), Headbutt 20, Brand 13, potions that offer or move cards 33, True Grit+ 8, Burning Pact 6, Armaments 6, others 14. At the Knowledge Demon the curse offers Disintegration (6, 7, then 8 damage to the player at the end of every turn, the amounts adding up) beside Mind Rot, then Sloth, then Waste Away, and Disintegration is listed first: in all 17 traced fights the Agent took it at every offer (twice in 15 fights, three times in one, once in the fight that ended on turn 3). The boss note's model and two guides rank Disintegration last at the first two offers (`knowledge/bosses/KNOWLEDGE_DEMON_BOSS.md`, `[HYPOTHESIS]` and `[COMMUNITY]`). Eight of the ten lost fights ended on turn 6, the turn after the second offer.

The correction (`c`): at a card choice inside a fight the answers the host lists are candidates like any other action, each scored on six sampled worlds with the fight played to its end by the rule planner. The first option stays the first candidate, so a tie is resolved as before. One candidate per distinct set of card names, ten at most. Declining is never a candidate (section 6). A choose action is matched by card names in each sampled world. Nothing else changes: in the rollouts the planner still takes the first option at later choices.

- **H1 (the Knowledge Demon, wins):** on the Knowledge Demon situations the search with the choices searched wins more fights than the search that takes the first option.
- A condition and not a hypothesis: on other boss fights and on ordinary fights of all room types searching the choices costs nothing that can be seen (section 4).
- Described and not tested: which curse is taken at each offer; how often the search's answer is another one than the first option, by kind of choice.

Choices made before the run and not tuned on it: ten candidates at most; declining left out; no rule for the curse (the note's choice rule comes from a model that fails calibration for this boss, so the search decides and the rule stays a hypothesis); the rollouts' own choices unchanged (a planner rule for choices would be a second change).

## 2. Runs
- **Set D:** `data/sim/boss-replay-4-d.json`, the 59 Knowledge Demon situations of run benchmarks 16 (42, all four arms) and 17 (17, both arms), A0; 35 were won in the runs. Sample indexes 0, 1 and 2 (fight seed 7000000 + 10 × situation + index): 177 fights an arm. Run benchmark 17's 17 situations are the ones trace sweep 2 replayed (fight seeds 7200000 + index) and where the hypothesis comes from; run benchmark 16's 42 are being replayed by trace sweep 3 with the first option taken (seeds 7400000 + index; `reports/phase9/run-bench-17.md` section 6), not read when this was written. No fight seed of those sweeps is used here.
- **Set O:** `data/sim/boss-replay-4-o.json`, the 93 other boss situations of run benchmark 17 (act 1: Ceremonial Beast 18, The Kin 22, Vantom 12; act 2: Kaiser Crab 18, The Insatiable 8; act 3: Test Subject 8, Queen 4, Aeonglass 3); 62 were won in the runs. Sample index 0.
- **Set B:** `data/sim/benchmark-v1.json` (60 fights: 30 hallway, 20 elite, 10 boss), sample index 3 (0 and 1 were played by earlier comparisons; 2 was registered for boss replay 3's Set B, which was not played).
- Arms, as the runs' search plays each room type, with the first option taken and with the choices searched: in boss and elite rooms `mcw6paf` and `mcw6pafc`; in hallway rooms `mcw6pf` and `mcw6pfc` (`tools/learn/bench.py`: wide candidates, six worlds, potions at the room's price, every usable potion a candidate in boss and elite rooms, the forms to come counted in the value of a lost rollout; the trailing `c` searches the choices). Both arms play each fight with the same sample seed.
- Each fight is started fresh from its spec. Host: the Release5 build. Order: D, O, B. Four workers at the lowest priority, beside run benchmark 20's last two seeds and then beside run benchmark 19's second sitting. No deadline: every fight is played.
- Tested before registration: unit cases (`tools/tests/test_sim.py`, `test_selfplay.py`, `test_choices_compare.py`); a probe of the host at the three curse offers of one fight (every listed answer is accepted; the options are the same after a restore and a resample); four fights outside every set above with both arms (`data/sim/boss-fights-rb9.json`, sample index 7); and one traced fight of a Set D situation with a seed outside the set (section 6).

## 3. Policies
- `mcw6paf`, `mcw6pf`: the fight search as the run benchmarks play it today (the first option at a card choice).
- `mcw6pafc`, `mcw6pfc`: the same with the answers to a card choice searched (`tools/sim.py SEARCH_CHOICES` on for the arm).

## 4. Metrics and tests
- **H1:** fights won per situation, the mean over its three sample seeds, on Set D: one-sided sign test at 0.05 over the situations whose two arms differ. Reported with it: fights won per arm (of 177) and by source benchmark, and the curse taken at each offer per arm.
- **Sets O and B:** fights won per arm, by encounter or room type; over the fights both arms win, the mean difference in HP left with a bootstrap 95% interval; over all fights the mean difference in priced value.
- Per arm and set (`tools/choices_compare.py`, from `choices` in the fight records): choices per fight, how many were searched, how many of those took another answer than the first option, by kind of choice; search errors; seconds per fight.
- A fight with a host error in either arm is left out of the paired tests and reported.
- **What follows.** Searching the choices becomes the default of the fight search for everything started afterwards if all of these hold: H1 holds; on Set O the arm with the choices searched wins at least as many fights as the arm without, less two at most; on Set B it wins at least as many, less one at most; and on Set B's fights that both arms win its mean HP left is not lower by more than 1.0. A run benchmark begun before that is finished with the setting it began with (`SIM_SEARCH_CHOICES=0`, as run benchmark 19 keeps `SIM_LOSS_FORMS=0`). Then the next free run-benchmark slot measures in whole runs what it is worth in wins. If H1 holds and a condition of Set O or Set B does not, the option stays off in general and a version limited to the Knowledge Demon's curse is registered on its own. If H1 does not hold, the option stays off and the fights are traced for the reason (in a fight whose rollouts are all lost an answer is judged by the enemies' HP left at death, which may favour the curse that kills sooner but leaves the deck whole).

## 5. Results
### Set D, the Knowledge Demon (read 2026-11-23 09:25)
Played 08:08–09:24 (four workers at the lowest priority; code `93c1b3c`; `data/learn/bench/boss-replay-4-d`; `python3 -I tools/choices_compare.py --a mcw6paf --b mcw6pafc --specs data/sim/boss-replay-4-d.json data/learn/bench/boss-replay-4-d`). 177 fights an arm; 176 with both arms (one fight of the arm with the choices searched ended in a game exception, section 6).

| | First option (`mcw6paf`) | Choices searched (`mcw6pafc`) |
|---|---|---|
| **Fights won** | **106 of 176 (60%)** | **125 of 176 (71%)** |
| on run benchmark 16's 42 situations | 88 of 125 | 103 of 125 |
| on run benchmark 17's 17 situations | 18 of 51 | 22 of 51 |
| Card choices a fight | 3.2 | 3.4 |
| searched | 0 | 603 of 607 |
| another answer than the first option | 0 | 297 |
| Seconds a fight | 49 | 53 |

- **H1 holds.** Of the 59 situations the arm with the choices searched wins more of its three fights in 15 and fewer in 5; one-sided sign test p = 0.021.
- Where both arms win (100 fights) the arm with the choices searched keeps 5.1 HP more (bootstrap 95% 2.5 to 7.6). Priced value over all fights: +29.3 (17.4 to 42.1).
- **The curse.** With the first option taken: Disintegration at all 176 first offers, all 153 second offers and all 7 third offers. With the choices searched: first offer Mind Rot 105 and Disintegration 71; second offer Sloth 72 and Disintegration 91; third offer Waste Away 8 and Disintegration 27. So the search takes the other card at the first offer in three fights of five and still stacks Disintegration in many: the answer is judged on six worlds played out by a planner that takes Disintegration at the later offers. Fights won by the number of Disintegrations taken: none 26 of 37, one 67 of 90, two 31 of 48.
- **The other choices.** Of the 229 searched choices that are not the curse (the card Headbutt puts back, the card to exhaust or upgrade, a potion's cards) 112 took another answer than the first option.
- Lost fights end on turn 6 or 7 in 47 of 70 with the first option and in 35 of 51 with the choices searched.

### Set O, the other bosses (read 2026-11-23 11:26)
Played 09:24–10:27 (`data/learn/bench/boss-replay-4-o`; `python3 -I tools/choices_compare.py --a mcw6paf --b mcw6pafc --specs data/sim/boss-replay-4-o.json data/learn/bench/boss-replay-4-o`). 93 fights an arm, all with both arms; no error.

| | First option (`mcw6paf`) | Choices searched (`mcw6pafc`) |
|---|---|---|
| **Fights won** | **59 of 93 (63%)** | **65 of 93 (70%)** |
| act 1: Ceremonial Beast, The Kin, Vantom | 17 of 18, 16 of 22, 11 of 12 | 17 of 18, 20 of 22, 12 of 12 |
| act 2: Kaiser Crab, The Insatiable | 8 of 18, 6 of 8 | 8 of 18, 6 of 8 |
| act 3: Test Subject, Queen, Aeonglass | 1 of 8, 0 of 4, 0 of 3 | 1 of 8, 1 of 4, 0 of 3 |
| Card choices a fight | 1.1 | 1.1 |
| searched | 0 | 101 of 102 |
| another answer than the first option | 0 | 57 |
| Seconds a fight | 77 | 78 |

- The arm with the choices searched wins the fight in 6 situations where the first option loses it and loses none the first option wins (one-sided sign test p = 0.016, not a registered test). Where both win (59 fights) it keeps 2.2 HP more (bootstrap 95% 0.7 to 3.9); priced value over all fights +12.0 (−0.3 to +24.5).
- **The condition of Set O holds** (65 against 59; at least 57 was asked).

### Set B, the benchmark fights (read 2026-11-23 11:26)
Played 10:27–11:12, sample index 3 (`data/learn/bench/boss-replay-4-b-eb` with `mcw6paf` and `mcw6pafc`, `data/learn/bench/boss-replay-4-b-h` with `mcw6pf` and `mcw6pfc`). 60 fights an arm, all with both arms; no error.

| | First option | Choices searched |
|---|---|---|
| **Fights won, all 60** | **52** | **50** |
| boss rooms (10) | 5 | 4 |
| elite rooms (20) | 18 | 17 |
| hallway rooms (30) | 29 | 29 |
| Card choices: boss and elite rooms, hallway rooms | 38, 13 | 38 (37 searched, 17 another answer), 12 (12 searched, 9 another answer) |
| Seconds a fight: boss and elite rooms, hallway rooms | 89, 44 | 78, 46 |

- Four fights end differently. The arm with the choices searched loses three the first option wins (the Knowledge Demon, the Test Subject, the elite Mecha Knight) and wins one the first option loses (Vantom).
- Where both arms win (49 fights) its mean HP left is 0.35 lower (bootstrap 95% −1.4 to +0.6): the condition of 1.0 holds. In hallway rooms alone +0.3 (−0.4 to +1.1). Priced value over all fights −8.3 (−20.5 to +2.3).
- **The condition on fights won does not hold:** 50 against 52, where 51 at least was asked.

### What follows (2026-11-23 11:26)
H1 holds, the condition of Set O holds, the condition on Set B's HP holds, the condition on Set B's fights won fails by one fight. By section 4 **the option stays off in general**, and a version limited to the Knowledge Demon's curse is registered on its own (`reports/phase9/boss-replay-6.md`). `SIM_SEARCH_CHOICES` keeps its default of 0.

Over the three sets together the arm with the choices searched wins 240 of 329 fights against 217, and more of a situation's fights in 22 situations against fewer in 8. That is not a registered test and does not change the rule's answer: the guard was there for the fights the gain does not come from, and it is the guard that failed. The same registration gives the general option a second look on more fights of the kind that failed, with its conditions fixed before they are played.

## 6. Deviations and notes
- 2026-11-23 08:07, before the run. **Declining a choice is never a candidate.** The host lists "take no card" as a legal answer wherever the game's card selector is given a minimum of 0, and at a choose-a-card screen it is given 0 even where the game does not let the player skip: `KnowledgeDemon.ChooseCurse` calls `CardSelectCmd.FromChooseACardScreen` with `canSkip` false (read from the game's code with `tools/asm`), and the host listed declining at all three curse offers and accepted it. A search that could decline would use a move the game does not have. Whether the other screens can be skipped in the game was not checked; none of them needs to be for this comparison. The host's list is noted as a fidelity gap of the simulator (`docs/simulator-integrity.md`); nothing played so far used it, because the first option was always taken.
- 2026-11-23 08:07, before the run. **One fight of a Set D situation was played with the choices searched while the code was tested** (run benchmark 17's Knowledge Demon situation 6, fight seed 7200006, the seed of trace sweep 2, with `tools/fight_trace.py --choices on`): Mind Rot at the first offer (−316 against −341 for Disintegration, every rollout lost), Disintegration at the second with 5 HP left; lost on turn 6 with 172 of 379 HP left on the boss, where the first-option search lost on turn 6 with 184 left. That seed is not in the set. In the four fights outside every set the arms won 1 and 2; neither is a result.
- 2026-11-23 08:12, a miscount in section 1, corrected here because the section is not edited after the start: of the ten Knowledge Demon fights lost in trace sweep 2, **seven** ended on turn 6 (two on turn 7, one on turn 3), not eight. Nothing registered depends on the figure.
- 2026-11-23 08:08, **started** (`data/learn/queue/boss-replay-4.sh`, Set D first, four workers at the lowest priority; code `93c1b3c`).
- 2026-11-23 09:25, Set D: one fight was left out of the paired figures (situation 2, sample index 2). In the arm with the choices searched a step ended in a game exception (`NullReferenceException` in `ActionQueueSynchronizer.GetHookActionForId`), the arm's only error in 177 fights; the first-option arm had none. One case does not say whether a searched answer led to it. It is looked for in Sets O and B, and the fight is traced if it shows again.
- 2026-11-23 09:25, a by-product of Set D for `reports/phase9/run-bench-17.md` (its section 6, 08:11): the first-option arm is the runs' own search, and its three replays of each situation win 88 of 126 fights on run benchmark 16's situations (70%; the runs won 29 of 42, 69%) and 18 of 51 on run benchmark 17's (35%; the runs won 6 of 17, 35%). The replays reproduce the runs in both, so trace sweep 3's 23 of 42 was a low draw of single fights, and the distance between the two benchmarks at this boss lies in the situations they reached it with.
- 2026-11-23 11:26, the two fights of Set B the arm with the choices searched lost early, traced with the same fight seeds (`tools/fight_trace.py --choices on`; the traces replay the recorded fights to the same turn and the same HP left on the enemy). **Mecha Knight** (fight 48, seed 7000483): the potion Droplet of Precognition offers the 30 cards of the draw pile on turn 1; the first option is Bash+, the search took Defend out of ten candidates and the fight was lost on turn 4 with 73 of 300 HP left on the enemy, where the first-option arm won on turn 5 with 44 HP. **Test Subject** (fight 43, seed 7000433): Secret Technique+ offers 16 skills on turn 1; the first option is Defend+, the search took Forgotten Ritual out of ten candidates and the fight was lost on turn 3 in the first form, where the first-option arm won with 64 HP. In both traces every candidate of every decision of the first turn is lost in all its rollouts, the answers to the choice among them (−196 to −265 at the potion, −374 to −462 at Secret Technique+). So in both the answer was picked among rollouts that are all lost, by the enemies' HP left at death, which is the case section 4 names; and both fights are ones the rollouts call lost from the first hand while the search itself can win them (in trace sweep 2, 5 of the 58 fights whose first turn had every candidate lost were won). Two fights do not make a rule; they are a lead for the value a lost rollout gets, not for the choices.
- 2026-11-23 11:26, the third fight of Set B lost by the arm with the choices searched is the Knowledge Demon (fight 22): Impervious in place of Flame Barrier at an offer of three cards, Mind Rot, Sloth and then Disintegration; lost on turn 10 with 58 of 399 HP left on the boss, where the first-option arm took Disintegration twice and won on turn 8 with 20 HP. The fight it won and the first option lost is Vantom (fight 1): the card taken from the hand to be exhausted was a Wound where the first option gave up Defend+.
- 2026-11-23 11:26, Set D once more: one more fight of the arm with the choices searched had a note that the 09:25 reading did not list (situation 1, sample index 2: won after two restarts of the host). It is counted, as a restarted fight is in every fight benchmark. The game exception of Set D did not show again in Sets O and B (153 fights of the arm, none with an error).
