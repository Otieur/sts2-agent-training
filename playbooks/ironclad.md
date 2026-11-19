# Ironclad Playbook

Version: v2.5 · Knowledge base: the Player's history v0.107.1; game data extract older (pre-v0.107.1) · Target game: v0.111.1 (main since 2026-11-16; see `knowledge/version-delta-v0.111.1.md`) · Last updated: 2026-11-19 · Status: draft (v2 adds game data, community knowledge and boss plans; not yet tested in the Agent's own runs)

The goal is strong play, judged by results. Every rule carries a provenance label and an evidence pointer. Conflicts follow the precedence in `docs/README.md`:

`[GAME]` > `[OBS]` > `[GAME-EXTRACT]` > `[COMMUNITY]` consensus > `[PLAYER-DATA]` outcomes > single `[COMMUNITY]` > `[PLAYER-SAID]` and habits > `[HYPOTHESIS]`

**Where things are:**
- Game mechanics: `knowledge/mechanics.md`
- Ascension: `knowledge/ascension.md`
- Cards with roles: `knowledge/cards/ironclad.md`
- Community tiers: `knowledge/community/ironclad-tiers.md`
- Archetypes: `knowledge/community/archetypes-ironclad.md`
- Bosses: `knowledge/bosses/`
- Elites and hallway fights: `knowledge/enemies/`
- History analysis: `reports/phase1/`
- Deck features per encounter: `reports/phase2/deck-features-by-encounter.md`

---

## 1. Win conditions and overview

- **Runs are lost early, at bosses.** In the Player's history, 55% of deaths happen in Act 1 (22/40) and 14 at the Act 1 boss. By fight type: 24 deaths to bosses, 10 to elites, 6 in hallways. `[PLAYER-DATA]`
  - **Priority 1:** reach each boss with a deck built for *that* boss (section 10) and enough HP for its typical damage.
- **Bosses are long:** median 6–10 turns. They need damage that holds up or grows (scaling), not only front-loaded damage. The Knowledge Demon history supports this: fatal decks had fewer powers, energy and Strength cards. `[PLAYER-DATA, weak]`
- **The boss is known at act start** (the map state holds it). Read it on floor 1 of every act. `[GAME-EXTRACT]` via STS2MCP
- **HP is a per-act budget.** The game heals at each act's Ancient: 100% of missing HP at A0–1, 80% from A2. `[PLAYER-DATA]`
- Burning Blood heals 6 after each won fight. `[COMMUNITY]`

## 2. Card evaluation

### 2.1 Procedure (in order)
1. **Deck needs.** Measure the deck against five needs, not feel. Run `python3 -I tools/deck_metrics.py --deck <card ids>` for damage and block per turn (random 5-card hands, 3 energy, base numbers).
   - **Corner targets on arrival at the boss** `[HYPOTHESIS H9]`, from `reports/phase2/deck-strength.md` (all characters, 356 boss fights):
     - Act 1: block per turn at least 10, and 2+ scaling cards (Powers or Strength cards)
     - Act 2: 4+ scaling cards
     - Act 3: block per turn at least 8
   - **Raw damage is not enough.** Decks with the most raw damage died *more* often at bosses (Act 1: 28% against 18%). Fatal Ironclad Act 1 decks had more damage (16.8 against 15.1 per turn) and less block (8.4 against 9.6). Once raw damage is about the starter deck's (15 per turn), add block and scaling before more attacks.
   - **Act 1 timing:** elites reward front-loaded damage, bosses reward block and scaling. Act 1 elites: highest raw-damage tercile 3/62 fatal against 7–9/62 for the others; lowest block tercile 10/62 fatal. So draft attacks for the first elites (floors 5–10), then shift to block and scaling before the Act 1 boss. `[PLAYER-DATA, observational]`
   - **Attack:** damage per turn for the next elite and the boss.
   - **Defence:** block for the biggest hit of the next elite and the boss (boss table, section 10).
   - **Operations:** card draw and energy.
   - **Scaling:** Strength, powers, energy growth.
   - **Attack shape:** what the next boss needs. Vantom wants many hit instances and punishes hit-all single hits. Entomancer punishes many hits. Skulking Colony caps damage per turn. The Kin wants hit-all damage.
2. **Boss fit** overrides tier: draft toward the act boss's deck checklist.
3. **Tier** from 2.2. Within a tier, prefer the card that fills the weakest need.
4. **Archetype fit** once committed (section 3).
5. **Skip** if nothing improves the deck for the coming fights. Bigger decks skip more: the Player's skip rate rises from 5% under 15 cards to 50% at 30+, a sensible pattern. `[PLAYER-DATA]`

`tools/draft.py` applies steps 1–5 mechanically (tier, v0.111.1 adjustments, boss fit, corner-target needs, engines, a skip bar rising 0.1 per card above 15) and prints the reasons. It cannot see relics, upgrades, Strength scaling of multi-hit cards or `?` card values; override it with a stated reason when those matter. `[HYPOTHESIS]` weights

### 2.2 Card tiers (community consensus, v0.107-era weighted)
From `knowledge/community/ironclad-tiers.md` `[COMMUNITY]`. † marks cards where sources disagree by 2+ tiers. Card roles are `[GAME-EXTRACT]`.

- **S:** Offering, Cascade, Conflagration, Corruption, Demon Form, Feed, Stoke, Unmovable
- **A:** Crimson Mantle, Impervious, Fiend Fire, Battle Trance, Brand, Colossus, Dominate, Hellraiser, One-Two Punch†, Pyre†, Tear Asunder†
- **B:** Barricade†, Bloodletting†, Burning Pact, Cruelty, Feel No Pain, Juggernaut†, Shrug It Off†, Aggression†, Mangle, Pact's End, Thrash†, Bully†, Dark Embrace†, Expect a Fight, Flame Barrier, Forgotten Ritual, Pommel Strike†, Rupture, Second Wind†, Stampede†, True Grit
- **C:** Break†, Armaments†, Ashen Strike, Body Slam, Drum of Battle†, Howl from Beyond†, Inferno†, Juggling†, Pillage, Rage, Stomp†, Stone Armor, Taunt†, Uppercut†, Vicious
- **D:** Anger, Blood Wall, Bludgeon†, Dismantle†, Evil Eye, Fight Me†, Headbutt†, Inflame, Molten Fist, Primal Force†, Spite, Sword Boomerang, Tremble, Unrelenting, Whirlwind†, Breakthrough, Hemokinesis, Infernal Blade, Perfected Strike, Rampage, Setup Strike, Twin Strike, Cinder, Havoc, Iron Wave, Thunderclap
- **Multiplayer-only value:** Tank, Demonic Shield. Rate them low solo.

**Changed on v0.111.1** (`knowledge/version-delta-v0.111.1.md`), adjust the tiers above:
- **Buffs:** Demon Form (3 Strength per turn, was 2), Mangle (20, was 15), Pact's End (18), Howl from Beyond (18), Rampage (10), Setup Strike (3 Strength), Forgotten Ritual (no exhaust needed).
- **Nerfs:** Colossus (4 block), Crimson Mantle (7 block), Taunt (6 block).
- **Expect a Fight** is a new card: 3 cost, 15 block + 5 per Strength. Rate it B in Strength decks, C otherwise `[HYPOTHESIS]`.
- **Rarity:** Dominate is now Rare, so expect it less often. Bloodletting is now Uncommon, Cruelty Uncommon, Taunt Common.

**Context overrides** (tier is a default, not a rule):
- **Vantom is the Act 1 boss:** raise cheap and multi-hit attacks (Anger, Twin Strike, Sword Boomerang, Thrash, Fight Me). They clear Slippery. Lower hit-all single-hit cards (Breakthrough, Thunderclap). `[GAME-EXTRACT]` mechanics, `[HYPOTHESIS]` value
- **Strength engine in the deck:** raise multi-hit payoffs one tier. `[COMMUNITY]`
- **Exhaust engine** (Feel No Pain or Dark Embrace in the deck): raise exhaust outlets one tier.
- **Second copies:** usually a tier lower, except engine pieces the deck needs twice. `[HYPOTHESIS]`

### 2.3 Upgrade priority (v2)
Upgrade sizes per card: `knowledge/cards/ironclad-upgrades.md` `[GAME-EXTRACT]`. Biggest jumps include Offering, Pyre and Bloodletting energy, Impervious +10 block, Bludgeon +10, Pact's End +6, Unrelenting +6. Cards marked "not in the extract" likely get cheaper (Barricade, Corruption, Body Slam, Armaments' text change).
Engine pieces first: Demon Form, Corruption, Barricade, Feel No Pain, Body Slam. Then cards whose upgrade changes their function (Armaments, True Grit gain card choice when upgraded `[GAME-EXTRACT]`). Then the best attack. The Player's habit of upgrading Armaments first is a reasonable baseline for decks without an engine. `[COMMUNITY]` + `[PLAYER-DATA]`

## 3. Archetypes and commit signals
See `knowledge/community/archetypes-ironclad.md`. Summary:

| Archetype | Engine | Payoffs | Commit signal `[HYPOTHESIS]` |
|---|---|---|---|
| Strength | Demon Form, Dominate, Brand, Fight Me, Rupture | Multi-hit: Twin Strike, Sword Boomerang, Thrash, Tear Asunder, Fiend Fire, Whirlwind | A repeating Strength source plus 2 multi-hit attacks by mid-Act 2 |
| Exhaust | Corruption, Feel No Pain, Dark Embrace | Fiend Fire, Ashen Strike, Pact's End | Feel No Pain or Dark Embrace plus 2 exhaust outlets |
| Block | Barricade, Unmovable, Juggernaut | Body Slam, Juggernaut | Barricade or Unmovable plus Body Slam or Juggernaut |
| HP as a resource | Offering, Bloodletting, Brand | Rupture, Inferno, Crimson Mantle | Rupture or Inferno plus 2 cheap HP costs; careful at high ascension |
| Tempo | Pyre, Offering, Stampede, Hellraiser, Aggression, Cascade | (any) | Always good; safest when no direction yet |

The Player's decks showed no archetypes (`reports/phase1/archetypes-ironclad.md`). Commit when the core appears. Otherwise draft for needs.

## 4. Path planning and HP budget

1. **At act start:** read the boss and open its plan. Choose a path by elites, rest sites before elites and the boss, shops, and expected HP cost (sum of benchmark medians; p75 for elites). Write the plan in the run journal. `tools/path.py` enumerates every route with these rules (room economics below, the H5 elite bands, the boss arrival curve, the section 5 rest rule) and ranks them. Its risk weight (12 / 16 / 25 by act) comes from the history: an Act 1 elite went with about +3.5 points of final win rate among Act 1 survivors (confounded). `[HYPOTHESIS]`
2. **Elites under 50% HP: avoid.** `[PLAYER-DATA]` outcome, n=308 elite fights in Acts 1–2, all characters, abandoned runs excluded:
   - 24% of fights entered under 50% HP ended the run (Ironclad 4/16)
   - 8% at 50–70% (Ironclad 3/32)
   - 3% at 70% or more (Ironclad 2/31)
   - Exception: the elite is one the deck handles easily (Phantasmal Gardeners, median 12) and the alternative path is worse.
3. **Elites at 50–70% HP:** take one only if current HP minus its p75 leaves enough to reach the next rest site.
4. **Re-plan** if HP falls more than 15% of max below the plan, a key card or relic changes the deck's needs, or a detour is forced.
5. **Room economics** (`reports/phase2/room-values.md`, all characters, mean per visit) `[PLAYER-DATA]`:

   | Room | HP change (Act 1 / 2 / 3) | What it gives |
   |---|---|---|
   | Monster | −6% / −10% / −8% | 0.6–0.9 cards (fewer in Act 3), 0.45–0.55 potions, 12–14 gold |
   | Elite | −23% / −28% / −25% | about 0.9 relics, 0.7–0.8 cards, 30 gold |
   | ? room | −1% / −1% / −2% (a fight about 20% of the time) | 0.5–0.8 cards, 0.2–0.4 relics, 8–22 gold |
   | Shop | +1% to +4% | 0.6–1 card and 0.6–1 relic bought |
   | Treasure | 0 | 1 relic, gold |

   **Path heuristics** `[HYPOTHESIS]`:
   - ? rooms are the cheapest source of value. Prefer them over monsters when HP is below plan.
   - Take monsters when the deck still needs cards, early in Act 1.
   - Take an elite only when HP minus the elite's p75 stays above 50%. An elite costs about a quarter of max HP for a relic.

**Elite reference** (Ironclad HP lost per fight, median / p75; notes in `knowledge/enemies/`):

| Act | Elite | Median / p75 | Fatal | Key mechanic `[GAME-EXTRACT]` | Answer |
|---|---|---|---|---|---|
| 1 | Bygone Effigy | 29 / 39.5 | 1/12 | Sleeps; wakes with +10 Strength (slash 25); Slow (takes more per card played) | Burst during sleep with many cards; block 25 |
| 1 | Terror Eel | 29 / 39 | 0/5 | First damage stuns it; then 99 Vulnerable on you | Hit it on turn 1; block ×1.5 hits |
| 1 | Byrdonis | 22.5 / 32.8 | 3/10 | +Strength every turn (Territorial) | Kill fast; never under 50% HP |
| 1 | Phrog Parasite | 19 / 30 | 1/9 | Spawns Wrigglers on death; Infection cards | Save hit-all damage for wave 2 |
| 1 | Skulking Colony | 19 / 35 | 1/9 | Loses at most 20 HP per turn (v0.107.1); 75 HP; no block | About 20 damage a turn for 4 turns; block Zoom 16 on turns 1–2 |
| 1 | Phantasmal Gardeners | 12 / 19 | 0/8 | Several small bodies | Hit-all damage; safest elite |
| 2 | Decimillipede | 36.5 / 39.2 | 0/8 | Segments reattach | Kill segments together; hit-all damage |
| 2 | Entomancer | 30 / 38 | 3/13 | **Each damage instance adds a card to your draw pile** | Few big hits, not multi-hit; block Bees 3×7 |
| 2 | Infested Prisms | 27 / 38.8 | 0/8 | Reworked (v0.106): each Skill you play gives you Tainted, +3 damage per hit of its attacks, growing over the fight | Play few Skills; block with big ones; prefer Attacks and Powers |
| 3 | Mecha Knight | 34 / 43 | 1/5 | Artifact; Heavy Cleave 35 (40 after Windup) | Block 40; strip Artifact first |

**v0.111.1 changes** (benchmarks above are v0.107.1): Mecha Knight's Flamethrower turn now also deals 8 (12); Entomancer has 165 HP at A8+ (was 155). `knowledge/version-delta-v0.111.1.md`

## 5. Rest-site policy

- **Before a boss** `[HYPOTHESIS H1]`, tested in Phase 4 against the Player's baseline (equally likely to heal or smith at 37% HP before a boss):
  - Acts 1–2: rest if HP is below the boss's median damage **for the current ascension band** + 10 (`data/benchmarks/ironclad-encounters-by-band-v0.107.1.csv`; all-characters band file where Ironclad has fewer than 5 fights). Otherwise smith. The pooled numbers in section 10 are mostly A7–A10. Both practice post-mortems (`runs/examples/`) died with HP exactly equal to the A10 band median, where the band rule said rest and the pooled rule said smith.
  - **Act 3 and the A10 double boss: rest if HP is below 70%.**
  - Evidence (`reports/phase2/boss-arrival-hp.md`) is mixed. Boss death rates fall steeply with arrival HP, most of all in Act 3. But the Player's heals and smiths at the same HP were followed by almost the same boss death rate (31% against 30% under 50% HP). Confounding cuts both ways.
- **Before an elite on the path:** rest if HP minus the elite's p75 would leave less than 50% of max for the next fights. `[HYPOTHESIS]`
- **Otherwise:** smith at 50% HP or more. Under 35%, rest. In between, decide by the next two fights' benchmark cost.
- A rest heals 30% of max HP, rounded down (24 on 80), capped at max HP. 237 of 297 heals match exactly; larger ones are presumably relic boosts. `[PLAYER-DATA]`

## 6. Shop policy (including removal)

- **Priority** `[HYPOTHESIS]`:
  1. A relic or card that fills the current boss's checklist
  2. An S or A-tier card
  3. **Removal of a removable curse** (Injury, Clumsy and others; Ascender's Bane is Eternal)
  4. Removal of a Strike in a small Act 1 deck
  5. Other relics
  6. Potions (especially Weak, Block and Strength for the coming boss)
- **Removal** `[HYPOTHESIS H4]`: remove a Strike at the first Act 1 shop when affordable, against the Player's relic-first baseline. Arithmetic: one removal is about a 3 percentage point improvement in draw quality. Act 1 basic-removal runs survived Act 1 in 79% of cases against 50% (confounded).
- From A3, gold is about 25% scarcer. `[PLAYER-DATA]`
- Ascender's Bane is Eternal and probably cannot be removed. `[GAME-EXTRACT]` keyword

## 7. Events and Ancients
- No outcome-backed event rules yet. Event options and risk tags are in `knowledge/data/extract-2026-09-21/events.json` and `event_options.json` `[GAME-EXTRACT]`. The Player's choices are the baseline (`reports/phase1/path-ironclad.md`).
- Observed safe value `[PLAYER-DATA]`:
  - Sunken Treasury, "Second chest": +342 gold on average
  - Wellspring, "Bathe": no HP cost
- Observed costly `[PLAYER-DATA]`:
  - Slippery Bridge: −6.8 HP on average
  - Whispering Hollow: −6 HP
- **Ancients:** relic text in `relics.json` `[GAME-EXTRACT]`. Rate by boss fit and scaling.

## 8. Potion policy
- **Use freely in elites and bosses.** The Player's baseline is good: about 1.1 per boss fight and 0.8 per elite, and only 4 of 40 deaths with an unused potion. `[PLAYER-DATA]` outcome
- From A4 there are 2 slots instead of 3 `[PLAYER-DATA]`. Don't hoard.
- Each boss plan has a potion section. The general rules:
  - Weak potions go on the boss's biggest-hit turn.
  - Strength potions never go before Vantom's Slippery is gone.
  - Debuff potions only after Artifact is stripped (Aeonglass, Mecha Knight).

## 9. Combat checklist
1. Read every intent. Total the incoming damage. Note special powers (Slippery, Hardened Shell, Personal Hive, Territorial, Thorns, Flutter).
2. Check for lethal. Killing an attacker removes its damage.
3. Block needed = incoming damage minus what the act's HP budget allows.
4. Order: draw and energy first; powers early in long fights; Vulnerable before attacks; Weak before the enemy's big turn.
5. **Encounter rules:**
   - Vantom: count Slippery stacks.
   - Entomancer: minimise hit count.
   - Skulking Colony: don't overkill the per-turn cap.
   - Toadpoles with Thorns: single hits.
   - Exoskeletons (Hard to Kill): many small hits.
   - Infested Prisms: few Skills (each gives you Tainted, +3 per hit of its attacks).
   - Kaiser Crab: end each turn facing the claw with the bigger next hit (back attacks ×1.5, to confirm).
   - Lagavulin Matriarch: set up while it sleeps; first damage on the last sleep turn.
6. Potions when they prevent serious HP loss or win a dangerous fight.
7. Check `end_turn_will_kill_player` and `lethal_risks` before ending the turn.
8. Write down the expected HP after the enemy turn and compare it next turn. Use `tools/calc.py` for exact numbers.
9. **Search the turn:** `tools/plan_turn.py` enumerates the hand and prints the safest plan and the best damage-for-HP plan, with targets. Choose between them by the act's HP budget (section 4): safe when HP is below plan or before a big hit, balanced when ahead. It does not model draw, relics, potions, Thorns or per-turn caps; re-run after drawing. `[HYPOTHESIS]` until the arithmetic is confirmed in game
10. **Targeting** (multi-enemy fights) `[HYPOTHESIS]`, also what `tools/plan_turn.py` searches for:
    - Kill first the enemy whose death removes the most incoming damage per point of HP and block you must spend. A kill this turn beats spreading damage.
    - Buffers and summoners next (they raise everyone's damage), then the highest single hit. Encounter notes override: the Kin Priest probably ends the fight; Kaiser Crab focuses Rocket; Phrog Parasite spawns Wrigglers on death.
    - Hit-all attacks are worth it when they kill at least one enemy or hit three or more. Not against Slippery.
    - Avoid overkill: put the spare damage on the next target. Against Skulking Colony, stop at the per-turn cap (20).

## 10. Boss preparation

| Act | Boss | Median / p75 | Fatal (Ironclad) | Rest if HP below | The one thing to prepare `[GAME-EXTRACT]` mechanics |
|---|---|---|---|---|---|
| 1 Overgrowth | [Vantom](../knowledge/bosses/VANTOM_BOSS.md) | 48 / 57.5 | 6/11 | ~58 | 9 hit instances to clear Slippery; block 27 on turn 3 |
| 1 Overgrowth | [Ceremonial Beast](../knowledge/bosses/CEREMONIAL_BEAST_BOSS.md) | 39 / 45.5 | 1/7 | ~49 | Front-load damage to break 150 Plow (stuns it, resets its Strength) |
| 1 Overgrowth | [The Kin](../knowledge/bosses/THE_KIN_BOSS.md) | 34.5 / 41.2 | 0/8 | ~45 | Hit-all damage for the followers |
| 1 Underdocks | [Waterfall Giant](../knowledge/bosses/WATERFALL_GIANT_BOSS.md) | 38 / 41 | 2/5 | ~48 | Fast kill; bank block for the death explosion |
| 1 Underdocks | [Soul Fysh](../knowledge/bosses/SOUL_FYSH_BOSS.md) | 33 / 41 | 3/7 | ~43 | Exhaust Beckon cards; burst outside Intangible |
| 1 Underdocks | [Lagavulin Matriarch](../knowledge/bosses/LAGAVULIN_MATRIARCH_BOSS.md) | 28 / 40.5 | 2/8 | ~38 | Set up while it sleeps; kill before repeated Soul Siphons |
| 2 Hive | [Knowledge Demon](../knowledge/bosses/KNOWLEDGE_DEMON_BOSS.md) | 45 / 59.8 | 4/12 | ~55 | Scaling and energy (about 60 damage per turn over 7 turns); curse choice: usually Sloth (at most 3 cards per turn), Disintegration last |
| 2 Hive | [Kaiser Crab](../knowledge/bosses/KAISER_CRAB_BOSS.md) | 43.5 / 48.5 | 2/6 | ~54 | Focus Rocket; block 31+ on the Laser and end that turn facing Rocket (back attacks ×1.5); kill a claw with the turn's last attack (Crab Rage: the other gets 99 Block and 5 Strength) |
| 2 Hive | [The Insatiable](../knowledge/bosses/THE_INSATIABLE_BOSS.md) | 31.5 / 45.8 | 2/6 | ~42 | Watch the Sandpit timer; energy for Frantic Escape |
| 3 Glory | [Aeonglass](../knowledge/bosses/AEONGLASS_BOSS.md) | 48 / 70 | 0/5 | ~58 (arrive high) | Fewer, bigger cards (Wither every 6 cards); strip 3 Artifact |
| 3 Glory | [Test Subject](../knowledge/bosses/TEST_SUBJECT_BOSS.md) | 44 / 44 | 0/5 | ~54 | Three phases: attacks in phase 1, full block in 2, burst on tangible turns in 3 |
| 3 Glory | [Queen](../knowledge/bosses/QUEEN_BOSS.md) | 41 / 47.5 | 2/7 | ~60 (arrive high) | Artifact against You're Mine (99 Weak, Vulnerable, Frail); draw |

At A10 there are two Glory bosses at the end of Act 3 (floors 48–49). Plan for both. `[PLAYER-DATA]`

**v0.111.1 changes:** Queen's Torch Head Amalgam opens with a new Strong Tackle, 26 (32): block 26+ on turn 1. Aeonglass's Ebb drops to 22 (26). Soul Fysh's De-Gas at A9 rises to 16 (18). `knowledge/version-delta-v0.111.1.md`

**Arrival HP by boss** (H8): it separated survived from fatal fights for Queen, The Kin and Aeonglass (gaps of 22–25 points), not for Vantom or Waterfall Giant (gap near zero). Their deaths are about the deck: Slippery, the death explosion, long fights.

**Benchmarks in this table are pooled, mostly from the Player's A7–A10 runs.** At lower ascension, use `data/benchmarks/ironclad-encounters-by-band-v0.107.1.csv` (or `allchars-…` where Ironclad has fewer than 5 fights). At A0–4, Vantom's all-character median is 22.5 against 48 pooled. Rest thresholds scale down accordingly.

## 11. Player baseline (habits to beat or test, not targets)
- Smiths down to low HP: equally likely to heal or smith at 27% HP overall, 37% before a boss.
- Takes elites at moderate or low HP "to get strong for later".
- Judges deck needs by feel.
- Rarely removes cards (34 of 57 runs ever remove one).
- Rarely takes second copies.
- **Card habit against consensus** (`knowledge/community/discrepancies.md`, 19 cards with a gap of 2+ tiers):
  - Rates higher than consensus: Evil Eye, Fight Me, Tremble, Cruelty, Aggression, Thrash, Dark Embrace, Second Wind, Ashen Strike, Drum of Battle, Vicious
  - Rates lower: Cascade, Demon Form, Battle Trance, Shrug It Off, Bully, Expect a Fight, Pommel Strike, Rupture
- The Player's implied card order (Phase 1 head-to-head scores): `reports/phase1/card-ranking-ironclad.md`.

## 12. Hypotheses to test (Phase 4 experiments)

| ID | Hypothesis | Evidence so far | Test | Status |
|---|---|---|---|---|
| H1 | Resting before a boss when HP is below the threshold (section 10; 70% in Act 3) reduces boss deaths | Arrival HP curve is steep (Act 3: fitted 64% fatal at 40% HP against 29% at 80%). The Player's heal and smith outcomes at equal HP are nearly identical. Mixed. | Rule against baseline over 10+ runs; log arrival HP and choice | Open |
| H2 | Vantom losses come from Slippery: big hits and hit-all single hits are wasted; the fight runs into cycle 2 | Multi-hit *count* does not separate outcomes (n=28). Fatal decks had more hit-all single-hit cards (0.8 against 0.3) and less draw (1.0 against 2.1) `[PLAYER-DATA, weak]` | Play the Vantom plan; log stack-clear turn and damage | Refined (v2) |
| H3 | ~~Entomancer punishes a lack of multi-target damage~~ **Replaced:** Entomancer punishes hit count (Personal Hive adds a card per damage instance) | `[GAME-EXTRACT]` power definition; fatal decks had more cheap attacks (9.5 against 8.1) | Few big hits against it | Replaced (v2) |
| H4 | Removing a Strike at the first Act 1 shop improves Act 1 survival | Runs that had the chance (Act 1 shop, 75+ gold): survived Act 1 in 80% with a basic removal against 67% without; A5–9 89% against 70%, A10 70% against 59%, A0–4 no gap (`reports/phase2/rule-backtests.md`) | Runs with and without at A5+ | Supported at A5+ (confounded) |
| H5 | Avoiding elites under 50% HP reduces deaths | n=308; 24% fatal against 3–8%. Holds in every band: A0–4 10% against 3%, A5–9 32% against 6%, A10 29% against 9% | Adopted as a rule | Adopted |
| H6 | Raising cheap and multi-hit attacks when Vantom is the boss fixes the Vantom problem | Mechanics support it; history can't test it (decks held about 0.7 multi-hit cards) | Phase 4 Vantom fights | Open |
| H7 | Knowledge Demon needs a scaling engine (powers, energy, Strength) by the end of Act 2 | Fatal decks: powers 1.7 against 2.7, energy 0.8 against 1.6 (n=40) `[PLAYER-DATA, weak]` | Track engine presence on arrival | New (v2) |
| H8 | Arrival HP matters most for Queen, The Kin and Aeonglass, and hardly at all for Vantom and Waterfall Giant | Median arrival HP, survived against fatal (all characters, abandoned runs excluded): Queen 79% / 54%, The Kin 64% / 41%, Aeonglass 87% / 65%; Vantom 57% / 58%, Waterfall Giant 57% / 59%. Fatal n is 5–12 per boss | Higher rest thresholds for the first three; for Vantom and Waterfall Giant, prefer a smith that fixes the deck's answer when HP is above the median damage | Refined (v2.5) |
| H9 | Boss survival depends more on block and scaling than on raw damage: targets in section 2.1 | Raw-damage terciles: Act 1 fatal 18% / 29% / 28% (low to high). Block: 30% / 24% / 21%. Scaling 2–3 cards: 17% against 28% (n=173 Act 1 boss fights) `[PLAYER-DATA, observational]` | Track the deck metrics at every boss arrival in Phase 4 | New (v2.2) |

## 13. Open questions and conflicts
- The extract predates v0.107.1 (`knowledge/version-delta-extract-to-v0.107.1.md`): Conflagration, Drum of Battle and Unrelenting changed in v0.107.1, and Infested Prism and Skulking Colony were reworked. On v0.111.1, the cards and enemies in `knowledge/version-delta-v0.111.1.md` differ as well. Re-check numbers against live data (P2.E1).
- Not Yet (card) and Aeonglass (boss) are missing from the extract.
- **Cards where sources disagree** (†, 29 cards): One-Two Punch, Pyre, Tear Asunder, Barricade, Bloodletting, Juggernaut, Shrug It Off, Aggression, Thrash, Bully and others (full list in §2.2). Nat 1 Gaming is v0.113 beta. Spire Codex (main) is partial.
- Bygone Effigy's Slow multiplier, the Colossus power and Infested Prism's Vital Spark: effects to verify in game.
- Whether killing the Kin Priest ends that fight; whether Lagavulin Matriarch wakes when damaged.

## 14. Changelog
- **v2.5 (2026-11-19, overnight):** consistency pass against the data: rest heal is 30% of max HP rounded down (was "about 29%"); room economics ranges per act; the elite HP-band sample excludes abandoned runs (stated); H8 widened to The Kin and narrowed for Vantom and Waterfall Giant; v0.111.1 elite and boss changes noted under the tables. Deck-strength figures recomputed with v0.107.1 card values (the extract predates v0.107.1): Act 1 raw-damage tercile 28% (was 29%), Ironclad fatal decks 16.8 against 15.1 (was 14.7); corner targets unchanged. Also fixed the quintile buckets in `tools/build_community_tiers.py` (the top bucket had absorbed the remainder). Consensus moved for four cards: Feel No Pain A→B, Body Slam B→C, Evil Eye C→D, Headbutt C→D. Habit discrepancies 23 → 19. Tier lists in §2.2 and §11 regenerated from the tier file.
- **v2.4 (2026-11-19, overnight):** main branch is now v0.111.1. Added the v0.111.1 card changes to §2.2; target version noted in the header.
- **v2.3 (2026-11-19, overnight):** pre-boss rest threshold uses the ascension-band median; curse removal added to the shop priority. Both from the practice post-mortems in `runs/examples/`.
- **v2.2 (2026-11-19, overnight):** numeric corner targets for deck needs (section 2.1) from the deck-strength analysis (`reports/phase2/deck-strength.md`, `tools/deck_metrics.py`); H9 added.
- **v2.1 (2026-11-19, overnight):** pre-boss rest rule split by act (Act 3 and A10: rest under 70%), from the boss arrival-HP analysis (`reports/phase2/boss-arrival-hp.md`). H1 evidence updated as mixed.
- **v2 (2026-11-19, overnight):** imported decompiled game data (card roles, monster moves, powers).
  - Replaced the provisional Player-habit card order with community consensus tiers plus context overrides.
  - Added boss plans for all 12 bosses and notes for 12 elites and 15 hallway fights.
  - Elite reference with mechanics; ascension-aware notes (A2 heal, A4 potion slots, A10 double boss).
  - Refined H2, replaced H3 (Entomancer punishes hit count), added H7 and H8.
  - Moved the Player's card habits to the baseline section.
- **v1 (2026-11-18):** first version from the Phase 1 run-history analysis and interview.
