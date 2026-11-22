# Comparison: credit for progress against a boss in the rollout value, at Ascension 0 (run benchmark 17)

Written before the run (decision 0005 item 3, ML-10), 2026-11-21 at 18:08, after the results of run benchmarks 2–9, 11 and 12 and before the results of run benchmarks 15 and 16 (of run benchmark 15, the floors of its first two seeds had been seen in the queue's log). Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypotheses
- **H1 (floors):** at Ascension 0, rollouts whose value credits progress against a boss (`bc`) reach more floors than the same rollouts without the credit.
- **H2 (wins):** they win more runs.

Why: a rollout's value is the floors it climbs plus a bonus for beating the act's boss. Inside rollouts the rule planner fights and rarely beats a boss, so most rollouts that reach the boss end with the same value whatever the deck holds: in run benchmark 11 every option has exactly the same value in 13% of card decisions and 4% of route decisions, and in a shop two floors before the act 2 boss all 15 options tied (run benchmark 15, section 6). With the credit, a rollout that dies in a boss fight also gets 5 times the fraction of the boss fight's enemy HP it removed, so a deck that nearly kills the boss is worth more than one that does not scratch it. Run benchmark 7 was meant to test this at A10 and did not: its treatment arm ran without the credit (its section 6), so the idea is untested. Act 2 bosses end 9 of 30 runs of the current stack and act 1 bosses 5.

## 2. Runs
- 30 new seeds (`RB017` + index 00000–00029), Ironclad, **Ascension 0**, whole new runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- `T`: the stack after run benchmark 16 by that registration's rule (`data/learn/queue/stack2.py after-route`), fixed by the queue script before any result of this run. Arms: `T`, `T+bc`.
- `bc` (`tools/run_eval.py`, weight `BOSS_CREDIT` = 5): in every rollout of the arm (card rewards, map moves, and shops and events if rollouts judge them), a rollout that dies in a boss fight gets 5 times the fraction of that fight's killable enemy HP it removed; a won run counts as beating the act's boss. Nothing else changes: the rollouts are played by the same rules with the rule planner fighting.
- Each arm's rollouts use that arm's own settings (`tools/run_bench.py set_evaluator`, the fix for the defect that voided run benchmark 7; a unit test checks that two policies in one worker get their own rollout policy and credit).
- Combat in both arms: `mcw6` in every fight, `--fight-rebuild save+run`. Host: the Release2 build, unchanged. 7 workers claim seeds in index order (`--dynamic`). Stopping rule: unfinished runs stop 5 hours after the start; time the machine is asleep does not count (the rule of run benchmark 12, section 6). The analysis uses the seeds for which both policies finished.
- Fights and rollout decisions are recorded as in run benchmark 11.

## 3. Policies
- `T`: rollout value = floors climbed, plus 5 + 5 × HP fraction left if the act's boss is beaten.
- `T+bc`: the same plus the boss credit.

## 4. Metrics and tests
- H1: floor reached, paired by seed (`T+bc` − `T`), one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval. H2: wins, one-sided exact sign test at 0.05 on the seeds where exactly one arm wins; wins per arm with Wilson intervals (`tools/run_details.py --wins-vs`).
- Secondary: boss fights won by act; how often all options of a decision have the same value, by kind of decision (`tools/run_details.py --decisions`); how often the choice differs from the rule's; relics, upgrades, potions and HP at each boss fight's start; where runs die; seconds per run.
- A check that the treatment was applied (the lesson of run benchmark 7): every recorded decision carries the rollout policy and the credit its evaluator used, read from the evaluator after it ran (`rollouts_by`, `boss_credit`); they must be the arm's own in every decision of both arms (`tools/run_details.py --decisions`, `rollout_settings_used`). The share of decisions where all options tie is reported per arm.
- What follows, the stack that runs next: `bc` enters if its mean paired difference in floors is positive and it does not win fewer runs. A claim that it helps needs its test.

## 5. Results
Pending.

## 6. Deviations and notes
- 2026-11-21 22:46, before the start: this run moves behind run benchmarks 18 and 16, and it runs only if `rfm` (fights inside rollouts ended by the fight-outcome model) is not in the stack after them: the boss credit applies to rollouts that play the boss fight and die in it, and has no meaning in rollouts that do not play it. If `rfm` is in the stack, this registration is withdrawn unrun and the seeds `RB017` stay unused. Host: the Release3 build, as for run benchmark 16. Nothing of this run was known.
- 2026-11-22 04:45, before the start, nothing of this run known: this run also moves behind run benchmark 19 (elites fought while healthy, healing before a boss). `T` is the stack after run benchmark 19 by that registration's rule (`data/learn/queue/stack3.py after-elbr`), or the stack after run benchmark 16 if 19 does not run. 9 workers, a shared evaluation host, and the main process ending workers still running 10 minutes after the deadline, as for run benchmark 16 (its section 6, 02:20 and 04:45). The condition of 22:46 stands: if `rfm` is in the stack, this registration is withdrawn unrun.
- 2026-11-22 05:30, before the start: run benchmark 18 is finished and `rfm` is not in the stack (its section 5), so this run takes place. It is played with the two changes to `tools/run_bench.py` described in section 6 of run benchmark 19 (05:30): a decision's sampled futures are numbered inside the run, and a fight past turn 100 is given up and the run counted with the floor it stands on. Nothing of this run or of run benchmarks 16 and 19 is known.
- 2026-11-22 06:05, before the start: the host is the Release4 build (a shop's card removal once a shop, as in the game; `docs/simulator-integrity.md` FI-7e; checks in section 6 of run benchmark 19, 06:05), not Release3.
- 2026-11-22 07:45, before the start: the host is the Release5 build, in which a relic picked from a chest reaches the player (`docs/simulator-integrity.md` FI-7f; checks in section 6 of run benchmark 19, 07:45). The boss credit was fitted on runs without chest relics; it is tested here as registered.
