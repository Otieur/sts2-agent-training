# Runbook: Build and Install the Mod (macOS, arm64)

**Prerequisites:**
1. The Player approved the security review (`docs/reviews/sts2-agent-security-review.md`).
2. A fresh backup exists (`docs/runbooks/restore-saves.md`).
3. The game is on the intended branch.

Decision record 0001 (revised 2026-11-19) proposes **STS2-Agent first** (Option B), since main is now v0.111.1, the version its docs reference. STS2MCP (Option A) is the fallback: it needs no SDK install but was last fixed for v0.107.

Game paths:
```bash
GAME_DIR="$HOME/Library/Application Support/Steam/steamapps/common/Slay the Spire 2"
MODS_DIR="$GAME_DIR/SlayTheSpire2.app/Contents/MacOS/mods"
```

---

## Option A: STS2MCP (reviewed commit 55e0648)

### Build
The project targets `net9.0`. The installed .NET 10 SDK should build it (to confirm). If it doesn't, the README's route is `brew install dotnet@9` (Player approval needed before installing).
```bash
cd vendor/STS2MCP
git rev-parse HEAD          # must be 55e064850a68f3b4cde7e5fd525bf9b2dec4e885 (the reviewed commit)
dotnet build STS2_MCP.csproj -c Release -o out/STS2_MCP -p:STS2GameDir="$GAME_DIR" 2>&1 | tee ../../logs/build-sts2mcp-$(date +%F).txt
```
The csproj detects macOS and uses `SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64` automatically.

### Install
The game must be closed.
```bash
mkdir -p "$MODS_DIR"
cp vendor/STS2MCP/out/STS2_MCP/STS2_MCP.dll "$MODS_DIR/"
cp vendor/STS2MCP/mod_manifest.json "$MODS_DIR/STS2_MCP.json"   # the manifest name must match the mod ID
shasum -a 256 "$MODS_DIR"/STS2_MCP.* | tee -a logs/mod-install-manifest.txt
```

### Enable (Player)
1. Launch the game. Accept the mod consent dialog and enable the mod in settings.
2. Quit fully and relaunch.
3. The game now uses the modded profile.

### Verify
```bash
curl -s http://localhost:15526/ ; echo
python3 -I tools/sts.py --mod sts2mcp health
python3 -I tools/sts.py --mod sts2mcp state
```
Then check the newest `~/Library/Application Support/SlayTheSpire2/logs/godot*.log` for `[STS2 MCP] ... server started` and no exceptions.

### Uninstall
```bash
rm "$MODS_DIR/STS2_MCP.dll" "$MODS_DIR/STS2_MCP.json"
```
Disable mods in the game settings if asked.

---

## Option B: STS2-Agent (reviewed commit 5d7c306)

### Installed 2026-11-19 11:56 (what was actually run)
The Player approved the security review and the .NET 9 SDK install. The game was closed and the saves matched the backup `backups/2026-11-19-pre-phase0/` (rsync dry run, no differences).
```bash
brew install dotnet@9                       # 9.0.124, keg-only
export DOTNET_ROOT=/opt/homebrew/opt/dotnet@9/libexec PATH=/opt/homebrew/opt/dotnet@9/bin:$PATH
DATA="$GAME_DIR/SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64"
cd vendor/STS2-Agent && git rev-parse HEAD   # 5d7c3061581bfd4382d6255cb39e18b19a40d3dc
dotnet build STS2AIAgent/STS2AIAgent.csproj -c Release "/p:Sts2DataDir=$DATA"   # 0 warnings, 0 errors
mkdir -p "$MODS_DIR"
cp STS2AIAgent/bin/Release/net9.0/STS2AIAgent.dll "$MODS_DIR/"
# mod_id.json copied with "has_pck" set to false (see the note below)
```
| File in `$MODS_DIR` | SHA-256 |
|---|---|
| `STS2AIAgent.dll` | `684e134cf233c1b3bbe0ed149a7060b846cd59f262b7e9927507d80f5d35ff69` |
| `mod_id.json` | `dfd767bbc7d41a100aeb22a84793bd88fb3c7a23e2f3abaed14b5b433cb40343` |

**Why no PCK.** `scripts/build-mod.sh` packs `mod_manifest.json` into `STS2AIAgent.pck` by running the game's own executable headless. A Godot export can load its own embedded game data even when given another project path, which could start the game's code against the real save folder and Steam. The PCK only repeats the manifest, the game's loader reads manifests from the JSON files in the mods folder, and it loads a mod with only a DLL (STS2MCP ships with `has_pck: false`). So the installed `mod_id.json` sets `has_pck` to false. If the game refuses the mod for the missing PCK, build the PCK with a standalone Godot editor of the game's engine version (a download that needs the Player's approval) and set `has_pck` back to true.

**Uninstall:** with the game closed, `rm "$MODS_DIR/STS2AIAgent.dll" "$MODS_DIR/mod_id.json"`, or start the game with `nomods` (the loader honours it).


### Build
Needs a .NET 9 SDK: `global.json` pins 9.0.x and only .NET 10.0.101 is installed. Installing one needs the Player's approval.
```bash
cd vendor/STS2-Agent
git rev-parse HEAD          # must be 5d7c3061581bfd4382d6255cb39e18b19a40d3dc
cat > STS2AIAgent/local.props <<'XML'
<Project><PropertyGroup>
  <Sts2DataDir>$(HOME)/Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64</Sts2DataDir>
</PropertyGroup></Project>
XML
./scripts/build-mod.sh --configuration Release 2>&1 | tee ../../logs/build-sts2agent-$(date +%F).txt
```

### Install
Copy only `STS2AIAgent.dll`, `STS2AIAgent.pck` and `mod_id.json` into `$MODS_DIR`. Don't install both mods at once until each has been tested alone.

### Verify
```bash
curl -s http://127.0.0.1:8080/health ; echo      # the port may differ; check the F8 overlay
python3 -I tools/sts.py --mod sts2agent health
```

### Conditions from the review
- Configure **no** LLM model or API key in the F8 overlay.
- Do not set `STS2_ENABLE_DEBUG_ACTIONS`.
- The AI-teammate launcher needs a macOS patch before co-op (Phase 6, P6.E2.S2).

---

## After a game update
Steam updates and "Verify integrity of game files" can remove files inside the app bundle. Rerun the Install step (and rebuild if the game's assemblies changed). Then repeat Verify.
