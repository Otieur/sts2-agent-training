# Comparison: boss fights reached in run benchmark 9, replayed with more search (boss replay 1)

Written before the run (ML-10), 2026-11-21 at 10:09, after the results of run benchmarks 2–6 and before any result of run benchmarks 7–10. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** on the boss fights that whole runs at A10 reach, wide search with twice the sampled worlds (`mcw12`) gets a higher fight value than the search used in the runs (`mcw6`).

Why: at A10 the rollout policies reach the act 1 boss as often as the Player (80% of runs against 76%) but beat it in 10% of fights against 63% (run benchmark 6). Either the decks brought to the boss are too weak, or the fight play is. Replaying the same boss situations with more search separates the two in part: a clear gain from more search says the play is a limit; no gain, with search well ahead of the planner, says the search is saturated on these decks and the deck building is the limit.

## 2. Runs
- Fight set: every boss fight reached in run benchmark 9 (both arms), from the fight specs recorded at each boss fight's start (deck, relics, potions, HP, max HP, encounter, act, ascension; `tools/boss_specs.py data/learn/runs/run-bench-9 --out data/sim/boss-fights-rb9.json`). If run benchmark 9 did not finish, the boss fights of run benchmark 8 are used instead (A0; noted in section 6).
- Each fight is started fresh from its spec (`tools/learn/bench.py --benchmark`), so the hidden state (draw order, enemy rolls) differs from the run; each fight is played once per arm with the same sample seed (`--seeds 1`).
- Arms: `planner` (rule planner), `mcw6` (the run benchmarks' search), `mcw12` (the same wide candidates with 12 sampled worlds each).
- Host: the Release2 build (`sim/bin/Release2`). 6 workers claim fights one at a time. Starts when run benchmark 10 has finished (queue); no deadline (every fight is played).
- Smoke test before registration: one benchmark boss fight with `planner` and `mcw6` through `--benchmark` (plumbing only).

## 3. Policies
- As in `tools/learn/bench.py`; potions as the planner proposes them, in every arm.

## 4. Metrics and test
- Primary: fight value (HP left if won, otherwise −100 minus the enemies' HP left), paired by fight, `mcw12` against `mcw6`: one-sided sign test at 0.05 and the mean difference with a bootstrap 95% interval (`tools/learn/bench.py --report … --baseline mcw6`).
- Secondary: fights won per arm, by act and boss; `mcw6` against `planner`; how often `mcw6` here agrees with the run's outcome (`source.won_in_run`); seconds per decision.
- What follows: if H1 holds and `mcw12` wins clearly more boss fights, a larger search budget for boss fights (only bosses, normal rooms unchanged) is tested in whole runs next. If H1 does not hold and `mcw6` is well ahead of the planner, deck building for the boss fight is the target (the rollout value and fighter), not the fight search.

## 5. Results
Run 2026-11-21, 11:52–12:12 (`data/learn/bench/boss-replay-1/manifest.json`; 1206 s wall, 7 workers, all 98 fights played by all three arms, no errors). Fight set: the 98 boss fights reached in run benchmark 9 (`data/sim/boss-fights-rb9.json`: 94 act 1, 4 act 2; 14 won in the runs). Code `9f09c11` plus the queue's tools as committed in `a781c3a`. Report: `.venv-learn/bin/python -I tools/learn/bench.py --report data/learn/bench/boss-replay-1 --baseline mcw6`.

| Arm | Fights | Won | Mean value | Mean HP left if won | Seconds per decision |
|---|---|---|---|---|---|
| planner | 98 | 9 | −209.3 | 16.0 | 0.00 |
| mcw6 | 98 | 15 | −181.4 | 20.7 | 1.02 |
| mcw12 | 98 | 11 | −185.3 | 25.9 | 1.97 |

| Pair (B − A), fight value | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| mcw12 − mcw6 (H1) | 98 | −3.8 | −14.0 to 5.5 | 40 | 30 | 28 | 0.14 |
| mcw6 − planner | 98 | +27.9 | 17.3 to 39.7 | 72 | 23 | 3 | < 0.001 |

- **H1** (`mcw12` gets a higher fight value than `mcw6` on the boss fights that A10 runs reach): p = 0.14, mean −3.8: **does not hold**. Twice the sampled worlds wins 11 fights against 15.

Wins by boss (planner / `mcw6` / `mcw12` / in the run): Ceremonial Beast (36 fights) 5 / 8 / 8 / 8; The Kin (36) 2 / 5 / 2 / 4; Vantom (22) 2 / 2 / 1 / 2; act 2 bosses (4) none. By the arm of run benchmark 9 that brought the deck: `rcard+rpath` (47 fights) 2 / 6 / 2 / 5; `rcard+rpath+ropt` (51) 7 / 9 / 9 / 9.

Agreement with the runs: the replayed `mcw6` fight ends as the fight did in the run in 91 of 98 cases (15 wins replayed, 14 in the runs), although the replay starts from the recorded situation with a fresh draw order. A fight started from a recorded spec is a good stand-in for the fight in the run.

**Verdict: H1 does not hold, and search is well ahead of the planner (+28 value, 72 fights better against 23) while winning only 15 of 98: the search is not what limits these boss fights; the decks are.** By section 4, deck building for the boss fight is the target (what the deck holds when it arrives: upgrades, relics, potions, card quality), not a larger search budget. This agrees with the review of 2026-11-21 (the Agent arrives underpowered; with the Player's decks search does as well as the Player) and with the boss study of 2026-11-20 (24 worlds against 6 on the Player's boss fights: 4.2 wins of 10 against 3.5). A larger budget for bosses is not tested in runs now. The planner's 9 wins against search's 15 on the same decks also measures how much the rollouts' fighter underrates a deck at a boss.

Two things this replay does not show: potions were not used by any arm here (as in run benchmark 9), and all decks are those of policies that upgrade Strikes and never shop.

## 6. Deviations and notes
- 2026-11-21 10:14, before the run (stopping rule, not outcomes): 7 workers instead of 6 (fights are claimed one at a time, as registered). Reason: the Player asked for full use of the CPU and stopped the other project's processes, which frees memory; with fixed seeds the workers that finish early sit idle at the end of each benchmark (32% of the CPU idle in run benchmark 7's tail). Each seed is played the same whichever worker plays it (the same random generator per seed, search by fixed counts of sampled worlds), so the change affects only the wall time and, if the deadline stops the run, which seeds are cut, and neither depends on outcomes.
- 2026-11-21 10:20, before the run (queue order, not outcomes): the replay starts when run benchmark 9 has finished, before run benchmark 10, instead of after run benchmark 10. Reason: run benchmark 7 (finished 10:18) found that the boss credit does not move the act 1 boss wall at A10, so the direct examination of decks against fight play comes first. The fight set (run benchmark 9's boss fights) and everything else are unchanged.
