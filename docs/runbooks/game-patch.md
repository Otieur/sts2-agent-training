# Runbook: After a Game Update (P2.E7.S1)

1. **Detect:** the newest `logs/godot*.log` shows a new `release=vX.Y.Z`, or `tools/sts.py health` (STS2-Agent) reports a new `game_version`.
2. **Back up** saves first (`docs/runbooks/restore-saves.md`).
3. **Mod:** reinstall (and rebuild if the game's assemblies changed). See `docs/runbooks/mod-install.md`, "After a game update".
4. **Data:**
   - If STS2-Agent is available, export `/data/<collection>` to `knowledge/data/vX.Y.Z/`.
   - Otherwise re-import a newer decompiled extract with `tools/import_extract.py --src <path>` into a new dated folder (edit `OUT` in the script).
   - Diff against the previous export: cards, monsters, powers, relics.
5. **Mark stale:** every note or playbook rule that depends on a changed item gets `STALE (vX.Y.Z)` next to its label. Re-verify the high-impact ones first: boss plans, the elite table, card tiers.
6. **Benchmarks** are per version. Start a new benchmark file once enough runs exist on the new version. Never edit the old one.
7. Record the update in `docs/environment.md` and in the playbook changelog.
