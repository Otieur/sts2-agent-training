# Version Delta: the Extract → v0.107.1

Written 2026-11-19 (overnight). Corrects an earlier conclusion the same night that the extracted game data matched v0.107.x–v0.110.

## Finding
The decompiled game data in `knowledge/data/extract-2026-09-21/` (`[GAME-EXTRACT]`) **predates v0.107.1**, the version of the Player's history. It is at least one main-branch update older: every v0.107.1 change that could be checked shows the old value.

| Check (v0.107.1 patch note, wiki) | Value before → after v0.107.1 | Value in the extract | Extract is |
|---|---|---|---|
| Act 3 boss | Doormaker → **Aeonglass** | Aeonglass missing | pre-v0.107.1 |
| Soul Fysh Scream | 11 (12) → 13 (15) | 11 | pre |
| Owl Magistrate HP | 234 (243) → 231 (247) | 234 | pre |
| Slimed Berserker HP | 266 (276) → 261 (281) | 266 | pre |
| Scroll of Biting HP | 31–38 → 30–37 | 31–38 | pre |
| Ruby Raider Assassin | 11 (12) → 10 (11) | 11 | pre |
| Haunted Ship | Ramming Speed removed | Ramming Speed present | pre |
| Punch Construct | Fast Punch applies Frail (was Weak) | Weak | pre |
| Conflagration | 8 (9) + 2 per other Attack → 2 to all, 4 (5) times | 8 + 2 per Attack | pre |
| Drum of Battle | 0-cost Power → 1-cost Skill (draw 2; 2 (3) energy when exhausted) | 0-cost Power | pre |
| Unrelenting | 12 (18) → 14 (20) | 12 | pre |

Source: wiki "V0.107.1 – Major Update 2" (https://slaythespire.wiki.gg/wiki/Slay_the_Spire_2:V0.107.1_-_Major_Update_2), accessed 2026-11-19 `[COMMUNITY]`; patched.gg's copy of the notes agrees on the enemy numbers. The extract's exact build is still unknown. Its file date (2026-09-21) is after v0.107.1, so the generator probably ran on an older decompile.

## Consequences
- **Two patch cycles behind the target.** Extract values are older than the Player's history (v0.107.1), which is older than the game the Agent plays (v0.111.1). Apply this delta, then `knowledge/version-delta-v0.111.1.md`.
- **Most extract values are still right.** Each update changed a few dozen items, and the rest of the content is unchanged. Treat an extract number as correct unless one of the two delta files lists the item.
- **Tools:** `tools/deck_metrics.py` applies the card changes from both deltas through `knowledge/data/card-patches.json` (`apply_patches(version)`). History analyses (`deck_metrics.py` report, `analyze_deck_features.py`) use v0.107.1 values; `draft.py`, `plan_turn.py` and the card references (`build_card_reference.py`) use v0.111.1. Rerunning the history analyses with v0.107.1 values moved a few figures by about one point (for example Knowledge Demon fatal-deck powers 1.8 → 1.7); no conclusion changed. Counting Osty attacks later moved the all-character Act 1 raw-damage terciles to 21% / 22% / 31%. Enemy changes are not patched: enemy notes carry warnings instead.

## Ironclad cards changed on v0.107.1
| Card | Change | Note |
|---|---|---|
| Conflagration | Was 8 (9) to all, +2 (3) per other Attack played this turn. Now 2 damage to all enemies, 4 (5) times | Multi-hit hit-all now: good against Slippery and against multi-enemy fights |
| Drum of Battle | Was a 0-cost Power. Now a 1-cost Uncommon Skill: draw 2; when exhausted, gain 2 (3) Energy | The Player's history is all v0.107.1, so the Player's 9/21 picks were of the new card; only the extract shows the old one |
| Howl from Beyond | Trigger moved from start of turn to end of turn | |
| Unrelenting | 12 (18) → 14 (20) | |
| Entrench | Gains extra Block from enchantments like Nimble | Minor |
| Hellraiser | Plays at most 9 cards per turn against infinite-HP enemies | Bug fix |

## Enemies changed on v0.107.1
| Enemy | Change | Note updated |
|---|---|---|
| **Doormaker → Aeonglass** | Act 3 boss replaced | `knowledge/bosses/AEONGLASS_BOSS.md` already relies on community data |
| **Infested Prism** | Reworked (no numbers in the notes) | `knowledge/enemies/INFESTED_PRISMS_ELITE.md`: move list from the extract is outdated |
| **Axebots** | Now a single, stronger Axebot | Hallway note not written; v0.111.1 buffed it again |
| **Skulking Colony** | HP 70 (75) → 75 (80); Hardened Shell 15 → 20; Smash removed, Zoom on turns 1–2; no longer gains Block; +1 Strength at high ascension | `knowledge/enemies/SKULKING_COLONY_ELITE.md` |
| Haunted Ship | 3 Weak on turn 1; Ramming Speed removed; alternates Swipe and Stomp | No note |
| Punch Construct | Order reversed (Ready → Fast Punch → Strong Punch); Frail instead of Weak | No note |
| Scrolls of Biting | HP 31 (32)–38 (39) → 30 (33)–37 (39) | Minor |
| Owl Magistrate | HP 234 (243) → 231 (247) | Minor |
| Slimed Berserker | HP 266 (276) → 261 (281) | Minor |
| **Soul Fysh** | Scream 11 (12) → 13 (15) | `knowledge/bosses/SOUL_FYSH_BOSS.md` |
| Ruby Raider Assassin | 11 (12) → 10 (11) | Minor |
| Vantom | Nerfed at lower ascension (no numbers) | `knowledge/bosses/VANTOM_BOSS.md` |
| Waterfall Giant | Heal at lower ascension 15 → 10 (15) | `knowledge/bosses/WATERFALL_GIANT_BOSS.md` |
| Multiplayer | Scaling reduced for Artifact, Slippery and Skittish | Phase 6 |

## Other changes on v0.107.1
- Colorless: Fasten block 5 (7) → 4 (6); Gold Axe counts all players' cards in multiplayer; Neow's Fury lets you choose the returned cards.
- Mechanics: cost effects that make the next card free now take precedence over cost increases. The PRNG changed, so seeds from earlier versions give different runs.
