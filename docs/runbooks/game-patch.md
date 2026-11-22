# Runbook: After a Game Update (P2.E7.S1)

1. **Detect:** the newest `logs/godot*.log` shows a new `release=vX.Y.Z`, or `tools/sts.py health` (STS2-Agent) reports a new `game_version`.
2. **Back up** saves first (`docs/runbooks/restore-saves.md`).
3. **Mod:** reinstall (and rebuild if the game's assemblies changed). See `docs/runbooks/mod-install.md`, "After a game update".
4. **Game code checks** (need the .NET SDK; about 2 minutes; all read-only on the game):
   - `python3 -I tools/game_facts.py`: re-reads the facts our rules and tools depend on (waits, TestMode, replay recording, random streams, save and achievement calls, hidden intents, multipliers). Every CHANGED row means a rule in `docs/simulator-integrity.md` or a tool assumption must be re-checked before it is used.
   - `python3 -I tools/game_cards.py` and `python3 -I tools/game_monsters.py`: write `knowledge/data/game-cards-<version>.json` and `game-monsters-<version>.json` and the difference reports in `reports/game-check/`. Then set `TARGET_BUILD` in `tools/plan_turn.py` and `GAME_FACTS` in `tools/build_encounter_notes.py` to the new version and run `python3 -I tools/build_encounter_notes.py`.
   - Hand-written parts of boss and elite notes and the playbook: fix every number listed in `reports/game-check/monsters.md`.
5. **Data (extract):**
   - If STS2-Agent is available, export `/data/<collection>` to `knowledge/data/vX.Y.Z/`.
   - Otherwise re-import a newer decompiled extract with `tools/import_extract.py --src <path>` into a new dated folder (edit `OUT` in the script).
   - Diff against the previous export: cards, monsters, powers, relics.
6. **Mark stale:** every note or playbook rule that depends on a changed item gets `STALE (vX.Y.Z)` next to its label. Re-verify the high-impact ones first: boss plans, the elite table, card tiers.
7. **Benchmarks** are per version. Start a new benchmark file once enough runs exist on the new version. Never edit the old one.
8. Record the update in `docs/environment.md` and in the playbook changelog.
9. Phases 7–9: the simulator refuses a build it has not been checked against; run its fidelity suite before any simulator result is used (`docs/simulator-integrity.md` FI-3, FI-4). Rebuild the call graph (`tools/asm/asm.cs calls`) and read `python3 -I tools/asm/ui_only.py` for logic that only screens call (FI-7e, FI-7f); `python3 -I tools/sim.py runcheck --test-max-hp 999` has to match on every line.
