# Comparison: rollout decisions at Ascension 10 (run benchmark 6)

Written before the run (decision 0004 steps 3–4, ML-10), 2026-11-21 at 06:34, after the results of run benchmarks 3 and 4 and before any result of run benchmark 5. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** at Ascension 10, choosing card rewards and map moves by sampled rollouts (`rcard+rpath`) reaches more floors than the best rule policy so far (`path`: first card, route planner) when search plays every fight.

Why: the milestone that matters is Ascension 10 (M8: the Player won 8% of finished Ironclad runs there). Tonight's rollout results are all at A5 (cards +6.6 floors over the draft scorer in run benchmark 3, routes +1.1 over the route planner in run benchmark 4). This tests whether rollout decisions, both together, carry to the target ascension, where enemies hit harder and the act 3 boss is doubled.

## 2. Runs
- 60 seeds (`RB006` + index 00000–00059), Ironclad, **Ascension 10**, whole runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- Combat in both arms: `mcw6` through the save-based fight rebuild, and the run-clone rebuild for fights the save cannot rebuild (`--fight-rebuild save+run`); mismatches and failures fall back to the planner (counted).
- Rollouts (`tools/run_eval.py`), at each card reward (every card and skip) and at each map choice with two or more next points (the boss excepted): every option is evaluated on the same 6 sampled futures; the run is rebuilt in an evaluation host from its room-entry save plus the actions since with the future re-sampled, the option taken, and the run played on to the end of the act or death by `path` (rollouts never start rollouts of their own) with the rule planner fighting. Rollout value: floors climbed, plus 5 and 5 times the HP fraction left if the act's boss is beaten. The best mean value is taken; exact ties go to the first card and to the route planner's move.
- Host: the Release2 build used by run benchmark 5 (`sim/bin/Release2`, all checks passed at 05:37), unchanged.
- Starts when run benchmark 5 has finished, and not after 09:15. Stopping rule, fixed in advance and independent of outcomes: 6 workers take seeds in index order (worker w: seeds w, w+6, …; each seed's two policies one after another). At 10:30 unfinished runs stop; the analysis uses the seeds for which both policies finished.
- A smoke test on one other seed with planner combat (`RB903…`, A10) checked the plumbing; its outcome is not used.

## 3. Policies
- `path`: first card of each card reward, leave shops, rest below 60% HP else smith the first card, every map move before the boss by the route planner.
- `rcard+rpath`: the same, except that card rewards and map moves are chosen by rollouts as above.
- Both: non-Ancient events by the Player's most frequent choice; Neow, Ancients, boss relics and potion rewards by the first option.

## 4. Metrics and test
- Primary: floor reached. Secondary: act bosses beaten, wins, where runs die, elites fought, how often rollouts differ from the rules, seconds per run, search fallbacks.
- Test: paired by seed, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval (`tools/run_bench.py --report … --baseline path`).
- Reference, not a test (different seeds and game version): the Player's finished Ironclad runs at A10 on v0.107.1 (`data/runs.db`): 25 runs, mean floor 23.8, median 17, 2 wins.
- What follows: if H1 holds, `rcard+rpath` becomes the default run policy for Ascension work and simulated-run fight specs at A10, and the next steps aim at boss fights and the rollout value. If it does not, the A5 gains do not carry to A10 as they are, and where the rollout policy's runs die at A10 decides what is examined first.

## 5. Results
Pending.

## 6. Deviations and notes
