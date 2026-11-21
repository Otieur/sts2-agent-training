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
Pending.

## 6. Deviations and notes
- 2026-11-21 04:10, during the run, a note on the rollouts (no change to the run): the run sampler of the Release build used here can put an encounter already met in the act back into a sampled future (9% of future encounters in a check of eight runs; the real game repeats none). Rollout worlds are therefore slightly off, the same for every option and arm. Fixed afterwards in `sim/RunSampler.cs` (0% after the fix), not used by this run.
