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
  party                          co-op: one view of both players (HP, block, energy, both hands), the enemies,
                                 and a consistency check between the host's and the teammate's state

Instances (co-op, Phase 6, P6.E3.S1/S2), chosen with --instance:
  solo      (default) the single game window
  host      the Player's window. Read-only: act is refused, the Agent never acts for the Player.
  teammate  the Agent's own window. STS2-Agent: the port is read from the host's /health
            (data.companion.api_port) unless --port is given, and act checks that the instance reports
            instance_role=companion. STS2MCP: --port is required.
  --host-port sets the host window's port (default 8080 for STS2-Agent, 15526 for STS2MCP).

Safety: profile deletion and debug/console actions are refused. Acting on a multiplayer run is refused unless
--instance teammate is used, so a co-op action can never land on the Player's character. Every action is
appended to a decision log (--log, default runs/current/decisions.jsonl) because STS2MCP keeps no decision log of
its own.

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

    def health_data(self):
        h = self.health()
        return h.get("data", h) if isinstance(h, dict) else {}

    @staticmethod
    def screen(state):
        return state.get("screen") or (state.get("session") or {}).get("screen") or "?"

    @staticmethod
    def is_multiplayer(state):
        return (state.get("session") or {}).get("mode") == "multiplayer" or bool((state.get("multiplayer") or {}).get("is_multiplayer"))


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


def _a_powers(lst):
    return ", ".join(f"{p.get('name') or p.get('power_id') or p.get('id')} {p.get('amount', p.get('stacks', ''))}".strip()
                     for p in (lst or [])) or "-"


def _a_intents(e):
    out = []
    for i in e.get("intents") or []:
        kind = i.get("intent_type") or "?"
        if i.get("damage") is not None:
            hits = i.get("hits") or 1
            out.append(f"{kind} {i.get('damage')}" + (f"x{hits}" if hits > 1 else "") + f" (={i.get('total_damage')})")
        else:
            out.append(f"{kind} {i.get('label') or ''}".strip())
    return "; ".join(out) or (e.get("move_id") or "-")


def _a_player_rows(players, local_label="you", other_label="teammate"):
    rows = []
    for p in players or []:
        who = local_label if p.get("is_local") else other_label
        dead = "" if p.get("is_alive", True) else " DEAD"
        conn = "" if p.get("is_connected", True) else " (disconnected)"
        rows.append(f"  [{p.get('slot_index')}] {p.get('character_name') or p.get('character_id')} ({who}) "
                    f"HP {p.get('current_hp')}/{p.get('max_hp')} block {p.get('block', 0)} energy {p.get('energy', '-')}{dead}{conn}")
    return rows


def _a_hand(hand):
    rows = []
    for c in hand or []:
        cost = "X" if c.get("costs_x") else c.get("energy_cost")
        flag = "" if c.get("playable", True) else f" (cannot: {c.get('unplayable_reason')})"
        tgt = f" targets {c.get('valid_target_indices')}" if c.get("requires_target") else ""
        text = c.get("resolved_rules_text") or c.get("rules_text") or ""
        rows.append(f"  [{c.get('index')}] {c.get('name')}{'+' if c.get('upgraded') else ''} ({cost}){tgt}: {text}{flag}")
    return rows


def brief_sts2agent(st):
    """Compact text view of a full STS2-Agent /state (fields per vendor/STS2-Agent/docs/api.md)."""
    scr = Sts2AgentAdapter.screen(st)
    run = st.get("run") or {}
    sess = st.get("session") or {}
    mode = "co-op" if Sts2AgentAdapter.is_multiplayer(st) else "solo"
    out = [f"[{scr}] {mode} floor {run.get('floor', '-')} A{run.get('ascension', '-')} turn {st.get('turn') or '-'}"]
    if run:
        pots = [x.get("name") for x in run.get("potions") or [] if x.get("occupied")]
        out.append(f"HP {run.get('current_hp')}/{run.get('max_hp')} gold {run.get('gold')} potions: {', '.join(pots) or 'none'}")
    c = st.get("combat")
    if c:
        p = c.get("player") or {}
        out.append(f"You: HP {p.get('current_hp')}/{p.get('max_hp')} block {p.get('block', 0)} energy {p.get('energy')}"
                   f"{' stars ' + str(p.get('stars')) if p.get('stars') else ''} | {_a_powers(p.get('powers'))}")
        if len(c.get("players") or []) > 1:
            out.append("Party:")
            out.extend(_a_player_rows(c.get("players")))
        out.append("Enemies:")
        for e in c.get("enemies") or []:
            if not e.get("is_alive", True):
                continue
            out.append(f"  [{e.get('index')}] {e.get('name')} HP {e.get('current_hp')}/{e.get('max_hp')} block {e.get('block', 0)} "
                       f"| {_a_intents(e)} | {_a_powers(e.get('powers'))}")
        out.append("Hand:")
        out.extend(_a_hand(c.get("hand")))
        if c.get("end_turn_will_kill_player"):
            out.append("WARNING: ending the turn now is lethal: " + "; ".join(
                f"{r.get('source')}: {r.get('reason') or r.get('kind') or ''}".strip() for r in c.get("lethal_risks") or []))
        ar = c.get("action_readiness") or {}
        if ar and ar.get("ready") is False:
            out.append(f"Not ready: {ar.get('reason') or ar}")
    elif st.get("map"):
        m = st["map"]
        out.append(f"Boss: {run.get('boss_id') or (m.get('boss_node') or {})}")
        for o in m.get("options") or m.get("next_options") or []:
            votes = f" votes {o.get('voted_player_ids')}" if o.get("voted_player_ids") else ""
            out.append(f"  [{o.get('index', o.get('i'))}] {o.get('node_type') or o.get('type')} {o.get('coord', '')}{votes}")
    else:
        body = {k: v for k, v in st.items() if v not in (None, [], {}) and k not in ("run", "session", "available_actions")}
        out.append(json.dumps(body, separators=(",", ":"))[:3000])
    if st.get("available_actions"):
        out.append("Actions: " + ", ".join(st["available_actions"]))
    return "\n".join(x for x in out if x)


def party_view(host_st, mate_st):
    """One screen for co-op: both players, both hands, enemies, and host/teammate consistency (P6.E3.S2, P6.E5)."""
    out = []
    hc, mc = host_st.get("combat") or {}, mate_st.get("combat") or {}
    hr, mr = host_st.get("run") or {}, mate_st.get("run") or {}
    out.append(f"[{Sts2AgentAdapter.screen(mate_st)}] floor {mr.get('floor', '-')} turn {mate_st.get('turn') or '-'}")
    players = mc.get("players") or hc.get("players") or mr.get("players") or []
    out.append("Players:")
    out.extend(_a_player_rows(players, local_label="Agent", other_label="Player"))
    if mc.get("enemies"):
        out.append("Enemies:")
        for e in mc["enemies"]:
            if e.get("is_alive", True):
                out.append(f"  [{e.get('index')}] {e.get('name')} HP {e.get('current_hp')}/{e.get('max_hp')} block {e.get('block', 0)} "
                           f"| {_a_intents(e)} | {_a_powers(e.get('powers'))}")
        total = sum((i.get("total_damage") or 0) for e in mc["enemies"] if e.get("is_alive", True) for i in e.get("intents") or [])
        out.append(f"Incoming attack damage this turn (sum of intents, before targeting): {total}")
    if hc.get("hand") is not None and hc:
        out.append("Player's hand (read-only):")
        out.extend(_a_hand(hc.get("hand")) or ["  (empty)"])
    if mc:
        out.append("Agent's hand:")
        out.extend(_a_hand(mc.get("hand")) or ["  (empty)"])
        if mc.get("end_turn_will_kill_player"):
            out.append("WARNING: ending the Agent's turn now is lethal for the Agent")
    if hc.get("end_turn_will_kill_player"):
        out.append("WARNING: the Player's end turn is lethal for the Player")
    issues = consistency(host_st, mate_st)
    out.append("Consistency: " + ("ok" if not issues else "; ".join(issues)))
    return "\n".join(out)


def consistency(host_st, mate_st):
    """Compare what both instances report about the shared world (lockstep: they should agree)."""
    issues = []
    hr, mr = host_st.get("run") or {}, mate_st.get("run") or {}
    if hr.get("floor") != mr.get("floor"):
        issues.append(f"floor host {hr.get('floor')} vs teammate {mr.get('floor')}")
    if host_st.get("run_id") and mate_st.get("run_id") and host_st["run_id"] != mate_st["run_id"]:
        issues.append(f"run_id host {host_st['run_id']} vs teammate {mate_st['run_id']}")
    he = [(e.get("enemy_id"), e.get("current_hp")) for e in (host_st.get("combat") or {}).get("enemies") or []]
    me = [(e.get("enemy_id"), e.get("current_hp")) for e in (mate_st.get("combat") or {}).get("enemies") or []]
    if he and me and he != me:
        issues.append(f"enemies host {he} vs teammate {me}")
    hp = {p.get("player_id"): p.get("current_hp") for p in (host_st.get("combat") or {}).get("players") or []}
    mp = {p.get("player_id"): p.get("current_hp") for p in (mate_st.get("combat") or {}).get("players") or []}
    if hp and mp and hp != mp:
        issues.append(f"player HP host {hp} vs teammate {mp}")
    return issues


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
    """Return the adapter for --instance. Raises ModError when the teammate cannot be located."""
    instance = getattr(args, "instance", "solo")
    if args.mod == "sts2mcp":
        if instance == "solo":
            return Sts2McpAdapter(args.port or 15526, multiplayer=args.mp, opener=opener)
        if instance == "host":
            return Sts2McpAdapter(args.host_port or 15526, multiplayer=True, opener=opener)
        if not args.port:
            raise SystemExit("--instance teammate with --mod sts2mcp needs --port (STS2MCP has no teammate discovery)")
        return Sts2McpAdapter(args.port, multiplayer=True, opener=opener)
    if instance == "solo":
        return Sts2AgentAdapter(args.port or 8080, opener=opener)
    host = Sts2AgentAdapter(args.host_port or 8080, opener=opener)
    if instance == "host":
        return host
    if args.port:
        return Sts2AgentAdapter(args.port, opener=opener)
    comp = host.health_data().get("companion")
    if not comp or not comp.get("api_port"):
        raise ModError("no teammate connected: the host's /health has companion = null (invite the AI teammate first)")
    if comp.get("api_host", "127.0.0.1") not in LOCAL_HOSTS:
        raise ModError(f"refusing non-local teammate address {comp.get('api_host')}")
    return Sts2AgentAdapter(int(comp["api_port"]), opener=opener)


def check_can_act(args, adapter, before):
    """Refuse actions that could land on the Player's character. Returns an error message or None."""
    instance = getattr(args, "instance", "solo")
    if instance == "host":
        return "refused: the host instance is the Player's window; the Agent never acts there (use --instance teammate)"
    if adapter.name == "sts2agent":
        if instance == "teammate":
            role = adapter.health_data().get("instance_role")
            if role != "companion":
                return f"refused: the target instance reports instance_role={role!r}, not 'companion'"
        elif Sts2AgentAdapter.is_multiplayer(before):
            return "refused: this is a multiplayer run; act through --instance teammate"
    elif instance == "solo" and args.mp:
        return "refused: --mp in solo mode; act through --instance teammate --port <teammate port>"
    return None


def main(argv=None, opener=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mod", choices=["sts2mcp", "sts2agent"], default="sts2mcp")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--mp", action="store_true", help="STS2MCP multiplayer endpoint")
    ap.add_argument("--instance", choices=["solo", "host", "teammate"], default="solo")
    ap.add_argument("--host-port", type=int, default=None)
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
    sub.add_parser("party")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "party":
            if args.mod != "sts2agent":
                raise SystemExit("party needs --mod sts2agent (STS2MCP: run state with --instance host and --instance teammate)")
            host = Sts2AgentAdapter(args.host_port or 8080, opener=opener)
            args.instance = "teammate"
            mate = make_adapter(args, opener)
            print(party_view(host.state(), mate.state()))
            return
        adapter = make_adapter(args, opener)
        brief = brief_sts2agent if adapter.name == "sts2agent" else brief_sts2mcp
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
            err = check_can_act(args, adapter, before)
            if err:
                raise SystemExit(err)
            ok, resp = adapter.act(args.action, params, args.reason)
            log_decision(args.log, {
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "mod": adapter.name,
                "instance": args.instance,
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
