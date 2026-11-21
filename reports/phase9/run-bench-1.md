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
Pending.

## 6. Deviations and notes
None yet.
