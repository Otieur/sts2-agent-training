# Deck Features on Arrival: Survived against Fatal Fights

All characters, solo runs on v0.107.1. Bosses and elites with at least 2 fatal fights. Features count cards in the deck at the start of the fight floor, with card roles from the extracted game data `[GAME-EXTRACT]`. Evidence is `[PLAYER-DATA]` from small samples: each difference is a hypothesis to test. Different characters' decks are pooled, which hides character-specific effects.

Script: `tools/analyze_deck_features.py`.

## KNOWLEDGE_DEMON_BOSS

Survived 27 (median damage 29.0), fatal 13 (median damage 53.0). Characters: Ironclad 12, Necrobinder 11, Regent 9, Silent 6, Defect 2.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 1.0 | 0.6 | -0.3 |
| Hit-all attacks | 1.1 | 1.2 | +0.1 |
| Single-hit hit-all attacks | 0.8 | 0.9 | +0.1 |
| Attacks costing 0–1 | 8.3 | 8.9 | +0.7 |
| Block cards | 6.7 | 6.1 | -0.7 |
| Draw cards | 2.7 | 2.3 | -0.4 |
| Energy cards | 1.6 | 0.8 | -0.8 |
| Strength cards | 0.7 | 0.2 | -0.4 |
| Vulnerable cards | 1.6 | 1.4 | -0.2 |
| Weak cards | 0.9 | 1.2 | +0.2 |
| Powers | 2.7 | 1.8 | -0.9 |
| Hit instances per card | 0.44 | 0.46 | +0.02 |
| Deck size | 26.7 | 25.6 | -1.1 |

## VANTOM_BOSS

Survived 16 (median damage 24.5), fatal 12 (median damage 42.5). Characters: Ironclad 11, Silent 6, Necrobinder 5, Regent 4, Defect 2.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 0.8 | 0.7 | -0.1 |
| Hit-all attacks | 0.4 | 1.0 | +0.6 |
| Single-hit hit-all attacks | 0.3 | 0.8 | +0.5 |
| Attacks costing 0–1 | 7.1 | 7.7 | +0.6 |
| Block cards | 5.6 | 5.8 | +0.2 |
| Draw cards | 2.1 | 1.0 | -1.1 |
| Energy cards | 0.6 | 0.4 | -0.1 |
| Strength cards | 0.4 | 0.1 | -0.3 |
| Vulnerable cards | 1.1 | 1.0 | -0.1 |
| Weak cards | 0.7 | 0.4 | -0.3 |
| Powers | 1.1 | 0.9 | -0.1 |
| Hit instances per card | 0.50 | 0.53 | +0.03 |
| Deck size | 19.2 | 19.6 | +0.4 |

## AEONGLASS_BOSS

Survived 18 (median damage 31.0), fatal 10 (median damage 46.0). Characters: Necrobinder 10, Silent 8, Ironclad 5, Regent 4, Defect 1.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 1.6 | 0.8 | -0.8 |
| Hit-all attacks | 0.8 | 1.5 | +0.7 |
| Single-hit hit-all attacks | 0.6 | 1.3 | +0.7 |
| Attacks costing 0–1 | 8.4 | 7.9 | -0.5 |
| Block cards | 7.4 | 6.7 | -0.7 |
| Draw cards | 3.6 | 4.2 | +0.6 |
| Energy cards | 2.1 | 1.9 | -0.2 |
| Strength cards | 0.8 | 0.3 | -0.5 |
| Vulnerable cards | 1.7 | 1.2 | -0.5 |
| Weak cards | 1.1 | 1.2 | +0.1 |
| Powers | 4.8 | 4.3 | -0.5 |
| Hit instances per card | 0.41 | 0.36 | -0.06 |
| Deck size | 32.6 | 31.0 | -1.6 |

## BYRDONIS_ELITE

Survived 25 (median damage 18.0), fatal 9 (median damage 22.0). Characters: Ironclad 10, Regent 10, Silent 8, Necrobinder 4, Defect 2.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 0.4 | 0.2 | -0.2 |
| Hit-all attacks | 0.6 | 0.6 | -0.0 |
| Single-hit hit-all attacks | 0.5 | 0.4 | -0.1 |
| Attacks costing 0–1 | 6.9 | 7.0 | +0.1 |
| Block cards | 5.7 | 5.1 | -0.6 |
| Draw cards | 1.0 | 0.9 | -0.2 |
| Energy cards | 0.5 | 0.2 | -0.3 |
| Strength cards | 0.2 | 0.2 | -0.0 |
| Vulnerable cards | 1.0 | 1.0 | +0.0 |
| Weak cards | 0.7 | 0.4 | -0.2 |
| Powers | 0.5 | 1.3 | +0.9 |
| Hit instances per card | 0.50 | 0.43 | -0.07 |
| Deck size | 16.9 | 17.8 | +0.9 |

## QUEEN_BOSS

Survived 16 (median damage 28.0), fatal 8 (median damage 53.0). Characters: Ironclad 7, Silent 6, Regent 6, Necrobinder 5.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 1.7 | 1.0 | -0.7 |
| Hit-all attacks | 1.0 | 1.2 | +0.2 |
| Single-hit hit-all attacks | 0.9 | 1.1 | +0.2 |
| Attacks costing 0–1 | 7.3 | 10.9 | +3.6 |
| Block cards | 7.0 | 8.8 | +1.8 |
| Draw cards | 3.9 | 2.2 | -1.6 |
| Energy cards | 1.5 | 2.5 | +1.0 |
| Strength cards | 0.6 | 1.2 | +0.6 |
| Vulnerable cards | 2.1 | 2.2 | +0.2 |
| Weak cards | 1.3 | 1.4 | +0.1 |
| Powers | 4.2 | 3.8 | -0.4 |
| Hit instances per card | 0.37 | 0.45 | +0.08 |
| Deck size | 32.0 | 35.2 | +3.2 |

## TEST_SUBJECT_BOSS

Survived 21 (median damage 36.0), fatal 8 (median damage 67.0). Characters: Silent 8, Regent 8, Necrobinder 6, Ironclad 5, Defect 2.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 1.2 | 0.6 | -0.6 |
| Hit-all attacks | 1.2 | 0.5 | -0.7 |
| Single-hit hit-all attacks | 1.0 | 0.5 | -0.5 |
| Attacks costing 0–1 | 8.5 | 10.6 | +2.1 |
| Block cards | 8.6 | 7.2 | -1.3 |
| Draw cards | 4.7 | 5.0 | +0.3 |
| Energy cards | 2.1 | 1.4 | -0.8 |
| Strength cards | 0.6 | 0.5 | -0.1 |
| Vulnerable cards | 1.7 | 1.2 | -0.5 |
| Weak cards | 1.4 | 1.8 | +0.3 |
| Powers | 3.9 | 2.9 | -1.0 |
| Hit instances per card | 0.39 | 0.42 | +0.03 |
| Deck size | 33.8 | 33.2 | -0.5 |

## WATERFALL_GIANT_BOSS

Survived 22 (median damage 25.0), fatal 8 (median damage 39.0). Characters: Silent 8, Regent 8, Necrobinder 7, Ironclad 5, Defect 2.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 0.5 | 0.5 | +0.0 |
| Hit-all attacks | 0.4 | 0.6 | +0.2 |
| Single-hit hit-all attacks | 0.4 | 0.6 | +0.2 |
| Attacks costing 0–1 | 7.7 | 7.1 | -0.6 |
| Block cards | 6.1 | 5.5 | -0.6 |
| Draw cards | 1.6 | 1.8 | +0.2 |
| Energy cards | 0.6 | 0.6 | -0.0 |
| Strength cards | 0.3 | 0.0 | -0.3 |
| Vulnerable cards | 0.7 | 1.2 | +0.5 |
| Weak cards | 0.9 | 0.8 | -0.2 |
| Powers | 1.3 | 1.1 | -0.2 |
| Hit instances per card | 0.46 | 0.47 | +0.01 |
| Deck size | 20.3 | 19.9 | -0.4 |

## SOUL_FYSH_BOSS

Survived 19 (median damage 25.0), fatal 8 (median damage 41.0). Characters: Silent 7, Necrobinder 7, Ironclad 7, Regent 6.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 0.6 | 0.2 | -0.3 |
| Hit-all attacks | 0.5 | 0.5 | +0.0 |
| Single-hit hit-all attacks | 0.4 | 0.5 | +0.1 |
| Attacks costing 0–1 | 7.3 | 7.8 | +0.4 |
| Block cards | 6.3 | 5.5 | -0.8 |
| Draw cards | 1.2 | 1.6 | +0.4 |
| Energy cards | 0.8 | 0.5 | -0.3 |
| Strength cards | 0.4 | 0.0 | -0.4 |
| Vulnerable cards | 0.9 | 1.4 | +0.4 |
| Weak cards | 0.9 | 0.6 | -0.3 |
| Powers | 1.2 | 1.1 | -0.1 |
| Hit instances per card | 0.44 | 0.46 | +0.01 |
| Deck size | 21.2 | 20.0 | -1.2 |

## CEREMONIAL_BEAST_BOSS

Survived 26 (median damage 27.5), fatal 6 (median damage 34.5). Characters: Silent 9, Regent 8, Necrobinder 7, Ironclad 7, Defect 1.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 0.4 | 0.8 | +0.4 |
| Hit-all attacks | 0.4 | 0.2 | -0.3 |
| Single-hit hit-all attacks | 0.4 | 0.2 | -0.3 |
| Attacks costing 0–1 | 6.6 | 7.0 | +0.4 |
| Block cards | 5.7 | 5.8 | +0.1 |
| Draw cards | 1.2 | 1.7 | +0.4 |
| Energy cards | 0.7 | 0.5 | -0.2 |
| Strength cards | 0.1 | 0.3 | +0.2 |
| Vulnerable cards | 1.2 | 0.5 | -0.7 |
| Weak cards | 0.9 | 0.8 | -0.1 |
| Powers | 0.8 | 1.0 | +0.2 |
| Hit instances per card | 0.46 | 0.51 | +0.05 |
| Deck size | 18.8 | 19.0 | +0.2 |

## THE_INSATIABLE_BOSS

Survived 28 (median damage 23.5), fatal 6 (median damage 33.5). Characters: Necrobinder 11, Silent 10, Ironclad 6, Regent 5, Defect 2.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 0.9 | 1.7 | +0.8 |
| Hit-all attacks | 0.6 | 1.2 | +0.5 |
| Single-hit hit-all attacks | 0.5 | 0.8 | +0.3 |
| Attacks costing 0–1 | 8.2 | 9.0 | +0.8 |
| Block cards | 6.9 | 7.7 | +0.8 |
| Draw cards | 2.7 | 2.5 | -0.2 |
| Energy cards | 1.4 | 1.0 | -0.4 |
| Strength cards | 0.4 | 0.7 | +0.2 |
| Vulnerable cards | 1.1 | 1.2 | +0.0 |
| Weak cards | 1.2 | 1.0 | -0.2 |
| Powers | 3.1 | 2.7 | -0.5 |
| Hit instances per card | 0.43 | 0.49 | +0.05 |
| Deck size | 26.6 | 28.0 | +1.4 |

## ENTOMANCER_ELITE

Survived 30 (median damage 15.0), fatal 6 (median damage 36.0). Characters: Ironclad 13, Regent 10, Necrobinder 9, Silent 3, Defect 1.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 1.2 | 1.0 | -0.2 |
| Hit-all attacks | 1.2 | 0.8 | -0.4 |
| Single-hit hit-all attacks | 0.9 | 0.7 | -0.2 |
| Attacks costing 0–1 | 8.1 | 9.5 | +1.4 |
| Block cards | 7.1 | 6.8 | -0.3 |
| Draw cards | 1.9 | 1.0 | -0.9 |
| Energy cards | 1.2 | 1.2 | -0.0 |
| Strength cards | 0.5 | 0.5 | -0.0 |
| Vulnerable cards | 1.5 | 2.2 | +0.6 |
| Weak cards | 1.0 | 0.7 | -0.3 |
| Powers | 2.3 | 2.0 | -0.3 |
| Hit instances per card | 0.49 | 0.53 | +0.04 |
| Deck size | 25.4 | 25.5 | +0.1 |

## THE_KIN_BOSS

Survived 23 (median damage 24.0), fatal 5 (median damage 35.0). Characters: Ironclad 8, Silent 7, Regent 7, Necrobinder 6.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 0.7 | 0.0 | -0.7 |
| Hit-all attacks | 0.8 | 0.8 | +0.0 |
| Single-hit hit-all attacks | 0.6 | 0.8 | +0.2 |
| Attacks costing 0–1 | 7.3 | 8.6 | +1.3 |
| Block cards | 6.0 | 6.0 | +0.0 |
| Draw cards | 0.9 | 2.0 | +1.1 |
| Energy cards | 0.4 | 0.2 | -0.2 |
| Strength cards | 0.3 | 0.0 | -0.3 |
| Vulnerable cards | 1.2 | 0.6 | -0.6 |
| Weak cards | 0.7 | 0.8 | +0.1 |
| Powers | 1.0 | 0.4 | -0.6 |
| Hit instances per card | 0.52 | 0.45 | -0.07 |
| Deck size | 19.2 | 20.2 | +1.0 |

## KAISER_CRAB_BOSS

Survived 23 (median damage 36.0), fatal 5 (median damage 47.0). Characters: Silent 9, Regent 7, Necrobinder 6, Ironclad 6.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 1.0 | 1.8 | +0.8 |
| Hit-all attacks | 1.0 | 2.0 | +1.0 |
| Single-hit hit-all attacks | 0.7 | 1.4 | +0.7 |
| Attacks costing 0–1 | 8.3 | 9.0 | +0.7 |
| Block cards | 7.0 | 7.2 | +0.2 |
| Draw cards | 2.7 | 2.4 | -0.3 |
| Energy cards | 1.2 | 0.6 | -0.6 |
| Strength cards | 0.3 | 0.2 | -0.1 |
| Vulnerable cards | 1.5 | 2.2 | +0.7 |
| Weak cards | 1.3 | 0.8 | -0.5 |
| Powers | 2.1 | 2.8 | +0.7 |
| Hit instances per card | 0.46 | 0.50 | +0.04 |
| Deck size | 26.2 | 27.2 | +1.0 |

## PHROG_PARASITE_ELITE

Survived 30 (median damage 13.0), fatal 4 (median damage 45.0). Characters: Silent 9, Necrobinder 9, Ironclad 9, Regent 5, Defect 2.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 0.6 | 0.5 | -0.1 |
| Hit-all attacks | 0.5 | 0.0 | -0.5 |
| Single-hit hit-all attacks | 0.4 | 0.0 | -0.4 |
| Attacks costing 0–1 | 6.8 | 6.2 | -0.6 |
| Block cards | 5.6 | 6.5 | +0.9 |
| Draw cards | 0.9 | 1.0 | +0.1 |
| Energy cards | 0.3 | 0.2 | -0.1 |
| Strength cards | 0.1 | 0.2 | +0.2 |
| Vulnerable cards | 1.0 | 1.2 | +0.3 |
| Weak cards | 0.5 | 1.8 | +1.3 |
| Powers | 0.6 | 1.0 | +0.4 |
| Hit instances per card | 0.51 | 0.45 | -0.07 |
| Deck size | 17.3 | 17.8 | +0.4 |

## LAGAVULIN_MATRIARCH_BOSS

Survived 28 (median damage 25.0), fatal 4 (median damage 43.0). Characters: Necrobinder 15, Ironclad 8, Regent 7, Silent 2.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 0.5 | 0.8 | +0.3 |
| Hit-all attacks | 0.4 | 0.8 | +0.4 |
| Single-hit hit-all attacks | 0.4 | 0.5 | +0.1 |
| Attacks costing 0–1 | 7.2 | 8.5 | +1.3 |
| Block cards | 5.6 | 6.2 | +0.6 |
| Draw cards | 1.0 | 1.5 | +0.5 |
| Energy cards | 0.7 | 0.8 | +0.0 |
| Strength cards | 0.3 | 0.2 | -0.0 |
| Vulnerable cards | 0.9 | 0.8 | -0.1 |
| Weak cards | 0.6 | 0.5 | -0.1 |
| Powers | 0.9 | 0.5 | -0.4 |
| Hit instances per card | 0.45 | 0.56 | +0.11 |
| Deck size | 19.2 | 21.0 | +1.8 |

## INFESTED_PRISMS_ELITE

Survived 44 (median damage 23.5), fatal 3 (median damage 35.0). Characters: Regent 14, Necrobinder 13, Silent 12, Ironclad 8.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 0.9 | 0.7 | -0.2 |
| Hit-all attacks | 0.9 | 1.3 | +0.4 |
| Single-hit hit-all attacks | 0.6 | 1.3 | +0.7 |
| Attacks costing 0–1 | 8.4 | 6.3 | -2.1 |
| Block cards | 6.6 | 6.7 | +0.0 |
| Draw cards | 2.1 | 1.3 | -0.8 |
| Energy cards | 1.2 | 1.0 | -0.2 |
| Strength cards | 0.2 | 0.0 | -0.2 |
| Vulnerable cards | 1.5 | 1.7 | +0.2 |
| Weak cards | 1.3 | 1.7 | +0.4 |
| Powers | 2.2 | 2.0 | -0.2 |
| Hit instances per card | 0.46 | 0.38 | -0.08 |
| Deck size | 25.4 | 22.7 | -2.7 |

## MECHA_KNIGHT_ELITE

Survived 21 (median damage 23.0), fatal 3 (median damage 45.0). Characters: Necrobinder 8, Silent 5, Ironclad 5, Regent 4, Defect 2.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 1.0 | 2.3 | +1.3 |
| Hit-all attacks | 1.2 | 1.3 | +0.1 |
| Single-hit hit-all attacks | 1.0 | 0.7 | -0.4 |
| Attacks costing 0–1 | 8.6 | 8.7 | +0.1 |
| Block cards | 6.7 | 7.7 | +1.0 |
| Draw cards | 3.4 | 2.3 | -1.1 |
| Energy cards | 2.1 | 0.3 | -1.8 |
| Strength cards | 0.8 | 1.3 | +0.5 |
| Vulnerable cards | 1.6 | 2.7 | +1.0 |
| Weak cards | 1.3 | 0.7 | -0.7 |
| Powers | 4.0 | 5.0 | +1.0 |
| Hit instances per card | 0.41 | 0.45 | +0.04 |
| Deck size | 30.5 | 32.0 | +1.5 |

## DECIMILLIPEDE_ELITE

Survived 37 (median damage 26.0), fatal 2 (median damage 57.0). Characters: Silent 10, Necrobinder 10, Regent 10, Ironclad 8, Defect 1.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 0.9 | 1.0 | +0.1 |
| Hit-all attacks | 0.9 | 2.0 | +1.1 |
| Single-hit hit-all attacks | 0.7 | 1.5 | +0.8 |
| Attacks costing 0–1 | 8.2 | 11.0 | +2.8 |
| Block cards | 6.6 | 7.0 | +0.4 |
| Draw cards | 2.3 | 3.0 | +0.7 |
| Energy cards | 1.1 | 0.5 | -0.6 |
| Strength cards | 0.2 | 0.0 | -0.2 |
| Vulnerable cards | 1.4 | 0.0 | -1.4 |
| Weak cards | 1.1 | 1.0 | -0.1 |
| Powers | 2.0 | 1.0 | -1.0 |
| Hit instances per card | 0.47 | 0.59 | +0.12 |
| Deck size | 25.0 | 25.5 | +0.5 |

## SKULKING_COLONY_ELITE

Survived 33 (median damage 17.0), fatal 2 (median damage 41.0). Characters: Silent 10, Ironclad 9, Necrobinder 9, Regent 6, Defect 1.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 0.4 | 1.5 | +1.1 |
| Hit-all attacks | 0.4 | 0.5 | +0.1 |
| Single-hit hit-all attacks | 0.3 | 0.5 | +0.2 |
| Attacks costing 0–1 | 6.5 | 7.0 | +0.5 |
| Block cards | 5.6 | 4.5 | -1.1 |
| Draw cards | 1.1 | 0.0 | -1.1 |
| Energy cards | 0.4 | 1.0 | +0.6 |
| Strength cards | 0.2 | 1.0 | +0.8 |
| Vulnerable cards | 0.7 | 1.0 | +0.3 |
| Weak cards | 0.6 | 0.0 | -0.6 |
| Powers | 0.6 | 0.5 | -0.1 |
| Hit instances per card | 0.48 | 0.60 | +0.12 |
| Deck size | 17.2 | 20.0 | +2.8 |

## PHANTASMAL_GARDENERS_ELITE

Survived 24 (median damage 13.0), fatal 2 (median damage 25.5). Characters: Ironclad 8, Regent 6, Necrobinder 6, Silent 5, Defect 1.

| Feature (cards in deck) | Survived (mean) | Fatal (mean) | Fatal − survived |
|---|---|---|---|
| Multi-hit attacks | 0.4 | 0.0 | -0.4 |
| Hit-all attacks | 0.3 | 0.5 | +0.2 |
| Single-hit hit-all attacks | 0.3 | 0.5 | +0.2 |
| Attacks costing 0–1 | 6.8 | 8.0 | +1.2 |
| Block cards | 5.7 | 5.0 | -0.7 |
| Draw cards | 1.5 | 1.5 | +0.0 |
| Energy cards | 0.4 | 0.5 | +0.1 |
| Strength cards | 0.2 | 0.0 | -0.2 |
| Vulnerable cards | 0.9 | 2.0 | +1.1 |
| Weak cards | 0.5 | 1.5 | +1.0 |
| Powers | 0.9 | 0.0 | -0.9 |
| Hit instances per card | 0.47 | 0.45 | -0.02 |
| Deck size | 18.0 | 19.0 | +1.0 |
