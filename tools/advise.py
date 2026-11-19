#!/usr/bin/env python3
"""One entry point for the decision loop: read a saved STS2-Agent /state, detect the screen, and print the
playbook's advice for it (P4.E2). The Agent still decides; this keeps the arithmetic and the rules consistent.

  COMBAT             tools/plan_turn.py: safe and balanced plays for this turn
  MAP                tools/path.py: best routes to the boss
  REWARD (cards)     tools/draft.py: score the offer against the skip bar
  REWARD (main)      claim order
  REST               playbook section 5 rest rule (three cases if the next fight is unknown) and upgrade candidates
  EVENT              each option's effect, cost and risk tag from the game data, and the Player's past outcomes
  SHOP               cards scored as in draft.py, removal per H4 and curses, relics and potions listed
  anything else      the compact brief from tools/sts.py

Usage: python3 -I tools/advise.py --state state.json [--next boss|elite|other]
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import draft  # noqa: E402
import plan_turn  # noqa: E402
import sts  # noqa: E402
from stslib import PROJECT, connect  # noqa: E402

ENGINE_UPGRADES = ["DEMON_FORM", "CORRUPTION", "BARRICADE", "FEEL_NO_PAIN", "BODY_SLAM"]
FUNCTION_UPGRADES = ["ARMAMENTS", "TRUE_GRIT"]
REMOVABLE_CURSES_HINT = "Injury, Clumsy and other non-Eternal curses"


def _run(st):
    return st.get("run") or {}


def _act(st):
    try:
        return int(_run(st).get("act_id") or 1)
    except (TypeError, ValueError):
        return 1


def _deck(st):
    return ["CARD." + d["card_id"] for d in _run(st).get("deck") or [] if d.get("card_id")]


def _character(st):
    return draft.guess_character(_deck(st)) if _deck(st) else "IRONCLAD"


# ------------------------------------------------------------------------------------------------ screens
def combat(st, top=2):
    hand, player, enemies = plan_turn.from_state(st)
    if not enemies:
        return "combat: no live enemies in the state"
    res = plan_turn.plans(hand, player, enemies)
    out = []
    for c in hand:
        if c.note:
            out.append(f"note: {c.name}: {c.note}")
    for mode in ("safe", "balanced"):
        out.append(f"{mode}:")
        out += ["  " + plan_turn.fmt(o, player.hp) for o in plan_turn.rank(res, mode)[:top]]
    c = st.get("combat") or {}
    if c.get("end_turn_will_kill_player"):
        out.append("WARNING: ending the turn now is lethal (mod's lethal check)")
    return "\n".join(out)


def map_screen(st, top=3):
    import path as pathmod
    m, run = st.get("map") or {}, _run(st)
    nodes, start, boss_rc = pathmod.load_map(m)
    paths = pathmod.enumerate_paths(nodes, start, boss_rc)
    if not paths:
        return "map: no route to the boss in the state"
    act, hp, mx = _act(st), run.get("current_hp"), run.get("max_hp")
    model = pathmod.get_model(_character(st), int(run.get("ascension") or 0))
    w = pathmod.DEFAULT_RISK_WEIGHT.get(act, 16.0)
    res = pathmod.rank(paths, nodes, model, act, hp, mx, run.get("boss_id"), w)
    idx = {(n["row"], n["col"]): n.get("index") for n in m.get("available_nodes") or []}
    out = [f"{len(res)} distinct routes, risk weight {w:g}"]
    for o in res[:top]:
        out.append(f"  score {o['score']:5.2f}  choose_map_node option_index={idx.get(o['first'], '?')} {o['first']}  {o['seq']}  "
                   f"boss arrival {o['boss_hp']}%, P(run ends) {100 * o['p_end']:.0f}%" + (f"  ! {'; '.join(o['notes'])}" if o["notes"] else ""))
    return "\n".join(out)


def card_reward(st):
    deck, offer, act, floor, boss = draft.from_state_obj(st)
    res = draft.score_offer(deck, offer, _character(st), act or 1, floor, boss)
    idx = {"CARD." + c.get("card_id"): c.get("index") for c in (st.get("reward") or {}).get("card_options") or []}
    out = [f"deck {res['base']['size']} cards, damage/turn {res['base']['dmg']:.1f}, block/turn {res['base']['block']:.1f}, "
           f"scaling {res['base']['scaling']}"]
    for r in res["rows"]:
        out.append(f"  {r['score']:5.2f}  [{idx.get('CARD.' + r['id'], '?')}] {r['card']}: {'; '.join(r['reasons'])}")
    out.append(f"  {res['skip_bar']:5.2f}  SKIP")
    p = res["pick"]
    out.append("Recommendation: " + (f"choose_reward_card option_index={idx.get('CARD.' + p['id'], '?')} ({p['card']})" if p else "skip"))
    return "\n".join(out)


def reward_main(st):
    rw = (st.get("reward") or {}).get("rewards") or []
    pots = [p for p in _run(st).get("potions") or []]
    free_slots = sum(1 for p in pots if not p.get("occupied"))
    out = ["Claim from the highest index down (indexes shift):"]
    for r in sorted(rw, key=lambda r: -r.get("index", 0)):
        t = r.get("reward_type")
        if t == "Potion" and free_slots == 0:
            note = "potion slots full: use or discard a weaker potion first, or skip"
        elif t == "Card":
            note = "opens the card choice (draft.py)"
        elif t == "RemoveCard":
            note = "take it: remove a Strike or a curse (H4)"
        else:
            note = "take it"
        out.append(f"  claim_reward option_index={r.get('index')}: {t} {r.get('description', '')} → {note}")
    return "\n".join(out)


def rest_rule(hp, max_hp, act, ascension, boss, character, nxt=None):
    import path as pathmod
    model = pathmod.get_model(character, ascension)
    thr = model.boss_threshold(act, boss, max_hp)
    p75 = model.elite_p75.get(act, 35.0)
    cases = {
        "boss": ("rest" if hp < thr else "smith", f"HP {hp} vs boss threshold {thr:.0f} ({'70% in Act 3' if act >= 3 else 'band median + 10'})"),
        "elite": ("rest" if hp - p75 < 0.5 * max_hp else "smith", f"HP {hp} minus elite p75 {p75:.0f} vs 50% of max ({0.5 * max_hp:.0f})"),
        "other": ("rest" if hp < 0.35 * max_hp else ("smith" if hp >= 0.5 * max_hp else "decide by the next two fights' p75"),
                  f"HP {hp}/{max_hp} = {100 * hp / max_hp:.0f}% (rest under 35%, smith at 50%+)"),
    }
    return {k: v for k, v in cases.items() if nxt in (None, k)}


def upgrade_candidates(st, n=3):
    deck = [d for d in _run(st).get("deck") or [] if not d.get("upgraded") and d.get("card_id")]
    ids = [d["card_id"] for d in deck]
    tiers = draft.load_tiers(_character(st))
    out = []
    for cid in ENGINE_UPGRADES + FUNCTION_UPGRADES:
        if cid in ids and cid not in out:
            out.append(cid)

    def tier_score(cid):
        c = draft.dm.CARDS.get(cid)
        t = tiers.get(draft.norm(c["name"])) if c else None
        return draft.TIER_SCORE.get(t[0], 2) if t else 0
    for cid in sorted(set(ids) - set(out), key=lambda c: -tier_score(c)):
        if tier_score(cid) > 0:
            out.append(cid)
    return out[:n]


def rest(st, nxt=None):
    run = _run(st)
    cases = rest_rule(run.get("current_hp"), run.get("max_hp"), _act(st), int(run.get("ascension") or 0), run.get("boss_id"),
                      _character(st), nxt)
    opts = {o.get("option_id"): o for o in (st.get("rest") or {}).get("options") or []}
    out = []
    for k, (choice, why) in cases.items():
        o = opts.get("HEAL" if choice == "rest" else "SMITH")
        out.append(f"  next fight {k}: {choice}" + (f" (choose_rest_option option_index={o.get('index')})" if o and choice in ("rest", "smith") else "")
                   + f" — {why}")
    up = upgrade_candidates(st)
    if up:
        out.append("  upgrade candidates (playbook 2.3: engine, then function-changing, then tier): " + ", ".join(up))
    others = [k for k in opts if k not in ("HEAL", "SMITH")]
    if others:
        out.append(f"  other options here: {', '.join(others)} (judge by the relic's effect)")
    return "\n".join(out)


def event(st):
    ev = st.get("event") or {}
    eid = (ev.get("event_id") or "").upper()
    table = {(e["Event"], e["Option"]): e for e in json.loads((PROJECT / "knowledge/data/extract-2026-09-21/event_options.json").read_text())}
    con = connect()
    out = [f"Event {eid}: {ev.get('title', '')}"]
    for o in ev.get("options") or []:
        key = re.sub(r"^[A-Z_]+\.pages\.", "", o.get("text_key") or "")
        info = table.get((eid, key), {})
        hist = con.execute("""SELECT COUNT(*), AVG(hp_change), AVG(gold_change), AVG(max_hp_change) FROM event_choices
                              WHERE event_id = ? AND choice_key LIKE ?""", ["EVENT." + eid, f"%{key}%"]).fetchone()
        flag = " LOCKED" if o.get("is_locked") else ""
        flag += " WILL KILL YOU" if o.get("will_kill_player") else ""
        past = f"; the Player chose it {hist[0]}x (HP {hist[1]:+.1f}, gold {hist[2]:+.0f}, max HP {hist[3]:+.1f})" if hist and hist[0] else ""
        out.append(f"  [{o.get('index')}] {o.get('title')}{flag}: {info.get('Effect', o.get('description', ''))} | cost: "
                   f"{info.get('Cost', '?')} | risk: {info.get('Risk', '?')}{past}")
    con.close()
    return "\n".join(out)


def shop(st):
    sh, run = st.get("shop") or {}, _run(st)
    deck, out = _deck(st), [f"gold {run.get('gold')}"]
    cards = [c for c in sh.get("cards") or [] if c.get("is_stocked", True) and c.get("card_id")]
    if cards:
        res = draft.score_offer(deck, ["CARD." + c["card_id"] for c in cards], _character(st), _act(st), run.get("floor"),
                                run.get("boss_id"))
        price = {"CARD." + c["card_id"]: (c.get("index"), c.get("price"), c.get("enough_gold")) for c in cards}
        out.append("Cards (draft scoring; skip bar %.2f):" % res["skip_bar"])
        for r in res["rows"]:
            i, p, ok = price["CARD." + r["id"]]
            out.append(f"  {r['score']:5.2f}  buy_card option_index={i} {r['card']} {p}g{'' if ok else ' (cannot afford)'}: {'; '.join(r['reasons'][:3])}")
    rm = sh.get("card_removal") or {}
    if rm:
        curses = [d["card_id"] for d in run.get("deck") or [] if (draft.dm.CARDS.get(d.get("card_id")) or {}).get("type") == "Curse"
                  and d.get("card_id") != "ASCENDERS_BANE"]
        strikes = sum(1 for d in deck if "STRIKE" in d)
        why = (f"remove a curse ({', '.join(curses)})" if curses else
               f"remove a Strike ({strikes} in deck; H4: supported at A5+)" if strikes else "no Strike or curse to remove")
        out.append(f"Removal {rm.get('price')}g, {'affordable' if rm.get('enough_gold') else 'not affordable or used'}: {why}")
    for r in sh.get("relics") or []:
        if r.get("is_stocked", True):
            out.append(f"  relic buy_relic option_index={r.get('index')} {r.get('name')} {r.get('price')}g{'' if r.get('enough_gold') else ' (cannot afford)'}: {r.get('description') or ''}")
    for p in sh.get("potions") or []:
        if p.get("is_stocked", True):
            out.append(f"  potion buy_potion option_index={p.get('index')} {p.get('name')} {p.get('price')}g")
    out.append("Priority (playbook section 6): boss checklist relic or card > S/A card > curse removal > Strike removal in a small Act 1 deck > other relics > potions")
    return "\n".join(out)


def advise(st, nxt=None):
    st = st.get("data", st)
    scr = (st.get("screen") or "").upper()
    if scr == "COMBAT" or st.get("combat"):
        return "[COMBAT]\n" + combat(st)
    if scr == "MAP":
        return "[MAP]\n" + map_screen(st)
    if scr == "REWARD":
        rw = st.get("reward") or {}
        if rw.get("card_options"):
            return "[CARD REWARD]\n" + card_reward(st)
        return "[REWARD]\n" + reward_main(st)
    if scr == "REST":
        return "[REST]\n" + rest(st, nxt)
    if scr == "EVENT":
        return "[EVENT]\n" + event(st)
    if scr == "SHOP":
        return "[SHOP]\n" + shop(st)
    return sts.brief_sts2agent(st)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", required=True)
    ap.add_argument("--next", choices=["boss", "elite", "other"])
    args = ap.parse_args(argv)
    print(advise(json.loads(Path(args.state).read_text()), args.next))
    return 0


if __name__ == "__main__":
    sys.exit(main())
