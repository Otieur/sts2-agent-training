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
- In every arm: non-Ancient events take the option the Player chose most often at that point in the history (`data/runs.db`, matched by page and option key) when it was chosen at least twice, else the first option; Neow and Ancient options, boss relics and potion rewards use the run simulator's simple policy (first option). Decisions use only what a player can see (FP-1).

## 4. Metrics and test
- Primary: floor reached. Secondary: act 1 and act 2 bosses beaten, wins, HP lost per fight by room type, where runs die, search fallbacks.
- Test: paired by seed, one-sided sign test at 0.05 per hypothesis, mean paired difference with a bootstrap 95% interval (`tools/run_bench.py --report`, baselines `base` for H1 and `draft+shop+rest` for H2).
- What follows: if H1 holds, rule deck building becomes the default run policy for run benchmarks and simulated-run fight specs; if not, the scorer's act 1 behaviour (skip rate, support cards) is tested next with decision-time run evaluation (decision 0004, steps 3–4). If H2 holds, the route planner becomes the default; if not, its room models are recalibrated against simulated outcomes before routes are tested again.

## 5. Results
Run 2026-11-21, 01:47–03:31 (`data/learn/runs/run-bench-2/manifest.json`; 6324 s wall, 6 workers, all exited cleanly, code `1b723ca`; all 60 seeds finished before the deadline). Reports: `python3 -I tools/run_bench.py --report data/learn/runs/run-bench-2` (H1) and `--baseline draft+shop+rest` (H2).

| Policy | Runs | Mean floor | Median floor | Reached the act 1 boss | Beat it | Act 2 boss | Won | Final deck (mean cards) |
|---|---|---|---|---|---|---|---|---|
| base | 60 | 16.37 | 17 | 36 | 10 | 0 | 0 | 20.4 |
| draft+shop+rest | 60 | 13.98 | 13 | 17 | 8 | 0 | 0 | 16.8 |
| draft+shop+rest+path | 60 | 16.65 | 17 | 34 | 14 | 0 | 0 | 16.7 |

| Pair (B − A), floors | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| draft+shop+rest − base (H1) | 60 | -2.38 | -4.32 to -0.52 | 9 | 36 | 15 | 1.000 |
| draft+shop+rest+path − draft+shop+rest (H2) | 60 | +2.67 | 0.55 to 4.85 | 37 | 15 | 8 | 0.0016 |
| draft+shop+rest+path − base (not tested) | 60 | +0.28 | -2.05 to 2.57 | 24 | 23 | 13 | 0.50 |

- **H1** (`draft+shop+rest` reaches more floors than `base`): p = 1.000, mean −2.38: **does not hold; the difference goes the other way** (36 runs worse, 9 better, interval entirely below zero).
- **H2** (adding the route planner reaches more floors than `draft+shop+rest`): p = 0.0016, mean +2.67: **holds**.

Where runs die (room type of the fatal fight): `base` elites 23, bosses 29, hallways 8; `draft+shop+rest` elites 34, bosses 10, hallways 14, outside a fight 2; `draft+shop+rest+path` elites 25, bosses 23, hallways 12. HP lost per won fight: hallways 3.0 / 4.3 / 3.3, elites 24.0 / 30.5 / 32.3, bosses 47.0 / 35.5 / 37.1 (same order).

Search in the fights: 26,747 searched moves; 0 fallbacks in `base`, 89 in `draft+shop+rest` (87 rebuild errors, 2 mismatches) and 67 in `draft+shop+rest+path` (66 and 1), about 0.6% overall; the errors come from fights started by events (the fight's save re-enters the event), which the planner then plays. No run was stopped by a host error.

**Verdict: H1 does not hold (it reverses); H2 holds.** With search playing every fight, the rule deck building (scorer drafting, shop removals and purchases, rest rules) still ends runs earlier than taking the first card of every reward: −2.4 floors, and only 17 of 60 runs reach the act 1 boss against 36. The rule decks are smaller (16.8 cards against 20.4) and die in elites (34 of 60). So the run benchmark 1 result was not only a weak-fighter effect: at A5 the scorer's act 1 choices (skipping, cards that need support) cost more than they give. The route planner recovers the loss (+2.7 floors over the same deck rules, 34 runs reach the boss), ending level with `base`. No policy beats the act 2 boss; at A5 the act 1 boss is the wall (beaten in 10, 8 and 14 runs).

By the rule in section 4: the route planner becomes the default route policy in run benchmarks and simulated-run fight specs; the deck-building rules do not, and the scorer's act 1 behaviour is tested next with decision-time evaluation (run benchmark 3, card rewards by sampled rollouts, pre-registered before these results were known).

## 6. Deviations and notes
- 2026-11-21 01:45, before the run: the timing pilot showed that the first-option rule wrecks runs in some events. In the Tablet of Truth it chooses Decipher again and again, and max HP falls from 80 to 1 by floor 3, after which every arm dies by floor 7 or 8 whatever it drafts. The shared event rule in section 3 was changed from first option to the Player's most frequent choice (`event_pick` in `tools/run_bench.py`); a sweep of 30 other seeds with planner combat then showed no run with max HP below 60. The hypotheses, arms, seeds and test are unchanged; the pilot's outcomes are not used.
