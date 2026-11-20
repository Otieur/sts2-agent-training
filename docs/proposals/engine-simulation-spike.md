# Spike: Using the Game's Own Engine for Fast Play and Simulation

Status: **desk study done 2026-11-19; prototypes not started** (they need a mod change and game restarts, see "Needs the Player").
Game: v0.111.1 (`sts2.dll` in `SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64/`).
Method: metadata and IL of `sts2.dll` read with `tools/asm/asm.cs`, which uses only the .NET runtime (no decompiler, no third-party code). Indexes are written to `data/asm/` (ignored by git; they describe the game's code and change every patch). Labels follow `docs/README.md`: `[GAME]` means read from the game's code, with the type and method as the evidence pointer.

## Question
Can the agent run the game's real combat logic without animations, (1) to make live play fast and (2) to simulate many turns or fights for search and for learned models? The alternative is our own approximate simulator (`tools/simulate_fight.py`), which does not cover relics, potions, most powers or upgrades.

## Findings

### 1. Waits can be switched off without changing game logic
- `[GAME]` `Commands.Cmd.Wait` returns at once if `NonInteractiveMode.IsActive`, if the wait is 0 seconds or less, if `PrefsSave.FastMode == Instant`, or if combat is ending. Otherwise it awaits a Godot `SceneTree` timer. `Cmd.CustomScaledWait` checks the same flag.
- `[GAME]` `Settings.FastModeType` has four values: None 0, Normal 1, Fast 2, **Instant 3**. The settings screen only offers Normal and Fast. The developer console command `instant` (`DevConsole.ConsoleCommands.InstantConsoleCmd`) sets Instant. The Agent's profile currently has `"fast_mode": "fast"`.
- `[GAME]` `NonInteractiveMode.IsActive` is `TestMode.IsOn || AutoSlayerCheck()`. `AutoSlayerCheck` is a public static settable function. Outside UI code, only waits and pauses read it: `Cmd.Wait`, `Cmd.CustomScaledWait`, `ActionExecutor.ExecuteActions`, `GameAction.Execute`, `CombatManager.Pause/Unpause/WaitForUnpause`.
- `[GAME]` `TestMode` is different: it changes game logic. Examples: `MonsterModel.PerformMove`, several monster moves (Vantom, Flyconid, Myte and others), `MerchantPotionEntry.CalcCost`, `ActModel.GetRandomList`, `MapCmd.SetBossEncounter`, `CreatureCmd.Heal/Kill`, and relic reward generation. **Do not use TestMode** where results must match the real game.
- `[HYPOTHESIS]` Instant mode or NonInteractiveMode removes most of the 3–7 s per end turn measured with Fast mode on. UI code may still await tweens of its own. Prototype 1 measures it.

### 2. Combat is deterministic and replayable
- `[GAME]` `Random.Rng` is counter-based (`_counter`, `_random`) and serializable (`ToSerializable`, `LoadFromSerializable`).
- `[GAME]` Co-op checks determinism: after actions, `RunManager.SendPostActionChecksum` and `Multiplayer.Game.ChecksumTracker` hash a `NetFullCombatState` with XxHash32 and compare peers (`StateDivergenceException`).
- `[GAME]` `Multiplayer.Replay.CombatReplay` records a combat: the `SerializableRun` at room entry, the synchronizer ids, every game action, player choice and hook resume, and the checksums. `CombatReplayWriter.RecordInitialState` is called from `RunManager.EnterMapPointInternal` and `EnterRoomDebug`. Recording is gated by `CombatReplayWriter.IsEnabled`.
- `[GAME]` A debug runner replays a combat and validates it: `Nodes.Debug.Multiplayer.NMultiplayerTest.RunReplay`. It calls `RunState.FromSerializable` → `RunManager.SetUpReplay` → `RunManager.Launch` → `NRun.Create`, fast-forwards the synchronizer ids, and loads the recorded checksums. It warns when the replay's git commit differs from the game's.
- Consequence: any combat state can be reproduced from its room-entry `SerializableRun` plus its action list, and checked against the game's own checksums.

### 3. There is no mid-combat restore
- `[GAME]` `NetFullCombatState` holds creatures (HP, max HP, Block, powers as id and amount), players (piles, potions, relics, energy, stars, turn and phase, orbs) and RNG. In this assembly its only consumer is the checksum code. Nothing restores a combat from it, and it does not carry monster move state.
- `[GAME]` Saves have no combat type: `SerializableRun` and `SerializablePlayer` exist, but no serializable combat.
- Consequence: a search over mid-combat states must replay from room entry for every branch, or clone the live objects. `AbstractModel.MutableClone`/`DeepCloneFields` exist for cards, powers, relics and monsters, but the combat singletons (`CombatManager.Instance`, `RunManager.Instance`) make a second live combat in the same process hard.

### 4. Combat logic is mostly separate from the UI
Methods in `sts2.dll` that call Godot directly (`Godot.*`) or touch UI nodes (`Core.Nodes.*`), by namespace. "Guarded" means the method also checks TestMode or NonInteractiveMode.

| Namespace | Methods | Call Godot | Touch UI nodes | Guarded |
|---|---|---|---|---|
| Hooks | 321 | 0 | 0 | 0 |
| Combat | 526 | 1 | 7 | 2 |
| GameActions | 420 | 2 | 6 | 6 |
| Models.Cards | 4,896 | 20 | 75 | 3 |
| Models.Powers | 2,417 | 12 | 47 | 6 |
| Models.Relics | 2,651 | 1 | 11 | 1 |
| Models.Monsters | 2,932 | 46 | 116 | 27 |
| Models.Potions | 576 | 26 | 30 | 1 |
| Models.Characters | 178 | 33 | 0 | 0 |
| Models.CardPools | 188 | 20 | 0 | 0 |

- `[GAME]` Card Godot calls are mostly `Godot.Color` and `Vector2` values for effects. These are managed structs and work without the engine. A card's play logic builds commands (`StrikeIronclad.OnPlay` → `DamageCmd.Attack(...).FromCard().Targeting().WithHitFx().Execute()`).
- `[HYPOTHESIS]` The UI-node references in models are effect calls that do nothing when the node is missing. Not checked one by one. Character and card-pool Godot calls (asset paths, colours) may run when the model database loads; that is the main risk for running the engine outside Godot.

### 5. Built-in automation and offline instances
- `[GAME]` `AutoSlay.AutoSlayer` is an internal test bot started with `--autoslay` (`--seed`, `--log-file`). It makes random choices, and from turn 3 adds 200 Strength a turn (`AutoSlayConfig.combatStrengthRampPerTurn`). It is a crash tester: useless as a player and as a benchmark. It shows a whole run can be driven with waits off.
- `[GAME]` The developer console has `fight <encounter>`, `card`, `relic`, `potion`, `power`, `energy`, `draw`, `instant`, `godmode`, `win`, `unlock`, `achievement` and more (`DevConsole.ConsoleCommands`). `fight` calls `EncounterModel.DebugRandomizeRng` and `RunManager.EnterRoomDebug`. With these, any fight can be set up with any deck: a practice gym.
- `[OBS]` STS2-Agent starts a second game instance with `--windowed --force-steam off --clientId <n> -fastmp join` (`vendor/STS2-Agent/STS2AIAgent/Multiplayer/CoopLaunchPolicy.cs`). The game supports offline instances with a separate user-data folder (`default/<clientId>`), away from the Steam profiles.
- `[GAME]` The game detects Godot's headless display server (`Nodes.NBackgroundModeHandler.IsHeadless` compares `DisplayServer.GetName()` with `"headless"`).

## Routes

| # | Route | What it gives | Main risk | Effort |
|---|---|---|---|---|
| R1 | Instant mode in the live game | Faster live play: more runs per hour, the same game | UI tweens may still wait; console use may mark the profile | Hours |
| R2 | Record a `CombatReplay` for every Agent fight | Exact action logs and checksums: ground truth for any simulator | Writer gating and output path to confirm | Half a day |
| R3 | Simulator host: our own .NET process loads `sts2.dll`, sets NonInteractiveMode, builds `RunState.FromSerializable`, runs combat | Fights in milliseconds, many processes in parallel: search, then learned models and reinforcement learning become possible | Godot native calls during model-database load or combat setup; singletons; may need Harmony stubs | 1–2 days to a yes or no |
| R4 | Offline headless game instance as a simulator server (`--headless --force-steam off --clientId`, our mod replays a combat plus candidate actions and returns the state) | The real engine with no fidelity gap | Each branch replays from room entry and pays scene setup; slower than R3; a second Godot process per worker | 1–2 days |

Order: R1 and R2 first (cheap, useful whatever happens next), then R3. Fall back to R4 if R3 fails.

## Fair-play rule for search
`[HYPOTHESIS]` A simulator built on the real engine knows the true RNG: the next draws, enemy move rolls and future rewards. Using it for decisions is clairvoyance. Results would not be comparable with the Player's, and the skill would not exist in co-op or for a human. Search must re-sample hidden information for each branch: shuffle the draw pile, roll enemy moves from their known distributions, and leave future rewards unknown. Live state the player can see (hand, piles as sets, intents) stays as it is.

## Prototype plan
1. **Instant mode (R1).** Back up saves (P0.E1). On profile 2, switch to Instant through a small toggle in our own mod, or the console if it opens in release builds. Play one fight with `play_turn.py` and compare end-turn latency with the Fast-mode numbers in `docs/api-notes.md`. Pass: no soft-locks, mod state still settles, latency at least halved.
2. **Replay capture (R2).** Turn on `CombatReplayWriter` for Agent runs and save each replay next to the run journal. Pass: one replay per fight, readable with `CombatReplay.Deserialize`.
3. **Simulator host (R3).** A console program references `sts2.dll` and `GodotSharp.dll` from the game folder (not copied into the repo), initialises the model database, loads a replay from step 2, applies its actions and compares checksums. Pass: checksums match on 10 recorded fights; report fights per second. Fail: list the Godot calls that crash, and judge whether Harmony stubs can cover them.
4. **If R3 fails: headless instance (R4)**, with the same pass test.

## Needs the Player
- A mod change: a new mod of our own, or a patch on top of STS2-Agent, installed in the app bundle. Back up first, and restart the game.
- Whether the developer console may be used on profile 2. Achievements are per Steam account, not per profile; console use could unlock or block them. The offline instance (`--force-steam off`) avoids Steam entirely and is the safer place for console and gym work.
- Running game code in our own process is local research only; nothing from the game is copied into the repository or shared.

## Open questions
- Does model-database initialisation (`ModelDb`) need Godot's resource loader?
- Is `CombatReplayWriter.IsEnabled` set by a preference, a command-line flag, or only in debug builds?
- How much of the remaining end-turn time comes from UI tweens rather than `Cmd.Wait`?
