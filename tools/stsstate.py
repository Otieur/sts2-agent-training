"""Shared helpers for live-state tools (watch.py, record.py, reconstruct.py). Both mods' state formats: STS2MCP
(`state_type`) and STS2-Agent (`screen`) are reduced to the same compact snapshot.

UNTESTED AGAINST THE LIVE GAME: field names follow vendor/STS2MCP/docs/raw-full.md and vendor/STS2-Agent/docs/api.md.
"""
import hashlib
import json
import re

DECISION_SCREENS = {"card_reward", "map", "rest_site", "shop", "fake_merchant", "event", "treasure", "relic_select",
                    "card_select", "bundle_select", "rewards"}
COMBAT_SCREENS = {"monster", "elite", "boss", "combat"}
AGENT_SCREENS = {"COMBAT": "combat", "MAP": "map", "REST": "rest_site", "SHOP": "shop", "FAKE_MERCHANT": "fake_merchant",
                 "EVENT": "event", "CHEST": "treasure", "CARD_SELECTION": "card_select", "BUNDLE_SELECTION": "bundle_select",
                 "GAME_OVER": "game_over", "MAIN_MENU": "menu"}


def compact(st):
    """Reduce a full state to what the recorder and reconstruction need."""
    st = st.get("data", st) if isinstance(st, dict) and "ok" in st else st
    if "state_type" not in st and "screen" in st:
        return compact_agent(st)
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


def compact_agent(st):
    """STS2-Agent full /state -> the same compact snapshot as compact() builds for STS2MCP."""
    run, c = st.get("run") or {}, st.get("combat") or {}
    p = c.get("player") or {}
    scr = (st.get("screen") or "?").upper()
    if scr == "REWARD":
        screen = "card_reward" if (st.get("reward") or {}).get("card_options") else "rewards"
    else:
        screen = AGENT_SCREENS.get(scr, scr.lower())
    boss = (run.get("boss_id") or "").upper().replace("_BOSS", "").replace("ENCOUNTER.", "")
    enemies = c.get("enemies") or []
    fight = None
    if c:
        fight = "boss" if boss and any(boss in str(e.get("enemy_id") or "").upper() for e in enemies) else "unknown"

    def label(i):
        if i.get("damage") is None:
            return i.get("intent_type")
        return f"{i['damage']}x{i.get('hits') or 1}" if (i.get("hits") or 1) > 1 else str(i["damage"])
    acts = st.get("available_actions") or []
    from stslib import act_number
    act = act_number(run.get("act_id"), default=None) if run.get("act_id") is not None else None
    return {
        "screen": screen, "fight": fight, "act": act, "floor": run.get("floor"),
        "hp": p.get("current_hp", run.get("current_hp")), "max_hp": p.get("max_hp", run.get("max_hp")),
        "block": p.get("block"), "gold": run.get("gold"), "energy": p.get("energy"),
        "hand": [{"id": h.get("card_id"), "name": h.get("name"), "cost": h.get("energy_cost"), "up": bool(h.get("upgraded"))}
                 for h in c.get("hand") or []],
        "piles": [len(c.get(k) or []) if isinstance(c.get(k), list) else None for k in ("draw", "discard", "exhaust")],
        "potions": [x.get("potion_id") for x in run.get("potions") or [] if x.get("occupied")],
        "status": {(s.get("power_id") or s.get("name")): s.get("amount", s.get("stacks")) for s in p.get("powers") or []},
        "round": st.get("turn"), "turn": "player" if c else None,
        "play_phase": ("play_card" in acts or "end_turn" in acts) if c else None,
        "enemies": [{"id": e.get("index"), "hp": e.get("current_hp"), "block": e.get("block"),
                     "status": {(s.get("power_id") or s.get("name")): s.get("amount", s.get("stacks")) for s in e.get("powers") or []},
                     "intents": [label(i) for i in e.get("intents") or []]}
                    for e in enemies if e.get("is_alive", True)],
        "options": _agent_options(st, screen),
    }


def _agent_options(st, screen):
    if screen == "card_reward":
        return [c.get("card_id") for c in (st.get("reward") or {}).get("card_options") or []]
    if screen == "map":
        return [o.get("node_type") for o in (st.get("map") or {}).get("available_nodes") or []]
    if screen == "rest_site":
        return [o.get("option_id") for o in (st.get("rest") or {}).get("options") or []]
    if screen == "shop":
        sh = st.get("shop") or {}
        return [x.get("card_id") or x.get("name") for k in ("cards", "relics", "potions") for x in sh.get(k) or [] if x.get("is_stocked", True)]
    if screen == "event":
        return [o.get("title") for o in (st.get("event") or {}).get("options") or []]
    return None


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
        kind = c.get("fight") or scr
        if kind in ("elite", "boss") and c.get("round") == 1:
            return f"turn 1 of {kind} fight"
        hp = c.get("hp") or 0
        inc = incoming_damage(c)
        if hp and inc >= flagged_combat_ratio * hp:
            return f"high incoming damage ({inc} against {hp} HP)"
    return None
