# Cross-Character Comparison

The Player's solo runs on v0.107.1, by character. Built by `tools/cross_character.py`. `[PLAYER-DATA]`

| Character | Runs | Wins / finished | Wins by band | Deaths Act 1/2/3 | Heal-vs-smith point | …before a boss | Elite deaths: <50% HP vs ≥50% | HP after floor 15: wins vs losses |
|---|---|---|---|---|---|---|---|---|
| Ironclad | 57 | 12/52 | A0-4 5/8 · A5-9 5/20 · A10 2/24 | 22 / 14 / 4 | 27% | 37% | 4/16 vs 5/63 | 64% vs 50% |
| Silent | 51 | 10/43 | A0-4 5/11 · A5-9 5/16 · A10 0/16 | 15 / 8 / 10 | 40% | 45% | 2/17 vs 3/55 | 57% vs 53% |
| Necrobinder | 59 | 11/52 | A0-4 5/12 · A5-9 5/28 · A10 1/12 | 15 / 15 / 11 | 37% | 45% | 2/9 vs 3/63 | 60% vs 46% |
| Regent | 53 | 10/45 | A0-4 5/17 · A5-9 5/18 · A10 0/10 | 14 / 14 / 7 | 31% | 42% | 7/21 vs 3/56 | 53% vs 45% |

## Most frequent killers

- **Ironclad:** VANTOM_BOSS ×6, KNOWLEDGE_DEMON_BOSS ×4, SOUL_FYSH_BOSS ×3
- **Silent:** AEONGLASS_BOSS ×4, CEREMONIAL_BEAST_BOSS ×3, TEST_SUBJECT_BOSS ×3
- **Necrobinder:** KNOWLEDGE_DEMON_BOSS ×4, TEST_SUBJECT_BOSS ×4, AEONGLASS_BOSS ×3
- **Regent:** INFESTED_PRISMS_ELITE ×3, HUNTER_KILLER_NORMAL ×3, KNOWLEDGE_DEMON_BOSS ×2

## Bosses by character (fights / fatal / median damage)

| Boss | Ironclad | Silent | Necrobinder | Regent |
|---|---|---|---|---|
| AEONGLASS_BOSS | 5 / 0 / 48 | 8 / 4 / 40 | 10 / 3 / 41 | 4 / 2 / 20 |
| CEREMONIAL_BEAST_BOSS | 7 / 1 / 39 | 9 / 3 / 36 | 7 / 1 / 28 | 8 / 1 / 17 |
| KAISER_CRAB_BOSS | 6 / 2 / 44 | 9 / 2 / 47 | 6 / 0 / 40 | 7 / 1 / 34 |
| KNOWLEDGE_DEMON_BOSS | 12 / 4 / 45 | 6 / 2 / 42 | 11 / 4 / 25 | 9 / 2 / 35 |
| LAGAVULIN_MATRIARCH_BOSS | 8 / 2 / 28 | 2 / 1 / 27 | 15 / 0 / 21 | 7 / 1 / 33 |
| QUEEN_BOSS | 7 / 2 / 41 | 6 / 2 / 30 | 5 / 2 / 33 | 6 / 2 / 35 |
| SOUL_FYSH_BOSS | 7 / 3 / 33 | 7 / 1 / 26 | 7 / 3 / 33 | 6 / 1 / 29 |
| TEST_SUBJECT_BOSS | 5 / 0 / 44 | 8 / 3 / 44 | 6 / 4 / 53 | 8 / 1 / 41 |
| THE_INSATIABLE_BOSS | 6 / 2 / 32 | 10 / 1 / 28 | 11 / 2 / 24 | 5 / 1 / 21 |
| THE_KIN_BOSS | 8 / 0 / 34 | 7 / 2 / 22 | 6 / 1 / 18 | 7 / 2 / 24 |
| VANTOM_BOSS | 11 / 6 / 48 | 6 / 2 / 24 | 5 / 3 / 27 | 4 / 1 / 16 |
| WATERFALL_GIANT_BOSS | 5 / 2 / 38 | 8 / 2 / 33 | 7 / 2 / 18 | 8 / 2 / 30 |

## Notes for the co-op pairing decision (P5.E6.S2)

- The Player's habits are consistent across characters: low rest thresholds and the same elite risk pattern. The playbook rules (rest thresholds, elite HP rule) apply to every character.
- Boss weaknesses differ by character. A pairing where the Agent's character covers the boss the Player's character struggles with is worth more than raw win rate. See the boss table above.
- Character-specific mechanics (Necrobinder's companion, Regent's Stars) need their own Phase 5 knowledge pass before the Agent can play them.
