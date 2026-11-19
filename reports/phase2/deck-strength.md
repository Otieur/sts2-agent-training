# Deck Strength at the Boss

All characters, solo, v0.107.1, finished runs: every boss fight with the deck at the start of the boss floor. Built by `tools/deck_metrics.py`. Proxies: average damage and block per turn from random 5-card hands with 3 energy, using base card numbers `[GAME-EXTRACT]`. They ignore Strength, powers, relics, upgrades and cards whose numbers are computed at play time, so they measure the raw attack and defence corners, not scaling. `[PLAYER-DATA]`, observational.

## Survived against fatal boss fights (medians)

| Act | Survived | Fatal | Damage/turn (survived) | Damage/turn (fatal) | Block/turn (survived) | Block/turn (fatal) | Deck size (survived) | Deck size (fatal) |
|---|---|---|---|---|---|---|---|---|
| 1 | 130 | 43 | 12.5 | 13.5 | 8.6 | 8.3 | 19 | 20 |
| 2 | 78 | 24 | 12.3 | 14.1 | 7.7 | 7.9 | 26 | 26 |
| 3 | 55 | 26 | 11.4 | 11.0 | 7.2 | 6.7 | 32 | 32 |

## Fatal rate by damage per turn (terciles within each act)

- **Act 1:** low (4–12): 10/57 fatal (18%) · middle (12–15): 16/58 fatal (28%) · high (15–30): 17/58 fatal (29%)
- **Act 2:** low (3–11): 6/34 fatal (18%) · middle (11–15): 7/34 fatal (21%) · high (15–29): 11/34 fatal (32%)
- **Act 3:** low (0–10): 7/27 fatal (26%) · middle (10–13): 9/27 fatal (33%) · high (13–24): 10/27 fatal (37%)

## Fatal rate by block per turn (terciles within each act)

- **Act 1:** low (5–7): 17/57 fatal (30%) · middle (8–10): 14/58 fatal (24%) · high (10–17): 12/58 fatal (21%)
- **Act 2:** low (4–7): 7/34 fatal (21%) · middle (7–9): 9/34 fatal (26%) · high (9–15): 8/34 fatal (24%)
- **Act 3:** low (3–6): 11/27 fatal (41%) · middle (6–8): 9/27 fatal (33%) · high (8–15): 6/27 fatal (22%)

## Fatal rate by scaling cards in the deck (Powers + Strength cards)

- **Act 1:** 0: 13/47 fatal (28%) · 1: 21/75 fatal (28%) · 2–3: 8/48 fatal (17%) · 4+: 1/3 fatal (33%)
- **Act 2:** 0: 1/3 fatal (33%) · 1: 7/20 fatal (35%) · 2–3: 10/42 fatal (24%) · 4+: 6/37 fatal (16%)
- **Act 3:** 1: 2/5 fatal (40%) · 2–3: 8/23 fatal (35%) · 4+: 16/53 fatal (30%)

## Ironclad only

| Act | Fights | Fatal | Damage/turn survived vs fatal | Block/turn survived vs fatal |
|---|---|---|---|---|
| 1 | 44 | 14 | 14.7 vs 16.8 | 9.6 vs 8.4 |
| 2 | 24 | 8 | 14.8 vs 16.8 | 9.0 vs 8.8 |
| 3 | 17 | 2 | 12.6 vs 13.8 | 8.4 vs 11.1 |

Starter Ironclad deck for reference: 15.0 damage/turn, 9.8 block/turn.

## Reading

- **Raw damage does not protect you at bosses.** Decks in the highest damage tercile died *more* often (Act 1: 29% against 18% for the lowest; Act 2: 32% against 18%). High raw damage usually means a deck of attacks with few powers and block, which wins hallways and loses long boss fights.
- **Block and scaling do.** Act 1: highest block tercile 21% fatal against 30% for the lowest; Act 3: 22% against 41%. Scaling cards: Act 1 decks with 2–3 had 17% fatal against 28% with 0–1; Act 2 decks with 4+ had 16% against 35% with 1.
- **Ironclad:** fatal Act 1 boss decks had more raw damage (16.8 against 14.7 per turn) and less block (8.4 against 9.6).
- Proposed corner targets on arrival at the boss `[HYPOTHESIS H9]`:
  - Act 1: block per turn at least 10, and 2 or more scaling cards
  - Act 2: 4 or more scaling cards
  - Act 3: block per turn at least 8
  Raw damage per turn should not fall below the starter deck's 15 without scaling to replace it.
