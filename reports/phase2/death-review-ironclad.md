# Death Review (Ironclad)

The Player's 40 Ironclad deaths on v0.107.1 (solo, finished runs), replayed through the playbook's checks before the fatal fight. Built by `tools/death_review.py`. A flag means the playbook would have warned; it does not prove the run would have survived. `[PLAYER-DATA, observational]`

**31 of 40 deaths (78%) had at least one flag.**

| Fight type | Deaths | Flagged |
|---|---|---|
| boss | 24 | 22 |
| elite | 10 | 5 |
| monster | 6 | 4 |

| Check | Deaths flagged |
|---|---|
| H9 | 21 |
| Boss checklist | 15 |
| H1 | 9 |
| H5 | 5 |
| H11 | 4 |

**Base rate at bosses** (the same checks on every boss fight; a check is informative only if it flags fatal fights more often than survived ones):

| Check | Fatal boss fights (n=24) | Survived boss fights (n=61) |
|---|---|---|
| any | 92% | 79% |
| H1 | 38% | 21% |
| H9 | 88% | 69% |
| Boss checklist | 62% | 39% |

## Every death

| Seed | Asc | Floor | Room | Encounter | Entry HP | Flags |
|---|---|---|---|---|---|---|
| 9WHJYMRG9F | A0 | 17 | boss | Vantom Boss | 60% | H9: block 7.9; Boss checklist: single-hit hit-all attacks: 1; Boss checklist: draw cards: 0 |
| ZDS61QSYXM | A1 | 33 | boss | Knowledge Demon Boss | 61% | none |
| DGX4GRS6LZ | A2 | 17 | boss | Soul Fysh Boss | 51% | H1: smithed at 41 HP, rule said rest (below 51); H9: scaling 0.0; H9: damage/turn 11.0 below the starter's 15 without scaling to replace it |
| 083QC020L9 | A7 | 43 | elite | Mecha Knight Elite | 42% | H5: elite at 42% HP |
| 9L7089VYN7 | A7 | 7 | elite | Bygone Effigy Elite | 55% | none |
| XLPCMG6AXP | A7 | 7 | elite | Phrog Parasite Elite | 70% | none |
| 1HTWD1ULUB | A7 | 31 | elite | Entomancer Elite | 49% | H5: elite at 49% HP |
| 5F54F0Z4JD | A8 | 48 | boss | Queen Boss | 63% | H1: smithed at 64 HP, rule said rest (below 71); Boss checklist: draw cards: 1 |
| GZCFQLZ3ZM | A8 | 33 | boss | Kaiser Crab Boss | 59% | H9: scaling 3.0; Boss checklist: energy cards: 0 |
| 5LF6MT47G9 | A8 | 25 | monster | Slumbering Beetle Normal | 14% | H11: hallway fight at 14% HP |
| MA7GR2DGYS | A8 | 17 | boss | Lagavulin Matriarch Boss | 55% | H9: block 9.2; H9: scaling 1.0; Boss checklist: powers to set up during sleep: 0 |
| RYN479KJ98 | A9 | 17 | boss | Vantom Boss | 60% | H9: block 9.2; H9: scaling 1.0; Boss checklist: draw cards: 1 |
| HNK20GL1NK | A9 | 17 | boss | Vantom Boss | 28% | H1: smithed at 22 HP, rule said rest (below 48); H9: scaling 1.0; H9: damage/turn 12.1 below the starter's 15 without scaling to replace it; Boss checklist: single-hit hit-all attacks: 1 |
| LH4GDM7D2A | A9 | 14 | elite | Skulking Colony Elite | 57% | none |
| FURNKT35CD | A9 | 28 | elite | Entomancer Elite | 75% | none |
| L5ZPL59UYG | A9 | 17 | boss | Vantom Boss | 68% | H9: block 9.6; H9: scaling 1.0; Boss checklist: single-hit hit-all attacks: 1; Boss checklist: draw cards: 0 |
| TC1312HTHN | A9 | 17 | boss | Soul Fysh Boss | 41% | H9: block 6.3; H9: scaling 0.0 |
| PKZHSGLJF5 | A9 | 33 | boss | Kaiser Crab Boss | 19% | H1: smithed at 15 HP, rule said rest (below 54); H9: scaling 1.0 |
| Y2GHL7K1PD | A10 | 17 | boss | Waterfall Giant Boss | 57% | H1: smithed at 38 HP, rule said rest (below 40); H9: scaling 1.0; H9: damage/turn 13.8 below the starter's 15 without scaling to replace it |
| 571KPSFWRM | A10 | 33 | boss | The Insatiable Boss | 100% | none |
| AB56HWC7A9 | A10 | 14 | elite | Byrdonis Elite | 28% | H5: elite at 28% HP |
| 9NQV2EXKAA | A10 | 6 | monster | Nibbits Normal | 34% | H11: hallway fight at 34% HP |
| GJ819JZQZE | A10 | 6 | monster | Cultists Normal | 57% | none |
| J61T7WBH9G | A10 | 17 | boss | Lagavulin Matriarch Boss | 74% | H9: block 7.9; H9: scaling 0.0; Boss checklist: powers to set up during sleep: 0 |
| QA8YWRT58F | A10 | 24 | elite | Entomancer Elite | 38% | H5: elite at 38% HP |
| 2K292R7M8M | A10 | 7 | elite | Byrdonis Elite | 59% | none |
| 2HEB9EZ1EP | A10 | 33 | boss | Knowledge Demon Boss | 56% | H9: scaling 2.0 |
| QCLTA8ZX2G | A10 | 17 | boss | Ceremonial Beast Boss | 42% | H1: smithed at 35 HP, rule said rest (below 37); H9: block 6.4 |
| 4F8KMAD56G | A10 | 33 | boss | The Insatiable Boss | 54% | H9: scaling 3.0 |
| S5AZQA208Y | A10 | 36 | monster | Devoted Sculptor Weak | 91% | none |
| KT4H1EXD7A | A10 | 49 | boss | Queen Boss | 52% | H9: block 7.3; Boss checklist: draw cards: 2 |
| AJBPD2DHSF | A10 | 12 | elite | Byrdonis Elite | 29% | H5: elite at 29% HP |
| JZVPTDEUYF | A10 | 33 | boss | Knowledge Demon Boss | 82% | H9: scaling 0.0; Boss checklist: Strength cards: 0; Boss checklist: energy cards: 0 |
| T5QZJXC72X | A10 | 17 | boss | Vantom Boss | 79% | H9: block 6.0; H9: scaling 0.0; Boss checklist: single-hit hit-all attacks: 1; Boss checklist: draw cards: 1 |
| JW8LUJHKBY | A10 | 17 | boss | Soul Fysh Boss | 49% | H1: smithed at 39 HP, rule said rest (below 50); H9: block 5.8; H9: scaling 1.0; Boss checklist: exhaust outlets: 0 |
| GK21D6LA3U | A10 | 17 | boss | Vantom Boss | 71% | H1: smithed at 57 HP, rule said rest (below 67); H9: block 8.7; H9: scaling 1.0; Boss checklist: single-hit hit-all attacks: 2; Boss checklist: draw cards: 0 |
| Y22Y9UYEAE | A10 | 22 | monster | Slumbering Beetle Normal | 37% | H11: hallway fight at 37% HP |
| B7RL6AZXGJ | A10 | 17 | boss | Waterfall Giant Boss | 75% | H9: block 4.9; H9: scaling 0.0; Boss checklist: block cards: 4 |
| NTPN13S8AU | A10 | 25 | monster | Chompers Normal | 39% | H11: hallway fight at 39% HP |
| 0K66038N1R | A10 | 33 | boss | Knowledge Demon Boss | 74% | H1: smithed at 59 HP, rule said rest (below 69); H9: scaling 1.0; Boss checklist: Strength cards: 0; Boss checklist: energy cards: 0 |

H11 (hallway fights under 40% HP) covers hallway deaths since 2026-11-19. Boss checklist items are the countable ones in `tools/deck_check.py`; card values are v0.111.1, applied to v0.107.1 decks.
