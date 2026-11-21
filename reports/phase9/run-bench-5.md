# Comparison: card rewards by sampled rollouts against the first card (run benchmark 5)

Written before the run (decision 0004 steps 3–4, ML-10), 2026-11-21 at 05:30, after run benchmark 3's results and before any result of run benchmark 4. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** choosing card rewards by sampled rollouts (`rcard+path`) reaches more floors than taking the first card of every reward (`path`) when search plays every fight.

Why: in run benchmark 3 rollouts beat the hand-made draft scorer by 6.6 floors (44 seeds better, 7 worse). But in run benchmark 2 the scorer was itself 2.4 floors worse than taking the first card, so run benchmark 3 does not show that rollouts beat the strongest card rule known. This comparison sets rollouts against the first card, with the route planner (the one rule that helped in run benchmark 2) in both arms, and with rollouts that play the first card rather than the scorer.

## 2. Runs
- 60 seeds (`RB005` + index 00000–00059), Ironclad, Ascension 5, whole runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- Combat in both arms: `mcw6` through the save-based fight rebuild, and, for fights the save cannot rebuild (fights started by events), the rebuild through the run clone (`--fight-rebuild save+run`). Mismatches and failures fall back to the planner (counted).
- Rollouts (`tools/run_eval.py`): at each card reward, every card and skip is evaluated on the same 6 sampled futures (common random numbers): the run is rebuilt in an evaluation host from its room-entry save plus the actions since with the future re-sampled (`run_from_save` with a sample seed), the option taken, and the run played on to the end of the act or death by the `path` policy (first card, route planner, simple shop and rest rules) with the rule planner fighting. Rollout value: floors climbed, plus 5 and 5 times the HP fraction left if the act's boss is beaten. The best mean value is taken; exact ties go to the first card.
- Host: a Release build of the current host code, which adds to the build used in run benchmarks 3 and 4 the run sampler fix (no encounter already met in the act comes back in a sampled future) and the fight rebuild through the run clone. Built into `sim/bin/Release2` so that run benchmark 4's host is not touched. Checks before the run: clone, clone from saves, clone from run clones, run clones and sampler (`sim.py runclone`), fair play, sandbox, fidelity. The run starts only if all pass.
- Starts when run benchmark 4 has finished, and not after 09:15. Stopping rule, fixed in advance and independent of outcomes: 6 workers take seeds in index order (worker w: seeds w, w+6, …; each seed's two policies one after another). At 10:00 unfinished runs stop; the analysis uses the seeds for which both policies finished.
- A smoke test on one other seed with planner combat (`RB902…`) checks the plumbing; its outcome is not used.

## 3. Policies
- `path`: first card of each card reward, leave shops, rest below 60% HP else smith the first card, every map move before the boss by the route planner (as in run benchmark 4).
- `rcard+path`: the same, except that card rewards are chosen by rollouts as above (the first card only breaks exact ties and decides if a rollout fails).
- Both: non-Ancient events by the Player's most frequent choice; Neow, Ancients, boss relics and potion rewards by the first option.

## 4. Metrics and test
- Primary: floor reached. Secondary: act 1 and act 2 bosses beaten, wins, where runs die, how often rollouts differ from the first card and how often they skip, final deck size, seconds per run, search fallbacks.
- Test: paired by seed, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval (`tools/run_bench.py --report … --baseline path`).
- What follows: if H1 holds, card rewards move to rollouts in the run policy for later benchmarks and simulated-run fight specs, and rollouts are extended to shops, rest sites and Ancients. If it does not, the run benchmark 3 gain is read as mostly undoing the scorer's mistakes, and the next step is to examine the rollout policy and value (planner fighting in rollouts, act-end horizon) before moving more decisions to rollouts.

## 5. Results
Pending.

## 6. Deviations and notes
