# Knowledge Gaps

Everything still unverified, ranked by how much it affects play (S6, written 2026-11-19 overnight). Update as items are resolved: move them to the "Resolved" section with the date and evidence.

## High impact (affects the first Phase 4 runs)
| # | Gap | Why it matters | How to close | Where |
|---|---|---|---|---|
| 1 | Does the mod work on v0.107.1 on this Mac? Which mods folder is scanned? | Nothing live happens without it | Phase 0: build, install and run the smoke tests | OQ0.1, OQ0.2 |
| 2 | Damage order and rounding (Strength before multipliers? floor per hit?) | Every turn's arithmetic and `tools/calc.py` | Checklist items 1–7 in the first fights | `knowledge/mechanics.md` |
| 3 | Is the extract's build the same as v0.107.1? | Card and monster numbers could be off | Compare live `/data` exports (STS2-Agent) or in-game card text against `knowledge/data/extract-2026-09-21/` | P2.E1 |
| 4 | Vantom's Slippery stack count (9 in solo) and cycle order in v0.107.1 | The Act 1 plan for the top Ironclad killer | Read state on turn 1 of the first Vantom fight | `knowledge/bosses/VANTOM_BOSS.md` |
| 5 | Is the boss shown on the map at act start? | Act planning, boss-fit drafting | Read `map.boss` on floor 1 | OQ2.3 (likely yes) |
| 6 | STS2MCP state field names (hand, intents, map) as documented? | `tools/sts.py`, `watch.py`, `record.py` all depend on them | Capture real samples (P0.E5.S1); fix the tools | `docs/api-notes.md` |
| 7 | Seeded starts: does standard mode accept a seed, or only Custom mode? | Exam seeds | Try `menu_select` with `seed=` | OQ0.6 |

## Medium impact
| # | Gap | Why it matters | How to close |
|---|---|---|---|
| 8 | Cards whose numbers are computed in game (`?`): Dominate (Strength per Vulnerable), Body Slam, Perfected Strike, Ashen Strike, Conflagration, Bully, Expect a Fight, Fiend Fire, Tear Asunder, Dismantle | Card evaluation; `deck_metrics.py` counts them as 0 | Read live card text in hand (`dynamic_values` on STS2-Agent, `description` on STS2MCP) |
| 9 | Cost upgrades missing from the extract (Barricade, Corruption, Body Slam, Dark Embrace, Armaments text) | Smith priority | Read upgraded card text in the shop or card library |
| 10 | Upgrade mapping where flagged ambiguous (Offering: energy or cards? Drum of Battle) | Smith priority | Same |
| 11 | Enemy powers with unclear effects: Slow (Bygone Effigy) multiplier, Vital Spark (Infested Prism), Skittish (Gardeners), Colossus power on you | Elite plans | Observe in fights; record in the enemy notes |
| 12 | Boss details: does damaging Lagavulin Matriarch wake it? Does killing the Kin Priest end the fight? Knowledge Demon curse choice mechanics; Insatiable Sandpit timer length; Waterfall Giant explosion vs Weak | Boss plans | First encounters; update `knowledge/bosses/` |
| 13 | Ascension effects not visible in data: A1 (more elites), A6 (one fewer rest site), A7 (fewer rares), A8 and A9 exact numbers | HP budgets at higher ascension | Read `run.ascension_effects` (STS2-Agent) or the in-game list |
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
| 2026-11-19 | Act boss lists per act variant | From run data (`knowledge/mechanics.md`) |
| 2026-11-19 | A2 Ancient heal, A3 gold, A4 potion slots, A10 double boss | Confirmed in run data (`knowledge/ascension.md`) |
