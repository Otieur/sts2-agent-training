# Co-op Playbook

Version: v0 (draft) · Target game: v0.111.1 · Last updated: 2026-11-19 · Status: written before any co-op play, from `knowledge/coop-rules.md`, the STS2-Agent documentation and the solo playbooks. Every rule is `[HYPOTHESIS]` unless labelled otherwise. The first co-op runs are shakedowns (`docs/phase-6-coop.md`).

The solo playbook (`playbooks/ironclad.md`, or the Agent's chosen character) applies unless this file says otherwise. Same labels and precedence (`docs/README.md`).

---

## 1. Verify first (first co-op fight, P6.E1.S2)
Two unknowns change everything below. Check them before trusting any co-op rule.

| Question | Why it matters | How to check |
|---|---|---|
| Does an enemy attack hit every player, or one target? | If every player is hit, each player blocks for themselves and party block cards become strong. If one target, block planning is per target and Tank / Intercept decide who is hit. | Read `combat.enemies[].intents` on both instances in the first fight, and compare both players' HP after the enemy turn (`tools/sts.py party`) |
| How do enemy HP and damage scale for 2 players? | Path costs, elite risk and the boss plans' HP targets | Compare `combat.enemies[].base_max_hp` with `max_hp` (STS2-Agent reports both) |

Also note: Vantom's Slippery stacks and Knowledge Demon's Ponder heal scale with players `[COMMUNITY]`, single sources each. Since v0.111.1, enemy block scaling in 2-player runs is lower `[COMMUNITY]`.

## 2. Communication protocol (P6.E4)
### 2.1 Turn huddle
On turns that matter (elites, bosses, big incoming damage, possible lethal), post within about 15 seconds of the turn starting:

`Incoming: <per player> · My plan: <cards → targets> · Need from you: <"block 12" / "kill the left one" / nothing>`

On routine turns, say nothing unless asked. Use `tools/sts.py party` to see both hands and the enemies, then `tools/plan_turn.py` for the Agent's own hand.

### 2.2 The Player's shorthand
| Command | Meaning | The Agent's reply |
|---|---|---|
| `focus <left/right/name>` | Target that enemy | "Focusing <name>." |
| `I block` / `you block` | Who takes the defence this turn | "OK, I'll attack." / "OK, blocking." |
| `go` / `wait` | End the turn now / hold the end-turn vote | "Ending." / "Holding." |
| `pot <name>` | Use that potion (on the Player if it targets an ally) | "Using <potion>." |
| `mend me` | Use the rest site's Mend on the Player | "Mending you." |
| `your call` | The Agent decides | One line with the decision and reason |

Each command gets one short confirmation. If a command would be fatal for either player, say so first in one line and wait.

### 2.3 Map and rewards
- **At act start:** propose a route with its reasons (`tools/path.py`, using the lower of the two players' HP for elite and rest decisions). The Player agrees or edits. Both vote the agreed route; never vote first and explain later.
- **Chests:** say which relic you want before choosing, and avoid the Player's pick (no two players can take the same relic; ties go to rock-paper-scissors).
- **Shops and card rewards:** mention synergy with the Player's deck when it matters (for example, Vulnerable sources when the Player's deck hits many times).

## 3. Role split (P6.E5.S2, provisional until the pairing is chosen in P5.E6.S2)
- **Default:** The Agent complements the Player's deck. If the Player's deck scales slowly, the Agent drafts front-loaded damage and hit-all damage for hallways and Act 1 elites; if the Player's deck has the burst, the Agent drafts block, debuffs and scaling for bosses.
- **Debuffs are worth more:** Vulnerable and Weak on an enemy help both players' damage and defence. Raise Vulnerable sources one tier in co-op.
- **Party block cards** (Rally 12 to all, Lift 11 to an ally, Intercept, Demonic Shield) are strong if attacks hit every player (section 1). Rate them low until that is verified.
- **Tank** (Ironclad): since v0.111.1 you take +50% damage and allies take −50%. Worth taking only when the Agent's deck blocks well and the Player's deck does not.

## 4. Pathing and HP (co-op)
- Use the **lower HP player** for the elite rule (avoid elites when either player is under 50%) and for rest-site thresholds.
- Enemy HP is scaled up for 2 players: fights last longer, so scaling and hit-all damage gain value and the solo benchmark medians underestimate damage until co-op benchmarks exist (`metrics/coop.csv`).
- A downed player returns at 1 HP after the fight. Never path into an elite with a teammate at 1 HP.

## 5. Rest sites (co-op)
- **Mend** heals another player `[COMMUNITY]`, single source. Use it when the teammate would fall under the solo rest threshold for the next boss and the Agent's own HP is above it.
- Otherwise each player follows their own solo rest rule.

## 6. Potions (co-op)
- Nearly any potion can be used on another player since v0.111.1 `[COMMUNITY]`.
- Priority: prevent a player from going down. A Block Potion on the teammate who would drop to 0 beats any damage potion.
- Debuff potions on the enemy (Weak, Vulnerable) help both players: use them on the biggest-hit turn.

## 7. Downed players
- A player at 0 HP sits out the rest of the fight and returns at 1 HP; the run ends only when the whole party is down `[COMMUNITY]`, two sources.
- If the teammate is down, the Agent plays safe (the `safe` plan of `tools/plan_turn.py`) and does not take optional risks until the fight ends.
- After the fight: rest or Mend before the next elite.

## 8. Co-op cards (P6.E5.S1, provisional tiers)
| Card | Owner | Effect (v0.111.1) | Co-op tier `[HYPOTHESIS]` |
|---|---|---|---|
| Rally | Colorless | All allies gain 12 block | A if attacks hit everyone, else B |
| Lift | Colorless | Give an ally 11 block | B |
| Intercept | Colorless | 9 block; redirect an ally's incoming attacks to you | B (A for a high-block deck) |
| Huddle Up | Colorless | All allies draw 2 | B |
| Believe in You | Colorless | An ally gains 3 energy | B |
| Demonic Shield | Ironclad | Lose 1 HP; give an ally block; exhaust | B |
| Tank | Ironclad | You take +50%, allies take −50% | C (B with a block engine) |
| Midnight | Ironclad | Rare; 60 (72) damage, cheaper per card exhausted by anyone | B in an exhaust party |
| Blaze | Ironclad | Give another player 5 (7) Strength | A if the Player's deck hits many times |
| Outrage | Ironclad | 0 cost, 9 (13) damage, copies into every player's discard pile | B |
| Underworld | Necrobinder | Doom equal to other players' attack damage this turn | A with a hard-hitting teammate |
| Soulbound | Necrobinder | Souls you create also go to an ally's draw pile | C |
| Cacophony | Necrobinder | Every 33 cards drawn by all players: 66 (99) damage to a random enemy | C |

## 9. Tooling
- `tools/sts.py --mod sts2agent --instance teammate ...` acts only on the Agent's window; acting on the host or on a multiplayer run without `--instance teammate` is refused.
- `tools/sts.py --mod sts2agent party` shows both players, both hands and the enemies, and checks that both instances agree (desync check).
- Never use the game's Load button for a co-op save; use the mod's Continue (`docs/phase-6-coop.md`).

## 10. Changelog
- **v0 (2026-11-19, overnight):** first draft from the co-op rules and the v0.111.1 patch notes, before any co-op play.
