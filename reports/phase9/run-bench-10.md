# Comparison: shop purchases by sampled rollouts (run benchmark 10)

Written before the run (decision 0004 steps 3–4, ML-10), 2026-11-21 at 10:09, after the results of run benchmarks 2–6 and before any result of run benchmarks 7, 8 and 9. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** at Ascension 10, choosing shop purchases by sampled rollouts (`Y+rshop`) reaches more floors than leaving every shop (`Y`), where `Y` is the run policy run benchmarks 7 and 9 support.

Why: every policy tested so far leaves shops without buying, so gold has no use and card removal never happens. Rollouts can judge each purchase (a card, a relic, a potion, removing a card) by what follows it, against keeping the gold.

## 2. Runs
- 60 seeds (`RB010` + index 00000–00059), Ironclad, **Ascension 10**, whole runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- `Y`: start from `X` of run benchmark 9 (`rcard+rpath+bc` if run benchmark 7's H1 holds, otherwise `rcard+rpath`) and add `ropt` if run benchmark 9's H1 holds (same rule: one-sided sign test p < 0.05 with a positive mean difference). Chosen by the queue script from the two manifests, before any result of this run.
- Combat in both arms: `mcw6` in every fight, `--fight-rebuild save+run`; mismatches and failures fall back to the planner (counted).
- Rollouts for `rshop` (`tools/run_opts.py`): on every shop screen, the options are leaving and buying each distinct affordable item (card removal, relics, cards, potions, in that order of listing); with more than 12 such options the screen is left to the rules (leave). Each option is evaluated on the same 6 sampled futures, played to the end of the act or death by the rule policy (`path`, which leaves shops) with the rule planner fighting, with `Y`'s rollout value. The best mean value is taken; exact ties and failures go to leaving. After a purchase the shop is judged again, until leaving wins. The card removed by the removal service is chosen by `ropt` if `Y` has it, otherwise by the rule (the first card). These rollouts share the evaluation host of the route rollouts.
- Host: the Release2 build (`sim/bin/Release2`), unchanged. Code as in run benchmark 9.
- Starts when run benchmark 9 has finished (queue). Stopping rule, fixed in advance and independent of outcomes: 6 workers take seeds in index order (worker w: seeds w, w+6, …; each seed's two policies one after another). Unfinished runs stop 4 hours after the start; the analysis uses the seeds for which both policies finished.
- Smoke test before registration on one other seed with planner combat (`RB907…`, A0): plumbing only, outcome not used.

## 3. Policies
- `Y`: as above; shops left without buying.
- `Y+rshop`: the same, with shop purchases by rollouts as above.

## 4. Metrics and test
- Primary: floor reached. Secondary: act bosses beaten, wins, where runs die, purchases per run (by kind), gold left at death, seconds per run, search fallbacks.
- Test: paired by seed, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval (`tools/run_bench.py --report … --baseline Y`).
- What follows: if H1 holds, `rshop` joins the run policy. If not, shops stay with the rule, and the purchase options or the rollout horizon (to the end of the act, which may undervalue relics and removal) are examined.

## 5. Results
Pending.

## 6. Deviations and notes
- 2026-11-21 10:14, before the run (stopping rule, not outcomes): 7 workers instead of 6, and the seeds are claimed in index order by whichever worker is free (`--dynamic`) instead of fixed seeds per worker. Reason: the Player asked for full use of the CPU and stopped the other project's processes, which frees memory; with fixed seeds the workers that finish early sit idle at the end of each benchmark (32% of the CPU idle in run benchmark 7's tail). Each seed is played the same whichever worker plays it (the same random generator per seed, search by fixed counts of sampled worlds), so the change affects only the wall time and, if the deadline stops the run, which seeds are cut, and neither depends on outcomes.
