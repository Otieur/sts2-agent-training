#!/bin/sh
# Runs the simulator host in its sandbox: HOME points at an empty folder so nothing can reach the real saves
# (docs/simulator-integrity.md SA-1), and the game's assemblies are read from the install folder.
# Usage: sim/run.sh <stage> [args]
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REAL_HOME="$HOME"
export STS2_DATA_DIR="${STS2_DATA_DIR:-$REAL_HOME/Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64}"
export DOTNET_ROOT="${DOTNET_ROOT:-/opt/homebrew/opt/dotnet@9/libexec}"
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 DOTNET_gcServer=0
export SIM_UI_TYPES="$ROOT/data/asm/ui-types-from-logic.json" SIM_TESTPATH="$ROOT/data/asm/testpath-methods.json"
SANDBOX="$ROOT/data/sim/sandbox-home"
mkdir -p "$SANDBOX"
HOME="$SANDBOX" exec "$DOTNET_ROOT/dotnet" "$ROOT/sim/bin/Release/net9.0/SimHost.dll" "$@"
