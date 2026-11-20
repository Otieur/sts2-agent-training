# Phase 7: Engine Simulator

**Goal:** the game's own combat logic runs in a separate process of our own, without graphics, Steam or saves. It matches the game exactly on recorded fights, takes a few milliseconds per fight, and has a fair-play layer that re-samples everything a player cannot see. Target: milestones M10 and M11.

**Depends on:** Phase 0 (game install, .NET 9 SDK, save backups). Phase 4 runs supply recorded fights (E2).
**Unblocks:** Phase 8 (combat search) and Phase 9 (learned models).
**Rules:** every story follows [simulator-integrity.md](simulator-integrity.md); the rule IDs a story must satisfy are listed in its criteria.
**Background:** [proposals/engine-simulation-spike.md](proposals/engine-simulation-spike.md) (desk study), [decisions/0003](decisions/0003-engine-simulator-and-learning.md) (direction).

---

## 1. What to expect

| | |
|---|---|
| **First milestone** | A 1–2 day feasibility spike (E1) ends in a go or no-go. Go means route R3 (our own process). If R3 fails, the spike tries route R4: an offline, headless game instance as a simulation server. If both fail, decision 0003 names the fallback. |
| **Speed target** | Median full hallway fight at most 5 ms on one core (200 fights per second), with fixed actions. Minimum to be useful for Phase 8: 20 fights per second. **Measured 2026-11-19: 31 ms CPU for a long boss fight (45 events), about 32 fights per second per core: above the minimum, about 6 times short of the target.** A hallway fight has fewer events and should be cheaper; not yet measured. |
| **Exactness target** | At least 99% of recorded fights replay with matching checksums and field comparisons; every mismatch explained. |
| **Player involvement** | Approve any offline-instance or console work (SA-6) and any downloaded package (SA-8). Recording fights needs nothing: the game already writes a replay of every fight (E2.S1). No involvement during simulator runs. |
| **Downloads** | None expected. The host references `sts2.dll`, `GodotSharp.dll` and `0Harmony.dll` in the game's install folder; Harmony ships with the game, so engine-call stubs need no download. The .NET 9 SDK is already installed. |
| **Machine load** | Simulator jobs use at most half the CPU cores at low priority by default (SA-7). |
| **What can go wrong** | Model-database start-up needs the Godot engine (EN-1); hidden engine calls in rare cards or monsters; state leaking between fights; game patches breaking the host mid-phase. Each has a story below. |

---

## 2. Architecture

```
            live game (Steam, profile 2)                      our machine, separate processes
 ┌──────────────────────────────────────┐        ┌────────────────────────────────────────────┐
 │ STS2-Agent mod (HTTP API, read/act)   │──state─▶ tools/*.py (advise, play_turn, Phase 8 search)│
 │ the game writes replays/latest.mcr    │──copy──▶ data/sim/replays/<run>/ ─▶ fidelity suite (E5) │
 └──────────────────────────────────────┘        │            │ JSON lines (tools/sim.py)        │
                                                 │            ▼                                   │
                                                 │  sim host (sim/, C#, .NET 9)                   │
                                                 │   loads sts2.dll + GodotSharp.dll + 0Harmony   │
                                                 │   from the install folder (never copied)       │
                                                 │   sandbox: stubs for engine calls, saves,      │
                                                 │   achievements, telemetry, Steam (E3)          │
                                                 │   modes: fidelity (true RNG, offline only)     │
                                                 │          decision (sanitized, re-sampled) (E6) │
                                                 └────────────────────────────────────────────┘
```

- **Where code lives:**
  - `sim/`: the C# host project, our own code. Build output goes to `sim/bin` and `sim/obj`, which git ignores.
  - `tools/sim.py`: the Python bridge.
  - Reports go to `reports/phase7/`; recorded fights go to `data/sim/replays/<run>/` (not in git).
- **Two modes** (FP-3):
  - *Fidelity mode* replays a finished, recorded fight with its true RNG, to test the simulator. Its output never reaches a decision.
  - *Decision mode* takes the current state, sanitizes it and re-samples every hidden stream (FP-15). Only this mode answers questions from Phase 8 and 9 code.
- **Reaching the current state in a live fight:** the engine has no mid-combat restore (EN-2). The host therefore rebuilds the fight from the room-entry state plus the actions taken so far. The sanitizer then checks that the result equals the live observation, hides the draw order, replaces the run seed, re-seeds every random generator and re-samples hidden pre-rolled state before any search (FP-15).

---

## 3. Epics and stories

### P7.E1: Feasibility spike (go or no-go)

> **P7.E1.S0: Desk study of the engine** · Size M · Status: Done (2026-11-19, `docs/proposals/engine-simulation-spike.md`, `tools/asm/asm.cs`)
> *As the Agent, I want to know how the engine runs combat before writing code, so that the spike tests the right things.*
>
> **Acceptance criteria**
> - [x] Waits, test flags, determinism, replay recording, the restore gap and Godot coupling documented with evidence.
> - [x] Integrity hazards audited ([simulator-integrity.md](simulator-integrity.md)).

> **P7.E1.S1: Host skeleton** · Size S · Status: Done (2026-11-19, `sim/`)
> *As the Agent, I want a console program that loads the game's assemblies from the install folder, so that later stories have somewhere to run.*
>
> **Acceptance criteria**
> - [ ] `sim/` holds a .NET 9 console project with no NuGet dependencies beyond the SDK. It loads `sts2.dll`, `GodotSharp.dll` and `0Harmony.dll` from the install path in `docs/environment.md` through a custom `AssemblyLoadContext`. (LG-1: nothing is copied into the repository.)
> - [ ] It prints the game build (`release_info.json`) and the model-id hash, and exits non-zero if either cannot be read (FI-3).
> - [ ] It refuses to start if its sandbox user folder is inside `~/Library/Application Support/SlayTheSpire2` (SA-1).
> - [ ] It sets the invariant culture and runs on the .NET 9 runtime (FI-9).
>
> **Notes:** `sim/bin` and `sim/obj` go into `.gitignore`.

> **P7.E1.S2: Model database start-up without the engine** · Size M · Status: Done (2026-11-19: 1,660 models, model-id hash equal to the game's; `reports/phase7/spike.md`)
> *As the Agent, I want to know whether the game's model database starts outside Godot, so that the spike fails fast if it cannot (EN-1).*
>
> **Acceptance criteria**
> - [ ] The host turns on NonInteractiveMode through `NonInteractiveMode.AutoSlayerCheck` and asserts `TestMode.IsOn` is false (FI-1, FI-2b).
> - [ ] It initialises `ModelDb` and lists the card, relic, power, potion, monster and encounter counts.
> - [ ] Every native Godot call reached during start-up is caught and logged with its stack. A table in `reports/phase7/spike.md` says, for each one, stub (with why it is logic-neutral), avoid, or blocker.
>
> **Notes:** catch at the first native call (Harmony prefix on suspect methods, or the exception GodotSharp throws without an engine). Desk check 2026-11-19 `[GAME]`: `ModelDb.Init`, `InitIds` and `Preload` call no Godot method; the static constructor of `RelicModel` creates a `Godot.StringName`, which needs the engine's native string table, so test that first. Character and card-pool Godot calls are colour structs.

> **P7.E1.S3: First fight in our process** · Size L · Status: Done (2026-11-19: a recorded boss fight replayed; all 26 turn-boundary states equal to the game's, final HP 87/102)
> *As the Agent, I want one real fight to run end to end in the host, so that the route is proven rather than assumed.*
>
> **Acceptance criteria**
> - [ ] The host builds a run state from a `SerializableRun`: a read-only copy of a profile-2 room-entry save, taken into the sandbox, or a run state built in code. It enters a hallway fight and plays cards and end turns until the fight ends. Enemies act.
> - [ ] No save, achievement, telemetry or Steam call is reached; if one is, it is stubbed and listed (SA-1 to SA-4).
> - [ ] The fight's final HP, turns and card plays are printed, and the same input gives the same output twice (FI-10).
>
> **Notes:** the save folder is read-only for analysis (the project instructions). Copy the file into the sandbox; never open it in place for writing.

> **P7.E1.S4: First timing** · Size S · Status: Done (2026-11-19: 400 warm passes of a 45-event boss fight, all correct; 31 ms CPU per fight including set-up, about 32 fights per second per core; `reports/phase7/spike.md`)
> *As the Agent, I want the cost of one fight measured, so that the speed target is grounded.*
>
> **Acceptance criteria**
> - [ ] A scripted policy (the first playable card on the first enemy, else end turn) plays the same fight 1,000 times. Median, p95 and start-up time are recorded in `reports/phase7/spike.md`.

> **P7.E1.S5: Go or no-go** · Size S · Status: Done (2026-11-19: go, route R3; `reports/phase7/spike.md`)
> *As the Player, I want a clear verdict with numbers, so that I know whether the fast-simulator plan holds.*
>
> **Acceptance criteria**
> - [ ] `reports/phase7/spike.md` ends with: route (R3, R4 or fallback), the blockers found, fights per second, and the next story.
> - [ ] Decision 0003 is updated with the verdict, and the Player gets a short summary.

> **P7.E1.S6: Route R4 spike (only if R3 fails)** · Size L · Status: Dropped (R3 works)
> *As the Agent, I want to test the real game binary as an offline headless simulation server, so that a failed R3 does not end the plan.*
>
> **Acceptance criteria**
> - [ ] A mod of our own stays inert unless the game was started with a dedicated flag (for example `--agent-sim`). It is installed only after a save backup and with the Player's approval (SA-6, SA-9).
> - [ ] Started as `--headless --force-steam off --clientId <n> --agent-sim`, the instance replays a recorded fight and returns the final checksum. Its user folder is separate from the Steam profiles.
> - [ ] Time per replayed fight measured; verdict added to the spike report.

### P7.E2: Ground truth from the real game

> **P7.E2.S1: How replay recording is switched on** · Size S · Status: Done (2026-11-19)
> *As the Agent, I want to know what enables `CombatReplayWriter`, so that recording needs the smallest possible change.*
>
> **Acceptance criteria**
> - [x] `[GAME]` Recording is on whenever TestMode is off: `RunManager.InitializeShared` sets `CombatReplayWriter.IsEnabled = !TestMode.IsOn`. No setting, flag or mod is needed.
> - [x] `[GAME]` The replay is written when a fight ends (`CombatManager.EndCombatInternal` → `RunManager.WriteReplay`), also on run clean-up and on a state divergence, to `replays/latest.mcr` in the profile folder. Each fight overwrites the last. `[OBS]` The files exist for every profile; profile 2's was the final boss fight of the first Agent run.
> - [x] Format: binary, starting with the game version and commit strings (`v0.111.1`, `cc1f9462`). `tools/game_facts.py` re-checks the gating after each patch.

> **P7.E2.S2: Keep every Agent fight's replay** · Size S · Status: In progress (implemented and unit-tested 2026-11-19; first live run pending)
> *As the Agent, I want each fight's replay copied before the next fight overwrites it, so that the simulator has exact ground truth.*
>
> **Acceptance criteria**
> - [x] `tools/play_turn.py` copies `replays/latest.mcr` from the Agent's profile (read-only) to `data/sim/replays/<run>/floor<NN>-<time>.mcr` when a fight ends. The folder is not in git (LG-4). No mod change and no Player step.
> - [x] The first Agent run's last fight is kept as the first corpus item (`data/sim/replays/2026-11-19-1ZWEN4BFQUZL/`).
> - [ ] A full live run yields one replay per fight (count equals the journal's fight count).
> - [ ] Fights ended outside `play_turn.py` (a manual `sts.py act`) are covered, or the gap is documented.

> **P7.E2.S3: Replay corpus index** · Size S · Status: Todo
> *As the Next Session, I want an index of recorded fights, so that tests and benchmarks pick fights by act, type and encounter.*
>
> **Acceptance criteria**
> - [ ] `tools/sim.py corpus` lists replays with run, floor, act, room type, encounter, ascension, game build and outcome, and writes `data/sim/corpus.csv`.
> - [ ] Fights from a different game build are flagged (FI-3).

> **P7.E2.S4: Fallback recording through the API** · Size M · Status: Todo (only if S2 is not possible)
> *As the Agent, I want per-action observations logged from the live API, so that observation-level checks are possible without replays.*
>
> **Acceptance criteria**
> - [ ] The existing combat trace is extended to one full observation per action. Its limits are documented: no RNG, so it cannot drive fidelity mode; it can check observations (E5.S3).

### P7.E3: Engine host and sandbox

> **P7.E3.S1: Deterministic scheduler** · Size M · Status: Todo
> *As the Agent, I want the game's async code to run on one thread in a fixed order, so that results never depend on timing (FI-8).*
>
> **Acceptance criteria**
> - [ ] A single-threaded `SynchronizationContext` drives all game tasks to completion; no thread-pool continuations (checked by asserting the thread id inside game callbacks).
> - [ ] NonInteractiveMode on, TestMode off, asserted at start and after every fight (FI-1, FI-2b).

> **P7.E3.S2: Engine-call stubs** · Size M · Status: Todo
> *As the Agent, I want every native Godot call reached by combat logic replaced by a tested stub, so that the engine is never needed (FI-7).*
>
> **Acceptance criteria**
> - [ ] Stubs use the game's bundled Harmony. Each stub has a one-line justification and a test that the fight result is identical with the stub's return value varied, where variation is possible.
> - [ ] Known calls covered: `Godot.Time.GetTicksMsec` (`CardModel.OnPlayWrapper`), timers in `Cmd.Wait`, `ActionExecutor`, `RollingBoulderPower.AfterPlayerTurnStart`, `LordsParasol.PurchaseEverything`, node lookups in effects.
> - [ ] Any call that cannot be made logic-neutral is a blocker, reported in the spike report.

> **P7.E3.S3: Sandbox for saves, achievements, telemetry and Steam** · Size M · Status: Todo
> *As the Player, I want the simulator unable to touch my saves, achievements or the developer's servers, so that experiments are harmless (SA-1 to SA-4).*
>
> **Acceptance criteria**
> - [ ] Stubs on the `SaveManager` save methods, `AchievementsHelper`, `MetricUtilities` uploads, `SentryService`, leaderboard and time-server calls. Steamworks is never loaded.
> - [ ] Test: after 1,000 simulated fights, the sandbox user folder is unchanged except for the host's own log, and no file under `~/Library/Application Support/SlayTheSpire2` has a newer modification time.
> - [ ] Test: no outbound connection during a simulation batch (checked with `lsof -i` or a firewall rule for the host binary).

> **P7.E3.S4: No state shared between fights** · Size M · Status: Todo
> *As the Agent, I want each simulated fight independent of the ones before it, so that results do not drift over a batch (FI-11).*
>
> **Acceptance criteria**
> - [ ] Singletons and static caches touched by a fight are reset, or each fight runs in a fresh context; the reset list is documented.
> - [ ] Test: replay A, replay B, replay A again in one process: both A runs give identical checksums and field comparisons.

> **P7.E3.S5: Version guard** · Size S · Status: Todo
> *As the Next Session, I want the host to refuse a game build it was not checked against, so that a Steam update cannot silently corrupt results (FI-3, EN-7).*
>
> **Acceptance criteria**
> - [ ] The host stores the build commit and model-id hash its fidelity suite last passed on, and refuses to run decision mode on any other, with a message pointing to the patch runbook (E7.S4).

### P7.E4: Combat interface

> **P7.E4.S1: Load a fight** · Size M · Status: Todo
> *As the Agent, I want to start a simulated fight from a recorded room entry or from my own save copy, with the right unlocks and progress, so that generation inside the fight matches the game (FI-5, FI-6).*
>
> **Acceptance criteria**
> - [ ] Loading from a replay (`CombatReplay.serializableRun` plus synchronizer ids) and from a room-entry `SerializableRun` both work.
> - [ ] Unlock state and progress fields come from the loaded data; solo fights load as single-player.

> **P7.E4.S2: One naming table for live and engine ids** · Size S · Status: Todo
> *As the Agent, I want live-API card, power, relic, potion and monster ids mapped to engine models in one place, so that live states and simulated states line up (EN-6).*
>
> **Acceptance criteria**
> - [ ] `tools/sim.py` holds the table; a test maps every id in the live fixtures (`tools/tests/fixtures/live/`) and the replay corpus without a miss.

> **P7.E4.S3: Legal actions and stepping** · Size L · Status: Todo
> *As Phase 8 code, I want to list the legal actions, apply one and get the new observation, so that search can explore a fight.*
>
> **Acceptance criteria**
> - [ ] Actions: play card (with target), use potion (with target), discard potion, end turn, and every in-fight choice prompt (card selection, choose one of N) through the player-choice path.
> - [ ] Each step returns the observation (through the shared encoder, E6.S5), the events, and a status (EN-5).
> - [ ] The legal-action list equals the live game's on the same state, tested on recorded fights.

> **P7.E4.S4: Branching** · Size M · Status: Todo
> *As Phase 8 code, I want to branch a fight at any point cheaply, so that search can try many lines (EN-2, EN-3).*
>
> **Acceptance criteria**
> - [ ] Two methods implemented and measured: replay from room entry with cached prefixes, and cloning live objects (`AbstractModel.MutableClone` and the combat containers). The cheaper correct one becomes the default; both results go in the performance report.
> - [ ] A branch never changes its parent (test).

> **P7.E4.S5: Python bridge** · Size M · Status: Todo
> *As the Agent, I want the simulator callable from Python with batching, so that the existing tools can use it.*
>
> **Acceptance criteria**
> - [ ] `tools/sim.py` talks to the host over JSON lines (stdin and stdout, or a local socket bound to 127.0.0.1). Requests are batchable: load, legal actions, step, branch, rollout with a named policy.
> - [ ] Errors come back as statuses, never as a hung process; a watchdog restarts a stuck host.

### P7.E5: Fidelity suite

> **P7.E5.S1: Replay the corpus** · Size M · Status: Todo
> *As the Agent, I want every recorded fight replayed in fidelity mode with checksums compared, so that exactness is measured.*
>
> **Acceptance criteria**
> - [ ] `tools/sim.py fidelity` replays the corpus and compares the game's recorded checksums step by step. It reports the match rate and the first divergence per failure (action id, state diff).

> **P7.E5.S2: Compare more than the checksum** · Size M · Status: Todo
> *As the Agent, I want intents, monster move state, card costs and upgrades, pile order and RNG counters compared at checkpoints, so that a checksum match cannot hide an error (FI-12).*
>
> **Acceptance criteria**
> - [ ] Field comparisons run at every end of turn. The recorded side comes from the replay's own re-run in the live game where available, otherwise from the API trace (E2.S4).

> **P7.E5.S3: Live observations against simulated ones** · Size M · Status: Todo
> *As the Agent, I want the live API's observation and the simulator's observation of the same moment compared through the shared encoder, so that the observation pipeline matches too (ML-1).*
>
> **Acceptance criteria**
> - [ ] For recorded fights with an API trace, every step's encoded observation matches, or the difference is documented as a known encoding gap.

> **P7.E5.S4: Reports carry their fidelity** · Size S · Status: Todo
> *As the Next Session, I want every simulator-based number stamped with the suite version and pass rate, so that results from a broken simulator are recognisable (FI-15).*
>
> **Acceptance criteria**
> - [ ] `reports/phase7/fidelity.md` is generated with game build, suite version, corpus size, pass rate and known gaps. `templates/` gains a simulator-report header that Phase 8 and 9 reports use.

> **P7.E5.S5: Live API field audit** · Size S · Status: Todo
> *As the Agent, I want a test that fails when the live API starts exposing hidden information, so that a mod update cannot leak it silently (FP-11).*
>
> **Acceptance criteria**
> - [ ] A test lists every field path in the live fixtures. Fields matching seed, RNG, order or future patterns must be on the reviewed list in `docs/simulator-integrity.md` §1.1, or the test fails.

> **P7.E5.S6: Coverage** · Size M · Status: Todo
> *As the Agent, I want to know which cards, relics, powers, potions and monsters the corpus has exercised, so that blind spots are visible.*
>
> **Acceptance criteria**
> - [ ] Coverage table in `reports/phase7/fidelity.md`. Uncovered items with special mechanics are listed for targeted tests: in an offline instance gym, only with the Player's approval (SA-6), or as code-reading notes.

### P7.E6: Fair-play layer

> **P7.E6.S1: Mode separation and the state sanitizer** · Size M · Status: Todo
> *As the Player, I want decisions made only from what a player could see, so that the Agent's results mean something (FP-1, FP-3, FP-15).*
>
> **Acceptance criteria**
> - [ ] Fidelity mode and decision mode have separate entry points; decision mode refuses input that has not passed the sanitizer.
> - [ ] The sanitizer rebuilds the current state, checks it equals the live observation (else stops and reports), hides the draw order, replaces the run seed and re-seeds every random generator (FP-2), and re-samples hidden pre-rolled state. The inventory of hidden pre-rolled state is documented (OQ7.3).

> **P7.E6.S2: Re-seed every random generator** · Size M · Status: Todo
> *As the Agent, I want the run seed and every random generator replaced per sampled world, so that no future roll is predictable (FP-2, FP-8, FP-9).*
>
> **Acceptance criteria**
> - [ ] The run seed, the 12 `RunRngSet` streams, the 3 `PlayerRngSet` streams and every other `Rng` instance reachable from the run and combat objects (each monster's `_rng`, event generators, relic-held ones) are re-seeded per sample from a logged sampler seed. The generators are found by walking the objects, not from a fixed list.
> - [ ] Test: after sanitizing, no reachable `Rng` has the state it had before. Two samples with different sampler seeds diverge on the next shuffle and the next monster roll.

> **P7.E6.S3: Draw-pile sampler** · Size M · Status: Todo
> *As the Agent, I want sampled draw orders consistent with what the player knows, so that search neither cheats nor forgets (FP-5, FP-14).*
>
> **Acceptance criteria**
> - [ ] Known positions (cards the player put on top or bottom; order revealed by card effects) are kept; everything else is shuffled.
> - [ ] Test on recorded fights: every sampled world is consistent with the observation at that moment.

> **P7.E6.S4: Invariance audit and leak canary** · Size L · Status: Todo
> *As the Player, I want proof that decisions do not depend on hidden information, so that I can trust the comparisons with my record.*
>
> **Acceptance criteria**
> - [ ] Invariance: for 200 recorded decision points, re-running the decision with the true RNG replaced by other seeds (same observation) gives the same action distribution within sampling noise.
> - [ ] Canary: a test plants a hidden advantage (for example the true draw order puts a lethal card next) and checks the decision does not use it more often than chance.
> - [ ] Both run in the fidelity suite and block decision mode when they fail.

> **P7.E6.S5: Observation encoder** · Size M · Status: Todo
> *As Phase 8 and 9 code, I want one documented observation format, built only from live-API fields, so that live and simulated play look the same to every model (ML-1, FP-7).*
>
> **Acceptance criteria**
> - [ ] `docs/observation-spec.md` lists every field, its source in the live API and in the engine, and its encoding. The gray-zone `move_id` is documented as used only to look up the visible move.
> - [ ] One implementation, used by both the live tools and the simulator bridge, with tests on live fixtures and simulated states.

### P7.E7: Performance and operations

> **P7.E7.S1: Benchmarks** · Size S · Status: Todo
> *As the Agent, I want fights per second, step latency, branch cost and memory measured, so that Phase 8 can size its search budget.*
>
> **Acceptance criteria**
> - [ ] `reports/phase7/performance.md` with hallway, elite and boss fights: median and p95 per fight, per step and per branch; memory per process; start-up time. Compared with the speed target in §1.

> **P7.E7.S2: Worker pool** · Size M · Status: Todo
> *As the Player, I want simulator jobs to share my Mac politely, so that it stays usable (SA-7, EN-4).*
>
> **Acceptance criteria**
> - [ ] `tools/sim.py` runs N host processes (default: half the cores) at low priority; restarts a worker after a set number of fights; a leak test runs 100,000 fights with memory sampled.

> **P7.E7.S3: Failure handling** · Size S · Status: Todo
> *As the Agent, I want failed simulations counted and sampled, so that a silent failure cannot bias results (EN-5).*
>
> **Acceptance criteria**
> - [ ] Each batch reports its failure rate; above 0.1% the batch is marked unusable and the first failures are saved for review.

> **P7.E7.S4: Game patch runbook** · Size S · Status: In progress (runbook extended 2026-11-19 with the checks that exist)
> *As the Next Session, I want a fixed procedure after every game update, so that the simulator is re-checked before use (FI-4).*
>
> **Acceptance criteria**
> - [x] `docs/runbooks/game-patch.md` (from P2.E7.S1) now runs `tools/game_facts.py` (the facts our rules cite), `tools/game_cards.py` and `tools/game_monsters.py` (numbers), and regenerates the notes.
> - [ ] Added once they exist: run the fidelity suite, update the version guard.

### P7.E8: Run-level simulation (after Phase 8 starts)

> **P7.E8.S1: Rewards after combat** · Size L · Status: Todo
> *As Phase 9 code, I want card, potion and gold rewards generated in the simulator with sampled streams, so that drafting can be trained (FP-9).*
>
> **Acceptance criteria**
> - [ ] Rewards come from the game's own factories with sampled `Rewards` streams and the profile's unlock state (FI-5); distributions checked against recorded rewards from real runs.

> **P7.E8.S2: Map, rest sites, shops, events and treasure** · Size XL (split before starting) · Status: Todo
> *As Phase 9 code, I want the rest of a run simulated, so that strategic decisions can be learned on whole runs.*
>
> **Acceptance criteria**
> - [ ] Each room type runs through the game's own logic with sampled streams; event choices go through the same choice interface as combat prompts.
> - [ ] Run-level fidelity checked on recorded runs where the true streams are known (fidelity mode only).

> **P7.E8.S3: Full-run driver** · Size L · Status: Todo
> *As Phase 9 code, I want to play whole simulated runs with a pluggable policy, so that run outcomes can train strategic models.*
>
> **Acceptance criteria**
> - [ ] A run from Neow to the Act 3 boss with any policy; outputs the run record in the same format as `data/runs.db` rows; runs per hour measured.

---

## 4. Exit gate

- [ ] M10: spike verdict recorded (route chosen, numbers in `reports/phase7/spike.md`).
- [ ] M11: at least 99% of at least 100 recorded fights match (checksums and field comparisons), across all three acts and every boss met so far. Every mismatch is explained or listed as a known gap.
- [ ] Speed: at least 20 fights per second per core (minimum); the 200 target is met or the gap is explained.
- [ ] Integrity: sandbox tests (SA-1 to SA-4), isolation (FI-11), version guard (FI-3), invariance audit and leak canary (E6.S4) pass in the suite.
- [ ] The Python bridge is used by at least one Phase 8 prototype.

---

## 5. Open questions

| ID | Question | Resolved by |
|---|---|---|
| OQ7.1 | Does `ModelDb` start without the Godot engine? Desk check: its own methods call no Godot method; `RelicModel`'s static constructor creates a `Godot.StringName` | E1.S2 |
| OQ7.2 | ~~What enables `CombatReplayWriter`, and where does it write?~~ Answered 2026-11-19: always on outside TestMode; `replays/latest.mcr` per profile, overwritten each fight | E2.S1 (done) |
| OQ7.3 | Which hidden state is pre-rolled and stored (beyond the draw order and random generators)? Known so far `[GAME]`: each monster stores `NextMove` (the move its shown intent comes from; hidden for Hidden intents) and a move state machine whose random branches roll at transition time; each monster has its own generator | E6.S1 (inventory from the IL of monster and power models) |
| OQ7.4 | Is branching cheaper by replay or by cloning? | E4.S4 |
| OQ7.5 | Can the in-progress fight's actions be read live (replay events or our own log) with enough detail to rebuild the state, including hook resumes and player choices? | E2.S2, E6.S1 |
| OQ7.6 | Is 200 fights per second realistic? First measurement: 32 per core on a long boss fight, with the cost in the game's own logic rather than in the stubs. Needs profiling (allocations, hook dispatch) and cheap branching before the target is judged | E7.S1, E4.S4 |
| OQ7.7 | Does the game's own replay validation (`NMultiplayerTest.ValidateReplay`) pass on our recorded fights in the real game? This tells real-game determinism apart from host errors. | E5.S1 |
