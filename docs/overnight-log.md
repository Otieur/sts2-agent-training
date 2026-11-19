# Overnight Log (2026-11-19)

START: 2026-11-19 00:22:47 EST
END:   2026-11-19 10:22:47 EST
Prompt: `prompts/overnight-2026-11-19.md`

Block K (morning report) starts no later than 09:52 EST.

## Progress

| Block | Start | End | Output | Notes |
|---|---|---|---|---|
| Start-up | 00:22 | 00:24 | log, keep-awake | Keep-awake requested (session_idle) |
| A: Scaffolding | 00:23 | 00:24 | The project instructions, .gitignore, templates/*.md, folders, git init + first commit | P0.E8 done |
| F: Mod review prep | 00:24 | 00:29 | vendor/ clones (STS2-Agent 5d7c306, STS2MCP 55e0648), docs/reviews/sts2-agent-security-review.md, docs/api-notes.md, docs/environment.md, docs/decisions/0001-mod-and-branch.md | Found decompiled game-data index in STS2-Agent repo; STS2MCP has v0.107 fix; .NET 9 SDK missing |
| B0: Game-data import | 00:29 | 00:36 | tools/import_extract.py → knowledge/data/extract-2026-09-21/*.json (577 cards, 121 monsters, 289 relics, 64 potions, 257 powers, 68 events); tools/build_card_reference.py → knowledge/cards/ironclad.md; tools/analyze_deck_features.py → reports/phase2/deck-features-by-encounter.md | Added because the extract changes what Phase 2 can do. Finding: multi-hit count does not separate Vantom outcomes (n=28); fatal Vantom decks carried more single-hit hit-all attacks and less draw |
| B: Community strategy | 00:32 | 00:37 | knowledge/community/{sources,ironclad-tiers,archetypes-ironclad,discrepancies}.md, tools/build_community_tiers.py | Spire Codex (main, July) is the best version match; Nat1 is v0.113 beta; two guides failed the game-data name check. Fixed X-cost tagging (Cascade). |
| C: Mechanics | 00:37 | 00:39 | knowledge/mechanics.md, knowledge/ascension.md | Ascension list checked against run data: A2, A3, A4, A5, A10 confirmed; MetaBot's list refuted |
| D: Boss plans | 00:39 | 00:44 | tools/build_encounter_notes.py (auto data blocks), knowledge/encounters.md, knowledge/bosses/*.md (12 plans) | Community boss research (6 searches + 2 pages); every plan lists checklist, HP threshold, opening turns, potions, killer analysis |
| E: Elites and encounters | 00:44 | 00:46 | knowledge/enemies/*.md (12 elites, 15 hallway) | Entomancer's Personal Hive punishes hit count (H3 replaced); Byrdonis gains Strength every turn; Skulking Colony caps damage per turn; Terror Eel stuns on first damage |
| J: Playbook v2 | 00:46 | 00:47 | playbooks/ironclad.md v2 | Consensus tiers + context overrides, boss table with plan links and thresholds, elite reference, H2 refined, H3 replaced, H7/H8 added |
| H: Other characters | 00:47 | 00:49 | Phase 1 reports + frozen benchmarks for NECROBINDER/SILENT/REGENT; knowledge/cards/{necrobinder,silent,regent}.md; tools/cross_character.py → reports/phase1/cross-character.md | Ironclad has the lowest heal threshold (27%) and the most Act 1 deaths; Vantom is an Ironclad-specific problem |
| G: Offline tools | 00:49 | 00:52 | tools/calc.py + tests, tools/postmortem.py, tools/sts.py (adapters for STS2MCP and STS2-Agent, decision log, safety blocks) + tests | 24 tests pass; sts.py untested against the live game |
| P0.E1 backup + runbooks + metrics | 00:52 | 00:54 | backups/2026-11-19-pre-phase0 (verified), docs/runbooks/{restore-saves,mod-install,start-run,decision-loop,end-run,game-patch}.md, metrics/{scoreboard.csv,milestones.md,exam-seeds.md} | Extra work pulled forward from Phases 0 and 4; all of it needs no game launch |
| I: Co-op rules | 00:54 | 00:56 | knowledge/coop-rules.md | Two sources agree on most rules; key open question: do enemy attacks hit every player? |
| X1: Boss arrival HP | 00:56 | 00:58 | tools/analyze_boss_arrival.py → reports/phase2/boss-arrival-hp.md; playbook v2.1 (§5, H1) | Steep arrival curve but heal vs smith outcomes equal at the same HP: mixed evidence, rule kept moderate (Act 3: rest under 70%) |
| X2: Deck strength | 00:58 | 01:00 | tools/deck_metrics.py → reports/phase2/deck-strength.md; playbook v2.2 (§2.1 corner targets, H9) | Raw damage does not predict boss survival (higher raw damage → more deaths); block and scaling do |
| X3: Phase 3 tools | 01:00 | 01:01 | tools/stsstate.py, watch.py, record.py, reconstruct.py + tests (29 total pass) | Untested live; STS2MCP format |
| X4: macOS teammate patch proposal | 01:01 | 01:02 | docs/proposals/sts2-agent-macos-teammate.md | Three code changes plus a test plan; not applied |
| X5: Relics, potions, events | 01:02 | 01:03 | tools/build_misc_reference.py → knowledge/{events,relics,potions}.md | 68 events with option risk tags and the Player choices; 289 relics with pick/buy counts and final-relic win rates; 64 potions |
| X6: Necrobinder v0 | 01:02 | 01:04 | playbooks/necrobinder.md v0 | Groundwork only: mechanics from the extract, the Player data, boss priorities, open questions |
| X7: Band benchmarks | 01:04 | 01:05 | tools/build_band_benchmarks.py → data/benchmarks/{ironclad,allchars}-encounters-by-band-v0.107.1.csv; postmortem.py picks band-matched benchmarks; M4 redefined per band | The pooled benchmark is mostly A7–A10 and would make low-ascension comparisons meaningless |
| X8: Elite deck metrics | 01:05 | 01:06 | deck-strength report: elite section; playbook §2.1 Act 1 timing rule | Act 1 elites reward raw damage (high tercile 3/62 fatal); bosses reward block and scaling |
| X9: Room values | 01:06 | 01:07 | tools/analyze_room_values.py → reports/phase2/room-values.md; playbook §4 room economics and path heuristics | ? rooms cost ~1% HP for 0.5+ cards and 0.2–0.4 relics; elites ~25% HP for ~0.9 relic |
| X10: Practice post-mortems | 01:07 | 01:09 | runs/examples/player-1791247295-vantom/, runs/examples/player-1791336980-knowledge-demon/ (facts + postmortem); playbook v2.3 | Both deaths would likely have been avoided by v2.3 rules; both died with HP = A10 band boss median |
