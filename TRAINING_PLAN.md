# Slay the Spire 2 Agent Training Plan

Goal: the Agent plays Slay the Spire 2 competently, first solo and then as a co-op teammate alongside the human player, controlling its own character through a state-export mod.

**The aim is to play well, judged by results. It is not to imitate the player.** The player's run history serves three purposes: a danger map (which fights cost HP and end runs), a benchmark to beat, and a source of hypotheses, especially where the player's runs are lost. The player's habits and stated reasoning are context. They become rules only when outcomes support them. (Clarified by the player on 2026-11-18.)

**The target is to become clearly better than the player** (2026-11-19). The player's statistics are a rough guide and a floor, not a ceiling. The advantages to build on: exact arithmetic every turn (incoming damage, lethal, block), the same rules applied every time, game data instead of memory, community expert knowledge, and controlled experiments on fixed seeds. The player's Ironclad win rate by band (finished runs, v0.107.1) is the bar: A0–4 63% (5/8), A5–9 25% (5/20), A10 8% (2/24).

Written 2026-11-18. Update this file when a phase finishes or the plan changes.

**Detailed phase documents** (epics, user stories, acceptance criteria, what to expect, exit gates) are in [docs/](docs/README.md). Progress is tracked in [docs/STATUS.md](docs/STATUS.md). This file is the overview; the phase documents are the specification.

---

## 1. How the agent "learns"

The Agent's model weights do not change between sessions. Every session starts with no memory of the last one. All improvement therefore has to be written down, so that the next session can read it before it plays:

| Component | What it holds | Where it lives |
|---|---|---|
| Playbook | Strategy per character: card evaluations, archetypes, pathing rules, HP budgets, boss plans | `playbooks/<character>.md` |
| Knowledge base | Game facts: cards, relics, potions, enemies, intents, encounter danger | `knowledge/` |
| Run journals | Live notes during a run (deck plan, threats ahead), so that context compaction does not lose the plan | `runs/<date>-<seed>/journal.md` |
| Post-mortems | Mistakes found after each run, and the playbook changes they caused | `runs/<date>-<seed>/postmortem.md` |
| Scoreboard | Metrics across runs, used to judge whether a playbook change actually helped | `metrics/scoreboard.csv` |

The training loop is: **play → log every decision with a reason → review the run → change the playbook only on evidence → replay**. The playbook keeps a changelog, so a bad change can be found and reverted.

---

## 2. Starting point

### 2.1 Available data

The run history (`~/Library/Application Support/SlayTheSpire2/steam/<id>/profile1/saves/history/*.run`) holds 233 unique runs. 227 of them were played on v0.107.1, which is the current main-branch version. Each `.run` file records, floor by floor:

- card rewards offered and the one picked (or a skip)
- shop stock and purchases, and card removals
- rest-site choices and upgrades
- event and Ancient choices
- relics, potions obtained and used
- damage taken, turns taken and the encounter ID for each fight
- the final deck and relics, the cause of death, and the ascension level

The files do **not** record turn-by-turn combat. Combat skill has to come from live observation (Phase 3) and from the Agent's own play (Phase 4).

| Character | Runs | Wins | Win % | A10 runs (wins) | Card reward screens | Fights | Most frequent killers |
|---|---|---|---|---|---|---|---|
| Ironclad | 57 | 12 | 21% | 28 (2) | 664 | 633 | Vantom boss ×6, Knowledge Demon boss ×4, Soul Fysh boss ×3 |
| Necrobinder | 59 | 11 | 19% | 16 (1) | 746 | 703 | Knowledge Demon ×4, Test Subject ×4, Vantom ×3 |
| Regent | 53 | 10 | 19% | 14 (0) | 627 | 588 | Hunter Killer ×3, Infested Prisms elite ×3 |
| Silent | 52 | 10 | 19% | 22 (0) | 634 | 595 | Aeonglass ×4, Test Subject ×3, Ceremonial Beast ×3 |

Win % counts abandoned runs as losses.

### 2.2 First character: Ironclad

1. The most high-ascension data: 28 A10 runs and 42 at A8 or above. It is the only character with two A10 wins.
2. The simplest kit to read from game state. It has fewer extra resources to track than characters with summons or secondary resources.
3. There is a public reference point. The STS2MCP author benchmarked full Ironclad runs played by language models, so results can be compared.

Second character: **Necrobinder**, which has the most card reward decisions recorded (746). Shared knowledge (enemies, pathing, events) carries over.

### 2.3 Game version and mod

- **Target version: main branch v0.107.1.** It matches 227 of the 233 recorded runs, and it is the branch with Steam Workshop mod support.
- **Primary mod: [Meddrin/STS2-Agent](https://github.com/Meddrin/STS2-Agent)**, a fork of CharTyr/STS2-Agent licensed under AGPL-3.0. It provides a localhost HTTP API, an optional MCP server, a decision log with per-action reasons, and an "Invite AI Teammate" feature. That feature launches a second local game instance in offline mode, which an external agent can drive. It was last updated 2026-09-24, and its docs reference game v0.111.0.
- **Fallback mod: [Gennadiyev/STS2MCP](https://github.com/Gennadiyev/STS2MCP)**, licensed under MIT. It runs a REST API on `localhost:15526`, documents the macOS install path, and supports beta multiplayer, including localhost joins. Its last release was v0.4.0 (May), tested up to v0.99.1.
- **Risk:** neither mod states v0.107.1 or macOS as tested. Phase 0 checks compatibility. If the primary mod fails on v0.107.1, the options in order are: rebuild it from source against the local game assemblies and fix the breaks, switch to the fallback mod, or switch the game to whichever branch the mod works on.

---

## 3. Phases

### Phase 0: Setup

1. **Back up saves.** Copy `~/Library/Application Support/SlayTheSpire2` to a dated backup folder before changing branches. Switching from beta (save schema newer) to main may not read the newer files.
2. **Switch branch.** In Steam, set Slay the Spire 2 → Properties → Betas to "None" so the game runs v0.107.1. Confirm the version in `logs/godot.log` (`release=v0.107.1`).
3. **Review the mod source.** Clone STS2-Agent and read the code before installing it. Check that it binds only to `127.0.0.1`, find any outbound network calls (the built-in autoplay calls external LLM APIs, and that feature stays unconfigured), and look at what the second-instance launcher executes.
4. **Build from source** with `dotnet` (`./scripts/build-mod.sh --configuration Release`). Do not use a prebuilt binary. Install the built files into the macOS mods folder (`SlayTheSpire2.app/Contents/MacOS/mods/`) and enable mods in the game settings.
5. **Verify** with `curl http://127.0.0.1:<port>/health`: it should show the game version and that the mod is loaded.
6. **Connect to the agent harness.** Enable the mod's MCP service (F8 → Connect) and add it to this project's `.mcp.json`. Read the bundled `skills/sts2-mcp-player/SKILL.md` and add it as a project skill if it holds up.
7. **Scaffold the project:**
   ```
   TRAINING_PLAN.md     this file
   data/                extracted run dataset (CSV/JSON)
   knowledge/           cards, relics, potions, enemies, encounters
   playbooks/           one strategy file per character
   runs/                journals and post-mortems for each agent run
   metrics/             scoreboard.csv
   tools/               analysis scripts, state recorder
   ```

**Done when:** The Agent reads `/state` in a live fight, plays one card through `/action`, and the decision shows up in `GET /decisions`.

### Phase 1: Learn from the run history (offline, can start before Phase 0)

The scripts in `tools/` turn the `.run` files into a dataset, then produce these analyses for Ironclad:

1. **Card pick table.** For each card: times offered, pick rate, pick rate by act, and skip rate. Pick rates describe what the player does, not what wins. With only 12 Ironclad wins, a win/loss split is reported only where the sample is large enough, and is marked as weak evidence.
2. **Encounter danger table.** Median and 90th-percentile damage taken, turns taken and deaths for every encounter ID. This feeds pathing and HP budgeting, and becomes the **combat benchmark**: the Agent's damage taken per encounter is later compared with the player's median.
3. **Pathing profile.** Elites, rests, shops and events per act, compared between wins and losses.
4. **Rest-site policy.** Rest versus upgrade by HP %, and which cards get upgraded first.
5. **Economy.** Shop purchases, card removals, gold at each shop.
6. **Ancient and event choices.**
7. **Death analysis.** For the top killers (Vantom, Knowledge Demon, Soul Fysh, Entomancer elite): deck and HP on arrival, turns survived.
8. **Winning deck archetypes.** Final decks clustered by card overlap.

Then a short **interview** about surprising decisions ("you skipped X for Y on floor 6, why?"). The answers explain the data and suggest hypotheses. They are recorded with a data check, and they do not become rules unless outcomes support them.

The player's own win rate is about 20% at mostly A9–A10. Learning only from that history would cap the Agent at the same level and copy the same mistakes. Phase 2 adds outside knowledge to counter this.

**Output:** `playbooks/ironclad.md` v1, `knowledge/encounters.md` and charts of the main findings.

### Phase 2: Build the knowledge base

1. Pull card, relic, potion and monster data from the mod's `GET /data/{collection}` endpoints. These are the game's own numbers for this version.
2. Write enemy notes: move patterns and intents, sourced from the in-game Bestiary, community wikis and live observation. Prioritise the top killers.
3. Collect community Ironclad strategy for v0.107.x: tier lists, archetype guides. Record where it disagrees with the player's habits.
4. Write a boss plan for each Act boss: what the deck needs by the time it gets there, and how to play the fight.

**Output:** `knowledge/` populated, and playbook v2 with the outside knowledge merged in.

### Phase 3: Shadowing (the player plays, the Agent watches through the mod)

With the mod in the player's game, the Agent reads the live state at each decision point.

1. **Call it first.** At every card reward, path choice, shop and rest site, the Agent writes down its choice and reasoning before the player picks. Each one is logged as agree or disagree. Disagreements are settled by evidence: what happened next, game data, community consensus, or a test in Phase 4. Neither side wins by default.
2. **Combat calls.** On selected turns, the Agent proposes the full turn (card order, targets, potion use) before the player acts, and compares it with what the player does.
3. **State recorder.** A script polls `/state` (or listens on `/events/stream`) and records snapshots, so the player's card plays can be reconstructed from the differences between them. The mod does not log human actions directly, so this needs testing. If it works, it fills the gap left by `.run` files having no combat turns.

**Target:** about 2 shadowed runs, mainly to test the live tools and record real combat. Agreement with the player is logged but is not a goal.

### Phase 4: Solo practice (the Agent plays)

The Agent plays full Ironclad runs through the mod.

**Per-decision protocol**
1. Read `/state` and `/actions/available`.
2. Check the playbook, the encounter notes and the run journal.
3. Choose, and send the action with `client_context.decision_reason` filled in, so every decision can be audited later.
4. Update the run journal at every floor: deck plan, HP budget, next threats.

**After each run: post-mortem**
- HP and deck trajectory, cause of death.
- The three costliest decisions and what should have happened instead.
- Damage per encounter compared with the player's median from Phase 1.
- Proposed playbook changes, each tied to evidence from this run or earlier ones.

**Ascension ladder**
- Start at A0. Move up one level after each win.
- After three losses in a row at one level, stop and do a focused review of those runs before playing again.

**Exam seeds**
- Fix a set of 5 seeds. Replay them at each milestone to measure progress between playbook versions under similar conditions.
- Optional: the player plays the same seeds for a head-to-head comparison.

**Metrics** (`metrics/scoreboard.csv`, one row per run): character, ascension, seed, playbook version, win, floor reached, elites killed per act, HP lost per encounter, decisions made, illegal or failed actions, wall-clock time, tokens used.

**Expected pace:** about 400–500 actions per full run. At several seconds per action, one run takes roughly 1.5–3 hours of wall time.

### Phase 5: Second character

Repeat Phases 1–4 for Necrobinder, reusing the knowledge base. It should go faster, because enemies, pathing and events are shared.

### Phase 6: Co-op

1. **Research the co-op rules:** map voting, simultaneous turns, co-op-only cards, how rewards and rest options work for multiple players (the mod's `choose_rest_option` accepts a target player in co-op), and how enemies choose targets.
2. **Setup:** the player hosts from their own game. "Invite AI Teammate" launches the second local instance. The Agent drives it through that instance's own `/state` and `/action`, with autoplay off. **macOS support for the second instance is untested.** Fallbacks: STS2MCP's localhost join, or a second machine.
3. **Coordination:** the mod exposes the full detail of the local player only. The Agent sees other players' HP and map votes, but not their hand. The plan for each turn is agreed in chat ("I take the left enemy, you block the big hit").
4. **Co-op playbook:** role split by character, map-vote policy, who takes which rewards, how to share HP pressure.
5. **Ladder:** A0 co-op first, then climb the same way as in Phase 4.

---

## 4. Milestones

| # | Milestone | Evidence |
|---|---|---|
| M1 | Full run finished with no mod failures or illegal actions | Scoreboard row, clean decision log |
| M2 | Beats the Act 1 boss in 3 of 5 runs | Scoreboard |
| M3 | First solo win at A0 | Scoreboard |
| M4 | Median damage per Act 1–2 hallway fight at or below the player's median **in the same ascension band** | Band benchmarks (`data/benchmarks/*-by-band-*`) versus scoreboard |
| M5 | Solo win at A5 | Scoreboard |
| M6 | First co-op win | Scoreboard |
| M7 | Solo win at A10 (stretch) | Scoreboard |
| M8 | Better than the player: higher win rate than the player's in the same ascension band over at least 10 finished runs (A5–9: above 25%; A10: above 8%) | Scoreboard against the Phase 1 baseline |
| M9 | Consistent at A10: 3 wins in any 10 consecutive A10 runs (stretch) | Scoreboard |

---

## 5. Known risks

| Risk | Mitigation |
|---|---|
| Mod not compatible with v0.107.1 or macOS | Build from source and patch; fallback mod; change branch |
| Mod bugs or co-op desync corrupt a run | Use the modded profile only; back up saves; never use the game's Load button for co-op saves (the mod docs warn this can mark the save corrupt) |
| Context compaction mid-run loses the plan | Run journal updated every floor |
| Learning only from the player's history caps skill at the player's level | Outside knowledge (Phase 2), the Agent's own experiments, exam seeds |
| Small sample sizes (12 Ironclad wins) | Report counts next to rates; treat win correlations as hypotheses |
| Overfitting the playbook to one run | Changes need evidence; changelog; exam seeds catch regressions |
| Token usage (the STS2MCP author reports about 8M tokens per run for a smaller model) | Record tokens per run in the scoreboard so the real cost is known |
