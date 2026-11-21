# Proposal: search in real runs (P8.E5)

Status: proposal, 2026-11-20. Next major step toward Ascension 10 once the current learning round ends.

## Why
On the benchmark, wide Monte Carlo search (`mcw6`) wins 80% of fights at Ascension 8+ against 58% for the rule planner, and it nearly matches the Player's own results on the same fights (86%). But search runs only inside the simulator; real runs are still played with the rule planner. The real-run ladder (one win at A0, one loss at A1) cannot move toward A10 until search plays real fights.

## The idea
Rebuild the live fight exactly in the simulator at every decision, then search from it with the hidden future re-sampled (fair play, FP-15).

- **Start of the fight:** the game saves the run when a room is entered (`current_run.save` in the Agent's own profile, `modded/profile2`; read-only, copied into the sandbox). The save holds the run state at room entry, including the random-generator state, so entering the room from it reproduces the real fight's set-up.
- **Everything since:** the Agent's own action log (`decisions.jsonl` from `tools/sts.py`: card plays with targets, potion uses, card choices, ends of turn) replayed in order.
- **Check:** after rebuilding, the host's visible state is compared field by field with the live observation (hand, piles, HP, block, energy, powers, enemy HP, block, powers and intents). Any mismatch stops search for that decision and falls back to the rule planner, and is logged.
- **Search:** the rebuilt state is sanitized (hidden draw order and future rolls re-sampled) and `mcw6` chooses the move; the move goes to the game through the mod with its one-sentence reason.

The exact part is already shown: the fidelity suite replays recorded fights from their start state and actions with every state equal to the game's (11 of 11). What is new is the source of the start state (the save rather than a recording) and of the actions (our log rather than the recording's events).

## Stories
1. **Save reader** (host): `load_save` builds the run from a copied `current_run.save` and enters the current room; test: a save captured at room entry, rebuilt, matches the first live observation of that fight. Needs one save captured during an Agent run on profile 2.
2. **Action log replay**: map `decisions.jsonl` entries to host actions (indexes, targets, choices, potions); test: on the Agent's two recorded runs, rebuilding every fight from the replay's start state plus our log matches the recording at every turn boundary.
3. **Live comparator**: field-by-field comparison with the live state, with a list of fields the live API lacks (pile contents need the pile view); mismatches logged with the first differing field.
4. **Autopilot loop**: `tools/play_turn.py --auto` (P8.E5.S2): rebuild, compare, search, act, log; escalations as written in P8.E5.S2.
5. **Latency** (P8.E5.S3): rebuild time (room entry plus replayed actions) and search time per decision; target median 3 s with `mcw6`, lower with the action-value candidate filter.
6. **Validation** (P8.E6): first in practice runs on profile 2, then the scored ladder after the Player's sign-off (P8.E5.S5).

## Risks
- The save may be written at a different moment than room entry; then story 1 needs the previous room's save plus the room transition.
- Actions the log does not capture (automatic card selections, timing-dependent prompts) break exactness; the comparator catches them and the planner covers that decision.
- Real runs must follow the scored-run rules (no reloads); the save is only read, never restored into the game.
