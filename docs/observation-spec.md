# Observation Specification (P7.E6.S5)

What a policy sees at a combat decision point. One format for live play and for the simulator (`docs/simulator-integrity.md` ML-1): the simulator host (`sim/Session.cs`, `Observe`) emits the same field names and values as the live API's state (STS2-Agent), so `tools/plan_turn.py from_state` reads both. Everything here is visible to a player (FP-1); the right-hand column says where each value comes from in the engine.

Version 1, 2026-11-20. Tested on the simulator side only (`tools/sim.py smoke`, `fairplay`, `planner`); the field-by-field comparison with live fixtures is P7.E5.S3.

| Field | Meaning | Engine source |
|---|---|---|
| `status` | `in_progress`, `won`, `lost` | `CombatManager.IsInProgress`, player creature dead |
| `turn` | Player turn number | `PlayerCombatState.TurnNumber` |
| `run.ascension`, `run.max_hp`, `run.current_hp` | Run facts | `RunState.AscensionLevel`, player creature |
| `run.relics[].relic_id` | Relics | `Player.Relics[].Id.Entry` |
| `run.potions[]` (`index`, `occupied`, `potion_id`) | Potion slots | `Player.PotionSlots` |
| `combat.player` (`current_hp`, `max_hp`, `block`, `energy`, `powers[]`) | The player | player creature, `PlayerCombatState.Energy`, `Creature.Powers` (`power_id` = `Id.Entry`, `amount`) |
| `combat.hand[]` (`index`, `card_id`, `upgraded`, `target_type`, `energy_cost`, `playable`, `dynamic_values[]`) | Cards in hand, in hand order | `EnergyCost.GetWithModifiers(All)`, `CanPlay()`, and for values a clone of the card's variables after `UpdateDynamicVarPreview(Normal, CurrentTarget)`: the same call the live mod makes, so values include the player's Strength, Weak and Frail |
| `combat.enemies[]` (`index`, `enemy_id`, `current_hp`, `max_hp`, `block`, `is_alive`, `is_hittable`, `powers[]`, `intents[]`) | Enemies in slot order | `CombatState.Enemies` |
| `intents[]` (`intent_type`, and for attacks `damage`, `hits`, `total_damage`) | The shown intent of the next move | `Monster.NextMove.Intents`; `AttackIntent.GetSingleDamage`, `Repeats`, `GetTotalDamage` |
| `combat.draw_pile`, `discard_pile`, `exhaust_pile` and their `_count` | Pile contents as sorted id lists (`+` marks an upgrade) | pile cards, **sorted**: the draw order is never exposed |
| `choice` (`kind`, `min`, `max`, `options[]`) | A pending card choice, or null | the intercepted card-selection command (`sim/Choices.cs`) |
| `waiting_for_choice`, `blocked` | A choice is pending; or an action is stuck on a prompt the host does not handle | host state |

**Deliberately absent:** `move_id` (it can name a move whose intent is hidden, FP-7), the run seed, any random-generator state, the draw order, future intents.

**Actions** (`legal` lists them; `step` applies one): `{"type":"play","card":i[,"target":j]}`, `{"type":"potion","slot":k[,"target":j]}`, `{"type":"end_turn"}`, `{"type":"choose","cards":[...]}`. The host supports potions; the planner rollouts and the search candidates (`tools/sim.py`) do not use them yet (2026-11-20), because a fight value without a price on spent potions would spend every potion.

**Known differences from the live API, to close in P7.E5.S3:** `enemies[].name` is the id (no localised text in the host); the live state has more fields (`action_readiness`, `lethal_risks`, card text) that no tool reads for decisions.
