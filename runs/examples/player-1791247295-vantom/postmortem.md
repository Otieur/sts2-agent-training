# Post-mortem (practice): the Player's run 1791247295, Ironclad A10, died to Vantom

Written 2026-11-19 as a practice post-mortem: the Phase 4 process (P4.E4) applied to one of the Player's runs, judged against playbook v2.2. The goal is to learn what beats this result, not to grade the Player.

Character Ironclad · A10 · Act 1 Overgrowth (Vantom was visible from floor 1) · **Died on floor 17 to Vantom with 57 HP on arrival, taking exactly 57.**

## Facts (from `facts.md` and the run history)
- **Path:** 5 monsters, 3 ? rooms, 1 elite (Phrog Parasite, only 6 damage), 1 treasure, 1 shop, 4 rest sites (all Smith).
- **HP:** 64 after Neow, 50–57 from floor 6 on, never healed. Arrived at Vantom with 57/80 (71%).
- **Deck at Vantom (20 cards):**
  - 4 Strike, 4 Defend, Bash, Ascender's Bane
  - Sword Boomerang+, Twin Strike, Anger, Bloodletting+, Cinder+, Rage, Blood Wall, Pact's End+, Stampede+, Breakthrough
- **Deck metrics** (`tools/deck_metrics.py`): **21.8 damage per turn** (well above the starter's 15), **8.7 block per turn** (Act 1 target 10), **1 scaling card** (target 2+). This is the exact profile that died most at bosses in the history: lots of raw damage, little block and scaling (H9).
- **Relics:** Burning Blood, Lost Coffer, Vajra, Ripple Basin, Belt Buckle (bought on floor 14 for 199 of 204 gold).
- **Potions:** Flex Potion used in the Vantom fight. Nothing else held.

## The three costliest decisions
| # | Floor | Decision | What the playbook says instead | Evidence | Would v2.2 have prevented it? |
|---|---|---|---|---|---|
| 1 | 16 | Rest site before Vantom at 57/80: **Smith** (Bloodletting) | Rest: 57 is below Vantom's threshold (A10 band median 57 + 10 = 67). A heal (+23) would have meant arriving at 80. | Same fight, same 57 damage, about 23 HP left. Vantom killed this Ironclad in 6 of 11 fights. | **Yes**, the pre-boss rest rule (§5) |
| 2 | 14 | Shop: 199 gold on Belt Buckle (+2 Dexterity while holding no potions) | §6 priority: boss checklist first. Vantom wants block for turn 3 (Dismember 27) and a Weak potion. Shrug It Off and True Grit were in stock; potions were available. | Deck block was 8.7 per turn against the target of 10. Belt Buckle also pushes you to hold no potions before a boss. | Probably. Boss fit (§2.1) and the shop priority (§6) |
| 3 | 15 | Card reward: **Breakthrough** over Blood Wall and Armaments | Against Vantom, hit-all single hits are wasted on Slippery (§2.2 override). A block card served the boss checklist. | Breakthrough was in 5 of 6 fatal Vantom decks in the history. | Yes, the Vantom override (§2.2) |

Also worth noting: the Flex Potion (temporary Strength) only helps once Slippery is gone. If it was used early, it was wasted (unknown from the record).

## What went well
- Cheap Act 1 hallway fights (2–12 damage each) and a cheap elite (6 damage).
- The multi-hit cards Vantom wants were already in the deck (Sword Boomerang+, Twin Strike, Anger), so stripping Slippery was possible.

## Proposed playbook changes
None new: v2.2 already covers all three decisions (§5 pre-boss rest, §2.1 corner targets and boss fit, §2.2 Vantom override, §6 shop priority). This run supports keeping them. It also shows the rest threshold should use the **band** median (A10: 57), not the pooled one (48): pooled + 10 = 58 would only just have triggered the rest at 57 HP.
