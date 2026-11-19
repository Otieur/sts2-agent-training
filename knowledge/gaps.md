# Knowledge Gaps

Everything still unverified, ranked by how much it affects play (S6, written 2026-11-19 overnight). Update as items are resolved: move them to the "Resolved" section with the date and evidence.

## High impact (affects the first Phase 4 runs)
| # | Gap | Why it matters | How to close | Where |
|---|---|---|---|---|
| 1 | Does the mod work on v0.111.1 (main since 2026-11-16) on this Mac? Which mods folder is scanned? | Nothing live happens without it | Phase 0: build, install and run the smoke tests | OQ0.1, OQ0.2 |
| 2 | Damage order and rounding (Strength before multipliers? floor per hit?) | Every turn's arithmetic and `tools/calc.py` | Checklist items 1–7 in the first fights | `knowledge/mechanics.md` |
| 3 | The extract predates v0.107.1 (`knowledge/version-delta-extract-to-v0.107.1.md`). Which of its numbers are wrong on v0.111.1 beyond the two delta files? | Card and monster numbers in `knowledge/` come from it; the known changes are listed in `knowledge/version-delta-v0.111.1.md`, but patch notes may be incomplete | Compare live `/data` exports (STS2-Agent) or in-game card text against the extract; start with the cards and enemies named in the delta | P2.E1 |
| 4 | Vantom's Slippery stack count (9 in solo) and cycle order on v0.111.1 | The Act 1 plan for the top Ironclad killer | Read state on turn 1 of the first Vantom fight | `knowledge/bosses/VANTOM_BOSS.md` |
| 5 | Is the boss shown on the map at act start? | Act planning, boss-fit drafting | Read `map.boss` on floor 1 | OQ2.3 (likely yes) |
| 6 | STS2MCP state field names (hand, intents, map) as documented? | `tools/sts.py`, `watch.py`, `record.py` all depend on them | Capture real samples (P0.E5.S1); fix the tools | `docs/api-notes.md` |
| 7 | Seeded starts: does standard mode accept a seed, or only Custom mode? Do the 10-character v0.107.1 exam seeds still work now that seeds are 12 characters? | Exam seeds | Try `menu_select` with `seed=`; if old seeds fail, pick new exam seeds from the first v0.111.1 runs | OQ0.6, `metrics/exam-seeds.md` |
| 28 | The Insatiable's Sandpit: starting value (4 per player, wiki), when it ticks (start of your turn?), Frantic Escape's +1 and rising cost; does Toxic's end-of-turn damage hit block? Every playable Status was unplayable in the planner until 2026-11-19 | `tools/plan_turn.py` marks a plan ending at Sandpit 1 or less as fatal | First Insatiable fight: read `SANDPIT_POWER` at each turn start and Frantic Escape's cost after each play | —  |

## Medium impact
| # | Gap | Why it matters | How to close |
|---|---|---|---|
| 21 | The Player's benchmarks are from v0.107.1; the Agent plays v0.111.1. How much do the changes (Demon Form, Mangle, Colossus, enemy HP and moves) shift encounter damage? | Benchmark comparisons (M4, post-mortems) | Track v0.111.1 encounter damage separately; compare only unchanged encounters until n ≥ 5 per encounter |
| 22 | Do STS2-Agent `dynamic_values` current values include your Strength, Weak, Dexterity and Frail, and exclude the target's Vulnerable? **Mostly answered by the mod's source (2026-11-19):** `current_value` is the game's normal card preview (`UpdateDynamicVarPreview(Normal, card.CurrentTarget)`), so it includes your own modifiers and includes the target's only when a target is selected (normally none). Intent damage is the game's own `GetSingleDamage` against the players, so it already includes the enemy's Strength and Weak and your Vulnerable (the planner no longer applies an existing Weak twice) | `tools/plan_turn.py` relies on both | Confirm once in game (first-session check 7) |
| 8 | Cards whose numbers are computed in game (`?`): Dominate (Strength per Vulnerable), Body Slam, Perfected Strike, Ashen Strike, Conflagration, Bully, Expect a Fight, Fiend Fire, Tear Asunder, Dismantle | Card evaluation; `deck_metrics.py` counts them as 0 | Read live card text in hand (`dynamic_values` on STS2-Agent, `description` on STS2MCP) |
| 9 | Cost upgrades missing from the extract (Barricade, Corruption, Body Slam, Dark Embrace, Armaments text) | Smith priority | Read upgraded card text in the shop or card library |
| 10 | Upgrade mapping where flagged ambiguous (Offering: energy or cards? Drum of Battle) | Smith priority | Same |
| 11 | Enemy powers, partly answered by the power data (2026-11-19): Slow is ×(1 + 0.1 × count), count unconfirmed; Colossus halves damage taken for a duration; Skittish gives block after an attack (whose attack: unconfirmed); Vital Spark belongs to the pre-rework Infested Prism | Elite plans | Observe in fights; record in the enemy notes |
| 23 | Kaiser Crab facing: **mostly answered by the wiki (2026-11-19)**: playing a card against a claw turns you toward it and the claw behind you deals ×1.5; hit-all and random attacks do not turn you. Still open: whether the state's intents already include the ×1.5, and Crab Rage's Strength on v0.111.1 (5 in the game data, 6 on the beta page) | Laser 31 against 46; the kill-turn plan; `tools/plan_turn.py` does not model facing | First Kaiser Crab fight: read both claws' intents before and after targeting each |
| 24 | Does unpowered potion damage (Fire Potion 20, Explosive Ampoule 10) ignore Vulnerable and Strength? | `tools/plan_turn.py` assumes it ignores both | Use a Fire Potion on a Vulnerable enemy and read the HP change |
| 25 | Ceremonial Beast: Plow triggers at 150 HP left (community; fixed in the simulator), but the model still fails calibration (9% simulated wins against 5 of 6 real survivals). One-assumption variants (`simulate_fight.py --beast-sensitivity`): no Strength gain on Plow 77%, Plow dealing 12 instead of 18 72%, no Ringing limit 37%, a two-turn stun 36%; a higher Plow threshold or a different post-stun order barely moves it. So the likely errors are Plow's damage or Strength gain (more guides confirm Ringing allows one card, so that is not it) | Boss plan and the simulator | First Ceremonial Beast fight: read Plow's intent each turn (does it climb by 2?), how many cards Ringing allows after Beast Cry, and how long the stun lasts |
| 26 | Entomancer: **mostly resolved by the wiki (2026-11-19)**: Bees 3x7, Spear 18, Pheromone Spit +1 Hive and +1 Strength (+2 at Hive 3); the corrected model is calibrated. Still to see: the Dazed count per hit in game | Elite plan; the simulator | First Entomancer fight: count Dazed added per hit |
| 27 | Soul Fysh and Waterfall Giant as simulated: does a held Beckon cost 6 HP at the end of the turn, and does playing it (1 energy) send it to the discard pile? Does Fade's Intangible last one of your turns or two? Which card does Gaze add? Is the Waterfall Giant's cycle Stomp, Ram, Siphon, Pressure Gun (20, +5 a use; numbers also on a wiki data page), Pressure Up (order from one guide; an older one shows only the first three repeating)? With it the model is far too hard (14% simulated wins from 60/80 against the Player's 3 of 5). Does Weak on the Giant reduce the explosion (one guide says yes)? | The simulator's Soul Fysh and Waterfall Giant models (used in drafting) and the safe-plan advice against the Giant | First fight against each: read the intents every turn, the Beckon card text, the Intangible counter, and the Steam Eruption amount before the explosion |
| 12 | Boss details: Lagavulin Matriarch: damage wakes it stunned per the power data (which power is removed with it?). Kin Priest: killing it ends the fight (two guides, 2026-11-19; followers are Minions) — confirm once in game. Knowledge Demon curse choice mechanics; Insatiable Sandpit timer length; Waterfall Giant explosion vs Weak | Boss plans | First encounters; update `knowledge/bosses/` |
| 13 | Ascension effects not visible in data: A1 (more elites), A6 (one fewer rest site), A8 and A9 exact numbers (A7 checked 2026-11-19: upgraded rewards halve, Rares drop from 14% to 12%) | HP budgets at higher ascension | Read `run.ascension_effects` (STS2-Agent) or the in-game list |
| 14 | Hypotheses H1–H9 | Core strategy rules | Phase 4 experiments with logging (`playbooks/ironclad.md` §12) |
| 15 | Co-op: do enemy attacks hit every player? Enemy HP scaling per player | All co-op block planning | Phase 6 first co-op fight (P6.E1.S2) |

## Low impact (later phases)
| # | Gap | How to close |
|---|---|---|
| 16 | Not Yet (card) and Aeonglass (boss) missing from the extract | Live data or in-game reading |
| 17 | Necrobinder's Osty and Summon rules | Phase 5 knowledge pass |
| 18 | Event outcomes beyond the risk tags (exact rewards) | Event screens during runs |
| 19 | Relic hook semantics (for example `AfterSideTurnStart` = start of your turn?) | Observe relic triggers |
| 20 | Whether the game throttles when unfocused | P0.E6.S5 |

## Resolved
| Date | Gap | Resolution |
|---|---|---|
| 2026-11-18 | Do run files log every deck change? | Yes: 232/232 decks reconstruct exactly (OQ1.1) |
| 2026-11-19 | Which ascension adds Ascender's Bane? | A5 (100% of A5+ runs) |
| 2026-11-19 | Gap 5: is the boss known at act start? | Yes on STS2-Agent: `run.boss_id` comes from the current act's boss encounter (mod source) |
| 2026-11-19 | Act boss lists per act variant | From run data (`knowledge/mechanics.md`) |
| 2026-11-19 | A2 Ancient heal, A3 gold, A4 potion slots, A10 double boss | Confirmed in run data (`knowledge/ascension.md`) |
| 2026-11-19 | Which game build is the extract from? | **Pre-v0.107.1** (corrected at 01:42 from an earlier "v0.107.x–v0.110"): eleven v0.107.1 changes show old values and Aeonglass is missing. Exact build unknown. Replaced by gap 3 |
| 2026-11-19 | Does killing The Kin's Priest end the fight? | Yes per two guides (followers are Minions); the planner treats it as lethal. Still to see once in game (gap 12) |
| 2026-11-19 | Test Subject's Enrage: every card or only Skills? | Skills, 2 Strength each (several guides); the planner counts Skills only |
| 2026-11-19 | What does Colossus do? | Half damage from Vulnerable enemies for the turn (two card pages); modelled |
| 2026-11-19 | Forgotten Ritual's exhaust condition | Removed on v0.111.1 (patch notes); the planner follows the patched card text |
| 2026-11-19 | Knowledge Demon curse offers and Ponder heal | Disintegration or Mind Rot, then Sloth, then Waste Away; heal 30 per player (two guides) |

| 2026-11-19 | Gap 29: Aeonglass Withers and Ebb | The wiki: a Wither every 6 cards, Unplayable, 3 (6 upgraded) at end of turn if held; Ebb 22 + 33 Block, no debuff since v0.107.0 (the conflicting guide predates it) |
