# Runbook: The Decision Loop (P4.E1.S2–S4)

The same loop for every decision. The interface is `tools/sts.py` (`--mod sts2agent` is the first choice since decision 0001 was revised; STS2MCP is the fallback). Field names follow the mods' documentation and must be confirmed in Phase 0.

## The loop
1. **Read** `python3 -I tools/sts.py state` (brief view). Use `--raw` only when a field you need is missing.
2. **Classify** the screen (`state_type`). Resolve overlays first (`hand_select`, `card_select`, `relic_select`, `bundle_select`, `overlay`).
3. **Load** only the playbook section the screen needs (section numbers in `playbooks/ironclad.md`). Use the current boss plan and the encounter note for fights.
4. **Advise, then decide.** With STS2-Agent, save the state (`tools/sts.py --mod sts2agent state --raw > runs/<run>/state.json`) and run `python3 -I tools/advise.py --state runs/<run>/state.json`. It routes to the turn planner, path planner, draft scorer, rest rule, event table or shop scoring. Follow it unless you can name a reason it misses (a relic, a synergy, a boss mechanic), and put that reason in the decision log. Big decisions (rare cards, relics, elite paths, boss turns) get explicit reasoning in the journal. Routine ones stay short.
5. **Act** with a one-sentence reason: `python3 -I tools/sts.py --log runs/<run>/decisions.jsonl act <action> key=value ... --reason "..."`. Add `--tool-pick "<action key=value ...>"` with what `advise.py` recommended, so the post-mortem can count overrides; when you override, the reason says why.
6. **Verify** the state moved as expected (`state`, or `wait` across animations). If not, use the error table below.
7. **On every new floor:** update the journal (floor log line; HP and budget; plan changes):
   - `python3 -I tools/journal.py status runs/<run> --from-state <saved state.json>` (or `--floor --act --hp --max-hp --gold --potions`)
   - `python3 -I tools/journal.py floor runs/<run> --floor <f> --room <type> --result "..." --hp-change <n> --note "<decision and reason>"`
   - Plan changes are written by hand in the plan sections.

Use only actions the state offers. Recompute every index from the latest state. **In combat, hand indexes shift after each card played:** play from the highest index down, or re-read state between plays.

## Screen handlers (STS2MCP state types)
| Screen | Steps | Playbook |
|---|---|---|
| `map` | At act start: read `map.boss`, plan the path (journal): `python3 -I tools/path.py --state <state.json>` ranks every route by expected loot against fatal risk; re-run after any big HP change. Then `choose_map_node index=<next_options index>` | §4, §10 |
| `monster` / `elite` / `boss` | Combat checklist (§9). At the start of each turn (and after any draw), save the state and run `python3 -I tools/plan_turn.py --state <state.json>`; compare the safe and balanced plans with the HP budget and the encounter note before playing. `play_card card_index=<i> target=<entity_id>`, `use_potion slot=<n> target=...`, `end_turn`. After `end_turn`, read state again; it may need two reads to reach your next turn. | §9, encounter note |
| `hand_select` | `combat_select_card card_index=<i>` (repeat), then `combat_confirm_selection` | §9 |
| `rewards` | Claim from the highest index down: `claim_reward index=<i>`. A card reward opens `card_reward`. `proceed` when done | §2, §8 |
| `card_reward` | Procedure §2.1. Score the offer first: `python3 -I tools/draft.py --deck <ids> --offer <names> --act <a> --floor <f> --boss <id>` (or `--from-state <state.json>` on STS2-Agent). Override it only with a stated reason (a relic, a synergy the tool cannot see). Then `select_card_reward card_index=<i>` or `skip_card_reward` | §2 |
| `rest_site` | §5 thresholds: `choose_rest_option index=<i>`, resolve any card selection, then `proceed` | §5 |
| `shop` | §6 priority: `shop_purchase index=<i>` (repeat), then `proceed` | §6 |
| `event` | Read options and their risk (`events.json`): `choose_event_option index=<i>`. Ancients: `advance_dialogue` until options show | §7 |
| `treasure` | `claim_treasure_relic index=<i>`, then `proceed` | §7 |
| `card_select` | `select_card index=<i>`, then `confirm_selection` (grid) or immediate (choose-a-card) | §2.3, §6 |
| `relic_select` | `select_relic index=<i>` or `skip_relic_selection` | §7 |
| `crystal_sphere` | `crystal_sphere_set_tool`, `crystal_sphere_click_cell x= y=`, `crystal_sphere_proceed` | none |
| `game_over` | Run end procedure (`docs/runbooks/end-run.md`), then `menu_select option=main_menu` | none |
| `overlay` / `unknown` | Read raw state; try `proceed` or `menu_select` options shown. If stuck after two tries, tell the Player | none |

## Error recovery
| Error or symptom | Response |
|---|---|
| `status: error` with a message (STS2MCP), or `invalid_action` / `invalid_target` (STS2-Agent) | Read the message; re-read state; fix the index or target. Never repeat the same call blindly. |
| STS2-Agent `action_in_flight` (409) | Wait for the previous response, re-read state, retry once. |
| STS2-Agent `pending` | `tools/sts.py wait`, then re-read. |
| The state did not change after an action | `wait`, then re-read; look for an overlay or a dialogue (`advance_dialogue`). |
| Combat `is_play_phase: false` | Enemy turn in progress: `wait`. |
| `cannot reach` (mod down) | Tell the Player. Once the game is relaunched, continue the run from the menu (`continue`) and resume from the journal. |
| Context was summarized mid-run | Read the project instructions, then the run journal, then state. Continue the plan in the journal. |
| `advise.py` prints `[ADVICE FAILED] ...` | The state had a shape the advisor did not expect. Keep the saved state (`runs/<run>/state.json` under a new name), decide by the playbook section for the screen, and add the line to the post-mortem's problems so the tool gets a fix and a fixture. |
| A warning line in combat advice (Sandpit, Steam Eruption, Withering Presence) or a `note:` line about a card | Read it before acting: Sandpit at 1 at the end of a turn kills you; Waterfall Giant explodes for its Steam Eruption the turn after its stun; a card marked not modelled needs your own arithmetic. |

## Logging
- Every action is logged in `runs/<run>/decisions.jsonl`: time, screen, floor, action, parameters, reason, result.
- Every fight gets a line in the journal's fight log: `python3 -I tools/journal.py fight runs/<run> --floor <f> --encounter <id or name> --turns <t> --damage <d> --potions a,b`. It adds the band-matched benchmark median and warns above the p75 or when the encounter changed on v0.111.1.
- Before an elite or boss: `python3 -I tools/journal.py budget --encounter <id> --ascension <n>` for the expected HP cost.
