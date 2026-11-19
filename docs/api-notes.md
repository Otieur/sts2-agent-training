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
