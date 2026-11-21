# Measurement: gate G1, the win rate of whole new runs at Ascension 0 (run benchmark 14)

Written before the run (decision 0005 item 1, ML-10), 2026-11-21 at 12:10, after the results of run benchmarks 2–9 and before any result of run benchmarks 11, 12 and 13. A measurement of one policy, like run benchmark 8. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Question
- Does the run policy supported by run benchmarks 11–13 pass gate G1 of decision 0005: at least 50% wins in 60 whole new runs at Ascension 0?

## 2. Runs
- 60 new seeds (`RB014` + index 00000–00059), Ironclad, **Ascension 0**, whole new runs from Neow to death or victory in the simulator (`tools/run_bench.py`). One policy.
- Policy: `S` as fixed in run benchmark 13's registration (from run benchmarks 11 and 12), plus `ropt` if run benchmark 13's H1 or H2 holds. Computed by the queue script before any result of this run.
- Combat: `mcw6` in every fight, `--fight-rebuild save+run`. Host: the Release2 build, unchanged. 7 workers claim seeds in index order (`--dynamic`). Stopping rule: unfinished runs stop 6 hours after the start; the analysis uses the finished runs.
- Fights and rollout decisions are recorded as in run benchmark 11.

## 3. Policy
- Every decision the Agent's own: card rewards and map moves by rollouts, the components in `S`, search in every fight; whatever is not in `S` stays with the rules of run benchmark 8.

## 4. Metrics
- Primary: wins out of finished runs with a Wilson 95% interval. **G1 is passed with at least 30 wins in 60 runs.**
- Secondary: mean and median floor; act bosses reached and beaten per act and per boss; where runs die; the state at each boss fight's start (upgrades, relics, potions, HP); potions used; purchases and gold left; elites fought; seconds per run; search fallbacks.
- Reference, not a test: run benchmark 8 (the policy before decision 0005: 0 wins in 30, mean floor 26.5) and the Player's A0–4 runs (5 wins in 8).
- What follows: if G1 is passed, gate G2 (63%) and the real-game check (five real A0 runs, decision 0005 item 6) are next. If not, where the runs die decides the next target, and the fight-outcome model for rollouts (decision 0005 item 4) is the main line.

## 5. Results
Pending.

## 6. Deviations and notes
