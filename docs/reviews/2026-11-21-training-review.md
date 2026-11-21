# Review of the project and the training plan, 2026-11-21

Asked for by the Player after run benchmark 8: no win in 30 whole new runs at Ascension 0. The question: does the training strategy need to change, and what is missing before the Agent can at least clear A0 reliably? This review looks at the evidence so far, the plan (`TRAINING_PLAN.md`, decision 0004) and how the work has been run. The proposed change of direction is in `docs/decisions/0005-a0-first-and-resource-use.md`.

## 1. Verdict in short
- **Yes, the strategy should change.** The simulator, the fight search and the rollout method are sound and stay. What is wrong is what they have been pointed at, and three basic resources the Agent does not use at all.
- **The Agent reaches bosses with too little power, not with too little HP.** At the act 1 boss it has half the upgrades of the Player (nearly all on Strikes), three relics against five, a full potion belt it never drinks from, and all its gold unspent. It arrives at 79% HP; the Player arrives at 56% and wins far more often.
- **Fight play is not the first problem.** On the Player's own recorded boss, elite and hallway situations, search does about as well as the Player did.
- **The rollouts are judged by the wrong fighter.** The rule planner fights inside them and search fights the real run, so rollouts prefer what the planner can use (HP, early attacks) and cannot see what search can use (upgrades, relics, scaling).
- **The ladder was skipped.** Benchmarks ran at A5 and A10 before A0 was ever measured. At A10 almost every run ends by floor 17, which leaves little signal for anything.

## 2. What is solid and stays
- **Simulator:** the game's own code, recorded fights exact (11 of 11), whole runs from a seed, a run copied at any decision with its unseen future re-sampled, fair-play checks. From run benchmark 5 on, search played every move of every fight (0 fallbacks in about 55,000 searched moves in run benchmarks 5–8).
- **Fight search at the Player's level on the same situations** (`data/sim/benchmark-v1.json`, decks built by the Player, mostly A8–A10; `vsearch-5b`, two games per fight):

| Room | Fights | The Player won | `mcw6` won (mean of two games) |
|---|---|---|---|
| Hallway | 30 | 30 | 29.5 |
| Elite | 20 | 17 | 16.5 |
| Boss | 10 | 4 | 3.5 (4.2 with 24 worlds, `boss-budget-1`) |

- **Rollout decisions beat rules wherever tested:** card rewards +5.5 floors against the first card (run benchmark 5, A5), map routes +1.1 (run benchmark 4, A5), both +2.8 at A10 (run benchmark 6); events, rest sites and card choices +3.0 floors in the first 35 seeds of run benchmark 9 (A10, still running, not a result yet).
- **Method:** pre-registered comparisons, paired seeds, failed experiments kept.

## 3. Findings

### F1. The Agent does not turn its resources into power
State at the start of the act 1 boss fight (the Agent: boss fight specs recorded in run benchmark 8, A0, 30 runs; the Player: `data/runs.db`, finished Ironclad runs on v0.107.1 that reached the act 1 boss):

| At the act 1 boss | Agent, A0 (30) | Player, A0–4 (8) | Player, A10 (19) | Player, won runs (12) |
|---|---|---|---|---|
| Beat the boss | 60% | 75% | 63% | 100% |
| Deck size | 17.8 | 19.9 | 20.3 | 19.5 |
| Upgraded cards | 2.3 | 5.1 | 3.6 | 5.4 |
| … of them on Strikes and Defends | 2.3 (68 of 70) | 0.4 | 0.1 | 0.7 |
| Relics | 3.2 | 5.3 | 5.2 | 5.0 |
| Potions used before the boss | 0 | 1.6 | 2.4 | 1.3 |
| Potions used in the boss fight | 0 | 1.6 | 1.3 | 1.3 |
| Potions in the belt at the fight's start | 2.8 of 3 | | | |
| Gold spent before the boss | 0 | 180 | 217 | 244 |
| Act 1 elites fought | 0.73 | 1.6 | 0.68 | 1.25 |
| Smith / heal at rest sites before the boss | not recorded | 4.0 / 0.1 | 2.8 / 0.5 | 3.8 / 0.3 |
| HP at the fight's start | 79% | 56% | 62% | 66% |

The Player's first upgrades in act 1 are Armaments (26), Bash (19), True Grit (13); the Agent's are Strike (65 of 70 in run benchmark 8). Runs in run benchmark 8 end with 462 gold on average. The Player uses 5.7 potions per Ironclad run.

Causes, all in the rule defaults (`tools/sim.py run_policy`, `tools/run_bench.py`):
- **Potions are never used in simulated runs.** Neither the search (`SearchCombat` calls `scored_search` without the room's potion setting) nor the planner gets potions as candidates inside runs. The fight-benchmark studies found no clear gain per fight from potions in search and concluded that drinking is a run-level question; inside runs that question was then left at "never", which is a dominated choice: with a full belt every further potion is thrown away.
- **Upgrades go to the first card in the deck** (a Strike), and the rest rule heals below 60% HP, so the Agent smiths less and on the wrong cards.
- **Shops are always left.** No purchase and no card removal has happened in any run benchmark arm since run benchmark 3.
- **Neow and the Ancients take the first option.**

### F2. Rule components were dropped without being tested alone
Run benchmark 2 tested `draft+shop+rest` as a bundle against `base`. The bundle lost because of the draft scorer, and the shop rule (card removal, one card) and the rest rule (heal thresholds, an upgrade priority list with Bash first) went out with it. They have never been tested on their own. Every later control arm carries these holes, so each comparison measured its hypothesis on top of a policy weak in unrelated ways.

### F3. Rollouts are judged by a different and weaker fighter than the one that plays
Inside rollouts the rule planner fights to the end of the act; in the real run search fights. On the benchmark the planner wins 3 of 20 boss games and 15 of 40 elite games, search 7 and 33. So a rollout's value mostly says how far the planner survives. Signs of this in the results:
- Route rollouts halve the elites fought and add no boss wins (run benchmark 4).
- Credit for boss damage in the rollout value changes nothing (run benchmark 7: 45 of 60 seeds end on the same floor). *Correction, 2026-11-21 17:50: the credit was never applied in that run (a defect in the benchmark tool; its report, section 6), so this point is withdrawn: the idea is untested.*
- In run benchmark 9's first 35 seeds the rollout arm brings fewer upgrades to the act 1 boss (1.5 against 2.2) and more HP (75% against 66%): it prefers healing to smithing, the opposite of the Player, who smiths four times and heals almost never before the act 1 boss at A0–4.
- The horizon is the end of the act, so upgrades, relics and removal that pay off later are undervalued.

Rollouts still beat the rules because the rules are so weak (F1), not because the rollout value is right.

### F4. The ladder was skipped and the metric is coarse
`TRAINING_PLAN.md` Phase 4 says: start at A0, move up after a win. The simulator work went straight to A5 and A10 (decision 0004: "target band Ascension 10, with Ascension 5 as a band that gives more signal"). A0 was first measured in run benchmark 8, the eighth run benchmark. At A10, 83% of runs reach the act 1 boss and 97% of those die there, so floors reached is nearly constant (45 of 60 pairs equal in run benchmark 7) and nothing after floor 17 is ever exercised. At A0 the runs spread over all three acts, which gives every decision type signal, and wins can be counted once there are any.

### F5. Nothing is learned yet at run level
Each decision is recomputed from nothing by rollouts (twice the time per run). No model accumulates experience across runs: decision 0004 step 5 (a run-state value network) and its "cheap deck evaluator" are not started, and the run benchmarks do not save what they would need (the value of every option at every rollout decision; every fight's starting situation with its outcome under search; only boss fights are recorded, since 10:09 today). About 7,000 search-played fights from run benchmarks 2–8 were recorded without the deck and relics they were fought with, and the option values of about 4,500 rollout decisions were not kept at all.

### F6. The automated stack has not been checked in the real game, and it ignores the written knowledge
The two real runs (A0 won, A1 lost at the act 1 boss with 3 elites killed in each) were played by the language model with the playbook, which says among other things "potions: use freely in elites and bosses" and carries upgrade priorities and boss plans. The automated stack uses none of that. One real win proves nothing, but the contrast (1 of 1 at A0 by hand, 0 of 30 automated in the simulator) points the same way as F1. No run-level comparison between the simulator and the real game exists yet.

### F7. Operations
- The queue died with the agent session at 11:26 (run benchmark 9 stopped at 35 of 60 seeds). Fixed: the queue now runs detached, and interrupted runs resume (`run_bench.py --resume`).
- Code was edited while a benchmark was running (08:12); the rule since then is no edits to the benchmark's modules during a run.
- A note in three registrations claimed runs are identical whichever worker plays a seed; that is true for fights but not for rollout sample seeds. Corrected in the registrations.
- The machine is shared (16 GB); worker counts follow memory, not cores.
- `docs/STATUS.md`'s header and the milestone table (M15–M18 missing from `TRAINING_PLAN.md`) were out of date.

## 4. What this says about the plan
- Decision 0004 (whole runs first, every decision type a training target) was right and its first three steps are done. Its order of attack was not: it moved the highest-variance decisions (cards, routes) to an expensive method first and left dominated defaults in place for potions, upgrades, shops and Neow, and it chose A10 and A5 as bands before A0 worked.
- The expected time to a usable agent does not get longer because of this review. The largest known gaps are now cheap ones (use potions, smith the right cards, spend gold), and each can be tested in about an hour at A0.
- What cannot be promised: that fixing them reaches a stable A0 clear. Bosses end 21 of 30 A0 runs, and after the resources are used, the rollout value (F3) is the next limit.

## 5. Proposed changes (decision 0005, for the Player to accept or change)
1. **A0 first.** One ascension at a time in the simulator. Gate G1: at least 50% wins on 60 new A0 seeds; gate G2: at least 63% (the Player's A0–4 rate), then A5, then A10. A10 is checked only at milestones.
2. **Wins are the primary metric** (with act bosses beaten); floors reached is secondary.
3. **Use every resource, one pre-registered test each at A0:** potions in fights inside runs; smith target and the heal threshold; shop purchases (run benchmark 10, moved to A0); Neow, Ancients and events (run benchmark 9's method, repeated at A0 if it holds). The control arm is always the best policy known so far, and bundled rules are tested one at a time.
4. **Make rollouts reflect the real fighter:** record every fight's starting situation and its outcome under search, and every rollout decision's option values, in all run benchmarks from now on; train a fight-outcome model (win probability and HP lost for a deck, relics, potions, HP and encounter as fought by search); use it instead of planner fights inside rollouts, which also makes whole-run horizons affordable; then the run-state value network of decision 0004 step 5. This is the first step that is training in the real sense, and the one where a GPU helps.
5. **Boss fights:** boss replay 1 (queued) decides whether a larger search budget for bosses and elites is worth testing in runs. Normal rooms keep the full search in every case.
6. **Real-game check at G1:** five real A0 runs on profile 2 with the same stack, with the Player present, compared with the simulator's prediction.
7. **Operations:** detached queue, no edits during runs, data kept from every benchmark.

## 6. What is still unknown
- How much each resource is worth: the per-fight potion studies found little; whole runs may differ. Each fix is a test, not an assumption.
- Whether search's parity with the Player on fights holds for the Agent's own decks (boss replay 1).
- Whether a fight-outcome model can be made accurate enough from about 10,000 fights; it needs a calibration check on held-out fights before it replaces anything.
- Whether simulated whole-run results carry over to the real game (item 6).
