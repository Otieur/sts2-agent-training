# Phase 1 Findings: Ironclad (v0.107.1)

Source: 57 solo Ironclad runs on v0.107.1 (12 wins, 40 deaths, 5 abandoned), mostly A7–A10. Generated 2026-11-18 from `data/runs.db`. All rates describe the Player's history, not proven strategy. The goal is strong play, not imitation: the Player's habits are a baseline, and outcome statistics are the evidence. Each finding carries n and a label.

## Top findings

1. **Runs end early, mostly at bosses.** 55% of deaths happen in Act 1 (22/40), and 14 of the 40 at the Act 1 boss alone. By fight type: bosses 24, elites 10, hallway 6. `[PLAYER-DATA]` (deaths-ironclad.md)

2. **Vantom is the Ironclad wall.** 6 deaths in 11 fights. Median damage 48 (60% of max HP), against 32 for all characters together (n=28). The fatal fights started with *more* HP than the survived ones (median 64% against 56%) but took 58 damage against 40. That points to the deck or the fight plan, not arrival HP. Weak signal: Breakthrough was in 5 of 6 fatal decks and 1 of 5 survived ones. `[PLAYER-DATA]`, n=11

3. **Two elites hurt Ironclad more than other characters.** Entomancer: median 30 damage for Ironclad against 17 for all characters (3 deaths in 13). Byrdonis: 3 deaths in 10, and every fatal fight started at about 29% HP. `[PLAYER-DATA]`

4. **The Player keeps smithing at low HP.** The point where heal and smith are equally likely is 27% HP overall: 37% right before a boss and 18% elsewhere. At 30–50% HP before a boss, the Player rests only 39% of the time. There are four cases of smithing at 14–29% HP, each followed by a death on the next floor. `[PLAYER-DATA]`, n=316 rest decisions (path-ironclad.md, interview cases 1–4)

5. **Losing runs fall behind on HP during Act 1.** Median HP after floor 15: 64% in wins, 50% in losses. After the Act 1 boss: 37% against 21%. `[PLAYER-DATA]`

6. **A clear card core.** Most often picked: Dominate (95% of 20 offers), Pyre (85% of 13), Fight Me (79% of 14), Second Wind (68%), Evil Eye (67%). The head-to-head ranking puts Pyre, Dominate, Thrash, Offering, Dark Embrace, Fiend Fire and Cruelty at the top. Almost never taken: Whirlwind 0/13, Juggling 0/15, Expect a Fight 0/14, Blood Wall 1/55, Anger 2/53, Perfected Strike 2/52. `[PLAYER-DATA]` (cards-ironclad.md, card-ranking-ironclad.md)

7. **Skips rise sharply through the run.** Skip rate by act: 10%, 31%, 49%. By deck size: 5% under 15 cards, 50% at 30 or more. In the ranking, SKIP sits above 12 cards with enough data, including Twin Strike, Sword Boomerang, Pommel Strike, Thunderclap and Havoc. `[PLAYER-DATA]`

8. **One copy is enough.** Armaments: 66% picked as a first copy, 0% as a second (n=27). Breakthrough: 51% to 4%. Shrug It Off: 36% to 0%. Armaments is also the usual first Smith upgrade (18 runs). `[PLAYER-DATA]`

9. **Card removal is rare.** Only 34 of 57 runs remove any card. The median first removal is on floor 14. Act 1 shops: 48 visits, 12 removals, median gold on arrival 191. `[PLAYER-DATA]`

10. **Potions are used well.** Only 4 of 40 deaths had an unused potion. About 1.1 potions per boss fight and 0.8 per elite. `[PLAYER-DATA]`

11. **No committed archetypes.** Deck clustering finds no real structure (silhouette about 0.04). Most decks are a shared core (Armaments 60%, Tremble 48%, True Grit 46%, Shrug It Off 44%, Molten Fist 38%, Bloodletting 37%) plus whatever was strong at the time. Community archetypes (Phase 2) will add the most here. `[PLAYER-DATA]`

12. **Outcome hints, to treat as hypotheses.** Win rate of finished runs with the card in the final deck, against without: Dominate 53% against 11% (n=15 with), True Grit 42% against 7% (n=24), Fight Me 47% against 14% (n=15), Molten Fist 42% against 12% (n=19). Survivorship inflates all of these. `[HYPOTHESIS]`

## Hypotheses for the interview and Phase 2

- **H1:** The low rest threshold before bosses causes avoidable Act 1 and Act 2 deaths. Test: interview cases 1–4; then in Phase 4, compare runs using a 50% pre-boss rest rule.
- **H2:** Vantom losses come from something specific in the fight, not from arrival HP. The Player had no explanation. Community guides describe **Slippery**: 9 stacks, each hit deals only 1 damage until the stacks are cleared. That rewards multi-hit and cheap attacks and wastes big single hits. Together with the Player ranking several multi-hit-looking cards below SKIP, this is the leading explanation. Test: confirm the mechanics and card text in Phase 2 (see `knowledge/bosses/VANTOM_BOSS.md`).
- **H3:** Ironclad's extra damage against Entomancer comes from a lack of multi-target damage. Several multi-target cards are rarely picked: Whirlwind 0/13, Thunderclap 15%, Cinder 15%. This needs the card text from Phase 2 to confirm which cards hit all enemies. `[HYPOTHESIS]`
- **H5 (supported):** Elites taken under 50% HP are far more dangerous. Across all characters, 24% of those fights ended the run, against 8% at 50–70% HP and 3% above 70% (n=308 elite fights in Acts 1–2). The Player takes them anyway at high ascension to scale for later acts. This is now a playbook rule, with the Player's habit as the baseline.
- **H4:** More early removals (Strikes in Act 1 shops) would improve Act 1 consistency. Test: Phase 4 experiment.

## Data quality

- 233 unique runs. Validation passes. Deck reconstruction matches the final deck in 232/232 solo runs (230/232 including upgrades).
- Each encounter ID appears in exactly one act (OQ1.3 resolved). Every fight has `turns_taken` (OQ1.2 resolved). Deck change logs are complete (OQ1.1 resolved).
- Shop card lists in the raw files show unsold stock; purchases are taken from cards gained (see `data/README.md`).

## Files

Visual report (private artifact): (private link) Its data files are rebuilt with `python3 -I tools/build_report_data.py`.


| Report | Content |
|---|---|
| `danger-ironclad.md` | Encounter danger by act and pool; deadliest compared with all characters |
| `cards-ironclad.md` | Pick rates, skips, context effects, outcome hints, upgrades, removals, shop purchases |
| `card-ranking-ironclad.md` | Head-to-head (Bradley-Terry) priority ranking including SKIP |
| `path-ironclad.md` | Room mix, elites, rest thresholds, shops, events, Ancients, potions |
| `deaths-ironclad.md` | Every death, deep dives on the top 5 killers, HP trajectories |
| `archetypes-ironclad.md` | Deck clustering (finding: no strong archetypes) |
| `interview-cases-ironclad.md` | 14 interview cases |
| `../../data/benchmarks/ironclad-encounters-v0.107.1.csv` | Frozen combat benchmark for Phase 4 |
