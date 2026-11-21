# Comparison: map routes chosen by sampled rollouts (run benchmark 4)

Written before the run (decision 0004 steps 3–4, ML-10), 2026-11-21 at 03:33, after run benchmark 2's results and before run benchmark 3's. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** choosing each map move by sampled rollouts (`rpath`) reaches more floors than choosing it by the route planner (`path`) when search plays every fight.

Why: in run benchmark 2 the route planner (`tools/path.py`, room models from the Player's history) was the only rule that helped (+2.7 floors, p = 0.002). Rollouts judge each next point by what follows it in re-sampled futures, using the actual deck, HP and map instead of averaged room models.

## 2. Runs
- 60 seeds (`RB004` + index 00000–00059), Ironclad, Ascension 5, whole runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- Combat in both arms: `mcw6` through the save-based fight rebuild, as in run benchmarks 2 and 3.
- Rollouts (`tools/run_eval.py`): at each map choice with two or more next points (the boss excepted), every next point is evaluated on the same 6 sampled futures (common random numbers): the run is rebuilt in an evaluation host from its room-entry save plus the actions since with the future re-sampled (`run_from_save` with a sample seed), the move taken, and the run played on to the end of the act or death by the `path` policy with the rule planner fighting. Rollout value: floors climbed, plus 5 and 5 times the HP fraction left if the act's boss is beaten. The best mean value is taken; exact ties go to the route planner's choice.
- Host: the Release build checked before run benchmark 3 (no host change in between).
- Starts when run benchmark 3 has finished. Stopping rule, fixed in advance and independent of outcomes: 6 workers take seeds in index order (worker w: seeds w, w+6, …; each seed's two policies one after another). At 09:45 unfinished runs stop; the analysis uses the seeds for which both policies finished.

## 3. Policies
- `path`: first card of each card reward, leave shops, rest below 60% HP else smith the first card (the `base` rules, which beat the hand-made deck rules in run benchmark 2), and every map move before the boss by the route planner.
- `rpath`: the same, except that map moves are chosen by rollouts as above (the route planner only breaks exact ties and decides if every rollout fails).
- Both: non-Ancient events by the Player's most frequent choice; Neow, Ancients, boss relics and potion rewards by the first option.

## 4. Metrics and test
- Primary: floor reached. Secondary: act 1 and act 2 bosses beaten, wins, where runs die, elites fought, how often rollouts disagree with the route planner, seconds per run.
- Test: paired by seed, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval (`tools/run_bench.py --report … --baseline path`).
- What follows: if H1 holds, routes move to rollouts in the run policy; with run benchmark 3 this decides whether rollout evaluation becomes the general method for strategic decisions. If not, the route planner stays the default.

## 5. Results
Run 2026-11-21, 05:20–06:27 (`data/learn/runs/run-bench-4/manifest.json`; 3993 s wall, 6 workers, all exited cleanly; all 60 seeds finished before the deadline). Code: the run started from `1cd8c0d`; the manifest records `b10dc5c`, the commit when it ended, and the changes in between (the `rcard` component, documents) do not touch `path`, `rpath`, the rollout evaluator or the Release host. Report: `python3 -I tools/run_bench.py --report data/learn/runs/run-bench-4 --baseline path`.

| Policy | Runs | Mean floor | Median floor | Reached the act 1 boss | Beat it | Reached the act 2 boss | Beat it | Won | Elites fought per run | Final deck (mean cards) | Seconds per run |
|---|---|---|---|---|---|---|---|---|---|---|---|
| path | 60 | 18.08 | 17 | 46 | 14 | 5 | 0 | 0 | 1.83 | 20.0 | 146 |
| rpath | 60 | 19.17 | 17 | 55 | 13 | 5 | 0 | 0 | 0.97 | 20.9 | 178 |

| Pair (B − A), floors | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| rpath − path (H1) | 60 | +1.08 | -0.50 to 2.65 | 22 | 11 | 27 | 0.040 |

- **H1** (map moves by sampled rollouts reach more floors than by the route planner): p = 0.040, mean +1.08 floors: **holds by the registered test, narrowly**; the bootstrap interval includes zero.

Act 1 bosses (won / fought): `path` Ceremonial Beast 5/13, The Kin 4/17, Vantom 5/16; `rpath` Ceremonial Beast 4/16, The Kin 4/20, Vantom 5/19. Act 2 bosses: `path` 0/5, `rpath` 0/5.

Where runs die (room type of the fatal fight): `path` bosses 37, elites 18, hallways 5; `rpath` bosses 47, elites 5, hallways 8. Last floor reached: floors 7–16 in 14 runs against 5, the act 1 boss floor in 32 against 42, beyond it in 14 against 13. HP lost per won fight: hallways 3.4 / 4.0, elites 26.8 / 23.9, bosses 40.0 / 42.7.

Rollout decisions: 393 map choices; the rollouts chose differently from the route planner in 158 (40%). Rollouts cost 1.2 times the seconds per run (178 against 146).

Search in the fights: 18,492 searched moves; fallbacks 9 in `path` (9 rebuild errors) and 56 in `rpath` (55 and 1 mismatch), 0.35% overall, from the same two host cases as in run benchmark 3 (a fight-start choice the save-based rebuild does not reproduce, seed `RB00400055`; fights the driver does not record as room fights, most likely started by events, seed `RB00400058`).

**Verdict: H1 holds narrowly, and the gain is of a particular kind.** Route rollouts gain about one floor, all of it by getting more runs to the act 1 boss (55 against 46): they fight about half as many elites (0.97 per run against 1.83) and die in elites far less often (5 against 18). They do not beat the boss more often (13 against 14), so runs mostly stop one floor later, at the boss. The likely reason is in the rollouts: the rule planner fights there, and it beats act bosses and elites much less often than the search that fights in the real run, so rollout values reward surviving to the boss floor and see little of what elites give for the boss fight (relics, upgrades, cards). Run benchmark 3's card rollouts used the same rollout fighter and still gained 6.6 floors, which suggests card choices are less sensitive to it than routes.

By the rule in section 4, routes move to rollouts in the run policy. With the interval including zero and no gain in boss wins, the next route test should change the rollout value or fighter before more weight is put on it: a value that credits boss readiness (for example a fight model of the act boss on the deck reached), or search in place of the planner for elites and bosses inside rollouts.

## 6. Deviations and notes
- 2026-11-21 04:05, during the run, a note on the rollouts (no change to the run): the run sampler of the Release build used here can put an encounter already met in the act back into a sampled future (9% of future encounters in a check of eight runs; the real game repeats none). Rollout worlds are therefore slightly off, the same for every option and arm. Fixed afterwards in `sim/RunSampler.cs` (0% after the fix), not used by this run.
