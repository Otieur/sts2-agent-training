# Status Board

Update this file whenever a story changes status. Story-level status lives in each phase document; this board tracks epics.

**Active phase:** Phase 0 (waiting on the Player: security verdict, branch switch to main v0.111.1, mod and SDK choice; then `docs/runbooks/first-session.md`). Phases 1 and 2 are done offline; Phase 4 tooling is ready and untested live.
**Last updated:** 2026-11-19

---

## Phase 0: Setup ([doc](phase-0-setup.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P0.E1 | Save safety | In progress | Backup taken and verified overnight; Steam Cloud setting (S3) needs the Player |
| P0.E2 | Game version | In progress | Target is now main v0.111.1 (since 2026-11-16); Player switches branch |
| P0.E3 | Mod acquisition and security review | In progress | Draft review done (both mods); Player approves verdict |
| P0.E4 | Build and install | In progress | Toolchain checked; nothing built |
| P0.E5 | API smoke test | In progress | tools/smoke.py (read-only) and docs/runbooks/first-session.md ready; needs the live mod |
| P0.E6 | The agent harness integration | In progress | tools/sts.py CLI (both mods, co-op instances) written and tested offline |
| P0.E7 | Fallback path | In progress | Decision 0001 (revised) proposes STS2-Agent first on v0.111.1; STS2MCP is the fallback |
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
| P2.E3 | Enemies and encounters | Done | 83-encounter catalogue; 12 elite + 15 hallway notes; Bestiary cross-check (S4) needs the live game |
| P2.E4 | Community strategy | Done | sources.md, ironclad-tiers.md, archetypes-ironclad.md, discrepancies.md |
| P2.E5 | Boss plans | Done | All 12 bosses; Aeonglass community-only. Fight simulator (tools/simulate_fight.py) calibrated for Vantom, Lagavulin Matriarch, Soul Fysh, Byrdonis; Waterfall Giant, Ceremonial Beast, Knowledge Demon, Entomancer modelled but not validated (sensitivity checks name what to read in the first fight) |
| P2.E6 | Playbook v2 | In progress | Now v2.15: checked against the data (tools/check_playbook.py, 60 checks including the quick reference), decision-point analyses, death review, boss-specific plan choice from the simulator; optional Player skim (S2) |
| P2.E7 | Knowledge maintenance | Done | docs/runbooks/game-patch.md |

## Phase 3: Shadowing ([doc](phase-3-shadowing.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P3.E1 | Live view of the Player's game | In progress | sts.py brief view and watch.py written; untested live |
| P3.E2 | Call-it-first (non-combat) | In progress | tools/shadow.py (calls before the Player acts; agreement from the next state); untested live |
| P3.E3 | Combat calls | In progress | Trigger policy and full-turn calls in tools/shadow.py |
| P3.E4 | State recorder and reconstruction | In progress | record.py and reconstruct.py written with offline tests |
| P3.E5 | Metrics and calibration | Todo | |
| P3.E6 | Retros and playbook v3 | Todo | |

## Phase 4: Solo practice ([doc](phase-4-solo-practice.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P4.E1 | Run harness | In progress | Runbooks written; resume test (S5) needs a live run |
| P4.E2 | Combat procedure | In progress | S1, S3, S4 done (plan_turn.py, journal.py); planner covers the common Ironclad cards whose text the extract leaves incomplete, playable statuses (Sandpit guard), 17 potions and the boss and elite powers in the notes; S2 calculator awaits in-game verification |
| P4.E3 | Strategy procedures | Done (tooling) | path.py, draft.py, advise.py, deck_check.py; advise.py never raises on damaged states (fuzz test); untested live |
| P4.E4 | Post-mortem | In progress | S1 facts sheet done (postmortem.py, tested on the Player's runs) |
| P4.E5 | Evaluation | In progress | Scoreboard, milestones, exam seeds ready |
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

## Milestones

| # | Milestone | Status | Date | Evidence |
|---|---|---|---|---|
| M1 | Clean full run | — | | |
| M2 | Act 1 boss in 3 of 5 | — | | |
| M3 | First solo win (A0) | — | | |
| M4 | Damage at or below the Player's median (Acts 1–2 hallway, same ascension band) | — | | |
| M5 | Solo win at A5 | — | | |
| M6 | First co-op win | — | | |
| M7 | Solo win at A10 (stretch) | — | | |
| M8 | Better than the Player (band win rate over 10+ runs: A5–9 above 25%, A10 above 8%) | — | | |
| M9 | 3 A10 wins in 10 consecutive A10 runs (stretch) | — | | |
