# Measurement: act 3 boss fights, the Player's situations and the Agent's, played by the runs' fight search (boss replay 2)

Written before the run (ML-10), 2026-11-22 at 14:55, after the results of run benchmark 16 (which prompted it) and before any fight of this replay is played. Two single fights of run benchmark 16 (one Test Subject, one Queen) were being replayed with a turn-by-turn trace while this was written, to see how such fights are lost; their traces had not been read (section 6 records what they showed). Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Question and hypothesis
On the corrected simulator the act 3 boss ends more of the Agent's runs than anything else: 8 of 42 act 3 boss fights won at A0 (Queen 0 of 9, Test Subject 3 of 24, Aeonglass 5 of 9; run benchmark 16, section 5), where the Player won 13 of the 15 act 3 boss fights of his recorded Ironclad runs, at Ascensions 1 to 10. The Agent arrives with about the Player's deck size, HP, relics and potions. Either the decks are too weak for these fights, or the fight search plays these fights badly, or both. This replay separates the two by giving the same search the Player's decks.

- **H1:** at A0, the runs' fight search wins a larger share of the Player's act 3 boss situations than of the Agent's own.
- A second question, described and not tested: at the ascensions the Player played them, how many of his 15 situations does the search win, beside his 13?

What is known before the run, from recorded data only (no fight played): the decks differ in kind, not in size.

| At the act 3 boss (means) | Agent, run benchmark 16 (42) | Player (15) |
|---|---|---|
| Deck size | 33.1 | 32.6 |
| Strikes and Defends | 6.9 | 7.5 |
| Upgraded cards | 13.2 | 18.0 |
| Attacks | 17.5 | 10.9 |
| Skills | 10.8 | 16.1 |
| Powers | 3.8 | 3.8 |
| Cards that give energy | 0.5 | 1.8 |
| Cards that draw | 2.9 | 2.8 |
| Rare cards | 3.7 | 5.9 |
| Cards costing 2 or more | 7.4 | 4.9 |
| Relics | 13.8 | 14.9 |
| HP at the start, share of the maximum | 73% | 72% |
| Potions | 1.7 | 2.1 |

`[OBS]` for the Agent, `[PLAYER-DATA]` for the Player (`data/learn/specs/fight-specs-ironclad.json`, exam seeds excluded; card types and tags from `tools/deck_check.py`). The Agent's decks hold seven more attacks and five fewer skills, a quarter of the energy cards, two fewer rare cards and five fewer upgrades. By the share of decks that hold a card, the Player's against the Agent's: Armaments 80% against 26%, Dominate 66% against 14%, Evil Eye 60% against 14%, True Grit 60% against 26%, Bloodletting 53% against none, Vicious 46% against 9%, Fiend Fire 40% against 7%, Infernal Blade 40% against 9%, Feel No Pain 40% against 9%; and the other way, Anger none against 66%, Blood Wall 13% against 57%, Inflame 13% against 50%, Iron Wave none against 47%, Perfected Strike none against 47%, Taunt none against 45%, Thunderclap none against 42%, Setup Strike none against 40%, Headbutt 6% against 40%, Stomp none against 38%. A second thing known from the code: a lost rollout is valued at −100 minus the enemies' HP left (`tools/sim.py _value`), and the Test Subject has three bodies in turn (100 HP `[GAME]`, then 200 and 300 `[COMMUNITY]`, `knowledge/bosses/TEST_SUBJECT_BOSS.md`), so a rollout that dies late in the second phase is valued above one that reaches the third; whether that costs fights is not known.

## 2. Runs
- **Set P0:** the Player's 15 act 3 boss situations (every act 3 boss fight of `fight-specs-ironclad.json`: Queen 6, Test Subject 4, Aeonglass 5; deck, relics, potions, HP and max HP before the fight), with the ascension set to 0 (`data/sim/player-act3-boss-a0.json`). Three sample seeds each: 45 fights.
- **Set P:** the same 15 at the ascension recorded (1 to 10; `data/sim/player-act3-boss.json`). Three sample seeds each: 45 fights.
- **Set G:** the Agent's 42 act 3 boss situations of run benchmark 16, all four arms, A0 (`tools/boss_specs.py data/learn/runs/run-bench-16 --act 3`, `data/sim/boss-fights-rb16-act3.json`; 8 won in the runs). One sample seed each: 42 fights. Its purpose is the check that a fight started from its spec is won about as often as the same fight was in the run.
- Each fight is started fresh from its spec (`tools/learn/bench.py --benchmark`), so the hidden state differs from the original fight.
- One arm: `mcw6pa`, the search the run benchmarks use in a boss room (every distinct legal move, six sampled worlds each, rollouts to the end of the fight by the rule planner, every usable potion a candidate at the boss price).
- Host: the Release5 build. Four workers at low priority, started when run benchmark 19 has ended, beside run benchmark 17; fight batch b0 stays paused until this replay is done. No deadline: every fight is played. Order: P0, P, G.
- Known limits of the Player's situations (recorded in the spec file): no enchantments, relics removed before the fight missing, potions capped at 3, source runs on v0.107.1 and played here on v0.111.1 (the Torch Head Amalgam's first move is stronger there). Three of the 15 are in `benchmark-v1`.

## 3. Policies
- As in `tools/learn/bench.py`; nothing is changed for this replay.

## 4. Metrics and test
- **H1:** fights won of the first sample seed, Set P0 (15) against the Agent's situations in their runs (8 of 42): one-sided Fisher exact test at 0.05. Reported with it: the share won over all three seeds of P0 with a bootstrap 95% interval over situations, and Set G's replayed share beside the runs' 8 of 42.
- The second question: per situation, the Player's result and the search's wins of three in Set P; no test (15 situations, another game version).
- Secondary, per set and boss: fights won, turns, HP left after a win, enemies' HP left after a loss (for the Test Subject this is the HP of the body then alive), potions used, seconds per decision; in Set G, agreement with the run's outcome by situation.
- **What follows.** If the search wins at least 70% of P0 and H1 holds: the decks are the main cause, and the next registered runs are about card choice for long fights (what a card rollout is played to and judged by, the number of upgrades), not the fight search. If it wins at most 40% of P0: the fight play on act 3 bosses is a main cause, and the search comes first (the value of a lost rollout across the Test Subject's bodies, the rollout policy under the Queen's debuffs), tried on these three sets as a fight benchmark before any whole run. Between the two: both, the search first because a fight benchmark is cheaper than a run benchmark.

## 5. Results
Pending.

## 6. Deviations and notes
