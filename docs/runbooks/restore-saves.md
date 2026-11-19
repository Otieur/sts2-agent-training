# Runbook: Back Up and Restore the Game Saves

Save folder: `~/Library/Application Support/SlayTheSpire2/` (profiles, modded profile, backup profile, settings, logs).
Backups: `backups/<YYYY-MM-DD>-<label>/SlayTheSpire2/` with a `MANIFEST.sha256` beside it. The `backups/` folder is not in git.

Existing backups:
- `backups/2026-11-19-pre-profile2/`: taken 2026-11-19 with the game open at the main menu (profile 1), before seeding profile 2. 1,110 files; only the live log differed afterwards.
- `backups/2026-11-19-pre-phase0/`: taken 2026-11-19 00:53 with the game closed, on the **beta branch (v0.113.1)**, before any branch switch or mod install. 1,104 files, 53,175,099 bytes (shader and Vulkan caches excluded). A dry-run restore showed no differences. Checked again 2026-11-19 11:44, after the switch to main v0.111.1 and before any launch: still no differences, so it is also the backup for the main branch until the game is launched.

## Take a backup
1. Close the game completely. `pgrep -fl "Slay the Spire 2"` must print nothing.
2. Run:
   ```bash
   S="$HOME/Library/Application Support/SlayTheSpire2"
   B="backups/$(date +%F)-<label>/SlayTheSpire2"
   mkdir -p "$B" && rsync -a --exclude shader_cache --exclude vulkan "$S/" "$B/"
   (cd "$B" && find . -type f -print0 | sort -z | xargs -0 shasum -a 256 > ../MANIFEST.sha256)
   ```
3. Check that the file count and byte total of `$B` match the source (commands in `docs/overnight-log.md`, Block "P0.E1").

## Restore
1. Close the game completely, then quit Steam too, so Steam Cloud can't sync during the restore.
2. Preview what will change (nothing is modified):
   ```bash
   rsync -an --delete --exclude shader_cache --exclude vulkan "backups/<backup>/SlayTheSpire2/" "$HOME/Library/Application Support/SlayTheSpire2/"
   ```
3. Restore for real (the same command without `-n`):
   ```bash
   rsync -a --delete --exclude shader_cache --exclude vulkan "backups/<backup>/SlayTheSpire2/" "$HOME/Library/Application Support/SlayTheSpire2/"
   ```
4. Verify the checksums:
   ```bash
   (cd "$HOME/Library/Application Support/SlayTheSpire2" && shasum -a 256 -c "$OLDPWD/backups/<backup>/MANIFEST.sha256" | grep -v ': OK$')
   ```
   No output means every file matches.
5. Start Steam. If Steam shows a **cloud conflict** dialog for Slay the Spire 2, choose the **local** files.
6. Launch the game and check that the profile shows the expected unlocks and run history.

## Notes
- The beta wrote save schema `SerializableProgress v24`. The main branch may not read newer files. If the profile looks reset after a branch switch, restore this backup and switch back to the beta.
- The mod's modded profile (`steam/<id>/modded/profile1`) is separate from the main profile. Mod testing does not touch main-profile progress.
- Steam Cloud setting: to be confirmed by the Player (OQ0.4).
