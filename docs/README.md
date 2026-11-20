# Phase Documents

Detailed specifications for each phase of [TRAINING_PLAN.md](../TRAINING_PLAN.md). Each phase document is written as epics and user stories with acceptance criteria. It also covers what to expect, who does what, the exit gate and known open questions.

Progress is tracked in [STATUS.md](STATUS.md).

---

## Document map

| Phase | Document | Goal | Depends on | Est. agent time | Est. Player time |
|---|---|---|---|---|---|
| 0 | [phase-0-setup.md](phase-0-setup.md) | Safe saves, main branch, mod built from source and verified, project scaffolding | — | 1–2 evenings | ~45 min |
| 1 | [phase-1-history-analysis.md](phase-1-history-analysis.md) | Run history turned into a dataset, analyses, combat benchmark, Ironclad playbook v1 | — (runs in parallel with 0) | 2–3 sessions | ~60 min (interview + review) |
| 2 | [phase-2-knowledge-base.md](phase-2-knowledge-base.md) | Verified game data, enemy notes, community strategy, playbook v2 | 0 (game data), 1 | 2–3 sessions | ~15 min (optional) |
| 3 | [phase-3-shadowing.md](phase-3-shadowing.md) | Agent watches live play, tests the live tools, records combat | 0, 2 | ~2 Player runs | 2 runs × 60–90 min |
| 4 | [phase-4-solo-practice.md](phase-4-solo-practice.md) | Agent plays full solo runs, reviews them, climbs ascension | 0, 2 (3 recommended) | 10+ runs × 1.5–3 h | Minimal |
| 5 | [phase-5-second-character.md](phase-5-second-character.md) | Necrobinder through the same pipeline, faster | 1–4 | About half of Phases 1–4 | ~2–3 runs shadowed |
| 6 | [phase-6-coop.md](phase-6-coop.md) | Co-op runs with the Agent as teammate, first co-op win | 4 (5 recommended) | Open-ended | Every co-op run |
| 7 | [phase-7-engine-simulator.md](phase-7-engine-simulator.md) | The game's own combat logic in our own process: exact, a few ms per fight, fair-play layer | 0; replays from 4 | Spike 1–2 days; phase several sessions | Approvals only (mod change, offline instance) |
| 8 | [phase-8-combat-search.md](phase-8-combat-search.md) | Search over the simulator beats the rule planner; live combat without language-model calls | 7 | Several sessions | Sign-off before autopilot runs |
| 9 | [phase-9-learning.md](phase-9-learning.md) | Neural combat models by expert iteration; learned strategy on simulated runs; M8, then M9 | 8 (strategy also P7.E8) | Open-ended | Framework approval; training schedule |

```
Phase 0 ──┬──> Phase 2 ──> Phase 3 ──> Phase 4 ──> Phase 5 ──> Phase 6
Phase 1 ──┘                  (shadowing)  (solo)    (2nd char)  (co-op)
```

Phase 1 needs neither the game nor the mod, so it can run while Phase 0 is in progress.

The engine track runs alongside Phases 4–6 and feeds them:

```
Phase 0 ──> Phase 7 ──> Phase 8 ──> Phase 9
(setup)    (engine     (combat     (learned models,
            simulator)  search,     reinforcement learning)
                        autopilot)
Phase 4 runs supply recorded fights to Phase 7; Phases 8 and 9 make Phases 4–6 faster and stronger.
```

Every story in Phases 7–9 follows [simulator-integrity.md](simulator-integrity.md): what the Agent may know when it decides, how the simulator stays exact, and how saves, accounts and evaluation stay safe and honest.

---

## Personas

| Persona | Who | Notes |
|---|---|---|
| **Player** | The human who owns the game and plays alongside the Agent | Makes every decision about their own machine, accounts and saves |
| **Agent** | The AI agent, working in an agent session in this folder | Reads state and acts through the mod; writes all project files |
| **Next Session** | A future Agent session that starts with no memory | Everything it needs must be in files; stories written "as the Next Session" exist to keep knowledge durable |

### Player-only actions

The Agent does not do these; the Player does them:

- Changing Steam settings (branch, Steam Cloud, Workshop subscriptions)
- Accepting the game's mod consent dialog and enabling mods in settings
- Approving the mod source review verdict before installation
- Installing paid software or buying a second copy of the game
- Approving tool permissions and allowlists for the agent harness
- Playing on their own character in co-op

---

## Story conventions

**IDs:** `P<phase>.E<epic>.S<story>`, for example `P1.E3.S4`.

**Format:**

> **P1.E3.S4: Freeze the encounter benchmark** · Size M · Status: Todo
> *As the Agent, I want a frozen per-encounter damage benchmark, so that solo runs in Phase 4 can be compared against the Player's real performance.*
>
> **Acceptance criteria**
> - [ ] …
>
> **Notes:** context, commands, pitfalls.

**Sizes** (Agent working time, excluding waiting on the Player or the game):

| Size | Effort |
|---|---|
| XS | under 15 min |
| S | 15–60 min |
| M | 1–3 h |
| L | 3–8 h |
| XL | more than one session; split it if possible |

**Status values:** `Todo`, `In progress`, `Blocked (<reason>)`, `Done`, `Dropped (<reason>)`.

---

## Knowledge provenance labels

Every rule in a playbook or knowledge file carries one label, so its strength is visible.

| Label | Meaning | Strength |
|---|---|---|
| `[GAME]` | Read from the game's own data via the mod, verified in a test fight, or read from the installed game's code (`tools/game_cards.py`, `tools/game_monsters.py`, `tools/game_facts.py`, `tools/asm/asm.cs`; cite the build and the type or method) | Highest |
| `[OBS]` | Observed repeatedly in the Agent's own runs (cite run IDs) | High |
| `[PLAYER-DATA]` | From the Player's run history (cite the report and n). **Outcome statistics** (deaths, damage taken, survival by situation) are evidence. **Pick rates and habits** are a baseline only. | Medium for outcomes; none for habits |
| `[PLAYER-SAID]` | The Player's stated reasoning from an interview or retro | Context and hypotheses; a rule only once outcomes support it |
| `[GAME-EXTRACT]` | Game data decompiled by a third party (for example the STS2-Agent `docs/game-knowledge` index, generated 2026-09-21), possibly from a different game build than ours | High for mechanics, but the version is unverified until checked against our build |
| `[COMMUNITY]` | From guides, tier lists or wikis (cite source and game version) | Medium-low until verified |
| `[HYPOTHESIS]` | An untested idea | Lowest; must be tested or dropped |

**When labels conflict:** `[GAME]` > `[OBS]` > `[GAME-EXTRACT]` > `[COMMUNITY]` consensus across several sources > `[PLAYER-DATA]` outcome evidence > a single `[COMMUNITY]` source > `[PLAYER-SAID]` and Player habits > `[HYPOTHESIS]`. Record the conflict in the playbook's "Open questions" section rather than deleting the losing view.

**Guiding principle:** the goal is to play well, judged by results. Matching the Player's choices is never a goal in itself. The Player's history is a danger map, a benchmark to beat and a source of hypotheses, especially where it loses.

---

## Definition of Ready (a story can start when)

- Its dependencies are `Done`.
- Any Player-only step it needs has been scheduled with the Player.
- Its acceptance criteria are testable.

## Definition of Done (a story is finished when)

- Every acceptance criterion is checked.
- Its outputs are saved at the paths named in the story.
- New knowledge carries provenance labels.
- [STATUS.md](STATUS.md) is updated.
- If it changed a playbook, the playbook changelog has an entry.

---

## How a new session starts

1. Read the project instructions (created in Phase 0).
2. Read [STATUS.md](STATUS.md) to find the active phase and story.
3. Read the active phase document, and only the sections it needs.
4. If a run is in progress, read its journal under `runs/` before touching the game.
