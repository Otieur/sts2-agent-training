# Ascension Levels

Last updated 2026-11-19. Levels stack: A10 has every modifier below it.

The level names and effects come from the Switchblade Gaming guide (patch v0.100, April 2026) `[COMMUNITY]`. Each was checked against the Player's 227 runs on v0.107.1 `[PLAYER-DATA]`. A different list on MetaBot (for example "Ascender's Bane at A10") contradicts the run data and is not used.

| Level | Name | Effect | Verified in run data | Strategy implication |
|---|---|---|---|---|
| A1 | Swarming Elites | About 60% more elite spawns | Not visible (elites fought per act depend on pathing: 1.3–1.7 at every level) | More elite options on the map. The under-50%-HP elite rule matters more. |
| A2 | Weary Traveler | Ancients heal 80% of missing HP | **Yes:** act-start heal is 100% at A0–1 and 79% from A2 | You no longer start Acts 2 and 3 at full HP. Count the missing 20% in the act's HP budget. |
| A3 | Poverty | 25% less gold from enemies and chests | **Yes:** gold per hallway fight falls from about 16 to 12–13 from A3 | Fewer shop purchases. Removal competes harder with relics. |
| A4 | Tight Belt | One fewer potion slot | **Yes:** 3 slots at A0–3, 2 from A4 (extra slots only from relics) | Use potions earlier; holding three for the boss is no longer possible. |
| A5 | Ascender's Bane | Start with the Ascender's Bane curse | **Yes:** 100% of A5+ runs, 0% below | A permanent dead card (Eternal, Unplayable, Ethereal). Small decks feel it most. |
| A6 | Gloom | One fewer rest site per act | Not visible (rest sites visited per act stay at about 3.4–4.1; pathing compensates) | Rest sites are scarcer. Pre-boss rest decisions get harder. |
| A7 | Scarcity | Rare and upgraded cards appear half as often | **Partly:** upgraded cards in card rewards halve (18.2% at A0–6 against 9.7% at A7–10, about 4,300 offers each); the Rare share falls from about 14.4% to 12.1%, a step at A7 but not half (rarity pity may soften it) | Take solid commons and uncommons; don't wait for rares. Ironclad's Strength and exhaust cores are mostly uncommon. |
| A8 | Tough Enemies | All enemies have more HP | Indirect: Act 1 hallway damage rises from about 5% to 8.7% of max HP at A8 | Fights last longer: AoE and scaling gain value. |
| A9 | Deadly Enemies | All enemies deal more damage | Indirect: Act 1 hallway damage about 9.6% at A9 | Block earlier; the benchmark at A9–10 is the one to plan with. |
| A10 | Double Boss | Two bosses at the end of Act 3 | **Yes:** A10 runs have boss floors 48 and 49 | The deck needs sustained damage over two fights. Finish Act 2 with a multi-turn win condition. |

## Planning notes for the Agent
- Phase 4 starts at A0. A2 changes HP planning (act starts are not full). A4 changes potion habits. A10 needs a two-boss plan.
- The benchmark (`data/benchmarks/ironclad-encounters-v0.107.1.csv`) pools all ascension levels. For HP budgets at A8+, use `reports/phase1/encounters-ironclad-by-band.csv` (A5–9 and A10 bands).
