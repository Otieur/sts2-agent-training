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
Run 2026-11-21, 09:12–10:18 (`data/learn/runs/run-bench-7/manifest.json`; 3994 s wall, 6 workers, all exited cleanly; all 60 seeds finished before the deadline). Host: `sim/bin/Release2`, as registered. Code: the run started from `e723598` (recorded at the start; see section 6 for edits made during the run). Report: `python3 -I tools/run_bench.py --report data/learn/runs/run-bench-7 --baseline rcard+rpath`.

| Policy | Runs | Mean floor | Median floor | Reached the act 1 boss | Beat it | Reached the act 2 boss | Won | Elites fought per run | Final deck (mean cards) | Seconds per run |
|---|---|---|---|---|---|---|---|---|---|---|
| rcard+rpath | 60 | 16.55 | 17 | 49 | 3 | 0 | 0 | 0.62 | 17.7 | 209 |
| rcard+rpath+bc | 60 | 16.10 | 17 | 50 | 0 | 0 | 0 | 0.57 | 17.6 | 159 |

| Pair (B − A), floors | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| rcard+rpath+bc − rcard+rpath (H1) | 60 | −0.45 | −1.38 to 0.38 | 7 | 8 | 45 | 0.70 |

- **H1** (rollouts that credit progress against a boss reach more floors at A10): p = 0.70, mean −0.45 floors: **does not hold**.

Act 1 bosses (fights won / fought): `rcard+rpath` Ceremonial Beast 2/8, The Kin 1/23, Vantom 0/18; `rcard+rpath+bc` Ceremonial Beast 0/10, The Kin 0/22, Vantom 0/18.

Where runs die (room type of the fatal fight): `rcard+rpath` bosses 46, elites 10, hallways 4; `rcard+rpath+bc` bosses 50, elites 8, hallways 2. HP lost per won fight: hallways 5.9 / 6.4, elites 30.7 / 31.8, bosses 36.0 / none won.

Rollout decisions: `rcard+rpath` 421 card rewards (252 different from the first card, 59 skips) and 343 map choices (131 different from the route planner); `rcard+rpath+bc` 401 (208, 47) and 315 (124). Search: 14,652 searched moves, 0 fallbacks, 0 mismatches.

Act 1 elites fought by the runs that reached the act 1 boss: 0.45 (`rcard+rpath`) and 0.50 (`rcard+rpath+bc`) per run; 0.67 in run benchmark 6's rollout arm and 1.5 in its `path` arm. The Player's 19 A10 runs that reached the act 1 boss fought 0.68 act 1 elites (`data/runs.db`), so the rollout policies' elite avoidance is not what separates them from the Player at the boss.

**Verdict: H1 does not hold; the act 1 boss at A10 is a wall that the rollout value does not move.** The boss credit leaves 45 of 60 seeds on the same floor. Together the two arms beat the act 1 boss in 3 of 99 fights (run benchmark 6: 5 of 48; the Player: 12 of 19), while reaching it in 83% of runs. A graded signal from the planner's boss fights is not enough. By section 4, boss readiness needs a better fighter or model inside the rollouts, or the deck and fight need to be examined directly, before more decisions are moved to rollouts. Boss replay 1 (registered at 10:09) does the direct examination; it is moved ahead of run benchmark 10 in the queue (section 6 of its registration).

## 6. Deviations and notes
- 2026-11-21 10:20, after the run, a note on the code: `tools/run_bench.py` gained default-off components (`ropt`, `rshop`), boss fight specs in the fight records and dynamic seed claiming while this run was in progress (commits `1857f28`, `aa98be4`). Both arms use rollouts from the first map decision, so every worker had imported its modules within the first minutes, before those edits; the records of this run have no boss fight specs, which confirms it.
