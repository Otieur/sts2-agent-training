# Status Board

Update this file whenever a story changes status. Story-level status lives in each phase document; this board tracks epics.

**Active phase:** Phase 4 (solo practice) is live: the Agent's first run on profile 2 won at A0 on 2026-11-19 (M3); the ladder is at A1. Phase 0 has only small items left (precise latency, permissions allowlist). Phases 1 and 2 are done; Phase 3 shadowing ran in the first live session. The overnight session of 2026-11-19 is summarised in `docs/overnight-report.md`.
**Engine track (2026-11-20):** Phase 7 simulator works for fights and whole runs: the game's own code runs in our process, recorded fights replay exactly (10 of 10), fights start from nothing for all 85 encounters, whole runs play from a seed through every room type, decision mode is fair-play checked (8 of 8). Next: Phase 8 search on top of it (snapshot and restore exist), the two-player host for co-op. Direction: `docs/decisions/0003-engine-simulator-and-learning.md`.
**Current priority (2026-11-22):** the act 3 boss first (decision `docs/decisions/0006-act-3-boss-first.md`). On the corrected simulator the Agent wins 8 of 104 runs at A0 and 8 of the 42 act 3 boss fights it reaches (the Player 13 of 15), with the Player's deck size, HP and relics. In order: the fight search where it misjudges a fight (found by a trace: against the Test Subject a lost rollout was valued by the form alive, so the search avoided killing the first form; correction under test in boss replay 2), judged on fights; then decks for long fights, one run benchmark at a time (boss credit in rollouts, bottom-tier cards kept out of late rewards, upgrades, energy). Gates unchanged.

**Current priority (2026-11-20, evening):** whole runs first (decision `docs/decisions/0004-whole-run-first.md`). Wide search wins 99 of 120 benchmark fights and is used to play every fight inside simulated runs; the strategic decisions (Neow and Ancients, card rewards, removal, upgrades and rest, shop, route, events, boss relics, potions) are now the main training target, judged by whole-run results at A5 and A10.
**Review (2026-11-21):** run benchmark 8 found no win in 30 whole new runs at A0. The review `docs/reviews/2026-11-21-training-review.md` finds the Agent reaches bosses underpowered (potions never used, upgrades on Strikes, gold unspent, three relics against five) while fight search is at the Player's level on the same situations, and rollouts are judged by a weaker fighter than the one that plays. Direction accepted by the Player the same day: `docs/decisions/0005-a0-first-and-resource-use.md` (A0 first, wins as the metric, use every resource, a fight-outcome model inside rollouts). Next gates: M19 (simulated A0 win rate at least 50%), M20 (at least 63%). First result under decision 0005 (run benchmark 11, A0, 30 seeds): potions, the smith rule and shops together add 7.0 floors (p 0.0005), the act 1 boss falls in 25 of 30 runs against 16 of 29, one run wins; runs now end in act 2 and shops still leave 503 gold unspent. Run benchmark 12 (each component removed in turn, same seeds): potions carry the gain (+6.8 floors, p 0.011; without them the stack is back at the old policy's level), the smith rule +2.2 (p 0.20; act 2 boss 6 of 15 against 1 of 14) and shops +3.0 (p 0.50) are not shown; all three stay by the registered rule. Correction (2026-11-21): in run benchmarks 11 and 12 card and route rollouts were played by the first arm's rule policy (`path` in 11, `path+smith` in 12) instead of each arm's own, so 12's drop-one differences carry a second difference and 11's treatment had old-rule rollouts; numbers stand as measured, section 6 of each report; fixed in `tools/run_bench.py` (`set_evaluator`). The shop component left every shop entered with more than about 180 gold to the rule, which leaves; `rshop2` repairs it. Run benchmark 15 (A0, 30 seeds, two factors, finished 2026-11-22 01:02): events and card choices outside fights by rollouts (`ropt`) +2.9 floors (17 seeds better, 7 worse, p 0.032, holds); shops with every item judged (`rshop2`) +0.2 floors (p 0.50, not shown) although the gold is now spent (210 left against 455); 4 wins in 120 runs; bosses end 82 of 116 lost runs (act 2 boss 41). Beside the Player's runs the Agent reaches the act 2 boss with 5.9 relics against 9.9 and 7.4 upgraded cards against 10.1, with more HP at the act 1 boss (77% against 60%) and half as many elites fought. Both treatments enter the stack by the registered rule (`rcard+rpath+pot+smith+rshop2+ropt`). Run benchmark 18 (fights in rollouts ended by the fight-outcome model `fight-v1c`) started on it at 01:02.
**Last updated:** 2026-11-21

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
| P7.E6 | Fair-play layer | In progress | Sanitizer (every generator re-seeded; known draw positions kept, FP-5), hidden pre-rolled state inventoried (FP-16), `tools/sim.py fairplay` 8 of 8; run-level re-sampling of pre-rolled content done 2026-11-21 (`sim/RunSampler.cs`, `tools/sim.py runclone`: exact rebuilds, determinism, difference across seeds, leak canary) |
| P7.E7 | Performance and operations | In progress | S4: patch runbook extended with `tools/game_facts.py`, `game_cards.py`, `game_monsters.py` |
| P7.E8 | Run-level simulation | In progress (done early) | Whole runs from a seed through every room type and act change (2026-11-20); batches of 40 flow-test and 30 normal runs all finish (`reports/phase7/whole-runs-*.md`); the closing Architect scene after the last boss is not entered (FI-7c); S4 (2026-11-21): run-level clones from the room-entry save kept in memory (`run_export`, `run_from_save`) and the run sampler |

---

## Phase 8: Combat search and autopilot ([doc](phase-8-combat-search.md))

| Epic | Title | Status | Notes |
|---|---|---|---|
| P8.E1 | Evaluation harness | In progress | Benchmark set `data/sim/benchmark-v1.json` (60 fights from history specs), comparison template, paired runner `tools/learn/bench.py`; five pre-registered comparisons run on 2026-11-20 |
| P8.E2 | Search | In progress | Flat Monte Carlo over every distinct legal move (`mcw6`) wins 99 of 120 benchmark games (+51 value per fight over the planner; +27 over search limited to the planner's candidates, pre-registered, `reports/phase8/wide-candidates.md`); more worlds per candidate add little; potions promising but not established |
| P8.E3 | Leaf evaluation | In progress | Value-network leaves tested three times (pre-registered), not yet better than rollouts |
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
| P9.E4 | Strategic decisions | In progress | Main line since 2026-11-20 (decision 0004): run benchmark `tools/run_bench.py`; first comparison (planner combat) shows deck building cannot be judged without search in fights; search combat inside runs via `export_fight`; 2026-11-21: search in every fight inside runs works (`fight_from_save`, 0.3% fallbacks), run benchmark 2: hand-made deck rules lose to the first card (−2.4 floors), route planner helps (+2.7); run benchmark 3: card rewards by sampled rollouts (`tools/run_eval.py`) beat the draft scorer by +6.6 floors (p 6e-8), first act 2 boss wins; run benchmark 4: map routes by rollouts +1.1 floors over the route planner (p 0.04, by avoiding elites, no more boss wins); run benchmark 5: card rollouts beat the first card by +5.5 floors (p 9e-5; act 2 boss reached in 12 runs against 1; 0 search fallbacks with the run-clone rebuild); run benchmark 6 (A10): card and route rollouts +2.8 floors over the rules (p 4e-5), all by reaching the act 1 boss (48 of 60 runs against 24), which they beat in 5 of 48 fights (the Player: 12 of 19); run benchmark 7: meant to test credit for boss progress in the rollout value, but the credit was never applied (evaluator defect found 2026-11-21: a worker's evaluators kept the first arm's settings), so its two arms were one policy (−0.45 floors, 45 of 60 seeds equal) and the idea is untested; 3 act 1 boss wins in 99 fights at A10; run benchmark 8: 0 wins in 30 whole new runs at A0 (mean floor 26.5; bosses end 21 runs; the Player 5 of 8 at A0–4); run benchmark 9 (A10): events, rest sites and card choices by rollouts +1.9 floors, not significant by the registered test (p 0.084), not adopted yet; boss replay 1: on the 98 boss fights A10 runs reach, twice the search budget does not help (11 wins against 15) while search is far ahead of the planner (+28 value): the decks are the limit, not the search; run benchmark 11 (A0, decision 0005): potions in fights, the smith-first rest rule and shop purchases together against the current policy +7.0 floors (21 better, 4 worse, p 0.0005), act 1 boss 25 of 30 against 16 of 29, act 2 boss 6 of 15 against 1 of 8, wins 1 against 0 of 30; shops buy about one card per run and leave 503 gold; run benchmark 12 (A0, each of the three removed in turn on the same seeds): potions +6.8 floors (p 0.011), smith rule +2.2 (p 0.20), shops +3.0 (p 0.50), all three stay; run benchmark 15 (A0, two factors): `ropt` +2.9 floors (p 0.032), `rshop2` +0.2 (p 0.50), 4 wins in 120 runs, both enter the stack; run benchmark 18 (A0, fights inside rollouts ended by the fight-outcome model `fight-v1c`): −9.7 floors at the act horizon (6 seeds better, 21 worse) and −14.6 at the run horizon, not adopted; the model's arms die in hallway fights entered at low HP (14 and 12 of 29 runs against 4) and the model does not beat base rates on the run's own fights (elite AUC 0.55 against 0.75); the stack without it reached floor 36.0 with 1 win in 29; a run was found to depend on what its worker played before it (rollout futures numbered over the worker's life; numbered inside the run from run benchmark 19 on, where a fight past turn 100 is also given up); a simulator defect found through the same run: a shop's card removal could be bought repeatedly (FI-7e; in 8 to 9% of runs with rollout purchases, none of the 5 wins), fixed in host build Release4; 2026-11-22 07:30: a second and larger defect found by going through what the game's screens do for its logic (`tools/asm/ui_only.py`): **a relic picked from a chest never reached the player** (FI-7f), in every whole run so far, so all floors and wins up to run benchmark 18 are those of a harder game (one or two relics short an act) and comparisons hold only within a benchmark; fixed in host build Release5, on which everything runs from here; run benchmark 16 on Release5 (2026-11-22 07:42–14:43, 26 of 30 seeds): route rollouts against the route planner +0.94 floors (11 seeds better, 11 worse) and the shop rule that buys `bshop` +1.48 (12 and 12), neither established, the two interacting (routes −3.2 floors without `bshop`, +5.0 with it); 8 wins in 104 runs (7.7%), the best cell `rcard+rpath+pot+smith+rshop2+ropt+bshop` 4 of 26, which is the stack from here by the registered rule; with chest relics the Agent holds 9.0 relics at the act 2 boss against the Player's 9.9 and beats it in 73% of the fights, and **the act 3 boss is now the wall** (8 of 42 won; Queen 0 of 9, Test Subject 3 of 24; it ends 34 of the 96 lost runs), next to be looked at in the recorded fights and in the simulator's Queen and Test Subject against the game's code; queue running at A0: run benchmark 19 (started 2026-11-22 14:43, deadline 21:43: elites fought while healthy and healing before a boss, two factors on the stack after 16), 17 (boss credit), then fight batch b1 and the fight-outcome model v2; a low-priority batch of elite and boss fights (b0) fills idle cores beside the queue; run benchmark 13 withdrawn (its question is a factor of 15), 14 (gate G1) deferred until a 30-seed benchmark shows at least 12 wins; run benchmark 10 (shops at A10) withdrawn before its start |
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
| M15 | Run benchmark with search playing every fight (decision 0004) | Done | 2026-11-21 | reports/phase9/run-bench-2.md (180 runs at A5, wide search in every fight, 0.6% planner fallbacks) |
| M16 | Every strategic decision type has a policy validated on the run benchmark | — | | |
| M17 | Simulated A5 win rate above 25% on the run benchmark | — | | |
| M18 | Simulated A10 win rate above 8% on the run benchmark | — | | |
