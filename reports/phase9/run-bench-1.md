# Comparison: deck-building components in whole simulated runs (planner combat)

Written before the run (ML-10), 2026-11-20 at 22:50. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypotheses
- **H1:** drafting by the draft scorer (`draft`) reaches more floors than taking the first card of every reward (`base`).
- **H2:** adding shop purchases (card removal, then the scorer's card) and rest-site rules (`draft+shop+rest`) reaches more floors than `draft`.

## 2. Runs
- 60 seeds (`RB001` + index), Ironclad, Ascension 0, whole runs in the simulator from Neow to death or victory (`tools/run_bench.py`). Every policy plays every seed.
- Combat in every arm: the rule planner (run-level states cannot be cloned for search yet). Known consequence: runs die early (a smoke test of three seeds ended on floors 9–14), which limits how much any deck-building rule can show; this is a baseline for the harness, not the final word on deck building.

## 3. Policies
- `base`: first card of each reward, leave shops, rest below 60% HP else smith the first card, first map move, first option elsewhere.
- `draft`: card rewards by `tools/draft.py score_offer` (skip below its bar); the rest as `base`.
- `draft+shop+rest`: as `draft`, plus shops (removal first: curses, Strikes, Defends; then the scorer's card if gold allows) and rest sites (heal below 50% HP, or 70% before the boss; upgrades by tier, Bash first).

## 4. Metrics and test
- Primary: floor reached. Secondary: act 1 and act 2 bosses beaten, wins.
- Test: paired by seed, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval. 60 seeds, no early stop.
- What follows: components that hold become the defaults of the simulated-run policy (`tools/run_specs.py` and later run-level work).

## 5. Results
Run 2026-11-20, 22:50–22:53 (`data/learn/runs/run-bench-1/manifest.json`; 156 s wall, code `622c981`).

| Policy | Runs | Mean floor | Act 1 boss beaten | Act 2 boss beaten | Won |
|---|---|---|---|---|---|
| base | 60 | 13.50 | 2 | 0 | 0 |
| draft | 60 | 11.63 | 1 | 0 | 0 |
| draft+shop+rest | 60 | 11.35 | 2 | 0 | 0 |

| Pair (B − A), floors | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| draft − base | 60 | -1.87 | -3.13 to -0.57 | 10 | 28 | 22 | 0.999 |
| draft+shop+rest − base | 60 | -2.15 | -3.52 to -0.68 | 12 | 30 | 18 | 0.999 |

**Verdict: H1 does not hold; the difference goes the other way.** With the rule planner fighting, drafting by the scorer ends runs 1.9 floors earlier than taking the first card of every reward (10 runs better, 28 worse); adding the shop and rest rules does not help (−2.2 against `base`; H2 is not met either, against `draft` it is −0.3). Almost every run dies in act 1 whatever the policy (at most 2 of 60 beat the act 1 boss).

Reading: the scorer was built for a strong player and the long run (it skips more often in act 1 and favours cards that need support), while these runs measure act 1 survival under a weak fighter, where any extra card helps. So this result says deck building cannot be judged with planner combat, not that the scorer is worse; but it also shows that the deck-building rules have never been validated by outcomes. Next: whole runs with search in every fight. Each fight is exported from the run host (the game's own fight recording) to a search host, which rebuilds it with the hidden future re-sampled and chooses the move (tested: 15 of 15 exports rebuild to the same visible state).


## 6. Deviations and notes
None yet.
