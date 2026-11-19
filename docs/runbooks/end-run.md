# Runbook: End a Run (P4.E1.S6)

1. On `game_over`: read the final state (`tools/sts.py state --raw > runs/<run>/final-state.json`), then `menu_select option=main_menu`.
2. Copy the game's run file into the run folder. It is the newest file in `~/Library/Application Support/SlayTheSpire2/steam/<id>/modded/profile1/saves/history/` (the modded profile while mods are on):
   ```bash
   cp "$(ls -t "$HOME/Library/Application Support/SlayTheSpire2/steam/"*/modded/profile1/saves/history/*.run | head -1)" runs/<run>/run.run
   ```
3. Generate the facts sheet: `python3 -I tools/postmortem.py runs/<run>/`
4. Write `runs/<run>/postmortem.md` from `templates/postmortem.md`: the three costliest decisions, proposed playbook changes (5 at most, each with evidence).
5. Append a scoreboard row to `metrics/scoreboard.csv` (columns in its header).
6. Apply accepted playbook changes: bump the version and add a changelog entry. Commit.
7. Rebuild the dataset so the run joins the analysis: `python3 -I tools/extract_runs.py && python3 -I tools/validate_data.py`.
8. Tell the Player in five lines: result, floor, cause of death, biggest mistake, playbook change. Send a push notification if they are away.
