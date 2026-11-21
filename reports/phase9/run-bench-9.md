# Comparison: events, rest sites and card choices by sampled rollouts (run benchmark 9)

Written before the run (decision 0004 steps 3–4, ML-10), 2026-11-21 at 10:09, after the results of run benchmarks 2–6 and before any result of run benchmarks 7 and 8. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** at Ascension 10, choosing events (Neow and the Ancients included), rest-site actions and card choices outside fights by sampled rollouts (`X+ropt`) reaches more floors than choosing them by rules (`X`), where `X` is the run policy run benchmark 7 supports.

Why: card rewards and map moves by rollouts gained 5.5 and 1.1 floors at A5 (run benchmarks 5 and 4) and 2.8 together at A10 (run benchmark 6). Every other run decision is still a rule: Neow and the Ancients take the first option, other events the Player's most frequent choice, rest sites heal below 60% HP and otherwise smith the first card in the deck, and card choices outside fights (upgrade, remove, transform, enchant) take the first card. Smithing before the act 1 boss and the Neow and Ancient relics bear directly on the boss fights where most A10 runs now end.

## 2. Runs
- 60 seeds (`RB009` + index 00000–00059), Ironclad, **Ascension 10**, whole runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- `X`: `rcard+rpath+bc` if run benchmark 7's H1 holds (one-sided sign test p < 0.05 with a positive mean difference), otherwise `rcard+rpath`. Chosen by the queue script from run benchmark 7's manifest, before any result of this run.
- Combat in both arms: `mcw6` in every fight, save-based fight rebuild with the run-clone rebuild when that fails (`--fight-rebuild save+run`); mismatches and failures fall back to the planner (counted).
- Rollouts for `ropt` (`tools/run_opts.py`): on every event page with two or more options, every rest-site screen with two or more site options (leaving empty-handed is not an option), and every card choice outside fights except card rewards, each distinct option (identical cards counted once) is evaluated on the same 6 sampled futures, played to the end of the act or death by the rule policy (`path`) with the rule planner fighting, with the same rollout value as `X` (with the boss credit if `X` has `bc`). Screens with more than 12 distinct options are left to the rules. The best mean value is taken; exact ties and failures go to the rule's choice. These rollouts share the evaluation host of the route rollouts.
- Host: the Release2 build (`sim/bin/Release2`), unchanged. Code: `tools/run_opts.py` and the hooks in `tools/run_bench.py` (off unless `ropt` or `rshop` is named).
- Starts when run benchmark 8 has finished (queue). Stopping rule, fixed in advance and independent of outcomes: 6 workers take seeds in index order (worker w: seeds w, w+6, …; each seed's two policies one after another). Unfinished runs stop 4 hours after the start; the analysis uses the seeds for which both policies finished.
- Smoke test before registration on one other seed with planner combat (`RB907…`, A0): plumbing only, outcome not used.

## 3. Policies
- `X`: card rewards and map moves by rollouts; Neow, Ancients, boss relics and potion rewards by the first option; other events by the Player's most frequent choice; shops left; rest below 60% HP, else smith the first card; other card choices outside fights by the first card.
- `X+ropt`: the same, with events, rest sites and card choices outside fights by rollouts as above.

## 4. Metrics and test
- Primary: floor reached. Secondary: act bosses beaten, wins, where runs die, elites fought per run, `ropt` decisions and how often they differ from the rules (by screen type), seconds per run, search fallbacks.
- Test: paired by seed, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval (`tools/run_bench.py --report … --baseline X`).
- What follows: if H1 holds, `ropt` joins the run policy (run benchmark 10 builds on it). If not, these decisions stay with the rules, and the rollout value or fighter is examined before more decisions move to rollouts.

## 5. Results
Pending.

## 6. Deviations and notes
- 2026-11-21 10:14, before the run (stopping rule, not outcomes): 7 workers instead of 6, and the seeds are claimed in index order by whichever worker is free (`--dynamic`) instead of fixed seeds per worker. Reason: the Player asked for full use of the CPU and stopped the other project's processes, which frees memory; with fixed seeds the workers that finish early sit idle at the end of each benchmark (32% of the CPU idle in run benchmark 7's tail). Each seed is played the same whichever worker plays it (the same random generator per seed, search by fixed counts of sampled worlds), so the change affects only the wall time and, if the deadline stops the run, which seeds are cut, and neither depends on outcomes.
- 2026-11-21 11:28, a correction to the note above: a seed's run is not identical whichever worker plays it. The fights are (search sample seeds depend only on the decision's position in the run), but the rollouts' sample seeds also depend on how many rollout decisions the worker's evaluation host has made before, so the sampled futures behind a card or route decision differ with the worker's history. They are fixed by position, never by outcomes, so the comparison stays valid; exact reproduction of a single run needs the same worker history.
- 2026-11-21 11:28, interruption: the run started at 10:55 and was stopped at 11:26 with 35 of 60 seeds recorded, when the agent session that had launched the queue ended and took its background processes with it (not the registered stopping rule, and not related to any outcome). Resumed at 11:28 with `tools/run_bench.py --resume` (new): the 35 recorded seeds are kept, the 7 seeds in progress at the interruption are played again from the start, and the rest follow, with the registered deadline unchanged (14:55, 4 hours after the first start). The queue now runs detached from the session.
