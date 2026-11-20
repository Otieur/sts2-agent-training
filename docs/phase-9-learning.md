# Phase 9: Learned Models and Reinforcement Learning

**Goal:** neural models learn combat evaluation and policy from search and self-play in the simulator, and strategic decisions (drafting, pathing, shops, rest sites, events) from whole simulated and real runs. Together they lift the Agent past the Player's win rate at A10 and towards a consistently high one. Target: milestones M14, M8 and M9.

**Depends on:** Phase 8 (search to learn from and to beat). The strategic epic (E4) also needs the run-level simulator (P7.E8).
**Unblocks:** the final product: a fast, strong player for solo and co-op (Phase 6 benefits directly).
**Rules:** [simulator-integrity.md](simulator-integrity.md), especially FP-10 (privileged training information), ML-1 to ML-10, and SA-8 (downloaded libraries).

---

## 1. What to expect

| | |
|---|---|
| **Approach** | Expert iteration (the AlphaZero idea): search produces better moves than the network; the network learns to imitate search and predict outcomes; the improved network guides better search. Strategic models start from outcome data and improve with reinforcement learning on simulated runs. |
| **Scale** | Combat: millions of simulated decisions. Strategy: tens to hundreds of thousands of simulated runs. Feasible only if Phase 7 meets its speed target; this phase sizes itself on the P7.E7 benchmarks. |
| **Hardware** | The Player's Apple Silicon Mac (CPU and GPU through Metal), shared politely (SA-7). Models stay small: inference must fit the 200 ms live budget. |
| **Downloads** | A neural-network framework is needed (for example PyTorch). That is downloaded code: a security review and the Player's approval come first (SA-8, E5.S1). |
| **Player involvement** | Approve the framework; agree on long training jobs and when they run; play optional head-to-head exam seeds. |
| **Realistic outcome** | Results are uncertain. A10 at 8% (the Player's rate) is the first bar (M8); 30% over 10 consecutive runs (M9) is a stretch. Phase 9 reports progress honestly at each gate, including no-gain results. |
| **What can go wrong** | Overfitting to the simulator or to the Agent's own style; reward hacking (ML-4); a patch invalidating models (E7); compute too slow for meaningful training. |

---

## 2. Design

- **Observation:** the Phase 7 encoder (P7.E6.S5) turned into tensors. Card, relic, power and monster identities as learned embeddings; numbers (HP, Block, energy, intents, power amounts) as scaled features; piles as sets. The same encoder runs live and in simulation (ML-1).
- **Combat models:**
  - *Value network*: predicts the fight result (survive, HP lost, resources used) from an observation and the run context. It replaces the heuristic leaf in search (P8.E3).
  - *Policy network*: predicts search's action distribution. It focuses search on good actions (priors) and is a fast fallback when time is short.
- **Strategic models:** card reward choice, map path, shop purchases and removals, rest-site choice, event options, boss relic and Ancient choices. Inputs: the encoded run state (deck, relics, potions, HP, gold, act, floor, map ahead, ascension). Outputs: action values, trained first from outcome data, then by reinforcement learning on the run-level simulator (P7.E8).
- **Rewards (ML-3):** combat models learn fight results priced by the run context (P8.E4); strategic models learn run outcomes (win, floor reached), with shaping only if it is pre-registered and checked for side effects.
- **Privileged information (FP-10):** a teacher may see hidden information during training only; deployed models take the observation alone, and the model card says so.

---

## 3. Epics and stories

### P9.E1: Data and encoding

> **P9.E1.S1: Tensor encoding** · Size M · Status: Todo
> *As the Agent, I want the shared observation turned into model inputs in one tested module, so that training and live play cannot diverge (ML-1).*
>
> **Acceptance criteria**
> - [ ] Encoding of every field in `docs/observation-spec.md`; vocabulary built from the game's model database, with an "unknown" entry for ids added by patches.
> - [ ] Tests: live fixtures and simulated states encode without error; round-trip checks for numeric fields.

> **P9.E1.S2: Datasets** · Size M · Status: Todo
> *As the Agent, I want versioned datasets of decisions and outcomes, so that every model can be traced to its data (ML-2).*
>
> **Acceptance criteria**
> - [ ] Combat: (observation, search action distribution, outcome, run context) from self-play in the simulator and from real fights.
> - [ ] Strategy: (run state, options, choice, run outcome) from simulated runs, Agent runs and the Player's history. The Player's history is an outcome source only: never an imitation target (project instructions, goal reminder).
> - [ ] Each dataset has a manifest: game build, simulator and fidelity version, encoder version, generating policy, sampler seeds, size. Stored under `data/learn/` (ignored by git; manifests committed).

### P9.E2: Combat value network

> **P9.E2.S1: First value model** · Size L · Status: Todo
> *As the Agent, I want a network that predicts fight results, so that search can judge positions better than the heuristic.*
>
> **Acceptance criteria**
> - [ ] Trained on E1.S2 combat data; held-out error and calibration reported against the heuristic of P8.E3.S1.

> **P9.E2.S2: Value in search** · Size M · Status: Todo
> *As the Agent, I want search to use the value network at the leaves, so that its gain is measured where it matters.*
>
> **Acceptance criteria**
> - [ ] Pre-registered comparison (P8.E1.S3): search with value network against search with heuristic at equal time budget, on the benchmark set.

> **P9.E2.S3: Inference speed** · Size S · Status: Todo
> *As the Player, I want the model fast enough for live play.*
>
> **Acceptance criteria**
> - [ ] Batch inference time measured; the live decision budget (P8.E5.S3) still holds with the model in the loop.

> **P9.E2.S4: Model card** · Size S · Status: Todo
> *As the Next Session, I want every model documented, so that it can be trusted, retrained or retired (ML-9).*
>
> **Acceptance criteria**
> - [ ] `models/<name>/MODEL_CARD.md` (weights ignored by git): inputs, data manifests, training settings, evaluation, known failures, privileged-information statement (FP-10).

> **P9.E2.S5: Privileged-teacher review** · Size S · Status: Todo
> *As the Player, I want certainty that no deployed model peeks at hidden information.*
>
> **Acceptance criteria**
> - [ ] For each deployed model, a check that its input pipeline is the observation encoder alone; the invariance audit (P7.E6.S4) runs with the model in the loop.

### P9.E3: Combat policy and expert iteration

> **P9.E3.S1: Policy network** · Size L · Status: Todo
> *As the Agent, I want a network that predicts search's choices, so that search is focused and a fast fallback exists.*
>
> **Acceptance criteria**
> - [ ] Trained on search action distributions; top-1 agreement and the policy's own fight results on the benchmark set reported.

> **P9.E3.S2: Self-play loop** · Size L · Status: Todo
> *As the Agent, I want generations of search plus networks, each trained on the last one's play, so that play keeps improving.*
>
> **Acceptance criteria**
> - [ ] A loop: generate fights with the current search plus networks; train new networks; promote them only if they win a pre-registered gate on the benchmark set (ML-10). Each generation is logged with its manifest.
> - [ ] The fight distribution for self-play comes from realistic run states (corpus and simulated runs), not only the benchmark set, to avoid overfitting it.

> **P9.E3.S3: Exploit watch** · Size M · Status: Todo
> *As the Agent, I want signs of simulator exploits caught early, so that a policy does not learn bugs (ML-4).*
>
> **Acceptance criteria**
> - [ ] Each generation is checked for outliers (fights much better than the real game would allow, unusual action loops). Its best fights are replayed through the fidelity suite, and a sample of its decisions is checked in real fights (P8.E6.S1).

### P9.E4: Strategic decisions

> **P9.E4.S1: Outcome models from existing data** · Size M · Status: Todo
> *As the Agent, I want first strategic models trained on outcomes from real runs, so that drafting and pathing improve before the run-level simulator exists.*
>
> **Acceptance criteria**
> - [ ] Card-choice and path models trained on (state, choice, outcome) from the Player's history and Agent runs, with decision-point controls as in `tools/analyze_card_choices.py`. Compared with `draft.py` and `path.py` on held-out runs by pre-registered metrics.
> - [ ] Limits stated: confounding and small samples (`TRAINING_PLAN.md` §5).

> **P9.E4.S2: Reinforcement learning on simulated runs** · Size XL (split before starting) · Status: Todo
> *As the Agent, I want strategic policies trained on whole simulated runs, so that drafting, pathing and shopping are judged by run results at scale.*
>
> **Acceptance criteria**
> - [ ] Uses the run-level simulator (P7.E8) with sampled streams (FP-9) and the combat stack from E2–E3 to play fights.
> - [ ] Policies are promoted only through pre-registered comparisons against the rule tools and the E4.S1 models.

> **P9.E4.S3: Ancients, boss relics and events** · Size M · Status: Todo
> *As the Agent, I want the rare high-impact choices learned too, so that no part of a run is left to rules by default.*
>
> **Acceptance criteria**
> - [ ] Covered by E4.S2's policies or by dedicated models; compared with `advise.py`'s current advice on held-out situations.

### P9.E5: Training infrastructure

> **P9.E5.S1: Framework choice and security review** · Size M · Status: Todo (Player-gated)
> *As the Player, I want any downloaded learning library reviewed before it runs on my machine (SA-8).*
>
> **Acceptance criteria**
> - [ ] `docs/reviews/<framework>-security-review.md`: source, version pinned, install method (a project virtual environment, nothing global), network behaviour, what it can access. The Player approves before installation.

> **P9.E5.S2: Training jobs** · Size M · Status: Todo
> *As the Player, I want training to run when I allow it and stop cleanly, so that my Mac stays usable (SA-7, EN-7).*
>
> **Acceptance criteria**
> - [ ] Jobs checkpoint, resume, run at low priority, respect a schedule agreed with the Player, and log progress to files.

> **P9.E5.S3: Experiment records** · Size S · Status: Todo
> *As the Next Session, I want every experiment written down, so that results are reproducible without memory.*
>
> **Acceptance criteria**
> - [ ] `reports/phase9/experiments.md`: one row per experiment (hypothesis, data, settings, result, decision), linked to manifests and model cards.

### P9.E6: Evaluation and the ascension ladder

> **P9.E6.S1: Scored-run protocol** · Size S · Status: Todo
> *As the Player, I want scored runs to be clean and comparable with my record (ML-5 to ML-8).*
>
> **Acceptance criteria**
> - [ ] `docs/runbooks/scored-runs.md`: unmodified game logic; Instant mode allowed; no console or debug hooks; no restarts; every run counted; exam seeds held out; version gap stated; counts, rates and intervals reported.

> **P9.E6.S2: Climb to A10** · Size XL (ongoing) · Status: Todo
> *As the Player, I want the Agent to beat my win rate at every band, then at A10.*
>
> **Acceptance criteria**
> - [ ] Ladder per Phase 4 rules with the learned stack; M8 per band; then M9 at A10.
> - [ ] Sample sizes planned before claims (ML-8): the report says how many runs a claimed difference needs.

> **P9.E6.S3: Head-to-head exam seeds (optional)** · Size S · Status: Todo (Player-optional)
> *As the Player, I want to play the same seeds as the Agent, so that the comparison is direct.*
>
> **Acceptance criteria**
> - [ ] Exam seeds played by both; results side by side, with the Agent's runs following the scored-run protocol.

### P9.E7: Patch resilience

> **P9.E7.S1: Retrain on patches** · Size M · Status: Todo
> *As the Next Session, I want a procedure for models after a game update, so that patches do not silently degrade play (FI-4).*
>
> **Acceptance criteria**
> - [ ] After the game patch runbook (P7.E7.S4), models are re-evaluated on the benchmark set; changed or new ids are listed; fine-tuning or retraining is triggered by pre-set thresholds; the rule-based stack is the fallback meanwhile (ML-10).

---

## 4. Exit gate

- [ ] M14: search with the learned combat models beats search with heuristic evaluation at equal time budget (pre-registered).
- [ ] Strategic models beat `draft.py` and `path.py` in pre-registered comparisons (offline and in real runs).
- [ ] M8: higher win rate than the Player in each band over at least 10 finished runs per band, scored-run protocol. M9 (3 wins in 10 consecutive A10 runs) attempted.
- [ ] Every deployed model has a model card and has passed the privileged-teacher review.

---

## 5. Open questions

| ID | Question | Resolved by |
|---|---|---|
| OQ9.1 | Which framework, and does it run well on this Mac's GPU? | E5.S1 |
| OQ9.2 | How much self-play is needed before the policy network helps search? | E3.S2 |
| OQ9.3 | Can strategic reinforcement learning work without a full run-level simulator, using only fight-level simulation plus outcome models? | E4.S1 against E4.S2 |
| OQ9.4 | How fast do models go stale after a patch? | E7.S1 after the next game update |
| OQ9.5 | Does co-op (Phase 6) need separate models or only extra inputs (teammate state)? | Phase 6 planning |
