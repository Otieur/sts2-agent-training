# Exam Seeds (P4.E5.S2)

**Warning (2026-11-19 01:15):** main is now v0.111.1, where seeds are 12 characters long. These 10-character v0.107.1 seeds may be rejected or generate different maps. Test one first; if it fails, choose new exam seeds from the first v0.111.1 runs.

Five seeds from the Player's Ironclad history (v0.107.1), chosen 2026-11-19: 2 wins and 3 losses, covering the three most common Ironclad killers and both Act 1 variants. Each is replayed at the Player's original ascension, so results compare directly with the Player's.

| # | Seed | Ascension | Act 1 | The Player's result | Why it is in the set |
|---|---|---|---|---|---|
| 1 | `9WHJYMRG9F` | A0 | Overgrowth | Died on floor 17 to **Vantom** | Vantom, the top Ironclad killer |
| 2 | `Y7M0Z35FZZ` | A0 | Underdocks | **Won** (floor 48) | Baseline win at A0 |
| 3 | `ZDS61QSYXM` | A1 | Overgrowth | Died on floor 33 to **Knowledge Demon** | Act 2 boss killer; tests scaling (H7) |
| 4 | `DGX4GRS6LZ` | A2 | Underdocks | Died on floor 17 to **Soul Fysh** | Third most common killer |
| 5 | `QMZ65RFVNX` | A3 | Overgrowth | **Won** (floor 48) | Win at A3 |

## Schedule
- Baseline: the first time each seed is played (after M1).
- Replay all five at M3 and at M5.
- Record each attempt in `metrics/scoreboard.csv` with `exam_seed=y`.

## Notes
- The same seed gives the same starting map and the same first events. Rewards diverge once choices differ, so results are similar but not identical.
- **Seeded starts:** STS2-Agent has no action to type a seed (it only reports `character_select.seed`), so the Player enters exam seeds in the game UI. STS2MCP's docs say a seed is rejected at the standard singleplayer character select, so seeded runs may need the Custom mode menu. Custom runs may not count toward unlocks; that doesn't matter here. Confirm in Phase 0 (OQ0.6).
