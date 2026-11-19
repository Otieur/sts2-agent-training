# Runbook: Start a Solo Run (P4.E1.S1)

1. **Check the mod:** `python3 -I tools/sts.py health`. On failure, see `docs/runbooks/mod-install.md`, Verify.
2. **Keep the computer awake:** request keep-awake (host tool) for the session. The game window stays open; minimise it only if OQ0.5 showed no throttling.
3. **Choose the run:**
   - Character: Ironclad (Phase 4).
   - Ascension: from the ladder in `metrics/milestones.md` (start at A0; up one level after each win; review after 3 losses in a row).
   - Seed: an exam seed from `metrics/exam-seeds.md` when an exam replay is due, otherwise random.
4. **Create the run folder:** `runs/<YYYY-MM-DD>-<seed or 'random'>/`.
   - Copy `templates/run-journal.md` to `journal.md`. Fill in the header: character, ascension, seed, **playbook version** (from `playbooks/ironclad.md`).
   - Point the decision log there: every `tools/sts.py act` call uses `--log runs/<run>/decisions.jsonl`. Alternatively, symlink `runs/current` to the run folder.
5. **Start the run through the menu actions** (STS2MCP: `menu_select` with the options shown by `tools/sts.py state`, plus `seed=` where supported).
6. **Tell the Player in one line:** "Starting run: Ironclad A<n>, seed <s>, playbook v<x>."
7. **Floor 1 (the Ancient):** read the act boss from the map state as soon as the map is visible (`map.boss`). Open `knowledge/bosses/<BOSS>.md` and write the act plan into the journal (P4.E3.S1).
8. Play using `docs/runbooks/decision-loop.md`.
