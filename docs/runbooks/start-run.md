# Runbook: Start a Solo Run (P4.E1.S1)

1. **Check the mod:** `python3 -I tools/sts.py --mod sts2agent health` (STS2MCP: `--mod sts2mcp`). Once per session after a game update, run `python3 -I tools/smoke.py`. On failure, see `docs/runbooks/mod-install.md`, Verify.
2. **Keep the computer awake:** request keep-awake (host tool) for the session. The game window stays open; minimise it only if OQ0.5 showed no throttling.
3. **Choose the run:**
   - Character: Ironclad (Phase 4).
   - Ascension: from the ladder in `metrics/milestones.md` (start at A0; up one level after each win; review after 3 losses in a row).
   - Seed: an exam seed from `metrics/exam-seeds.md` when an exam replay is due, otherwise random.
4. **Create the run folder:** `runs/<YYYY-MM-DD>-<seed or 'random'>/` (the journal command below creates it).
   - Create the journal: `python3 -I tools/journal.py new --character IRONCLAD --ascension <n> --seed <seed> [--exam]`. It copies `templates/run-journal.md` and fills in the header, including the **playbook version** read from `playbooks/ironclad.md`.
   - Point the decision log there: every `tools/sts.py act` call uses `--log runs/<run>/decisions.jsonl`. Alternatively, symlink `runs/current` to the run folder.
5. **Start the run through the menu actions.**
   - STS2-Agent: `act open_character_select`; read `character_select.characters[]` from the state and `act select_character option_index=<Ironclad's index>`; raise or lower the ascension with `act increase_ascension` / `act decrease_ascension` until the state shows the target level; then `act embark`. Every action needs `--reason`.
   - **Seeds:** STS2-Agent shows `character_select.seed` but has no action to set one. For an exam seed, ask the Player to type it in the game's seeded or custom run screen, then continue from the Ancient. STS2MCP documents `seed=` on `menu_select`, but its README warns the standard mode may reject it (OQ0.6).
   - STS2MCP: `menu_select` with the options shown by `tools/sts.py --mod sts2mcp state`.
6. **Tell the Player in one line:** "Starting run: Ironclad A<n>, seed <s>, playbook v<x>."
7. **Floor 1 (the Ancient):** read the act boss (`run.boss_id` on STS2-Agent, known from the first floor; `map.boss` on STS2MCP). Open `knowledge/bosses/<BOSS>.md` and write the act plan into the journal (P4.E3.S1): `python3 -I tools/path.py --state <state.json>` for the route, `python3 -I tools/deck_check.py --state <state.json>` for the deck's gaps against the corner targets and the boss checklist (P4.E3.S4). Repeat the deck check before the boss.
8. Play using `docs/runbooks/decision-loop.md`. Keep `playbooks/ironclad-quickref.md` in context; open the full playbook section only when a decision needs it.
