# Overnight Report (2026-11-19)

> **Draft, updated at 05:30 EST.** Block K (from 09:52) finishes every section; until then the full record is `docs/overnight-log.md`.

Session: 00:22–10:22 EST, autonomous, following `prompts/overnight-2026-11-19.md`. No game launch, no mod build, no installs, no messages, no pushes. Local git only.

## 1. Summary
1. **Version facts were corrected twice.** The main branch moved to v0.111.1 on 2026-11-16, and the decompiled game data turned out to predate even v0.107.1. Both gaps are documented (`knowledge/version-delta-*.md`) and patched into the tools (`knowledge/data/card-patches.json`); where the game data leaves out a card's condition, the planner now follows community-confirmed text.
2. **The offline toolchain for Phase 4 is complete and tested, but untested live.** `tools/advise.py` routes each screen to the turn planner, path planner, draft scorer, deck check and screen-specific advice, for either mod. The turn planner now handles the mechanics that would have lost fights silently (for example, every playable Status used to be treated as unplayable, so the Agent would never have played Frantic Escape and would have died to The Insatiable's Sandpit). The advisor no longer crashes on damaged states. 133 tests pass.
3. **The playbook's rules were checked against the Player's history at the decision point**: community card tiers predict the Player's Ironclad outcomes (A-tier picks +17 points of act survival), the pre-boss rest rule and corner targets flag more fatal than survived boss fights, and Breakthrough and Hefty Tablet stand out as costly picks.
4. **A fight simulator tests rules before play, and says honestly where it cannot.** Boss-specific plan choice matters: the balanced plan wins against Vantom, Lagavulin Matriarch and Byrdonis, the safe plan against Waterfall Giant and Soul Fysh. The Knowledge Demon curse rule was rebuilt around the real offers (Mind Rot, then Sloth, then Waste Away; never stack Disintegration). With the Player's own decks the simulator's absolute win rates are near zero (no relics, upgrades or many card effects), so it is used only to compare options; models that fail calibration are kept out of drafting, with sensitivity checks that say what to read in the first fight.
5. **Nothing needs undoing; several steps need you** (section 5): the security verdict, the Steam branch switch, the .NET 9 SDK decision, then a 30-minute first session following `docs/runbooks/first-session.md`.

## 2. Work done (by block)
Planned blocks (A–J) were finished by 01:11; everything after is extra work from the stretch and never-idle lists. Times are EST; per-row times are in the log.

| Block | Main outputs |
|---|---|
| A Scaffolding | The project instructions, templates, git |
| F Mod review prep | `vendor/` clones (read-only), `docs/reviews/sts2-agent-security-review.md` (draft), `docs/api-notes.md`, `docs/environment.md`, `docs/decisions/0001-mod-and-branch.md` |
| B0 Game-data import | `knowledge/data/extract-2026-09-21/`, card references, deck features by encounter |
| B Community strategy | `knowledge/community/` (sources, Ironclad tiers, archetypes, discrepancies) |
| C Mechanics | `knowledge/mechanics.md`, `knowledge/ascension.md` |
| D Boss plans | `knowledge/bosses/` (12 plans) |
| E Elites and encounters | `knowledge/enemies/` (12 elites, 15 hallway fights) |
| J Playbook v2 | `playbooks/ironclad.md` (now v2.15), `playbooks/ironclad-quickref.md` |
| H Other characters | Phase 1 reports and benchmarks for Necrobinder, Silent, Regent; `playbooks/necrobinder.md` (v0.3) |
| G Offline tools | `tools/calc.py`, `postmortem.py`, `sts.py` |
| I Co-op rules | `knowledge/coop-rules.md` |
| X1–X13 | Boss arrival HP, deck strength, Phase 3 tools, macOS teammate patch proposal, relics/potions/events references, band benchmarks, room values, practice post-mortems, upgrade table, rule backtests, gaps file |
| X14 | **Main branch is v0.111.1**: `knowledge/version-delta-v0.111.1.md`, decision 0001 revised to STS2-Agent first |
| X15–X21 | `tools/journal.py`; co-op instances in `tools/sts.py`; Necrobinder tiers; playbook consistency checker; `tools/draft.py`, `tools/plan_turn.py` |
| X22–X26 | **Extract predates v0.107.1**; card patches; Kaiser Crab, Knowledge Demon, Test Subject, Lagavulin, Kin mechanics from the power data |
| X27–X39 | `tools/path.py`, `tools/advise.py`, potions in the planner, `tools/deck_check.py`, `tools/smoke.py`, first-session runbook, Ancient and card-choice analyses, integration test, fight model, draft and H1 backtests |
| X40–X62 | `playbooks/coop.md` v0; death review; re-tuned boss checklists; event choices; card-selection advice; `tools/mcp_adapter.py` (every helper works with STS2MCP) |
| X63–X69 | `tools/simulate_fight.py` with calibration; simulation in drafting; survival guard; tool-pick logging |
| X70–X77 | `tools/shadow.py`; path planner from minutes to under 1 s per map; H11 hallway rule; quick reference; **two bugs found in the mod's source**: `act_id` is 0-based and intents already include Weak |
| X78–X86 | Exact action names; STS2-Agent support in journal and wait; Byrdonis model; 40% rest rule; `tools/replay_run.py` (agent replays of two example deaths); Ceremonial Beast fix; start-run runbook for STS2-Agent |
| X87 | **Soul Fysh and Waterfall Giant models** (safe plan for both); real-deck calibration; **Knowledge Demon curse offers**; Slippery credit; **turn planner card and power coverage** (playable Statuses and Sandpit, Toxic, Mangle, Flame Barrier, Body Slam, Fiend Fire, Dismantle, Setup Strike, Rage, Unrelenting, Feel No Pain, Wither; Sloth, Ringing, Disintegration, Enrage, Hardened Shell, Thorns, Artifact, Hard to Kill, Shriek, Crab Rage; an Attack's own Strength after its hits) |
| X88 | Six more potions in the planner (Potion-Shaped Rock, Blood Potion and others); planner fuzz |
| X89–X90 | **Advisor robustness**: damaged-state fuzz found about 150 crashes in 800; `advise()` never raises now; fuzz test |
| X91–X92 | Sensitivity checks for the failing models: Ceremonial Beast (gap 25), Entomancer (gap 26), Knowledge Demon |
| X93 | Live-safety pass on the planner: commands stop after a card that changes the hand (True Grit's random exhaust), Minion semantics (killing The Kin's Priest or the Queen counts as lethal), Tender; notes for the four rare-but-deadly hallway fights (Slumbering Beetle killed 2 of 5 Ironclad runs that met it; in all four the fatal fights started at low HP, H11); quick reference and decision-loop runbook updated |
| X94–X97 | Colossus; Necrobinder card audit (Unleash read as 0 offline, now Osty 6 + his HP; Invoke's next-turn energy no longer counted this turn); smoke test now catches advisor failures; Doom on enemies and on you in the planner; the full dataset rebuild reproduces every report unchanged; plan choice against the uncalibrated bosses is mostly level |

## 3. Stories whose status changed
- P0: E8 done; E1 backup done; E5.S1 in progress (smoke test ready); E5 and E6 in progress (smoke test for both mods; sts.py).
- P2: knowledge base stories largely done (see `docs/STATUS.md`); E4.S4 discrepancies updated; boss plans gained simulation sections.
- P4: E1.S1–S4, S6 done (runbooks); E2.S1, S3, S4 done; E3.S1–S4 done (tooling); E4.S1 done; E5.S1, S3 done; E6.S1 done.
- P5: E2.S1 done; E2.S2 and E2.S3 in progress.
- P6: E1.S1 done; E2.S2, E3.S1, E3.S2, E4.S2, E5.S3 in progress.

## 4. Decisions taken without you
Fourteen, each with its reason and how to reverse it: `docs/overnight-decisions.md`. The ones that matter most: the target version is now v0.111.1 (6); decision record 0001 now proposes STS2-Agent first (6, proposal only); the extract's version was corrected (8); the Knowledge Demon curse rule was replaced (12); the planner's status and power handling (13, 14).

## 5. Needs the Player
- [ ] **Approve or reject the security review verdict** (`docs/reviews/sts2-agent-security-review.md`).
- [ ] **Switch Steam to the main branch** (now v0.111.1; you are on the public beta, v0.113.1). A save backup was taken first (`backups/2026-11-19-pre-phase0/`).
- [ ] **Decide the mod**: approve a .NET 9 SDK install for STS2-Agent (recommended, `docs/decisions/0001-mod-and-branch.md`) or try STS2MCP first (no install, last fixed for v0.107).
- [ ] **Check the Steam Cloud setting** for the game (backup safety).
- [ ] **Approve the permissions allowlist** if you want fewer prompts during play.
- [ ] **Run the first session** (`docs/runbooks/first-session.md`, about 30 minutes): smoke test, one API action, arithmetic checks, and the mechanics list to confirm when met (gaps 4–28).
- [ ] **Exam seeds**: STS2-Agent cannot type a seed, so seeded runs need you to enter the seed in the game; the v0.107.1 exam seeds are 10 characters and v0.111.1 seeds are 12, so check one.

## 6. Problems and failures
- **Nothing is tested live.** All tools follow the mods' documentation; field names and arithmetic assumptions need the first session.
- **The simulator is pessimistic for real decks.** Replaying the Player's own decks gives near-zero simulated win rates for every boss (no relics, upgrades, potions or many card effects), so its numbers are for comparing options on one deck only. Three models fail calibration and are kept out of drafting: Ceremonial Beast, Entomancer, Waterfall Giant (and Knowledge Demon is not validated). The sensitivity checks name the assumption to read first in each first fight.
- **Bugs that would have hurt live play, found offline and fixed with tests:** `act_id` is 0-based (tools read Act 1 as "act 0"); intents already include Weak; every playable Status was unplayable in the planner (fatal against The Insatiable); an Attack's own Strength gain was applied to its own hits (Fight Me overstated); the advisor crashed on damaged states; the path planner took minutes per map.
- **Mistakes of mine caught and corrected during the night:** guessed times in two status messages (05:00 and 05:40 were not from `date`; logged); "fixing" Forgotten Ritual's exhaust condition before checking that v0.111.1 removed it (caught within minutes); a 0-cost status check that read cost 0 as missing; Feel No Pain block counted twice in the simulator; the Waterfall Giant first modelled with a partial cycle; earlier ones (quintile bucketing, rest heal percentage, Drum of Battle claim, an over-strong first Vantom reading) are in the log.
- **Several sources were unreachable** (BrokenBuilds, Mobalytics, SlashSkill returned 403); some guides disagree (The Insatiable's cycle), and those conflicts are recorded rather than resolved.
- **Evidence is observational.** Outcome comparisons from the history are confounded by the Player's own choices and labelled `[PLAYER-DATA, weak]`.

## 7. Suggested next steps
1. The Player steps above, then the first session.
2. Phase 2 live data export (`/data` on STS2-Agent) to replace the extract with v0.111.1 game data, then re-run `tools/check_playbook.py` and the simulator report.
3. First practice runs at A0 with `tools/advise.py` in the loop; log tool picks against final choices (`--tool-pick`).
4. In the first fights against Ceremonial Beast, Entomancer, Soul Fysh, Waterfall Giant, Knowledge Demon and The Insatiable, read the items in gaps 25–28 and update the models.
5. Revisit H1, H9, H10 and the draft weights after 10 runs.

## 8. Time log
See `docs/overnight-log.md` (one row per block, start and end times from `date`).
