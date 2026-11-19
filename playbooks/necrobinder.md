# Necrobinder Playbook

Version: v0 (draft) · Game version: v0.107.1 · Last updated: 2026-11-19 · Status: groundwork for Phase 5, written overnight before any Necrobinder study. Not ready to play from.

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

## 3. Card baseline (the Player's habit, not strength)
- **Highest:** Demesne, Fetch, Neurosurge, Borrowed Time, Seance, Enfeebling Touch, Sentry Mode, Melancholy, Friendship, Hang, Death's Door, End of Days. `[PLAYER-DATA]` (`reports/phase1/card-ranking-necrobinder.md`)
- **Below skipping:** Sow, Delay, Defile, Eradicate, Bury, Danse Macabre, Necro Mastery, Sculpting Strike, Reave, Spur, Reap, Lethality.
- Community tiers: Phase 5 (P5.E2.S3). MetaBot and Nat 1 Gaming both publish Necrobinder lists.

## 4. Rest and elites (the Player's habits)
- Heals at a higher HP than with Ironclad: equally likely to heal or smith at 37% overall, 45% before a boss (Ironclad: 27% and 37%).
- Elite deaths under 50% HP: 2 of 9, against 3 of 63 at 50% or more. The general rule holds: avoid elites under 50%.

## 5. Open questions for Phase 5
- Exact Summon and Osty rules: how Osty's HP works, what happens when Osty dies, whether Osty blocks for you.
- Doom interactions with bosses (Test Subject revives; Knowledge Demon heals).
- Necrobinder archetypes (Doom, Osty and Summon, Ethereal and Retain) and their commit signals.
- Whether the corner targets (block per turn, scaling cards) need adjusting for a character whose damage partly comes through Osty. `tools/deck_metrics.py` does not count Osty damage yet.

## 6. Changelog
- **v0 (2026-11-19):** groundwork from the extracted game data and the Player's history.
