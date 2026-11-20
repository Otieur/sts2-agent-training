# Status Board

Update this file whenever a story changes status. Story-level status lives in each phase document; this board tracks epics.

**Active phase:** Phase 4 (solo practice) is live: the Agent's first run on profile 2 won at A0 on 2026-11-19 (M3); the ladder is at A1. Phase 0 has only small items left (precise latency, permissions allowlist). Phases 1 and 2 are done; Phase 3 shadowing ran in the first live session. The overnight session of 2026-11-19 is summarised in `docs/overnight-report.md`.
**Engine track (2026-11-20):** Phase 7 simulator works for fights and whole runs: the game's own code runs in our process, recorded fights replay exactly (10 of 10), fights start from nothing for all 85 encounters, whole runs play from a seed through every room type, decision mode is fair-play checked (8 of 8). Next: Phase 8 search on top of it (snapshot and restore exist), the two-player host for co-op. Direction: `docs/decisions/0003-engine-simulator-and-learning.md`.
**Last updated:** 2026-11-20

---

## Phase 0: Setup ([doc](phase-0-setup.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P0.E1 | Save safety | In progress | Backup taken and verified overnight, still matching after the branch switch; Steam Cloud is on (choose local files on a cloud conflict after a restore) |
| P0.E2 | Game version | Done | Main v0.111.1 running; the modded profile loads with everything unlocked (2026-11-19) |
| P0.E3 | Mod acquisition and security review | In progress | Draft review done (both mods); the Player chose STS2-Agent (decision 0001 accepted) and approved the verdict and the .NET 9 SDK install (2026-11-19) |
| P0.E4 | Build and install | Done | STS2-Agent 0.16.2 built (0 warnings against v0.111.1), installed DLL-only, loaded by the game; `/health` ready, 28 of 28 game members resolved (2026-11-19) |
| P0.E5 | API smoke test | In progress | Live 2026-11-19: every screen met passed; one card and one full fight played; event stream probed (no card plays in it); 16 screen samples saved. Left: card-reward and relic-reward samples, precise latency, live error shapes |
| P0.E6 | The agent harness integration | In progress | CLI tested live (decision 0002: CLI primary, MCP off). Left: gameplay skill review (S3), permissions allowlist (S4, needs the Player), unfocused-game test (S5) |
| P0.E7 | Fallback path | Done | Not needed: STS2-Agent works on v0.111.1 (decision 0001 results) |
| P0.E8 | Project scaffolding | Done | Folders, the project instructions, git (local), templates (2026-11-19 overnight) |

## Phase 1: History analysis ([doc](phase-1-history-analysis.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P1.E1 | Dataset extraction | Done | 233 runs; validation passes; decks 232/232 |
| P1.E2 | Card evaluation | Done | Card-type rules wait for Phase 2 data |
| P1.E3 | Encounter danger and benchmark | Done | Benchmark frozen: data/benchmarks/ironclad-encounters-v0.107.1.csv |
| P1.E4 | Pathing, rest, shops, events, Ancients, potions | Done | Rest 50/50 point: 27% HP |
| P1.E5 | Death analysis | Done | 55% of deaths in Act 1 |
| P1.E6 | Deck archetypes | Done | No strong clusters (silhouette ~0.04) |
| P1.E7 | Visual report | Done | Artifact "Ironclad Run History": (private link) |
| P1.E8 | Player interview | Done | Closed after 2 batches; goal clarified as strong play, not imitation |
| P1.E9 | Playbook v1 | Done | playbooks/ironclad.md v1; Player review optional |

## Phase 2: Knowledge base ([doc](phase-2-knowledge-base.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P2.E1 | Game data export | In progress | Decompiled extract imported; it predates v0.107.1, so card changes are patched (knowledge/data/card-patches.json) and both version deltas documented; live /data export needs Phase 0 |
| P2.E2 | Mechanics reference | Done | mechanics.md, ascension.md; verification checklist for Phase 4 |
| P2.E3 | Enemies and encounters | Done | 83-encounter catalogue; 12 elite + 19 hallway notes (15 most frequent, 4 rare but deadly), all with the community wiki's move tables (2026-11-19); Bestiary cross-check (S4) needs the live game |
| P2.E4 | Community strategy | Done | sources.md, ironclad-tiers.md, archetypes-ironclad.md, discrepancies.md |
| P2.E5 | Boss plans | Done | All 12 bosses; Aeonglass community-only. Fight simulator (tools/simulate_fight.py) calibrated for Vantom, Lagavulin Matriarch, Soul Fysh, Byrdonis, Entomancer; Waterfall Giant, Ceremonial Beast, Knowledge Demon, The Kin, The Insatiable modelled but not validated (sensitivity checks name what to read in the first fight); boss move tables checked against the community wiki |
| P2.E6 | Playbook v2 | In progress | Now v2.17: checked against the data (tools/check_playbook.py, 60 checks including the quick reference), decision-point analyses, death review, boss-specific plan choice from the simulator; optional Player skim (S2) |
| P2.E7 | Knowledge maintenance | Done | docs/runbooks/game-patch.md |

## Phase 3: Shadowing ([doc](phase-3-shadowing.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P3.E1 | Live view of the Player's game | In progress | Watcher with combat trace running live (`tools/smoke.py --watch --trace`); The Kin, The Insatiable and the Queen recorded 2026-11-19 |
| P3.E2 | Call-it-first (non-combat) | In progress | `tools/shadow.py` running live since 2026-11-19 (`runs/shadow-01/`); map and rest pick resolution fixed; early agreement: maps 6/9, card rewards 3/6 |
| P3.E3 | Combat calls | In progress | Trigger policy and full-turn calls in tools/shadow.py |
| P3.E4 | State recorder and reconstruction | In progress | record.py and reconstruct.py written with offline tests |
| P3.E5 | Metrics and calibration | Todo | |
| P3.E6 | Retros and playbook v3 | Todo | |

## Phase 4: Solo practice ([doc](phase-4-solo-practice.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P4.E1 | Run harness | In progress | Runbooks written (start, decision loop with STS2-Agent screen table, end of run with STS2-Agent game-over actions); `advise.py --live` gives state and advice in one command; resume test (S5) needs a live run |
| P4.E2 | Combat procedure | In progress | S1, S3, S4 done (plan_turn.py, journal.py); planner covers the common Ironclad cards whose text the extract leaves incomplete, playable statuses (Sandpit guard), 17 potions and the boss and elite powers in the notes; S2 calculator awaits in-game verification |
| P4.E3 | Strategy procedures | Done (tooling) | path.py, draft.py, advise.py, deck_check.py; advise.py never raises on damaged states (fuzz test); untested live |
| P4.E4 | Post-mortem | In progress | S1 facts sheet done (postmortem.py, tested on the Player's runs) |
| P4.E5 | Evaluation | In progress | Scoreboard: 2 Agent runs (A0 won 2026-11-19; A1 died to the act 1 boss 2026-11-20) |
| P4.E6 | Ascension ladder | In progress | Rules written |
| P4.E7 | Operations | Todo | |

## Phase 5: Second character ([doc](phase-5-second-character.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P5.E1 | Rerun the history pipeline | Done | All characters; cross-character report |
| P5.E2 | Necrobinder knowledge | In progress | S3 done (tiers, discrepancies, archetypes; tiers fail the decision-point check); S2 Osty, Summon and Doom from the power data; planner models Unleash and Doom |
| P5.E3 | Playbook v1 (Necrobinder) | In progress | playbooks/necrobinder.md v0.3 (groundwork) |
| P5.E4 | Light shadowing | Todo | |
| P5.E5 | Solo ladder | Todo | |
| P5.E6 | Transfer report and co-op pairing | Todo | Player decides pairing |

## Phase 6: Co-op ([doc](phase-6-coop.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P6.E1 | Verify co-op rules | In progress | Rules file done; in-game verification and HP scaling measurement (S2) in Phase 6 |
| P6.E2 | Second instance on macOS | In progress | Patch proposal written (user-data path, app-bundle write, exe fallback) |
| P6.E3 | Teammate control | In progress | S1, S2 tooling written offline (sts.py --instance, party; advise.py party line and teammate potion command); untested live |
| P6.E4 | Communication protocol | In progress | Protocol and shorthand drafted in playbooks/coop.md |
| P6.E5 | Co-op strategy | In progress | playbooks/coop.md v0 (draft, before any co-op play) |
| P6.E6 | Co-op run ladder | Todo | |
| P6.E7 | Reliability | Todo | |

---

## Phase 7: Engine simulator ([doc](phase-7-engine-simulator.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P7.E1 | Feasibility spike | Done | **Go, route R3** (2026-11-19, `reports/phase7/spike.md`): a recorded boss fight replays in our own process with all 26 turn-boundary states equal to the game's; 400 warm passes all correct at 31 ms CPU per fight (about 32 fights per second per core: above the minimum of 20, short of the 200 target) |
| P7.E2 | Ground truth from the real game | In progress | S1 done: the game records every fight itself (`replays/latest.mcr`); S2 live 2026-11-20: `tools/play_turn.py` kept 9 fights of the A1 run (hallways, three elites, the boss); no mod change needed |
| P7.E3 | Engine host and sandbox | In progress | `sim/`: fake engine, inert UI (made inert first and eagerly: FI-7b), stubs, single-thread scheduler, sandbox HOME, version check on load; automated sandbox test 3 of 3 (save folder unchanged, sandbox home empty, no network socket) |
| P7.E4 | Combat interface | In progress | Decision mode: reset to a decision point or a fight from nothing (85 of 85 encounters), observe, legal actions, step, card choices through the game's local selector, potions; snapshot and restore by recipe (exact, about 45 ms); live-object cloning not started |
| P7.E5 | Fidelity suite | In progress | `tools/sim.py fidelity`: 11 of 11 recorded fights exact (244 states; nine from the 2026-11-20 run, a lost boss fight included, one from the Player's own play via `tools/keep_replays.py`; other game builds skipped); recorded run reproduced from its seed 71 of 71. Needs 100 fights for M11 |
| P7.E6 | Fair-play layer | In progress | Sanitizer (every generator re-seeded; known draw positions kept, FP-5), hidden pre-rolled state inventoried (FP-16), `tools/sim.py fairplay` 8 of 8; run-level re-sampling of pre-rolled content open |
| P7.E7 | Performance and operations | In progress | S4: patch runbook extended with `tools/game_facts.py`, `game_cards.py`, `game_monsters.py` |
| P7.E8 | Run-level simulation | In progress (done early) | Whole runs from a seed through every room type and act change (2026-11-20); batches of 40 flow-test and 30 normal runs all finish (`reports/phase7/whole-runs-*.md`); the closing Architect scene after the last boss is not entered (FI-7c) |

---

## Phase 8: Combat search and autopilot ([doc](phase-8-combat-search.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P8.E1 | Evaluation harness | Todo | |
| P8.E2 | Search | Todo | |
| P8.E3 | Leaf evaluation | Todo | |
| P8.E4 | Run-context costs | Todo | |
| P8.E5 | Live combat autopilot | Todo | S5 needs the Player's sign-off |
| P8.E6 | Validation in the real game | Todo | |

---

## Phase 9: Learned models and reinforcement learning ([doc](phase-9-learning.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P9.E1 | Data and encoding | In progress | S1 done 2026-11-20 (`tools/learn/encode.py`, vocabulary from the game assembly, 8 tests); S2: `combat-v1` (586 history fights, flat Monte Carlo teacher) |
| P9.E2 | Combat value network | In progress | S1 trainer and model card (`tools/learn/train_value.py`); S2 comparison pre-registered (`reports/phase9/value-search-comparison.md`) |
| P9.E3 | Combat policy and expert iteration | In progress | S1 action-value network (`tools/learn/train_q.py`); self-play takes a value-network teacher |
| P9.E4 | Strategic decisions | Todo | S2 needs P7.E8 |
| P9.E5 | Training infrastructure | In progress | S1 done: PyTorch 2.15.0 approved 2026-11-20 and installed in `.venv-learn/` |
| P9.E6 | Evaluation and the ascension ladder | Todo | |
| P9.E7 | Patch resilience | Todo | |

---

## Milestones

| # | Milestone | Status | Date | Evidence |
|---|---|---|---|---|
| M1 | Clean full run | — | | |
| M2 | Act 1 boss in 3 of 5 | — | | |
| M3 | First solo win (A0) | Done | 2026-11-19 | runs/2026-11-19-1ZWEN4BFQUZL |
| M4 | Damage at or below the Player's median (Acts 1–2 hallway, same ascension band) | — | | |
| M5 | Solo win at A5 | — | | |
| M6 | First co-op win | — | | |
| M7 | Solo win at A10 (stretch) | — | | |
| M8 | Better than the Player (band win rate over 10+ runs: A5–9 above 25%, A10 above 8%) | — | | |
| M9 | 3 A10 wins in 10 consecutive A10 runs (stretch) | — | | |
| M10 | Engine spike verdict: the game's combat runs in our own process (or route R4) | Done | 2026-11-19 | reports/phase7/spike.md |
| M11 | Simulator fidelity (99% of 100+ recorded fights exact) and speed (20+ fights/s per core; target 200) | — | | |
| M12 | Combat autopilot: every fight of 3 real runs, no language-model calls, median decision 1 s or less | — | | |
| M13 | Search beats the rule planner (pre-registered) | — | | |
| M14 | Learned combat models beat search with heuristic evaluation (pre-registered) | — | | |
