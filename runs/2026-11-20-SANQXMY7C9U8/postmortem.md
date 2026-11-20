# Post-mortem: Run 2026-11-20 SANQXMY7C9U8

Character Ironclad · A1 · Playbook v2.19 · Result: died on floor 17 to Ceremonial Beast (the act 1 boss, left at 77/252 HP)

## Facts (from `facts.md`)
- Floor 17, act 1. Elites killed: 3 (Byrdonis, Bygone Effigy, Phrog Parasite). Run time 150 min, 256 logged actions.
- HP curve: 80/80 through floor 6; 63 after Byrdonis; 48 after Bygone Effigy; 42 after the Ruby Raiders; 30 after Phrog Parasite; rested to 54 (68%) before the boss; 0 on boss turn 7.
- Fights above the benchmark p75: Slimes (floor 4, 6 vs 3.0), Byrdonis (23 vs 19.5), Slimes (floor 9, 15 vs 13.2), and the boss.
- Potions: Ship in a Bottle (Byrdonis), Potion-Shaped Rock in four fights (Petrified Toad renews it every fight), Fysh Oil and Distilled Chaos (Phrog Parasite), Colorless Potion (boss). None held at death.
- Errors and failed actions: `--tool-pick` passed to `tools/play_turn.py`, which does not accept it, so the next command played a Defend instead of the planned Strike (floor 4); two target indexes went stale after a kill (a step failed and was redone); one potion slot index assumed to shift (it does not). No reloads.

## The three costliest decisions
| # | Floor | Decision and reason given | What should have happened | Evidence | Would the playbook have prevented it? |
|---|---|---|---|---|---|
| 1 | 17 | Boss turn 2: Cinder+ played before the 0-cost Salvo the planner sequenced after it. Cinder exhausts a random card in hand and took Salvo (15 damage lost); the last energy then went to Rupture rather than a Strike or Defend. | Play Salvo first (any card that must survive goes before Cinder); with the Plow break two turns away either way, a Defend (5) would have been worth more than Rupture in a fight that ended three turns later. The run died by exactly 0 HP on turn 7: 5 block or 15 earlier damage changes that turn. | Boss turns 2 and 7 in `decisions.jsonl`; the death turn had 9 block against 17 at 8 HP | No: `tools/plan_turn.py` does not model Cinder's random exhaust, and values Powers at 10 per energy in boss fights regardless of the fight's remaining length |
| 2 | 15 | Took the third elite (Phrog Parasite) at 52% HP, following the path planner (boss arrival 68% against 48% for the hallway route) and H5 (threshold 50%). Arrived at 30 HP, rested to 54. | The planner's estimate looks inverted (an extra elite should not raise boss arrival HP); a hallway route would have arrived with about the same HP after the rest, but with a smith. The elite gave Molten Egg and Cinder+ (55 damage in the boss fight), so the net effect is unclear. | `tools/path.py` scores at floor 14; facts HP curve | Partly: H5 allowed it; the planner's number deserves a check |
| 3 | 1 | Neow: took Small Capsule (a random relic: Vajra) over Cursed Pearl (333 gold and the Greed curse) and New Leaf, because the map was not visible yet. | The best route had a shop on floor 2 (Feed, tier S, 155 gold, unaffordable with 109) and a second shop on floor 13. With 333 gold the deck gets its best card early. | Floor 3 shop list; Ancient record for Cursed Pearl 67% vs 53% (small sample) | No: the map is not in the state during the Neow event, and the playbook has no rule for gold versus relic |

Also: the deck arrived at the boss with 10.8 block per turn. `tools/deck_check.py` passed it (act 1 target 10), while the boss note asks for about 18 per turn early against Plow's 18, 20, 22. The Ringing turn (one card) and the following Crush (17) found the deck without a block card that also helps under Ringing.

## What went well
- Every hallway fight before floor 9 at full HP; Byrdonis killed on turn 4 by overriding the balanced plan with Bash + Molten Fist.
- Live mechanics confirmed: Molten Fist doubles Vulnerable (3 to 6); Slow on Bygone Effigy is ×(1 + 0.1 × cards played this turn) (Strike 10 → 14 after four cards); breaking Plow (crossing 150 HP) stuns Ceremonial Beast at once and removes its Strength, cancelling that turn's attack.
- The Phrog Parasite was killed at the start of a turn, so all four Wrigglers spawned stunned and the potions were spent in that free turn.
- Nine fights recorded by the game and kept for the simulator (floors 2–17, the boss included); the first two replay exactly in the host.

## Proposed playbook changes (max 5)
| Change | Evidence | Expected effect | Label |
|---|---|---|---|
| Ceremonial Beast checklist in `tools/deck_check.py`: block about 15–18 per turn on arrival (the note's figure), not the generic act 1 target 10 | This run: 10.8 block, died with the Beast at 77 HP after taking 18, 20, 18 (Plow) and 15, 17 | Flags the gap before the boss while there is a shop or smith to fix it | `[HYPOTHESIS]` (one run) |
| Planner: Cinder exhausts a random card in hand; plan cards that must survive before it | Boss turn 2: Salvo exhausted | Removes a planning error worth about one card per Cinder play | `[OBS]` |
| Planner: crossing Plow's threshold stuns Ceremonial Beast and cancels its attack that turn; value plans that cross it accordingly | Boss turn 4: intent changed to Stun after the second Strike | Prefers threshold-crossing lines that the current model scores as taking the full hit | `[OBS]` |
| Knowledge: Molten Fist doubles the target's Vulnerable; Slow is ×(1 + 0.1 × cards played this turn) | Byrdonis turn 3; Bygone Effigy turn 2 | Correct damage in the planner and draft scorer (Molten Fist is tier D in the lists) | `[OBS]` |
| Path planner: check why an extra elite raises the predicted boss arrival HP (68% vs 48% at floor 14) | Floor 14 map scores | Avoids elites taken at the H5 margin on a wrong estimate | `[HYPOTHESIS]` |

**Applied the same night (factual planner fixes, with tests in `tools/tests/test_plan_turn.py`):** Cinder is ordered after every other planned card; Plow is read as a stun threshold like Shriek. The other three rows remain proposals.

## Scoreboard row
Appended to `metrics/scoreboard.csv`: yes
