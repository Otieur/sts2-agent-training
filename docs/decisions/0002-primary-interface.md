# 0002: Primary interface to the game

Date: 2026-11-19 · Status: **accepted** (Agent decision within the approved plan; revisit if the CLI becomes a bottleneck)

## Context
STS2-Agent offers an HTTP API and an optional MCP server (enabled from the in-game overlay). The project's own CLI, `tools/sts.py`, wraps the HTTP API, and `tools/advise.py --live` turns a state into advice in one command.

## Options
1. **CLI over HTTP** (`tools/sts.py`, `tools/advise.py`): standard library only; every action carries a decision reason and is logged to a JSONL file; compact text views keep each decision small. Tested live on 2026-11-19 (health, state, one card, one full fight).
2. **MCP server**: bundled tools (`decide`, `wait_until_actionable`, game data lookups). Needs the overlay setting, a sidecar process (`uv run`), and an entry in `.mcp.json`; full states are large in context.
3. **Mix**: CLI for actions and advice, MCP for occasional lookups.

## Decision
**CLI over HTTP is the primary interface.** MCP stays disabled. It adds a process and a permission surface without a need the CLI does not already cover; its game-data lookups are covered by the extract and the knowledge files.

## Consequences
- Live play follows `docs/runbooks/decision-loop.md` with `tools/advise.py --live` and `tools/sts.py act`.
- P0.E6.S2 (MCP connection) is closed without enabling MCP. Revisit if a decision needs data the HTTP state lacks.
