# 0005: Ascension 0 first; use every resource; rollouts that reflect the real fighter

Date: 2026-11-21 · Status: **proposed** (awaiting the Player; written after the review `docs/reviews/2026-11-21-training-review.md`, which the Player asked for when run benchmark 8 found no win in 30 whole new runs at A0). Amends decision 0004: its primary metric (whole runs with search in every fight) and its decision types stay; the target band, the order of work and the rollout fighter change.

## Context
- At A0 the Agent wins 0 of 30 simulated runs; bosses end 21 of them. At A10 it reaches the act 1 boss in 83% of runs and beats it in 3%.
- At the act 1 boss it has 2.3 upgrades (68 of 70 on Strikes and Defends) against the Player's 5.1 at A0–4, 3.2 relics against 5.3, no potion used against 3.2, no gold spent against 180, and 79% HP against 56%. In simulated runs potions are never used, shops are always left, upgrades go to the first card, Neow and the Ancients take the first option.
- With the Player's decks, search fights about as well as the Player did (bosses 3.5 of 10 against 4, elites 16.5 of 20 against 17, hallways 29.5 of 30 against 30).
- Inside rollouts the rule planner fights; in the run, search does. Rollout values therefore reward HP and early attacks and miss upgrades, relics and scaling (run benchmarks 4 and 7; run benchmark 9's first seeds).
- Benchmarks ran at A5 and A10 before A0 was measured; at A10 floors reached is nearly constant.

## Decision
1. **Ladder in the simulator, one ascension at a time, starting at A0.** Gate G1: at least 50% wins on 60 new A0 seeds. Gate G2: at least 63% (the Player's A0–4 rate). Then A5 (bar 25%), then A10 (bar 8%). Higher ascensions are measured only at milestones until the gate below them is passed.
2. **Primary metric: wins,** with act bosses beaten; floors reached is secondary. Tests stay paired by seed and pre-registered (ML-10).
3. **Use every resource.** One pre-registered test each at A0, the control arm always the best policy known, components one at a time: potions in fights inside runs; smith target and heal threshold at rest sites; shop purchases and card removal; Neow, Ancients and events.
4. **Rollouts that reflect the real fighter.** From now on every run benchmark records each fight's starting situation with its outcome under search, and each rollout decision's option values. A fight-outcome model (win probability and HP lost given deck, relics, potions, HP, encounter and ascension, as fought by search) is trained on that data and checked for calibration on held-out fights; it then replaces planner fights inside rollouts (pre-registered against the current rollouts), which also allows whole-run horizons. The run-state value network of decision 0004 step 5 follows.
5. **Boss fights.** Boss replay 1 decides whether a larger search budget for bosses and elites is tested in runs. No room type ever gets less search than it has now (the Player's decision of 2026-11-21).
6. **Real game.** At G1, five real A0 runs on profile 2 with the same stack, the Player present, compared with the simulator's prediction. The scored ladder of decision 0004 item 5 keeps its bars.

## Consequences
- Run benchmark 10 (shop purchases) moves from A10 to A0 before it starts; run benchmark 9 and boss replay 1 finish as registered.
- New milestones: M19 simulated A0 win rate at least 50% (G1); M20 at least 63% (G2); M21 five real A0 runs with the automated stack. M17 and M18 (A5 above 25%, A10 above 8%) follow them.
- More data is written per benchmark (fight situations, option values); nothing personal is in it.
- A GPU becomes useful at step 4 (model training); the simulator stays on the local machine.
