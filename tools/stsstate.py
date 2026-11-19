"""Shared helpers for live-state tools (watch.py, record.py, reconstruct.py). STS2MCP state format.

UNTESTED AGAINST THE LIVE GAME: field names follow vendor/STS2MCP/docs/raw-full.md.
"""
import hashlib
import json
import re

DECISION_SCREENS = {"card_reward", "map", "rest_site", "shop", "fake_merchant", "event", "treasure", "relic_select",
                    "card_select", "bundle_select", "rewards"}
COMBAT_SCREENS = {"monster", "elite", "boss"}


def compact(st):
    """Reduce a full state to what the recorder and reconstruction need."""
    p = st.get("player") or {}
    b = st.get("battle") or {}
    run = st.get("run") or {}
    return {
        "screen": st.get("state_type"),
        "act": run.get("act"), "floor": run.get("floor"),
        "hp": p.get("hp"), "max_hp": p.get("max_hp"), "block": p.get("block"), "gold": p.get("gold"),
        "energy": p.get("energy"),
        "hand": [{"id": c.get("id"), "name": c.get("name"), "cost": c.get("cost"), "up": bool(c.get("is_upgraded"))}
                 for c in p.get("hand") or []],
        "piles": [p.get("draw_pile_count"), p.get("discard_pile_count"), p.get("exhaust_pile_count")],
        "potions": [x.get("id") or x.get("name") for x in p.get("potions") or []],
        "status": {s.get("id") or s.get("name"): s.get("amount") for s in p.get("status") or []},
        "round": b.get("round"), "turn": b.get("turn"), "play_phase": b.get("is_play_phase"),
        "enemies": [{"id": e.get("entity_id"), "hp": e.get("hp"), "block": e.get("block"),
                     "status": {s.get("id") or s.get("name"): s.get("amount") for s in e.get("status") or []},
                     "intents": [i.get("label") for i in e.get("intents") or []]}
                    for e in b.get("enemies") or []],
        "options": _options(st),
    }


def _options(st):
    t = st.get("state_type")
    if t == "card_reward":
        return [c.get("id") for c in (st.get("card_reward") or {}).get("cards") or []]
    if t == "map":
        return [o.get("type") for o in (st.get("map") or {}).get("next_options") or []]
    if t == "rest_site":
        return [o.get("id") or o.get("name") for o in (st.get("rest_site") or {}).get("options") or []]
    if t in ("shop", "fake_merchant"):
        return [i.get("card_id") or i.get("relic_id") or i.get("potion_id") for i in (st.get(t) or {}).get("items") or []
                if i.get("is_stocked", True)]
    if t == "event":
        return [o.get("title") or o.get("name") for o in (st.get("event") or {}).get("options") or []]
    return None


def fingerprint(c):
    return hashlib.sha1(json.dumps(c, sort_keys=True).encode()).hexdigest()[:16]


def parse_intent_damage(label):
    """'11' -> 11; '6x2' or '6 x 2' -> 12; non-numeric -> 0."""
    if label is None:
        return 0
    s = str(label).replace("×", "x")
    m = re.match(r"\s*(\d+)\s*(?:x\s*(\d+))?", s)
    if not m:
        return 0
    return int(m.group(1)) * (int(m.group(2)) if m.group(2) else 1)


def incoming_damage(c):
    return sum(parse_intent_damage(lbl) for e in c.get("enemies") or [] for lbl in e.get("intents") or [])


def decision_point(c, flagged_combat_ratio=0.3):
    """Return a short reason string if this compact state is a decision point worth waking the Agent for."""
    scr = c.get("screen")
    if scr in DECISION_SCREENS:
        return f"decision screen: {scr}"
    if scr in COMBAT_SCREENS and c.get("play_phase") and c.get("turn") == "player":
        if scr in ("elite", "boss") and c.get("round") == 1:
            return f"turn 1 of {scr} fight"
        hp = c.get("hp") or 0
        inc = incoming_damage(c)
        if hp and inc >= flagged_combat_ratio * hp:
            return f"high incoming damage ({inc} against {hp} HP)"
    return None
