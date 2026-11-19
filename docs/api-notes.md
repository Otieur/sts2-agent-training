# Mod API Notes

Two candidate mods. "Documented behaviour" comes from the vendor docs and source (read 2026-11-19). "Observed behaviour" is filled in during the Phase 0 smoke tests, and wins wherever the two differ.

---

## STS2-Agent (vendor/STS2-Agent, commit 5d7c306)

Full reference: `vendor/STS2-Agent/docs/api.md` (about 2,000 lines) and the machine-readable `vendor/STS2-Agent/docs/openapi.json`.

### Documented behaviour
- **Address:** `http://127.0.0.1:8080`. The port increments if busy, unless `STS2_API_PORT` is set explicitly. JSON only, compact on the wire.
- **Response envelope:**
  - Success: `{"ok": true, "request_id": ..., "data": {...}}`
  - Failure: `{"ok": false, "request_id": ..., "error": {"code", "message", "details", "retryable"}}`
- **Endpoints:**
  - `GET /health`
  - `GET /state`: full state; the compact form is in `agent_view`
  - `GET /actions/available`
  - `POST /action`
  - `GET /decisions`: decision log, including each action's `client_context.decision_reason`
  - `GET /events/stream`: server-sent events with heartbeats every 15 s and a 256-entry queue per client
  - `GET /data/{collection}`: game metadata export
  - `POST /session/control`: loopback only
  - `POST /teammate/control`: main window only
  - `POST /companion/control` and `POST /companion/message`: teammate instance, need a session token
  - `POST /mcp`: native MCP, off by default
- **Action call:** `POST /action {"action": "<name>", ...params, "client_context": {"decision_reason": "..."}}`. Parameters by action:
  - `card_index` and an optional `target_index`: `play_card`
  - `option_index`: `choose_map_node`, `claim_reward`, `choose_reward_card`, `select_deck_card`, `choose_treasure_relic`, `choose_event_option`, `choose_rest_option` (plus `target_index` for co-op options), `buy_card`, `buy_relic`, `buy_potion`, `select_character`, `use_potion`, `discard_potion`, `choose_bundle`, `choose_capstone_option`, `choose_timeline_epoch`
  - No parameters: `end_turn`, `proceed`, `continue_run`, `continue_game_over`, `abandon_run`, `save_and_quit`, `open_chest`, `confirm_selection`, `confirm_modal`, `dismiss_modal`, `embark`, `unready`, `invite_ai_teammate`, `continue_ai_teammate`
  - About 70 actions in total
- **Action `status` in the response:**
  - `completed`: the returned state has settled
  - `pending`: still in transition; read state again
  - `failed`: never treat as success
- **Error codes and the correct response:**

  | Code | HTTP | Retryable | Response |
  |---|---|---|---|
  | `invalid_request` | 400 | no | Fix the request body |
  | `invalid_action` | 409 | no | Not available in this state; re-read `/state` and `available_actions` |
  | `invalid_target` | 409 | no | Index out of range; recompute from fresh state |
  | `action_in_flight` | 409 | after waiting | Not executed or queued. Wait for the previous response, re-read, retry once |
  | `state_unavailable` | 503 | yes | Transition in progress; wait and retry |
  | `forbidden_actor` | 403 | no | Co-op: acting for another player; check `player_id` and target |
  | `session_not_ready` | 409 | yes | Team setup not finished |
  | `pause_pending` | 409 | yes | Retry shortly |
  | `companion_not_ready` | 409 | yes | Teammate not ready |
  | `not_host` | 409 | no | `/teammate/control` sent to the teammate instead of the main window |
  | `invite_failed` / `continue_failed` | 409 | yes / depends | AI teammate flows; see api.md |
  | `local_only` | 403 | no | Request must come from loopback |
  | `collection_not_found` | 404 | no | Wrong `/data` collection name |
  | `internal_error` / `listener_error` | 500 | no / yes | Check `/health` before retrying |
- **Screens** (`session`/screen enum): `MAIN_MENU`, `CHARACTER_SELECT`, `MULTIPLAYER_LOBBY`, `MULTIPLAYER_LOAD`, `BUNDLE_SELECTION`, `CAPSTONE_SELECTION`, `PAUSE_MENU`, `SETTINGS`, `COMPENDIUM`, `RELIC_COLLECTION`, `POTION_LAB`, `BESTIARY`, `STATS`, `RUN_HISTORY`, `MAP`, `COMBAT`, `EVENT`, `CRYSTAL_SPHERE`, `SHOP`, `REST`, `REWARD`, `CHEST`, `CARD_SELECTION`, `CARDS_VIEW`, `CARD_LIBRARY`, `CARD_PILE`, `MODAL`, `GAME_OVER`, `UNLOCK`, `TIMELINE`, `FAKE_MERCHANT`, `PATCH_NOTES`, `CARD_INSPECT`, `RELIC_INSPECT`, `FEEDBACK`, `UNKNOWN`.
  - When a human pauses, room actions disappear until the pause menu closes.
- **Key `/state` fields for play:**
  - `combat.action_readiness`: whether actions can be sent now, and why not
  - `combat.lethal_risks[]`, `end_turn_will_kill_player`
  - `combat.hand[]` with `dynamic_values[]` (the actual current numbers)
  - `combat.enemies[].intents[]` (damage, hits, total)
  - `combat.player.powers[]`
  - `run.deck[]`, `run.relics[]`, `run.potions[]`, `run.ascension_effects[]`
  - `map.available_nodes[]`, `map.nodes[]`, `map.player_votes[]`
  - `reward.card_options[]`, `shop.*`, `rest.options[]`, `event.options[]`
- **Co-op specifics:**
  - Each instance acts only for its own character.
  - On the map, wait once `map.local_vote` is set.
  - Never use the game's Load button for a co-op save; use `continue_ai_teammate`.
- **Debug:** `run_console_command` and `inject_event_churn` need `STS2_ENABLE_DEBUG_ACTIONS=1`. Do not set it.

### Observed behaviour
(Filled in during Phase 0 E5.)

---

## Observed live (STS2-Agent 0.16.2 on v0.111.1, 2026-11-19) `[OBS]`
- **First action** (13:35 EST): `play_card` Tremble on a Fogmog returned `status: completed`; `GET /decisions` showed the `decision_reason`.
- **First full fight** (14:10 EST, A10 floor 22, Bowlbug Rock and Egg, won in 2 turns, 60 to 61 HP with Burning Blood): 9 actions, no stuck state. Sequence: `play_card` Brand+ (returned `status: pending`, `stable: false`, after 1.34 s, and opened a `CARD_SELECTION` screen, `combat_hand_select`), `select_deck_card option_index=0` (exhaust Ascender's Bane), five more `play_card`, `end_turn`, `play_card` for lethal. Each call returned in about 1 to 1.5 s; the other actions returned `completed`, `stable: true`. Per-action median and p95 (request to settled state) were not measured precisely; the next fight should time them.
- **Waits:** right after `end_turn` the next turn's state came back with a partial hand and `available_actions` without `play_card` for about 2 s while cards were drawn. Wait until `play_card` is in `available_actions` (or `combat.action_readiness.can_use_combat_actions` is true) before planning the turn.
- **A card that asks for a choice** (Brand's "Exhaust 1 card") switches the screen to `CARD_SELECTION` with `selection.kind = combat_hand_select`; answer with `select_deck_card option_index=<n>` (indexes of the hand, in order).
- **Live card values** (`dynamic_values`) include the player's own Strength (Strike 6 to 8 at 2 Strength) but not the target's Vulnerable (Strike stayed 6 against a Vulnerable enemy). Gap 22 answered.
- **After a fight** the state keeps the last `combat` object (dead enemies) on the map and reward screens; route by `screen`, not by the presence of `combat`.
- **Event stream** (`GET /events/stream`, a 4-minute capture while the Player played two fights by hand, `knowledge/api-samples/events-human-play.txt`): **does any event identify the card the human played? No.** The 269 events were `available_actions_changed` (130), `player_action_window_opened` and `_closed` (44 each; one close and open per card played), `screen_changed` (32), `combat_turn_changed` (6, with `from` and `to`), `route_decision_required` (5), `reward_decision_required`, `combat_started`, `combat_ended` (2 each), `session_started`, `stream_ready`. So Phase 3 reconstructs the Player's plays from state differences (`tools/smoke.py --trace`), and `player_action_window_opened` is a good signal that the state has settled and can be read.
- **Quitting the game** drops the connection mid-request (`RemoteDisconnected`); `tools/sts.py` reports it as a `ModError` and says when an action may or may not have been applied.

## STS2MCP (vendor/STS2MCP, commit 55e0648)

### Documented behaviour
- **Address:** `http://localhost:15526/` (port set in the mod's config file).
- **Routes** (`McpMod.cs:194-256`):
  - `/`: health
  - `/api/v1/singleplayer`: `GET` returns state, `POST` sends an action
  - `/api/v1/multiplayer`: the same for multiplayer runs
  - `/api/v1/profile`, `/api/v1/compendium`, `/api/v1/wiki?query=...`
  - `/api/v1/profiles`: `GET` lists, `POST` switches or deletes. **Never call delete.**
- **Actions:** `play_card`, `end_turn`, `undo_end_turn`, `use_potion`, `discard_potion`, `choose_map_node`, `claim_reward`, `select_card_reward`, `skip_card_reward`, `choose_event_option`, `advance_dialogue`, `choose_rest_option`, `shop_purchase`, `claim_treasure_relic`, `select_relic`, `skip_relic_selection`, `select_card`, `confirm_selection`, `cancel_selection`, `combat_select_card`, `combat_confirm_selection`, `select_bundle`, `confirm_bundle_selection`, `cancel_bundle_selection`, `crystal_sphere_set_tool`, `crystal_sphere_click_cell`, `crystal_sphere_proceed`, `proceed`. Also menu and lobby actions: `singleplayer`, `multiplayer`, `standard`, `daily`, `custom`, `continue`, `abandon_run`, `host`, `join`, `load`, `timeline`, `compendium`, `settings`, `quit`.
- **State formats:** `vendor/STS2MCP/docs/raw-full.md` and `raw-simplified.md`. `/api/v1/singleplayer?format=json` returns JSON.
- **Map boss:** exposed in map state (commit `3154670`), so the act boss can be read at act start.
- **MCP server:** `vendor/STS2MCP/mcp/server.py`, run with `uv run --directory <path> python server.py`. Tools include `get_game_state`, `get_profile`, `get_compendium`, `search_wiki`, `list_profiles`, `switch_profile`, `delete_profile`. Do not expose `delete_profile` to the agent.

### Observed behaviour
(Filled in during Phase 0 E5 if STS2MCP is used.)

## Co-op harness (tools/sts.py), from the STS2-Agent docs (2026-11-19, untested live)
- Teammate discovery: the host window's `GET /health` returns `data.companion` (`api_host`, `api_port`, `process_id`, `auto_play`) once the teammate is connected; `null` otherwise. The teammate's port is usually not 8080 (examples in the mod's validation log: 8081, 18081, 18082).
- `data.instance_role` is `human` on the Player's window and `companion` on the teammate. `sts.py --instance teammate act` checks it before every action.
- Routing: `session.mode` (`singleplayer` / `multiplayer`) is the documented basis; `multiplayer.is_multiplayer` is the fallback. `sts.py` refuses to act on a multiplayer run unless `--instance teammate` is used.
- Both instances simulate the whole run (lockstep), so `run.players[]` (deck, relics, potions) and `combat.players[]` (HP, block, energy) are fresh on either. Only the local hand is exposed: the Player's hand needs the host's `/state` (`sts.py --instance host state`, read-only).
- `target_index` for ally-targeting cards and potions uses the position in `combat.players[]` / `run.players[]`, not `player_id`.
- `sts.py party` compares floor, run_id, enemy HP and player HP between the two instances and prints any mismatch (P6.E5 desync check).

## Field facts from the STS2-Agent source (read-only, 2026-11-19)
- **`run.act_id` is 0-based** (`CurrentActIndex.ToString()`): "0" is Act 1. The mod's live-validation log shows `act_id: "0"` with Vantom and `act_id=1` at floor 17 before The Insatiable. All tools convert with `stslib.act_number()`; `tools/mcp_adapter.py` emits the same 0-based value for STS2MCP (whose `run.act` is 1-based).
- **`run.boss_id`** is the current act's boss encounter id entry (`Act.BossEncounter.Id.Entry`, for example `VANTOM_BOSS`), so the boss is known from the first floor of each act.
- **Card `dynamic_values[].current_value`** is the game's normal card preview against `card.CurrentTarget`: your own modifiers included, the target's only while targeting.
- **Intent `damage` / `total_damage`** come from the game's `GetSingleDamage` / `GetTotalDamage` against the players: they already include the enemy's Strength and Weak and your Vulnerable.
- **Map `node_type`** is the game's `PointType.ToString()` (PascalCase names such as `RestSite`).
