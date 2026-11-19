# Ironclad Playbook

Version: v1 · Game version: v0.107.1 · Last updated: 2026-11-18 · Status: draft, waiting for the Player's factual review

The goal is strong play, judged by results. Every rule carries a provenance label and an evidence pointer. Conflicts follow the precedence in `docs/README.md`. v1 is built from the Player's run history (57 solo Ironclad runs: 12 wins, 40 deaths, 5 abandoned, mostly A7–A10) and two early community notes. Card text and enemy data are not loaded yet; Phase 2 fills most gaps marked "Phase 2".

Evidence files: `reports/phase1/` (SUMMARY.md, danger-ironclad.md, cards-ironclad.md, path-ironclad.md, deaths-ironclad.md), `data/benchmarks/ironclad-encounters-v0.107.1.csv`, `knowledge/player-reasoning.md`.

---

## 1. Win conditions and overview

- **Runs are lost early, at bosses.** 55% of deaths happen in Act 1 (22/40), and 14 at the Act 1 boss alone. Overall: 24 deaths to bosses, 10 to elites, 6 in hallway fights. `[PLAYER-DATA]` (deaths-ironclad.md)
  - **Priority 1:** reach the Act 1 boss with a deck that fits that boss and enough HP to survive its typical damage.
- **HP falls behind in Act 1 in losing runs.** Median HP after floor 15 is 64% in wins and 50% in losses. After the Act 1 boss it is 37% against 21%. `[PLAYER-DATA]`
- **Bosses are long fights:** median 6–10 turns (benchmark), against 3–6 for hallway fights. Decks need damage that holds up or grows over the fight, not only front-loaded damage. `[PLAYER-DATA]` turn counts; the scaling conclusion is `[HYPOTHESIS]` until Phase 4.
- **The game heals between acts,** so HP is a per-act budget. Spend it to gain strength within the act, but arrive at each boss with enough. `[PLAYER-DATA]` (HP jumps at floors 18 and 35)

## 2. Card evaluation

### 2.1 Procedure (use in this order)

1. **Assess deck needs** against the triangle plus two additions. `[PLAYER-SAID]` framework, adopted. Thresholds come in Phase 2.
   - **Attack:** enough damage per turn for the next elite and the act boss.
   - **Defence:** enough block per turn for the next elite's and the boss's big turns.
   - **Operations:** card draw and energy.
   - **Scaling:** damage or block that grows over a 6–10 turn boss fight.
   - **Attack shape:** multi-hit or cheap attacks against big single hits; single-target against multi-target. This matters for specific bosses and elites (sections 10 and 12).
2. **Fit the boss.** Read the act boss at the start of the act and draft toward its plan (section 10). `[PLAYER-SAID]` + standard practice.
3. **Look up the card.** Use the provisional order in 2.2 until Phase 2 replaces it.
4. **Skip if nothing improves the deck for the coming fights.** The Player skips 10% of reward screens in Act 1, 31% in Act 2 and 49% in Act 3, and half the time once the deck reaches 30 cards. That is a sensible pattern, kept as the baseline. `[PLAYER-DATA]` habit
5. **Duplicates:** the Player almost never takes a second Armaments, Shrug It Off or Breakthrough. Treat a second copy as lower value unless the deck plan needs it. `[PLAYER-DATA]` habit, to be confirmed with card text.

### 2.2 Provisional card order (Player baseline, not proven strength)

This is the Player's implied priority from 632 reward screens (Bradley-Terry, card-ranking-ironclad.md). It describes **habit, not strength**. It is a default only for when Phase 2 data is missing. Brackets give the score and the number of comparisons.

- **High:** Pyre (+3.1, 35), Dominate (+3.1, 58), Thrash (+3.0, 19), Offering (+2.7, 12), Dark Embrace (+2.7, 13), Fiend Fire (+2.6, 14), Cruelty (+2.5, 13), Brand (+2.5, 14), Conflagration (+2.2, 16), Fight Me (+2.1, 36)
- **Good:** Evil Eye, One-Two Punch, Second Wind, Impervious, Aggression, Pact's End, Stoke, Burning Pact
- **Situational:** Mangle, Stampede, Vicious, Hellraiser, Colossus, True Grit, Crimson Mantle, Feed, Tear Asunder, Drum of Battle, Tremble, Ashen Strike, Molten Fist, Armaments, Bloodletting, Forgotten Ritual, Infernal Blade, Demon Form, Cascade, Barricade, Unrelenting, Not Yet
- **Marginal (just above skipping):** Breakthrough, Feel No Pain, Battle Trance, Inferno, Flame Barrier, Uppercut, Shrug It Off, Taunt, Dismantle
- **Usually skipped by the Player:** Pillage, Bully, Twin Strike, Stomp, Rage, Howl from Beyond, Sword Boomerang, Rupture, Cinder, Pommel Strike, Thunderclap, Havoc, Rampage, Inflame, Iron Wave, Headbutt, Setup Strike, Body Slam, Spite, Bludgeon, Stone Armor, Hemokinesis, Anger, Perfected Strike, Whirlwind, Juggling, Blood Wall, Expect a Fight

**Known risk in this order** `[HYPOTHESIS]`: several cheap or multi-hit-looking attacks sit in the skipped group (Anger, Twin Strike, Sword Boomerang). Those may be exactly what Vantom requires (H2). When Vantom is the Act 1 boss, raise cheap and multi-hit attacks until Phase 2 card text and Phase 4 tests settle it.

**Outcome hints** `[HYPOTHESIS]` (survivorship-inflated): win rate of finished runs with the card in the final deck, against without it:
- Dominate: 53% against 11% (n=15 with)
- True Grit: 42% against 7% (n=24)
- Fight Me: 47% against 14% (n=15)
- Molten Fist: 42% against 12% (n=19)

## 3. Archetypes and commit signals

- The Player's final decks show no clear archetypes (silhouette about 0.04). They share a core (Armaments 60%, Tremble 48%, True Grit 46%, Shrug It Off 44%, Molten Fist 38%, Bloodletting 37%) plus whatever was strong at the time. `[PLAYER-DATA]`
- Real archetypes, with their key cards, relics and commit signals, come from community sources in Phase 2 (P2.E4.S3). Until then: draft for deck needs (2.1), not for an archetype.

## 4. Path planning and HP budget

1. **At each act start:** read the boss, list candidate paths, and choose one. Score each path on elites, rest sites before elites and the boss, shops, and expected HP cost (sum of benchmark medians for likely fights). Write the plan in the run journal.
2. **Elites under 50% HP: avoid.** `[PLAYER-DATA]` outcome evidence, n=308 elite fights in Acts 1–2, all characters:
   - Entered under 50% HP: 24% ended the run (Ironclad 4/16).
   - Entered at 50–70%: 8% (Ironclad 3/32).
   - Entered at 70% or more: 3% (Ironclad 2/31).
   - Exception: take one under 50% only when the alternative path is worse, or the deck clearly handles that elite.
3. **Elites at 50–70% HP:** decide by the elite's benchmark damage (below) against current HP, with a margin for a bad draw (use p75).
4. **Re-plan when:** HP falls more than 15% of max below the plan, a key card or relic changes the deck's needs, or a forced detour happens.

**Elite benchmark** (Ironclad, HP lost per fight; median / p75; fights). `[PLAYER-DATA]`

| Act | Elite | Median | p75 | n | Fatal |
|---|---|---|---|---|---|
| 1 | Bygone Effigy | 29 | 39.5 | 12 | 1 |
| 1 | Terror Eel | 29 | 39 | 5 | 0 |
| 1 | Byrdonis | 22.5 | 32.8 | 10 | 3 (all entered at about 29% HP) |
| 1 | Phrog Parasite | 19 | 30 | 9 | 1 |
| 1 | Skulking Colony | 19 | 35 | 9 | 1 |
| 1 | Phantasmal Gardeners | 12 | 19 | 8 | 0 |
| 2 | Decimillipede | 36.5 | 39.2 | 8 | 0 |
| 2 | Entomancer | 30 | 38 | 13 | 3 (all characters median: 17) |
| 2 | Infested Prisms | 27 | 38.8 | 8 | 0 |
| 3 | Mecha Knight | 34 | 43 | 5 | 1 |

## 5. Rest-site policy

- **Default: Smith.** At 50% HP or more, the Player's Smith-first habit matches the outcomes seen so far. Before a boss at 50–70% HP, 24% of Smith choices ended at the boss, and both Heal cases are too few to compare. `[PLAYER-DATA]`
- **Before a boss:** rest if current HP is below that boss's median benchmark damage plus about 10. Otherwise smith. `[HYPOTHESIS]` to test in Phase 4 against the Player's baseline (equally likely to heal or smith at 37% HP before a boss).
  - Supporting evidence (small samples): before a boss at 35–50% HP, death at the boss after Heal was 17% (1/6) and after Smith 25% (3/12). Across all characters, 21% against 31%.
  - A Heal restores about 29% of max HP (about 23 on 80).
- **Not before a boss:** rest under 35% HP if an elite or a dangerous hallway fight is likely before the next rest site. Otherwise smith. `[HYPOTHESIS]`
- **Upgrade order (baseline):** the Player most often upgrades Armaments first (18 runs), then True Grit, Bash, Dominate, Vicious and Stampede. `[PLAYER-DATA]` habit. Phase 2 card text decides real upgrade value.

## 6. Shop policy (including removal)

- **Gold:** the Player arrives at Act 1 shops with a median 191 gold and spends most of it. Purchases are mostly relics and colorless cards. Most bought relics: Bag of Marbles, Miniature Tent, Vajra, Oddly Smooth Stone, Wing Charm, Membership Card. `[PLAYER-DATA]` habit
- **Removal:** the Player rates removal as weak in big or draw-heavy decks. The arithmetic agrees that one removal is a small shift, about 3 percentage points of draw quality. `[PLAYER-SAID]` + arithmetic.
  - **Default:** removal below a good relic or a card that fills a deck need.
  - **To test** `[HYPOTHESIS]`: remove a Strike at the first Act 1 shop when affordable. Runs that removed a basic card in Act 1 survived Act 1 in 79% of cases (11/14), against 50% (19/38). That comparison is confounded.
- Ascender's Bane (A5 and up) was never removed in any run. Whether it can be removed is an open question for Phase 2.

## 7. Events and Ancients

- **No outcome-backed event rules yet.** The Player's choices per event are in path-ironclad.md as a baseline. Phase 2 adds event text and outcomes.
- **Observed safe values** `[PLAYER-DATA]`:
  - Sunken Treasury, "Second chest": +342 gold on average (6 visits).
  - Wellspring, "Bathe": no HP cost (4 visits).
- **Observed costly ones** `[PLAYER-DATA]`:
  - Slippery Bridge: −6.8 HP on average (23 visits).
  - Whispering Hollow: −6 HP (6 visits).
- **Ancients:** the Player's pick rates are a baseline only (path-ironclad.md). Phase 2 relic text decides.

## 8. Potion policy

- **Use potions freely in elites and bosses.** The Player uses about 1.1 per boss fight and 0.8 per elite, and only 4 of 40 deaths still had an unused potion. Keep this. `[PLAYER-DATA]` outcome
- **Never end a run holding potions.** On a turn where `end_turn_will_kill_player` is true, every usable potion is played first.
- **Weak potion against Vantom:** use it early (section 10). `[COMMUNITY]`

## 9. Combat checklist (v1; extended in Phases 2–4)

1. Read every enemy intent. Total the incoming damage.
2. Check for lethal on enemies. Killing an attacker removes its damage.
3. Block needed = incoming damage minus the HP loss the act budget allows.
4. Play draw and energy first when they change the options. Play powers early in long fights. Apply Vulnerable before attacks, and Weak before the enemy's big turn.
5. Use a potion when it prevents serious HP loss or wins a dangerous fight.
6. Check `end_turn_will_kill_player` and `lethal_risks` before ending the turn.
7. Write down the expected HP after the enemy turn, and compare it next turn to catch arithmetic errors.

## 10. Boss preparation

Read the boss at the start of the act. Draft and path toward its plan. Benchmarks are Ironclad HP lost per fight. `[PLAYER-DATA]`

| Act | Boss | Median | p75 | n | Fatal | Rest before the boss if HP is below | Plan |
|---|---|---|---|---|---|---|---|
| 1 | Vantom | 48 | 57.5 | 11 | 6 | about 58 | `knowledge/bosses/VANTOM_BOSS.md`: strip Slippery with cheap or multi-hit attacks, don't stall `[COMMUNITY]` |
| 1 | Ceremonial Beast | 39 | 45.5 | 7 | 1 | about 49 | Phase 2 |
| 1 | Waterfall Giant | 38 | 41 | 5 | 2 | about 48 | Phase 2 |
| 1 | The Kin | 34.5 | 41.2 | 8 | 0 | about 45 | Phase 2 (longest fight: median 9 turns) |
| 1 | Soul Fysh | 33 | 41 | 7 | 3 | about 43 | Phase 2 |
| 1 | Lagavulin Matriarch | 28 | 40.5 | 8 | 2 | about 38 | Phase 2 (high spread: p90 53) |
| 2 | Knowledge Demon | 45 | 59.8 | 12 | 4 | about 55 | Phase 2 |
| 2 | Kaiser Crab | 43.5 | 48.5 | 6 | 2 | about 54 | Phase 2 |
| 2 | The Insatiable | 31.5 | 45.8 | 6 | 2 | about 42 | Phase 2 |
| 3 | Aeonglass | 48 | 70 | 5 | 0 | about 58 | Phase 2 |
| 3 | Test Subject | 44 | 44 | 5 | 0 | about 54 | Phase 2 (median 10 turns) |
| 3 | Queen | 41 | 47.5 | 7 | 2 | about 51 | Phase 2 |

The rest column applies the section 5 hypothesis: median plus 10, rounded.

## 11. Player baseline (habits to beat or test, not targets)

- Smiths down to low HP: equally likely to heal or smith at 27% HP overall, 37% before a boss, 18% elsewhere. Reason given: "at high ascension, get strong for Acts 2–3 or die."
- Takes elites at moderate or low HP for the same reason.
- Judges the triangle by feel.
- Rarely removes cards (34 of 57 runs ever remove one).
- Rarely takes second copies.
- The card order in 2.2.

## 12. Hypotheses to test (Phase 4 experiments)

| ID | Hypothesis | Test | Status |
|---|---|---|---|
| H1 | Resting before a boss when HP is below the boss's median damage plus 10 reduces boss deaths | Compare runs following the rule with the baseline | Open |
| H2 | Vantom punishes decks without cheap or multi-hit attacks (Slippery) | Phase 2 card text plus Vantom fights in Phase 4 | Leading explanation |
| H3 | Entomancer punishes a lack of multi-target damage | Phase 2 enemy and card data | Open |
| H4 | Removing a Strike at the first Act 1 shop improves Act 1 survival | Phase 4 runs with and without | Open |
| H5 | Avoiding elites under 50% HP reduces deaths | Already supported by outcome data; adopted as a rule (4.2) | Adopted |
| H6 | Raising cheap and multi-hit attacks when Vantom is the Act 1 boss fixes the Vantom problem | Phase 4 | Open |

## 13. Open questions and conflicts

- Card types and text are needed before the provisional order can be replaced (Phase 2).
- Which cards are multi-hit, multi-target or 0-cost (Phase 2)?
- Can Ascender's Bane be removed?
- The act-to-boss mapping: which Act 1 bosses belong to which act variant, and is the boss visible at act start (OQ2.3)?
- Rest policy: the Player's baseline against H1. Both stay until Phase 4 data decides.

## 14. Changelog

- **v1 (2026-11-18):** first version from the Phase 1 run-history analysis and the interview. Adopted: elite HP rule (outcome evidence), triangle framework, boss-first drafting, potion policy. Hypotheses H1–H6 opened. Card order marked as Player baseline only.
