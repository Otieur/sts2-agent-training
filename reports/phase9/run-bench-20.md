# Comparison: community card tiers as a prior in card rewards, as a tie-break and as a hard filter, at Ascension 0 (run benchmark 20)

Written before the run (decision 0006 item 5, ML-10), 2026-11-22 at 15:45, after the results of run benchmark 16 and before any result of run benchmarks 19 and 17 and of boss replay 2. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypotheses
- **H1 (tie-break, floors):** taking, among the card-reward options whose rollout values are within one point of the best, the one the tier table rates highest (`ctb`) reaches more floors than taking the best rollout value.
- **H2 (hard filter, floors):** from act 2 on, leaving the cards of the lowest tier (defined below) out of card rewards altogether (`cth`) reaches more floors than taking the best rollout value.
- **H3, H4 (wins):** each wins more runs.

Why: at the act 3 boss the Agent's decks hold 17.5 attacks against the Player's 10.9 and 10.8 skills against 16.1, and win 8 of 42 fights where the Player won 13 of 15 (`reports/phase9/boss-replay-2.md` section 1). A card rollout is played to the end of the act by the rule planner, so it rewards what helps the next hallway fights, and the margins it decides by are small beside what six futures can tell apart (a point of rollout value is one floor climbed, or a fifth of the HP kept through a boss beaten).

The prior is the project's community tier table (`knowledge/community/ironclad-tiers.md`, `[COMMUNITY]`, 83 rated Ironclad cards), read with care, because it is not unanimous: its sources are two or more tiers apart on 29 cards, and it puts in its lowest tier cards the Player wins with (Evil Eye is in 9 of his 15 act 3 boss decks, Tremble in 10, Molten Fist in 11; the Player asked on 2026-11-22 whether the tiers were used, and the look at where table and Player disagree followed from that, before this registration was committed). So a card counts as **lowest tier** here only where the views agree: consensus tier D, its sources less than two tiers apart, and the Player's own picking of it in the lowest fifth or not recorded (`[PLAYER-DATA]`, the table's habit column). That leaves 15 cards: Anger, Blood Wall, Cinder, Havoc, Hemokinesis, Inflame, Iron Wave, Perfected Strike, Rampage, Setup Strike, Spite, Sword Boomerang, Tank, Thunderclap, Twin Strike. The other 12 cards of consensus tier D (Bludgeon, Breakthrough, Dismantle, Evil Eye, Fight Me, Headbutt, Infernal Blade, Molten Fist, Primal Force, Tremble, Unrelenting, Whirlwind) are scored as unrated cards.

By that list a deck at the act 3 boss holds 7.1 lowest-tier cards in the Agent's hands and 1.5 in the Player's. In run benchmark 16 the rollouts took such a card in 256 of 925 card decisions in act 1, 167 of 679 in act 2 and 80 of 308 in act 3; its rollout value was within one point of an option that is not of the lowest tier (another card or skipping) in 128, 113 and 77 of them, and the median margin was 1.00, 0.59 and 0.00 points. The tiers are other players' judgement of whole runs, which is why they are tried as a prior, in two strengths, and adopted only by this run's result.

## 2. Runs
- 30 new seeds (`RB020` + index 00000–00029), Ironclad, **Ascension 0**, whole new runs in the simulator (`tools/run_bench.py`). Three policies play every seed.
- `C*`: the stack after run benchmark 17 by that registration's rule (`data/learn/queue/stack3.py after-bc`), fixed by the queue script when this run starts. Arms: `C*`, `C*+ctb`, `C*+cth`.
- `ctb` (`tools/run_bench.py`): at a card reward decided by rollouts, the options whose mean rollout value is within `CARD_TIER_MARGIN` = 1.0 of the best are tied, and the one with the highest tier score is taken (the table's consensus score; 2.4 for a card the table does not rate and for the 12 disputed cards of consensus tier D; skipping counts 2.0, above the 15 lowest-tier cards and below every other card); among equal scores the higher rollout value.
- `cth`: at a card reward from act 2 on, the 15 lowest-tier cards are not candidates; the rollouts decide among the rest and skipping; if every card offered is of that tier the reward is skipped without rollouts. Act 1 is unchanged.
- Neither component acts inside rollouts (there the first card of a reward is taken, as before), so all three arms' rollouts are played by the same rules.
- Combat in all arms: `mcw6` in every fight, `--fight-rebuild save+run`; the value of a lost rollout as boss replay 2 leaves it before this run starts (`tools/sim.py LOSS_COUNTS_FORMS`; the same in all arms; section 6 records it). Host: the Release5 build. 9 workers claim seeds in index order (`--dynamic`). Stopping rule: unfinished runs stop 7 hours after the start. The analysis uses the seeds for which all three policies finished.
- Tested before registration (development copy): the choice of each component on made-up rewards (a lowest-tier card best by 0.4 with an A-tier card on offer; the same with the A-tier card 3 points behind; only lowest-tier cards with skipping close; an unrated card best; skipping far behind), and one seed outside every benchmark with planner fights (section 6).

## 3. Policies
- `C*`: as it stands after run benchmark 17.
- `C*+ctb`, `C*+cth`: the same with the component in card rewards.

## 4. Metrics and tests
- H1 and H2: floors reached, `C*+ctb` and `C*+cth` each against `C*` paired by seed: one-sided sign test at 0.05, with the mean difference and a bootstrap 95% interval. H3 and H4: wins, one-sided exact sign test at 0.05 on the seeds where the two differ; wins per arm with Wilson intervals (`tools/run_details.py --wins-vs`). The two components are two answers to one question; no correction is applied, and a claim for either needs its own test.
- Secondary: act bosses reached and beaten per arm, by boss; at each boss fight's start the deck size, the attacks, skills and powers, the cards per consensus tier, upgrades, relics and HP; card rewards skipped per run; how often `ctb` found a tie and changed the choice (`ctb_ties`, `ctb_changed`) and how many cards `cth` left out and how many rewards it skipped (`cth_dropped`, `cth_skips`); where runs die; seconds per run.
- The check that each arm's rollouts were played with its own rules: every recorded decision names the rollout policy of `C*` (the components are not part of it), in all three arms (`tools/run_details.py --decisions`). Rollouts that failed are reported per arm.
- What follows, the stack that runs next: of `ctb` and `cth`, the one with the larger mean floor difference against `C*` enters if that difference is positive and its arm does not win fewer runs than `C*`; otherwise neither.

## 5. Results
Run 2026-11-23 02:52 to 08:32 (host Release5, code `a248ed9`, nine workers, 20,417 s). All 30 seeds were finished by all three arms, 80 minutes before the deadline. `C*` = `rcard+rpath+pot+smith+rshop2+ropt+bshop`. Read with `python3 -I tools/run_bench.py --report data/learn/runs/run-bench-20 --baseline <C*>`, `tools/run_details.py data/learn/runs/run-bench-20 --wins-vs <C*>` and `--decisions`.

| | `C*` | `C*+ctb` | `C*+cth` |
|---|---|---|---|
| Floors reached, mean (median) | 41.13 (48) | 40.20 (48) | 39.30 (47) |
| **Runs won** (Wilson 95%) | **0 of 30** (0–11%) | **3 of 30** (4–26%) | **4 of 30** (5–30%) |
| Act 1 boss, beaten of reached | 28 of 30 | 28 of 30 | 28 of 30 |
| Act 2 boss | 20 of 27 | 18 of 26 | 16 of 26 |
| Act 3 boss | 0 of 16 | 3 of 16 | 4 of 15 |
| Elites fought a run | 1.50 | 1.23 | 1.60 |
| Card rewards skipped a run | 3.5 | 2.4 | 3.9 |
| Seconds a run | 1,616 | 1,427 | 1,442 |

- **H1 (tie-break, floors): does not hold.** −0.93 floors against `C*` (bootstrap 95% −4.5 to 2.4); 7 seeds better, 8 worse, 15 equal; one-sided sign test p = 0.70.
- **H2 (hard filter, floors): does not hold.** −1.83 floors (−4.2 to 0.6); 3 better, 8 worse, 19 equal; p = 0.97.
- **H3 and H4 (wins): do not hold at 0.05.** `C*+ctb` won 3 runs and `C*` none (seeds 00004, 00024, 00026; exact sign test p = 0.125). `C*+cth` won 4 and `C*` none (seeds 00007, 00008, 00016, 00024; p = 0.0625).
- **What follows by the rule of section 4:** neither component enters, because both mean floor differences are negative (`data/learn/queue/stack3.py after-ct` gives the unchanged stack). The stack stays `rcard+rpath+pot+smith+rshop2+ropt+bshop`.

**What the floors do not show.** A run that beats the last boss ends on floor 48, and so does a run that loses to it. In three of `C*+ctb`'s 15 equal seeds and in three of `C*+cth`'s 19 the arm with the tiers won the run and `C*` lost it on the same floor. The floors the two arms lose are lost at the act 2 boss, where a run ends on floor 33:

| Boss fights won | `C*` | `C*+ctb` | `C*+cth` |
|---|---|---|---|
| Act 2: Kaiser Crab | 6 of 7 | 4 of 8 | 3 of 7 |
| Act 2: Knowledge Demon | 6 of 10 | 7 of 9 | 4 of 10 |
| Act 2: The Insatiable | 8 of 10 | 7 of 9 | 9 of 9 |
| Act 3: Aeonglass | 0 of 6 | 2 of 6 | 2 of 5 |
| Act 3: Queen | 0 of 5 | 0 of 6 | 1 of 5 |
| Act 3: Test Subject | 0 of 5 | 1 of 4 | 1 of 5 |

The arms with the tiers lose a little more often at the act 2 boss (34 of 52 against 20 of 27) and are the only ones that beat the act 3 boss: 7 fights of 31 against 0 of 16. That comparison was not registered as a test (a one-sided Fisher exact test would give p = 0.04) and is a description. The same holds for the wins taken together: 6 of the 30 seeds were won by an arm with the tiers and none by `C*`.

**The decks.** The tiers moved the decks toward the Player's (10.9 attacks, 16.1 skills and 1.5 lowest-tier cards at the act 3 boss, `reports/phase9/boss-replay-2.md`): fewer attacks, more skills and powers, half the lowest-tier cards. `cth` acts from act 2 on, so its decks are `C*`'s through act 1.

| At the boss of | Arm | Cards | Attacks | Skills | Powers | Lowest-tier cards | Upgraded | Relics | HP |
|---|---|---|---|---|---|---|---|---|---|
| Act 2 | `C*` | 26.5 | 15.7 | 8.5 | 1.8 | 5.7 | 8.0 | 8.4 | 72% |
| | `C*+ctb` | 27.4 | 14.0 | 10.3 | 2.8 | 3.0 | 7.8 | 8.9 | 71% |
| | `C*+cth` | 26.5 | 14.7 | 9.3 | 2.2 | 4.0 | 7.9 | 8.4 | 70% |
| Act 3 | `C*` | 32.2 | 18.7 | 10.4 | 2.4 | 7.1 | 13.3 | 13.1 | 64% |
| | `C*+ctb` | 33.1 | 16.5 | 12.4 | 3.6 | 3.4 | 13.9 | 13.5 | 64% |
| | `C*+cth` | 32.8 | 17.3 | 12.0 | 2.9 | 3.7 | 12.1 | 12.8 | 71% |

**The components at work.** `ctb` found another option within a point of the best at 420 of its 569 card rewards and changed the choice at 243 (43%). `cth` left 273 cards out over its 551 card rewards and skipped 8 rewards whose cards were all of the lowest tier.

**Where runs end.** `C*`: act 3 boss 16, act 2 boss 7, act 3 hallway 3, act 1 boss 2, act 3 elite 1, act 2 hallway 1. `C*+ctb`: won 3, act 3 boss 13, act 2 boss 8, act 1 boss 2, act 2 hallway 2, act 3 elite 1, act 3 hallway 1. `C*+cth`: won 4, act 3 boss 11, act 2 boss 10, act 1 boss 2, act 2 hallway 2, act 3 hallway 1.

**Checks.** Every recorded decision's rollouts were played by `bshop+path+pot+smith` without the boss credit, in all three arms (1,504, 1,490 and 1,458 decisions). Rollouts that failed: 0, 16 and 1. Search errors: 1, 2 and 0, each a decision left to the planner; no mismatch, no host error, no fight given up. The longest seed (00011) took four hours for its three runs to the last boss, most of it in the rollouts of the strategic decisions; nothing was stuck.

**`C*` over three benchmarks.** The same policy won 4 of 26 runs in run benchmark 16, 1 of 26 in run benchmark 17 and 0 of 30 here: 5 of 82 (Wilson 95% 3–13%).

**What this leaves open.** The rule registered for this run decides by floors, and floors do not see a win at the last boss; decision 0005 makes wins the measure of the project. By that rule the tiers stay out. What the run describes, that the decks built with the tiers beat the last boss where `C*`'s do not and pay for it at the act 2 boss, is a lead and gets a registration of its own before anything enters the stack.

## 6. Deviations and notes
- 2026-11-22 16:25, before the start: the tests named in section 2. Unit cases on made-up rewards with the final list of 15, all as intended (`ctb` takes an A-tier card 0.4 behind a lowest-tier one and leaves it 3 behind; it skips when only lowest-tier cards are within a point of skipping; a disputed card is neither preferred to nor dropped for a lowest-tier one beyond its score of 2.4; `cth` drops the 15 from act 2 on, skips a reward of nothing else, and leaves act 1 alone). One seed outside every benchmark (`RB905`, planner fights, three arms): no host error; every decision's rollouts played by `path+pot+smith` in all three arms; `ctb` found 2 ties and changed 1 choice in a run of 3 card decisions that ended on floor 9; `cth` left out 13 cards and skipped 1 reward in 17 decisions. That seed was played with the score in its first form (the consensus alone, 27 cards in the lowest tier); the list of 15 was fixed afterwards, before this registration was committed, and is what the unit cases check. Floors of one seed with planner fights say nothing and are not read as a result.
- 2026-11-22 18:15, before the start: `C*` is still the stack after run benchmark 17 by that registration's rule; if run benchmark 19 has fewer than 15 finished seeds at its stopping rule, that stack is built on the stack after run benchmark 16 (run benchmark 19, section 6, 18:15).
- 2026-11-22 18:50, before the start: the value of a lost rollout in the fight search counts the forms to come in all three arms (`tools/sim.py LOSS_COUNTS_FORMS`, on by default since 18:50; `reports/phase9/boss-replay-2.md` section 6, 18:50). This is the state section 2 left to be recorded.
- 2026-11-23 02:52, **started** (deadline 09:52): run benchmark 17 ended with 26 seeds and the boss credit does not enter (its section 5: mean −0.58 floors, one win an arm), so `C*` is `rcard+rpath+pot+smith+rshop2+ropt+bshop` and the arms are `C*`, `C*+ctb` and `C*+cth`. The fight search counts the forms to come in the value of a lost rollout, leaves minions in it (boss replay 2, H3 not supported) and does not check the end of a turn against the planner (boss replay 3, not adopted), the same in all three arms; the manifest records the three settings. Nothing runs beside it: fight batch b0 stays paused, because a side job at the lowest priority was measured to take about a third of a run benchmark's processor time (`docs/overnight-log.md`, 2026-11-23 01:05). Of this run nothing is known. What is known of `C*` since the registration: on run benchmark 17's 26 seeds it reaches 36.42 floors and wins one run, and the act 2 boss ends more of its runs than the act 3 boss (10 against 8).
- 2026-11-23 08:32, **ended** with all 30 seeds, by the manifest (no worker was ended at the deadline). Section 5 was written from the tools named there. From 07:16 other work ran beside the run's last two seeds, on the cores its seven finished workers had freed: trace sweeps 2 and 3 (four fight loops at the lowest priority, 07:16–08:07) and boss replay 4 from 08:08 (four fight workers). Measured at 07:19, the two workers left kept 90% to 96% of a core each (97% to 99% before); both seeds were finished 80 minutes before the deadline, so the side work cost no seed. Only the number of seeds recorded and their ids were looked at before the end.
- 2026-11-23 08:40, a weakness of this registration's measure, noted for the next one: floors reached do not tell a run won from a run lost to the last boss (both end on floor 48), so H1, H2 and the stack rule could not see the one place where the arms differ most. A registration that is to decide what enters the stack names wins, or the last boss beaten, in its rule.
