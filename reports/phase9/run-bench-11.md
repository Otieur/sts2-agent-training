# Comparison: using every resource at Ascension 0 (run benchmark 11)

Written before the run (decision 0005 item 3, ML-10), 2026-11-21 at 11:53, after the results of run benchmarks 2–8 and the review of 2026-11-21, and after run benchmark 9 (its H1 did not hold by the registered test, so `Y` is `rcard+rpath`). Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypotheses
- **H1 (floors):** at Ascension 0, the run policy with potions used in fights, the smith-first rest rule and shop purchases by rollouts (`Y+pot+smith+rshop`) reaches more floors than the same policy without them (`Y`).
- **H2 (wins):** it wins more runs.

Why: the review of 2026-11-21 (`docs/reviews/2026-11-21-training-review.md`, F1) found that the Agent reaches bosses with far less power than the Player while holding more HP: potions are never used in simulated runs, upgrades go to the first card (a Strike) and rest sites heal below 60% HP, and shops are always left (462 gold unspent per run at A0). Run benchmark 8 found no win in 30 runs at A0 with bosses ending 21 of them. Each of these defaults wastes a resource; this comparison turns all three on at once to see whether that produces wins, and run benchmark 12 removes them one at a time.

## 2. Runs
- 30 seeds (`RB011` + index 00000–00029), Ironclad, **Ascension 0**, whole new runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- `Y`: `rcard+rpath`, plus `ropt` if run benchmark 9's H1 holds (one-sided sign test p < 0.05 with a positive mean difference); chosen by the queue script from that manifest.
- Combat in both arms: `mcw6` in every fight, `--fight-rebuild save+run`; mismatches and failures fall back to the planner (counted).
- `pot`: potions may be used in fights. In elite and boss fights search adds every usable potion (one per distinct potion and target) to its candidates; in hallway fights it considers the planner's potion plans. A spent potion is priced as lost HP by room (hallway 25, elite 6, boss 2; `tools/sim.py POTION_PRICE`, fixed since the fight studies of 2026-11-20). The planner (search fallbacks, and every fight inside rollouts) uses its potion plans at the same prices.
- `smith`: rest sites heal only below 35% HP (below 50% at the last rest site before a boss), otherwise smith; every upgrade choice follows the upgrade priority list (Bash, then the draft tiers, Strikes and Defends last; `Policy.upgrade_pick`). With `ropt` in `Y`, rest sites and upgrade choices follow this rule instead of rollouts. The thresholds are fixed before the run: the Player's A0–4 runs smith 4.0 times and heal 0.1 times before the act 1 boss.
- `rshop`: shop purchases by sampled rollouts, one purchase at a time, as registered for run benchmark 10 (leave, or buy one affordable item; ties and failures to leaving; more than 12 options left to the rule).
- Rollouts in both arms are played by the arm's own rules (for the treatment arm `path+pot+smith`: the planner drinks potions and the rest rule smiths inside rollouts too).
- Code note: from this run on, the planner inside runs (fights in rollouts, search fallbacks) aims at the target its plan names. Until now a planner action that did not match a legal action exactly (most plays, because legal actions carry the card id) was replaced by the first legal play of the same card, whatever its target, so multi-enemy fights hit the first enemy. Found and fixed on 2026-11-21 (`tools/sim.py run_policy`); it applies to both arms.
- Host: the Release2 build (`sim/bin/Release2`), unchanged. 7 workers claim seeds in index order (`--dynamic`). Stopping rule, fixed in advance: unfinished runs stop 5 hours after the start; the analysis uses the seeds for which both policies finished.
- Every fight's starting situation with its outcome, and every rollout decision with its options' values, are recorded for later model training (decision 0005 item 4); recording does not change play.
- Smoke tests before registration on two other seeds (`RB921…` with planner combat, `RB922…` with search): plumbing only, outcomes not used.

## 3. Policies
- `Y`: card rewards and map moves by rollouts (and events, rest sites and card choices if `ropt` is in it); no potions; shops left; rest below 60% HP, else smith the first card (or by rollouts with `ropt`).
- `Y+pot+smith+rshop`: as above with the three components.
- Both: Neow, Ancients, boss relics and potion rewards by the first option and other events by the Player's most frequent choice, unless `ropt` is in `Y`.

## 4. Metrics and tests
- H1: floor reached, paired by seed, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval (`tools/run_bench.py --report … --baseline Y`).
- H2: wins, paired by seed: one-sided exact sign test at 0.05 on the seeds where exactly one arm wins; wins per arm with Wilson 95% intervals.
- Secondary: act bosses reached and beaten per act; where runs die; at each boss fight's start the upgrades (and how many on Strikes and Defends), relics, potions held, HP; potions used per run and per room type; purchases per run by kind and gold left; elites fought; seconds per run; search fallbacks.
- Reference, not a test: the Player's A0–4 runs (5 wins in 8; at the act 1 boss 5.1 upgrades, 5.3 relics, 3.2 potions used, 180 gold spent, 56% HP).
- What follows: if H1 holds, the three components join the run policy subject to run benchmark 12 (one removed at a time), and gate G1 of decision 0005 (at least 50% wins on 60 new A0 seeds) is measured with the resulting stack. If H1 does not hold, run benchmark 12 shows which component hurts, and the fight-outcome model for rollouts (decision 0005 item 4) moves first.

## 5. Results
Run 2026-11-21 12:12–13:34 (30 of 30 seeds, 4,894 s, 7 workers, code `00d7251`; no search errors, fallbacks or mismatches in either arm).

| | `rcard+rpath` | `rcard+rpath+pot+smith+rshop` |
|---|---|---|
| Mean floor (median) | 23.87 (21.5) | 30.90 (32) |
| Wins | 0 of 30 (Wilson 95% 0–11%) | 1 of 30 (1–17%) |
| Act 1 boss beaten | 16 of 29 | 25 of 30 |
| Act 2 boss beaten | 1 of 8 | 6 of 15 |
| Act 3 boss beaten | 0 of 1 | 1 of 3 |
| Potions used per run (hallways / elites / bosses) | 0 | 5.73 (1.10 / 1.77 / 2.87) |
| Upgrades at the act 1 boss (of them on Strikes and Defends) | 2.07 (1.93) | 3.07 (0.17) |
| Upgrades at the act 2 boss (of them on Strikes and Defends) | 4.62 (2.50) | 7.33 (0.60) |
| Shop purchases per run | 0 | 1.07 cards, 0.17 potions, 0.03 removals, no relics |
| Gold left at the end | 482 | 503 |
| Seconds per run | 336 | 620 |

- **H1 holds.** Treatment − baseline: +7.03 floors (21 better, 4 worse, 5 equal; one-sided sign test p = 0.00046; bootstrap 95% 3.0 to 11.0).
- **H2 is not shown.** Wins 1 against 0 (one discordant seed, p = 0.5).
- Where runs end. Treatment: act 2 boss 9, act 1 boss 5, act 2 elites 5, act 2 hallways 5, act 3 hallways 3, act 3 boss 2. Baseline: act 1 boss 13, act 2 boss 7, act 2 hallways 6, act 2 elites 2, act 1 elite 1, act 3 boss 1.
- Gold is still unspent. Shop rollouts buy about one card per run and almost never a removal or a relic, and 503 gold is left at the end: the shop component as built barely acts. Run benchmark 12 shows whether it adds anything; the unspent gold stays an open gap against the Player (about 180 gold spent before the act 1 boss).
- Verdict: potions, the smith rule and shops together move the agent from dying at the act 1 boss to dying in act 2. That is a large gain and still far from gate G1 (50% wins). As registered, the three components join the run policy subject to run benchmark 12.

## 6. Deviations and notes
