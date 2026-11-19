#!/usr/bin/env python3
"""Shadowing with call-it-first (P3.E2, P3.E3): watch the Player's game read-only, log the Agent's call at every
decision before the Player acts, then fill in the Player's actual pick from the next state and mark agreement.

Calls (runs/shadow-<NN>/calls.jsonl), one JSON line each:
  card_reward  agent_pick = card id or SKIP (tools/draft.py); player_pick from the deck change
  map          agent_pick = node "row,col" (tools/path.py); player_pick from the next map position
  rest         agent_pick = HEAL or SMITH (playbook rest rule, "other" case); player_pick from HP or upgrades
  combat       on turn 1 of elites and bosses, incoming damage >= 30% of HP, or possible lethal (P3.E3.S1):
               the safe plan's plays, expected HP lost and damage (tools/plan_turn.py); actual HP lost filled in
               at the next player turn (combat-calls.jsonl)
Other screens are logged with options only. Nothing is ever sent to the game.

Usage: python3 -I tools/shadow.py --out runs/shadow-01 [--mod sts2agent|sts2mcp] [--port N] [--minutes 240]
UNTESTED AGAINST THE LIVE GAME.
"""
import argparse
import collections
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import advise  # noqa: E402
import draft  # noqa: E402
import mcp_adapter  # noqa: E402
import plan_turn  # noqa: E402
import sts  # noqa: E402


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def norm_state(st):
    st = st.get("data", st) if isinstance(st, dict) and "ok" in st else st
    return mcp_adapter.mcp_to_agent(st) if mcp_adapter.is_mcp(st) else st


def deck_counter(st):
    return collections.Counter(d.get("card_id") for d in (st.get("run") or {}).get("deck") or [] if d.get("card_id"))


def upgraded_count(st):
    return sum(1 for d in (st.get("run") or {}).get("deck") or [] if d.get("upgraded"))


def screen_key(st):
    """Identity of a decision screen, so each one is called once."""
    run = st.get("run") or {}
    return (st.get("screen"), run.get("floor"), st.get("turn"), json.dumps(sorted((st.get("available_actions") or [])))[:80])


def make_call(st):
    """The Agent's call for this screen, or None when the screen is not a decision worth logging."""
    scr = (st.get("screen") or "").upper()
    run = st.get("run") or {}
    base = {"ts": now(), "floor": run.get("floor"), "screen": scr}
    if scr == "REWARD" and (st.get("reward") or {}).get("card_options"):
        deck, offer, act, floor, boss = draft.from_state_obj(st)
        res = draft.score_offer(deck, offer, advise._character(st), act or 1, floor, boss)
        rows = res["rows"]
        margin = (rows[0]["score"] - max(rows[1]["score"] if len(rows) > 1 else -9, res["skip_bar"])) if rows else 0
        pick = res["pick"]["id"] if res["pick"] else "SKIP"
        return {**base, "kind": "card_reward", "options": [o.split(".", 1)[-1] for o in offer], "agent_pick": pick,
                "confidence": "high" if margin >= 1 else ("medium" if margin >= 0.5 else "low"),
                "reason": "; ".join(res["pick"]["reasons"][:3]) if res["pick"] else "nothing beats the skip bar",
                "rule": "playbook 2.1 (tools/draft.py)"}
    if scr == "MAP" and (st.get("map") or {}).get("nodes"):
        import path as pathmod
        m = st["map"]
        nodes, start, boss_rc = pathmod.load_map(m)
        paths = pathmod.enumerate_paths(nodes, start, boss_rc)
        if not paths:
            return None
        act = advise._act(st)
        model = pathmod.get_model(advise._character(st), int(run.get("ascension") or 0))
        res = pathmod.rank(paths, nodes, model, act, run.get("current_hp"), run.get("max_hp"), run.get("boss_id"),
                           pathmod.DEFAULT_RISK_WEIGHT.get(act, 16.0))
        first = res[0]["first"]
        return {**base, "kind": "map", "options": [f"{n.get('row')},{n.get('col')}" for n in m.get("available_nodes") or []],
                "agent_pick": f"{first[0]},{first[1]}", "confidence": "n/a", "reason": f"best route {res[0]['seq']}",
                "rule": "playbook 4 (tools/path.py)"}
    if scr == "REST":
        cases = advise.rest_rule(run.get("current_hp"), run.get("max_hp"), advise._act(st), int(run.get("ascension") or 0),
                                 run.get("boss_id"), advise._character(st), "other")
        choice, why = cases["other"]
        return {**base, "kind": "rest", "options": [o.get("option_id") for o in (st.get("rest") or {}).get("options") or []],
                "agent_pick": "HEAL" if choice == "rest" else ("SMITH" if choice == "smith" else "EITHER"), "confidence": "n/a",
                "reason": why, "rule": "playbook 5"}
    if scr in ("EVENT", "SHOP", "CARD_SELECTION", "CHEST"):
        lines = advise.advise(st).splitlines()  # once: advice can be slow
        return {**base, "kind": scr.lower(), "options": None, "agent_pick": None, "confidence": "n/a",
                "reason": lines[1] if len(lines) > 1 else (lines[0] if lines else ""), "rule": None}
    return None


def combat_call(st):
    """P3.E3.S1 trigger policy and the full-turn call."""
    c = st.get("combat") or {}
    if not c or "play_card" not in (st.get("available_actions") or ["play_card"]):
        return None
    hand, player, enemies = plan_turn.from_state(st)
    if not enemies:
        return None
    ft = advise.fight_type(st)
    incoming = sum(e.intent_per_hit * e.intent_hits for e in enemies)
    res = plan_turn.plans(hand, player, enemies)
    if not res:
        return None
    best = plan_turn.rank(res, "balanced" if ft == "boss" else "safe")[0]
    trigger = None
    if st.get("turn") == 1 and ft in ("elite", "boss"):
        trigger = f"turn 1 of {ft} fight"
    elif player.hp and incoming >= 0.3 * player.hp:
        trigger = f"incoming {incoming} >= 30% of {player.hp} HP"
    elif best["all_dead"]:
        trigger = "lethal available"
    if not trigger:
        return None
    return {"ts": now(), "floor": (st.get("run") or {}).get("floor"), "turn": st.get("turn"), "kind": "combat", "trigger": trigger,
            "plays": best["plays"], "expected_hp_lost": best["hp_lost"], "expected_dealt": best["dealt"], "hp_before": player.hp}


def resolve(call, before, after):
    """Fill in the Player's pick from the state change."""
    k = call.get("kind")
    if k == "card_reward":
        added = deck_counter(after) - deck_counter(before)
        new = [cid for cid in added if cid in call["options"]]
        call["player_pick"] = new[0] if new else ("SKIP" if (after.get("run") or {}).get("deck") is not None else None)
    elif k == "map":
        cur = (after.get("map") or {}).get("current_node") or {}
        call["player_pick"] = f"{cur.get('row')},{cur.get('col')}" if cur else None
    elif k == "rest":
        hb, ha = (before.get("run") or {}).get("current_hp"), (after.get("run") or {}).get("current_hp")
        if ha is not None and hb is not None and ha > hb:
            call["player_pick"] = "HEAL"
        elif upgraded_count(after) > upgraded_count(before):
            call["player_pick"] = "SMITH"
        else:
            call["player_pick"] = "OTHER"
    if call.get("agent_pick") is not None and call.get("player_pick") is not None:
        call["agree"] = call["agent_pick"] == call["player_pick"] or call["agent_pick"] == "EITHER"
    return call


def shadow(adapter, out_dir, interval=1.0, max_seconds=4 * 3600, clock=time.time, sleep=time.sleep, max_states=None):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    calls_f, combat_f = out / "calls.jsonl", out / "combat-calls.jsonl"
    pending, pending_combat, seen = None, None, set()
    prev = None
    n = 0
    deadline = clock() + max_seconds
    while clock() < deadline:
        try:
            st = norm_state(adapter.state())
        except sts.ModError:
            sleep(interval * 3)
            continue
        n += 1
        key = screen_key(st)
        if prev is not None and key != screen_key(prev):
            if pending:  # the Player acted on the previous screen
                with open(calls_f, "a") as f:
                    f.write(json.dumps(resolve(pending, pending["_state"], st) | {"_state": None}, default=str) + "\n")
                pending = None
            if pending_combat and (st.get("combat") or {}) and st.get("turn") != pending_combat["turn"]:
                hp = ((st.get("combat") or {}).get("player") or {}).get("current_hp")
                if hp is not None and pending_combat.get("hp_before") is not None:
                    pending_combat["actual_hp_lost"] = pending_combat["hp_before"] - hp
                with open(combat_f, "a") as f:
                    f.write(json.dumps(pending_combat) + "\n")
                pending_combat = None
        if key not in seen:
            seen.add(key)
            try:  # one decision the tools cannot handle must not end a long shadowing session
                call = make_call(st)
                if call:
                    call["_state"] = st
                    pending = call
                if (st.get("screen") or "").upper() == "COMBAT":
                    cc = combat_call(st)
                    if cc:
                        pending_combat = cc
            except Exception as e:  # noqa: BLE001
                with open(calls_f, "a") as f:
                    f.write(json.dumps({"screen": st.get("screen"), "error": f"{type(e).__name__}: {e}",
                                        "floor": (st.get("run") or {}).get("floor")}) + "\n")
        prev = st
        if max_states and n >= max_states:
            break
        sleep(interval)
    for f, item in ((calls_f, pending), (combat_f, pending_combat)):
        if item:
            item.pop("_state", None)
            with open(f, "a") as fh:
                fh.write(json.dumps(item, default=str) + "\n")
    return n


def summary(out_dir):
    rows = [json.loads(x) for x in (Path(out_dir) / "calls.jsonl").read_text().splitlines()] if (Path(out_dir) / "calls.jsonl").exists() else []
    by = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        if r.get("agree") is not None:
            by[r["kind"]][0] += int(r["agree"])
            by[r["kind"]][1] += 1
    return {k: f"{a}/{n} agree" for k, (a, n) in by.items()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mod", choices=["sts2agent", "sts2mcp"], default="sts2agent")
    ap.add_argument("--port", type=int)
    ap.add_argument("--minutes", type=float, default=240)
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--summary", action="store_true", help="print agreement from an existing calls.jsonl and exit")
    args = ap.parse_args(argv)
    if args.summary:
        print(summary(args.out))
        return 0
    adapter = sts.Sts2AgentAdapter(args.port or 8080) if args.mod == "sts2agent" else sts.Sts2McpAdapter(args.port or 15526)
    n = shadow(adapter, args.out, args.interval, args.minutes * 60)
    print(f"{n} states read; agreement: {summary(args.out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
