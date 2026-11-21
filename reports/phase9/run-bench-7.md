# Comparison: rollout value with credit for progress against bosses (run benchmark 7)

Written before the run (decision 0004 steps 3–4, ML-10), 2026-11-21 at 08:17, after the results of run benchmarks 3, 4 and 5 and before any result of run benchmark 6. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** at Ascension 10, rollouts whose value credits progress against a boss (`rcard+rpath+bc`) reach more floors than the same rollouts with the current value (`rcard+rpath`) when search plays every fight.

Why: in run benchmarks 4 and 5 the rollout policies stop mostly at bosses (run benchmark 5: 38 of 60 rollout runs die in a boss fight; run benchmark 4: route rollouts reach the act 1 boss more often but beat it no more often, and avoid elites). Inside the rollouts the rule planner fights, and it rarely beats a boss, so most rollouts that reach the boss end with the same value (floors climbed) whatever the deck. A rollout that dies with the boss nearly dead then scores the same as one that barely scratches it, and what an elite gives for the boss fight (relics, upgrades, cards) is invisible. Crediting the fraction of the boss's HP removed gives the rollouts a graded signal of boss readiness at no extra cost.

## 2. Runs
- 60 seeds (`RB007` + index 00000–00059), Ironclad, **Ascension 10**, whole runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- Combat in both arms: `mcw6` through the save-based fight rebuild, and the run-clone rebuild for fights the save cannot rebuild (`--fight-rebuild save+run`); mismatches and failures fall back to the planner (counted).
- Rollouts as in run benchmark 6 (`tools/run_eval.py`): at each card reward (every card and skip) and at each map choice with two or more next points (the boss excepted), every option on the same 6 sampled futures, played to the end of the act or death by `path` with the rule planner fighting; best mean value, exact ties to the first card and to the route planner's move.
- Rollout value, `rcard+rpath`: floors climbed, plus 5 and 5 times the HP fraction left if the act's boss is beaten (as in run benchmarks 3–6).
- Rollout value, `rcard+rpath+bc`: the same, plus, for a rollout that dies in a boss fight, 5 times the fraction of that fight's enemy HP it removed (enemy HP at the fight's start, the most seen during it, against what is left at its last observation; enemies above 10,000 HP not counted); and a won run counts as beating the act's boss (in act 3 the act number never advances). The weight 5 makes a death with the boss at 0 HP worth as much as beating it with 0 HP left. Fixed before the run; no tuning.
- Host: the Release2 build used by run benchmarks 5 and 6 (`sim/bin/Release2`), unchanged. The new value is Python only (`tools/run_eval.py`, `tools/run_bench.py` component `bc`).
- Starts when run benchmark 6 has finished, and not after 10:45. Stopping rule, fixed in advance and independent of outcomes: 6 workers take seeds in index order (worker w: seeds w, w+6, …; each seed's two policies one after another). At 13:30 unfinished runs stop; the analysis uses the seeds for which both policies finished.
- A smoke test on one other seed with planner combat (`RB904…`, A10) checks the plumbing; its outcome is not used.

## 3. Policies
- `rcard+rpath`: first-card rules replaced by rollouts for card rewards, route planner replaced by rollouts for map moves; leave shops, rest below 60% HP else smith the first card.
- `rcard+rpath+bc`: the same, with the boss credit in every rollout value.
- Both: non-Ancient events by the Player's most frequent choice; Neow, Ancients, boss relics and potion rewards by the first option.

## 4. Metrics and test
- Primary: floor reached. Secondary: act bosses beaten, wins, where runs die, elites fought per run, how often the two arms' rollouts differ from the rules, seconds per run, search fallbacks.
- Test: paired by seed, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval (`tools/run_bench.py --report … --baseline rcard+rpath`).
- What follows: if H1 holds, the boss credit becomes part of the rollout value, and the next step is a stronger boss signal (search instead of the planner for boss fights inside rollouts, or a learned fight-outcome model) to see how much more there is. If it does not, a graded boss signal from the planner is not enough, and boss readiness needs a better fighter or model inside the rollouts before more decisions move to rollouts.

## 5. Results
Pending.

## 6. Deviations and notes
