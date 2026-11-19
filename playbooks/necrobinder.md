# Necrobinder Playbook

Version: v0.1 (draft) · Game version: v0.107.1 · Last updated: 2026-11-19 · Status: groundwork for Phase 5, written overnight before any Necrobinder study. Not ready to play from.

Same rules and labels as `playbooks/ironclad.md`. Everything general there (path planning, the elite HP rule, pre-boss rest rule, corner targets, potion policy, combat checklist, boss plans) applies here too, unless this file says otherwise.

**Sources:**
- Card data: `knowledge/cards/necrobinder.md` `[GAME-EXTRACT]`
- The Player's Necrobinder history: `reports/phase1/*-necrobinder.*` `[PLAYER-DATA]`
- Character comparison: `reports/phase1/cross-character.md`

---

## 1. Overview
- **Start:** 66 HP (the lowest of the four characters), 99 gold, relic Bound Phylactery. Deck: 4 Strike, 4 Defend, Bodyguard (Summon 5), Unleash. `[GAME-EXTRACT]`
- **Osty:** a companion that Summon cards build up and that some attacks act through: "Your Osty deals X damage" (Poke, Snap, Flatten). It appears in fights as a separate creature with its own HP. `[GAME-EXTRACT]` cards; the exact Summon and Osty rules are to be documented in Phase 5 (P5.E2.S2).
- **Doom:** an enemy dies at the end of its turn if its HP is at or below its Doom. Sources include Blight Strike, Negative Pulse (7), Scourge (13), End of Days (29). `[GAME-EXTRACT]`
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

Version note: none of the three sources is v0.111.1. Nat 1 says the 11/12 beta made no Necrobinder card changes; v0.108–v0.111 changes to Necrobinder cards have not been checked yet (gap).

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

### 3.3 Starting rule (until Phase 5 study)
Draft by the consensus tier, but treat † cards as one tier lower when the source that rates them highly is MetaBot alone (its sample sizes are unknown). Melancholy and Wisp stay in the pick pool against the consensus, because the Player's outcomes favour them; they are Phase 5 test cards. `[HYPOTHESIS]`

## 4. Rest and elites (the Player's habits)
- Heals at a higher HP than with Ironclad: equally likely to heal or smith at 37% overall, 45% before a boss (Ironclad: 27% and 37%).
- Elite deaths under 50% HP: 2 of 9, against 3 of 63 at 50% or more. The general rule holds: avoid elites under 50%.

## 5. Open questions for Phase 5
- Exact Summon and Osty rules: how Osty's HP works, what happens when Osty dies, whether Osty blocks for you.
- Doom interactions with bosses (Test Subject revives; Knowledge Demon heals).
- Necrobinder archetypes (Doom, Osty and Summon, Ethereal and Retain) and their commit signals.
- Whether the corner targets (block per turn, scaling cards) need adjusting for a character whose damage partly comes through Osty. `tools/deck_metrics.py` does not count Osty damage yet.

## 6. Changelog
- **v0.1 (2026-11-19, overnight):** community tiers from three sources (§3.1), habit discrepancies with the Player's outcomes (§3.2), a starting draft rule (§3.3).
- **v0 (2026-11-19):** groundwork from the extracted game data and the Player's history.
