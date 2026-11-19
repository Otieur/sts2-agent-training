# Vantom (Act 1 boss, Overgrowth)

Status: **early note**, written during Phase 1. To be completed in Phase 2 (P2.E5.S1) from game data and the Bestiary. Mechanics below are `[COMMUNITY]` from a guide dated 2026-03-27, an earlier build than v0.107.1, so the numbers may be out of date.

## Mechanics `[COMMUNITY]`

- **HP:** 173 (solo).
- **Slippery:** starts with 9 stacks in solo, more with more players. While it is active, each time Vantom would lose HP it loses only 1 instead, regardless of the damage. Each instance removes one stack, so 9 separate hits are needed to clear it.
- **Move cycle** (repeats):
  1. Ink Blot: 7 damage
  2. Inky Lance: 2 × 6 damage
  3. Dismember: 27 damage, and shuffles 3 Wounds into the discard pile
  4. Prepare: gains 2 Strength
- **Scaling:** Strength from Prepare each cycle, plus 3 more Wounds each cycle. Long fights get worse on both counts.

## What this implies `[HYPOTHESIS]` until verified

- Multi-hit attacks and 0-cost or cheap attacks strip Slippery fastest. Big single hits played while Slippery is up deal 1 damage.
- Do not stall: every cycle adds Strength and Wounds. Clear Slippery quickly, then switch to the biggest damage.
- Turn 3 of each cycle (Dismember, 27 before Strength) is the turn to block for, or to have Weak applied.
- A Weak potion early reduces the whole first cycle.
- This may explain why Vantom hurts the Player's Ironclad most. The Player ranks several multi-hit-looking cards below SKIP (Twin Strike, Sword Boomerang) and rarely takes Anger (0 cost). Card text in Phase 2 confirms which cards are multi-hit.

## The Player's record (v0.107.1)

| Character | Fights | Deaths | Mean damage |
|---|---|---|---|
| Ironclad | 11 | 6 | 48 |
| Necrobinder | 5 | 3 | 33 |
| Silent | 6 | 2 | 24 |
| Regent | 4 | 1 | 20 |
| Defect | 2 | 0 | 17 |

Ironclad benchmark: median 48 damage, p75 57.5, p90 63, median 7 turns (n=11).

Ironclad fatal fights started at a median 64% HP, survived ones at 56%. Arrival HP was not the difference; damage taken was (58 against 40). Weak signal (n=11): Breakthrough was in 5 of 6 fatal decks and 1 of 5 survived ones.

## Rest-site rule before Vantom (proposal, `[HYPOTHESIS]`)

Rest if HP is under about 55 (median damage plus a margin), unless the deck clearly strips Slippery fast. Test in Phase 4.

## Sources

- Selphie1999 Gaming, "How to Defeat Vantom in Slay the Spire 2" (2026-03-27)
- Player run history (`reports/phase1/deaths-ironclad.md`)
