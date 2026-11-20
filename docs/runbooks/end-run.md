# Runbook: End a Run (P4.E1.S6)

1. On `game_over`: read the final state (`tools/sts.py --mod sts2agent state --raw > runs/<run>/final-state.json`).
   - STS2-Agent: while `game_over.can_continue`, `act continue_game_over` (slow: it waits until the result is written to the save; do not repeat it after one timeout); when `game_over.save_verified` is true and `can_return_to_main_menu`, `act return_to_main_menu`. In co-op, `waiting_for_other_players` means wait.
   - STS2MCP: `menu_select option=main_menu`.
2. Copy the game's run file into the run folder. For the Agent's own runs it is the newest file in `~/Library/Application Support/SlayTheSpire2/steam/<id>/modded/profile2/saves/history/` (profile 2 is the Agent's; a shadowed Player run is in `modded/profile1`, so check the seed in the file name matches the run):
   ```bash
   cp "$(ls -t "$HOME/Library/Application Support/SlayTheSpire2/steam/"*/modded/profile2/saves/history/*.run | head -1)" runs/<run>/run.run
   ```
3. Generate the facts sheet: `python3 -I tools/postmortem.py runs/<run>/`. For a quick check of the fight log against the benchmark first: `python3 -I tools/journal.py summary runs/<run>`.
4. Write `runs/<run>/postmortem.md` from `templates/postmortem.md`: the three costliest decisions, proposed playbook changes (5 at most, each with evidence).
5. Append a scoreboard row to `metrics/scoreboard.csv` (columns in its header). In the notes, state the reload count: `tools/play_turn.py` warns during the run when the game's own counter (`num_reloads` in the in-progress save) is above 0; a scored run needs 0 (`docs/simulator-integrity.md` ML-6). Replays of the run's fights are kept by `tools/play_turn.py` in `data/sim/replays/<run>/` (not in git).
6. Apply accepted playbook changes: bump the version and add a changelog entry. Commit.
7. Rebuild the dataset so the run joins the analysis: `python3 -I tools/extract_runs.py && python3 -I tools/validate_data.py`.
8. Tell the Player in five lines: result, floor, cause of death, biggest mistake, playbook change. Send a push notification if they are away.
