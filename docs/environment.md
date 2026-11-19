# Environment

Drafted 2026-11-19 (overnight). Items marked "to confirm" need the Player or a game launch.

## Machine
| Item | Value |
|---|---|
| OS | macOS 15.6 (build 24G84) |
| CPU | Apple Silicon (arm64) |
| Python | 3.13.12 (miniforge). Analysis scripts use the standard library only; run with `python3 -I`. |
| uv | 0.11.16 (Homebrew) |
| .NET SDK | **10.0.101 only** (`/usr/local/share/dotnet/sdk`). No .NET 9 SDK installed. |
| git | 2.54.0 |

## Game
| Item | Value |
|---|---|
| Install | `~/Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app` |
| Executable | `SlayTheSpire2.app/Contents/MacOS/Slay the Spire 2` |
| Game assemblies (arm64) | `SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64/` (`sts2.dll`, `GodotSharp.dll`, `0Harmony.dll`) |
| Steam app ID | 2868840 |
| Branch / version | **Main branch (`public`), v0.111.1** since 2026-11-19 (app `release_info.json`: commit cc1f9462, built 2026-11-13; Steam build 26655341). Was `public-beta`, v0.113.1, until then. |
| Save data | `~/Library/Application Support/SlayTheSpire2/` (`steam/<id>/profile1`, `steam/<id>/modded/profile1`, `steam/back_prof1`, `logs/`, `mods/config/`) |
| Logs | `~/Library/Application Support/SlayTheSpire2/logs/godot*.log` (contains `release=vX.Y.Z` and save schema versions) |
| Acts seen in v0.107.1 data | Act 1: `ACT.OVERGROWTH` or `ACT.UNDERDOCKS`; Act 2: `ACT.HIVE`; Act 3: `ACT.GLORY` |

## Mods folder (macOS)
- STS2MCP documents `SlayTheSpire2.app/Contents/MacOS/mods/` (create it). The manifest must be named after the mod ID (for example `STS2_MCP.json`).
- `~/Library/Application Support/SlayTheSpire2/mods/config/` also exists. Which folder the game actually scans should be confirmed from the log on first launch with a mod (P0.E4.S3).
- Note: files inside the app bundle may be removed by a Steam update or "Verify integrity". Reinstall after updates.

## Mod candidates (source in `vendor/`, not in git)
| Mod | Commit | Build requirements on this Mac | Port |
|---|---|---|---|
| STS2MCP | `55e0648` (2026-07-29, v0.107 compatibility fix) | `net9.0` target, no `global.json`. The csproj detects macOS and finds `data_sts2_macos_arm64` from `-p:STS2GameDir=...`. The installed .NET 10 SDK should be able to build a `net9.0` target (to confirm). The README suggests `brew install dotnet@9` if not. | 15526 (config file `port`) |
| STS2-Agent | `5d7c306` (2026-10-23) | `global.json` pins SDK 9.0.x (`rollForward: latestFeature`), so **a .NET 9 SDK must be installed** (Player approval needed). Set `Sts2DataDir` to the macOS arm64 data folder via `local.props` or `STS2_DATA_DIR`. | 8080 by default, increments if busy; `STS2_API_PORT` |

## Ports in use by the game and mods
- 15526: STS2MCP HTTP API
- 8080 (and up): STS2-Agent HTTP API
- 33771: the game's local direct-connect port for multiplayer (`-fastmp`)

## To confirm
- [x] Game version after the branch switch: v0.111.1 from `release_info.json` (the log line `release=` comes at first launch)
- [ ] Which mods folder the game scans
- [ ] Whether the .NET 10 SDK builds STS2MCP's `net9.0` target
- [ ] Whether the game throttles when unfocused (OQ0.5)
- [x] Steam Cloud setting for this game (OQ0.4): on
