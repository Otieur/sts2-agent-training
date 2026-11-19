# Combat Mechanics

Game version target: v0.107.1. Last updated 2026-11-19.

Labels:
- `[GAME-EXTRACT]`: decompiled power definitions (`knowledge/data/extract-2026-09-21/powers.json`; build may be newer than v0.107.1)
- `[PLAYER-DATA]`: verified in the Player's run history
- `[COMMUNITY]`: guides
- `[HYPOTHESIS]`: carried over from Slay the Spire 1 conventions and not yet verified

Everything not yet verified in a v0.107.1 fight is on the checklist at the end.

## Turn structure
- Each turn: the player draws, gains energy, plays cards, ends the turn. Then enemies act on their shown intents. `[COMMUNITY]`
- Block expires at the start of your next turn unless something prevents it (Barricade: `ShouldClearBlock` returns false while active). `[GAME-EXTRACT]`
- Intents show what each enemy will do next. Monster move sets and numbers are in `knowledge/data/extract-2026-09-21/monsters.json`, with notes in `knowledge/enemies/` and `knowledge/bosses/`.
- Ironclad starts with Burning Blood: heal 6 HP after each combat. `[COMMUNITY]`

## Damage and block arithmetic
Powers modify damage in two passes: additive hooks (`ModifyDamageAdditive`) and multiplicative hooks (`ModifyDamageMultiplicative`). `[GAME-EXTRACT]`

**Working formula** for one hit of an attack, used by `tools/calc.py` `[HYPOTHESIS]` on order and rounding:

```
damage = floor( (base + Strength + Vigor) × (1.5 if target Vulnerable) × (0.75 if attacker Weak) × other multipliers )
damage = min(damage, 1) if the target has Slippery or Intangible (a cap per hit)
HP lost = max(0, damage − target block); block absorbs first
```

**Block from a card:**
```
block = floor( (base + Dexterity) × (0.75 if Frail) × (2 if Unmovable active) )
```

| Effect | Type | Exact behaviour | Source |
|---|---|---|---|
| Strength | Buff | Adds its amount to attack damage (per hit) | `[GAME-EXTRACT]` |
| Dexterity | Buff | Adds its amount to block from cards | `[GAME-EXTRACT]` |
| Vulnerable | Debuff, duration | Damage taken × 1.5; ticks down at end of turn | `[GAME-EXTRACT]` |
| Weak | Debuff, duration | Damage dealt × 0.75; ticks down at end of turn | `[GAME-EXTRACT]` |
| Frail | Debuff, duration | Block gained × 0.75; ticks down at end of turn | `[GAME-EXTRACT]` |
| Vigor | Buff | Adds to the next attack's damage, then is consumed | `[GAME-EXTRACT]` |
| Artifact | Buff, counter | Blocks the next debuff, then decrements | `[GAME-EXTRACT]` |
| Thorns | Buff | Deals its amount to an attacker when hit | `[GAME-EXTRACT]` |
| Plating (Stone Armor) | Buff | Gives block at turn start and before turn end; decrements | `[GAME-EXTRACT]` |
| Ritual | Buff | Gains that much Strength at the end of each turn | `[GAME-EXTRACT]` |
| Intangible | Buff, duration | Caps damage per hit (the cap depends on the dealer) | `[GAME-EXTRACT]` |
| **Slippery** (Vantom) | Buff, counter | Caps each damage instance at **1**; loses one stack after each instance of damage | `[GAME-EXTRACT]` |
| Barricade | Buff | Block is not cleared at turn start | `[GAME-EXTRACT]` |
| Regen | Buff | Heals its amount at end of turn, then decrements | `[GAME-EXTRACT]` |
| Poison | Debuff | Deals its amount at the start of the target's side turn, then decrements | `[GAME-EXTRACT]` |
| No Draw (Battle Trance) | Debuff | No more draws this turn; removed at end of turn | `[GAME-EXTRACT]` |
| Rage | Buff | Gain its amount of block per card played this turn | `[GAME-EXTRACT]` |
| Flame Barrier | Buff | Deals its amount back when you are hit; removed at end of turn | `[GAME-EXTRACT]` |
| Colossus | Buff, duration | Damage multiplier 0.5 (presumably halves damage taken; to verify) | `[GAME-EXTRACT]` |
| One-Two Punch | Buff | Your next card is played one extra time; removed at end of turn | `[GAME-EXTRACT]` |
| Free Attack (Unrelenting) | Buff, counter | Your next attack costs 0 | `[GAME-EXTRACT]` |
| Mangle | Debuff | Target loses Strength temporarily (this turn) | `[GAME-EXTRACT]` |
| Grapple | Debuff | Deals damage to the target each time you gain block, this turn | `[GAME-EXTRACT]` |
| Doom | Debuff | The target dies at end of turn if its HP ≤ Doom | `[GAME-EXTRACT]` |

### Enemy-specific powers worth knowing
| Power | On | Behaviour | Play implication |
|---|---|---|---|
| Territorial | Byrdonis | Gains Strength at the end of every turn | Byrdonis gets more dangerous every turn. Kill it fast; never enter at low HP (all 3 fatal Ironclad fights started at about 29%). |
| Slow | Bygone Effigy | Damage taken rises with cards played (the multiplier is computed at play time) | Long turns with many cards hurt more. Plan big single turns carefully. |
| Plow | Ceremonial Beast | Enough damage removes its Strength and stuns it | Burst it to trigger the stun. |
| Ravenous | Corpse Slugs | When one dies, the others are stunned and gain Strength | Kill order matters. |
| Imbalanced | Bowlbug Rock | Stuns itself after dealing damage | Its big hit is followed by a free turn. |
| Stock | Axebots | Keeps combat from ending at death (spawns more) | Expect extra waves. |
| Ringing | Ceremonial Beast (Beast Cry) | An affliction on your cards for the turn | Read your hand before playing. |

## Statuses and curses in the deck
- **Wound:** status card, unplayable (Vantom's Dismember adds 3 per cycle). `[GAME-EXTRACT]` (monster move list)
- **Dazed:** added by Chomper's Screech (3). `[GAME-EXTRACT]`
- **Ascender's Bane:** curse with keywords Eternal, Unplayable, Ethereal. Added from A5 `[PLAYER-DATA]`. "Eternal" suggests it cannot be removed `[HYPOTHESIS]`; the Player never removed it in 80+ A5+ runs `[PLAYER-DATA]`.

## Map and acts
- **Act 1:** Overgrowth or Underdocks. **Act 2:** Hive. **Act 3:** Glory. `[PLAYER-DATA]`
- A run is about 48 floors (Act 1 ends at floor 17, Act 2 at floor 33, Act 3 at floor 48), plus floor 49 for the second boss at A10. Floor 1 of each act is an Ancient. `[PLAYER-DATA]`
- **Bosses by act** `[PLAYER-DATA]` (each seen 24–40 times across all characters):
  - Overgrowth: Ceremonial Beast, Vantom, The Kin
  - Underdocks: Lagavulin Matriarch, Waterfall Giant, Soul Fysh
  - Hive: Knowledge Demon, The Insatiable, Kaiser Crab
  - Glory: Test Subject, Aeonglass, Queen (two of them at A10)
- **The boss is known at the start of the act.** The game's map state contains the boss identity, which STS2MCP exposes (commit `3154670`, "Expose map boss identity"). Plan the act around it. Resolves OQ2.3 (likely; confirm on the live map).
- Room types: monster, elite, ? (unknown: event, or sometimes a fight), shop, rest site, treasure, Ancient (act start), boss. `[PLAYER-DATA]`
- The game heals between acts at the Ancient. From A2 the heal is 80% of missing HP (data: 79%) instead of 100%. `[PLAYER-DATA]`
- Rest-site options seen: Smith (upgrade), Heal (restores 30% of max HP, rounded down, capped at max HP; 237 of 297 heals match exactly, 34 were larger, presumably relic boosts), and relic-driven options (Dig, Cook, Kindle, Hatch, Lift, Clone). `[PLAYER-DATA]`

## Verification checklist (first Phase 4 runs; P2.E2.S2)
| # | Rule to verify | Test | Expected |
|---|---|---|---|
| 1 | Vulnerable multiplier and rounding | Strike (6) on a Vulnerable enemy with 0 Strength | 9 |
| 2 | Odd-number rounding under Vulnerable | Twin Strike (5) on a Vulnerable enemy | 7 per hit (floor of 7.5) |
| 3 | Weak multiplier | Enemy intent of 10 while the enemy is Weak | Intent shows 7 |
| 4 | Order: Strength before multipliers | Strike with 2 Strength on a Vulnerable target | 12 (= (6+2)×1.5) |
| 5 | Frail | Defend (5) while Frail | 3 |
| 6 | Slippery cap and stacks | Twin Strike on Vantom on turn 1 | 1 + 1 damage; stacks 9 → 7 |
| 7 | Block absorbs before HP | 10 damage into 6 block | Lose 4 HP |
| 8 | Burning Blood heal | After any won fight | +6 HP |
| 9 | Heal amount at rest | Rest at 40/80 | +24 (30% of max, rounded down) |
| 10 | Colossus power effect | Play Colossus, then take a hit | Damage halved? |
| 11 | Ascender's Bane removable? | Try removal at a shop with A5+ | Expect refused (Eternal) |

## Facing (Surrounded)
- Kaiser Crab applies **Surrounded** to you: a ×1.5 damage multiplier on back attacks, re-evaluated before each card and potion `[GAME-EXTRACT]` (`SURROUNDED_POWER`). Facing rule `[HYPOTHESIS]`: you face the enemy you last targeted. To confirm in the first Kaiser Crab fight.
