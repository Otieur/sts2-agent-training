# Proposal: Make STS2-Agent's AI Teammate Launcher Work on macOS

Status: **proposal, not applied** (written 2026-11-19 overnight, for P6.E2.S2). Applies to vendor/STS2-Agent at commit `5d7c306`. Local modification of AGPL-3.0 code for private use; not distributed.

## Problems found in review
| # | File | Problem on macOS | Effect |
|---|---|---|---|
| 1 | `Multiplayer/CompanionProfileBootstrap.cs`, `DefaultUserRoot()` | Uses `Environment.SpecialFolder.ApplicationData`. On macOS .NET maps that to `~/.config`, but the game's data lives in `~/Library/Application Support/SlayTheSpire2` (Godot `user://`). | The teammate's `default/<clientId>/settings.save` (mods enabled, intro skipped, EA disclaimer seen) is written where the game never reads it. The second instance may start with mods disabled and first-run popups, so the mod (and its API) doesn't load. |
| 2 | `Multiplayer/LocalDualInstanceLauncher.cs`, `EnsureSteamAppIdFile()` | Writes `steam_appid.txt` next to the executable, which on macOS is inside the signed app bundle (`SlayTheSpire2.app/Contents/MacOS/`). | Changing a signed bundle can trip macOS code-signing checks. The companion runs with `--force-steam off`, so the file may not be needed at all. |
| 3 | `Multiplayer/LocalDualInstanceLauncher.cs`, `ResolveGameExe()` | The fallback path is Windows-only (`ProgramFilesX86/.../SlayTheSpire2.exe`). | Only matters if `OS.GetExecutablePath()` fails; on macOS it should return the bundle binary. |
| 4 | `Multiplayer/LocalDualInstanceLauncher.cs`, `StageWorkshopModForOfflineCompanion()` | Looks for a Workshop copy. | Not an issue when the mod is installed locally (flat DLL in `mods/`), because it keeps the local copy. |

## Proposed changes

### 1. Use the game's own user-data folder
```csharp
// Multiplayer/CompanionProfileBootstrap.cs
public static string DefaultUserRoot()
{
    try
    {
        // Godot's user:// for this game, the folder SaveManager writes (~/Library/Application Support/SlayTheSpire2 on macOS)
        var dir = Godot.OS.GetUserDataDir();
        if (!string.IsNullOrWhiteSpace(dir) && Directory.Exists(dir))
        {
            return dir;
        }
    }
    catch
    {
    }

    if (OperatingSystem.IsMacOS())
    {
        return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
            "Library", "Application Support", "SlayTheSpire2");
    }

    var root = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
    return Path.Combine(root, "SlayTheSpire2");
}
```
Check first: confirm that `Godot.OS.GetUserDataDir()` returns `~/Library/Application Support/SlayTheSpire2` inside the game. The mod already uses `user://` elsewhere (`GameStateService.Rooms.cs:812`, `CoopSaveProbe.cs:46`), so the call is available.

### 2. Don't write into the app bundle on macOS
```csharp
// Multiplayer/LocalDualInstanceLauncher.cs, in the launch path
if (!OperatingSystem.IsMacOS())
{
    try { EnsureSteamAppIdFile(exe); }
    catch (Exception ex) { Log.Warn($"{LogPrefix} steam_appid.txt: {ex.Message}"); }
}
```
If the companion then fails to start with Steam off, the alternative is a temporary working directory holding `steam_appid.txt` (`startInfo.WorkingDirectory = <temp dir>`), so the bundle stays untouched.

### 3. A macOS fallback for the executable
```csharp
// Multiplayer/LocalDualInstanceLauncher.cs, ResolveGameExe(), after the OS.GetExecutablePath() attempt
if (OperatingSystem.IsMacOS())
{
    var mac = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
        "Library", "Application Support", "Steam", "steamapps", "common", "Slay the Spire 2",
        "SlayTheSpire2.app", "Contents", "MacOS", "Slay the Spire 2");
    if (File.Exists(mac)) return mac;
}
```

## Test plan (P6.E2.S1–S3)
1. Back up saves.
2. Build with the patch; install it as in `docs/runbooks/mod-install.md` (Option B).
3. Main menu: F8 overlay → AI Teammate → Invite AI Teammate, with no model configured.
4. Check that:
   - a second window opens
   - `~/Library/Application Support/SlayTheSpire2/default/<clientId>/settings.save` exists with `mods_enabled: true`
   - the main window's `/health` shows `companion.api_port`
   - the teammate's `/health` answers
   - the teammate joins the lobby
5. Check `SlayTheSpire2.app/Contents/MacOS/` for new files. Expect only `mods/`, and no `steam_appid.txt` with patch 2.
6. Record CPU, memory and frame rate with both instances in a fight (P6.E2.S3).
7. If the launcher still fails: fall back to STS2MCP's localhost join with a manually started second instance (`"…/Slay the Spire 2" --force-steam off --clientId 2 -fastmp join`). That needs the companion settings file from step 4 written by hand, with mods enabled.
