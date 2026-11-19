#!/usr/bin/env python3
"""Phase 0 smoke test (P0.E5): read-only checks that the live mod serves every field the project's tools use.

It never sends an action. For STS2-Agent it:
  1. reads GET /health: service, game version (expects v0.111.x), status ready/degraded, missing members;
  2. reads GET /state and checks the field paths that tools/plan_turn.py, path.py, draft.py, advise.py,
     deck_check.py and journal.py read, for the current screen;
  3. lists card IDs in the deck, hand, rewards and shop that are not in the extract (new on v0.107.1+);
  4. runs tools/advise.py on the state and reports any exception;
  5. with --save, stores the state under tools/tests/fixtures/live/<screen>-<time>.json so the offline tests
     can be rerun on real data.
With --watch it polls (read-only) and checks each new screen once, so the Player can click through a run.

Usage:
  python3 -I tools/smoke.py [--port 8080] [--save] [--watch [--minutes 30]]
  python3 -I tools/smoke.py --file state.json        (check a saved state offline)
"""
import argparse
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sts  # noqa: E402
from stslib import PROJECT  # noqa: E402

FIXTURES = PROJECT / "tools" / "tests" / "fixtures" / "live"
COMMON = ["screen", "session.mode", "run.floor", "run.current_hp", "run.max_hp", "run.ascension", "run.act_id",
          "run.boss_id", "run.deck[].card_id", "run.deck[].upgraded", "run.potions[].occupied", "run.potions[].potion_id",
          "run.gold"]
SPEC = {
    "COMBAT": ["combat.player.energy", "combat.player.current_hp", "combat.player.block", "combat.player.powers",
               "combat.hand[].index", "combat.hand[].card_id", "combat.hand[].energy_cost", "combat.hand[].playable",
               "combat.hand[].dynamic_values", "combat.enemies[].index", "combat.enemies[].current_hp",
               "combat.enemies[].block", "combat.enemies[].powers", "combat.enemies[].intents",
               "combat.end_turn_will_kill_player"],
    "MAP": ["map.nodes[].row", "map.nodes[].col", "map.nodes[].node_type", "map.nodes[].children", "map.boss_node",
            "map.available_nodes[].index", "map.available_nodes[].row"],
    "REWARD": ["reward.rewards", "reward.card_options"],
    "REST": ["rest.options[].option_id", "rest.options[].index"],
    "SHOP": ["shop.cards[].card_id", "shop.cards[].price", "shop.cards[].enough_gold", "shop.cards[].index",
             "shop.relics", "shop.potions", "shop.card_removal"],
    "EVENT": ["event.event_id", "event.options[].text_key", "event.options[].index"],
}
OPTIONAL_PATHS = {"combat.player.powers", "combat.enemies[].powers", "reward.rewards", "reward.card_options",
                  "run.boss_id", "shop.relics", "shop.potions", "shop.card_removal"}


def get_path(obj, path):
    """Resolve 'a.b[].c' to a list of values; [] maps over lists. Returns (found, values)."""
    vals = [obj]
    for part in path.split("."):
        many = part.endswith("[]")
        key = part[:-2] if many else part
        nxt = []
        for v in vals:
            if not isinstance(v, dict) or key not in v:
                continue
            x = v[key]
            if many:
                if isinstance(x, list):
                    nxt.extend(x)
            else:
                nxt.append(x)
        if not nxt and not (many and any(isinstance(v, dict) and isinstance(v.get(key), list) for v in vals)):
            return False, []
        vals = nxt
    return True, vals


def check_state(st):
    st = st.get("data", st)
    scr = (st.get("screen") or "?").upper()
    issues, notes = [], []
    paths = COMMON + SPEC.get(scr, [])
    for p in paths:
        ok, _ = get_path(st, p)
        if not ok:
            # a list path whose list is empty is fine; a missing key is not
            parent = p.split("[]")[0]
            pok, pvals = get_path(st, parent) if "[]" in p else (False, [])
            if pok and pvals and isinstance(pvals[0], list) and not pvals[0]:
                continue
            (notes if p in OPTIONAL_PATHS else issues).append(f"missing: {p}")
    import deck_metrics
    deck_metrics.apply_patches("v0.111.1")
    ids = set()
    for p in ("run.deck[].card_id", "combat.hand[].card_id", "reward.card_options[].card_id", "shop.cards[].card_id"):
        ids |= {x for x in get_path(st, p)[1] if isinstance(x, str)}
    unknown = sorted(i for i in ids if i.split(".", 1)[-1] not in deck_metrics.CARDS)
    if unknown:
        notes.append("cards not in the extract (tools count them as 0): " + ", ".join(unknown))
    if scr == "COMBAT":
        for e in (st.get("combat") or {}).get("enemies") or []:
            for i in e.get("intents") or []:
                if i.get("damage") is not None and i.get("hits") is None:
                    issues.append(f"intent without hits on {e.get('name')}")
        for h in (st.get("combat") or {}).get("hand") or []:
            if not h.get("dynamic_values"):
                notes.append(f"no dynamic_values on {h.get('card_id')}: planner falls back to base values")
                break
    try:
        import advise
        advise.advise(st)
    except Exception as ex:  # report, never crash the smoke test
        issues.append(f"advise.py raised {type(ex).__name__}: {ex}\n" + traceback.format_exc(limit=3))
    return scr, issues, notes


def check_health(h):
    d = h.get("data", h) if isinstance(h, dict) else {}
    out = []
    if d.get("service") != "sts2-ai-agent":
        out.append(f"service is {d.get('service')!r}, expected 'sts2-ai-agent'")
    gv = d.get("game_version") or "?"
    if not str(gv).startswith("v0.111"):
        out.append(f"game_version {gv}: the plan targets main v0.111.x")
    if d.get("status") != "ready":
        miss = (d.get("compatibility") or {}).get("missing_members") or []
        out.append(f"status {d.get('status')!r}; missing members: " + ", ".join(f"{m.get('member')} ({m.get('feature')})" for m in miss))
    return d, out


def save(st, scr):
    FIXTURES.mkdir(parents=True, exist_ok=True)
    f = FIXTURES / f"{scr.lower()}-{datetime.now():%Y%m%d-%H%M%S}.json"
    f.write_text(json.dumps(st, indent=1))
    return f


def report(scr, issues, notes):
    print(f"[{scr}] " + ("OK" if not issues else f"{len(issues)} problem(s)"))
    for i in issues:
        print("  PROBLEM " + i)
    for n in notes:
        print("  note    " + n)


def main(argv=None, opener=None, sleep=time.sleep, clock=time.time):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--file")
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--minutes", type=float, default=30)
    args = ap.parse_args(argv)
    if args.file:
        scr, issues, notes = check_state(json.loads(Path(args.file).read_text()))
        report(scr, issues, notes)
        return 1 if issues else 0
    ad = sts.Sts2AgentAdapter(args.port, opener=opener)
    try:
        d, hissues = check_health(ad.health())
    except sts.ModError as e:
        print(f"cannot reach the mod: {e}")
        return 2
    print(f"health: {d.get('service')} {d.get('mod_version')} · game {d.get('game_version')} · {d.get('status')} · "
          f"role {d.get('instance_role')} · port {d.get('api_port')}")
    for i in hissues:
        print("  PROBLEM " + i)
    seen, bad = set(), bool(hissues)
    deadline = clock() + args.minutes * 60
    while True:
        st = ad.state()
        scr, issues, notes = check_state(st)
        if scr not in seen:
            seen.add(scr)
            report(scr, issues, notes)
            bad |= bool(issues)
            if args.save:
                print(f"  saved {save(st, scr).relative_to(PROJECT)}")
        if not args.watch or clock() > deadline:
            break
        sleep(1.0)
    print(f"screens checked: {', '.join(sorted(seen))}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
