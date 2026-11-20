# Tools

Standard-library Python. Run every script from the project root with `python3 -I tools/<name>.py`; each has a docstring with its full usage. Tests: `python3 -I -m unittest discover -s tools/tests`.

Live tools are **untested against the live game** until Phase 0 (`docs/runbooks/first-session.md`).

## Playing a run (Phase 4; STS2-Agent first, STS2MCP fallback)
| Tool | What it does | Typical call |
|---|---|---|
| `sts.py` | Talks to the mod: health, state (brief or raw), act with a mandatory reason (logged to `decisions.jsonl`), wait; co-op `--instance host/teammate` and `party` | `sts.py --mod sts2agent state --raw > runs/<run>/state.json` |
| `advise.py` | Reads the state (live from the mod, or a saved file), detects the screen and runs the right helper below; never raises on odd states | `advise.py --live --save runs/<run>/state.json` |
| `plan_turn.py` | Combat: searches the hand (and potions) for the safest and the best damage-for-HP plays, with targets; card-specific rules for the common Ironclad cards whose text the extract leaves incomplete (see its docstring) | `plan_turn.py --state state.json` |
| `path.py` | Map: ranks every route to the boss by expected loot against fatal risk | `path.py --state state.json` |
| `draft.py` | Card reward: tier, v0.111.1 changes, boss fit, corner-target needs, engines, skip bar | `draft.py --from-state state.json` |
| `deck_check.py` | Act start and before the boss: corner targets and the boss's countable checklist | `deck_check.py --state state.json` |
| `calc.py` | Single damage, block and incoming-damage calculations | `calc.py attack 6 --hits 2 --vulnerable` |
| `simulate_fight.py` | Monte Carlo boss fight with the turn planner as policy (validated: Vantom, Lagavulin Matriarch, Soul Fysh, Byrdonis, Entomancer; modelled but not validated: Waterfall Giant, Ceremonial Beast, Knowledge Demon, The Kin, The Insatiable): compare draft options against the boss (the run's upgrades, potions and common relics count); `--report` writes the simulation report, `--beast-sensitivity` the gap 25 variants | `simulate_fight.py --deck ... --vs TWIN_STRIKE --vs SHRUG_IT_OFF` |
| `journal.py` | Run journal: new, active, status, floor, fight (with benchmark), budget, summary | `journal.py fight runs/<run> --floor 7 --encounter vantom --turns 7 --damage 30` |
| `postmortem.py` | Facts sheet for a finished run (works on the Player's `.run` files too) | `postmortem.py runs/<run>/` |
| `smoke.py` | Phase 0: read-only check of every field the tools use; saves live fixtures | `smoke.py --save --watch` |
| `play_turn.py` | Live play: one call per decision (play the chosen combat plan or one action with a reason, wait only as long as the game needs, print the next advice) | `play_turn.py runs/<run> --go safe` |
| `fuzz_advise.py` | Robustness: advise.py on damaged and wrong-type copies of its fixtures; counts `[ADVICE FAILED]` answers by error site | `fuzz_advise.py --top 25` |
| `mcp_adapter.py` | Converts STS2MCP states to the STS2-Agent shape, so `advise.py` and every helper work with either mod (deck cached from combat piles) | used by `advise.py` automatically |

## Shadowing (Phase 3; both mods, `--mod sts2agent` by default)
`shadow.py` (call-it-first: logs the Agent's call at each decision before the Player acts, fills in the Player's pick and agreement; `--summary`), `watch.py` (decision-point watcher), `record.py` (state recorder), `reconstruct.py` (actions from snapshots), `stsstate.py` (shared helpers).

## Dataset and analyses (Phases 1–2)
| Tool | Output |
|---|---|
| `extract_runs.py`, `validate_data.py` | `data/runs.db` from the run files, and its checks |
| `analyze_encounters.py`, `analyze_cards.py`, `analyze_path.py`, `analyze_deaths.py`, `analyze_archetypes.py`, `interview_cases.py`, `build_report_data.py`, `cross_character.py` | Phase 1 reports in `reports/phase1/` |
| `build_band_benchmarks.py` | `data/benchmarks/*-by-band-v0.107.1.csv` |
| `analyze_boss_arrival.py` | `reports/phase2/boss-arrival-hp.md` |
| `deck_metrics.py` | Deck-strength proxies; `reports/phase2/deck-strength.md`; `apply_patches(version)` brings the extract's cards to v0.107.1 or v0.111.1 |
| `analyze_deck_features.py` | `reports/phase2/deck-features-by-encounter.md` |
| `analyze_room_values.py` | `reports/phase2/room-values.md` |
| `fight_model.py` | `reports/phase2/fight-model.md`, `data/tables/fight_model.json` (used by `path.py`) |
| `analyze_ancients.py` | `reports/phase2/ancient-relics.md`, `data/tables/ancient_relics.csv` (used by `advise.py`) |
| `analyze_card_choices.py` | `reports/phase2/card-choices-<character>.md`, `data/tables/card_choices_<character>.csv` (used by `draft.py`) |
| `backtest_rules.py` | `reports/phase2/rule-backtests.md` (H1, H4, H5) |
| `backtest_draft.py` | `reports/phase2/draft-backtest-<character>.md` |
| `check_playbook.py` | Recomputes the playbook's data-backed figures; exit 1 on any mismatch |
| `replay_run.py` | One of the Player's runs, decision by decision, against today's tools (`runs/examples/*/agent-replay.md`) |
| `death_review.py`, `fight_model.py`, `analyze_event_choices.py` | Death review, deck strength against HP lost, event choices at the decision point |

## Knowledge builders (Phase 2)
| Tool | Output |
|---|---|
| `import_extract.py` | `knowledge/data/extract-2026-09-21/*.json` from the STS2-Agent game-knowledge index (pre-v0.107.1) |
| `build_card_reference.py` | `knowledge/cards/<character>.md` (v0.111.1 values, patched cards marked) |
| `build_upgrade_table.py` | `knowledge/cards/ironclad-upgrades.md` |
| `build_community_tiers.py` | `knowledge/community/<character>-tiers.md`, discrepancy files |
| `build_encounter_notes.py` | Data blocks of `knowledge/bosses/` and `knowledge/enemies/` notes (bosses, elites, the 15 most frequent hallway fights, and hallway fights with 2+ deaths) |
| `build_misc_reference.py` | `knowledge/events.md`, `relics.md`, `potions.md` |

## Shared
`stslib.py` (database, statistics, tables), `knowledge/data/card-patches.json` (card changes after the extract).

## Simulator (Phase 7; host in `sim/`, C# on .NET 9)
| Tool | What it does | Typical call |
|---|---|---|
| `sim.py` | Bridge to the simulator host: the game's own combat logic outside the game. `smoke` positions a recorded fight and rolls it out; `fidelity` replays every recorded fight against the game's recorded states; `fairplay` runs the sanitizer, determinism, invariance and leak-canary checks; `planner` runs `plan_turn.py` as the policy on sampled futures; `sweep` starts every encounter from nothing; `runs` plays whole runs from new seeds; `runcheck` replays a recorded run from its seed; `clone` checks snapshot and restore; `sandbox` checks saves, sandbox home and network; `search` compares the planner with flat Monte Carlo over its candidate actions | `sim.py fidelity` · `sim.py planner --seeds 10` · `sim.py runs --count 30` · `sim.py search --fights 12 --k 6` |

## Checks against the game's own code (run after every game update: `docs/runbooks/game-patch.md`)
| Tool | What it does | Typical call |
|---|---|---|
| `game_facts.py` | Re-reads the facts about the game's code that our rules and tools cite (15 checks); exit code 1 and a CHANGED row when one no longer holds | `game_facts.py` |
| `game_cards.py` | Card cost, type, rarity, target, values and upgrade amounts from the game; writes `knowledge/data/game-cards-<version>.json` (used by `plan_turn.py`) and `reports/game-check/cards.md` | `game_cards.py` |
| `game_monsters.py` | Monster HP and move numbers with A8+ and A9+ values; writes `knowledge/data/game-monsters-<version>.json` (used by `build_encounter_notes.py`) and `reports/game-check/monsters.md` | `game_monsters.py` |

## Game engine research
`asm/asm.cs` (C#, .NET 10 file-based app, runtime libraries only): indexes `sts2.dll` (types, members, constant values), builds a call graph from IL, or prints the IL of matching methods. Outputs go to `data/asm/` (not in git). Findings and next steps: `docs/proposals/engine-simulation-spike.md`.
`dotnet run tools/asm/asm.cs -- index|calls <dll> <out>` · `dotnet run tools/asm/asm.cs -- il <dll> "Cmd+<Wait>"`
