# Overnight Log (2026-11-20): Full Runs in the Simulator

**Status: IN PROGRESS.** A new session must read "Resume here" first, then continue from the first unfinished stage. The previous night's log is `docs/overnight-log-2026-11-19.md` (finished).

## Instructions from the Player (2026-11-20, before sleeping)
- Work alone through the night; the Player cannot answer questions or approve prompts. He will ask for a report when he wakes; until then keep going. It may be more or less than 10 hours.
- The simulator must: start a fight from nothing (any deck, any encounter); start a new run from a seed and play it to the end in the background, with route choice, card rewards, shops, rest sites, events, the Ancient and the rest. Every run must be a new one.
- Scope: the standard single-player mode only (the run that opens with an Ancient). Not daily, custom or co-op tonight. **Co-op is one of the final goals: keep it prepared at every step** (see "Co-op readiness").
- Everything else on the open list is to be solved too (potions, known draw positions, hidden pre-rolled state, state cloning, automated sandbox test, more recorded fights). Host start-up time (16–40 s) is accepted as it is.
- Authorizations given: launch the game from Steam; control the screen (granted for Steam and the game, background mode); create a branch and push (private repository created: `origin`, branch `overnight/2026-11-20-full-run-sim`); use the external drive if space runs out (17 GB free at the start).

## Limits that still hold tonight
- Profile 1 is never written. Before any real play, confirm the live state says profile 2; otherwise skip real play.
- No credentials typed anywhere; if Steam asks to sign in, stop that step.
- No downloaded code or libraries (nobody can approve a security review): no neural-network framework tonight.
- Real runs follow the scored-run rules: no reloads, no restarts; a loss is recorded as a loss.
- `docs/simulator-integrity.md` applies to everything: decisions only from what a player can see; TestMode never on globally; the simulator never writes saves or touches achievements, Steam or telemetry.
- A blocker that takes more than 45 minutes: write it down here and move to the next item.
- Commit and push after every milestone.

## Co-op readiness (standing requirement)
- No interface assumes one player: observations and actions carry a player index; the session keeps a list of players.
- Run-level code goes through the game's own multiplayer-capable paths (the action queue, the choice synchronizer), not single-player shortcuts.
- When a single-player milestone works, note in this log what a two-player version would need, and try a two-player smoke test where it is cheap.

## Stages
| # | Stage | Done when | Status |
|---|---|---|---|
| 0 | Setup: access, private repository, branch, this log, keep-awake | all in place | Done 2026-11-20 |
| 1 | A fight from nothing: any encounter, any deck, potions usable | `tools/sim.py` can start and finish a chosen fight without a recording | Done: 85 of 85 encounters start from nothing and finish (`reports/phase7/encounter-sweep.md`); custom deck, relics, potions, HP; potion actions |
| 2 | A new run from a seed: Ancient, map, every room type, act changes, run end | a run plays from floor 1 to its end in the host | Done (flow): whole runs from a seed through every room type, act changes and the final boss; 3 of 4 flow-test runs won (test-only max HP), 1 died in act 2 (to investigate) |
| 3 | Run-level fidelity: the Agent's recorded run (seed 1ZWEN4BFQUZL) replayed from its seed; encounters and rewards per floor compared with `runs/2026-11-19-1ZWEN4BFQUZL/run.run` | every floor matches or each mismatch is explained | Todo |
| 4 | Background runs with a simple policy: many new runs, each from a new seed | N runs finish; runs per hour measured | Todo |
| 5 | A real A1 run on profile 2 for recorded fights (replays kept by `tools/play_turn.py`), then the fidelity suite on them | run finished and post-mortem written, or the reason it could not start | Todo |
| 6 | Open list: known draw positions, hidden pre-rolled state inventory, state cloning, automated sandbox test | each done or its blocker written | Todo |
| 7 | Morning report | `docs/overnight-report-2026-11-20.md` | Todo |

## Resume here
Stage 2: a new run from a seed. The run is created the way `NGame.StartNewSingleplayerRun` and `NGame.StartRun` do it (`Player.CreateForNewRun`, `RunState.CreateForNewRun`, `RunManager.SetUpNewSingleplayer`, `FinalizeStartingRelics`, `Launch`, `EnterAct(0)`). The Ancient is an `AncientEventModel` (an event). Next: how the game applies event options, map moves (`MoveToMapCoordAction` already runs on the test path), rewards, rest sites, shops and treasure; the STS2-Agent mod's `GameActionService.*` shows which game calls it uses in the real game.

## Progress
| Time | What | Result |
|---|---|---|
| start | Screen-control access granted (Steam, the game); private repository created and `master` pushed; branch `overnight/2026-11-20-full-run-sim`; keep-awake on | ok |
| +1 h | Stage 1: `new_fight` in the host (new run for a seed, deck, relics, potions, HP, then `RunManager.EnterRoomDebug`); potion actions; game errors captured (`diag`); first sweep 67 of 85 | 18 failed |
| +1.5 h | Fixes from the sweep: speech bubbles (`TalkCmd`) inert; the game's preferences and settings answered with host-owned defaults (Instant speed); three display-only monster and power methods stubbed. Second sweep: **85 of 85 encounters start from nothing and finish** | stage 1 done |
| +3 h | Stage 2: run mode (`sim/Session.Run.cs`): new run as the game creates it, then the event, rest-site, rewards, treasure and act-change synchronizers; card rewards, deck selections, relic and bundle choices in the choice interceptor; end-of-run telemetry, achievements, Steam stats, daily score, run history, progress and save deletion stubbed; asset preloader inert; engine-resource and hover-tip getters answer null or empty | first run: Neow to floor 7 |
| +4 h | Full potion slots handled (discard action; failed rewards no longer offered); display flags forced off on game commands (previews, visuals, animation, sound); effect and sound commands inert; every game-written scene node inert; engine objects get inert stand-ins | **3 of 4 flow-test runs reach and beat the act 3 boss** (floor 46); all room types visited |

