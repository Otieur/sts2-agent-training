# Runbook: Start a Solo Run (P4.E1.S1)

1. **Check the mod:** `python3 -I tools/sts.py health`. On failure, see `docs/runbooks/mod-install.md`, Verify.
2. **Keep the computer awake:** request keep-awake (host tool) for the session. The game window stays open; minimise it only if OQ0.5 showed no throttling.
3. **Choose the run:**
   - Character: Ironclad (Phase 4).
   - Ascension: from the ladder in `metrics/milestones.md` (start at A0; up one level after each win; review after 3 losses in a row).
   - Seed: an exam seed from `metrics/exam-seeds.md` when an exam replay is due, otherwise random.
4. **Create the run folder:** `runs/<YYYY-MM-DD>-<seed or 'random'>/` (the journal command below creates it).
   - Create the journal: `python3 -I tools/journal.py new --character IRONCLAD --ascension <n> --seed <seed> [--exam]`. It copies `templates/run-journal.md` and fills in the header, including the **playbook version** read from `playbooks/ironclad.md`.
   - Point the decision log there: every `tools/sts.py act` call uses `--log runs/<run>/decisions.jsonl`. Alternatively, symlink `runs/current` to the run folder.
5. **Start the run through the menu actions** (STS2MCP: `menu_select` with the options shown by `tools/sts.py state`, plus `seed=` where supported).
6. **Tell the Player in one line:** "Starting run: Ironclad A<n>, seed <s>, playbook v<x>."
7. **Floor 1 (the Ancient):** read the act boss from the map state as soon as the map is visible (`map.boss`). Open `knowledge/bosses/<BOSS>.md` and write the act plan into the journal (P4.E3.S1): `python3 -I tools/path.py --state <state.json>` for the route, `python3 -I tools/deck_check.py --state <state.json>` for the deck's gaps against the corner targets and the boss checklist (P4.E3.S4). Repeat the deck check before the boss.
8. Play using `docs/runbooks/decision-loop.md`. Keep `playbooks/ironclad-quickref.md` in context; open the full playbook section only when a decision needs it.
