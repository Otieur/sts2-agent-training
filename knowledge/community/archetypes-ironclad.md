# Ironclad Archetypes

Last updated 2026-11-19. Card functions are `[GAME-EXTRACT]` (`knowledge/cards/ironclad.md`). Archetype claims are `[COMMUNITY]` (sources in `sources.md`). Commit signals are `[HYPOTHESIS]` until Phase 4 tests them. The Player's decks showed no clear archetype clusters (`reports/phase1/archetypes-ironclad.md`), so this file adds structure the history does not have.

Community tiers in brackets come from `ironclad-tiers.md` (consensus, mostly v0.107-era sources).

---

## 1. Strength scaling
- **Engine:** Demon Form (+2 Strength each turn, power) [S], Inflame (+2 Strength) [D–C], Dominate (+? Strength, exhausts) [A], Fight Me (5×2 damage, +2 Strength for you, +1 for the target) [D], Brand (exhaust a card, +1 Strength, costs 1 HP) [A], Rupture (Strength when you lose HP) [B].
- **Payoffs (multi-hit):** Twin Strike (5×2), Sword Boomerang (3×3 random), Thrash (4×2), Dismantle (8×?), Tear Asunder (5×?) [A], Fiend Fire (7× per card exhausted) [A], Whirlwind (5×X to all).
- **Commit signal:** one Strength source that keeps paying (Demon Form, or Dominate and Brand together) plus at least two multi-hit attacks by mid-Act 2. One Inflame alone is not a plan. `[HYPOTHESIS]`
- **Strengths:** scales through long boss fights (6–10 turns). Multi-hit plus Strength also clears Vantom's Slippery stacks.
- **Weaknesses:** slow setup turns. Fight Me also buffs the enemy. Demon Form costs 3 energy on a turn you may need to block.
- **The Player:** loves Dominate (95% pick rate) and Fight Me (79%), but skips the common multi-hit payoffs (Twin Strike 19%, Sword Boomerang 17%). Strength without payoffs is a half-built engine.

## 2. Exhaust engine
- **Engine:** Corruption (ancient, power) [S], Dark Embrace (draw when a card is exhausted) [B, sources disagree], Feel No Pain (block when a card is exhausted) [B].
- **Exhaust outlets:** Burning Pact (exhaust 1, draw 2) [B], True Grit (7 block, exhaust a card) [C–D], Second Wind (exhaust, 5 block) [B], Stoke (exhaust, draw ?) [S], Brand [A], Thrash, Cinder, Drum of Battle (exhausts a card at the start of each turn) [C], Fiend Fire [A].
- **Payoffs:** Ashen Strike (damage scales, presumably with exhausted cards; to verify) [C], Pact's End (0 cost, 17 to all enemies; condition to verify) [B], Feel No Pain block, Dark Embrace draw.
- **Commit signal:** Feel No Pain or Dark Embrace plus two exhaust outlets. Corruption makes it a full engine. `[HYPOTHESIS]`
- **Strengths:** card quality improves as the bad cards burn away. Block and draw come for free.
- **Weaknesses:** needs specific cards to come together. Exhausting the wrong card early can lose a fight.

## 3. Block and Barricade
- **Engine:** Barricade (block does not clear) [B, sources disagree], Unmovable (doubles block gained) [S], Juggernaut (deal damage when gaining block) [B, sources disagree].
- **Block sources:** Impervious (30, exhausts) [A], Colossus (5 + Colossus power) [A], Crimson Mantle (block and damage each turn) [A], Stone Armor (4 Plating) [D], Flame Barrier (12 + thorns) [C], Evil Eye (8) [D], Shrug It Off (8, draw 1) [B], Blood Wall (16, costs 2 HP) [D].
- **Payoff:** Body Slam (damage equal to block) [C], Juggernaut.
- **Commit signal:** Barricade or Unmovable plus Body Slam or Juggernaut. `[HYPOTHESIS]`
- **Strengths:** very safe in long fights. The natural co-op tank (Taunt applies Vulnerable and blocks).
- **Weaknesses:** low damage until the payoff arrives. Slow against scaling bosses unless Body Slam or Juggernaut is online.

## 4. HP as a resource
- **Costs:** Offering (lose 6: +2 energy, draw 3) [S], Bloodletting (lose 3: +2 energy) [B], Brand [A], Hemokinesis (lose 2: 14 damage) [D], Blood Wall [D], Breakthrough (lose 1: 9 to all) [D].
- **Payoffs:** Rupture (Strength per HP lost) [B], Inferno (damage when hit, and each turn) [C], Crimson Mantle [A].
- **Support:** Burning Blood (the starter relic) heals 6 after each combat `[COMMUNITY]`. Feed raises max HP [S].
- **Commit signal:** Rupture or Inferno plus two cheap HP costs. Offering is good in any deck. `[HYPOTHESIS]`
- **Weaknesses:** at high ascension with fewer heals, HP spent early is HP missing at the boss. This conflicts with the Phase 1 finding that losing runs fall behind on HP during Act 1. Use with care.

## 5. Vulnerable
- **Sources:** Tremble (2 Vulnerable, 1 cost, no damage) [D], Molten Fist (10 damage + ? Vulnerable, exhausts) [D], Taunt (7 block + 1 Vulnerable) [C], Uppercut (13 damage + Weak + Vulnerable) [C], Thunderclap (4 to all + Vulnerable) [D], Break (ancient: 20 damage + 5 Vulnerable) [S on the 0.113 beta, a trap on 0.107 per Spire Codex].
- **Payoff:** Cruelty (25 Cruelty, presumably extra damage against Vulnerable enemies; to verify) [B].
- **Community view:** the 0.113 beta made Vulnerable "its own archetype" (Nat 1 Gaming). On v0.107 the Vulnerable-only cards rate low.
- **The Player:** takes Tremble (44%) and Molten Fist (42%) much more often than the consensus suggests. This is the biggest gap in habit (`discrepancies.md`).

## 6. Energy and tempo (fits any deck)
- Pyre (+1 max energy, power) [A], Offering [S], Bloodletting [B], Forgotten Ritual (+3 energy) [C], Expect a Fight (+? energy) [B], Stampede (auto-plays a card each turn end) [C], Hellraiser (auto-plays drawn cards; presumably attacks) [A], Aggression (adds and upgrades a card each turn) [B], Cascade (auto-play X cards) [S].
- These are the safest picks when the deck has no direction yet.

---

## Drafting guidance (v1)
1. Acts 1 and early 2: take strong cards from any archetype that fill the deck's gaps (triangle plus scaling). Energy and tempo cards are always fine.
2. By mid-Act 2: commit to one engine if its core has appeared (the commit signals above). Otherwise keep drafting good stand-alone cards.
3. Strength without multi-hit payoffs, or exhaust outlets without an exhaust payoff, are half-built engines. Value the missing half higher.
4. Boss-specific needs override archetype loyalty (see `knowledge/bosses/`).
