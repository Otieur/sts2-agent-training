# Overnight Report (2026-11-20)

> **Final report.** The full record is `docs/overnight-log.md`. Session: about 00:00–06:00 EST, autonomous. Work was pushed to the private repository on branch `overnight/2026-11-20-full-run-sim`.

## 1. Summary
1. **The simulator plays whole runs on its own.** A new run starts from any seed and plays through the Ancient, the map, every room type (hallway fights, elites, bosses, events including the Crystal Sphere minigame, rest sites, shops, treasure), act changes and the final boss, all with the game's own code and its multiplayer-capable synchronizers. Fights also start from nothing (any encounter, deck, relics, potions, HP): 85 of 85 encounters start and finish.
2. **It reproduces the real game exactly wherever that can be checked.** All 10 recorded fights replay with every state equal to the game's (218 states; nine of them recorded live tonight, including three elites and a lost boss fight). The Agent's recorded A0 run, replayed from its seed with its choices, matches the game in 71 of 71 checks over all 48 floors.
3. **Background runs are fast and reliable.** Batches of 40 flow-test runs and 30 normal runs from new seeds all finish. About 7.7 ms per decision including the Python driver; a full-length run takes 4–16 s on one host on an idle machine.
4. **The open list is closed.** Known draw positions are kept by the sampler (FP-5); hidden pre-rolled state is inventoried (new rule FP-16); snapshot and restore work (exact, about 45 ms per restore); the sandbox test is automated (saves unchanged, no network).
5. **A first search already beats the rule planner in the simulator** (exploratory): flat Monte Carlo over the planner's candidate actions, scored on re-sampled worlds, was better than the planner in 23 of 36 paired fights and worse in 4 (sign test p = 0.0002); it won 24 against 22 with 32.5 against 28.9 mean HP left. Baselines on the same fights: greedy won 20, random 3.
6. **The real A1 run died to the act 1 boss.** Ironclad A1, seed SANQXMY7C9U8: three elites killed, then died to Ceremonial Beast on floor 17 with the Beast at 77/252 HP. Post-mortem: `runs/2026-11-20-SANQXMY7C9U8/postmortem.md`. The ladder stays at A1.

## 2. Work done (by stage)
| Stage | Result |
|---|---|
| 1 A fight from nothing | Done: 85 of 85 encounters; custom deck, relics, potions, HP; potion actions |
| 2 A new run from a seed | Done: whole runs through every room type, act changes and the final boss |
| 3 Run-level fidelity | Done: 71 of 71 checks over 48 floors (`reports/phase7/run-fidelity.md`) |
| 4 Background runs | Done: 40 of 40 flow-test runs (test-only max HP so a weak driver reaches every room type) and 30 of 30 normal runs finish (`reports/phase7/whole-runs-flow.md`, `whole-runs-play.md`) |
| 5 Real A1 run on profile 2 | Done: died on floor 17 to Ceremonial Beast; 9 fights recorded and kept; all replay exactly |
| 6 Open list | Done: FP-5 sampler, FP-16 inventory, snapshot and restore, sandbox test |
| 7 This report | Done |

## 3. Problems the background runs found, and the fixes
The first batches finished every normal run but left 13 of 40 flow-test runs looping or stuck. Every cause was in the host, not the game:

| Symptom | Cause | Fix |
|---|---|---|
| Electric Shrymp (an Orobas Ancient option) looped | The host built the card options for deck selections itself and offered a card the enchantment cannot apply to | Card selections now go through the game's own local selector (`CardSelectCmd.PushSelector`, the mechanism the Whispering Earring relic uses in ordinary play): the game computes the options and limits and syncs the answer, as in co-op |
| Crystal Sphere looped | Its minigame waits for clicks from its screen | New `minigame` screen; the observation shows only uncovered cells |
| Amalgamator stopped half-way | A raw real-time pause in the event's code | The pause completes at once (a rewrite of those two methods only) |
| Doom kills stopped a fight | A death-animation helper reached with a stand-in creature node | The display-only helper is skipped (its one logic call is empty or visual) |
| Trial event failed | A portrait effect and a null asset cache | Effect skipped; inert helper classes hand out inert objects instead of null |
| Battleworn Dummy's event never finished (and its potion reward was lost) | After an event's fight the host never pressed "proceed", which is where the game returns to the event | The proceed step runs once per combat room, also when there are no rewards |
| **Inlining** | The JIT inlines small methods into callers compiled earlier, so a patch applied later is bypassed (`NGame.ScreenShakeTrauma`, `NEventLayout.RemoveNodesOnPortrait`, the `NGame.Instance` getter) | UI classes are made inert first, before any other patch, and eagerly (230 UI classes and 26 game scene-node classes); `Instance` fields of inert singletons are filled. Documented as FI-7b |
| Silent failures | The game catches some exceptions and only logs them; a driver then retried an option that had done nothing | Any caught game exception now fails the step with the game's message, in runs and in fights |

Also found: the game records every fight in memory whenever TestMode is off; the host never writes the file, so this recording is now turned off (part of the restore speed-up from 289 ms to about 45 ms).

## 4. The real run (stage 5)
- **Setup:** launched through Steam; the mod reported `native_profile_id: 2` before anything was touched. Ironclad A1, random seed SANQXMY7C9U8. No reloads.
- **Course:** Neow's Small Capsule gave Vajra; Byrdonis, Bygone Effigy and Phrog Parasite killed; arrived at the boss with 54/80 after resting. Ceremonial Beast's Plow phase (18, 20, 22) took the run to 18 HP before Plow broke on turn 4; the Ringing turn and a Crush for 17 then killed it at exactly 0 HP on turn 7.
- **Costliest decisions** (post-mortem): on boss turn 2, Cinder+ (which exhausts a random card in hand) was played before a 0-cost Salvo and exhausted it, and the last energy went to Rupture instead of block; the third elite was taken at 52% HP on the path planner's estimate; Neow's 333 gold was declined while the best route had a shop on floor 2 (Feed, tier S, was unaffordable).
- **Confirmed live:** Molten Fist doubles the target's Vulnerable; Slow multiplies damage by 1 + 0.1 per card played this turn; crossing Plow's 150 HP stuns Ceremonial Beast at once and cancels that turn's attack.
- **Tool lessons:** `tools/play_turn.py` does not accept `--tool-pick`; target indexes shift after a kill; potion slot indexes do not shift.
- **Data fix:** `tools/extract_runs.py` read every profile, so the Agent's runs were entering the Player's dataset and benchmarks. It now skips `modded/profile2` by default (`--include-agent` to read it).

## 5. Co-op readiness
- Fights: the acting player is an index; the sampler covers every player's draw pile; replays apply any player's events.
- Card choices go through the game's local selector and `PlayerChoiceSynchronizer`, the co-op path.
- Run level: every room action uses the multiplayer-capable synchronizers. Missing: a two-player run in one process. `RunManager.SetUpNewMultiplayer` takes an `INetHostGameService` (about 30 members, mostly trivial in process); ours would deliver the second seat's actions to the game's registered message handlers as messages from a client, the way `NetReplayGameService` feeds recorded actions. Not started.

## 6. Next steps and what needs you
- **Phase 8 (search):** snapshot and restore exist (about 45 ms); the next step is a search policy on top of decision mode, measured against the rule planner in the simulator.
- **Planner fixes from the run** (proposed in the post-mortem, not applied): Cinder's random exhaust; the Plow stun when its threshold is crossed; Molten Fist's Vulnerable doubling; a Ceremonial Beast block target in `tools/deck_check.py`; a check of the path planner's elite estimate.
- **Run-level search** must first re-sample pre-rolled run content (FP-16); until then the host refuses run-level snapshots.
- **Co-op:** the two-player host (above), and a recorded co-op fight with you to test the replay path.
- **Merge:** tonight's work is on `overnight/2026-11-20-full-run-sim` (pushed to the private repository), not on `master`; merging is your call.
- **Nothing needs undoing.** Your profile 1 was not touched; the game was closed at the main menu after the run.

## 7. After the report (06:00 on)
- **Planner fixes from the run, applied with tests** (564f686): Cinder is ordered after every other planned card; Plow is read as a stun threshold, so a plan that crosses it is valued with the cancelled attack. 191 tool tests pass. The dataset's derived tables were rebuilt after the profile fix (`analyze_*`, `check_playbook.py`: all figures match).
- **First search experiment** (`tools/sim.py search`, `reports/phase8/search-first-experiment.md`, exploratory): on 36 hallway and elite fights from nothing, search won 24 of 36 (mean HP left 32.5) against the planner's 22 (28.9); search was better in 23 fights, worse in 4, equal in 9 (sign test one-sided p = 0.0002; mean paired value difference 11.67, bootstrap 95% interval 4.06 to 22.00). Exploratory (not under the comparison protocol); about 10–50 s per fight in Python.
- **Comparison template** for future experiments: `templates/comparison.md` (P8.E1.S3).

