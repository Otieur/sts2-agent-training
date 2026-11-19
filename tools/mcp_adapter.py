#!/usr/bin/env python3
"""Convert an STS2MCP state (`state_type` format, vendor/STS2MCP/docs/raw-full.md) into the STS2-Agent shape that
tools/advise.py, plan_turn.py, path.py, draft.py and deck_check.py read, so every helper works with either mod.

STS2MCP gives no deck list outside combat. The deck is rebuilt from the combat piles (hand + draw + discard +
exhaust) and cached (runs/current/deck.json by default); card rewards and shops, which follow fights, read the cache.
Live card numbers come from the card text ("Deal 9 damage." -> Damage 9), like STS2-Agent's dynamic_values.

UNTESTED AGAINST THE LIVE GAME: field names follow the STS2MCP documentation.
"""
import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DEFAULT_CACHE = PROJECT / "runs" / "current" / "deck.json"
SCREEN = {"monster": "COMBAT", "elite": "COMBAT", "boss": "COMBAT", "hand_select": "COMBAT", "map": "MAP",
          "card_reward": "REWARD", "rewards": "REWARD", "rest_site": "REST", "shop": "SHOP", "fake_merchant": "SHOP",
          "event": "EVENT", "card_select": "CARD_SELECTION", "treasure": "CHEST", "menu": "MAIN_MENU", "game_over": "GAME_OVER"}


def is_mcp(st):
    return isinstance(st, dict) and "state_type" in st


def _cost(c):
    v = str(c.get("cost", ""))
    return (None, True) if v.upper() == "X" else ((int(v) if v.lstrip("-").isdigit() else None), False)


def _live_values(desc):
    vals = []
    m = re.search(r"Deal (\d+) damage", desc or "")
    if m:
        vals.append({"name": "Damage", "current_value": int(m.group(1))})
    m = re.search(r"Gain (\d+) Block", desc or "")
    if m:
        vals.append({"name": "Block", "current_value": int(m.group(1))})
    return vals


def _powers(lst):
    return [{"power_id": (s.get("id") or s.get("name") or "").upper(), "amount": s.get("amount")} for s in lst or []]


def _intents(e):
    out = []
    for i in e.get("intents") or []:
        lbl = str(i.get("label") or "").replace("×", "x")
        m = re.match(r"\s*(\d+)\s*(?:x\s*(\d+))?", lbl) if (i.get("type") or "").lower().startswith("attack") else None
        if m:
            d, h = int(m.group(1)), int(m.group(2) or 1)
            out.append({"intent_type": "Attack", "label": lbl, "damage": d, "hits": h, "total_damage": d * h})
        else:
            out.append({"intent_type": i.get("type"), "label": lbl, "damage": None, "hits": None})
    return out


def _deck_from_piles(p):
    deck = []
    for key in ("hand", "draw_pile", "discard_pile", "exhaust_pile"):
        for c in p.get(key) or []:
            if c.get("id"):
                deck.append({"card_id": c["id"], "upgraded": bool(c.get("is_upgraded"))})
    return deck


def mcp_to_agent(st, deck_cache=DEFAULT_CACHE):
    """STS2MCP state -> STS2-Agent-shaped dict (the `data` part)."""
    t = st.get("state_type", "?")
    p, run_in = st.get("player") or {}, st.get("run") or {}
    out = {"screen": SCREEN.get(t, t.upper()), "turn": (st.get("battle") or {}).get("round"), "room_type": t,
           "available_actions": [], "_source": "sts2mcp"}
    deck = _deck_from_piles(p) if p.get("draw_pile") is not None or p.get("discard_pile") is not None else None
    cache = Path(deck_cache) if deck_cache else None
    if deck and cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(deck))
    elif cache and cache.exists():
        try:
            deck = json.loads(cache.read_text())
        except ValueError:
            deck = None
    boss = ((st.get("map") or {}).get("boss") or {}).get("id")
    out["run"] = {"floor": run_in.get("floor"), "act_id": str(run_in.get("act")) if run_in.get("act") is not None else None,
                  "ascension": run_in.get("ascension"), "current_hp": p.get("hp"), "max_hp": p.get("max_hp"),
                  "gold": p.get("gold"), "boss_id": (boss or "").replace("ENCOUNTER.", "") or None, "deck": deck or [],
                  "potions": [{"index": x.get("slot", i), "potion_id": x.get("id"), "name": x.get("name"), "occupied": True}
                              for i, x in enumerate(p.get("potions") or [])]}
    if t in ("monster", "elite", "boss", "hand_select"):
        b = st.get("battle") or {}
        hand = []
        for i, c in enumerate(p.get("hand") or []):
            cost, x = _cost(c)
            hand.append({"index": c.get("index", i), "card_id": c.get("id"), "name": c.get("name"), "energy_cost": cost or 0,
                         "costs_x": x, "upgraded": bool(c.get("is_upgraded")), "playable": c.get("can_play", True),
                         "target_type": c.get("target_type"), "dynamic_values": _live_values(c.get("description"))})
        out["combat"] = {
            "player": {"current_hp": p.get("hp"), "max_hp": p.get("max_hp"), "block": p.get("block", 0), "energy": p.get("energy"),
                       "powers": _powers(p.get("status")),
                       "pets": [{"pet_id": (x.get("id") or "").upper(), "current_hp": x.get("hp") if x.get("alive", True) else 0,
                                 "max_hp": x.get("max_hp"), "block": x.get("block")} for x in p.get("pets") or []]},
            "hand": hand,
            "enemies": [{"index": e.get("entity_id", i), "enemy_id": re.sub(r"_\d+$", "", str(e.get("entity_id") or "")),
                         "name": e.get("name"), "current_hp": e.get("hp"), "max_hp": e.get("max_hp"), "block": e.get("block", 0),
                         "is_alive": (e.get("hp") or 0) > 0, "powers": _powers(e.get("status")), "intents": _intents(e)}
                        for i, e in enumerate(b.get("enemies") or [])],
            "end_turn_will_kill_player": False}
        if b.get("is_play_phase"):
            out["available_actions"] = ["play_card", "end_turn"]
    elif t == "map":
        m = st.get("map") or {}
        out["map"] = {
            "nodes": [{"row": n.get("row"), "col": n.get("col"), "node_type": n.get("type"),
                       "children": [{"col": ch[0], "row": ch[1]} for ch in n.get("children") or []]} for n in m.get("nodes") or []],
            "current_node": {"row": (m.get("current_position") or {}).get("row"), "col": (m.get("current_position") or {}).get("col")}
            if m.get("current_position") else None,
            "boss_node": {"row": (m.get("boss") or {}).get("row"), "col": (m.get("boss") or {}).get("col")} if m.get("boss") else None,
            "available_nodes": [{"index": o.get("index"), "row": o.get("row"), "col": o.get("col"), "node_type": o.get("type")}
                                for o in m.get("next_options") or []]}
    elif t == "card_reward":
        out["reward"] = {"card_options": [{"index": c.get("index"), "card_id": c.get("id"), "name": c.get("name")}
                                          for c in (st.get("card_reward") or {}).get("cards") or []]}
    elif t == "rewards":
        out["reward"] = {"rewards": [{"index": r.get("index"), "reward_type": str(r.get("type") or "").replace("_", " ").title().replace(" ", ""),
                                      "description": r.get("description")} for r in (st.get("rewards") or {}).get("items") or []]}
    elif t == "rest_site":
        out["rest"] = {"options": [{"index": o.get("index"), "option_id": (o.get("id") or o.get("name") or "").upper()}
                                   for o in (st.get("rest_site") or {}).get("options") or []]}
    elif t in ("shop", "fake_merchant"):
        items = (st.get(t) or {}).get("items") or []
        def ok(i):
            return i.get("is_stocked", True) and i.get("can_afford", True)
        out["shop"] = {
            "cards": [{"index": i.get("index"), "card_id": i.get("card_id"), "price": i.get("price"), "is_stocked": i.get("is_stocked", True),
                       "enough_gold": ok(i)} for i in items if i.get("card_id")],
            "relics": [{"index": i.get("index"), "name": i.get("relic_name"), "price": i.get("price"), "is_stocked": i.get("is_stocked", True),
                        "enough_gold": ok(i), "description": i.get("relic_description")} for i in items if i.get("relic_id") or i.get("relic_name")],
            "potions": [{"index": i.get("index"), "name": i.get("potion_name"), "price": i.get("price"), "is_stocked": i.get("is_stocked", True)}
                        for i in items if i.get("potion_id") or i.get("potion_name")],
            "card_removal": next(({"price": i.get("price"), "available": i.get("is_stocked", True), "enough_gold": ok(i)}
                                  for i in items if (i.get("category") or "").lower() in ("card_removal", "removal")), None)}
    elif t == "event":
        ev = st.get("event") or {}
        eid = str(ev.get("id") or ev.get("name") or "").upper().replace("EVENT.", "")
        out["event"] = {"event_id": eid, "title": ev.get("name"),
                        "options": [{"index": o.get("index"), "title": o.get("title") or o.get("name"), "description": o.get("description"),
                                     "is_locked": o.get("is_locked", False),
                                     "text_key": o.get("text_key") or f"{eid}.pages.INITIAL.options.{str(o.get('title') or '').upper().replace(' ', '_')}"}
                                    for o in ev.get("options") or []]}
    elif t == "card_select":
        cs = st.get("card_select") or {}
        out["selection"] = {"kind": cs.get("mode") or "deck_card_select", "prompt": cs.get("prompt") or cs.get("title"),
                            "cards": [{"index": c.get("index"), "card_id": c.get("id"), "name": c.get("name"), "upgraded": bool(c.get("is_upgraded"))}
                                      for c in cs.get("cards") or []]}
    return out
