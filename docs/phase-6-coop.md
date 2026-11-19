# Phase 6: Co-op

**Goal:** the Player and the Agent play Slay the Spire 2 co-op runs together, each controlling their own character, and win one (milestone M6). Then climb the multiplayer ascension ladder.

**Depends on:** Phase 4. Phase 5 is recommended, for the pairing decision and a second character.
**Unblocks:** the end goal.

---

## 1. What to expect

| | |
|---|---|
| **Setup** | The Player hosts from their own game. The mod's "Invite AI Teammate" launches a second game window on the same Mac, in offline mode, and it joins the lobby. The Agent controls that second window's character through its own API. No second Steam account is needed with this method. |
| **Biggest unknown** | Whether the second-instance launcher works on macOS. The mod documents Windows install steps only. E2 tests this first and has fallbacks. |
| **Pace** | Turns are simultaneous. The Agent reads both states, plans and acts, which takes about 20–60 s per turn. The Player will sometimes wait for the Agent to end its turn. A full co-op run is probably 2–4 hours. |
| **Coordination** | Happens in the agent chat. The Agent posts a short turn plan when it matters. The Player can give shorthand instructions. |
| **First runs** | Expect them to be messy: interface edge cases unique to multiplayer, waiting on map votes, a desync or two. The first co-op run is a shakedown, not a win attempt. |
| **Ascension** | Multiplayer ascension is separate from single-player ascension, so co-op starts at A0 whatever the solo progress. |

---

## 2. Co-op rules (community sources; to be verified in E1)

| Area | Rule as reported |
|---|---|
| Party | 1–4 players, Steam friends only; no public matchmaking. The mod's local teammate uses offline mode instead. Duplicate characters allowed. |
| Saves | Tied to the host. The group can resume a paused run together. |
| Individual | Deck, gold, energy, relics, card rewards, merchant inventory, Ancient options |
| Shared | Map path and encounters, including enemy buffs and debuffs |
| Turns | Simultaneous. Everyone queues actions in the same window and the game resolves them in order. No turn timer reported. |
| Potions | Can target other players |
| Visibility | Teammates' cursors are visible in game, and each player can inspect the others' decks and relics |
| Enemy HP | Scales with party size (exact numbers not reported) |
| Debuffs | Vulnerable is worth more, because several players hit the debuffed enemy |
| Map | Players vote at forks; a weighted roulette picks the path. Players can draw on the map. |
| Chests | Each player is offered one relic, and no two players can take the same one. Ties are settled by an automatic rock-paper-scissors. |
| Rest sites | Each option is available to every player independently. "Mend" heals another player. |
| Death | A player at 0 HP is out for the rest of that fight and comes back at 1 HP afterwards. The next act restores more HP. |
| Co-op-only cards | Exist in every character pool and in colorless (for example, sharing block with the party, or redirecting a teammate's incoming attacks) |
| Progression | Finishing a multiplayer run unlocks an ascension level for each character present. Multiplayer ascension is separate. |

### Mod constraints (from the STS2-Agent docs)

- Each instance can act only for its own character. Acting for another player returns `403 forbidden_actor`.
- In map voting, once `map.local_vote` is set, the Agent waits. It does not vote again; advancing needs every player's vote.
- `choose_rest_option` accepts a `target_index` for co-op options such as Mend.
- **Never use the game's Load button for a co-op save.** It can reject local-connection player IDs and rename the save as corrupt. Use the mod's "Continue the saved co-op run" (`continue_ai_teammate`) instead.
- Autoplay must stay off. `/teammate/control {"running": false}` on the main window. The Agent drives the teammate through the teammate instance's own `/state` and `/action`.

---

## 3. Epics and stories

### P6.E1: Verify the co-op rules

> **P6.E1.S1: Rules file** · Size S · Status: Done (knowledge/coop-rules.md; two community sources cross-checked, co-op cards from the extract)
> *As the Agent, I want the co-op rules in one file with verification status, so that strategy rests on confirmed rules.*
>
> **Acceptance criteria**
> - [ ] `knowledge/coop-rules.md` has every rule from section 2, labelled `[COMMUNITY]`.
> - [ ] Each is re-labelled `[GAME]` once observed in a co-op run or confirmed from game data. Contradictions are noted.

> **P6.E1.S2: Measure enemy HP scaling** · Size S · Status: Todo
> *As the Agent, I want the real HP scaling for a 2-player party, so that damage planning and elite decisions use correct numbers.*
>
> **Acceptance criteria**
> - [ ] Enemy max HP is recorded for at least 10 encounters in co-op and compared with the solo values from `/data/monsters`. The multiplier is recorded.

---

### P6.E2: Second instance on macOS

> **P6.E2.S1: Test Invite AI Teammate** · Size S · Status: Todo
> *As the Player, I want to know quickly whether the built-in teammate launcher works on my Mac, so that we choose the right setup path.*
>
> **Acceptance criteria**
> - [ ] With autoplay unconfigured: Main Menu → AI Teammate tab → Invite AI Teammate.
> - [ ] Recorded: the main window's `/health` (`dual_launch_outcome`, `dual_status`), whether a second window opens, whether it joins the lobby, and the companion `api_port`.
> - [ ] Result goes into `docs/api-notes.md`: works, partly works, or fails, with details.

> **P6.E2.S2: Patch the launcher for macOS (if E2.S1 fails)** · Size M · Status: In progress (patch proposal in docs/proposals/sts2-agent-macos-teammate.md; not applied)
> *As the Agent, I want the launcher to start the macOS binary correctly, so that the built-in co-op path works.*
>
> **Acceptance criteria**
> - [ ] Find the launcher code (from the P0.E3.S2 review). Make it start the macOS executable inside `SlayTheSpire2.app/Contents/MacOS/` with `--force-steam off` and the companion settings file. Alternatively, `open -n -a <app> --args ...`.
> - [ ] Rebuild, reinstall, and repeat E2.S1.
> - [ ] The patch is kept in `vendor/patches/` with a note. It is not distributed.

> **P6.E2.S3: Resource check** · Size XS · Status: Todo
> *As the Player, I want two game instances to run smoothly on my Mac, so that co-op is playable.*
>
> **Acceptance criteria**
> - [ ] With both instances in a fight, CPU, memory and frame rate are checked. If the Mac struggles, lower the teammate window's graphics settings (it can stay small and in the background if throttling allows, per OQ0.5).

> **P6.E2.S4: Fallback A, STS2MCP localhost join** · Size M · Status: Todo (only if E2.S1 and E2.S2 fail)
> *As the Agent, I want a second way to run a local co-op client, so that macOS launcher problems do not block co-op.*
>
> **Acceptance criteria**
> - [ ] Using STS2MCP's documented host and localhost join support: the Player hosts, a second instance is launched manually and joins through localhost, and the Agent drives it through STS2MCP's API (port 15526, or a configured port).
> - [ ] Smoke test: lobby, character select, first fight.

> **P6.E2.S5: Fallback B, a second machine (Player decision)** · Size XS · Status: Todo (only if A fails)
> *As the Player, I want the last-resort option written down with its costs, so that I can decide with full information.*
>
> **Acceptance criteria**
> - [ ] Documented requirements: a second computer that runs the game, a second Steam account that owns the game, Steam friendship between the accounts, and the mod installed on the second machine. Network access from the agent harness to that machine's API (SSH tunnel or an agent session on that machine). Cost noted. The Player decides.

---

### P6.E3: Teammate control

> **P6.E3.S1: Point the harness at the teammate instance** · Size S · Status: Todo
> *As the Agent, I want the Phase 4 harness to target the teammate's port, so that all the solo tooling works in co-op.*
>
> **Acceptance criteria**
> - [ ] `tools/sts.py --instance teammate` resolves the port from the main window's `/health` (`data.companion.api_port`).
> - [ ] Every subcommand works against the teammate.
> - [ ] `data.companion.auto_play` is confirmed `false`.

> **P6.E3.S2: Read the host's state too** · Size S · Status: Todo
> *As the Agent, I want to read the Player's own instance as well, so that I can see the Player's hand, energy and plan around it, which my own instance does not show.*
>
> **Acceptance criteria**
> - [ ] `tools/sts.py --instance host state --brief` shows the Player's hand and status.
> - [ ] A combined view `tools/sts.py party` shows both players' HP, block and energy, the Player's hand, the Agent's hand, and the enemies' intents, all on one screen.
> - [ ] Reading the host is allowed. The Agent never sends actions to the host instance; the harness refuses it.

> **P6.E3.S3: Multiplayer screen handlers** · Size M · Status: Todo
> *As the Agent, I want handlers for the screens that only exist in co-op, so that the run does not stall on them.*
>
> **Acceptance criteria**
> - [ ] The decision loop runbook gains handlers for:
>   - lobby (select character, ready, unready)
>   - map voting (vote once, then wait on `local_vote`)
>   - chest relic choice with ties
>   - co-op rest options with a target
>   - waiting for the teammate
>   - the downed state (out of the fight until it ends)

> **P6.E3.S4: Actor-error handling** · Size XS · Status: Todo
> *As the Agent, I want `403 forbidden_actor` handled cleanly, so that a wrong target does not derail a turn.*
>
> **Acceptance criteria**
> - [ ] The error table in the runbook includes `forbidden_actor`: re-read the state, check that `player_id` and the target belong to the local player, and correct the call.

---

### P6.E4: Communication protocol

> **P6.E4.S1: Turn huddle** · Size S · Status: Todo
> *As the Player, I want the Agent's plan in a quick, readable form when it matters, so that we coordinate without long messages.*
>
> **Acceptance criteria**
> - [ ] On turns that matter (elites, bosses, high incoming damage, possible lethal), the Agent posts within about 15 s of the turn starting:
>   `Incoming: <total per player> · My plan: <cards/targets> · Need from you: <e.g. "block 12" or "kill the left one">`
> - [ ] On routine turns, no message unless the Player asks.

> **P6.E4.S2: Player shorthand** · Size XS · Status: Todo
> *As the Player, I want short commands the Agent understands, so that I can steer without typing much mid-fight.*
>
> **Acceptance criteria**
> - [ ] A glossary in `playbooks/coop.md`, for example:
>   - `focus <left/right/name>`: target an enemy
>   - `I block` / `you block`: who takes defence
>   - `go` / `wait`: start or hold the turn
>   - `pot <name>`: use a potion
>   - `mend me`: rest-site heal on the Player
>   - `your call`: the Agent decides
> - [ ] The Agent confirms each command with one short line.

> **P6.E4.S3: Map plan agreement** · Size XS · Status: Todo
> *As the Player, I want us to agree on the act's path before voting, so that the roulette does not split our plan.*
>
> **Acceptance criteria**
> - [ ] At each act start, the Agent proposes a path with its reasons (P4.E3.S1 logic, adjusted for co-op HP scaling and both players' HP). The Player agrees or edits. Both vote the agreed path.

> **P6.E4.S4: Reward and relic coordination** · Size XS · Status: Todo
> *As the Agent, I want to coordinate chest relic choices and rewards, so that we avoid ties and each relic goes where it does most good.*
>
> **Acceptance criteria**
> - [ ] At chests, the Agent states which relic it wants before choosing, and avoids picking the Player's choice. At shops and rewards, it mentions synergy with the Player's deck when relevant.

---

### P6.E5: Co-op strategy

> **P6.E5.S1: Co-op card evaluation** · Size M · Status: Todo
> *As the Agent, I want co-op-only cards and co-op card values documented, so that drafting in co-op reflects the party.*
>
> **Acceptance criteria**
> - [ ] Every co-op-only card in the Agent's chosen character's pool and in colorless, with its tier, read from the game data.
> - [ ] Adjustments to solo tiers in co-op (for example, Vulnerable effects worth more, AoE value against scaled HP).

> **P6.E5.S2: Role split** · Size S · Status: Todo
> *As the Player, I want a clear division of roles between our characters, so that our decks complement rather than duplicate each other.*
>
> **Acceptance criteria**
> - [ ] Based on the pairing decision (P5.E6.S2): who brings front-loaded damage, scaling, AoE, block and support. Written into `playbooks/coop.md`, with the drafting implications for the Agent.

> **P6.E5.S3: Co-op playbook** · Size M · Status: Todo
> *As the Next Session, I want everything about co-op play in one file, so that every co-op session starts informed.*
>
> **Acceptance criteria:** `playbooks/coop.md` covers:
> - [ ] The communication protocol.
> - [ ] The role split.
> - [ ] Co-op pathing (HP scaling, the HP of both players).
> - [ ] Rest-site coordination (when to Mend).
> - [ ] Potion sharing.
> - [ ] Downed-player rules.
> - [ ] Co-op card tiers.
> - [ ] A changelog.

---

### P6.E6: Co-op run ladder

> **P6.E6.S1: Shakedown run** · Size L (plus Player time) · Status: Todo
> *As the Player, I want a first co-op run focused on making everything work, so that problems surface without pressure.*
>
> **Acceptance criteria**
> - [ ] A0 co-op, played to the end or to a run-ending failure.
> - [ ] Every interface problem is logged in `docs/api-notes.md`. A retro is written.
> - [ ] Success means no desync and no stalls the Agent could not recover from, not a win.

> **P6.E6.S2: Co-op retros** · Size S · Status: Todo
> *As the Player, I want a retro after every co-op run from both sides, so that we improve as a team.*
>
> **Acceptance criteria**
> - [ ] `runs/coop-<date>/retro.md`:
>   - what worked
>   - what did not
>   - coordination misses
>   - The Agent's 3 costliest decisions
>   - the Player's feedback
>   - changes to `playbooks/coop.md`

> **P6.E6.S3: Co-op scoreboard** · Size XS · Status: Todo
> *As the Player, I want co-op results tracked separately, so that our team progress is visible.*
>
> **Acceptance criteria**
> - [ ] `metrics/coop.csv`: date, characters (Player and Agent), multiplayer ascension, win, floor reached, killed_by, downed count per player, desyncs, wall_minutes, tokens.

> **P6.E6.S4: Climb** · Size XL · Status: Todo
> *As the Player, I want us to climb the multiplayer ascension levels together, so that the challenge keeps growing.*
>
> **Acceptance criteria**
> - [ ] The same ladder rule as solo: move up after a win, and run a focused review after 3 losses in a row.
> - [ ] M6 (first co-op win) is recorded in `metrics/milestones.md`.

---

### P6.E7: Reliability

> **P6.E7.S1: Save and resume procedure** · Size S · Status: Todo
> *As the Player, I want a safe way to pause and resume co-op runs, so that a long run can span several evenings.*
>
> **Acceptance criteria**
> - [ ] `docs/runbooks/coop-session.md`:
>   - back up saves before each session
>   - start-up order (host first, then invite the teammate)
>   - pausing (save and quit from the host)
>   - resuming (`continue_ai_teammate` on the host main menu, **never** the Load button)
>   - the NetId mismatch error and what to do about it

> **P6.E7.S2: Desync detection** · Size S · Status: Todo
> *As the Agent, I want to notice a desync quickly, so that we stop before it corrupts the run.*
>
> **Acceptance criteria**
> - [ ] Each turn, the Agent compares the host's and the teammate's state: floor, enemy HP and intents, both players' HP.
> - [ ] On a mismatch that persists past animations, the Agent stops, tells the Player and follows the runbook (save and quit from the host, resume).

> **P6.E7.S3: Crash recovery** · Size S · Status: Todo
> *As the Player, I want a clear procedure if either window crashes, so that we lose as little as possible.*
>
> **Acceptance criteria**
> - [ ] The runbook covers: teammate crash (it exits with the host, per the mod changelog; relaunch through Continue), host crash (relaunch, Continue), and the backup restore as a last resort.

---

## 4. Exit gate (the end goal)

- [ ] Co-op setup works reliably on the Player's machine (or an agreed fallback)
- [ ] `playbooks/coop.md` v1 or later
- [ ] **M6: first co-op win**
- [ ] Stretch: a co-op win at multiplayer A5

---

## 5. Open questions

| ID | Question | Resolved by |
|---|---|---|
| OQ6.1 | Does Invite AI Teammate work on macOS, as is or patched? | P6.E2.S1–S2 |
| OQ6.2 | What is the exact enemy HP multiplier for 2 players? | P6.E1.S2 |
| OQ6.3 | Does the offline teammate instance use its own profile and unlocks, and does that limit its character or ascension options? | P6.E2.S1 |
| OQ6.4 | How long does the Player actually wait per Agent turn, and is that acceptable? | P6.E6.S1 retro |
| OQ6.5 | Can the Agent read the host instance's state while the host is controlled by the Player? | P6.E3.S2 |
