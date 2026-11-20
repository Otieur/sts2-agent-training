# Post-mortem: Run 2026-11-19 1ZWEN4BFQUZL

Character Ironclad · A0 · Playbook v2.18 · Result: **won** (floor 48, 87/102 HP at the end) · first Agent run (profile 2)

## Facts (from `facts.md`)
- 48 floors, 3 acts. Elites killed: Act 1 Phrog Parasite; Act 2 Infested Prism, Decimillipede. Bosses: Ceremonial Beast, The Insatiable, Test Subject.
- HP never fell below 41 (Insatiable fight); lowest after a floor 47/94 (Act 2 boss). 11 of 19 fights above the Player's benchmark p75 (the benchmarks come from A0–A10 history at v0.107.1, so this is a rough comparison).
- Potions: Power Potion and Dexterity Potion (Act 1 boss), Fire Potion (floor 24, measured flat damage), Touch of Insanity (Act 2 elite), Speed and Dexterity (Act 3 boss). Three potions unused at the end.
- 599 actions, 5 failed (invalid targets after an enemy died, one reward claim while the overlay was open). Wall time 120 minutes, including tool fixes made during the run.

## The three costliest decisions
| # | Floor | Decision and reason given | What should have happened | Evidence | Would the playbook have prevented it? |
|---|---|---|---|---|---|
| 1 | 19 | Two turns ended without playing a card: a menu opened during a play, and a "test" command sent a real end_turn | Never send a real action as a test; stop a command chain on the first failure | The Thieving Hopper escaped with Pillage; about 16 HP lost | No: tooling (now fixed: `play_turn.py` refuses unavailable actions and returns failure codes) |
| 2 | 2 | Balanced plan in a hallway traded 11 HP for 15 damage | Safe plan in hallways unless lethal is close | Floor 2 fight log | Partly: the playbook says safe when HP is below plan; the balanced score values 1 damage as 1 HP, too much for hallways |
| 3 | 42 | All-in on the Fabricator took 33 on turn 3 | Some block that turn would have cost about one more turn | Floor 42: 78 to 52 | No |

## What went well
- Scaling first: Demon Form (Neow Arcane Scroll), Juggernaut with Daughter of the Wind (every Attack is a block gain), Crimson Mantle, a second Demon Form; Cascade and Forgotten Ritual for big turns.
- Boss plans from the notes worked: Ceremonial Beast's Plow broken at 149 on turn 3 (stun cancelled the attack); The Insatiable's Sandpit kept at 3 or more with Frantic Escape while cheap, 142 damage on the buff turn; Test Subject phases ended on schedule, phase 3 killed on its first tangible turn.
- Overrides of the tools that paid off: elites taken against the route tool's risk estimate when the deck met the act targets (three elites, 8–11 HP each); Powers over "scaling" credit in drafting (Feel No Pain, Rupture, Cruelty without enablers); Stomp's cost reduction and Juggernaut damage counted by hand.

## Proposed playbook changes (max 5)
| Change | Evidence | Expected effect | Label |
|---|---|---|---|
| The turn planner should count Juggernaut damage on block gains, Stomp's cost reduction, and Strength gains that last the fight (Brand, Demon Form, Armaments upgrades) | This run (floors 6, 17, 28, 33) and gap 30 | Fewer manual overrides; better lines | `[OBS]` |
| Drafting: a Power only earns the "scaling" credit when its enabler is in the deck (exhaust for Feel No Pain, self-damage for Rupture, Vulnerable uptime for Cruelty) | Floors 3, 5, 6 overrides | Fewer bad picks | `[HYPOTHESIS]` |
| Hallways: default to the safe plan; use balanced only for lethal or a scaling enemy | Floor 2 | Less HP lost in hallways | `[HYPOTHESIS]` |
| Rest before the final boss even above the threshold, since no later fight uses an upgrade | Floor 47 | More HP for the last fight | `[HYPOTHESIS]` |
| Feed's max HP needs a real kill: it does not trigger on a Decimillipede segment that can reattach | Floor 30 | Correct Feed targeting | `[OBS]` |

## Scoreboard row
Appended to `metrics/scoreboard.csv`: yes
