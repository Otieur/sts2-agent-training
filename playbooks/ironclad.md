# Ironclad Playbook

Version: v2.1 · Game version: v0.107.1 · Last updated: 2026-11-19 · Status: draft (v2 adds game data, community knowledge and boss plans; not yet tested in the Agent's own runs)

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
1. **Deck needs.** Measure the deck against five needs, not feel. Thresholds `[HYPOTHESIS]` are set from Phase 4 data.
   - **Attack:** damage per turn for the next elite and the boss.
   - **Defence:** block for the biggest hit of the next elite and the boss (boss table, section 10).
   - **Operations:** card draw and energy.
   - **Scaling:** Strength, powers, energy growth.
   - **Attack shape:** what the next boss needs. Vantom wants many hit instances and punishes hit-all single hits. Entomancer punishes many hits. Skulking Colony caps damage per turn. The Kin wants hit-all damage.
2. **Boss fit** overrides tier: draft toward the act boss's deck checklist.
3. **Tier** from 2.2. Within a tier, prefer the card that fills the weakest need.
4. **Archetype fit** once committed (section 3).
5. **Skip** if nothing improves the deck for the coming fights. Bigger decks skip more: the Player's skip rate rises from 5% under 15 cards to 50% at 30+, a sensible pattern. `[PLAYER-DATA]`

### 2.2 Card tiers (community consensus, v0.107-era weighted)
From `knowledge/community/ironclad-tiers.md` `[COMMUNITY]`. † marks cards where sources disagree by 2+ tiers. Card roles are `[GAME-EXTRACT]`.

- **S:** Offering, Cascade, Conflagration, Corruption, Demon Form, Feed, Stoke, Unmovable
- **A:** Crimson Mantle, Impervious, Fiend Fire, Battle Trance, Brand, Colossus, Dominate, Feel No Pain†, Hellraiser, One-Two Punch†, Pyre†, Tear Asunder†
- **B:** Barricade†, Bloodletting†, Burning Pact, Cruelty, Juggernaut†, Shrug It Off†, Aggression†, Mangle, Pact's End, Thrash†, Body Slam†, Bully†, Dark Embrace†, Expect a Fight, Flame Barrier, Forgotten Ritual, Pommel Strike†, Rupture, Second Wind†, Stampede†, True Grit
- **C:** Break†, Armaments†, Ashen Strike, Drum of Battle†, Evil Eye, Headbutt†, Howl from Beyond†, Inferno†, Juggling†, Pillage, Rage, Stomp†, Stone Armor, Taunt†, Uppercut†, Vicious
- **D:** Anger, Blood Wall, Bludgeon†, Dismantle†, Fight Me†, Inflame, Molten Fist, Primal Force†, Spite, Sword Boomerang, Tremble, Unrelenting, Whirlwind†, Breakthrough, Hemokinesis, Infernal Blade, Perfected Strike, Rampage, Setup Strike, Twin Strike, Cinder, Havoc, Iron Wave, Thunderclap
- **Multiplayer-only value:** Tank, Demonic Shield. Rate them low solo.

**Context overrides** (tier is a default, not a rule):
- **Vantom is the Act 1 boss:** raise cheap and multi-hit attacks (Anger, Twin Strike, Sword Boomerang, Thrash, Fight Me). They clear Slippery. Lower hit-all single-hit cards (Breakthrough, Thunderclap). `[GAME-EXTRACT]` mechanics, `[HYPOTHESIS]` value
- **Strength engine in the deck:** raise multi-hit payoffs one tier. `[COMMUNITY]`
- **Exhaust engine** (Feel No Pain or Dark Embrace in the deck): raise exhaust outlets one tier.
- **Second copies:** usually a tier lower, except engine pieces the deck needs twice. `[HYPOTHESIS]`

### 2.3 Upgrade priority (v2)
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

1. **At act start:** read the boss and open its plan. Choose a path by elites, rest sites before elites and the boss, shops, and expected HP cost (sum of benchmark medians; p75 for elites). Write the plan in the run journal.
2. **Elites under 50% HP: avoid.** `[PLAYER-DATA]` outcome, n=308 elite fights in Acts 1–2, all characters:
   - 24% of fights entered under 50% HP ended the run (Ironclad 4/16)
   - 8% at 50–70% (Ironclad 3/32)
   - 3% at 70% or more (Ironclad 2/31)
   - Exception: the elite is one the deck handles easily (Phantasmal Gardeners, median 12) and the alternative path is worse.
3. **Elites at 50–70% HP:** take one only if current HP minus its p75 leaves enough to reach the next rest site.
4. **Re-plan** if HP falls more than 15% of max below the plan, a key card or relic changes the deck's needs, or a detour is forced.

**Elite reference** (Ironclad HP lost per fight, median / p75; notes in `knowledge/enemies/`):

| Act | Elite | Median / p75 | Fatal | Key mechanic `[GAME-EXTRACT]` | Answer |
|---|---|---|---|---|---|
| 1 | Bygone Effigy | 29 / 39.5 | 1/12 | Sleeps; wakes with +10 Strength (slash 25); Slow (takes more per card played) | Burst during sleep with many cards; block 25 |
| 1 | Terror Eel | 29 / 39 | 0/5 | First damage stuns it; then 99 Vulnerable on you | Hit it on turn 1; block ×1.5 hits |
| 1 | Byrdonis | 22.5 / 32.8 | 3/10 | +Strength every turn (Territorial) | Kill fast; never under 50% HP |
| 1 | Phrog Parasite | 19 / 30 | 1/9 | Spawns Wrigglers on death; Infection cards | Save hit-all damage for wave 2 |
| 1 | Skulking Colony | 19 / 35 | 1/9 | Caps HP lost per turn | Steady damage; no burst |
| 1 | Phantasmal Gardeners | 12 / 19 | 0/8 | Several small bodies | Hit-all damage; safest elite |
| 2 | Decimillipede | 36.5 / 39.2 | 0/8 | Segments reattach | Kill segments together; hit-all damage |
| 2 | Entomancer | 30 / 38 | 3/13 | **Each damage instance adds a card to your draw pile** | Few big hits, not multi-hit; block Bees 3×7 |
| 2 | Infested Prisms | 27 / 38.8 | 0/8 | Hits 22–27, Pulsate +4 Strength and 20 block | Block big; don't attack into Pulsate |
| 3 | Mecha Knight | 34 / 43 | 1/5 | Artifact; Heavy Cleave 35 (40 after Windup) | Block 40; strip Artifact first |

## 5. Rest-site policy

- **Before a boss** `[HYPOTHESIS H1]`, tested in Phase 4 against the Player's baseline (equally likely to heal or smith at 37% HP before a boss):
  - Acts 1–2: rest if HP is below the boss's threshold in section 10 (median + 10). Otherwise smith.
  - **Act 3 and the A10 double boss: rest if HP is below 70%.**
  - Evidence (`reports/phase2/boss-arrival-hp.md`) is mixed. Boss death rates fall steeply with arrival HP, most of all in Act 3. But the Player's heals and smiths at the same HP were followed by almost the same boss death rate (31% against 30% under 50% HP). Confounding cuts both ways.
- **Before an elite on the path:** rest if HP minus the elite's p75 would leave less than 50% of max for the next fights. `[HYPOTHESIS]`
- **Otherwise:** smith at 50% HP or more. Under 35%, rest. In between, decide by the next two fights' benchmark cost.
- A rest heals about 29% of max HP (about 23 on 80). `[PLAYER-DATA]`

## 6. Shop policy (including removal)

- **Priority** `[HYPOTHESIS]`:
  1. A relic or card that fills the current boss's checklist
  2. An S or A-tier card
  3. Removal of a Strike in a small Act 1 deck
  4. Other relics
  5. Potions (especially Weak, Block and Strength for the coming boss)
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
6. Potions when they prevent serious HP loss or win a dangerous fight.
7. Check `end_turn_will_kill_player` and `lethal_risks` before ending the turn.
8. Write down the expected HP after the enemy turn and compare it next turn. Use `tools/calc.py` for exact numbers.

## 10. Boss preparation

| Act | Boss | Median / p75 | Fatal (Ironclad) | Rest if HP below | The one thing to prepare `[GAME-EXTRACT]` mechanics |
|---|---|---|---|---|---|
| 1 Overgrowth | [Vantom](../knowledge/bosses/VANTOM_BOSS.md) | 48 / 57.5 | 6/11 | ~58 | 9 hit instances to clear Slippery; block 27 on turn 3 |
| 1 Overgrowth | [Ceremonial Beast](../knowledge/bosses/CEREMONIAL_BEAST_BOSS.md) | 39 / 45.5 | 1/7 | ~49 | Front-load damage to break 150 Plow (stuns it, resets its Strength) |
| 1 Overgrowth | [The Kin](../knowledge/bosses/THE_KIN_BOSS.md) | 34.5 / 41.2 | 0/8 | ~45 | Hit-all damage for the followers |
| 1 Underdocks | [Waterfall Giant](../knowledge/bosses/WATERFALL_GIANT_BOSS.md) | 38 / 41 | 2/5 | ~48 | Fast kill; bank block for the death explosion |
| 1 Underdocks | [Soul Fysh](../knowledge/bosses/SOUL_FYSH_BOSS.md) | 33 / 41 | 3/7 | ~43 | Exhaust Beckon cards; burst outside Intangible |
| 1 Underdocks | [Lagavulin Matriarch](../knowledge/bosses/LAGAVULIN_MATRIARCH_BOSS.md) | 28 / 40.5 | 2/8 | ~38 | Set up while it sleeps; kill before repeated Soul Siphons |
| 2 Hive | [Knowledge Demon](../knowledge/bosses/KNOWLEDGE_DEMON_BOSS.md) | 45 / 59.8 | 4/12 | ~55 | Scaling and energy (about 60 damage per turn over 7 turns); curse choice |
| 2 Hive | [Kaiser Crab](../knowledge/bosses/KAISER_CRAB_BOSS.md) | 43.5 / 48.5 | 2/6 | ~54 | Focus the Rocket claw; block 31+ on the Laser |
| 2 Hive | [The Insatiable](../knowledge/bosses/THE_INSATIABLE_BOSS.md) | 31.5 / 45.8 | 2/6 | ~42 | Watch the Sandpit timer; energy for Frantic Escape |
| 3 Glory | [Aeonglass](../knowledge/bosses/AEONGLASS_BOSS.md) | 48 / 70 | 0/5 | ~58 (arrive high) | Fewer, bigger cards (Wither every 6 cards); strip 3 Artifact |
| 3 Glory | [Test Subject](../knowledge/bosses/TEST_SUBJECT_BOSS.md) | 44 / 44 | 0/5 | ~54 | Three phases: attacks in phase 1, full block in 2, burst on tangible turns in 3 |
| 3 Glory | [Queen](../knowledge/bosses/QUEEN_BOSS.md) | 41 / 47.5 | 2/7 | ~60 (arrive high) | Artifact against You're Mine (99 Weak, Vulnerable, Frail); draw |

At A10 there are two Glory bosses at the end of Act 3 (floors 48–49). Plan for both. `[PLAYER-DATA]`

## 11. Player baseline (habits to beat or test, not targets)
- Smiths down to low HP: equally likely to heal or smith at 27% HP overall, 37% before a boss.
- Takes elites at moderate or low HP "to get strong for later".
- Judges deck needs by feel.
- Rarely removes cards (34 of 57 runs ever remove one).
- Rarely takes second copies.
- **Card habit against consensus** (`knowledge/community/discrepancies.md`, 23 cards with a gap of 2+ tiers):
  - Rates higher than consensus: Fight Me, Evil Eye, Molten Fist, Tremble, Second Wind, Thrash, Cruelty, Aggression, Dark Embrace, Armaments, Vicious, Drum of Battle, Ashen Strike, Pact's End
  - Rates lower: Cascade, Demon Form, Battle Trance, Feel No Pain, Body Slam, Bully, Expect a Fight, Pommel Strike, Rupture
- The Player's implied card order (Phase 1 head-to-head scores): `reports/phase1/card-ranking-ironclad.md`.

## 12. Hypotheses to test (Phase 4 experiments)

| ID | Hypothesis | Evidence so far | Test | Status |
|---|---|---|---|---|
| H1 | Resting before a boss when HP is below the threshold (section 10; 70% in Act 3) reduces boss deaths | Arrival HP curve is steep (Act 3: fitted 64% fatal at 40% HP against 29% at 80%). The Player's heal and smith outcomes at equal HP are nearly identical. Mixed. | Rule against baseline over 10+ runs; log arrival HP and choice | Open |
| H2 | Vantom losses come from Slippery: big hits and hit-all single hits are wasted; the fight runs into cycle 2 | Multi-hit *count* does not separate outcomes (n=28). Fatal decks had more hit-all single-hit cards (0.8 against 0.3) and less draw (1.0 against 2.1) `[PLAYER-DATA, weak]` | Play the Vantom plan; log stack-clear turn and damage | Refined (v2) |
| H3 | ~~Entomancer punishes a lack of multi-target damage~~ **Replaced:** Entomancer punishes hit count (Personal Hive adds a card per damage instance) | `[GAME-EXTRACT]` power definition; fatal decks had more cheap attacks (9.5 against 8.1) | Few big hits against it | Replaced (v2) |
| H4 | Removing a Strike at the first Act 1 shop improves Act 1 survival | 79% against 50%, confounded | Runs with and without | Open |
| H5 | Avoiding elites under 50% HP reduces deaths | n=308; 24% against 3–8% | Adopted as a rule | Adopted |
| H6 | Raising cheap and multi-hit attacks when Vantom is the boss fixes the Vantom problem | Mechanics support it; history can't test it (decks held about 0.7 multi-hit cards) | Phase 4 Vantom fights | Open |
| H7 | Knowledge Demon needs a scaling engine (powers, energy, Strength) by the end of Act 2 | Fatal decks: powers 1.8 against 2.7, energy 0.8 against 1.6 (n=40) `[PLAYER-DATA, weak]` | Track engine presence on arrival | New (v2) |
| H8 | Arrival HP matters most for Queen and Aeonglass | Survived arrived at 79% / 87%, fatal at 54% / 65% (all characters) | Higher rest thresholds there | New (v2) |

## 13. Open questions and conflicts
- The extract's build version is unverified. Re-check card numbers against live `/data` on v0.107.1 (P2.E1).
- Not Yet (card) and Aeonglass (boss) are missing from the extract.
- **Cards where sources disagree** (†): Feel No Pain, One-Two Punch, Pyre, Barricade, Juggernaut, Aggression, Dark Embrace, Body Slam and others. Nat 1 Gaming is v0.113 beta. Spire Codex (main) is partial.
- Bygone Effigy's Slow multiplier, the Colossus power and Infested Prism's Vital Spark: effects to verify in game.
- Whether killing the Kin Priest ends that fight; whether Lagavulin Matriarch wakes when damaged.

## 14. Changelog
- **v2.1 (2026-11-19, overnight):** pre-boss rest rule split by act (Act 3 and A10: rest under 70%), from the boss arrival-HP analysis (`reports/phase2/boss-arrival-hp.md`). H1 evidence updated as mixed.
- **v2 (2026-11-19, overnight):** imported decompiled game data (card roles, monster moves, powers).
  - Replaced the provisional Player-habit card order with community consensus tiers plus context overrides.
  - Added boss plans for all 12 bosses and notes for 12 elites and 15 hallway fights.
  - Elite reference with mechanics; ascension-aware notes (A2 heal, A4 potion slots, A10 double boss).
  - Refined H2, replaced H3 (Entomancer punishes hit count), added H7 and H8.
  - Moved the Player's card habits to the baseline section.
- **v1 (2026-11-18):** first version from the Phase 1 run-history analysis and interview.
