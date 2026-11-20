# Phase 8: Combat Search and Autopilot

**Goal:** search over the Phase 7 simulator, in decision mode, chooses combat actions better than the current rule-based planner (`tools/plan_turn.py`) and fast enough that live combat needs no language-model calls. Target: milestones M12 and M13.

**Depends on:** Phase 7 epics P7.E3–P7.E6 (host, sandbox, combat interface, fidelity suite, fair-play layer). The P7.E7.S1 benchmarks size the search budget.
**Unblocks:** Phase 9 (search provides training targets and the baseline to beat). Speeds up Phases 4–6, because combat is most of a run's actions.
**Rules:** [simulator-integrity.md](simulator-integrity.md), especially FP-1 to FP-15 (what search may know) and ML-5 to ML-10 (evaluation).

---

## 1. What to expect

| | |
|---|---|
| **Why search** | The current planner searches one turn exhaustively with hand-written card rules and approximations (gaps 28 and 30, Juggernaut until 2026-11-19). The engine knows every card, relic, power and monster exactly; search over it can look several turns ahead and weigh the draws a player cannot see. |
| **Speed budget** | Live: at most 1 s of search per decision, target 200 ms. Offline evaluation: thousands of fights per comparison. With 200 fights per second per core (Phase 7 target) and several workers, 1 s allows thousands of rollouts. |
| **Strength target** | Pre-registered comparisons on a fixed benchmark set (E1): search must beat the planner on HP lost and on fight win rate for elites and bosses, by margins fixed before testing. |
| **Player involvement** | Approve the switch to autopilot for real runs (E5.S5). Optionally watch the first autopilot fights. |
| **What can go wrong** | Strategy fusion and too few samples (FP-12, FP-13); a weak evaluation function that values HP wrongly across the run (ML-3); the state rebuild failing in live play; a policy that exploits a simulator bug (ML-4). |

---

## 2. Design

- **Decision point:** any moment the player can act in combat: play a card, use a potion, answer a prompt, or end the turn.
- **Information sets:** The Agent sees the observation (Phase 7 encoder). Hidden parts (draw order outside known positions, future rolls, random targets and generation) are sampled by the fair-play layer, one *world* per sample.
- **Search families** (E2 compares them):
  1. **Determinized root voting (PIMC):** run search in each sampled world, then vote or average at the root, so one action is chosen for all worlds (FP-12).
  2. **Information-set MCTS (ISMCTS):** one tree over information sets; a new world is sampled each iteration.
  3. **Turn-level beam search:** enumerate a turn's card sequences, as the current planner does, with exact engine outcomes; roll out later turns with a fast default policy.
- **Action reduction:** hand-order symmetries (equal cards), dominated targets, and the end-turn action always available. Prompts reduce the same way.
- **Leaf evaluation** (E3): first a heuristic built from run context, later Phase 9's value network.
- **Run context** (E4): HP, potions, exhausted or transformed cards and turns spent cost different amounts at different points in a run; the fight's score includes these costs.

---

## 3. Epics and stories

### P8.E1: Evaluation harness

> **P8.E1.S1: Benchmark fight set** · Size M · Status: Todo
> *As the Agent, I want a fixed, versioned set of fights to compare policies on, so that every comparison is like for like.*
>
> **Acceptance criteria**
> - [ ] `data/sim/benchmark-v1.json`: room-entry states from the replay corpus (P7.E2.S3): at least 30 hallway, 20 elite and 10 boss fights across the three acts, with the run context (act, floor, deck, relics, potions, HP).
> - [ ] Exam seeds are excluded (ML-7). The file records the game build and fidelity version (ML-2).

> **P8.E1.S2: Baseline policies in the simulator** · Size M · Status: In progress (2026-11-20: planner, greedy and random policies in `tools/sim.py baselines`; exploratory results on 36 fights from nothing, `reports/phase8/baselines.md`: planner won 22 (mean HP left 28.9), greedy 20 (24.5), random 3 (3.0); the benchmark-set run waits for P8.E1.S1)
> *As the Agent, I want the current planner, a greedy policy and a random policy runnable inside the simulator, so that search has baselines.*
>
> **Acceptance criteria**
> - [ ] `tools/sim.py` runs `plan_turn.py` as a policy (safe and balanced modes) through an adapter from the shared observation; greedy (best immediate damage-for-HP) and random policies too.
> - [ ] Each baseline's results on the benchmark set are in `reports/phase8/baselines.md`.

> **P8.E1.S3: Comparison protocol** · Size S · Status: In progress (2026-11-20: `templates/comparison.md` written; the first search experiment ran before it and is labelled exploratory)
> *As the Player, I want comparisons fixed before they run, so that results are not cherry-picked (ML-10).*
>
> **Acceptance criteria**
> - [ ] `templates/comparison.md`: hypothesis, metric (HP lost per fight, fight win rate, potions used, turns), benchmark version, sampler seeds, number of samples per fight, margin and test (paired by fight and seed), written before the run.
> - [ ] Results reports carry the simulator header from P7.E5.S4.

### P8.E2: Search

> **P8.E2.S1: Turn-level beam search with exact outcomes** · Size M · Status: Todo (exploratory precursor 2026-11-20: `tools/sim.py search`, flat Monte Carlo over the planner's candidate first actions with engine outcomes and planner rollouts on re-sampled worlds; `reports/phase8/search-first-experiment.md`: on 36 hallway and elite fights from nothing, search won 24 of 36 (mean HP left 32.5) against the planner's 22 (28.9); search was better in 23 fights, worse in 4, equal in 9 (sign test one-sided p = 0.0002; mean paired value difference 11.67, bootstrap 95% interval 4.06 to 22.00). Exploratory (not under the comparison protocol); about 10–50 s per fight in Python)
> *As the Agent, I want the current planner's idea (search a turn's plays) run on the exact engine, so that the first gain needs no new algorithm.*
>
> **Acceptance criteria**
> - [ ] For each sampled world, the turn's play sequences are enumerated with action reduction. Outcomes come from the engine; the rest of the fight is rolled out with the planner as default policy.
> - [ ] Root decision across worlds by voting (FP-12). Compared with the planner by protocol E1.S3.

> **P8.E2.S2: Information-set MCTS** · Size L · Status: Todo
> *As the Agent, I want ISMCTS over multi-turn horizons, so that setup turns and boss patterns are planned.*
>
> **Acceptance criteria**
> - [ ] A world is sampled per iteration (P7.E6.S2, S3); chance events (draws, random targets, generation) are handled through the sampled world; time and iteration budgets are configurable.
> - [ ] Compared with E2.S1 at equal time budgets.

> **P8.E2.S3: Sample counts and stability** · Size S · Status: Todo
> *As the Agent, I want to know how many worlds a decision needs, so that decisions are stable without wasting time (FP-13).*
>
> **Acceptance criteria**
> - [ ] For 200 decision points: agreement of the chosen action across repeated searches with 4, 16, 64 and 256 worlds. The minimum count and the live budget are set from this.

> **P8.E2.S4: Prompts and potions** · Size M · Status: Todo
> *As the Agent, I want card-selection prompts and potion timing searched too, so that no part of combat falls back to rules by accident.*
>
> **Acceptance criteria**
> - [ ] Prompts (exhaust, discard, choose one of N, upgrade in fight) and potion use are actions in the same search; potion costs come from the run context (E4).

### P8.E3: Leaf evaluation

> **P8.E3.S1: Heuristic evaluation** · Size M · Status: Todo
> *As the Agent, I want a leaf score that a fight cut off mid-way can be judged by, so that search does not need to play every fight to the end.*
>
> **Acceptance criteria**
> - [ ] Score from player HP, enemy HP and Block, incoming damage, scaling (own and enemy Strength and similar powers), cards and potions left, with weights from the run context (E4).
> - [ ] Calibration: on recorded fights, the score at turn k predicts the final HP lost (correlation and error reported).

> **P8.E3.S2: Rollout policy** · Size S · Status: Todo
> *As the Agent, I want a fast default policy for rollouts, so that leaves deep in a fight are still informative.*
>
> **Acceptance criteria**
> - [ ] The planner (fast mode) or greedy policy as rollout policy; its speed and its effect on search quality measured.

### P8.E4: Run-context costs

> **P8.E4.S1: What HP, potions and cards are worth** · Size M · Status: Todo
> *As the Agent, I want the fight score to price HP, potions and lost cards by where the run is, so that search does not win a fight in a way that loses the run (ML-3).*
>
> **Acceptance criteria**
> - [ ] Prices for HP by act and floor (from the fight model and the playbook's HP budgets), potion cost by fight type (`plan_turn.POTION_COST` as the starting point), Power value, and the cost of exhausting or transforming permanent cards.
> - [ ] Each price carries a provenance label; the playbook changelog records the source.

> **P8.E4.S2: Sensitivity** · Size S · Status: Todo
> *As the Agent, I want to know how much decisions change when the prices change, so that the weak points are known.*
>
> **Acceptance criteria**
> - [ ] The benchmark is re-run with each price ±50%; decisions and results reported.

### P8.E5: Live combat autopilot

> **P8.E5.S1: Rebuild and sanitize the live state** · Size M · Status: Todo
> *As the Agent, I want the live fight rebuilt in the simulator and sanitized, so that search starts from the real present and nothing more (FP-15).*
>
> **Acceptance criteria**
> - [ ] From the room-entry save copy and the actions so far (replay events or our decision log), the host rebuilds the fight; the sanitizer checks it against the live observation and stops on any mismatch.
> - [ ] Measured: rebuild time per decision.

> **P8.E5.S2: `play_turn.py --auto`** · Size M · Status: Todo
> *As the Player, I want whole fights played by search with no language-model calls, so that runs go fast.*
>
> **Acceptance criteria**
> - [ ] `play_turn.py --auto` plays until the fight ends or an escalation fires; every action carries a one-sentence decision reason generated from the search result (the project instructions hard rule).
> - [ ] Escalation to the language model: a rebuild mismatch, search disagreement above a threshold, an unknown id, a prompt the interface does not cover, or HP below the danger line set in the playbook.
> - [ ] Fallback to the rule planner if the simulator is down or the version guard refuses (P7.E3.S5).

> **P8.E5.S3: Latency** · Size S · Status: Todo
> *As the Player, I want decisions under a second, so that the speed goal is met.*
>
> **Acceptance criteria**
> - [ ] Median decision time at most 1 s, p95 at most 3 s, over at least one full run's fights, reported with the game's own animation time separately.

> **P8.E5.S4: Journal and logs** · Size S · Status: Todo
> *As the Next Session, I want autopilot fights recorded as fully as manual ones, so that post-mortems still work.*
>
> **Acceptance criteria**
> - [ ] Decisions log to `decisions.jsonl` with the search summary; the journal gets its floor line; the replay is captured (P7.E2.S2).

> **P8.E5.S5: Player sign-off for real runs** · Size XS · Status: Todo (Player-gated)
> *As the Player, I want to approve autopilot before it plays a real run, so that I know what changed.*
>
> **Acceptance criteria**
> - [ ] A one-page summary of the comparison results (E6) and the escalation rules is shown to the Player; autopilot runs only after a yes.

### P8.E6: Validation in the real game

> **P8.E6.S1: Real fights against the simulator's prediction** · Size M · Status: Todo
> *As the Agent, I want each autopilot fight's real result compared with what search expected, so that sim-to-real gaps show up.*
>
> **Acceptance criteria**
> - [ ] Per fight: expected HP lost (from the search at turn 1) against real HP lost; the gap distribution reported per run.

> **P8.E6.S2: Real-run comparison** · Size M · Status: Todo
> *As the Player, I want proof in real runs, not only in simulation.*
>
> **Acceptance criteria**
> - [ ] Real runs alternate between planner combat and autopilot combat by a pre-registered schedule. HP lost per fight is compared with the Player's band benchmarks (`data/benchmarks/`) and between the two policies, with counts and intervals (ML-8).

---

## 4. Exit gate

- [ ] M13: search beats the planner on the benchmark set by the pre-registered margins (HP lost per fight; win rate on elites and bosses).
- [ ] M12: autopilot plays every fight of at least 3 full real runs with no illegal actions, median decision time at most 1 s, and escalations logged and reviewed.
- [ ] The invariance audit and leak canary pass with the search policy itself (P7.E6.S4 run against search).
- [ ] Real-run comparison (E6.S2) reported, whatever the result.

---

## 5. Open questions

| ID | Question | Resolved by |
|---|---|---|
| OQ8.1 | Which family wins at a 200 ms to 1 s budget: beam search with exact turns, PIMC voting or ISMCTS? | E2.S1, E2.S2 |
| OQ8.2 | How many worlds does a stable decision need? | E2.S3 |
| OQ8.3 | Is the live rebuild fast enough per decision, or does the host need to keep the fight state between decisions? | E5.S1 |
| OQ8.4 | How should run-context prices be learned rather than set by hand? | Phase 9 (value of a run state) |
