# Sources

Accessed 2026-11-19 unless noted. **Quality** reflects version match with v0.107.1, method and checks against the extracted game data (a source that names cards or relics absent from the game data is marked unreliable).

## Data sources (game data)
| Source | Kind | Version | Quality | Notes |
|---|---|---|---|---|
| STS2-Agent `docs/game-knowledge` index (vendor/STS2-Agent @ 5d7c306) | Decompiled game data: 577 cards, 121 monsters, 289 relics, 64 potions, 257 powers, 68 events | Generated 2026-09-21; build not stated (the project targeted v0.111 beta then) | High for mechanics; version unverified | Imported as `[GAME-EXTRACT]` into `knowledge/data/extract-2026-09-21/`. Missing: Not Yet (card), Aeonglass (boss). |

## Aggregated statistics
| Source | URL | Kind | Version | Quality | Notes |
|---|---|---|---|---|---|
| Spire Codex: Ironclad tier list guide | https://spire-codex.com/guides/ironclad-tier-list | Win rate when picked, community-submitted runs | Main branch, mid-July 2026 (v0.107.x era) | **High (best version match)**, but only a partial list | Offering 52.5%, Crimson Mantle 52.3%, Impervious 51.6%, Fiend Fire 50.5%; traps Break and Cinder (~31%). The full tier-list page returned 403. |
| MetaBot | https://metabot.gg/en/slay-the-spire-2/cards/tier-list/ironclad | Win rate of tracked runs containing the card, plus pick rate | Not stated; about 519 runs across all characters seen 2026-11-19 | Medium-low: survivorship bias, no sample sizes, pages disagree with each other | Used at weight 1, converted to quintiles. |
| sts2.untapped.gg | https://sts2.untapped.gg/characters/ironclad | Statistics site | — | Not used: returned 403 | Patch-note articles from this site were used on 2026-11-18. |

## Expert opinion
| Source | URL | Version | Quality | Notes |
|---|---|---|---|---|
| Nat 1 Gaming (DoggertQBones), Ironclad card tier list | https://nat1gaming.com/sts2/tier-list/ironclad-card-tier-list/ | 11/12 beta patch (v0.113.x), 2026-11-15 | Medium: expert, but **not our version** (for example, Break and Vulnerable were changed on the beta) | Full tier list; weight 1. |
| BrokenBuilds strength guide | https://brokenbuilds.gg/slay-the-spire-2/guides/slay-the-spire-2-ironclad-strength-build-guide | "Major Update 2" | Unknown | 403. Search summary only: stack Strength, release through multi-hit. |
| FinalBoss Ironclad guide | https://finalboss.io/slay-the-spire-2-ironclad-guide-from-aggro | Unknown | Not read in full | Search summary: Exhaust is the base of strong late builds. |
| Mobalytics Ironclad guide | https://mobalytics.gg/slay-the-spire-2/characters/ironclad-guide | References beta v0.100 | Low (old) | Not used for tiers. |

## Unreliable (fails the game-data check)
| Source | URL | Problem |
|---|---|---|
| slay-the-spire-2.pages.dev Ironclad builds | https://slay-the-spire-2.pages.dev/guides/ironclad-builds | Names "Limit Break" and the relic "Calipers", neither of which exists in the game data. Looks recycled from Slay the Spire 1. Not used. |
| dood.gg builds (via search summary) | https://dood.gg/sts2/ironclad/builds | Names "Immolate", which is not in the game data. Not used. |

## Patch notes
| Source | URL | Used for |
|---|---|---|
| Wiki: V0.111.1 – Major Update 3 (main branch, 2026-11-16) | https://slaythespire.wiki.gg/wiki/Slay_the_Spire_2:V0.111.1_-_Major_Update_3 | `knowledge/version-delta-v0.111.1.md` |
| Wiki: V0.111.0 – Beta Patch | https://slaythespire.wiki.gg/wiki/Slay_the_Spire_2:V0.111.0_-_Beta_Patch | Same |

Note: the community tier sources above predate v0.111.1. Re-check the changed cards.

## Bosses and mechanics
| Source | URL | Version | Used for |
|---|---|---|---|
| Selphie1999 Gaming: How to Defeat Vantom | https://selphie1999gaming.com/game-guides/slay-the-spire-2/how-to-defeat-vantom-in-slay-the-spire-2/ | 2026-03-27 (early access launch) | Vantom HP and moves. Matches the extracted game data (173 HP; 7, 6×2, 27 + 3 Wounds, +2 Strength). |
| Co-op mechanics guide (allthings.how) | https://allthings.how/slay-the-spire-2-co-op-multiplayer-every-mechanic-and-rule-explained/ | Unknown | Co-op rules (Phase 6). |
| Patch notes v0.107.1, v0.110.0 (untapped.gg articles) | https://sts2.untapped.gg/articles/slay-the-spire-2-v01071-patch-notes-main-branch-update-2 | v0.107.1 | Version context. |
