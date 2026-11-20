# Overnight Report (2026-11-20)

> **Draft, being written during the session.** The full record is `docs/overnight-log.md`. Sections marked "pending" are filled in at the end.

## 1. Summary
1. **The simulator plays whole runs on its own.** A new run starts from any seed, with the Ancient, the map, every room type (fights, elites, bosses, events including the Crystal Sphere minigame, rest sites, shops, treasure), act changes and the final boss, all through the game's own code and its multiplayer-capable synchronizers. Fights also start from nothing (any encounter, deck, relics, potions, HP): 85 of 85 encounters start and finish.
2. **It reproduces the real game exactly where that can be checked.** The recorded fight replays with 26 of 26 states equal; the Agent's recorded run, replayed from its seed with its choices, matches the game in 71 of 71 checks over all 48 floors (encounters, card rewards, shop stock, relics, chest relics, event and Ancient options).
3. **Background runs are fast.** About 7.7 ms per decision including the Python driver; a full-length run takes 4 to 16 s on one host, about 500 to 560 full-length runs per hour per host (more when runs end early).
4. **The open list is closed except two items** (section 4): the known draw positions are kept by the sampler, the hidden pre-rolled state is inventoried (new rule FP-16), state cloning works (exact, but too slow for search yet), and the sandbox test is automated (saves unchanged, no network).
5. **Real play (stage 5):** pending.

## 2. Work done (by stage)
| Stage | Result |
|---|---|
| 1 A fight from nothing | Done: 85 of 85 encounters; custom deck, relics, potions, HP; potion actions |
| 2 A new run from a seed | Done: whole runs through every room type, act changes and the final boss |
| 3 Run-level fidelity | Done: 71 of 71 checks over 48 floors (`reports/phase7/run-fidelity.md`) |
| 4 Background runs | Done: batches of 40 flow-test runs (test-only max HP, so a weak driver reaches every room) and 30 normal runs; see section 3 |
| 5 Real A1 run on profile 2 | pending |
| 6 Open list | Draw positions, hidden-state inventory, cloning, sandbox test done; see section 4 |
| 7 This report | |

## 3. Problems the background runs found, and the fixes
The first batches finished every normal run but left 13 of 40 flow-test runs looping or stuck. Each cause was in the host, not the game:

| Symptom | Cause | Fix |
|---|---|---|
| Electric Shrymp (an Orobas Ancient option) looped | The host built the card options for deck selections itself and offered a card the enchantment cannot apply to | Card selections now go through the game's own local selector (`CardSelectCmd.PushSelector`, the mechanism the Whispering Earring relic uses): the game computes the options and limits, and syncs the answer as in co-op |
| Crystal Sphere looped | Its minigame waits for clicks from its screen | New `minigame` screen: uncover cells with the small or big tool; the observation shows only uncovered cells |
| Amalgamator stopped half-way | A raw real-time pause in the event's code, then a UI call inlined into game code | The pause completes at once (a rewrite of those two methods only); see the inlining row |
| Doom kills stopped a fight | A death animation helper reached with a stand-in creature node | The display-only helper is skipped (its one logic call is empty or visual) |
| Trial event failed | A portrait effect, then a UI call inlined into the event | Effect skipped; UI made inert earlier and more widely |
| Battleworn Dummy's event never finished | After an event's fight, the host never pressed "proceed", which is where the game returns to the event | The proceed step now runs once per combat room, also when there are no rewards |
| **Inlining** | The JIT inlines small methods into callers compiled earlier, so a patch applied later is bypassed (`NGame.ScreenShakeTrauma`, `NEventLayout.RemoveNodesOnPortrait`, the `NGame.Instance` getter) | UI classes are made inert first, before any other patch, and eagerly (230 UI classes and 26 game scene-node classes); `Instance` fields of inert singletons are filled; documented as FI-7b |
| Silent failures | The game catches some exceptions and only logs them; a driver then retried an option that had silently done nothing | Any caught game exception now fails the step with the game's message |

After the fixes: pending (final batch numbers).

## 4. Open list
| Item | Result |
|---|---|
| Known draw positions (FP-5) | The host logs the visible draw-pile operations since the last shuffle (top, bottom, random inserts, draws seen from the top, unseen removals, the discard pile shuffled in) and samples orders consistent with them by rejection sampling. A card put on top stays on top in 12 of 12 samples while the rest varies. pending: fallbacks on the recorded fight |
| Hidden pre-rolled state (OQ7.3) | Inventory written as FP-16: each act's encounter and event sequences, its Ancient and bosses, pre-shuffled relic queues, pity counters, event values rolled at start, the Crystal Sphere's items. None is in an observation; run-level search must re-sample them |
| State cloning (P7.E4.S4) | Snapshot and restore by recipe (origin plus the steps since): 12 of 12 restores exact. pending: speed |
| Sandbox test (P7.E3.S3) | Automated: 1,291 save files unchanged, sandbox home empty, no socket in 27 polls |
| More recorded fights | pending (stage 5) |

## 5. Co-op readiness
- Fights: the acting player is an index; the sampler covers every player's draw pile; replays apply any player's events.
- Card choices go through the game's local selector and `PlayerChoiceSynchronizer`, the co-op path.
- Run level: every room action uses the multiplayer-capable synchronizers. Missing: a two-player run in one process (`RunManager.SetUpNewMultiplayer` needs a host-side net service that delivers the second seat's actions). Not started.

## 6. What needs you
pending
