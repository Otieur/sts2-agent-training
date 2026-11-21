# Comparison: deck-building components in whole runs with search in every fight (run benchmark 2)

Written before the run (P9, decision 0004, ML-10), 2026-11-21 at 01:41. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypotheses
- **H1:** rule deck building (`draft+shop+rest`) reaches more floors than `base` when search plays every fight.
- **H2:** adding the route planner (`draft+shop+rest+path`) reaches more floors than `draft+shop+rest`.

Why: the first run benchmark (`run-bench-1.md`, rule planner fighting) found scorer drafting 1.9 floors worse than taking the first card, which was read as an effect of a weak fighter: almost every run died in act 1. With search playing every fight (wide search wins 99 of 120 games on the fight benchmark against 75 for the planner), the deck-building rules get their first fair test by outcomes. The route planner (`tools/path.py`) has never been tested by outcomes at all.

## 2. Runs
- 60 seeds (`RB002` + index 00000–00059), Ironclad, **Ascension 5** (decision 0004: the band that gives more signal than A10), whole runs in the simulator from Neow to death or victory (`tools/run_bench.py`). Every policy plays every seed; runs start identical and diverge with the decisions.
- Combat in every arm: `mcw6` (flat Monte Carlo over the wide candidate set, cap 8, 6 worlds each, planner rollouts). Each decision is searched in a second host on the fight rebuilt from the run state saved at room entry plus the fight's actions so far (`fight_from_save`), with the hidden future re-sampled (FP-15). If the rebuilt visible state differs from the run host's, or the search host fails, the planner decides that move (counted and reported).
- Potions are not offered to search (`reports/phase8/potions-all.md`: drinking is a run-level question); the planner fallback may drink. Same in every arm.
- Host: Release build with tonight's fixes; checks before the run: clone 12/12, clone from saved run states 11/11, fair play 8/8, sandbox 3/3, fidelity 11/11 (`docs/overnight-log.md`).
- Timing pilot: 3 other seeds (`RB900…`) with the same settings, started before this file was written; it sets nothing here except the expectation that 60 seeds may not finish overnight. Its outcomes are not part of the test.
- Stopping rule, fixed in advance and independent of outcomes: 6 workers take seeds in index order (worker w plays seeds w, w+6, …; each seed's three policies one after another). At 09:45 any unfinished runs stop; the analysis uses the seeds for which all three policies finished.

## 3. Policies
- `base`: first card of each card reward, leave shops, rest below 60% HP else smith the first card, first map move, first option elsewhere.
- `draft+shop+rest`: card rewards by `tools/draft.py score_offer` (skip below its bar); shops (removal first: curses, Strikes, Defends; then the scorer's card if gold allows); rest sites (heal below 50% HP, or 70% before the boss; upgrades by tier, Bash first).
- `draft+shop+rest+path`: as above, plus every map choice before the boss by the route planner (`tools/path.py rank`: expected loot against fatal risk, room models from the history, risk weight per act).
- In every arm, Neow and Ancient options, events, boss relics and potion rewards use the run simulator's simple policy (first option). Decisions use only what a player can see (FP-1).

## 4. Metrics and test
- Primary: floor reached. Secondary: act 1 and act 2 bosses beaten, wins, HP lost per fight by room type, where runs die, search fallbacks.
- Test: paired by seed, one-sided sign test at 0.05 per hypothesis, mean paired difference with a bootstrap 95% interval (`tools/run_bench.py --report`, baselines `base` for H1 and `draft+shop+rest` for H2).
- What follows: if H1 holds, rule deck building becomes the default run policy for run benchmarks and simulated-run fight specs; if not, the scorer's act 1 behaviour (skip rate, support cards) is tested next with decision-time run evaluation (decision 0004, steps 3–4). If H2 holds, the route planner becomes the default; if not, its room models are recalibrated against simulated outcomes before routes are tested again.

## 5. Results
Pending.

## 6. Deviations and notes
None yet.
