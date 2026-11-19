# Boss Arrival HP and Pre-Boss Rest Sites

All characters, solo runs on v0.107.1, finished runs only. Built by `tools/analyze_boss_arrival.py`. `[PLAYER-DATA]`, observational: decks that keep HP high are also stronger, so these curves overstate how much HP alone buys. They calibrate hypothesis H1; Phase 4 tests it.

## Act 1 bosses (n=173, fatal 43)

| Arrival HP | Fights | Fatal | Rate |
|---|---|---|---|
| under 40% | 21 | 8 | 38% |
| 40–50% | 37 | 11 | 30% |
| 50–60% | 30 | 9 | 30% |
| 60–70% | 35 | 7 | 20% |
| 70–80% | 25 | 7 | 28% |
| 80–90% | 17 | 0 | 0% |
| 90–100% | 8 | 1 | 12% |

Logistic fit, P(fatal | arrival HP): 40% → 35%, 50% → 29%, 60% → 24%, 70% → 19%, 80% → 15%, 90% → 12%, 100% → 9%

## Act 2 bosses (n=102, fatal 24)

| Arrival HP | Fights | Fatal | Rate |
|---|---|---|---|
| under 40% | 10 | 5 | 50% |
| 40–50% | 9 | 1 | 11% |
| 50–60% | 17 | 5 | 29% |
| 60–70% | 23 | 6 | 26% |
| 70–80% | 14 | 3 | 21% |
| 80–90% | 10 | 2 | 20% |
| 90–100% | 19 | 2 | 11% |

Logistic fit, P(fatal | arrival HP): 40% → 37%, 50% → 31%, 60% → 26%, 70% → 22%, 80% → 18%, 90% → 14%, 100% → 11%

## Act 3 bosses (n=81, fatal 26)

| Arrival HP | Fights | Fatal | Rate |
|---|---|---|---|
| under 40% | 5 | 5 | 100% |
| 40–50% | 6 | 3 | 50% |
| 50–60% | 7 | 3 | 43% |
| 60–70% | 5 | 2 | 40% |
| 70–80% | 15 | 2 | 13% |
| 80–90% | 10 | 4 | 40% |
| 90–100% | 33 | 7 | 21% |

Logistic fit, P(fatal | arrival HP): 40% → 64%, 50% → 55%, 60% → 46%, 70% → 37%, 80% → 29%, 90% → 22%, 100% → 16%

## What a pre-boss heal is worth on the fitted curves

A rest heals 30% of max HP rounded down (237 of 297 rests match exactly; about 29% after rounding, used here). Reduction in fitted fatal-fight probability from healing at each HP level (capped at 100%):

| HP at the rest site | Act 1 | Act 2 | Act 3 |
|---|---|---|---|
| 30% | −17 pts | −16 pts | −25 pts |
| 40% | −15 pts | −15 pts | −26 pts |
| 50% | −13 pts | −13 pts | −25 pts |
| 60% | −11 pts | −12 pts | −23 pts |
| 70% | −9 pts | −10 pts | −20 pts |
| 80% | −6 pts | −6 pts | −13 pts |

These are upper bounds (see Reading the evidence). An upgrade's value cannot be read from these data.

## What the Player actually did right before a boss

| HP at the rest site | Healed: fatal at boss | Smithed: fatal at boss |
|---|---|---|
| under 50% | 31/99 (31%) | 18/61 (30%) |
| 50–70% | 5/20 (25%) | 18/76 (24%) |
| 70%+ | 2/11 (18%) | 13/90 (14%) |

Choices are confounded: the Player smiths at low HP mainly when the deck already looks strong.

## Reading the evidence

- **The arrival curve says HP matters:** fatal rates fall from about 30–40% (under 50% HP) to about 10–15% (80%+) in Acts 1–2, and more steeply in Act 3.
- **The Player's own choices say a heal bought little:** at the same HP, healing and smithing were followed by almost the same boss death rate (under 50%: 31% against 30%; 50–70%: 25% against 24%).
- The two are confounded in opposite directions. The curve credits HP with what strong decks do. The direct comparison hides the heal's value, because the Player smithed mostly when the deck was already strong. The true value of a pre-boss heal is probably smaller than the heal table above suggests (treat it as an upper bound), but not zero.

## Rule to test (H1, revised)

- **Acts 1–2:** rest before the boss if HP is below the boss's median damage + 10 (playbook section 10; typically 40–60% of max). Otherwise smith.
- **Act 3 and the A10 double boss:** rest if HP is below **70%**. Act 3 shows the steepest arrival effect, and A10 adds a second boss.
- Phase 4 records arrival HP, the rest choice and the outcome for every boss, so the rule can be checked against the Player's baseline (equally likely to heal or smith at 37% HP before a boss).
