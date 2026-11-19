# Security Review: STS2-Agent and STS2MCP

**Verdict: DRAFT. Needs the Player's approval before anything is built or installed.**

Reviewed 2026-11-19 (overnight, read-only). No code was built, installed or run.

| Mod | Repository | Commit reviewed | Commit date | License |
|---|---|---|---|---|
| STS2-Agent (primary candidate) | https://github.com/Meddrin/STS2-Agent | `5d7c3061581bfd4382d6255cb39e18b19a40d3dc` | 2026-10-23 | AGPL-3.0 |
| STS2MCP (fallback candidate) | https://github.com/Gennadiyev/STS2MCP | `55e064850a68f3b4cde7e5fd525bf9b2dec4e885` | 2026-07-29 ("Fix game API compatibility with STS2 v0.107") | MIT |

Method: a targeted read of the C# sources (175 files, about 47.7k lines for STS2-Agent excluding tests; about 8.9k lines for STS2MCP). The review searched for network listeners, outbound HTTP, process launches, file writes, game patches, debug gates and telemetry, then read each hit in context. This is not a line-by-line audit of every file.

---

## STS2-Agent

### 1. Network listeners: loopback only ✅
- `Server/LoopbackListener.cs:102` binds `http://127.0.0.1:{port}/` only. `Server/HttpServer.cs:9-10` sets the default host to `127.0.0.1` and the port to 8080.
- If the port is taken it increments, unless `STS2_API_PORT` is set explicitly (`HttpServer.cs:44-46`).
- `Server/LoopbackListener.cs:115` binds a TCP listener to `IPAddress.Loopback` port 0, only to pick a free port.
- No `0.0.0.0`, `+` or `*` prefixes were found.
- `/session/control` accepts loopback requests only (`local_only` error, docs/api.md). The native MCP endpoint checks `Origin` (`origin_not_allowed`).

### 2. Outbound network calls: only for optional LLM autoplay, plus localhost ✅ with a condition
- `Llm/OpenAiCompatibleClient.cs:34-41,233` and `Llm/JevClient.cs:233`: HTTP clients for LLM providers. They are used only when an autoplay model or the "Jev" planner is configured with a base URL and API key (`Config/AgentSettings.cs:97,110,362`).
- Every other HTTP client targets `127.0.0.1`: `Multiplayer/CompanionConnection.cs:65,71,115,143` (the main window talking to the teammate instance), `Agent/McpProcessLauncher.cs:275` (sidecar health check) and `Multiplayer/LocalDualInstanceLauncher.cs:365`.
- **Condition:** do not configure any model, base URL or API key in the F8 overlay. The project uses the external-agent route (the agent harness drives the game), so no LLM key is needed in the mod.
- Note: if a key were configured, it would be stored in plain JSON in the settings file (`Config/SettingsStore.cs:35-53`).

### 3. Process launching: two launchers, both started only from the overlay ⚠️
1. **AI-teammate launcher** (`Multiplayer/LocalDualInstanceLauncher.cs:278-306`). It starts a second copy of the game executable with `--windowed --force-steam off --clientId <n> -fastmp join` (`Multiplayer/CoopLaunchPolicy.cs:22`). It passes environment variables for port, role, host IP `127.0.0.1`, net ID, an autoplay flag (0 unless configured), a settings path, the parent PID (the teammate exits when the host exits) and a session token. It runs only when the Player presses "Invite AI Teammate".
2. **MCP sidecar launcher** (`Agent/McpProcessLauncher.cs:119-135`). It runs `uv run sts2-network-mcp-server --host 127.0.0.1 --port <p> --path /mcp --api-base-url <api>` in the repository's `mcp_server` folder. It runs only when "Open MCP service" is enabled, and that Python server also binds `127.0.0.1`.

### 4. File writes ⚠️ (one write into the game's app bundle)
| Code | Writes | Concern |
|---|---|---|
| `Config/SettingsStore.cs` | `<ApplicationData>/STS2AIAgent/settings.json` | None. On macOS, .NET's ApplicationData is usually `~/.config`, so the file lands at `~/.config/STS2AIAgent/settings.json`. |
| `Agent/PlaySessionStore.cs` | `.../STS2AIAgent/sessions/*.json` | None |
| `Agent/DecisionLog.cs:209-217` | decision log (append, rotates to `.previous`) | None |
| `Server/CompanionPortFile.cs` | `<temp>/sts2-ai-agent-companion-<pid>.port` | None |
| `Multiplayer/CoopLaunchPolicy.cs:90-93` | copies the settings file for the teammate | None |
| `Multiplayer/CompanionProfileBootstrap.cs:68-111` | writes `<ApplicationData>/SlayTheSpire2/default/<clientId>/settings.save` for the teammate | **macOS mismatch:** the game's real data folder is `~/Library/Application Support/SlayTheSpire2`, not ApplicationData (`~/.config`). The teammate's settings will probably be written where the game never reads them. |
| `Multiplayer/LocalDualInstanceLauncher.cs:154-166` | `steam_appid.txt` next to the game executable, if missing | **On macOS this is inside the signed app bundle** (`SlayTheSpire2.app/Contents/MacOS/`). Adding files to a signed bundle can upset macOS code-signing checks. STS2MCP's documented install also puts a `mods/` folder there, so the game presumably tolerates it, but it is untested. |

- `Game/ProgressSaveVerification.cs:59` opens the progress save **read-only** (`FileAccess.Read`) to confirm the game's own save succeeded. No writes to save files were found.

### 5. Game patches: none applied ✅
- The project references `0Harmony.dll` (`STS2AIAgent.csproj:22`), but no `[HarmonyPatch]` attributes or `new Harmony` calls exist in the mod sources. The mod drives the game through its own services from `[ModInitializer]` (`ModEntry.cs:14-32`).

### 6. Debug and console features: gated ✅
- `run_console_command` and `inject_event_churn` refuse unless `STS2_ENABLE_DEBUG_ACTIONS=1` (`Game/GameActionService.Menus.cs:240,273,284`). Do not set that variable.

### 7. Telemetry: none found ✅
- No analytics, telemetry or crash-reporting client in the mod sources. The game itself initializes Sentry; that is the game's own, not the mod's.

### 8. macOS readiness: not ready for the AI teammate ⚠️
- `LocalDualInstanceLauncher.ResolveGameExe()` first uses `OS.GetExecutablePath()`, which on macOS should return `.../SlayTheSpire2.app/Contents/MacOS/Slay the Spire 2`, so the launch itself may work. Its fallback path is Windows-only (`ProgramFilesX86`).
- The teammate profile bootstrap uses the wrong folder on macOS (item 4).
- The project's own status page notes the AI teammate was "BLOCKED in the Steam-off environment" during its v0.16.0 validation (`PRODUCT_PLAN_CURRENT.md:2`).
- The default build references `data_sts2_windows_x86_64`. On this Mac, `Sts2DataDir` must point to `SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64`, via `local.props` or `STS2_DATA_DIR`. The machine is arm64.
- The required SDK is .NET 9.0.100 with `rollForward: latestFeature` inside 9.0 (`global.json`). See `docs/environment.md` for what is installed.

### Verdict (draft)
**Go with conditions** for solo play:
1. Build from this reviewed commit with `Sts2DataDir` set to the macOS arm64 data folder.
2. Configure no LLM model or API key. Use the external-agent route only.
3. Do not set `STS2_ENABLE_DEBUG_ACTIONS`.
4. Back up saves first (P0.E1).

**AI-teammate co-op: not ready on macOS** without a patch to `CompanionProfileBootstrap.DefaultUserRoot()`, plus a live test of the launcher. Phase 6 (P6.E2.S2) covers this.

---

## STS2MCP

### Findings
- **Listeners:** `McpMod.cs:94-96` adds prefixes `http://localhost:{port}/` and `http://127.0.0.1:{port}/`. Loopback only ✅
- **Outbound calls:** none in the C# mod ✅. The optional Python MCP server (`mcp/server.py`) uses `httpx` to call the mod's localhost API.
- **Process launching:** none ✅
- **File writes:** `McpMod.cs:52` writes the mod's own config file ✅
- **Game patches:** Harmony patches on the settings screen and the Fast Mode toggle (`McpMod.SettingsUI.cs:83-139`), to add its settings UI. They do not touch saving or loading ✅
- **Risky endpoint:** `POST /api/v1/profiles` with `action: delete` calls the game's `DeleteProfile` (`McpMod.Profile.cs:171-176`). It refuses the active profile, but it can delete another save profile. **Rule: never call it.** The project CLI must refuse it.
- **Version:** the latest commit is an explicit compatibility fix for STS2 v0.107. Its README documents the macOS mods folder (`SlayTheSpire2.app/Contents/MacOS/mods/`) and says the same DLL works on all platforms.

### Verdict (draft)
**Go with conditions** for solo play: never call the profile-delete endpoint, and back up saves first. Its co-op support is a localhost join with a manually launched second instance (`-fastmp`, port 33771). That is a possible fallback for Phase 6.

---

## Recommendation for decision record 0001 (proposed, not taken)

STS2MCP has an explicit v0.107 compatibility fix and documented macOS install steps. STS2-Agent's docs reference v0.111 beta, and its teammate launcher needs macOS fixes. So the proposal: **try STS2MCP first for solo play on v0.107.1** (Phase 0 smoke tests and Phase 4), and keep STS2-Agent for its richer API and the co-op teammate, to be patched and tested in Phase 6. The Player decides.
