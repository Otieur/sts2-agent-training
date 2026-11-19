# Overnight Report (2026-11-19)

> **Draft written at 02:35 EST, updated at 03:15** as insurance against an interruption. Block K (from 09:52) updates every section; until then the full record is `docs/overnight-log.md`.

Session: 00:22–10:22 EST, autonomous, following `prompts/overnight-2026-11-19.md`. No game launch, no mod build, no installs, no messages, no pushes.

## 1. Summary
1. **The main branch moved to v0.111.1 on 2026-11-16**, and the decompiled game data turned out to predate even v0.107.1. Both version gaps are now documented (`knowledge/version-delta-*.md`) and patched into the tools (`knowledge/data/card-patches.json`).
2. **The full offline toolchain for Phase 4 exists and is tested**: one entry point (`tools/advise.py`) routes each screen to a turn planner (with potions, Powers, Osty, a survival guard and ready-to-run commands), path planner, draft scorer, deck check, card-selection, rest, event and shop advice, for either mod (STS2MCP states are converted). 108 tests pass; nothing has touched the live game yet.
3. **The playbook's rules were checked against the Player's history at the decision point**: community card tiers predict the Player's Ironclad outcomes (A-tier picks +17 points of act survival, C/D −13 to −16); the pre-boss rest rule and corner targets flag more fatal than survived boss fights; Breakthrough and Hefty Tablet stand out as costly picks.
4. **A fight simulator now tests rules before play**: against Vantom, multi-hit attacks and Demon Form are the best additions and Breakthrough is worse than a plain Strike; at Knowledge Demon, Sloth is the best curse; the balanced turn plan beats the safe one in boss fights. Models that failed calibration against the Player's record (Ceremonial Beast, Entomancer) are excluded. **Boss and elite plans gained mechanics found in the game data**: Kaiser Crab's Crab Rage and back attacks, Lagavulin Matriarch waking stunned, the Kin followers being Minions, Knowledge Demon's curse choices (Sloth is usually the cheapest), Infested Prism's rework.
5. **Nothing needs undoing, but several things need you** (section 5): the security verdict, the Steam branch switch, the .NET 9 SDK, then a 30-minute first session following `docs/runbooks/first-session.md`.

## 2. Work done (by block)
Planned blocks (A–J) were finished by 01:11; everything after is extra work from the stretch and never-idle lists. Times are EST.

| Block | Main outputs |
|---|---|
| A Scaffolding | The project instructions, templates, git |
| F Mod review prep | `vendor/` clones (read-only), `docs/reviews/sts2-agent-security-review.md` (draft), `docs/api-notes.md`, `docs/environment.md`, `docs/decisions/0001-mod-and-branch.md` |
| B0 Game-data import | `knowledge/data/extract-2026-09-21/`, card references, deck features by encounter |
| B Community strategy | `knowledge/community/` (sources, Ironclad tiers, archetypes, discrepancies) |
| C Mechanics | `knowledge/mechanics.md`, `knowledge/ascension.md` |
| D Boss plans | `knowledge/bosses/` (12 plans) |
| E Elites and encounters | `knowledge/enemies/` (12 elites, 15 hallway fights) |
| J Playbook v2 | `playbooks/ironclad.md` (now v2.10) |
| H Other characters | Phase 1 reports and benchmarks for Necrobinder, Silent, Regent; `playbooks/necrobinder.md` (now v0.3) |
| G Offline tools | `tools/calc.py`, `postmortem.py`, `sts.py` |
| I Co-op rules | `knowledge/coop-rules.md` |
| X1–X13 | Boss arrival HP, deck strength, Phase 3 tools, macOS teammate patch proposal, relics/potions/events references, band benchmarks, room values, practice post-mortems, upgrade table, rule backtests, gaps file |
| X14 | **Main branch is v0.111.1**: `knowledge/version-delta-v0.111.1.md`, decision 0001 revised to STS2-Agent first |
| X15–X16 | `tools/journal.py`; co-op instances and party view in `tools/sts.py` |
| X17 | Necrobinder community tiers; tier builder per character; quintile bucket fix |
| X18 | Playbook consistency pass; `tools/check_playbook.py` (now 51 checks) |
| X19 | Necrobinder, Silent, Regent changes on v0.111.1 |
| X20–X21 | `tools/draft.py`, `tools/plan_turn.py` |
| X22–X23 | **Extract predates v0.107.1**: `knowledge/version-delta-extract-to-v0.107.1.md`, card patches, enemy notes updated |
| X24–X26 | Kaiser Crab, Knowledge Demon, Test Subject, Lagavulin, Kin mechanics from the power data |
| X27–X31 | `tools/path.py`, `tools/advise.py`, potions in the planner, `tools/deck_check.py`, `tools/smoke.py`, `docs/runbooks/first-session.md` |
| X32–X35 | Playbook coherence pass; Ancient relic analysis (H10); card choices at the decision point; co-op rules for v0.111.1 |
| X36–X39 | Integration test; `tools/fight_model.py`; draft backtest; H1 backtest |
| X40–X52 | `playbooks/coop.md` v0; power-data gap closures (Slow, Colossus); Slow and Osty in the planner; `tools/README.md`; reproducibility check; death review; re-tuned boss checklists; data-backed boss fit; A7 check; event choices; Osty damage in deck metrics |
| X53–X58 | Draft report; Power value and potion cost in the planner; executable combat commands; fight type from enemy IDs; status board refresh |
| X59–X62 | Card-selection advice; shadowing tools read STS2-Agent; `tools/mcp_adapter.py` (every helper works with STS2MCP); smoke test for STS2MCP |
| X63–X69 | `tools/simulate_fight.py` (Vantom, Lagavulin, Ceremonial Beast, Knowledge Demon, Entomancer) with calibration; Vantom simulation in drafting; survival guard; balanced plan for bosses; tool-pick logging; Personal Hive cost |

## 3. Stories whose status changed
- P0: E8 done; E1 backup done; E5.S1 in progress (smoke test ready).
- P2: knowledge base stories largely done (see `docs/STATUS.md`); E4.S4 discrepancies updated.
- P4: E1.S1–S4, S6 done (runbooks); E2.S1, S3, S4 done; E3.S1–S4 done (tooling); E4.S1 done; E5.S1, S3 done; E6.S1 done.
- P0: E5 and E6 in progress (smoke test for both mods; sts.py).
- P5: E2.S1 done; E2.S2 and E2.S3 in progress.
- P6: E1.S1 done; E2.S2, E3.S1, E3.S2, E4.S2, E5.S3 in progress.

## 4. Decisions taken without you
Nine, each with its reason and how to reverse it: `docs/overnight-decisions.md`. The ones that matter most: the target version is now v0.111.1 (6); decision record 0001 now proposes STS2-Agent first (6, proposal only); the extract's version was corrected (8).

## 5. Needs the Player
1. **Approve or reject the security review verdict** (`docs/reviews/sts2-agent-security-review.md`).
2. **Switch Steam to the main branch** (now v0.111.1, released 2026-11-16).
3. **Decide the mod**: approve a .NET 9 SDK install for STS2-Agent (recommended, `docs/decisions/0001-mod-and-branch.md`) or try STS2MCP first (no install, but last fixed for v0.107).
4. **Check the Steam Cloud setting** for the game (backup safety).
5. **Approve the permissions allowlist** if you want fewer prompts during play.
6. **Run the first session** (`docs/runbooks/first-session.md`, about 30 minutes): smoke test, one API action, arithmetic checks. The exam seeds are 10 characters; v0.111.1 seeds are 12, so check one.

## 6. Problems and failures
- **Version facts changed twice tonight.** At 01:12 the main branch turned out to be v0.111.1, not v0.107.1. At 01:42 the extract turned out to predate v0.107.1, which corrected an earlier conclusion from the same night (decision 8). Every affected file now says which version its numbers are from.
- **Nothing is tested live.** All tools follow the mods' documentation; field names and the arithmetic assumptions (gaps 22–24) need the first session.
- **Several sources were unreachable** (untapped.gg, BrokenBuilds, Mobalytics returned 403); MetaBot's relic list was rejected as biased.
- **Evidence is observational.** Every outcome comparison in the history is confounded by the Player's own choices; they are labelled `[PLAYER-DATA, weak]` or `observational`. The re-tuned boss checklists were measured on overlapping data.
- **Two simulator models failed calibration** (Ceremonial Beast, Entomancer): their move cycles from the extract cannot be right as read; both are excluded and logged as gaps 25 and 26.
- **Mistakes caught and fixed during the night:** guessed log times (fixed with `date`), a quintile bucketing bug in the tier builder, "about 29%" rest heal (it is 30% rounded down), a mislabelled check in the death review, non-deterministic tie order in one report, a wrong claim about the Player's Drum of Battle picks, a potion cost that spent a Fire Potion on a hallway fight, an over-strong reading of the first Vantom simulation, and an edit that briefly dropped the simulation report's calibration section (restored before commit).

## 7. Suggested next steps
1. The five Player steps above, then the first session.
2. Phase 2 live data export (`/data` on STS2-Agent) to replace the extract with v0.111.1 game data.
3. First practice runs at A0 with `tools/advise.py` in the loop; log tool recommendations against final choices.
4. Revisit H1, H9, H10 and the draft weights after 10 runs.

## 8. Time log
See `docs/overnight-log.md` (one row per block, start and end times from `date`).
