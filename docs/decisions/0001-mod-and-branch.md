# 0001: Which mod to start with, on which branch

Date: 2026-11-19 · Status: **accepted** (drafted overnight, revised at 01:15 when the main-branch update was found; the Player chose STS2-Agent on 2026-11-19 at about 11:44. The Player approved the security review and the .NET 9 SDK install at 11:51)

## Context
The Agent needs a mod that exposes game state and accepts actions on macOS arm64. Two open-source candidates were reviewed read-only (`docs/reviews/sts2-agent-security-review.md`).

**New fact (found 2026-11-19 01:12):** the main branch moved from v0.107.1 to **v0.111.1** on 2026-11-16/17 (`knowledge/version-delta-v0.111.1.md`). Switching Steam off the beta now installs v0.111.1. The Player's history is from v0.107.1.

## Options considered
1. **STS2-Agent first** (main branch v0.111.1)
   - Pros:
     - Its docs reference game v0.111.0, the base of the new main.
     - The richest API: decision log with reasons, event stream, `action_readiness`, `lethal_risks`, `/data` export.
     - The co-op teammate feature.
     - Latest commit 2026-10-23.
   - Cons:
     - Needs a .NET 9 SDK (`global.json` pins 9.0.x; only .NET 10 is installed), so an install needs the Player's approval.
     - The teammate launcher needs macOS fixes (`docs/proposals/sts2-agent-macos-teammate.md`), but solo play doesn't use it.
2. **STS2MCP first** (main branch v0.111.1)
   - Pros:
     - Documented macOS install.
     - The csproj detects macOS; no `global.json`, so the .NET 10 SDK may build it.
     - Small codebase.
   - Cons:
     - Its latest commit (2026-07-29) is a fix for **v0.107**. Compatibility with v0.111.1 is unknown.
     - Thinner API.
     - A dangerous profile-delete endpoint, which the CLI blocks.
3. **Stay on the beta (v0.113.1)**
   - Cons: neither mod targets it; the Player chose the tested versions.

## Decision (accepted 2026-11-19)
**Option 1: STS2-Agent on main v0.111.1**, the best version match. Install the .NET 9 SDK (Homebrew `dotnet@9`, Player approval). Keep **STS2MCP as the fallback**. It builds without installing anything, so if the .NET 9 install is a problem, try it first and see whether it still loads on v0.111.1.

`tools/sts.py` already supports both (`--mod sts2agent` / `--mod sts2mcp`), and `tools/advise.py` reads either format (`tools/mcp_adapter.py` converts STS2MCP states), so switching later only changes a flag. With STS2MCP the deck is rebuilt from combat piles, and the turn planner has no `end_turn_will_kill_player` check.

## Results (2026-11-19)
- STS2-Agent 0.16.2 built against v0.111.1 with 0 warnings, loaded on the first modded launch, and reported 28 of 28 reflected game members.
- The smoke test passed on every screen met in two runs; one card and one full fight were played through the API; the event stream was probed.
- The fallback (STS2MCP, P0.E7.S1) and a branch switch (P0.E7.S2) were not needed.

## Consequences
- The Agent plays on v0.111.1 while the Player's benchmarks come from v0.107.1. Compare cautiously: changed cards and enemies are flagged in `knowledge/version-delta-v0.111.1.md`. Start v0.111.1 benchmarks once there are enough runs.
- Exam seeds may need replacing (seeds are 12 characters on v0.111.1).
- Revisit if STS2-Agent fails to build or load, or if the .NET 9 install is declined.
