# Tools

Standard-library Python. Run every script from the project root with `python3 -I tools/<name>.py`; each has a docstring with its full usage. Tests: `python3 -I -m unittest discover -s tools/tests`.

Live tools are **untested against the live game** until Phase 0 (`docs/runbooks/first-session.md`).

## Playing a run (Phase 4; STS2-Agent first, STS2MCP fallback)
| Tool | What it does | Typical call |
|---|---|---|
| `sts.py` | Talks to the mod: health, state (brief or raw), act with a mandatory reason (logged to `decisions.jsonl`), wait; co-op `--instance host/teammate` and `party` | `sts.py --mod sts2agent state --raw > runs/<run>/state.json` |
| `advise.py` | Reads a saved state, detects the screen and runs the right helper below | `advise.py --state runs/<run>/state.json` |
| `plan_turn.py` | Combat: searches the hand (and potions) for the safest and the best damage-for-HP plays, with targets | `plan_turn.py --state state.json` |
| `path.py` | Map: ranks every route to the boss by expected loot against fatal risk | `path.py --state state.json` |
| `draft.py` | Card reward: tier, v0.111.1 changes, boss fit, corner-target needs, engines, skip bar | `draft.py --from-state state.json` |
| `deck_check.py` | Act start and before the boss: corner targets and the boss's countable checklist | `deck_check.py --state state.json` |
| `calc.py` | Single damage, block and incoming-damage calculations | `calc.py attack 6 --hits 2 --vulnerable` |
| `simulate_fight.py` | Monte Carlo boss fight (Vantom) with the turn planner as policy: compare draft options against the boss | `simulate_fight.py --deck ... --vs TWIN_STRIKE --vs SHRUG_IT_OFF` |
| `journal.py` | Run journal: new, active, status, floor, fight (with benchmark), budget, summary | `journal.py fight runs/<run> --floor 7 --encounter vantom --turns 7 --damage 30` |
| `postmortem.py` | Facts sheet for a finished run (works on the Player's `.run` files too) | `postmortem.py runs/<run>/` |
| `smoke.py` | Phase 0: read-only check of every field the tools use; saves live fixtures | `smoke.py --save --watch` |
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

## Knowledge builders (Phase 2)
| Tool | Output |
|---|---|
| `import_extract.py` | `knowledge/data/extract-2026-09-21/*.json` from the STS2-Agent game-knowledge index (pre-v0.107.1) |
| `build_card_reference.py` | `knowledge/cards/<character>.md` (v0.111.1 values, patched cards marked) |
| `build_upgrade_table.py` | `knowledge/cards/ironclad-upgrades.md` |
| `build_community_tiers.py` | `knowledge/community/<character>-tiers.md`, discrepancy files |
| `build_encounter_notes.py` | Data blocks of `knowledge/bosses/` and `knowledge/enemies/` notes |
| `build_misc_reference.py` | `knowledge/events.md`, `relics.md`, `potions.md` |

## Shared
`stslib.py` (database, statistics, tables), `knowledge/data/card-patches.json` (card changes after the extract).
