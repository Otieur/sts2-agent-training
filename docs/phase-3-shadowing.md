# Phase 3: Shadowing

**Goal:** The Agent learns from live play. The Player plays their own runs. The Agent watches the game state through the mod, commits to its own call before each decision, and records combat, which the run history files do not contain. Disagreements are discussed and settled by evidence, not by whose habit it is.

**Depends on:** Phase 0 (mod working in the Player's game) and Phase 2 (playbook v2). Playbook v1 is enough to start if Phase 2 runs late.
**Unblocks:** Phase 4. Playbook v3, combat lessons and a combat dataset feed solo play.

---

## 1. What to expect

| | |
|---|---|
| **Runs** | About 2 Player runs of Ironclad on the modded profile, on the main branch, at whatever ascension the Player likes. The aim is better-than-Player play, so shadowing is kept short: it tests the live tools and records real combat. |
| **Time per run** | The Player's normal pace (60–90 min) plus 10–20% for the Agent's calls and the end-of-run retro (about 10 min) |
| **What the Player sees** | Short messages in the agent chat at each decision: one line with the pick, the reason and a confidence level. More only on request. A retro at the end of each run. |
| **What the Player does** | Plays normally. Glances at the call, optionally replies. Answers 3–5 "why?" questions in the retro. |
| **Early agreement** | Expect roughly 50–70% agreement on card rewards in the first run, higher on rest sites and pathing. Agreement is a sanity check, not the goal: some disagreements will be the Agent being right. |
| **Main technical risk** | Recording the Player's combat actions. The mod logs the Agent's actions, not the human's, so card plays may have to be reconstructed from state differences (E4). This is verified in the first run. |

---

## 2. Two ways for the Agent to watch

| Mode | How it works | When to use |
|---|---|---|
| **A: Player-prompted** | The Player types `?` (or anything) in chat at a decision. The Agent reads `/state` and answers. | Always available. The fallback if B fails. |
| **B: Auto-watch** | A background watcher (`tools/watch.py`) listens to `/events/stream` (or polls `/state`) and exits with a short screen summary when a decision screen appears. That wakes the Agent, which posts its call and restarts the watcher. | Preferred. Needs P3.E1.S2 working. |

The agent harness cannot see a video feed. "Watching" means reading the exact game state at each decision point, which is more precise than video but only happens at discrete moments.

---

## 3. Epics and stories

### P3.E1: Live view of the Player's game

> **P3.E1.S1: Brief view of the Player's game** · Size S · Status: Todo
> *As the Agent, I want a compact read of the Player's current screen in under a second, so that calls arrive before the Player has already decided.*
>
> **Acceptance criteria**
> - [ ] `python3 tools/sts.py state --brief` against the Player's instance returns in under 1 s, with the screen type, the options and their indexes, and the context needed (deck summary on reward screens, HP and gold everywhere).

> **P3.E1.S2: Decision-point watcher** · Size M · Status: Todo
> *As the Agent, I want to be woken automatically when the Player reaches a decision, so that the Player does not have to prompt me every time.*
>
> **Acceptance criteria**
> - [ ] `tools/watch.py` subscribes to `/events/stream`. It falls back to polling every 1 s if the stream is unavailable.
> - [ ] It exits, printing a summary of 10 lines or fewer, on these events:
>   - a card reward, map choice, shop, rest site, event, Ancient, treasure, or boss relic screen
>   - the first turn of an elite or boss fight
>   - any turn where incoming damage is at least 30% of current HP
> - [ ] It never fires twice for the same screen (deduplicated by state fingerprint).
> - [ ] It is started in the background, and the Agent is re-invoked when it exits. Measured wake latency is under 3 s from the screen appearing.

> **P3.E1.S3: Call format and etiquette** · Size XS · Status: Todo
> *As the Player, I want calls that are short and arrive fast, so that shadowing does not slow my game down.*
>
> **Acceptance criteria**
> - [ ] Default format: `Pick: <option> · <reason, 15 words or fewer> · <confidence %>`. For maps: the planned path, up to the next rest site.
> - [ ] Longer explanations only when the Player asks ("why?").
> - [ ] No calls during ordinary hallway combat turns unless the Player asks.

---

### P3.E2: Call-it-first for non-combat decisions

> **P3.E2.S1: Commit before the Player acts** · Size S · Status: Todo
> *As the Agent, I want my call written to a log before the Player chooses, so that agreement statistics are free of hindsight.*
>
> **Acceptance criteria**
> - [ ] Each call is appended to `runs/shadow-<NN>/calls.jsonl` with: timestamp, floor, screen, the options offered, agent_pick, confidence, reason, and the playbook rule used (if any). This happens before the call is posted in chat.

> **P3.E2.S2: Capture the Player's choice** · Size S · Status: Todo
> *As the Agent, I want the Player's actual pick captured automatically, so that the Player does not have to report it.*
>
> **Acceptance criteria**
> - [ ] The Player's pick is filled in from the next state (deck change, map position, purchase) and confirmed against the run's `.run` file after the run ends.
> - [ ] `calls.jsonl` rows gain `player_pick` and `agree`.

> **P3.E2.S3: Disagreement review** · Size S (plus Player time) · Status: Todo
> *As the Player, I want to discuss only the disagreements that matter, so that the retro stays short.*
>
> **Acceptance criteria**
> - [ ] At run end, the Agent ranks disagreements by impact: rare cards, relics, elite paths and rest sites before a boss come first. The top 3–5 are brought to the Player.
> - [ ] Each one is resolved by evidence: what happened next in the run, game data, or community consensus where it exists. Otherwise it becomes a `[HYPOTHESIS]` to test in Phase 4. Neither side wins by default; the Player's reasoning is recorded as input.

> **P3.E2.S4: Agent-only notes** · Size XS · Status: Todo
> *As the Agent, I want to note where I was uncertain or missing information, so that knowledge gaps get filled.*
>
> **Acceptance criteria**
> - [ ] Any call made with less than 50% confidence, or with an unknown card, relic or event, adds an item to `knowledge/gaps.md`.

---

### P3.E3: Combat calls

> **P3.E3.S1: Trigger policy** · Size XS · Status: Todo
> *As the Player, I want combat calls only where they are worth it, so that ordinary fights flow.*
>
> **Acceptance criteria**
> - [ ] Calls are made on:
>   - turn 1 of every elite and boss fight
>   - any turn with incoming damage at least 30% of current HP
>   - any turn where the Agent sees possible lethal on the enemy
>   - whenever the Player asks
> - [ ] At most about 15 combat calls per run, unless the Player asks for more.

> **P3.E3.S2: Full-turn call** · Size S · Status: Todo
> *As the Agent, I want to propose a complete turn, so that it can be compared with what the Player does.*
>
> **Acceptance criteria**
> - [ ] Each call gives the card order with targets, any potion use, and the expected result: damage dealt per enemy, block gained, expected HP after enemy actions.
> - [ ] It is logged to `runs/shadow-<NN>/combat-calls.jsonl` before the Player acts.

> **P3.E3.S3: Compare outcomes** · Size S · Status: Todo
> *As the Agent, I want to compare my proposed turn with the Player's actual turn, so that I find my blind spots.*
>
> **Acceptance criteria**
> - [ ] For each call: the Player's actual sequence (from E4) and the actual result (HP lost, damage dealt). A verdict: same, Player better, Agent better, or unclear. The Agent's expected result is checked against the actual numbers, which catches arithmetic mistakes.

> **P3.E3.S4: Combat lessons log** · Size S · Status: Todo
> *As the Next Session, I want combat insights collected in one place, so that I play better fights without re-learning.*
>
> **Acceptance criteria**
> - [ ] `knowledge/combat-lessons.md` gets one entry per lesson: situation, mistake or insight, rule, and evidence (run and turn), with a label.

---

### P3.E4: State recorder and action reconstruction

> **P3.E4.S1: Recorder** · Size M · Status: Todo
> *As the Agent, I want every state change during the Player's runs saved, so that combat can be analysed afterwards.*
>
> **Acceptance criteria**
> - [ ] `tools/record.py` runs in the background for the whole run. It snapshots `/state` on every change (from events, or polling every 0.5 s during combat), deduplicates by fingerprint, and writes `runs/shadow-<NN>/states.jsonl.gz`.
> - [ ] Size is checked after the first run. It should be under about 50 MB per run compressed.

> **P3.E4.S2: Reconstruct the Player's plays** · Size L · Status: Todo
> *As the Agent, I want the Player's card plays recovered from consecutive snapshots, so that real combat decisions become training data.*
>
> **Acceptance criteria**
> - [ ] `tools/reconstruct.py` reads two snapshots and infers the play from:
>   - the card that left the hand
>   - the energy spent
>   - target HP, block and power changes
>   - potion slot changes
>   - end of turn
> - [ ] It handles draw and discard effects, cards that create cards, and multi-step selections.
> - [ ] Every inferred action carries a confidence level. Low-confidence actions are flagged, not guessed.
> - [ ] **If the Phase 0 event-stream probe (OQ0.3) shows the stream reports human plays, use the stream directly and drop this story.**

> **P3.E4.S3: Validate the reconstruction** · Size S (plus Player time) · Status: Todo
> *As the Agent, I want to know how accurate the reconstruction is, so that the combat data is trusted only as far as it deserves.*
>
> **Acceptance criteria**
> - [ ] The Player plays 2 fights while saying each card played in chat (or the Agent compares against a screen recording). The reconstruction must identify at least 90% of cards and targets correctly.
> - [ ] Below that, the limits are documented, and only the high-confidence turns are used.

> **P3.E4.S4: Combat dataset** · Size S · Status: Todo
> *As the Agent, I want a clean per-turn dataset of the Player's combat, so that Phase 4 can compare my turns with real ones.*
>
> **Acceptance criteria**
> - [ ] `data/combat_turns.jsonl`: run, floor, encounter, turn, state at turn start (hand, energy, HP, block, enemies and intents), the Player's sequence, and the result (HP lost, damage dealt, enemies killed).
> - [ ] Its documentation goes in `data/README.md`.

---

### P3.E5: Metrics and calibration

> **P3.E5.S1: Agreement metrics** · Size S · Status: Todo
> *As the Player, I want to see whether the Agent's judgment is converging with mine, so that we know when it is ready to play alone.*
>
> **Acceptance criteria**
> - [ ] `metrics/shadow.csv`: one row per run, with agreement % for card rewards, map, rest, shop, event and combat calls, plus the number of decisions.
> - [ ] A trend across runs is shown after run 3.

> **P3.E5.S2: Calibration** · Size S · Status: Todo
> *As the Agent, I want to know whether my confidence levels mean anything, so that I can tell when to trust myself.*
>
> **Acceptance criteria**
> - [ ] Calls are grouped by confidence (50–60%, 60–70%, and so on) against the agreement rate, across all shadow runs. Over- or under-confidence is noted in `knowledge/combat-lessons.md` or the playbook's hypotheses list.

---

### P3.E6: Retros and playbook v3

> **P3.E6.S1: Run retro** · Size S (plus about 10 min of Player time) · Status: Todo
> *As the Player, I want a short retro after each run, so that the session ends with something learned rather than a log dump.*
>
> **Acceptance criteria:** The Agent presents:
> - [ ] Agreement stats.
> - [ ] The top disagreements (E2.S3).
> - [ ] 1–2 combat observations.
> - [ ] One thing the Agent now believes differently.
> - [ ] Saved to `runs/shadow-<NN>/retro.md`.

> **P3.E6.S2: Playbook v3** · Size M · Status: Todo
> *As the Next Session, I want everything learned while shadowing folded into the playbook, so that solo play starts from it.*
>
> **Acceptance criteria**
> - [ ] Rules are added or changed from the retros and the combat lessons, each labelled by its evidence (`[OBS]`, `[GAME]`, `[COMMUNITY]`, or `[HYPOTHESIS]` pending a test). The changelog has an entry for v3.

---

## 4. Exit gate

- [ ] At least 2 shadowed runs (a third only if the tools or the recorder still need testing).
- [ ] E4 validated (at least 90% accuracy) **or** declared infeasible, with the reason recorded in `docs/api-notes.md`
- [ ] `knowledge/combat-lessons.md` has at least 20 entries
- [ ] Playbook v3 committed
- [ ] `metrics/shadow.csv` filled for every shadow run

---

## 5. Open questions

| ID | Question | Resolved by |
|---|---|---|
| OQ3.1 | Can the background watcher wake the Agent reliably mid-session, or is mode A needed? | P3.E1.S2 |
| OQ3.2 | Does polling `/state` every 0.5 s affect game performance? | P3.E4.S1 |
| OQ3.3 | How accurate can reconstruction be for cards that draw, discard or create cards? | P3.E4.S3 |
