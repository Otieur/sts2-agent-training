# Comparison: potions, the smith rule and shop purchases removed one at a time at Ascension 0 (run benchmark 12)

Written before the run (decision 0005 item 3, ML-10), 2026-11-21 at 11:53, together with run benchmark 11 and before any of its results. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypotheses
With `F` = `Y+pot+smith+rshop`, the treatment arm of run benchmark 11:
- **H1 (potions):** `F` reaches more floors than `F` without `pot`.
- **H2 (smith rule):** `F` reaches more floors than `F` without `smith`.
- **H3 (shops):** `F` reaches more floors than `F` without `rshop`.

Why: run benchmark 11 turns three components on at once; this run tells which of them carry the effect, each in the presence of the other two (a rule tested only in a bundle was the mistake of run benchmark 2).

## 2. Runs
- The same 30 seeds as run benchmark 11 (`RB011` + index 00000–00029), Ironclad, **Ascension 0**. Three arms per seed: `Y+smith+rshop`, `Y+pot+rshop`, `Y+pot+smith`. Each is compared with the `F` arm of run benchmark 11 on the same seed.
- Everything else as in run benchmark 11 (combat `mcw6`, `--fight-rebuild save+run`, Release2 host, 7 workers with dynamic seed claiming, the same component definitions, data recording). Without `smith`, rest sites and upgrades go back to `Y`'s way (rollouts if `ropt` is in `Y`, otherwise heal below 60% HP and smith the first card).
- Starts when run benchmark 11 has finished (queue). Stopping rule, fixed in advance: unfinished runs stop 6 hours after the start; each comparison uses the seeds finished in both runs.
- A seed's rollouts use sample seeds that depend on the worker's history (see run benchmark 9, section 6), so arms on the same seed share the run's true future but not the sampled futures inside rollouts.

## 3. Policies
- As defined in run benchmark 11, section 2.

## 4. Metrics and tests
- For each hypothesis: floor reached, paired by seed with run benchmark 11's `F` arm, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval (`tools/run_ablation.py`). Three tests, reported without correction; 30 seeds detect only large effects.
- Secondary: wins per arm with Wilson intervals; act bosses beaten; the state at each boss fight's start (upgrades, relics, potions, HP); potions used; purchases and gold left; where runs die.
- What follows: a component stays in the run policy if `F` is ahead of its drop-one arm in mean floors; a component whose removal does better is taken out and examined before any re-test. The stack that results is the one measured against gate G1.

## 5. Results
Run 2026-11-21 14:39–16:49 (30 of 30 seeds in every arm, 7,819 s, 7 workers, code `6565f85`; no mismatches; one search error, see section 6). The `F` column is run benchmark 11's treatment arm on the same seeds.

| | `F` (run benchmark 11) | without `pot` | without `smith` | without `rshop` |
|---|---|---|---|---|
| Mean floor (median) | 30.90 (32) | 24.07 (23) | 28.67 (31) | 27.87 (32) |
| Wins | 1 of 30 | 0 of 30 (Wilson 95% 0–11%) | 0 of 30 | 0 of 30 |
| Act 1 boss beaten | 25 of 30 | 16 of 30 | 24 of 29 | 19 of 30 |
| Act 2 boss beaten | 6 of 15 | 0 of 8 | 1 of 14 | 4 of 15 |
| Act 3 boss beaten | 1 of 3 | – | 0 of 1 | 0 of 2 |
| Potions used per run | 5.73 | 0.03 | 5.60 | 5.13 |
| Upgrades at the act 1 boss (of them on Strikes and Defends) | 3.07 (0.17) | 2.90 (0.13) | 2.72 (2.55) | 2.83 (0.17) |
| Upgrades at the act 2 boss (of them on Strikes and Defends) | 7.33 (0.60) | 6.62 (1.00) | 5.86 (3.93) | 6.60 (0.47) |
| Relics at the act 1 boss | 3.37 | 3.30 | 3.28 | 2.97 |
| Elites fought per run | 1.27 | 0.93 | 1.03 | 0.90 |
| Shop purchases per run | 1.07 cards, 0.17 potions, 0.03 removals | 0.90 cards | 0.77 cards, 0.10 potions, 0.07 removals | none |
| Gold left at the end | 503 | 403 | 480 | 490 |
| Seconds per run | 620 | 358 | 628 | 551 |

`F` minus each drop-one arm, paired by seed (`tools/run_details.py --pair`):

| Component | Mean floors | Better / worse / equal | One-sided sign test | Bootstrap 95% |
|---|---|---|---|---|
| `pot` | +6.83 | 18 / 6 / 6 | p = 0.011 | 3.2 to 10.6 |
| `smith` | +2.23 | 14 / 9 / 7 | p = 0.20 | −1.3 to 5.9 |
| `rshop` | +3.03 | 11 / 10 / 9 | p = 0.50 | −0.6 to 6.9 |

- **H1 (potions): the registered test passes, on a comparison that carries a second difference (correction in section 6).** Without potions the stack falls back to where `rcard+rpath` alone stood in run benchmark 11 (24.07 against 23.87 floors, the act 1 boss beaten in 16 runs in both): the smith rule and shop purchases add nothing measurable unless the fight search also drinks.
- **H2 (smith rule) is not shown.** The mean is +2.2 floors with an interval that includes zero. Where it shows is the act 2 boss: beaten in 1 of 14 fights without the rule against 6 of 15 with it, while the act 1 boss falls equally often (24 of 29 against 25 of 30). Without the rule 2.55 of 2.72 upgrades before the act 1 boss go to Strikes and Defends.
- **H3 (shops) is not shown.** The mean is +3.0 floors, and as many seeds are worse as better (10 against 11). The arm without shop purchases beats the act 1 boss in 19 of 30 runs against 25 of 30; the purchases are about one card per run and cost little (gold left 490 against 503). The component barely acts above 180 gold (run benchmark 15, section 1), so this says little about what shops are worth.
- Where runs end. Without `pot`: act 1 boss 14, act 2 boss 8, act 2 hallways 7, act 2 elite 1. Without `smith`: act 2 boss 13, act 2 hallways 7, act 1 boss 5, act 2 elites 3, act 1 elite 1, act 3 boss 1. Without `rshop`: act 1 boss 11, act 2 boss 11, act 2 elites 2, act 2 hallways 2, act 3 hallways 2, act 3 boss 2.
- No drop-one arm wins a run; `F` won one. No claim about wins.
- Verdict, by the rule of section 4: `F` is ahead of each drop-one arm in mean floors, so all three components stay and the stack is `rcard+rpath+pot+smith+rshop`. Potions most likely carry most of the gain of run benchmark 11; by the correction in section 6 no component has a clean test here. Gate G1 is not measured on this stack (one win in 30; run benchmark 14 is deferred until a 30-seed benchmark shows at least 12 wins); run benchmark 15 tests the shop repair and events by rollouts on it.

## 6. Deviations and notes
- 2026-11-21 13:37, pause: the first start (13:34) was stopped after two minutes, before any seed finished, because the machine was about to sleep (the Player closing the lid). The run starts again from seed 0 with the same arguments and a deadline of its new start + 6 h (`data/learn/queue/queue5b.sh`). Before the restart the host call timeout in `tools/sim.py` was moved to the monotonic clock, which stands still while the machine sleeps: on the wall clock, every call under way during a sleep longer than its timeout would have failed on waking. Nothing else in the run code (`run_bench.py`, `run_eval.py`, `run_opts.py`, `sim.py`) differs from run benchmark 11's.
- Rule for sleeps, fixed before any seed of this run finished: time asleep does not count towards the deadline. If the deadline cuts the run short after a sleep, the run is resumed with `--resume` and a deadline moved by the time asleep. `seconds` of a seed under way during a sleep includes the time asleep and is not used in any comparison.
- 2026-11-21 16:55, analysis tool: section 4 names `tools/run_ablation.py`, which was never written. The registered test (floors paired by seed with run benchmark 11's `F` arm, one-sided sign test, bootstrap interval) is computed by `tools/run_details.py --pair`, written before this run's results.
- One search error in 20,685 searched decisions: seed `RB01100022`, arm without `rshop`, the act 1 boss fight, decision 37 (`a card choice is pending: answer it first`). That decision was played by the rule planner; the fight was won and the run ended at the act 2 boss. The cause is open (a step sent while a card choice was pending); it does not bear on the comparison.
- 2026-11-21 17:50, correction, found while preparing run benchmark 16: **the three comparisons are not clean drop-one comparisons.** A worker keeps one rollout evaluator per kind of decision for its whole life and plays every arm of a seed in turn. Until 2026-11-21 an evaluator kept the settings (the rollout policy and the boss credit) of the first policy that used it (`tools/run_bench.py`: created once, `if _CARD_EVALUATOR is None`), so in a benchmark whose arms differ in either, every arm's card and route rollouts ran with the first arm's settings. Here the first arm of every seed was `rcard+rpath+smith+rshop`, so the card and route rollouts of all three arms were played by `path+smith`, and those of run benchmark 11's `F` arm by `path` (its own correction). Each difference in section 5 therefore has two parts: the component removed from the run itself, and rollouts played with the smith rule (the three arms here) against rollouts played with the old rest rule (`F`). In none of the four arms did card or route rollouts use potions. The numbers stand as measured. Reading: the arm without potions is level with `rcard+rpath` (24.07 against 23.87 floors) and 6.8 floors below `F`, a gap the size of run benchmark 11's whole effect, so potions in the run's own fights remain the likely carrier; the smaller differences for the smith rule and shops (2.2 and 3.0 floors, neither passing its test) cannot be told from the effect of the rollout policy. The stack rule used mean floors and kept all three; that choice stands as the rule's outcome, and run benchmark 15 tests the stack with rollouts played by its own rules. Fixed in `tools/run_bench.py` (`set_evaluator`).
