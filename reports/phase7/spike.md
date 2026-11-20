# Phase 7 Spike: The Game's Combat Logic in Our Own Process

Date: 2026-11-19 · Game v0.111.1 (cc1f9462) · Host: `sim/` on .NET 9.0.23 (the game ships 9.0.7) · Stories P7.E1.S1–S5
Input: `data/sim/replays/2026-11-19-1ZWEN4BFQUZL/floor48-191400.mcr`, the game's own recording of the first Agent run's final fight (Test Subject, three phases; 45 recorded events, 57 checkpoints).

## Verdict: go, route R3

The game's combat logic runs in a separate process of our own, with no Godot engine, no window, no Steam and no saves. On the one recorded fight available it reproduces the real game exactly at every turn boundary.

| Question | Result |
|---|---|
| Does the game assembly load outside the game? | Yes. `sts2.dll`, `GodotSharp.dll` and `0Harmony.dll` are referenced from the install folder; nothing is copied. |
| Does the model database start without the engine? | Yes. 1,660 models (603 cards, 299 relics, 283 powers, 126 monsters, 98 encounters, …). The host's model-id hash is 1568834832, identical to the hash the real game stored in the replay. |
| Can a real fight be rebuilt? | Yes. `RunState.FromSerializable` on the replay's room-entry state: Ironclad, 28 cards, 15 relics, 102/102 HP, Act 3. |
| Does combat run? | Yes. All 45 recorded events applied: card plays, two potions, two choice prompts, five enemy turns, three boss phases (100, 200 and 300 HP). |
| Is it the same fight? | Yes, where compared. The fight ends, and the player's final HP is 87/102, the real run's result. The host produced 26 checkpoints (every turn start, both turn-end phases, enemy turn start and end); **all 26 full combat states are equal, as text, to the states the game recorded**, apart from the anonymised player id. |
| Were saves, Steam or telemetry touched? | No. 0 files changed under the game's save folder and install during the spike; the sandbox home stayed empty. The game chose its no-Steam platform path by itself. Two save calls were reached and stubbed (`SaveRun`, `SaveProgressFile`). |
| Is TestMode off? | Globally, yes. 26 command-layer display helpers run with the flag on for the duration of each call only (see below). |

## How it works

1. **Fake engine table.** GodotSharp reaches the engine only through `Godot.NativeInterop.NativeFuncs`, a table of 225 function pointers the engine normally fills in. The host fills it with stubs that return zero and record the caller. Without this the first engine call kills the process (a segmentation fault with no stack trace). In the whole fight 13 of the 225 functions were called: string and name creation, method lookups, log printing, a dictionary for command-line parsing. None carries game state.
2. **Engine singletons.** 36 placeholder objects for Godot's singletons (OS, Engine, Time and so on).
3. **Inert UI.** Game logic calls 165 UI classes directly. All their methods (3,871) are replaced with ones that do nothing and return an empty value; lookups ("Find…") answer "not found".
4. **Scoped test path.** 26 methods in the command layer (`Commands`, `Entities.Creatures`, `Combat`, `GameActions`) check `TestMode` to skip visuals. The host switches the flag on for exactly the duration of each such call (1,567 calls in the fight) and restores it. Card, monster, relic and power logic never sees the flag.
5. **Game-method stubs** (11): saves, combat asset preloading, localised text (lookups return an empty string; "does this text exist" answers yes), the Power card fly effect.
6. **No mods, no Steam.** The mod manager is marked as finished with an empty list; the game's `NullPlatformUtilStrategy` is selected automatically.
7. **One thread.** A single-threaded scheduler runs the game's async code; 5 continuations were posted in the whole fight, the rest ran inline.

## What is not done, and what the numbers do not show yet

- **Speed is not measured properly.** One cold pass of the fight (45 events) took 1.4–1.6 s. That includes first-time compilation of every game method touched, logging, and a machine with a load average near 30 from unrelated work. A warm second pass in the same process failed at clean-up (`RunManager.CleanUp` needs a save profile), so the per-fight time once warm is still unknown. The millisecond target is neither confirmed nor refuted.
- **Start-up is slow: about 30 s**, almost all of it replacing the 3,871 UI methods one at a time. It must come down (patch lazily, or prepare a stripped assembly once).
- **31 of the 57 recorded checkpoints were not compared**: the ones the game takes after each action ("finished action execution …"). The host does not produce them, so the game's own id-by-id check reports divergence 25 times. The 26 turn-boundary states that were compared are exact, and each later one depends on every action before it.
- **One fight is not a fidelity suite.** Other cards, relics, monsters and events will reach display code not yet stubbed; each new failure is a small stub, found by replaying more recorded fights (P7.E3.S2, P7.E5).
- **No reset between fights** (FI-11), no decision mode, no sampler, no Python bridge: Phase 7 epics E3–E6.
- **Each stub's neutrality is argued, not proven**, beyond this fight's exact match. Text lookups returning empty strings would break any rule that reads text; none was hit here.

## Notes for the next stories

- `ModelDb.Init(null)` uses the game's own type list; an empty array loads nothing, and the replay reader then misreads the file (the model-id hash check catches it).
- Replays are already anonymised when written (`CombatReplay.Anonymized`), and each checkpoint stores the full state next to its hash; the anonymised player id differs per process, so states are compared with the id masked.
- Harmony cannot patch `NativeFuncs` wrappers (function-pointer bodies); it works on ordinary game methods.
- One UI namespace is spelled `MegaCrit.sts2.Core.Nodes.TopBar` (lower-case "sts2").
- Reproduce: `STS2_DATA_DIR=<game data folder> dotnet build sim -c Release` with the .NET 9 SDK, then `sim/run.sh replay <file.mcr> [trace] [once]`. Lists the host needs: `data/asm/ui-types-from-logic.json` and `data/asm/testpath-methods.json` (built from the call graph; not in git).
