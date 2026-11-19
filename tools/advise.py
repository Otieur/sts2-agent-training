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
STS2MCP states are detected and converted by tools/mcp_adapter.py (the deck comes from the last combat's piles).
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


def _rows(path):
    """CSV rows from a file that is closed straight away (avoids unclosed handles)."""
    import csv as _csv
    with open(path, newline="") as fh:
        return list(_csv.DictReader(fh))

ENGINE_UPGRADES = ["DEMON_FORM", "CORRUPTION", "BARRICADE", "FEEL_NO_PAIN", "BODY_SLAM"]
FUNCTION_UPGRADES = ["ARMAMENTS", "TRUE_GRIT"]
REMOVABLE_CURSES_HINT = "Injury, Clumsy and other non-Eternal curses"


def _run(st):
    return st.get("run") or {}


def _act(st):
    try:
        from stslib import act_number
        return act_number(_run(st).get("act_id"))
    except (TypeError, ValueError):
        return 1


def _deck(st):
    return draft.deck_ids_from_state(_run(st).get("deck"))


def _character(st):
    return draft.guess_character(_deck(st)) if _deck(st) else "IRONCLAD"


# ------------------------------------------------------------------------------------------------ screens
_ROOM_OF_MONSTER = None


def room_of_monster():
    """Monster id -> the room type it appeared in most (monster / elite / boss), from the Player's history."""
    global _ROOM_OF_MONSTER
    if _ROOM_OF_MONSTER is None:
        import collections
        counts = collections.defaultdict(collections.Counter)
        con = connect()
        for room, ids in con.execute("SELECT room_type, monster_ids FROM floors WHERE room_type IN ('monster','elite','boss') AND monster_ids IS NOT NULL"):
            try:
                names = json.loads(ids)
            except (TypeError, ValueError):
                names = []
            for m in names:
                counts[str(m).split(".", 1)[-1].upper()][room] += 1
        con.close()
        _ROOM_OF_MONSTER = {m: c.most_common(1)[0][0] for m, c in counts.items()}
    return _ROOM_OF_MONSTER


def fight_type(st):
    """boss / elite / hallway / unknown from the STS2-Agent state: an explicit room type if the state has one,
    else the act boss's name, else the room each enemy appeared in during the Player's history."""
    c = st.get("combat") or {}
    ids = [str(e.get("enemy_id") or "").split(".", 1)[-1].upper() for e in c.get("enemies") or []]
    room = str((st.get("run") or {}).get("room_type") or st.get("room_type") or "").lower()
    boss = (_run(st).get("boss_id") or "").upper().replace("_BOSS", "").replace("ENCOUNTER.", "")
    if "boss" in room or (boss and any(boss in i for i in ids)):
        return "boss"
    if "elite" in room:
        return "elite"
    if room:
        return "hallway"
    rooms = {room_of_monster().get(i) for i in ids if i} - {None}
    if "boss" in rooms:
        return "boss"
    if "elite" in rooms:
        return "elite"
    return "hallway" if rooms == {"monster"} else "unknown"


def combat(st, top=2):
    hand, player, enemies = plan_turn.from_state(st)
    ft = fight_type(st)
    if not enemies:
        return "combat: no live enemies in the state"
    res = plan_turn.plans(hand, player, enemies)
    out = []
    for c in hand:
        if c.note:
            out.append(f"note: {c.name}: {c.note}")
    scaling_powers = ("TERRITORIAL", "RITUAL", "DEMON_FORM", "ENRAGE")  # enemies that gain Strength every turn
    scaling = any(str(x.get("power_id") or x.get("name") or "").upper().startswith(scaling_powers)
                  for e in (st.get("combat") or {}).get("enemies") or [] for x in e.get("powers") or [])
    pc = plan_turn.POTION_COST.get(ft, plan_turn.POTION_COST["hallway"])  # unknown: hold potions
    pv = plan_turn.POWER_VALUE.get(ft, plan_turn.POWER_VALUE["elite"])
    raw_enemies = (st.get("combat") or {}).get("enemies") or []
    ids_up = [str(e.get("enemy_id") or e.get("name") or "").upper().replace(" ", "_") for e in raw_enemies]
    giant = any("WATERFALL_GIANT" in i for i in ids_up)
    fysh = any("SOUL_FYSH" in i for i in ids_up)
    steam = max((int(x.get("amount") or 0) for e in raw_enemies for x in e.get("powers") or []
                 if str(x.get("power_id") or x.get("name") or "").upper().startswith("STEAM_ERUPTION")), default=0)
    party = [x for x in (st.get("combat") or {}).get("players") or [] if isinstance(x, dict)]
    if len(party) > 1:  # co-op: the team's health lines (combat.players[]; target_index is the position in this list)
        cells = []
        for i, x in enumerate(party):
            hp_, mx_ = x.get("current_hp"), x.get("max_hp")
            low = isinstance(hp_, (int, float)) and isinstance(mx_, (int, float)) and mx_ and hp_ < 0.3 * mx_
            cells.append(f"[{i}] {x.get('character_name') or x.get('character_id') or '?'}{' (you)' if x.get('is_local') else ''} "
                         f"HP {hp_}/{mx_} block {x.get('block', 0)}" + (" DOWN" if x.get("is_alive") is False else " LOW" if low else ""))
        out.append("party: " + " | ".join(cells) + " · a Block or heal potion can go to a teammate: use_potion option_index=<slot> "
                   "target_index=<their [n]> (v0.111.1)")
    if any(str(x.get("power_id") or x.get("name") or "").upper().startswith("WITHERING") for e in raw_enemies for x in e.get("powers") or []):
        out.append("Withering Presence: every 6th card you play adds a Wither to your hand (3 damage at the end of each turn "
                   "it is held); prefer fewer, bigger plays and exhaust Withers")
    if player.sandpit:
        out.append(f"Sandpit {player.sandpit}: it ticks down before your next turn and kills you when it runs out; end every "
                   f"turn at 2 or more (plans below that are marked fatal). Each Frantic Escape adds 1 and costs 1 more each play, "
                   f"so play them while cheap if the fight will outlast the counter")
    if steam:
        out.append(f"Steam Eruption {steam}: after its HP reaches 0 the Giant is stunned for a turn, then hits for {steam} "
                   f"(+3 for each move it makes before then); your HP plus the next turn's block must exceed it")
    out.append(f"fight type: {ft} (potion cost {pc:g} HP, Powers {pv:g} per energy)"
               + (" · recommended: the safe plan (Waterfall Giant: the death explosion punishes HP spent; simulated)" if giant else
                  " · recommended: the safe plan (Soul Fysh: simulated, clearly better below full HP)" if fysh else
                  " · recommended: the balanced plan (boss fights, simulation)" if ft == "boss" else
                  " · recommended: the balanced plan (an enemy gains Strength every turn; simulated Byrdonis)" if scaling else
                  " · choose safe if HP is below the act plan, balanced if ahead"))
    best = {}
    for mode in ("safe", "balanced"):
        out.append(f"{mode}:")
        ranked = plan_turn.rank(res, mode, pc, pv)
        best[mode] = ranked[0] if ranked else None
        out += ["  " + plan_turn.fmt(o, player.hp) for o in ranked[:top]]
    for mode, o in best.items():
        if o:
            out.append(f"commands for the top {mode} plan (indexes already adjusted):")
            out += ["  " + c for c in plan_turn.commands(o, hand, mode=mode, mod="sts2mcp" if st.get("_source") == "sts2mcp" else "sts2agent")]
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
    note = None
    if not isinstance(mx, (int, float)) or mx <= 0:
        mx, note = 80, "max HP missing from the state: 80 assumed"
    if not isinstance(hp, (int, float)):
        hp, note = mx, "HP missing from the state: full HP assumed, so the routes below are optimistic"
    model = pathmod.get_model(_character(st), int(run.get("ascension") or 0))
    w = pathmod.DEFAULT_RISK_WEIGHT.get(act, 16.0)
    res = pathmod.rank(paths, nodes, model, act, hp, mx, run.get("boss_id"), w, pathmod.deck_metrics_from(_deck(st)))
    idx = {(n.get("row"), n.get("col")): n.get("index") for n in m.get("available_nodes") or []}
    out = [f"{len(res)} distinct routes, risk weight {w:g}"] + ([f"note: {note}"] if note else [])
    for o in res[:top]:
        out.append(f"  score {o['score']:5.2f}  choose_map_node option_index={idx.get(o['first'], '?')} {o['first']}  {o['seq']}  "
                   f"boss arrival {o['boss_hp']}%, P(run ends) {100 * o['p_end']:.0f}%" + (f"  ! {'; '.join(o['notes'])}" if o["notes"] else ""))
    return "\n".join(out)


def card_reward(st):
    deck, offer, act, floor, boss = draft.from_state_obj(st)
    run = _run(st)
    res = draft.score_offer(deck, offer, _character(st), act or 1, floor, boss, simulate=(act or 1) == 1,
                            hp=run.get("current_hp"), max_hp=run.get("max_hp") or 80, sim_deck=draft.sim_deck_from_state(st),
                            sim_relics=draft.sim_relics_from_state(st))  # potions left out: they triple the time and shift every option alike
    idx = {"CARD." + str(c.get("card_id")): c.get("index") for c in (st.get("reward") or {}).get("card_options") or [] if c.get("card_id")}
    out = [f"deck {res['base']['size']} cards, damage/turn {res['base']['dmg']:.1f}, block/turn {res['base']['block']:.1f}, "
           f"scaling {res['base']['scaling']}"]
    for r in res["rows"]:
        out.append(f"  {r['score']:5.2f}  [{idx.get('CARD.' + r['id'], '?')}] {r['card']}: {'; '.join(r['reasons'])}")
    out.append(f"  {res['skip_bar']:5.2f}  SKIP")
    p = res["pick"]
    out.append("Recommendation: " + (f"choose_reward_card option_index={idx.get('CARD.' + p['id'], '?')} ({p['card']})" if p else "skip_reward_cards"))
    return "\n".join(out)


def reward_main(st):
    rw = (st.get("reward") or {}).get("rewards") or []
    pots = [p for p in _run(st).get("potions") or []]
    free_slots = sum(1 for p in pots if not p.get("occupied"))
    out = ["Claim from the highest index down (indexes shift):"]
    for r in sorted(rw, key=lambda r: -(r.get("index") if isinstance(r.get("index"), int) else 0)):
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
    if not isinstance(hp, (int, float)) or not isinstance(max_hp, (int, float)) or not max_hp:
        why = "HP or max HP missing from the state: decide by hand (playbook section 5)"
        return {k: ("either", why) for k in ("boss", "elite", "other") if nxt in (None, k)}
    model = pathmod.get_model(character, ascension)
    thr = model.boss_threshold(act, boss, max_hp)
    p75 = model.elite_p75.get(act, 35.0)
    cases = {
        "boss": ("rest" if hp < thr else "smith", f"HP {hp} vs boss threshold {thr:.0f} ({'70% in Act 3' if act >= 3 else 'band median + 10'})"),
        "elite": ("rest" if hp - p75 < 0.5 * max_hp else "smith", f"HP {hp} minus elite p75 {p75:.0f} vs 50% of max ({0.5 * max_hp:.0f})"),
        "other": ("rest" if hp < 0.40 * max_hp else ("smith" if hp >= 0.5 * max_hp else "decide by the next two fights' p75"),
                  f"HP {hp}/{max_hp} = {100 * hp / max_hp:.0f}% (rest under 40% per H11, smith at 50%+)"),
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
    others = [str(k) for k in opts if k and k not in ("HEAL", "SMITH")]
    if others:
        out.append(f"  other options here: {', '.join(others)} (judge by the relic's effect)")
    return "\n".join(out)


def event(st):
    ev = st.get("event") or {}
    eid = (ev.get("event_id") or "").upper()
    table = {(e["Event"], e["Option"]): e for e in json.loads((PROJECT / "knowledge/data/extract-2026-09-21/event_options.json").read_text())}
    con = connect()
    ancients = {}
    afile = PROJECT / "data" / "tables" / "ancient_relics.csv"
    if afile.exists():
        import csv
        ancients = {r["relic"]: r for r in _rows(afile)}
    events = {}
    efile = PROJECT / "data" / "tables" / "event_choices.csv"
    if efile.exists():
        import csv
        events = {(r["event"], r["option"]): r for r in _rows(efile)}
    out = [f"Event {eid}: {ev.get('title', '')}"]
    for o in ev.get("options") or []:
        key = re.sub(r"^[A-Z_]+\.pages\.", "", o.get("text_key") or "")
        info = table.get((eid, key), {})
        hist = con.execute("""SELECT COUNT(*), AVG(hp_change), AVG(gold_change), AVG(max_hp_change) FROM event_choices
                              WHERE event_id = ? AND choice_key LIKE ?""", ["EVENT." + eid, f"%{key}%"]).fetchone()
        flag = " LOCKED" if o.get("is_locked") else ""
        flag += " WILL KILL YOU" if o.get("will_kill_player") else ""
        past = f"; the Player chose it {hist[0]}x (HP {hist[1]:+.1f}, gold {hist[2]:+.0f}, max HP {hist[3]:+.1f})" if hist and hist[0] else ""
        evrec = events.get((eid, key))
        if evrec:
            past += (f"; decision-point record: survived the act {int(evrec['survived_chosen'])}/{int(evrec['chosen'])} chosen vs "
                     f"{int(evrec['survived_others'])}/{int(evrec['others'])} other options, p={evrec['p']}")
        anc = ancients.get(key.rsplit(".", 1)[-1].upper())
        if anc and anc["survive_act_chosen"] and anc["survive_act_passed"]:
            past += (f"; Ancient record (all characters): survived the act {float(anc['survive_act_chosen']):.0%} picked vs "
                     f"{float(anc['survive_act_passed']):.0%} passed, p={anc['p_survive']} (reports/phase2/ancient-relics.md)")
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
        out.append(f"Removal {rm.get('price')}g, {'affordable' if rm.get('enough_gold') else 'not affordable or used'}: {why}"
                   + (" → remove_card_at_shop, then select_deck_card on the card selection screen" if rm.get("enough_gold") else ""))
    for r in sh.get("relics") or []:
        if r.get("is_stocked", True):
            out.append(f"  relic buy_relic option_index={r.get('index')} {r.get('name')} {r.get('price')}g{'' if r.get('enough_gold') else ' (cannot afford)'}: {r.get('description') or ''}")
    for p in sh.get("potions") or []:
        if p.get("is_stocked", True):
            out.append(f"  potion buy_potion option_index={p.get('index')} {p.get('name')} {p.get('price')}g")
    out.append("Priority (playbook section 6): boss checklist relic or card > S/A card > curse removal > Strike removal in a small Act 1 deck > other relics > potions")
    return "\n".join(out)


def _tier_score(cid, tiers):
    c = draft.dm.CARDS.get(cid)
    tr = tiers.get(draft.norm(c["name"])) if c else None
    return draft.TIER_SCORE.get(tr[0], 2) if tr else 2


def selection(st):
    """Card selection screens: upgrade, remove, transform, exhaust, duplicate (playbook sections 2.3 and 6)."""
    sel = st.get("selection") or {}
    kind, prompt = (sel.get("kind") or "").lower(), (sel.get("prompt") or "").lower()
    cards = [c for c in sel.get("cards") or [] if c.get("card_id")]
    tiers = draft.load_tiers(_character(st))

    def is_curse(c):
        rec = draft.dm.CARDS.get(c["card_id"]) or {}
        return rec.get("type") in ("Curse", "Status") or (c.get("card_type") or "") in ("Curse", "Status")

    def badness(c):  # higher = worse card to keep
        cid = c["card_id"]
        if is_curse(c):
            return 100 if cid != "ASCENDERS_BANE" else -100  # Eternal: cannot be removed
        if cid.startswith("STRIKE"):
            return 50
        if cid.startswith("DEFEND"):
            return 40
        return 10 - 2 * _tier_score(cid, tiers) - (3 if c.get("upgraded") else 0)

    ids = {c["card_id"].split(".", 1)[-1].upper() for c in cards}
    if "DISINTEGRATION" in ids and ids & {"MIND_ROT", "SLOTH", "WASTE_AWAY"}:
        # Knowledge Demon's Curse of Knowledge: Disintegration or one other card (playbook section 10; simulated)
        other = next(iter(ids & {"MIND_ROT", "SLOTH", "WASTE_AWAY"}))
        pick = {"MIND_ROT": "MIND_ROT", "SLOTH": "SLOTH", "WASTE_AWAY": "WASTE_AWAY"}[other]
        note = {"MIND_ROT": "offer 1: take Mind Rot (Disintegration stacks for the rest of the fight)",
                "SLOTH": "offer 2: take Sloth unless the deck plays many 0-cost cards (at most 3 cards a turn)",
                "WASTE_AWAY": "offer 3 is close: Waste Away by default; Disintegration if the fight ends within about 2 turns "
                              "or the deck needs every energy; never if Disintegration is already on you"}[other]
        ranked = sorted(cards, key=lambda c: c["card_id"].split(".", 1)[-1].upper() != pick)
        why = "Curse of Knowledge: " + note
    elif "upgrade" in kind or "upgrade" in prompt:
        def up_score(c):
            cid = c["card_id"]
            s = 3 * _tier_score(cid, tiers)
            if cid in ENGINE_UPGRADES:
                s += 20
            elif cid in FUNCTION_UPGRADES:
                s += 10
            if c.get("upgrade_energy_cost") is not None and c.get("energy_cost") is not None and c["upgrade_energy_cost"] < c["energy_cost"]:
                s += 6
            if cid.startswith(("STRIKE", "DEFEND")):
                s -= 10
            return s
        ranked, why = sorted(cards, key=lambda c: -up_score(c)), "upgrade: engine pieces, then function-changing upgrades and cost cuts, then tier (playbook 2.3)"
    elif "remove" in prompt or "transform" in kind or "transform" in prompt or "exhaust" in prompt:
        ranked, why = sorted(cards, key=lambda c: -badness(c)), "remove / transform / exhaust: curses (not Ascender's Bane, which is Eternal), then Strikes, Defends, lowest tier (playbook 6, H4)"
    else:
        ranked, why = sorted(cards, key=lambda c: -_tier_score(c["card_id"], tiers)), "best card by tier (copy, enchant or other)"
    out = [f"Selection: {sel.get('prompt') or kind} ({why})"]
    for c in ranked[:5]:
        out.append(f"  select_deck_card option_index={c.get('index')}: {c.get('name') or c['card_id']}{'+' if c.get('upgraded') else ''}"
                   + (f" -> {c['upgrade_rules_text']}" if c.get("upgrade_rules_text") else ""))
    return "\n".join(out)


def _clean(o):
    """Drop null list items (a list of cards or options with a null in it) so the screen handlers can use .get safely."""
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_clean(v) for v in o if v is not None]
    return o


def advise(st, nxt=None, deck_cache=None):
    """Advice for the current screen. A handler that fails on an unexpected state shape reports the error and the
    screen instead of raising, so a live run is never stopped by the advisor (act by judgment and save the state)."""
    import traceback
    try:
        return _advise(st, nxt, deck_cache)
    except Exception as ex:  # noqa: BLE001
        tb = traceback.extract_tb(ex.__traceback__)[-1]
        scr = ((st or {}).get("data", st) or {}).get("screen") if isinstance(st, dict) else None
        return (f"[ADVICE FAILED] {type(ex).__name__}: {ex} at {tb.filename.split('/')[-1]}:{tb.lineno} (screen {scr}). "
                "Act by judgment; save this state to runs/<run>/ and report it in the post-mortem.")


def _advise(st, nxt=None, deck_cache=None):
    import mcp_adapter
    if not isinstance(st, dict):
        return "no state (expected a JSON object)"
    if mcp_adapter.is_mcp(st):
        st = mcp_adapter.mcp_to_agent(st, **({"deck_cache": deck_cache} if deck_cache else {}))
    st = st.get("data", st) if isinstance(st.get("data", st), dict) else st
    st = _clean(st)
    scr = str(st.get("screen") or "").upper()
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
    if st.get("selection") and (st["selection"].get("cards")):
        return "[CARD SELECTION]\n" + selection(st)
    return sts.brief_sts2agent(st)


def main(argv=None, opener=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--state", help="a saved state file")
    src.add_argument("--live", action="store_true", help="read the state from the running mod (one command per decision)")
    ap.add_argument("--save", help="with --live: also write the state here (for example runs/<run>/state.json)")
    ap.add_argument("--mod", choices=["sts2agent", "sts2mcp"], default="sts2agent")
    ap.add_argument("--instance", choices=["solo", "teammate", "host"], default="solo")
    ap.add_argument("--port", type=int)
    ap.add_argument("--host-port", type=int)
    ap.add_argument("--mp", action="store_true", help="STS2MCP: multiplayer endpoint")
    ap.add_argument("--next", choices=["boss", "elite", "other"])
    ap.add_argument("--deck-cache", help="STS2MCP only: where the deck seen in the last combat is cached (default runs/current/deck.json)")
    args = ap.parse_args(argv)
    if args.live:
        try:
            st = sts.make_adapter(args, opener=opener).state()
        except sts.ModError as ex:
            print(f"cannot read the state: {ex}")
            return 1
        if args.save:
            Path(args.save).parent.mkdir(parents=True, exist_ok=True)
            Path(args.save).write_text(json.dumps(st, indent=1))
    else:
        st = json.loads(Path(args.state).read_text())
    print(advise(st, args.next, args.deck_cache))
    return 0


if __name__ == "__main__":
    sys.exit(main())
