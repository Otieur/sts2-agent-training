# Comparison: card rewards chosen by sampled rollouts (run benchmark 3)

Written before the run (decision 0004 steps 3–4, ML-10), 2026-11-21 at 02:21. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** choosing card rewards by sampled rollouts (`rdraft+shop+rest`) reaches more floors than choosing them by the draft scorer (`draft+shop+rest`) when search plays every fight.

Why: every deck-building rule so far is a hand-made score (`tools/draft.py`), never checked against outcomes; run benchmark 1 found it worse than taking the first card. Since 2026-11-21 a run can be copied at any decision point and played forward with its unseen future re-sampled (checked by `tools/sim.py runclone`; FP-16), so each option can be judged by what tends to follow it rather than by a score.

## 2. Runs
- 60 seeds (`RB003` + index 00000–00059), Ironclad, Ascension 5, whole runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- Combat in both arms: `mcw6` through the save-based fight rebuild, as in run benchmark 2.
- Rollouts (`tools/run_eval.py`): at each card reward, every card and skip is evaluated on the same 6 sampled futures (common random numbers): the run is rebuilt in an evaluation host from its room-entry save plus the actions since, the future re-sampled (`run_from_save` with a sample seed), the option taken, and the run played on to the end of the act or death by `draft+shop+rest` with the rule planner fighting. Rollout value: floors climbed, plus 5 and 5 times the HP fraction left if the act's boss is beaten. The option with the best mean value is taken; exact ties go to the scorer's choice.
- Host: Release build with run clones and the run sampler, rebuilt after run benchmark 2 has finished; checks before the run: clone, clone from saves, run clones and sampler (`sim.py runclone`), fair play, sandbox, fidelity. The run starts only if all pass.
- Stopping rule, fixed in advance and independent of outcomes: 6 workers take seeds in index order (worker w: seeds w, w+6, …; each seed's two policies one after another). At 09:45 unfinished runs stop; the analysis uses the seeds for which both policies finished.
- A smoke test on two other seeds with planner combat (`RB901…`) was run before this was written, to check the plumbing; its outcomes are not used.

## 3. Policies
- `draft+shop+rest`: as in run benchmark 2 (draft scorer, shop removal and scorer's card, rest rules).
- `rdraft+shop+rest`: the same, except that card rewards are chosen by rollouts as above (the scorer only breaks exact ties and decides if every rollout fails).
- Both: non-Ancient events by the Player's most frequent choice, Neow, Ancients, boss relics and potion rewards by the first option, first map move (no route planner), as in run benchmark 2.

## 4. Metrics and test
- Primary: floor reached. Secondary: act 1 and act 2 bosses beaten, wins, where runs die, how often rollouts disagree with the scorer and how often they skip, seconds per run.
- Test: paired by seed, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval (`tools/run_bench.py --report … --baseline draft+shop+rest`).
- What follows: if H1 holds, rollout evaluation becomes the method for strategic decisions (next: map routes, then shops, rest sites and Ancients, then a run-state value network trained on the rollouts, decision 0004 step 5); if it does not, the rollout policy (planner combat in rollouts) and the value are examined before more decision types are moved to rollouts.

## 5. Results
Pending.

## 6. Deviations and notes
- 2026-11-21 04:05, during the run, a note on the rollouts (no change to the run): the run sampler of the Release build used here can put an encounter already met in the act back into a sampled future (9% of future encounters in a check of eight runs; the real game repeats none). Rollout worlds are therefore slightly off, the same for every option and arm. Fixed afterwards in `sim/RunSampler.cs` (0% after the fix), not used by this run.
