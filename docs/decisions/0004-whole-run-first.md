# 0004: Whole-run results first; deck building, pathing and choices as first-class training targets

Date: 2026-11-20 · Status: **accepted as direction** (the Player pointed out on 2026-11-20 that deck building, map routes and option choices matter more than fight play, and asked for the plan to be revised). Supersedes the ordering in 0003 where strategic decisions came last (P9.E4); the simulator, search and learning tracks of 0003 stay.

## Context
- The engine track so far measured fights: a benchmark of 60 fights taken from the Player's runs, with the Player's decks. Wide search wins 99 of 120 games there and is close to the Player's own results on the same fights. That says little about runs: the decks in those fights were built by the Player.
- Every non-combat decision (Neow and Ancients, card rewards, removal, upgrades, rest, shop, map route, events, boss relics, potion slots) is made by rule tools built from the history analysis and community sources (`tools/draft.py`, `path.py`, `advise.py`) or by placeholders in the run simulator. None of them has been validated by run outcomes.
- The first run-level comparison (`reports/phase9/run-bench-1.md`) showed the problem: with the rule planner fighting, scorer drafting ended runs earlier than taking the first card, and almost every run died in act 1 whatever the policy. Deck building cannot be judged with a weak fighter, and our deck-building rules are untested.
- Since 2026-11-20 a fight inside a simulated run can be exported to a search host and rebuilt there with the hidden future re-sampled (`export_fight`, 15 of 15 rebuilds equal), so whole runs can be played with search in every fight.

## Decision
1. **Primary metric:** whole-run results in the simulator with search playing every fight: floor reached, act bosses beaten, wins. Target band Ascension 10, with Ascension 5 as a band that gives more signal. Fixed seed sets, paired comparisons, pre-registered as before (ML-10).
2. **Every decision type is a training target** with a baseline, an evaluation on the run benchmark and its own story: Neow and Ancient options, card rewards (take or skip), card removal, upgrades and rest, shop purchases, map route, event options, boss relics, potion keeping.
3. **Order of work:**
   1. Run benchmark with search combat (`tools/run_bench.py --combat mcwK`).
   2. The existing rule tools wired into the run simulator as the strategic baseline (drafting, route, events and Ancients, rest, shop), each compared with simple baselines on the run benchmark.
   3. Run-level cloning with the run's hidden future re-sampled (future card offers, event outcomes, shop and chest contents; FP-16), so any strategic choice can be judged at decision time by playing each option forward without seeing the seed.
   4. Decision-time evaluation: rollouts to the end of the act for the high-impact choices (boss relics, Ancients, elite routes, key picks); a cheap deck evaluator (engine fights against the act's known encounter pools) for card decisions.
   5. A run-state value network trained on many simulated runs (P9.E4) to replace rollouts at scale, then expert iteration at run level.
4. **Combat work narrows** to what the run loop needs: speed (the action-value candidate filter) and potions. The learned leaf evaluation (comparisons 1–4) is paused.
5. **Real games:** fight search in live runs (P8.E5, `docs/proposals/live-search.md`) uses the same rebuild path; the scored ladder resumes when the simulated win rate on the run benchmark beats the Player's band rates (A5–9 25%, A10 8%).

## Consequences
- Compute goes mostly to whole runs. A run with search in every fight takes minutes, so run benchmarks run in batches (overnight); the planner-combat harness stays for fast checks of the plumbing only.
- New milestones: M15 a run benchmark with search combat in place; M16 each strategic decision type has a validated policy; M17 simulated A5 win rate above 25%; M18 simulated A10 win rate above 8%.
- The Player's history stays a source of hypotheses and of situations (fight specs); its card-pick and path statistics are baselines to beat, not targets.
