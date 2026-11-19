# Ironclad Quick Reference (for live play)

One page to keep in context during a run. It summarises `playbooks/ironclad.md` (v2.18); when they differ, the playbook wins. Section numbers point there.

## Every decision
1. State and advice in one: `python3 -I tools/advise.py --live --save runs/<run>/state.json` (co-op: add `--instance teammate`; STS2MCP: `--mod sts2mcp`)
2. (Or from a saved file: `python3 -I tools/advise.py --state runs/<run>/state.json`)
3. Act with a reason and the tool's pick: `python3 -I tools/sts.py --mod sts2agent --log runs/<run>/decisions.jsonl act <action> key=value ... --reason "..." --tool-pick "<advised action>"`
4. New floor: `python3 -I tools/journal.py floor ...`; after each fight: `python3 -I tools/journal.py fight ...`
5. Act start and before each boss: `python3 -I tools/deck_check.py --state runs/<run>/state.json`; the route: `python3 -I tools/path.py --state ...`

## Rules backed by the history (adopted)
| Rule | Evidence |
|---|---|
| **H5:** no elite under 50% HP | 24% of such elite fights ended the run, against 3–8% above (§4) |
| **H11:** no hallway fight under 40% HP when there is a choice | 21% fatal under 30%, 12% at 30–40%, about 1–2% above; Act 2 under 40%: 14/40 (§4) |
| **Rest before a boss** below the band median + 10 (Acts 1–2) or 70% (Act 3) | Following the rule went with lower boss fatality both ways (H1, §5) |
| **Corner targets on arrival at the boss:** Act 1 block/turn 10+ and 2+ scaling cards; Act 2 4+ scaling; Act 3 block/turn 8+ | Missed in 88% of fatal against 69% of survived boss fights (H9, §2.1) |

## Drafting (§2)
- Consensus tier first (it predicted the Player's Ironclad outcomes: A-tier picks +17 points of act survival).
- Boss fit overrides tier. Vantom: cheap and multi-hit attacks up, single-hit hit-all down (simulated: multi-hit best; Breakthrough worse than a Strike). Knowledge Demon: Strength, energy, powers.
- Avoid Breakthrough (the Player's picks: 48% against 78% act survival).
- Skip when nothing clears the bar (rises with deck size).
- Ancients: avoid Hefty Tablet (H10), prefer Fishing Rod (§7).

## Combat (§9)
- Read intents; lethal first; never end a turn the planner marks as fatal.
- **Boss fights and enemies that scale every turn (Byrdonis): follow the balanced plan** (simulation: the safe plan collapsed against Byrdonis with a weak deck). **Exceptions: Waterfall Giant and Soul Fysh, safe plan** (simulated). Other hallways and elites: safe when HP is below the act plan.
- Against Slippery (Vantom), each stack stripped counts about 3 damage in the balanced plan: strip early.
- Potions: hold them in hallways unless they decide the fight; use freely in elites and bosses.
- Statuses that cost HP when held (Beckon 6, Toxic 5, Wither): get rid of them when energy allows. **Sandpit (The Insatiable): end every turn at 2 or more** (Frantic Escape +1, cost rises each play).
- Under Tender, every card costs 1 Strength and 1 Dexterity this turn: fewer, bigger cards. Kaiser Crab: kill a claw with the turn's last attack (Crab Rage gives the other 99 Block).

## Bosses (§10, notes in `knowledge/bosses/`)
| Boss | The one thing |
|---|---|
| Vantom | 8 Slippery stacks at low ascension, 9 higher (wiki): cheap and multi-hit attacks; block 27 on turn 3 |
| Lagavulin Matriarch | Set up while asleep; first damage on the last sleep turn (wakes stunned) |
| Ceremonial Beast | Plow: stunned at 150 HP left (community); Ringing after Beast Cry: one card next turn |
| Soul Fysh | Get rid of Beckons (6 HP each if held at end of turn; 1 energy to play, exhaust is better); burst outside Fade's Intangible; block De-Gas after Scream (24); safe plan |
| Waterfall Giant | **Safe plan** (simulated): the death explosion = its Steam Eruption; the turn after the kill is a stun, then block the explosion |
| Knowledge Demon | Curse offers are Disintegration or one card: take Mind Rot, then Sloth, then Waste Away (close); never stack Disintegration (simulated) |
| Kaiser Crab | Focus Rocket; end the Laser turn facing Rocket; kill a claw with the turn's last attack (Crab Rage) |
| Queen | Turn 1 Strong Tackle 26 (Amalgam): block it; turn 2 You're Mine puts 99 Frail, Weak and Vulnerable on you (Artifact blocks it); she blocks 20 a turn while the Amalgam lives and only attacks after it dies; arrive high |
| The Kin | Killing the Priest ends the fight (followers are Minions; confirmed in game): race it with a single-target deck; with hit-all damage clear the followers first (simulated) |
| The Insatiable | Sandpit (4) kills you at 0: end every turn at 2 or more, and play Frantic Escape while cheap to keep 3–4; cost rises each play |
| Test Subject | Phase 1: each Skill gives it 2 Strength, so attack; phases 100/200/300 HP with a one-turn stun between |
| Aeonglass | Strip its 3 Artifact before debuffs; a Wither every 6 cards (3 damage at end of turn if held, 6 once upgraded): fewer, bigger plays; Ebb 22 + 33 Block |

## Elites (§4)
Infested Prisms: few Skills (each Skill makes its hits stronger). Entomancer: few big hits (Personal Hive adds Dazed). Byrdonis: kill fast (+2 Strength a turn). Skulking Colony: at most 20 damage a turn counts (Hardened Shell). Bygone Effigy: big attack last (Slow). Terror Eel: at 70 HP it is stunned, then puts 99 Vulnerable on you: be ready to finish it after the threshold. Phantasmal Gardeners: the first attack on each Gardener gives it 6 Block, so one hit per Gardener or hit-all.

## Before trusting a number
Gaps 22–28 list the assumptions still unverified in game (live card values, flat potion damage, Kaiser facing, Ceremonial Beast Plow, Entomancer's Dazed count, the simulated boss cycles, Sandpit timing). `docs/runbooks/first-session.md` checks them.
