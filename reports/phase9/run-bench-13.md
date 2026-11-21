# Comparison: events and card choices by sampled rollouts at Ascension 0 (run benchmark 13)

Written before the run (decision 0005 item 3, ML-10), 2026-11-21 at 12:10, after the results of run benchmarks 2–9 and before any result of run benchmarks 11 and 12. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypotheses
- **H1 (floors):** at Ascension 0, choosing events (Neow and the Ancients included) and card choices outside fights by sampled rollouts (`S+ropt`) reaches more floors than choosing them by rules (`S`).
- **H2 (wins):** it wins more runs.

Why: run benchmark 9 tested `ropt` at A10 and found +1.9 floors with act 1 boss wins 9 against 5, short of the registered test (p = 0.084, 34 of 60 seeds tied on the same floor). At A0 runs spread over three acts, Neow and the three Ancients each get a decision that lasts, and wins can be counted.

## 2. Runs
- 30 seeds (`RB013` + index 00000–00029), Ironclad, **Ascension 0**, whole new runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- `S`, the stack supported by run benchmarks 11 and 12, fixed by this rule before their results: start from `rcard+rpath`; add each of `pot`, `smith`, `rshop` for which run benchmark 11's treatment arm (all three on) reaches more floors on average than run benchmark 12's arm without that component, on the seeds both finished. Computed by the queue script (`tools/run_details.py --pair`).
- `ropt` as in run benchmark 9 (`tools/run_opts.py`): every event page with two or more options and every card choice outside fights except card rewards, each distinct option on the same 6 sampled futures played to the end of the act by `S`'s rules with the rule planner fighting; ties and failures to the rule; more than 12 options left to the rule. If `smith` is in `S`, rest sites and upgrade choices stay with that rule; otherwise `ropt` decides them too.
- Combat in both arms: `mcw6` in every fight, `--fight-rebuild save+run`. Host: the Release2 build, unchanged. 7 workers claim seeds in index order (`--dynamic`). Stopping rule: unfinished runs stop 5 hours after the start; the analysis uses the seeds for which both policies finished.
- Fights and rollout decisions are recorded as in run benchmark 11.

## 3. Policies
- `S`: as fixed above; Neow, Ancients, boss relics and potion rewards by the first option, other events by the Player's most frequent choice, card choices outside fights by the rules.
- `S+ropt`: the same with events and card choices outside fights by rollouts.

## 4. Metrics and tests
- H1: floor reached, paired by seed, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval. H2: wins, one-sided exact sign test at 0.05 on the seeds where exactly one arm wins; wins per arm with Wilson intervals (`tools/run_details.py --wins-vs S`).
- Secondary: act bosses beaten; the state at each boss fight's start; `ropt` decisions by screen and how often they differ from the rules; relics by source; seconds per run.
- What follows: `ropt` joins the stack if H1 or H2 holds. Run benchmark 14 measures gate G1 with the stack that results.

## 5. Results
None: withdrawn before its start (section 6).

## 6. Deviations and notes
- 2026-11-21, withdrawn before its start. Run benchmark 11's shop decisions showed that `rshop` buys nothing once more than 11 items are affordable, so the stack this benchmark would have tested events on has a known defect. Its question (H1 and H2 for `ropt` at A0) is one of the two factors of run benchmark 15, on new seeds (`RB015`), together with the repaired shop component. The `RB013` seeds were never used. The rule that fixes `S` (section 2) is kept.
