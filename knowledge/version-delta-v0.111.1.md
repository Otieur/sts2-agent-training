# Version Change: v0.107.1 → v0.111.1 (main branch, 2026-11-16)

**What happened:** on 2026-11-16/17 Mega Crit moved the main branch from v0.107.1 to **v0.111.1** ("Major Update 3"), which bundles beta patches v0.108.0–v0.111.0. It does not include v0.113 content (the Fool, Blitz, Dread). Discovered overnight 2026-11-19; the plan's "main branch v0.107.1" was written before this.

Sources: [wiki: V0.111.1 – Major Update 3](https://slaythespire.wiki.gg/wiki/Slay_the_Spire_2:V0.111.1_-_Major_Update_3), [wiki: V0.111.0 – Beta Patch](https://slaythespire.wiki.gg/wiki/Slay_the_Spire_2:V0.111.0_-_Beta_Patch), Mega Crit's announcement (X/Steam). `[COMMUNITY]` (official patch notes summarised by the wiki).

## What it means for this project
| Area | Effect |
|---|---|
| **Target game version** | Switching Steam off the beta now gives **v0.111.1**, not v0.107.1. Phase 0 targets v0.111.1. |
| **The Player's history (227 runs on v0.107.1)** | Still the best available data: most content is unchanged. Benchmarks and pick rates are one patch cycle old. Buffed or nerfed cards and enemies below are flagged. |
| **Extracted game data** | Older still: it predates v0.107.1 (`knowledge/version-delta-extract-to-v0.107.1.md`). Apply that delta first, then this one. Corrected 2026-11-19 01:42; the rest of this row is the earlier, wrong reading: it matches v0.107.x–v0.110, i.e. the Player's history, better than the new main. Cards and enemies below differ on v0.111.1. |
| **Mod choice (decision 0001)** | STS2-Agent's docs reference v0.111.0, the base of the new main. STS2MCP's latest fix targets v0.107. **STS2-Agent is now the better version match.** See the revised `docs/decisions/0001-mod-and-branch.md`. |
| **Exam seeds** | **Seeds are now 12 characters long.** The five exam seeds (10 characters, from v0.107.1) may be rejected or generate different maps. Test one; if it fails, pick new exam seeds from the first v0.111.1 runs. |
| **Community tiers** | Spire Codex (July, v0.107) and MetaBot predate v0.111.1. Nat 1 Gaming rates the v0.113 beta. Re-check tiers for the changed cards below. |

## Ironclad cards changed on v0.111.1
| Card | Change | Effect on the playbook |
|---|---|---|
| **Expect a Fight** | Reworked: now Uncommon Skill, cost 3, 15 (16) block + 5 (8) block per Strength | Old energy card replaced by a Strength-scaling block card. Its tier and Player data no longer apply. Good in Strength decks. |
| **Demon Form** | Strength per turn 2 (3) → **3 (4)** | Stronger: already S-tier; the best scaling card got better. |
| **Mangle** | Damage 15 (20) → **20 (26)** | Buff |
| **Pact's End** | 17 (23) → 18 (24) | Small buff |
| **Howl from Beyond** | 16 (21) → 18 (24) | Buff |
| **Primal Force** | Giant Rock token 16 (20) → 20 (24) | Buff |
| **Rampage** | Base 9 → 10; scaling 5 (9) → 5 (10) | Buff |
| **Setup Strike** | Strength 2 (3) → 3 (4) | Buff |
| **Forgotten Ritual** | No longer needs a card exhausted to give energy | Buff (easier to use) |
| **Colossus** | Block 5 (8) → 4 (7) | Nerf |
| **Crimson Mantle** | Block 8 (10) → 7 (10) | Small nerf |
| **Taunt** | Block 7 (8) → 6 (7); Uncommon → Common | Nerf; seen more often |
| **Bloodletting** | Common → Uncommon | Seen less often |
| **Cruelty** | Rare → Uncommon | Seen more often |
| **Dominate** | Uncommon → **Rare** | Seen less often: the Player's favourite card is now rarer |
| **Tank** (multiplayer) | Now +50% damage taken, allies −50% (was double / half) | Co-op only |
| New multiplayer cards | Midnight (Rare, 60 (72), cheaper per card exhausted by anyone), Blaze (gives another player 5 (7) Strength), Outrage (0 cost, 9 (13), copies to everyone's discard) | Co-op only (Phase 6) |

## Enemies changed on v0.111.1
| Enemy | Change | Note to update |
|---|---|---|
| **Aeonglass** | Ebb damage 26 (32) → 22 (26) | The boss note already uses 22 (its source was updated on 2026-11-16). |
| **Torch Head Amalgam** (Queen fight) | **New turn-1 Strong Tackle: 26 (32)**; Weak Tackle at A9 14 (15) → 14 (16); Tackle at A9 18 (19) → 18 (22) | Queen plan: block 26+ on turn 1. |
| **Mecha Knight** | Flamethrower turn now also deals 8 (12) | Elite note: the Burns turn is no longer free. |
| **Entomancer** | HP at A8+ 145 (155) → 145 (165) | Longer fight at A8+. |
| **Soul Fysh** | De-Gas at A9: 16 (17) → 16 (18) | Minor. |
| Axebot | Hammer Uppercut 12 (14) → 14 (18); One-Two 9 (10)×2 → 10 (11)×2; +10 max HP per respawn | Minor (Act 3 hallway). |
| Exoskeleton, Globe Head, Louse Progenitor | Small A8–A9 buffs | Minor. |
| Multiplayer | Enemy block scaling reduced in 2-player runs | Phase 6. |

## Necrobinder cards changed on v0.111.1
Source: wiki V0.111.1 – Major Update 3, accessed 2026-11-19 `[COMMUNITY]`. Matters for Phase 5 and for `knowledge/community/necrobinder-tiers.md` (no tier source is on v0.111.1).

| Card | Change | Tier impact `[HYPOTHESIS]` |
|---|---|---|
| **Eidolon** | Reworked: was "Exhaust your hand; 9 exhausted gives 1 Intangible". Now "Play all Ethereal cards in your Exhaust pile. Exhaust." Upgrade lowers cost by 1 | Old F/D ratings no longer apply. Good only in Ethereal-heavy decks |
| **Time's Up** | No longer exhausts | Up |
| **Legion of Bone** | No longer exhausts | Up (Spire Codex already rated it A) |
| **Sacrifice** | Block 2× → 3× Osty's max HP | Up (the Player rated it A, consensus D) |
| **Soul Storm** | Extra damage 2 (3) → 4 (6) | Up (the Player rated it S, consensus C) |
| **The Scythe** | Damage scaling 4 (5) → 5 (7) | Up |
| Reave | 9 (11) → 10 (13) | Small up |
| Shroud | Block 2 (3) → 3 (4) | Small up |
| Haunt | HP loss 6 (8) → 7 (9) | Small up |
| Transfigure | Can no longer be generated in combat (bug fix) | None for drafting |

New multiplayer-only Necrobinder cards: Underworld (Doom from allies' attack damage), Soulbound, Cacophony.
Fixes: Cruelty's extra damage now applies to Osty attacks; Enfeebling Touch with Misery no longer gives Artifact enemies Strength; a crash when an enemy dies to Doom.

## Silent and Regent (brief, for Phase 5 choice)
- **Silent:** Outbreak is now a Rare 3-cost skill (9 (12) Poison to all); Well-Laid Plans is a Rare power that stops end-of-turn discards; Haze costs 2 and adds Weak; Tracking is 50% (was double); Expertise draws 2 (3) with Retain; Accelerant and Echoing Slash are now Uncommon.
- **Regent:** many star costs lowered (Guiding Star 1, Alignment 2, Resonance 2); Devastate 35 (45); Regalite gives 4 Block the first time each turn you create a card (was 2 per creation); small nerfs to Pillar of Creation, Collision Course, Refine Blade.

## Relics changed for every character (selected)
History Course now repeats only Attacks; Tough Egg gives 1 more max HP; Unsettling Lamp is no longer used up when Artifact blocks the debuff; Hand Drill triggers from Expose. The rest are bug fixes.

## General changes
- Uncommon cards appear slightly more often.
- Seeds are 12 characters.
- Nearly any potion can be used on other players (co-op).
- End-of-turn Orb passives trigger before Doom; Regen Potion heals before Doom.
- Custom Run has a Randomize button.
- New Ancient relics and changes (Neow's Sacrifice, Dowsing Rod; Diamond Diadem rework; Beautiful Bracelet, Fur Coat, Signet Ring, Meat Cleaver, Toybox, Seal of Gold, Toasty Mittens changes).
