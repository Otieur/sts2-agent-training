# Co-op Rules

Last updated 2026-11-19 (P6.E1.S1).

Sources:
- `[COMMUNITY-A]`: allthings.how co-op mechanics guide (date not stated)
- `[COMMUNITY-B]`: FinalBoss "How co-op works" (2026-04-29, early access)
- `[GAME-EXTRACT]`: the decompiled game data
- `[MOD]`: the STS2-Agent and STS2MCP documentation

Everything below is unverified in our own game until Phase 6 confirms it. Change a label to `[GAME]` or `[OBS]` once a rule has been seen in a co-op run.

## Lobby and saves
| Rule | Sources | Agree? |
|---|---|---|
| 1–4 players; Steam friends only; no public matchmaking; no couch co-op | A, B | Yes |
| The host creates the run from one of their profiles; each profile holds one co-op campaign; the save belongs to the host | A, B | Yes |
| Duplicate characters are allowed | A, B | Yes |
| The mod's AI teammate instead joins through an offline local connection (`--force-steam off`, `-fastmp join`, port 33771) | `[MOD]` | — |
| **Never load a co-op save with the game's Load button** while using the mod. Use `continue_ai_teammate` (STS2-Agent) or the multiplayer load lobby (STS2MCP). The Load button can reject local-connection player IDs and mark the save corrupt. | `[MOD]` | — |

## Individual and shared
| Rule | Sources | Agree? |
|---|---|---|
| Individual: deck, gold (no shared wallet), energy, relics, potions, card rewards, shop stock, Ancient options | A, B | Yes |
| Shared: map path, encounters, enemies, the turn | A, B | Yes |
| The map path is decided by vote at forks, then a weighted random pick (A) or a tally with random tie-break (B); players can draw on the map | A, B | Mostly (the tie-breaking detail differs) |
| Chests: each player is offered one relic; no two players take the same one; ties are settled by an automatic rock-paper-scissors | A | Single source |
| Rest sites: every option is available to every player; "Mend" heals another player | A | Single source. The run data shows a rest option `CLONE` and others we don't yet know `[PLAYER-DATA]` |

## Combat
| Rule | Sources | Agree? |
|---|---|---|
| Turns are simultaneous; the turn ends when every player has ended theirs (an end-turn vote) | A, B, `[MOD]` (STS2MCP `end_turn` is a vote; `undo_end_turn` retracts it) | Yes |
| **Enemy attacks hit every player** ("an attack of 12 hits each player for 12"); enemies have no individual targeting | B (explicit), A ("no individual targeting") | Consistent, **to verify**: it changes block planning completely |
| Buffs and debuffs from enemies apply to all players | A | Single source |
| Potions can target other players | A, C | Confirmed by the v0.111.1 patch notes: nearly any potion can now be used on another player `[COMMUNITY]`. Potions with `target_type` AnyAlly or AnyPlayer exist `[MOD]` |
| Enemy HP (and damage, per B) grows with party size; no numbers given | A, B | Yes, amount unknown. Measure it (P6.E1.S2) |
| Some boss mechanics scale with players: Vantom's Slippery stacks rise with more players (`[COMMUNITY]` Vantom guide); Knowledge Demon's Ponder heals 30 **per player** (`[COMMUNITY]` KD guide) | Boss guides | Single sources |
| A player at 0 HP is out for the rest of the fight and returns at 1 HP after it; the run ends only when the whole party falls | A (B: "the run ends when the party falls apart") | Consistent |

## Co-op cards `[GAME-EXTRACT]`
Cards that target allies (multiplayer value):

| Owner | Card | Effect (base) |
|---|---|---|
| Ironclad | Demonic Shield | Lose 1 HP; give an ally ? block; exhaust |
| Ironclad | Tank | Gain Tank. **v0.111.1:** you take +50% damage and allies take −50% (was double and half) `[COMMUNITY]` patch notes |
| Colorless | Believe in You | Ally gains 3 energy |
| Colorless | Coordinate | Apply 5 Coordinate to an ally |
| Colorless | Huddle Up | All allies draw 2 |
| Colorless | Intercept | Gain 9 block; apply Covered to an ally (redirect) |
| Colorless | Lift | Give an ally 11 block |
| Colorless | Mimic | Gain ? block; exhaust |
| Colorless | Rally | All allies gain 12 block |
| Defect | Energy Surge | All allies gain 2 energy; exhaust |
| Defect | Ignition | Ally channels Plasma; exhaust |
| Necrobinder | Glimpse Beyond, Legion of Bone | Party-wide effects |
| Regent | Largesse | Gives an ally a generated card |

Community tier data from MetaBot rates Tank and Demonic Shield highly (S on its list), which reflects multiplayer runs. Rate them low in solo play.

## Changed on v0.111.1 (main since 2026-11-16) `[COMMUNITY]`
Source: wiki V0.111.1 – Major Update 3 (`knowledge/version-delta-v0.111.1.md`), accessed 2026-11-19.
- **Enemy block scaling is lower in 2-player runs.** Multiplayer scaling of Artifact, Slippery (Vantom) and Skittish was already reduced in v0.107.1.
- **Nearly any potion can be used on another player.** A Block Potion or a heal on the teammate about to take the big hit is a real option; the turn planner does not model ally targets yet.
- **New Ironclad multiplayer cards:** Midnight (Rare; 60 (72) damage, cheaper for each card exhausted by anyone), Blaze (gives another player 5 (7) Strength), Outrage (0 cost, 9 (13) damage, copies itself into every player's discard pile).
- **New Necrobinder multiplayer cards:** Underworld (Doom equal to the attack damage other players deal this turn), Soulbound (Souls you create also go to an ally's draw pile), Cacophony (every 33 cards drawn by all players: 66 (99) damage to a random enemy).
- **Tank** rebalanced (above). Legion of Bone no longer exhausts.
- Ghost Seed no longer makes other players' generated Strikes and Defends Ethereal (bug fix).

## Progression
| Rule | Sources | Agree? |
|---|---|---|
| Multiplayer ascension is a separate track from solo ascension | A, B | Yes |
| The available ascension is capped by the lowest-ranked player (B), or each player must have the level unlocked (A) | A, B | Same meaning |
| Finishing a multiplayer run unlocks the next multiplayer ascension for each character present | A | Single source |

## Implications for the Agent as teammate (feeds `playbooks/coop.md` in Phase 6)
1. If every attack hits every player, **each player blocks for themselves**. Party block cards (Rally, Lift, Intercept, Demonic Shield) become strong. Verify this first.
2. Bigger enemy HP pools make scaling and hit-all damage worth more. Long fights favour Strength and exhaust engines.
3. Map votes: agree on the path in chat before voting, so the random pick can't split the plan.
4. Chest relics: say which relic you want before choosing, to avoid ties.
5. A downed player returns at 1 HP. Avoid leaving the downed teammate exposed in the next hallway fight. Rest-site "Mend" exists for this.
