# Comparison: the decks built with the card tiers against the last boss (boss replay 5)

Written before the run (ML-10, decision 0006 item 3), 2026-11-23 at 09:01, after run benchmark 20 was read (`reports/phase9/run-bench-20.md` section 5) and before any fight of this comparison is played. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Question and hypothesis
In run benchmark 20 the two arms that used the community card tiers in card rewards beat the act 3 boss in 7 of 31 fights (3 of 16 as a tie-break, 4 of 15 as a hard filter) and the unchanged policy `C*` in 0 of 16. The run's registered measure was floors, which cannot tell a run won from a run lost to the last boss, and its rule kept the tiers out. The Player's reading of the run (2026-11-23) is that this row is the measure that counts, and that the unchanged policy is the worst of the three.

One fight a situation is thin ground for that. Each of the 47 fights was played once, and over three benchmarks `C*` has beaten the last boss in 5 of 39 fights (4 of 14 in run benchmark 16, 1 of 9 in run benchmark 17, 0 of 16 in run benchmark 20), so its level is not zero and this run's seeds were below it. The question here is narrow: **are the situations that the arms with the tiers bring to the last boss better than the unchanged policy's, or were seven wins against none the luck of single fights?** Every situation is played five times with the fight search of the runs, and the arms are compared on the seeds where both reached the boss.

- **H1 (the last boss, fights won):** on the seeds of run benchmark 20 where `C*` and at least one arm with the tiers reached the act 3 boss, the situations of the arms with the tiers win a larger share of their fights than `C*`'s situation.

Not asked here: what the tiers cost before the last boss (in run benchmark 20 the two arms beat the act 2 boss in 34 of 52 fights against 20 of 27), and what they are worth in runs won. Those need whole runs (section 4).

## 2. Runs
- **The set:** `data/sim/boss-replay-5.json`, the 47 act 3 boss situations of run benchmark 20 (`tools/boss_specs.py data/learn/runs/run-bench-20 --act 3`): 16 of `C*`, 16 of `C*+ctb`, 15 of `C*+cth`; Aeonglass 17, Queen 16, Test Subject 14; 7 won in the runs. A situation is the deck, relics, potions and HP a run arrived with. On 15 seeds both `C*` and at least one arm with the tiers reached the boss (all three on 9), and on every seed the arms met the same boss.
- Sample indexes 0 to 4 (fight seed 7000000 + 10 × situation + index): 235 fights.
- Arm: `mcw6paf`, the fight search as run benchmark 20's runs played boss rooms (`tools/learn/bench.py`: wide candidates, six worlds, potions at the room's price, every usable potion a candidate, the forms to come counted in the value of a lost rollout, the first option at a card choice). One arm: the comparison is between situations, not between searches.
- Each fight is started fresh from its spec. Host: the Release5 build. Four workers at the lowest priority, after boss replay 4, beside run benchmark 19's second sitting and what follows it. No deadline: every fight is played.

## 3. Policies
The situations come from `C*` = `rcard+rpath+pot+smith+rshop2+ropt+bshop`, `C*+ctb` and `C*+cth` as run benchmark 20 defines them. Nothing is played by those policies here; the fights are played by `mcw6paf`.

## 4. Metrics and tests
- A situation's value is the share of its five fights won. **H1:** per seed with a situation of `C*` and of at least one arm with the tiers, the mean value of the arms with the tiers against the value of `C*`: one-sided sign test at 0.05 over the seeds whose two values differ (`tools/origin_compare.py --control <C*>`).
- Reported with it: fights won per arm of origin (of 80, 80 and 75) and by boss; each arm with the tiers against `C*` alone, the same test (no claim for one of them without it); situations with at least one fight won; the replays beside the runs' own outcomes of these fights.
- A fight with a host error is left out and reported.
- **What follows.** If H1 holds: the component whose situations win the larger share of their fights goes into the next run benchmark against `C*`, registered with **runs won** as its measure and the act 2 boss as a reported guard. It does not enter the stack on this comparison alone, because this says nothing about what the tiers cost before the last boss. If H1 does not hold: the seven wins of run benchmark 20 are read as the luck of single fights, the tiers stay out, and they are not tested again without a new reason.

## 5. Results
Pending.

## 6. Deviations and notes
- 2026-11-23 09:01, before the run: the reader's arithmetic is checked on made-up records (`tools/tests/test_origin_compare.py`). No fight of the set has been played outside run benchmark 20's runs.
