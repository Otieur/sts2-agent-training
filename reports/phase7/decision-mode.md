# Phase 7: Decision Mode, Sanitizer and First Policy in the Simulator

Date: 2026-11-20 · Game v0.111.1 (cc1f9462) · Host `sim/`, bridge `tools/sim.py` · Input: the one recorded fight so far (Test Subject, 45 events, 36 decision points). Machine under heavy unrelated load throughout.

## What exists now
- **Decision mode** (`sim/Session.cs`): rebuild the recorded fight up to any decision point, sanitize it, then `observe`, list `legal` actions and `step`. Actions: play a card (with target), end the turn, answer a card choice (`sim/Choices.cs` intercepts the game's selection commands). Not yet: potions; any other prompt is reported as `blocked`.
- **Sanitizer** (`sim/Sanitizer.cs`): every random generator reachable from the run and combat objects is given a fresh state from the sample seed, and the draw pile is shuffled. About 2 ms.
- **Bridge** (`tools/sim.py`): JSON lines to one host process; commands `smoke`, `fidelity`, `fairplay`, `planner`.
- **Observation** (`docs/observation-spec.md`): the live API's field names and values, so `tools/plan_turn.py` reads simulated fights unchanged.
- **Version check**: a recording from another game build or with another model list is refused on load.

## Checks
| Check | Result |
|---|---|
| Fidelity mode: recorded states (`tools/sim.py fidelity`) | 1 of 1 fights exact: 26 of 26 turn-boundary states, final HP 87/102 |
| Stepping path: the recording replayed with the host's own play and end-turn actions | won at HP 87, as recorded; 39 of 45 events driven by own actions (2 potions, 2 choices and 2 resumes applied as recorded) |
| Sanitizing leaves the observation unchanged | 96 of 96 (8 decision points, 12 seeds) |
| No generator keeps its state | 96 of 96 |
| Same sample seed, same hidden state and observation | 8 of 8 |
| Draw order changes with the seed | 84 of 84 |
| Leak canary: true next three draws reproduced | 0 of 84 samples |
| Planner's choice independent of the sample seed | 8 of 8 decision points |
| Step on an unsanitized state | refused |

## First policy in the simulator: the rule planner
`tools/sim.py planner --seeds 10 --mode safe`: `tools/plan_turn.py` chooses every action from the observation (first play of its top plan, then re-plan), from the first decision of the fight, on 10 sampled futures.

- **Won 1, lost 9** (final HP 36 in the win). 463 decisions in 8.2 s: 17.6 ms per decision, planner plus simulator plus bridge.
- The real fight was won at 87/102 with the language model choosing among the planner's plans, two potions, and Powers played early. In the simulator the planner has no potions, takes the first option at every card choice, and plans one turn at a time. So this is a baseline for the planner alone, on one boss; it is not a measure of the Agent.
- What it shows: the simulator can score a policy on futures the real game would take hours to produce, and the one-turn planner alone does poorly against a three-phase boss. That is the gap Phase 8's search is meant to close.

## Limits
- One recorded fight. Everything above is conditional on it; M11 needs 100 fights from real runs.
- Known draw-pile positions (a card the player put on top) are not kept by the sampler yet (FP-5).
- Hidden state pre-rolled into objects other than generators and the draw pile has not been inventoried (OQ7.3).
- Potions cannot be stepped; `legal` has not been compared with the live game's available actions.
- Branching is by replay from room entry; no state cloning.
- Start-up 16–40 s per host process.
