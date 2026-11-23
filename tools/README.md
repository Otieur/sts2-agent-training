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
| `keep_replays.py` | Keeps the game's fight recordings from the Player's own play, read-only, for the simulator's fidelity suite (`docs/runbooks/keep-player-replays.md`); skips the Agent's profile and other game builds are flagged | `keep_replays.py watch --while-game-runs` · `keep_replays.py status` |
| `fight_specs.py` | Realistic fight starting points from the Player's history (deck, relics, potions, HP before each fight; exam seeds excluded); `--validate` starts each in the simulator; `--benchmark` writes the 60-fight benchmark set `data/sim/benchmark-v1.json` | `fight_specs.py --character IRONCLAD --validate --benchmark` |
| `fight_trace.py` | One recorded fight replayed with the runs' fight search, every decision's candidates and values kept, with the card, potion or choice named and the hand, energy and incoming damage: how a fight is lost, turn by turn (decision 0006: a trace before any rule for a boss the Agent loses far more often than the Player). `--loss-value f/m/none` sets the options for the value of a lost rollout and `--end-turn-z` the check of the end of a turn against the planner (boss replay 3); default for both: as the runs play | `fight_trace.py data/learn/runs/run-bench-16 TEST_SUBJECT_BOSS 0` |
| `selfplay.py` | Self-play datasets for the learned models: fights in the simulator with the search policy as teacher, several hosts in parallel, a manifest per dataset (`data/learn/`) | `selfplay.py --workers 6 --fights 586 --specs data/learn/specs/fight-specs-ironclad.json` |
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

`asm/ui_only.py` (Python, reads the call graph): the game logic that only screen code calls, and the setters of logic properties that screen code calls (`--setters`). The simulator host has no screens, so each line is something the host has to do itself or do without; this is how the chest relic that never reached the player was found (`docs/simulator-integrity.md` FI-7e, FI-7f). Read the list after every game update.

## Fight situations from simulated runs
| Tool | What it does | Typical call |
|---|---|---|
| `run_specs.py` | Plays whole runs in the simulator (by default the run benchmark's `path` policy; `--policy` takes any run-benchmark policy, rollout ones with `--no-test-hp`) and records every fight's starting situation as a fight spec; with the test max HP (default) runs reach acts 2 and 3 and HP is re-drawn to 45-100% of the real max. Sources are `sim-<seed>`, which training always puts in the training split | `run_specs.py --runs 60 --workers 2` |
| `run_bench.py` | Run benchmark: whole runs from new seeds, policies built from components (`path`, `rcard`, `rpath`, `ropt`, `rshop`, `bc`, `el`, `br`, …; the list is in the script's header), search in every fight (`--combat mcw6 --fight-rebuild save+run`), paired report by seed; records each boss fight's start as a fight spec; with `--deadline`, workers stop between steps and the main process ends any that is still running 10 minutes later; a fight past turn 100 is given up and the run counted as lost there; a run does not depend on what its worker played before | `run_bench.py --out data/learn/runs/<name> --policies path rcard+rpath --seeds 60 --ascension 10 --combat mcw6`; `--report <dir> --baseline path` |
| `run_eval.py` | Decision-time evaluation by sampled rollouts: each option played forward over the same re-sampled futures to the end of the act (optional credit for progress against a boss) | used by `run_bench.py` |
| `run_opts.py` | Rollout decisions for events, rest sites, card choices outside fights (`ropt`) and shop purchases (`rshop`, `rshop2`) | used by `run_bench.py` |
| `run_details.py` | Details of a run benchmark folder for its report: per policy the state at each boss, purchases, where runs die; paired and factor comparisons; rollout decisions with the settings their evaluator used (`--decisions`) | section 5 of the run benchmark reports |
| `boss_specs.py` | Collects the boss fights reached in run benchmarks as a fight set for `learn/bench.py --benchmark` | `boss_specs.py data/learn/runs/run-bench-9 --out data/sim/boss-fights.json` |
| `boss_replay_read.py` | Reads boss replay 2: fights won per set, boss and arm, H1 (Fisher exact, bootstrap), Set G beside the runs, H3 (sign test), the Player's situations one by one | `boss_replay_read.py` |
| `forms_compare.py` | Two fight-benchmark arms compared on Test Subject files by situation: share of the three forms' HP removed, fights won, the form a lost fight ended in, sign tests (boss replays 2 and 3) | `forms_compare.py --a mcw6paf --b mcw6pafe data/learn/bench/boss-replay-3-t1` |

## Repository front page
| Tool | What it does | Typical call |
|---|---|---|
| `update_readme.py` | Regenerates the marked sections of `README.md` (headline numbers, latest benchmark table, real-run line, roadmap, refresh date) and `assets/benchmark-*.svg` from tracked files: reports, dataset and benchmark manifests, scoreboard, status board. Run after every milestone and at the end of each work block, then fast-forward `master` | `update_readme.py`, `update_readme.py --check` |
