# Sources

Accessed 2026-11-19 unless noted. **Quality** reflects version match with v0.107.1, method and checks against the extracted game data (a source that names cards or relics absent from the game data is marked unreliable).

## Data sources (game data)
| Source | Kind | Version | Quality | Notes |
|---|---|---|---|---|
| STS2-Agent `docs/game-knowledge` index (vendor/STS2-Agent @ 5d7c306) | Decompiled game data: 577 cards, 121 monsters, 289 relics, 64 potions, 257 powers, 68 events | Generated 2026-09-21; build not stated; **predates v0.107.1** (eleven v0.107.1 changes show old values; see `knowledge/version-delta-extract-to-v0.107.1.md`) | High for mechanics; numbers two updates behind the target | Imported as `[GAME-EXTRACT]` into `knowledge/data/extract-2026-09-21/`. Missing: Not Yet (card), Aeonglass (boss). |

## Aggregated statistics
| Source | URL | Kind | Version | Quality | Notes |
|---|---|---|---|---|---|
| Slay the Spire Wiki, StS2 enemy pages | https://slaythespire.wiki.gg/wiki/Slay_the_Spire_2:Bosses | Community wiki with move tables and per-version update history | Pages edited 2026-11-14/15; banners point to the v0.113 beta; histories list v0.111.1 changes | High for move order and numbers (structured, versioned) | Used 2026-11-19 for Vantom, Ceremonial Beast, Waterfall Giant, Entomancer, The Insatiable, Soul Fysh, The Kin, Byrdonis, Knowledge Demon, Lagavulin Matriarch, Aeonglass; corrected the Entomancer, Byrdonis and Lagavulin models and the Kin follower offset; settled Aeonglass (gap 29) |
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

## Necrobinder sources (accessed 2026-11-19)
| Source | URL | Kind | Version | Quality | Notes |
|---|---|---|---|---|---|
| Spire Codex: Necrobinder tier list guide | https://spire-codex.com/guides/necrobinder-tier-list | Win rate when picked, community runs | Main branch, mid-July 2026 (v0.107.x era) | High (best version match), partial list | Glimpse Beyond 62%, Neurosurge 56.5%, Shared Fate 55.4%, Banshee's Cry 54.9%, Legion of Bone 52.7%, Misery 52.6%; Reap and Sow at the bottom (~30–33%). Three letter tiers derived from win rates (see the builder). |
| MetaBot: Necrobinder tier list | https://metabot.gg/en/slay-the-spire-2/cards/tier-list/necrobinder | Win rate of runs containing the card, pick rate | Period "November 2026"; version and sample sizes not stated | Medium-low | The page mixes in colorless, event and curse cards; only Necrobinder cards are used. Six cards show 0.0%, a likely data gap. |
| Nat 1 Gaming (DoggertQBones): Necrobinder card tier list | https://nat1gaming.com/sts2/tier-list/necrobinder-card-tier-list/ | Expert opinion | 11/12 beta patch; the article says that patch did not change Necrobinder cards | Medium (not our version) | Full list. |
| BrokenBuilds: Necrobinder card tier list (Major Update 2) | https://brokenbuilds.gg/slay-the-spire-2/tier-lists/slay-the-spire-2-necrobinder-card-tier-list | Tier list | v0.107.1 per search summary | Not used | 403. The search summary says Capture Spirit tops the list after the v0.107 reworks; unverified. |
| Necrobinder build guides (search summaries): BrokenBuilds Soul Engine guide, FinalBoss character and defensive scaling guides, Mobalytics guide | https://brokenbuilds.gg/slay-the-spire-2/guides/slay-the-spire-2-necrobinder-soul-engine-build-guide ; https://finalboss.io/slay-the-spire-2-how-to-play-necrobinder | Archetype descriptions | v0.107.1 (BrokenBuilds); others unstated | Low-medium: summaries only; six card names in them do not exist in the game data | Used for `archetypes-necrobinder.md` after the name check |
| Dygamelab blog posts (April 30, May 7) | https://dygamelab.blogspot.com/2026/05/slay-spire-2-necrobinder-card-tier-list.html | Blog tier list | Pre-v0.107 | Low (old) | Not used. |

## Relic sources (accessed 2026-11-19)
| Source | URL | Kind | Quality | Notes |
|---|---|---|---|---|
| MetaBot Ironclad relic tier list | https://metabot.gg/en/slay-the-spire-2/relics/tier-list/ironclad | Win rate of runs carrying the relic | **Unusable for choices**: biased by acquisition time (Burning Blood, carried by every Ironclad from floor 1, 14%; Act 3 relics 50–80%) | Not imported. The Player's Ancient choices are analysed at the decision point instead (`reports/phase2/ancient-relics.md`). |
| Mobalytics relic tier list | https://mobalytics.gg/slay-the-spire-2/tier-lists/relics | Editorial | Not read (403) | |
| BrokenBuilds Neow relic guide; search summaries | https://brokenbuilds.gg/slay-the-spire-2/guides/slay-the-spire-2-act-1-neow-boss-relic-guide | Relic effects | Effects only | Hefty Tablet: choose 1 of 3 Rare cards and add an Injury. Fishing Rod: every 3 normal combats, upgrade a random card (v0.107.1 wording; one database says every combat). |

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
