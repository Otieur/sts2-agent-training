# Necrobinder Archetypes

Written 2026-11-19 (overnight) for P5.E2.S3. Card groups come from the card text in the extracted game data `[GAME-EXTRACT]`; tiers from `knowledge/community/necrobinder-tiers.md` `[COMMUNITY]` (which did not predict the Player's outcomes, see `playbooks/necrobinder.md` §3.2b). Community descriptions are summarised from search results (sources in `knowledge/community/sources.md`); card names in those summaries were checked against the game data, and six of them (Reckoning, Doomsday, Bone Reinforce, Possession, Soul Eater, Soul Extraction) do not exist, so those claims were dropped.

## Doom (execute)

| Card | Consensus tier |
|---|---|
| Blight Strike | D |
| Borrowed Time | A |
| Deathbringer | B |
| End of Days | B |
| Negative Pulse | D |
| No Escape | B |
| Scourge | D |
| Countdown | B |
| Reaper Form | B |

## Osty and Summon

| Card | Consensus tier |
|---|---|
| Bodyguard | - |
| Afterlife | D |
| Spur | D |
| Legion of Bone | A |
| Invoke | C |
| Reanimate | B |
| Necro Mastery | B |
| Sic Em | D |
| Rattle | B |
| Poke | D |
| Fetch | B |
| Snap | C |
| Flatten | D |
| High Five | B |
| Bone Shards | C |
| Sacrifice | D |
| Right Hand Hand | D |
| Dirge | B |
| Pull Aggro | D |
| Cleanse | D |

## Souls (Soul: 0 cost, draw 2, exhaust)

| Card | Consensus tier |
|---|---|
| Seance | B |
| Soul Storm | C |
| Capture Spirit | C |
| Dirge | B |
| Glimpse Beyond | S |
| Grave Warden | C |
| Reave | D |
| Severance | D |
| Undeath | A |
| Haunt | C |

## How the community describes them `[COMMUNITY]`, search summaries
- **Doom** is a finisher layered on a defensive core, not a deck on its own: enemies die at the end of their turn when HP is at or below their Doom. Stacking Doom without defence fails. The Undying Sigil relic (enemies with Doom at or above their HP deal 50% less damage) supports it.
- **Osty** builds grow Osty with Summon and let him shield (he takes your unblocked damage, `[GAME-EXTRACT]` DIE_FOR_YOU_POWER) and attack. Called the most beginner-friendly plan. Bone Flute (block whenever Osty attacks) supports it.
- **Souls**: cards that create Soul cards (0 cost, draw 2, exhaust) fuel draw and scaling. One guide calls Soul Engine into Doom execute the strongest line on v0.107.1; another calls Souls the most consistent archetype.

## Commit signals `[HYPOTHESIS]`
- **Doom:** a repeatable Doom source (Countdown, Reaper Form, Borrowed Time) plus enough block to survive the turns it needs.
- **Osty:** two or more Summon sources (Bodyguard in the starter deck counts once) plus Osty attacks; consider Sacrifice or Bone Shards as payoffs.
- **Souls:** two or more Soul generators plus Haunt or Soul Storm as payoffs.

## Changed on v0.111.1
Time's Up and Legion of Bone no longer exhaust; Soul Storm (+4 per card), Sacrifice (3x Osty max HP) and The Scythe were buffed; Eidolon was reworked (`knowledge/version-delta-v0.111.1.md`).
