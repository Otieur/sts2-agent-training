# Necrobinder Playbook

Version: v0.3 (draft) · Knowledge base: v0.107.1 · Target game: v0.111.1 · Last updated: 2026-11-19 · Status: groundwork for Phase 5, written overnight before any Necrobinder study. Not ready to play from.

Same rules and labels as `playbooks/ironclad.md`. Everything general there (path planning, the elite HP rule, pre-boss rest rule, corner targets, potion policy, combat checklist, boss plans) applies here too, unless this file says otherwise.

**Sources:**
- Card data: `knowledge/cards/necrobinder.md` `[GAME-EXTRACT]`
- The Player's Necrobinder history: `reports/phase1/*-necrobinder.*` `[PLAYER-DATA]`
- Character comparison: `reports/phase1/cross-character.md`

---

## 1. Overview
- **Start:** 66 HP (the lowest of the four characters), 99 gold, relic Bound Phylactery. Deck: 4 Strike, 4 Defend, Bodyguard (Summon 5), Unleash. `[GAME-EXTRACT]`
- **Osty** `[GAME-EXTRACT]` unless noted:
  - An allied creature (`OSTY`, 1 base HP) shown under `combat.player.pets` in STS2-Agent. **Summon N adds N to Osty's HP** (`OstyCmd.Summon`), and Bound Phylactery summons 1 at the start of each combat and each turn.
  - **Osty takes the unblocked damage aimed at you while it lives** (`DIE_FOR_YOU_POWER`: unblocked damage is redirected to its owner, Osty). Your effective HP is your HP plus Osty's, and block still applies first. Community guides call Osty a meat shield and the Phylactery the real HP bar `[COMMUNITY]`.
  - Osty attacks through cards ("Your Osty deals X damage": Poke 6, Fetch 3, Snap 7, Flatten 12, High Five 11 to all, Bone Shards 9 to all). They do nothing while Osty is dead. Your Strength probably does not apply (the damage is Osty's) `[HYPOTHESIS]`; Cruelty applies to Osty attacks since v0.111.1 `[COMMUNITY]`.
  - Some cards kill your own Osty for value (Bone Shards: 9 to all + 9 block; Sacrifice: block equal to 3× Osty's max HP since v0.111.1). Summon again afterwards.
  - `tools/plan_turn.py` models Osty: Summon before Osty attacks, Osty absorbing unblocked damage, kill-own-Osty cards.
- **Doom:** a debuff; at the end of the enemy's turn it dies if its HP is at or below its Doom (`DOOM_POWER`: `CurrentHp <= Amount`) `[GAME-EXTRACT]`. Sources include Blight Strike, Negative Pulse (7), Scourge (13), End of Days (29), Countdown (Doom each turn) and Reaper Form (Doom on every damage dealt).
- **Energy and draw engines:** Demesne (+draw and +energy each turn), Friendship (+energy) `[GAME-EXTRACT]`.
- **Ethereal and Retain** are common card keywords (9 and 6 cards). Ethereal cards are lost if not played; Retain cards stay in hand.
- **The Player's record** (v0.107.1): 59 runs, 11 wins of 52 finished.
  - By band: A0–4 5/12, A5–9 5/28, A10 1/12.
  - Deaths spread evenly by act (15 / 15 / 11), unlike Ironclad, which dies mostly in Act 1.
  - 25 of 41 deaths came at bosses. `[PLAYER-DATA]`

## 2. Boss priorities (from the Player's history)
| Boss | Fights / fatal / median damage | Note |
|---|---|---|
| Test Subject | 6 / 4 / 53 | Worst boss for this character (Ironclad: 0/5). Needs Act 3 scaling and block. |
| Knowledge Demon | 11 / 4 / 25 | Same scaling problem as Ironclad (H7). |
| Aeonglass | 10 / 3 / 41 | Watch the card count (Wither every 6 cards). Retain and big cards help. |
| Vantom | 5 / 3 / 27 | Slippery: Osty hits and multi-hit Eradicate (11×?) strip stacks. |
| Soul Fysh | 7 / 3 / 33 | Exhaust Beckon cards (14 Necrobinder cards exhaust). |
| Lagavulin Matriarch | 15 / 0 / 21 | Comfortable. |

## 3. Card tiers

### 3.1 Community consensus
From `knowledge/community/necrobinder-tiers.md` `[COMMUNITY]` (built 2026-11-19 by `tools/build_community_tiers.py`). Three sources:
- **Spire Codex:** win rate when picked, main branch mid-July 2026; partial list, weight 2.
- **MetaBot:** win rate of runs containing the card, period "November 2026", version not stated; survivorship-biased, converted to quintiles, weight 1.
- **Nat 1 Gaming:** expert list on the 11/12 beta patch, weight 1.

† marks a spread of 2+ tiers between sources. The sources disagree on about two cards in five (34 of 84 carry †; Ironclad: 29 of 83), so treat single tiers as soft.

- **S:** Neurosurge, Glimpse Beyond, Call of the Void, Eradicate, Friendship, Transfigure
- **A:** Banshee's Cry, Shared Fate†, Borrowed Time, Debilitate†, Demesne†, Enfeebling Touch†, Hang, Pagestorm†, Squeeze, Undeath, Legion of Bone†, Misery, Spirit of Ash†
- **B:** Oblivion†, Reanimate, Seance†, Defy†, Dirge†, Dredge, End of Days†, Lethality, Pull from Below†, Rattle, Sleight of Flesh, The Scythe†, Time's Up, Necro Mastery, Countdown, Deathbringer†, Death's Door, Fetch†, Forbidden Grimoire, High Five, No Escape†, Putrefy†, Reaper Form, Shroud
- **C:** Bone Shards†, Calcify†, Capture Spirit†, Danse Macabre†, Death March, Delay, Devour Life, Graveblast, Grave Warden†, Haunt, Invoke†, Parse†, Sentry Mode, Snap†, Soul Storm†, Veilpiercer†
- **D:** Bury, Cleanse, Eidolon†, Fear, Flatten†, Melancholy†, Negative Pulse†, Protector†, Right Hand Hand, Sacrifice, Scourge†, Severance, Spur, Afterlife, Blight Strike, Defile, Drain Power, Poke, Pull Aggro, Reave, Sculpting Strike, Wisp, Reap, Sow, Sic 'Em

Version note: none of the three sources is v0.111.1. v0.111.1 changed ten Necrobinder cards (`knowledge/version-delta-v0.111.1.md`): Eidolon is reworked (ignore its old tier); Time's Up and Legion of Bone no longer exhaust; Sacrifice, Soul Storm and The Scythe got clear buffs. Raise those five by about one tier until v0.111.1 data exists. `[HYPOTHESIS]`

### 3.2 The Player's habit against consensus
29 cards differ by 2+ tiers (`knowledge/community/discrepancies-necrobinder.md`). Where the card appears in 10+ finished runs, the Player's own outcome is shown: wins with the card in the final deck against wins without `[PLAYER-DATA]`. This is weak evidence: longer runs collect more cards, so any card looks better in winning decks.

| Card | Consensus | Player habit | Wins with / without | Reading |
|---|---|---|---|---|
| Melancholy | D | S | 6/14 vs 5/38 | Outcome leans to the Player. Test it. |
| Wisp | D | A | 8/21 vs 3/31 | Outcome leans to the Player. Test it. |
| Death March | C | S | 5/14 vs 6/38 | Outcome leans to the Player. |
| Fetch | B | S | 6/19 vs 5/33 | Slight lean to the Player. |
| Seance | B | S | 4/12 vs 7/40 | Slight lean to the Player. |
| Death's Door | B | S | 3/12 vs 8/40 | Neutral. |
| Parse | C | A | 3/11 vs 8/41 | Neutral. |
| Defy | B | D | 3/11 vs 8/41 | Neutral. |
| Drain Power | D | A | 2/21 vs 9/31 | Outcome supports the consensus. Take it less. |

- **The Player skips cards the consensus rates highly:** Eradicate (S, picked 0/10), Banshee's Cry, Debilitate, Pagestorm, Undeath, Misery (all A), Lethality and Necro Mastery (B, 0/24 and 0/15). Not enough runs with these cards to judge outcomes. `[HYPOTHESIS]` Eradicate and Banshee's Cry are the first to test, since they are multi-hit and AoE damage, which the Player's Vantom and hallway deaths suggest the deck lacks.
- **The Player rates higher:** Sentry Mode, Soul Storm, Sacrifice, Sic 'Em, End of Days, Capture Spirit, Devour Life (no outcome data).

### 3.2b Decision-point check (`reports/phase2/card-choices-necrobinder.md`)
Act survival when a card was picked against when it was passed on the same kind of screen (44 cards) `[PLAYER-DATA, weak]`:
- **The consensus tiers do not predict outcomes for Necrobinder** (weighted effect: A +6, B −9, C −9, D +8 points), unlike Ironclad, where A-tier picks were +17 and C/D −13 to −16. Together with the version mismatch and the sources' disagreement, this argues for treating Necrobinder tiers as weak until Phase 5 data exists.
- Signals near p = 0.05: Death March (C; 13/17 against 4/11, p = 0.05), Cleanse (D; 8/8 against 11/18, p = 0.06), Drain Power (D; 15/19 against 24/46, p = 0.06, but won less often when picked), Haunt (C; 1/6 against 12/18, p = 0.06). Death March supports the Player's S rating.

### 3.3 Starting rule (until Phase 5 study)
Draft by the consensus tier, but treat † cards as one tier lower when the source that rates them highly is MetaBot alone (its sample sizes are unknown). Melancholy and Wisp stay in the pick pool against the consensus, because the Player's outcomes favour them; they are Phase 5 test cards. `[HYPOTHESIS]`

## 4. Rest and elites (the Player's habits)
- Heals at a higher HP than with Ironclad: equally likely to heal or smith at 37% overall, 45% before a boss (Ironclad: 27% and 37%).
- Elite deaths under 50% HP: 2 of 9, against 3 of 63 at 50% or more. The general rule holds: avoid elites under 50%.

## 5. Open questions for Phase 5
- Osty: does Osty keep its HP between fights, and does block or Strength apply to it? (Summon and the damage redirect are answered by the game data, §1.)
- Doom interactions with bosses (Test Subject revives; Knowledge Demon heals).
- Necrobinder archetypes (Doom, Osty and Summon, Ethereal and Retain) and their commit signals.
- Whether the corner targets (block per turn, scaling cards) need adjusting for a character whose damage partly comes through Osty. `tools/deck_metrics.py` does not count Osty damage yet.

## 6. Changelog
- **v0.3 (2026-11-19, overnight):** Osty, Summon and Doom rules from the power data (§1); the turn planner models Osty.
- **v0.2 (2026-11-19, overnight):** decision-point check of the tiers (§3.2b): they do not predict the Player's Necrobinder outcomes.
- **v0.1 (2026-11-19, overnight):** community tiers from three sources (§3.1), habit discrepancies with the Player's outcomes (§3.2), a starting draft rule (§3.3).
- **v0 (2026-11-19):** groundwork from the extracted game data and the Player's history.
