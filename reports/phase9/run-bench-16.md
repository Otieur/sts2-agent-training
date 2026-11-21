# Comparison: map routes by rollouts against the route planner on the new stack, at Ascension 0 (run benchmark 16)

Written before the run (decision 0005 item 3, ML-10), 2026-11-21 at 14:48, after the results of run benchmarks 2–9 and 11 and before any result of run benchmarks 12 and 15. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypotheses
- **H1 (floors):** on the stack that uses potions, upgrades and shops, choosing map moves by rollouts (`rpath`) still reaches more floors than the route planner (`path`).
- **H2 (wins):** it wins more runs.

Why: run benchmark 4 found +1.1 floors for route rollouts over the planner at A5 (p = 0.04, interval including zero), gained by avoiding elites, on a stack that drank no potion and upgraded Strikes. The rollouts judge a route with the rule planner fighting, which loses elite fights that search wins, so they keep away from elites: 1.3 elites per run in run benchmark 11, 9 elite choices in 282 forks. Elites are where relics come from, and the agent holds 3.4 relics at the act 1 boss against the Player's 5.3. With potions now used in elite fights the balance may have moved. The planner weighs expected loot against fatal risk from the Player's history and takes about two elites per run. The result says whether route rollouts keep their place until the fight-outcome model replaces the planner inside them.

## 2. Runs
- 30 new seeds (`RB016` + index 00000–00029), Ironclad, **Ascension 0**, whole new runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- `S*`: the stack after run benchmark 15 by that registration's rule (`data/learn/queue/stack2.py final`), fixed by the queue script before any result of this run. `P*`: `S*` with `path` in place of `rpath`.
- In `P*` the card rollouts (and shop and event rollouts, if in the stack) are unchanged; their futures are played with the route planner in both arms, as before.
- Combat in both arms: `mcw6` in every fight, `--fight-rebuild save+run`. Host: the Release2 build, unchanged. 7 workers claim seeds in index order (`--dynamic`). Stopping rule: unfinished runs stop 5 hours after the start; time the machine is asleep does not count (the rule of run benchmark 12, section 6). The analysis uses the seeds for which both policies finished.
- Fights and rollout decisions are recorded as in run benchmark 11.

## 3. Policies
- `S*`: map moves by sampled rollouts, ties and failures to the route planner.
- `P*`: map moves by the route planner (`tools/path.py`).

## 4. Metrics and tests
- H1: floor reached, paired by seed (`S*` − `P*`), one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval. H2: wins, one-sided exact sign test at 0.05 on the seeds where exactly one arm wins; wins per arm with Wilson intervals (`tools/run_details.py --wins-vs`).
- Secondary: elites fought per run and their results; relics, upgrades, potions and HP at each boss fight's start; act bosses beaten; where runs die; node types chosen; seconds per run.
- What follows, the stack that runs next: `rpath` stays if its mean paired difference in floors is positive and it does not win fewer runs; otherwise `path` replaces it (it is also the cheaper of the two). A claim either way needs its test.

## 5. Results
Pending.

## 6. Deviations and notes
