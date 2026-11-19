# Post-mortem (practice): the Player's run 1791336980, Ironclad A10, died to Knowledge Demon

Written 2026-11-19 as a practice post-mortem (P4.E4), judged against playbook v2.2.

Character Ironclad · A10 · Overgrowth, Hive · **Died on floor 33 to Knowledge Demon with 59 HP on arrival, taking exactly 59 (the A10 band median).**

## Facts
- **Act 1: three elites.**
  - Byrdonis at 57/80: took 35
  - Bygone Effigy at 52/80: took 43, down to **15 HP**
  - Phrog Parasite at 39/80 (**49%**): took 30, down to 15 HP
  - Three heals were needed in between. Survived The Kin with 16 HP.
- **Act 2:** full HP after the Ancient. Hallways cheap except Chompers (19) and Spiny Toad (24). Three Smiths, one of them right before the boss at 59/80 (Pyre).
- **Act 2 card rewards:** skipped three screens in a row (floors 20, 23, 27), passing up True Grit, Blood Wall, Shrug It Off, Armaments and Drum of Battle. The only power added in Act 2 was Pyre (bought on floor 31).
- **Deck at Knowledge Demon (26 cards):**
  - Basics: 4 Strike, 3 Defend, Bash
  - Dead cards: Ascender's Bane, **Injury**, **Clumsy**
  - Others: One-Two Punch ×2, Armaments, Unrelenting, Bully, Pact's End, Breakthrough, Headbutt, Molten Fist, Body Slam, Flash of Steel, Squash, Tremble, Shrug It Off, Pyre
- **Deck metrics:** 19.2 damage per turn, **5.7 block per turn** (very low), **1 scaling card** (Act 2 target: 4+). Fatal Knowledge Demon decks in the history had fewer powers, energy and Strength (H7). This deck fits that pattern.
- **Relics:** strong energy (Nunchaku, Lantern) and block (Ornamental Fan) from the Act 1 elites. The relics weren't the problem.

## The three costliest decisions
| # | Floor | Decision | What the playbook says instead | Evidence | Would v2.2 have prevented it? |
|---|---|---|---|---|---|
| 1 | 20–31 | Act 2 drafting: three skips, no scaling added until Pyre on floor 31 | §10: Knowledge Demon needs about 60 damage per turn over 7 turns, which means scaling. §2.1 Act 2 target: 4+ scaling cards. Drum of Battle (floor 27) was a power. | Fatal KD decks: powers 1.8 against 2.7 for survivors, energy 0.8 against 1.6. This deck reached KD with 1 scaling card. | Yes: boss fit plus corner targets (§2.1, §10) |
| 2 | 32 | Smith (Pyre) at 59/80 right before KD | Rest: KD's A10 band median is 59, so the threshold is about 69. | Arrived at 59, took 59. | **Yes** (§5, using the band median) |
| 3 | 14 | Third Act 1 elite at 39/80 (49%) | Avoid elites under 50% HP (§4, rule H5). | 24% of elite fights entered under 50% ended the run (n=66). This one cost 30 HP and forced heals instead of Smiths for the rest of Act 1. | Yes: the elite HP rule |

Also: two curses (Injury, Clumsy) were taken from events, and neither was removed at the three shops (floors 15, 21, 31; all gold went to relics and cards). Removal of curses outranks relics in a deck aiming for scaling. `[HYPOTHESIS]`

## What went well
- The aggressive Act 1 paid off in relics (Ornamental Fan, Lantern, Strike Dummy, Nunchaku), which gave Act 2 a strong base.
- Act 2 hallways cost little.

## Proposed playbook changes
1. **Curse removal priority** `[HYPOTHESIS]`: at a shop, remove a non-Eternal curse (Injury, Clumsy) before buying a relic, unless the relic fills the boss checklist. Add to §6.
2. Use the **ascension-band** boss median for the rest threshold; it is already noted in §10. Again confirmed: pooled median + 10 = 55 would *not* have triggered the rest at 59 HP, but the A10 band median + 10 = 69 would have.
