# Runbook: The First Live Session (Phase 0 smoke test and in-game checks)

Written 2026-11-19 (overnight) so the first session with the mod running is short and complete. It covers P0.E5 (API smoke test) and the in-game checks the offline tools depend on. Every check names the file to update when the game differs.

## Before (the Player)
1. Steam: switch Slay the Spire 2 to the main branch (v0.111.1) and let it update.
2. Approve the security review (`docs/reviews/sts2-agent-security-review.md`) and the .NET 9 SDK install, or choose the STS2MCP fallback (`docs/decisions/0001-mod-and-branch.md`).
3. Fresh save backup (`docs/runbooks/restore-saves.md`), then build and install the mod (`docs/runbooks/mod-install.md`).
4. Launch the game, accept the mod dialog, relaunch.

## Step 1: Smoke test (read-only, about 15 minutes)
```bash
python3 -I tools/smoke.py --save --watch --minutes 30
```
With the STS2MCP fallback, add `--mod sts2mcp` (it checks the raw fields `tools/mcp_adapter.py` converts; there is no `/health` version check). While it runs, click through: main menu, start a standard Ironclad run at A0, the Ancient, the map, the first fight (play a few cards), the card reward, and any rest site, shop or event on the way. The tool:
- checks `/health`: service name, `game_version` v0.111.x, `status` ready (a `degraded` status lists the missing members);
- checks every state field the tools read, per screen, and runs `tools/advise.py` on each screen;
- lists card IDs that are not in the extract (new cards since it was made);
- saves one fixture per screen under `tools/tests/fixtures/live/`.

**Pass:** no PROBLEM lines. **Fix:** a missing field means the field names in `tools/plan_turn.py` (`from_state`), `tools/path.py` (`load_map`), `tools/draft.py` (`from_state_obj`) or `tools/advise.py` differ from the live format. Fix the reader and add the saved fixture to a test. Commit the fixtures.

Then run the full test suite: `python3 -I -m unittest discover -s tools/tests`.

## Step 2: One action through the API (P0.E5.S2)
In the first fight, with a decision reason:
```bash
python3 -I tools/sts.py --mod sts2agent --log runs/smoke/decisions.jsonl act play_card card_index=0 target_index=0 --reason "Smoke test: play the first card"
```
Check: the card is played, `runs/smoke/decisions.jsonl` has the line, and `GET /decisions` on the mod shows the reason.

## Step 3: Arithmetic checks (first fights; the Agent reads the numbers from the state)
| # | Check | How | Expected | If different, update |
|---|---|---|---|---|
| 1 | Vulnerable ×1.5, floor | Strike on a Vulnerable enemy, 0 Strength | 9 | `tools/calc.py` constants, `knowledge/mechanics.md` |
| 2 | Rounding | Twin Strike on a Vulnerable enemy | 7 per hit | `tools/calc.py` `hit_damage` |
| 3 | Weak on enemy intent | An intent of 10 while the enemy is Weak | 7 | `tools/calc.py`, `plan_turn.py` intent handling |
| 4 | Strength before multipliers | Strike, 2 Strength, Vulnerable target | 12 | `tools/calc.py` order |
| 5 | Frail | Defend while Frail | 3 | `tools/calc.py` `block_gain` |
| 6 | Block before HP | 10 damage into 6 block | lose 4 | — |
| 7 | **Live values include your modifiers** (gap 22) | With Strength 2, read a Strike's `dynamic_values` Damage; then target a Vulnerable enemy | 8, still 8 (Vulnerable not included) | `plan_turn.py` `per_hit` (live branch) |
| 8 | **Intent numbers include your Vulnerable and the enemy's Weak?** (the mod's source says yes: `GetSingleDamage` against the players) | Read an intent before and after you become Vulnerable, and after you Weaken the enemy | Both change the shown number | `plan_turn.py` `simulate` (existing Weak is not applied again) |
| 9 | **Potion damage is flat** (gap 24) | Fire Potion on a Vulnerable enemy | 20 | `plan_turn.py` `POTIONS` (`flat`) |
| 10 | Burning Blood | After a won fight | +6 HP | `path.py` assumes it is in the history's net HP |
| 11 | Rest heal | Rest at a site | floor(30% of max) | `path.py` `REST_HEAL`, playbook section 5 |

## Step 4: Mechanics to confirm when met (record in the encounter note, then close the gap)
| Gap | What to look at | Note to update |
|---|---|---|
| 4 | Vantom's Slippery stacks on turn 1 (expected 9) | `knowledge/bosses/VANTOM_BOSS.md` |
| 5 | The boss shows on the map at act start (`run.boss_id`, `map.boss_node`) | `knowledge/gaps.md` |
| 7 | Seeded start: does standard mode accept a seed? Do 10-character v0.107.1 exam seeds work on v0.111.1? | `metrics/exam-seeds.md` |
| 12 | Lagavulin Matriarch wakes stunned when hit; which power goes with Asleep. Kin Priest's death ends the fight? | boss notes |
| 13 | `run.ascension_effects` lists the ascension rules | `knowledge/ascension.md` |
| 23 | Kaiser Crab facing: target each claw and read the intent numbers (×1.5 from behind?) | `knowledge/bosses/KAISER_CRAB_BOSS.md` |
| — | Infested Prism's current moves and Tainted duration (reworked after the extract) | `knowledge/enemies/INFESTED_PRISMS_ELITE.md` |
| — | Test Subject's Enrage: every card or only Skills? | `knowledge/bosses/TEST_SUBJECT_BOSS.md` |
| — | Does the combat state say whether the fight is a hallway, elite or boss room? (`tools/advise.py` `fight_type` guesses from the boss name, else assumes elite) | `tools/advise.py` |

## Step 5: Live data export (P2.E1.S2)
STS2-Agent serves `/data/{collection}`. Export cards, monsters, relics, potions and powers for v0.111.1 into `knowledge/data/v0.111.1/` and compare them with the extract plus `knowledge/data/card-patches.json`. Every difference not in the two delta files is a new entry for the delta files and the patches.

## After
- Update `docs/environment.md` (the "To confirm" list), `docs/STATUS.md` and `knowledge/gaps.md` (move closed gaps to Resolved with the date and evidence).
- Commit: fixtures, fixes, notes.
