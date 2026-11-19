# 0001: Which mod to start with, on which branch

Date: 2026-11-19 · Status: **proposed** (drafted overnight; the Player decides)

## Context
The Agent needs a mod that exposes game state and accepts actions on game v0.107.1 (main branch), on macOS arm64. Two open-source candidates were reviewed read-only (`docs/reviews/sts2-agent-security-review.md`).

## Options considered
1. **STS2MCP first (solo), STS2-Agent later (co-op).**
   - Pros: explicit v0.107 compatibility fix (latest commit). Documented macOS install. The csproj auto-detects the macOS data folder. No `global.json`, so the installed .NET 10 SDK may build its `net9.0` target without installing anything. Small codebase (about 8.9k lines), which keeps the review tractable. Loopback only, no outbound calls, no process launching.
   - Cons: thinner API than STS2-Agent (no decision log with reasons, no event stream). One dangerous endpoint (profile delete) that the CLI must block. Co-op only through a manually launched second instance.
2. **STS2-Agent for everything.**
   - Pros: richest API (decision log, SSE events, `action_readiness`, `lethal_risks`, `/data` export), a bundled gameplay skill, the AI-teammate feature.
   - Cons: docs reference v0.111 beta, so v0.107.1 compatibility is unknown. Needs a .NET 9 SDK installed (`global.json` pin). The teammate launcher has macOS problems: it writes the profile seed to the wrong folder and puts `steam_appid.txt` inside the app bundle. Its own status page records the teammate as blocked with Steam off during validation.
3. **Switch the game to whatever branch STS2-Agent targets.**
   - Cons: the beta has moved to v0.113.1, so the build STS2-Agent was validated on (v0.111) is no longer offered. It also breaks the match with the Player's v0.107.1 history.

## Decision (proposed)
Option 1. Smoke-test STS2MCP on v0.107.1 first. If it works, Phase 3 and Phase 4 run on it, with a thin `tools/sts.py` adapter. Revisit STS2-Agent for Phase 6 co-op, with a local patch for the macOS teammate issues.

## Consequences
- `tools/sts.py` should target an adapter interface, so switching mods later only changes the adapter.
- The decision log with reasons is kept by our own tooling (`runs/<run>/decisions.jsonl`) instead of the mod's.
- Revisit if STS2MCP fails to load on v0.107.1, or if its API cannot express a needed action.
