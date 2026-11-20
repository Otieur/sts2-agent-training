# Comparison: <policy A> against <policy B>

Written before the run (P8.E1.S3, ML-10). Do not edit sections 1–4 after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
<One sentence: what is expected and by how much, for example "B loses at least 2 HP less per fight than A on the hallway set".>

## 2. Fights
- Benchmark set and version: <`data/sim/benchmark-v<n>.json`, or a named exploratory set such as "fights from nothing, starting deck">
- Encounters and room types: <list or rule>
- Run seeds and sample seeds: <ranges>
- Exam seeds excluded: <yes / not applicable> (ML-7)
- Simulator header: game build, host commit, fidelity result at that commit (P7.E5.S4)

## 3. Policies and budgets
- A: <name, mode, parameters>
- B: <name, parameters: candidates, worlds per candidate, depth, time budget>
- Both play the same fight (same run seed and sample seed); decisions use only what the player can see (FP-1, FP-15)

## 4. Metrics and test
- Primary: <HP lost per fight, or value = HP left after a win and a fixed penalty for a loss>
- Secondary: win rate, potions used, turns, decision time
- Test: paired by fight and seed; sign test on better/worse pairs and the mean paired difference with a bootstrap interval
- Margin that counts as a result: <for example 2 HP per fight, or a sign-test p below 0.05>
- Number of fights fixed in advance: <n>; no stopping early on a good result

## 5. Results
<Filled after the run: the summary lines, the table, the test.>

## 6. Deviations and notes
<Anything that changed after the run started, and why.>
