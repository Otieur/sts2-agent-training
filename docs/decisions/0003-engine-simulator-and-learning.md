# 0003: Real-engine simulator, search and learned models

Date: 2026-11-19 · Status: **accepted as direction** (the Player asked for it on 2026-11-19); each phase is gated by the previous phase's exit gate. Phase 7 starts with a feasibility spike whose result can change the route (R3 or R4) but not the direction.

## Context
- The final goal is an AI that clears A10 with a high win rate (M8, then M9 and beyond) and plays fast.
- Today every decision goes through the language model: the first Agent run took 599 actions in 120 minutes. The tools take about 0.1 s per call; the rest is model round trips and game animations. That is fine for finding gaps and writing rules, not for a finished product.
- The training plan until now had no learned components: "learning" meant written playbooks, knowledge files, post-mortems and statistics (`TRAINING_PLAN.md` §1). Reinforcement learning needs on the order of 10⁵–10⁷ fights or runs; the real game, even fully automated, gives tens of runs a day.
- The desk study ([proposals/engine-simulation-spike.md](../proposals/engine-simulation-spike.md)) found that the game's combat logic is deterministic, replayable from room entry with checksums, and rarely calls the Godot engine. So it may be able to run outside the game.
- Our own simulator (`tools/simulate_fight.py`) covers a fraction of the cards, relics, potions and powers, and would need re-work every patch.

## Options
1. **Keep the language model in the loop** for every decision; improve rules and tools. Simple, but slow and capped by rule quality.
2. **Our own simulator** (extend `simulate_fight.py` or write a new one). Full control, but hundreds of card, relic, power and monster behaviours to port and keep current with every patch; fidelity is never exact.
3. **The game's own engine, in our own process** (route R3): load `sts2.dll`, stub the few engine and platform calls, run combat headless. Exact game logic; fast if the spike succeeds.
4. **The game's own engine in an offline headless game instance** (route R4): the real game binary as a simulation server. Exact, slower per simulation, heavier.

## Decision
Build on the **game's own engine** (option 3, falling back to option 4), in three phases:

| Phase | Goal | Exit gate in short |
|---|---|---|
| [7: Engine simulator](../phase-7-engine-simulator.md) | The game's combat logic runs in our own process, matches the game exactly on recorded fights, at a few milliseconds per fight, with a fair-play layer that re-samples hidden information | Fidelity suite passes; speed target met; integrity tests pass |
| [8: Combat search and autopilot](../phase-8-combat-search.md) | Search over the simulator replaces the language model for combat decisions; live combat runs without model calls | Beats the current planner in simulation and in real fights; under 1 s per decision |
| [9: Learned models and reinforcement learning](../phase-9-learning.md) | Neural value and policy models for combat, then learned strategic decisions on a run-level simulator; self-play training | Learned components beat the rule-based ones in pre-registered A/B tests; M8, then M9 |

The language model stays for what it does well: reviewing runs, writing and checking rules, unusual situations, co-op communication, and supervising the automated components.

All three phases follow [simulator-integrity.md](../simulator-integrity.md). Its fair-play rules are part of this decision: a decision may use only what a player can see, and a simulator built on the real engine must re-sample every hidden random stream for decisions.

## Spike verdict (2026-11-19)
**Go, route R3.** The host in `sim/` loads the game's assemblies, starts the model database (hash equal to the game's), rebuilds a recorded boss fight and replays it: all 26 turn-boundary states equal the game's recorded states and the final HP matches the real run. Saves and the install were untouched. Not yet shown: per-fight speed once warm (one cold pass took 1.4–1.6 s under heavy load; start-up about 30 s) and fidelity beyond one fight. Details: `reports/phase7/spike.md`.

## Consequences
- New phase documents 7–9, STATUS rows, milestones M10–M14 in `TRAINING_PLAN.md`.
- Phases 4–6 continue in parallel: real runs supply replays (ground truth) and evaluation. Scored runs follow the integrity rules ML-5 to ML-8.
- Downloaded libraries for learning (a neural-network framework) need a security review and the Player's approval before Phase 9 builds anything with them (SA-8).
- If both R3 and R4 fail the spike, fall back to option 2 limited to the encounters that matter most (bosses, elites), with the replay corpus as the test set, and record a new decision.
- Every game patch costs a fidelity re-check before simulator results are used again (FI-4).
