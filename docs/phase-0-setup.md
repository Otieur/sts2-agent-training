# Phase 0: Setup and Mod Integration

**Goal:** a safe, reproducible environment where the Agent can read the live game state and send actions. The game runs on the main branch, with a reviewed mod built from source.

**Depends on:** nothing.
**Unblocks:** Phases 2, 3, 4 and 6. Phase 1 does not need this phase.

---

## 1. What to expect

| | |
|---|---|
| **Duration** | 1–2 evenings of Agent work. Most of the elapsed time goes to downloads, builds and game restarts. |
| **Player time** | About 45 minutes: switch the Steam branch, launch and quit the game a few times, accept the mod consent dialog, approve the security review verdict, approve tool permissions. |
| **Best case** | The mod builds on the first try, loads on v0.111.1, and the Agent plays a full fight through the API in the first evening. |
| **Likely case** | One or two snags: the build cannot find the game's assemblies inside the macOS app bundle, the mods folder location needs to be discovered from the logs, or the API port differs from the documented default. Each is a 15–60 minute fix. |
| **Worst case** | The mod does not compile against v0.111.1, or loads but crashes. Then E7 applies: patch the mod, switch to the fallback mod, or run the game on whichever branch the mod supports. Expect an extra evening. |
| **What the Player will notice** | With mods enabled, the game uses a separate modded profile (`modded/profile1`). Runs played with mods on do not mix with the main profile. A copy of the main profile already exists there. |

---

## 2. Roles

| Step | Player | Agent |
|---|---|---|
| Back up saves | Closes the game | Copies the files, writes checksums, documents the restore |
| Switch branch | Changes the Steam setting | Verifies the version from the logs |
| Mod review | Approves or rejects the verdict | Reads the source, writes the review |
| Build and install | — | Builds, installs, writes the uninstall steps |
| Enable mods | Accepts the consent dialog, restarts the game | Verifies the API responds |
| The agent harness wiring | Approves permissions | Writes the CLI wrapper, MCP config, project files |

---

## 3. Epics and stories

### P0.E1: Save safety

> **P0.E1.S1: Back up the full save folder** · Size S · Status: Done (2026-11-19 00:53, backups/2026-11-19-pre-phase0/, 1,104 files verified)
> *As the Player, I want a complete, verified copy of my saves before anything changes, so that a bad branch switch or a mod bug cannot cost me progress.*
>
> **Acceptance criteria**
> - [ ] The game is not running during the copy (`pgrep -fl "Slay the Spire 2"` returns nothing).
> - [ ] `~/Library/Application Support/SlayTheSpire2/` is copied to `backups/<YYYY-MM-DD>-pre-phase0/SlayTheSpire2/` with `rsync -a`. Shader and Vulkan caches may be excluded.
> - [ ] `backups/<...>/MANIFEST.sha256` lists a SHA-256 for every copied file.
> - [ ] The file count and total size of the copy match the source.
>
> **Notes:** the folder holds the main profile, the modded profile, a backup profile, settings and 233 unique run histories. `backups/` stays out of version control.

> **P0.E1.S2: Write and dry-run the restore procedure** · Size S · Status: Done (docs/runbooks/restore-saves.md; dry run showed no differences)
> *As the Player, I want a tested restore procedure, so that I can roll back without the Agent's help if needed.*
>
> **Acceptance criteria**
> - [ ] `docs/runbooks/restore-saves.md` gives the exact commands to restore, including closing the game first.
> - [ ] A dry run (`rsync -an --delete <backup>/ <live>/`) right after the backup shows no differences.
> - [ ] The runbook says how to check that the restore worked: the game launches and the profile shows the expected unlocks.

> **P0.E1.S3: Account for Steam Cloud** · Size XS · Status: Done (2026-11-19)
> *As the Player, I want to know whether Steam Cloud syncs my saves, so that a restore is not silently overwritten by an older cloud copy.*
>
> **Acceptance criteria**
> - [x] The Player checks Steam → Slay the Spire 2 → Properties → General → Steam Cloud and reports the setting. **Steam Cloud is on** (the Player, 2026-11-19; the library page shows Cloud status "Up to date").
> - [x] The restore runbook says how to handle a Steam Cloud conflict dialog: choose the local files after a restore.

---

### P0.E2: Game version

> **P0.E2.S1: Switch to the main branch** · Size XS · Player-only · Status: Done (2026-11-19)
> *As the Player, I want the game on the main branch (v0.111.1 since 2026-11-16), the closest supported version to my 227 runs on v0.107.1 and the version STS2-Agent was validated on.*
>
> **Acceptance criteria**
> - [x] Steam → Library → Slay the Spire 2 → Properties → Betas (or "Game Versions & Betas") → set to none or the default.
> - [x] Steam finishes the download, which appears as an update. Checked 11:44: the app manifest shows branch `public`, build 26655341, download complete; the app's `release_info.json` reads v0.111.1 (commit cc1f9462, built 2026-11-13). The save folder was unchanged by the switch (rsync dry run against the overnight backup: no differences).
>
> **Expect:** the Fool and the v0.113.x content disappear until the Player opts back into the beta.

> **P0.E2.S2: Verify the version and save compatibility** · Size XS · Status: Done (2026-11-19 12:07 launch)
> *As the Agent, I want to confirm the running version from the game's own logs, so that every later note is tagged with the right version.*
>
> **Acceptance criteria**
> - [x] After one launch, the newest `~/Library/Application Support/SlayTheSpire2/logs/godot*.log` contains `release=v0.111.1`. (Before launch, `release_info.json` in the app already reads v0.111.1.)
> - [x] The "Current save versions" log line is recorded in `docs/environment.md`.
> - [x] The log shows no save-load errors. Only non-fatal "Progress parse" warnings for beta-only IDs (the Fool, its cards, some relics, potions, epochs and one encounter), which v0.111.1 does not know.

> **P0.E2.S3: First-launch profile check** · Size XS · Status: Done (2026-11-19: the main menu loads on the modded profile; the Player confirms everything is unlocked)
> *As the Player, I want to confirm my profile survived the downgrade, so that we stop early if it did not.*
>
> **Acceptance criteria**
> - [x] The main menu loads. Character select shows the unlocked characters, and the ascension levels look as expected. (Confirmed by the Player.)
> - [ ] If the profile looks reset or the game reports an error: stop, restore from P0.E1.S1, opt back into the beta, and record the finding in `docs/environment.md`.
>
> **Notes:** the beta wrote `SerializableProgress v24`. Older builds may not read newer save schemas. This is the main reason for the backup.

> **P0.E2.S4: Record the environment** · Size XS · Status: In progress (drafted overnight; game version to confirm)
> *As the Next Session, I want a single file describing the environment, so that I do not re-discover paths and versions.*
>
> **Acceptance criteria**
> - [ ] `docs/environment.md` records the macOS version, game version and Steam build ID, branch, game install path, save path pattern (with the Steam ID replaced by `<id>`), mods folder, `dotnet --version`, Python version, `uv --version`, mod name, mod commit and API port.

---

### P0.E3: Mod acquisition and security review

> **P0.E3.S1: Clone the mod source at a pinned commit** · Size XS · Status: Done (2026-11-19: both repos cloned to vendor/, SHAs in docs/environment.md)
> *As the Agent, I want the mod source at a known commit, so that the review, the build and any later patches refer to the same code.*
>
> **Acceptance criteria**
> - [ ] `git clone https://github.com/Meddrin/STS2-Agent vendor/STS2-Agent`
> - [ ] The commit SHA is recorded in `docs/environment.md`.
> - [ ] The fallback `https://github.com/Gennadiyev/STS2MCP` is cloned to `vendor/STS2MCP` for E7, but not reviewed unless needed.

> **P0.E3.S2: Security review** · Size M · Status: Done (STS2-Agent verdict approved by the Player 2026-11-19)
> *As the Player, I want the mod's code read before it runs inside my game, so that I know what it can do on my machine.*
>
> **Acceptance criteria:** `docs/reviews/sts2-agent-security-review.md` covers each item below with file and line references.
> - [ ] **Network listeners:** every HTTP or socket listener and its bind address. Expected: loopback only (`127.0.0.1`). Anything else is a blocker.
> - [ ] **Outbound network calls:** every HTTP client, its destinations, and when it fires. Expected: only the optional LLM autoplay client, active only when a model is configured. The Agent does not configure one.
> - [ ] **Process launching:** every `Process.Start` or equivalent, with its arguments. Expected: the second game instance for the AI teammate, with `--force-steam off`.
> - [ ] **File writes:** every path the mod writes to. Expected: its own config, logs and the companion settings clone.
> - [ ] **Game patches:** the list of Harmony patches and the game methods they touch, flagging any that affect saving or loading.
> - [ ] **Debug and console features:** confirm `run_console_command` is gated behind `STS2_ENABLE_DEBUG_ACTIONS=1`.
> - [ ] **Telemetry or analytics:** present or absent.
> - [ ] **Verdict:** Go, Go with conditions, or No-Go, with reasons.
> - [x] The Player reads the verdict and approves it in chat before P0.E4.S3. (2026-11-19, STS2-Agent)

> **P0.E3.S3: License note** · Size XS · Status: Done (licenses noted in the review)
> *As the Player, I want to know the license obligations, so that local patches stay compliant.*
>
> **Acceptance criteria**
> - [ ] The review notes that the mod is AGPL-3.0. Private use and local modification are fine. Patched builds are not distributed from this project.

---

### P0.E4: Build and install

> **P0.E4.S1: Prepare the toolchain** · Size S · Status: Done (2026-11-19: .NET 9.0.124 from Homebrew `dotnet@9`, keg-only, installed with the Player's approval)
> *As the Agent, I want the exact .NET SDK and game assembly references the project expects, so that the build is reproducible.*
>
> **Acceptance criteria**
> - [x] The SDK version in `vendor/STS2-Agent/global.json` is compared with `dotnet --list-sdks`. If it is missing, the Agent asks the Player before installing it (for example `brew install --cask dotnet-sdk` or a versioned cask).
> - [x] The Agent finds how the project references game assemblies (`.csproj` properties or environment variables) and where those assemblies live in the macOS bundle (`find "<install>/SlayTheSpire2.app" -name "*.dll"`).
> - [x] The reference path is set through a local, untracked override file or environment variable, not by editing tracked project files where avoidable. (Passed as `/p:Sts2DataDir=...` on the command line.)

> **P0.E4.S2: Build from source** · Size S–M · Status: Done (2026-11-19, DLL only; see the note in `docs/runbooks/mod-install.md`)
> *As the Player, I want the mod built from reviewed source rather than downloaded as a binary, so that what runs is what was reviewed.*
>
> **Acceptance criteria**
> - [x] The game is closed. The build completes with zero errors (0 warnings) against the v0.111.1 assemblies. `dotnet build` was run directly instead of `build-mod.sh`, whose PCK step runs the game's own executable headless.
> - [x] The outputs are `STS2AIAgent.dll` and `mod_id.json`. No `STS2AIAgent.pck`: it would only repeat the manifest, and the game's loader reads the manifest from the JSON file and accepts a mod without a PCK (`has_pck: false`, as STS2MCP does).
> - [x] The build log is saved to `logs/build-sts2agent-2026-11-19.txt`.
> - [ ] **If compilation fails** on game API differences: the errors are listed in `docs/api-notes.md`, with an estimate of the patch effort. More than about 2 hours of patching triggers E7.

> **P0.E4.S3: Install into the macOS mods folder** · Size S · Status: Done (installed 2026-11-19 11:56; the game loads mods from `SlayTheSpire2.app/Contents/MacOS/mods/`, log line "Found mod manifest file"; DLL only, no PCK needed)
> *As the Agent, I want the mod installed where the macOS build actually loads mods, so that it runs on launch.*
>
> **Acceptance criteria**
> - [ ] The correct folder is found: the candidates are `SlayTheSpire2.app/Contents/MacOS/mods/` (documented by STS2MCP for macOS) and `~/Library/Application Support/SlayTheSpire2/mods/` (exists, holds `config/`). Confirm from the log lines on the next launch.
> - [x] Only the built files are copied (`STS2AIAgent.dll`, `mod_id.json`).
> - [x] `docs/runbooks/mod-install.md` records the install manifest (paths and checksums), the uninstall steps, and the reinstall steps after a game update.
>
> **Notes:** a Steam update or "Verify integrity of game files" may remove files inside the app bundle. If that happens, rerun the reinstall steps.

> **P0.E4.S4: Enable mods in game** · Size XS · Player-only · Status: Done (2026-11-19)
> *As the Player, I want to enable the mod myself, so that I control what runs in my game.*
>
> **Acceptance criteria**
> - [x] The Player launches the game, accepts the untrusted-code consent dialog, enables the mod in settings, quits fully and relaunches. This follows the mod's README sequence. (Launch at 12:05 without mods, 12:07 with the mod loaded: "RUNNING MODDED! --- Loaded 1 mods".)
> - [x] The game opens on the modded profile (`user://steam/<id>/modded/profile1`).

> **P0.E4.S5: Verify the API** · Size XS · Status: Done (2026-11-19)
> *As the Agent, I want proof the mod is serving requests, so that later stories can rely on it.*
>
> **Acceptance criteria**
> - [x] The port is found (the F8 overlay, the mod config, or the logs). The documented default is 8080, but it is not guaranteed. (8080, from the log and the overlay.)
> - [x] `curl -s http://127.0.0.1:<port>/health` returns JSON with the game version `v0.111.1` and the mod version (0.16.2, status ready, 28 of 28 reflected game members resolved).
> - [x] The Godot log shows no exceptions from the mod during startup.

---

### P0.E5: API smoke test

> **P0.E5.S1: Capture state samples for every screen** · Size M · Status: In progress (tools/smoke.py --save --watch and docs/runbooks/first-session.md ready; needs the live mod)
> *As the Next Session, I want real JSON samples of each screen type, so that parsers and handlers are built against reality, not documentation.*
>
> **Acceptance criteria**
> - [ ] `knowledge/api-samples/` holds one raw `/state` sample for each screen: main menu, character select, map, combat (start of turn, mid-turn), card reward, relic reward, shop, rest site, event, treasure, Ancient, game over. Samples from the `agent_view` compact form are included too.
> - [ ] Each sample is captured during a throwaway Ironclad A0 run on the modded profile.

> **P0.E5.S2: Play one card through the API** · Size S · Status: Done (2026-11-19 13:35 EST)
> *As the Agent, I want to play a card via `/action` with a reason attached, so that the full control loop is proven.*
>
> **Acceptance criteria**
> - [x] `POST /action {"action":"play_card","card_index":N,"target_index":M,"client_context":{"decision_reason":"..."}}` plays the card in game. (Tremble on a Fogmog, A10 floor 8: status completed, energy 3 to 2, the Fogmog shows 3 Vulnerable; logged in `runs/smoke/decisions.jsonl`.)
> - [x] `GET /decisions` contains the entry with the reason. Side finding for gap 22: with the target Vulnerable, a Strike's live `Damage` value stays 6, so live card values do not include the target's Vulnerable (the planner applies it on top).

> **P0.E5.S3: Play one full fight and measure latency** · Size S · Status: In progress (fight won through the API 2026-11-19; precise latency still to time)
> *As the Agent, I want to finish an entire Act 1 hallway fight via the API, so that I know the loop holds across turns and animations.*
>
> **Acceptance criteria**
> - [x] The fight ends in a win with no stuck state. (A10 floor 22 hallway, Bowlbug Rock and Egg, 2 turns, 9 actions; an Act 2 fight rather than Act 1.)
> - [ ] `docs/api-notes.md` records the actions taken, the median and p95 time per action (request to state settled), and any waits needed (`combat.action_readiness`).

> **P0.E5.S4: Probe the event stream** · Size S · Status: Done (2026-11-19)
> *As the Agent, I want to know exactly what `/events/stream` emits when the human plays a card, so that Phase 3 can choose between direct event capture and state-diff reconstruction.*
>
> **Acceptance criteria**
> - [x] A 2-minute capture of `/events/stream` while the Player plays a fight by hand is saved to `knowledge/api-samples/events-human-play.txt`. (4 minutes, two fights.)
> - [x] `docs/api-notes.md` answers: does any event identify the card the human played? (Yes / No / Partial.) **No**: the stream reports action windows, screens, turns and decisions, not cards; plays are reconstructed from state differences.

> **P0.E5.S5: Document error behaviour** · Size S · Status: Todo
> *As the Agent, I want to see each error shape once, so that the run harness handles them correctly.*
>
> **Acceptance criteria**
> - [ ] Triggered and recorded: an invalid card index (`invalid_action` or `invalid_target`), a concurrent action (`409 action_in_flight`), and an action during an animation.
> - [ ] Each shape and the correct response are added to `docs/api-notes.md`.

---

### P0.E6: the agent harness integration

> **P0.E6.S1: CLI wrapper `tools/sts.py`** · Size M · Status: In progress (tools/sts.py written against both mods' docs: STS2-Agent and STS2MCP adapters, co-op instances, party view, safety refusals; 16 offline tests; untested live)
> *As the Agent, I want a small, token-efficient command-line interface to the mod, so that each decision costs as little context as possible.*
>
> **Acceptance criteria**
> - [ ] Python standard library only (`urllib`, `json`, `argparse`).
> - [ ] Subcommands:
>   - `health`
>   - `state` (with `--raw` and `--brief`)
>   - `actions`
>   - `act <action> [key=value ...] --reason "..."`
>   - `wait` (until actionable, with a timeout)
>   - `decisions --last N`
>   - `data <collection>`
>   - `--port`, which defaults to the value in `docs/environment.md`
> - [ ] `state --brief` fits a combat screen into about 30 lines: player HP, block, energy, and powers; the hand with indexes, costs and short text; enemies with HP, block, intents and powers; potions; relic names.
> - [ ] Each subcommand is tested against the live game, with the output shown in `docs/api-notes.md`.

> **P0.E6.S2: MCP connection** · Size S · Status: Todo
> *As the Agent, I want the mod's MCP server available in the agent harness, so that the bundled tools (`decide`, `wait_until_actionable`, game data lookups) can be used where they beat the CLI.*
>
> **Acceptance criteria**
> - [ ] The MCP service is enabled in the overlay (F8 → Connect → Open MCP service), and the URL is copied.
> - [ ] The project's `.mcp.json` has an HTTP server entry for it, and `get_game_state` works from a fresh session.
> - [ ] Decision record `docs/decisions/0002-primary-interface.md` chooses the CLI, MCP or a mix as the primary interface. Criteria: tokens per decision, reliability, ease of logging.

> **P0.E6.S3: Review and adopt the gameplay skill** · Size S · Status: Todo
> *As the Next Session, I want the mod's `sts2-mcp-player` skill available, so that I follow the tested decision loop and error rules.*
>
> **Acceptance criteria**
> - [ ] `vendor/STS2-Agent/skills/sts2-mcp-player/SKILL.md` is read in full.
> - [ ] It is copied to the agent's skills folder, with a local section pointing to `playbooks/` and the protocols in Phase 4.

> **P0.E6.S4: Permissions for long runs** · Size XS · Player approval · Status: Todo
> *As the Player, I want routine game commands pre-approved, so that a 2-hour run does not stall on a permission prompt while I am away.*
>
> **Acceptance criteria**
> - [ ] The project's agent settings file allows `python3 tools/sts.py *`, `python3 tools/*.py *` and `curl -s http://127.0.0.1:*`. The Player approves the change.

> **P0.E6.S5: Keep the game reachable during long runs** · Size XS · Status: Todo
> *As the Agent, I want the Mac awake and the game unpaused during runs, so that actions do not time out.*
>
> **Acceptance criteria**
> - [ ] It is known whether the game pauses or throttles when unfocused, tested by sending an action while another app is in front.
> - [ ] The run procedure in Phase 4 includes requesting keep-awake.

---

### P0.E7: Fallback path (only if E4 or E5 fails)

> **P0.E7.S1: Try STS2MCP** · Size M · Status: Todo
> *As the Agent, I want a second mod option ready, so that one broken mod does not block the project.*
>
> **Acceptance criteria**
> - [ ] The same review checklist as P0.E3.S2 is applied, and the Player approves it.
> - [ ] Built with `dotnet build`. `STS2_MCP.dll` and `STS2_MCP.json` are installed in `SlayTheSpire2.app/Contents/MacOS/mods/`.
> - [ ] `curl -s http://localhost:15526/` responds. The smoke tests in E5 pass.

> **P0.E7.S2: Try another branch** · Size S · Status: Todo
> *As the Player, I want to know whether the primary mod works on the beta branch instead, so that we can pick the branch to fit the mod.*
>
> **Acceptance criteria**
> - [ ] With the Player's agreement, switch to the beta, rebuild and run the smoke tests. Record the result.

> **P0.E7.S3: Decision record** · Size XS · Status: In progress (decision record 0001 proposed)
> *As the Next Session, I want to know which mod and branch were chosen and why.*
>
> **Acceptance criteria**
> - [ ] `docs/decisions/0001-mod-and-branch.md` covers the context, the options tried, the results, the decision and its consequences.

---

### P0.E8: Project scaffolding

> **P0.E8.S1: Folder structure** · Size XS · Status: Done
> *As the Next Session, I want a predictable layout, so that I know where everything lives.*
>
> **Acceptance criteria:** the following exist.
> ```
> TRAINING_PLAN.md
> docs/  (phase docs, runbooks/, reviews/, decisions/, environment.md, api-notes.md)
> data/  (raw/, tables, benchmarks/)
> knowledge/  (data/, cards/, enemies/, bosses/, api-samples/)
> playbooks/  runs/  metrics/  reports/  templates/  tools/  vendor/  backups/  logs/
> ```

> **P0.E8.S2: Project instructions** · Size S · Status: Done
> *As the Next Session, I want standing instructions loaded automatically, so that I follow the same rules every time.*
>
> **Acceptance criteria:** The project instructions contain:
> - [ ] The session start procedure from `docs/README.md`.
> - [ ] Hard rules:
>   - Never use the game's Load button for a co-op save.
>   - Every action carries a decision reason.
>   - Update the run journal every floor.
>   - Label all knowledge with its provenance.
>   - Personal details stay out of files.
> - [ ] Pointers to `docs/STATUS.md`, `docs/environment.md`, `playbooks/` and `tools/sts.py`.

> **P0.E8.S3: Version control** · Size XS · Status: Done
> *As the Player, I want playbook history in git, so that a bad change can be found and reverted.*
>
> **Acceptance criteria**
> - [ ] `git init`.
> - [ ] `.gitignore` covers `backups/`, `vendor/`, `logs/`, `data/raw/` and large state captures.
> - [ ] A first commit with the docs and scaffolding.

> **P0.E8.S4: Templates** · Size S · Status: Done
> *As the Agent, I want templates for recurring documents, so that every run, note and decision has the same shape.*
>
> **Acceptance criteria**
> - [ ] `templates/` holds `run-journal.md`, `postmortem.md`, `playbook.md`, `enemy-note.md`, `boss-plan.md` and `decision-record.md`, matching the formats specified in Phases 1, 2 and 4.

---

## 4. Exit gate

Phase 0 is done when all of these hold, and the Player has confirmed in chat:

- [ ] E1 complete (backup verified, restore documented)
- [ ] E2 complete (v0.111.1 confirmed, profile intact) **or** a decision record choosing another branch
- [ ] E3.S2 verdict approved by the Player
- [ ] E4 complete (mod built from source, installed, `/health` OK)
- [ ] E5.S1–S3 complete (samples captured, one full fight played via the API)
- [ ] E6.S1 or E6.S2 complete (a working interface from the agent harness)
- [ ] E8 complete

E5.S4 (event stream probe) and E5.S5 (error shapes) may finish early in Phase 3 if needed.

---

## 5. Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| Build cannot find game types | Assembly reference path not set for the macOS bundle | Find the DLLs inside the `.app` (P0.E4.S1) and set the override |
| Compile errors in game API calls | The mod targets a newer game build (docs mention v0.111.0) | List the errors and patch if small; otherwise E7 |
| Game starts, `/health` refuses the connection | Mod not loaded (wrong folder), mods disabled, or a different port | Check the Godot log for mod loading lines; check F8 for the port |
| Game shows the consent dialog every launch | Mods not saved as enabled | The Player enables them in settings and relaunches fully |
| Profile looks reset after the branch switch | Save schema mismatch | Stop, restore the backup, decide on another branch (E7.S2) |
| Mod files gone after a Steam update | Steam replaced the app bundle | Reinstall from `docs/runbooks/mod-install.md` |
| Actions time out while the game is in the background | Game throttles when unfocused | Keep the game window visible during runs; record in the environment notes |

---

## 6. Open questions

| ID | Question | Resolved by |
|---|---|---|
| OQ0.1 | Does STS2-Agent compile and run on v0.111.1 (main since 2026-11-16)? | P0.E4.S2, P0.E5 |
| OQ0.2 | Which folder does the macOS build load mods from? | P0.E4.S3 |
| OQ0.3 | Does the event stream identify the human's card plays? | P0.E5.S4 |
| OQ0.4 | Does Steam Cloud sync these saves? | P0.E1.S3 |
| OQ0.5 | Does the game throttle in the background? | P0.E6.S5 |
| OQ0.6 | Do seeded runs work through the API (`select_character` with a seed)? | P0.E5.S1 (needed for exam seeds in Phase 4) |
