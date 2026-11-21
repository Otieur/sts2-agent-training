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
Pending.

## 6. Deviations and notes
