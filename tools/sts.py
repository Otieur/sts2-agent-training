#!/usr/bin/env python3
"""Command-line interface to the game through a state-export mod (P0.E6.S1).

UNTESTED AGAINST THE LIVE GAME (written 2026-11-19 from the mods' documentation and source). Phase 0 smoke
tests (P0.E5) must confirm field names and behaviour; fix this file where reality differs.

Two adapters, chosen with --mod:
  sts2mcp   (default) STS2MCP, http://localhost:15526, GET/POST /api/v1/singleplayer (or /multiplayer with --mp)
  sts2agent STS2-Agent, http://127.0.0.1:8080, GET /state, POST /action, GET /health

Commands:
  health                         is the mod answering?
  state [--brief | --raw]        current screen (brief = compact text for decisions)
  act <action> [key=value ...] --reason "..."   send one action; the reason is mandatory and logged
  wait [--timeout 20]            poll until the screen settles (combat play phase, or a new screen)

Safety: profile deletion and debug/console actions are refused. Every action is appended to a decision log
(--log, default runs/current/decisions.jsonl) because STS2MCP keeps no decision log of its own.

Standard library only. Run with python3 -I.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
BLOCKED_ACTIONS = {"run_console_command", "inject_event_churn", "delete", "delete_profile", "switch_profile"}
LOCAL_HOSTS = ("127.0.0.1", "localhost")


class ModError(Exception):
    pass


def _http(method, url, body=None, timeout=10, opener=None):
    host = url.split("/")[2].split(":")[0]
    if host not in LOCAL_HOSTS:
        raise ModError(f"refusing non-local address {url}")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with (opener or urllib.request.urlopen)(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise ModError(f"HTTP {e.code}: {raw[:200]}")
    except urllib.error.URLError as e:
        raise ModError(f"cannot reach {url}: {e.reason}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_text": raw}


class Sts2McpAdapter:
    name = "sts2mcp"

    def __init__(self, port=15526, multiplayer=False, opener=None):
        self.base = f"http://localhost:{port}"
        self.path = "/api/v1/multiplayer" if multiplayer else "/api/v1/singleplayer"
        self.opener = opener

    def health(self):
        return _http("GET", self.base + "/", opener=self.opener)

    def state(self):
        return _http("GET", f"{self.base}{self.path}?format=json", opener=self.opener)

    def act(self, action, params, reason):
        body = {"action": action, **params}
        resp = _http("POST", self.base + self.path, body, opener=self.opener)
        ok = resp.get("status") == "ok"
        return ok, resp

    @staticmethod
    def screen(state):
        return state.get("state_type", "?")


class Sts2AgentAdapter:
    name = "sts2agent"

    def __init__(self, port=8080, opener=None):
        self.base = f"http://127.0.0.1:{port}"
        self.opener = opener

    def health(self):
        return _http("GET", self.base + "/health", opener=self.opener)

    def state(self):
        resp = _http("GET", self.base + "/state", opener=self.opener)
        return resp.get("data", resp)

    def act(self, action, params, reason):
        body = {"action": action, **params, "client_context": {"decision_reason": reason}}
        resp = _http("POST", self.base + "/action", body, opener=self.opener)
        ok = bool(resp.get("ok")) and (resp.get("data") or {}).get("status") != "failed"
        return ok, resp

    @staticmethod
    def screen(state):
        return (state.get("session") or {}).get("screen") or state.get("screen") or "?"


# ---------------------------------------------------------------------------------------------- brief views
def _powers(lst):
    return ", ".join(f"{p.get('name') or p.get('id')} {p.get('amount')}" for p in (lst or [])) or "-"


def _player_line(p):
    if not p:
        return ""
    s = f"HP {p.get('hp')}/{p.get('max_hp')}  block {p.get('block', 0)}  gold {p.get('gold')}"
    if "energy" in p:
        s += f"  energy {p.get('energy')}/{p.get('max_energy')}"
    if p.get("stars") is not None:
        s += f"  stars {p.get('stars')}"
    return s + f"\nYou: {_powers(p.get('status'))}"


def brief_sts2mcp(st):
    t = st.get("state_type", "?")
    run = st.get("run") or {}
    p = st.get("player") or {}
    out = [f"[{t}] act {run.get('act', '-')} floor {run.get('floor', '-')} A{run.get('ascension', '-')}"]
    if p:
        out.append(_player_line(p))
        pots = p.get("potions") or []
        out.append("Potions: " + (", ".join(f"[{x.get('slot')}] {x.get('name')} ({x.get('target_type')})" for x in pots) or "none")
                   + f"  (slots {len(pots)}/{p.get('max_potion_slots', '?')})")
    if t in ("monster", "elite", "boss"):
        b = st.get("battle") or {}
        out.append(f"Round {b.get('round')} turn {b.get('turn')} play_phase={b.get('is_play_phase')}")
        for e in b.get("enemies") or []:
            intents = "; ".join(f"{i.get('type')} {i.get('label', '')}".strip() for i in e.get("intents") or [])
            out.append(f"  {e.get('entity_id')}: {e.get('name')} HP {e.get('hp')}/{e.get('max_hp')} block {e.get('block', 0)} "
                       f"| {intents or '-'} | {_powers(e.get('status'))}")
        out.append("Hand:")
        for c in p.get("hand") or []:
            flag = "" if c.get("can_play", True) else f" (cannot: {c.get('unplayable_reason')})"
            up = "+" if c.get("is_upgraded") else ""
            out.append(f"  [{c.get('index')}] {c.get('name')}{up} ({c.get('cost')}) {c.get('target_type')}: {c.get('description')}{flag}")
        out.append(f"Piles: draw {p.get('draw_pile_count')} discard {p.get('discard_pile_count')} exhaust {p.get('exhaust_pile_count')}")
    elif t == "card_reward":
        cr = st.get("card_reward") or {}
        for c in cr.get("cards") or []:
            out.append(f"  [{c.get('index')}] {c.get('name')}{'+' if c.get('is_upgraded') else ''} ({c.get('cost')}, {c.get('type')}, {c.get('rarity')}): {c.get('description')}")
        out.append(f"can_skip={cr.get('can_skip')}")
    elif t == "rewards":
        r = st.get("rewards") or {}
        for it in r.get("items") or []:
            out.append(f"  [{it.get('index')}] {it.get('type')}: {it.get('description')}")
        out.append(f"can_proceed={r.get('can_proceed')}")
    elif t == "map":
        m = st.get("map") or {}
        boss = m.get("boss") or {}
        out.append(f"Boss: {boss.get('name', '?')} ({boss.get('id', '?')})" + (f"; all bosses {[x.get('name') for x in m.get('bosses')]}" if len(m.get("bosses") or []) > 1 else ""))
        cur = m.get("current_position") or {}
        out.append(f"At row {cur.get('row')} ({cur.get('type')})")
        for o in m.get("next_options") or []:
            nxt = ", ".join(x.get("type", "?") for x in o.get("leads_to") or [])
            out.append(f"  [{o.get('index')}] {o.get('type')} (col {o.get('col')}, row {o.get('row')}) -> {nxt}")
    elif t == "rest_site":
        for o in (st.get("rest_site") or {}).get("options") or []:
            out.append(f"  [{o.get('index')}] {o.get('name')}: {o.get('description')}{'' if o.get('is_enabled', True) else ' (disabled)'}")
    elif t in ("shop", "fake_merchant"):
        for it in (st.get(t) or {}).get("items") or []:
            name = it.get("card_name") or it.get("relic_name") or it.get("potion_name") or it.get("category")
            desc = it.get("card_description") or it.get("relic_description") or it.get("potion_description") or ""
            flags = ("" if it.get("is_stocked", True) else " sold") + ("" if it.get("can_afford", True) else " (can't afford)")
            out.append(f"  [{it.get('index')}] {it.get('category')} {name} {it.get('price')}g{flags}: {desc[:90]}")
    elif t == "event":
        ev = st.get("event") or {}
        out.append(f"Event: {ev.get('name') or ev.get('id', '?')} in_dialogue={ev.get('in_dialogue')}")
        for o in ev.get("options") or []:
            lock = " (locked)" if o.get("is_locked") else ""
            out.append(f"  [{o.get('index')}] {o.get('title') or o.get('name')}: {o.get('description', '')}{lock}")
    elif t in ("card_select", "hand_select", "relic_select", "bundle_select", "treasure"):
        block = st.get(t) or {}
        for key in ("cards", "relics", "bundles", "items"):
            for x in block.get(key) or []:
                out.append(f"  [{x.get('index')}] {x.get('name') or x.get('id')}: {x.get('description', '')}")
        prompt = block.get("prompt") or block.get("title")
        if prompt:
            out.append(f"Prompt: {prompt}")
    elif t in ("menu", "game_over"):
        out.append("Options: " + ", ".join(map(str, st.get("options") or [])))
    else:
        out.append(json.dumps({k: v for k, v in st.items() if k not in ("player", "run")})[:1500])
    return "\n".join(x for x in out if x)


def brief_sts2agent(st):
    view = st.get("agent_view") or st
    return json.dumps(view, separators=(",", ":"))[:6000]


# ----------------------------------------------------------------------------------------------------- CLI
def parse_params(pairs):
    params = {}
    for kv in pairs:
        if "=" not in kv:
            raise SystemExit(f"parameter must be key=value: {kv}")
        k, v = kv.split("=", 1)
        try:
            params[k] = int(v)
        except ValueError:
            params[k] = v
    return params


def log_decision(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def make_adapter(args, opener=None):
    if args.mod == "sts2agent":
        return Sts2AgentAdapter(args.port or 8080, opener=opener)
    return Sts2McpAdapter(args.port or 15526, multiplayer=args.mp, opener=opener)


def main(argv=None, opener=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mod", choices=["sts2mcp", "sts2agent"], default="sts2mcp")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--mp", action="store_true", help="STS2MCP multiplayer endpoint")
    ap.add_argument("--log", default=str(PROJECT / "runs/current/decisions.jsonl"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("health")
    s = sub.add_parser("state")
    s.add_argument("--raw", action="store_true")
    a = sub.add_parser("act")
    a.add_argument("action")
    a.add_argument("params", nargs="*")
    a.add_argument("--reason", required=True)
    w = sub.add_parser("wait")
    w.add_argument("--timeout", type=float, default=20)
    args = ap.parse_args(argv)
    adapter = make_adapter(args, opener)
    brief = brief_sts2agent if adapter.name == "sts2agent" else brief_sts2mcp
    try:
        if args.cmd == "health":
            print(json.dumps(adapter.health()))
        elif args.cmd == "state":
            st = adapter.state()
            print(json.dumps(st, indent=1) if args.raw else brief(st))
        elif args.cmd == "act":
            if args.action in BLOCKED_ACTIONS:
                raise SystemExit(f"refused: '{args.action}' is blocked by project rules (see docs/reviews/)")
            params = parse_params(args.params)
            before = adapter.state()
            ok, resp = adapter.act(args.action, params, args.reason)
            log_decision(args.log, {
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "mod": adapter.name,
                "screen": adapter.screen(before), "floor": (before.get("run") or {}).get("floor"),
                "action": args.action, "params": params, "reason": args.reason, "ok": ok,
                "message": resp.get("message") or (resp.get("error") or {}).get("code"),
            })
            print(("OK " if ok else "FAILED ") + json.dumps(resp)[:800])
            if not ok:
                sys.exit(2)
        elif args.cmd == "wait":
            deadline = time.time() + args.timeout
            first = adapter.screen(adapter.state())
            while time.time() < deadline:
                st = adapter.state()
                scr = adapter.screen(st)
                battle = st.get("battle") or {}
                if scr != first or battle.get("is_play_phase") is True:
                    print(brief(st))
                    return
                time.sleep(0.5)
            print("timeout; last screen: " + adapter.screen(adapter.state()))
            sys.exit(3)
    except ModError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
