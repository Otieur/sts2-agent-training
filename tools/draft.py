#!/usr/bin/env python3
"""Card-reward helper: applies the playbook's drafting procedure (playbooks/<character>.md §2) to one reward screen,
so every pick is scored the same way and the reason can go straight into the decision log.

Score per offered card (higher is better; tier scale S=5, A=4, B=3, C=2, D=1):
  1. Consensus tier from knowledge/community/<character>-tiers.md                         [COMMUNITY]
  2. v0.111.1 adjustments for changed cards (knowledge/version-delta-v0.111.1.md)           [HYPOTHESIS]
  3. Boss fit for the act boss (playbook §2.2 context overrides, boss plans)              [HYPOTHESIS]
  4. Deck needs against the corner targets (playbook §2.1, reports/phase2/deck-strength.md) [HYPOTHESIS H9]
  5. Engine overrides: Strength engine raises multi-hit, exhaust engine raises exhaust outlets [COMMUNITY]
SKIP wins when no card beats the skip bar, which rises with deck size (the playbook: bigger decks skip more).

Deck metrics (damage and block per turn, scaling count) come from tools/deck_metrics.py: base card numbers only.

Usage:
  python3 -I tools/draft.py --deck STRIKE_IRONCLAD:5 DEFEND_IRONCLAD:4 BASH --offer "Twin Strike" Inflame "Shrug It Off" \\
      --act 1 --floor 6 --boss VANTOM
  python3 -I tools/draft.py --from-state state.json      (STS2-Agent full state: deck, reward cards, floor, boss)
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deck_metrics as dm  # noqa: E402
dm.apply_patches("v0.111.1")  # live tools use the target game's card values
from stslib import PROJECT  # noqa: E402


def _rows(path):
    """CSV rows from a file that is closed straight away (avoids unclosed handles)."""
    import csv as _csv
    with open(path, newline="") as fh:
        return list(_csv.DictReader(fh))

TIER_SCORE = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
UNKNOWN_TIER = 2.0

# v0.111.1 changes relative to the tier sources (playbook §2.2 "Changed on v0.111.1"; necrobinder playbook §3.1).
V0111 = {
    "IRONCLAD": {"MANGLE": (+1.0, "v0.111.1 buff: 20 damage"), "PACTS_END": (+0.5, "v0.111.1 buff: 18 to all"),
                 "HOWL_FROM_BEYOND": (+0.5, "v0.111.1 buff: 18"), "RAMPAGE": (+0.5, "v0.111.1 buff: 10"),
                 "SETUP_STRIKE": (+0.5, "v0.111.1 buff: 3 Strength"), "FORGOTTEN_RITUAL": (+0.5, "v0.111.1: no exhaust needed"),
                 "COLOSSUS": (-0.5, "v0.111.1 nerf: 4 block"), "CRIMSON_MANTLE": (-0.5, "v0.111.1 nerf: 7 block"),
                 "TAUNT": (-0.5, "v0.111.1 nerf: 6 block")},
    "NECROBINDER": {"TIMES_UP": (+1.0, "v0.111.1: no longer exhausts"), "LEGION_OF_BONE": (+1.0, "v0.111.1: no longer exhausts"),
                    "SACRIFICE": (+1.0, "v0.111.1 buff: 3x Osty max HP"), "SOUL_STORM": (+1.0, "v0.111.1 buff: +4 (6) per card"),
                    "THE_SCYTHE": (+1.0, "v0.111.1 buff: scaling 5 (7)")},
}
REWORKED = {"EIDOLON": "reworked on v0.111.1; old tier ignored", "EXPECT_A_FIGHT": "reworked on v0.111.1 (15 block + 5 per Strength)"}

# Corner targets on arrival at the boss (playbook §2.1).
TARGETS = {1: {"block": 10, "scaling": 2}, 2: {"scaling": 4}, 3: {"block": 8}}
STARTER_DAMAGE = 15  # about the starter deck's damage per turn


def norm(s):
    return re.sub(r"[^A-Z0-9]", "", s.upper())


CARD_BY_NORM = {norm(c["id"]): c for c in dm.CARDS.values()}
CARD_BY_NORM.update({norm(c["name"]): c for c in dm.CARDS.values()})


def resolve(name, character=None):
    """Card name or ID (any case, with or without CARD. prefix) -> extract record."""
    key = norm(name.split(".", 1)[-1] if name.upper().startswith("CARD.") else name)
    c = CARD_BY_NORM.get(key)
    if c is None and character:  # starter cards carry the character suffix (STRIKE_IRONCLAD)
        c = CARD_BY_NORM.get(key + norm(character))
    return c


def expand_deck(items, character):
    deck = []
    for it in items:
        name, _, n = it.replace("*", ":").partition(":")  # NAME:3 (or NAME*3 when quoted)
        c = resolve(name, character)
        if not c:
            raise SystemExit(f"unknown card: {name}")
        deck += ["CARD." + c["id"]] * (int(n) if n else 1)
    return deck


def load_tiers(character):
    path = PROJECT / "knowledge" / "community" / f"{character.lower()}-tiers.md"
    tiers = {}
    if not path.exists():
        return tiers
    for line in path.read_text().splitlines():
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(cells) == 10 and cells[2].startswith("**"):
            tiers[norm(cells[0])] = (cells[2].strip("*"), float(cells[3]), cells[7])
    return tiers


_DP = {}


def decision_point(character):
    """Strong decision-point signals from tools/analyze_card_choices.py: |effect| >= 20 points, p < 0.05, 10+ picks.
    Returns {card_id: (score delta, reason)}. [PLAYER-DATA, weak]"""
    if character in _DP:
        return _DP[character]
    out = {}
    f = PROJECT / "data" / "tables" / f"card_choices_{character.lower()}.csv"
    if f.exists():
        import csv
        for r in _rows(f):
            d, p, n = float(r["survive_diff"]), float(r["p"]), int(r["picked"])
            if abs(d) >= 0.20 and p < 0.05 and n >= 10:
                out[r["card"]] = (0.5 if d > 0 else -0.5,
                                  f"the Player's picks: act survival {d * 100:+.0f} pts vs passing (p={p:.2f}) ({'+' if d > 0 else '-'}0.5)")
    _DP[character] = out
    return out


def display(c):
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", c["name"])


def is_single_hit_aoe(c):
    return "aoe" in c["tags"] and "multi-hit" not in c["tags"]


def boss_fit(c, boss):
    """Context overrides from the playbook, the boss plans and the deck-feature data (the same items as
    tools/deck_check.py BOSS_CHECKS). Returns a list of (delta, reason)."""
    b = (boss or "").upper().replace("ENCOUNTER.", "")
    tags, cost, ctype = c["tags"], c["cost"] if c["cost"] is not None else 9, c["type"]
    attack, power = ctype == "Attack", ctype == "Power"
    out = []

    def add(cond, delta, reason):
        if cond:
            out.append((delta, reason))
    if "VANTOM" in b:
        add(attack and ("multi-hit" in tags or 0 <= cost <= 1) and not is_single_hit_aoe(c), +1.0, "Vantom: cheap or multi-hit attacks clear Slippery")
        add(attack and "multi-hit" in tags and not is_single_hit_aoe(c), +0.5, "Vantom: several Slippery stacks per card (simulation: multi-hit best)")
        add(attack and is_single_hit_aoe(c), -1.0, "Vantom: single-hit hit-all attacks are wasted on Slippery")
        add("draw" in tags, +0.5, "Vantom: draw (survived decks 2.1, fatal 1.0)")
    elif "KNOWLEDGE_DEMON" in b:
        add(power or "strength" in tags or "energy" in tags, +0.5, "Knowledge Demon: scaling and energy (H7)")
    elif "THE_KIN" in b:
        add("aoe" in tags, +0.5, "The Kin: hit-all damage for the followers")
        add(power, +0.5, "The Kin: powers for the longest Act 1 fight")
    elif "CEREMONIAL_BEAST" in b:
        add(attack and (dm.card_numbers("CARD." + c["id"]) or {}).get("dmg", 0) >= 10, +0.5, "Ceremonial Beast: front-loaded damage breaks Plow")
        add("vulnerable" in tags, +0.5, "Ceremonial Beast: Vulnerable (survived 1.2, fatal 0.5)")
    elif "SOUL_FYSH" in b:
        add("exhaust-other" in tags, +0.25, "Soul Fysh: exhaust the Beckon cards (simulated: worth little more than a filler card)")
    elif "WATERFALL_GIANT" in b:
        add("block" in tags, +0.5, "Waterfall Giant: bank block for the death explosion")
    elif "AEONGLASS" in b:
        add(cost == 0 and not power, -0.5, "Aeonglass: Wither every 6 cards; cheap filler costs card plays")
        add("strength" in tags, +0.5, "Aeonglass: Strength (survived 0.8, fatal 0.3)")
        add(attack and "multi-hit" in tags, +0.5, "Aeonglass: damage per card played (multi-hit)")
    elif "QUEEN" in b:
        add("draw" in tags, +0.5, "Queen: draw (survived 3.9, fatal 2.2)")
    elif "KAISER_CRAB" in b:
        add(attack and is_single_hit_aoe(c), -0.5, "Kaiser Crab: focus one claw, not hit-all")
        add("energy" in tags, +0.5, "Kaiser Crab: energy (survived 1.2, fatal 0.6)")
    elif "LAGAVULIN" in b:
        add(power, +0.5, "Lagavulin Matriarch: powers to set up during sleep")
    elif "TEST_SUBJECT" in b:
        add(attack and "multi-hit" in tags, +0.5, "Test Subject: burst on tangible turns (multi-hit)")
    return out


def metrics(deck):
    return {"dmg": dm.simulate(deck, "damage", sims=400), "block": dm.simulate(deck, "block", sims=400),
            "scaling": dm.scaling_count(deck), "size": len(deck)}


def engines(deck):
    ids = {d.split(".", 1)[-1] for d in deck}
    strength = sum(1 for d in deck if "strength" in (dm.CARDS.get(d.split(".", 1)[-1]) or {}).get("tags", []))
    return {"strength": strength >= 2 or "DEMON_FORM" in ids,
            "exhaust": bool(ids & {"FEEL_NO_PAIN", "DARK_EMBRACE", "CORRUPTION"})}


def skip_bar(deck_size):
    """[HYPOTHESIS] A pick must beat C (2.0) in a deck of 15 or fewer, rising 0.1 per card above 15."""
    return 2.0 + 0.1 * max(0, deck_size - 15)


SIM_RUNS = 80


def simulated_boss_value(deck, offer_ids, boss, hp=None, max_hp=80, runs=SIM_RUNS, relics=(), potions=()):
    """For bosses tools/simulate_fight.py models and marks validated (Vantom, Lagavulin Matriarch, Soul Fysh,
    Byrdonis): simulated win rate of the deck and of the deck plus each
    offered card, each deck scored with the better of the planner's two plans (the choice of plan changes results).
    Returns (base rate, {card_id: delta_win}) or None. [HYPOTHESIS] model."""
    import simulate_fight as sf
    key = next((k for k in sf.BOSSES if boss and k in boss.upper() and sf.BOSSES[k].get("validated")), None)
    if not key:
        return None
    start = hp or max_hp

    def rate(d):
        """Win rate plus half the share of the boss's HP removed (separates options when every deck still loses)."""
        best = max((sf.evaluate(d, key, start, max_hp, runs, mode, relics=relics, potions=potions) for mode in ("balanced", "safe")),
                   key=lambda r: (r["win_rate"], r["progress"]))
        return best["win_rate"] + 0.5 * best["progress"], best["win_rate"]
    base, base_win = rate(deck)
    out = {}
    for cid in offer_ids:
        val, _ = rate(deck + [cid])
        out[cid] = val - base
    return base_win, out


def score_offer(deck, offer_ids, character, act, floor, boss, simulate=False, hp=None, max_hp=80, sim_deck=None, sim_relics=(),
                sim_potions=()):
    tiers = load_tiers(character)
    base = metrics(deck)
    eng = engines(deck)
    target = TARGETS.get(act, {})
    rows = []
    for cid in offer_ids:
        c = dm.CARDS.get(cid.split(".", 1)[-1])
        if c is None:  # newer than the game data extract (seen live: NOT_YET on v0.111.1): neutral score, judge by its text
            raw = cid.split(".", 1)[-1]
            rows.append({"card": raw.replace("_", " ").title(), "id": raw, "score": UNKNOWN_TIER,
                         "reasons": ["not in the game data (newer card): neutral score, judge it from the card text"],
                         "d_dmg": 0.0, "d_block": 0.0, "d_scaling": 0})
            continue
        reasons = []
        t = tiers.get(norm(c["name"]))
        if c["id"] in REWORKED:
            s = UNKNOWN_TIER
            reasons.append(REWORKED[c["id"]])
        elif t:
            s = TIER_SCORE[t[0]]
            reasons.append(f"tier {t[0]}" + (" (sources disagree)" if t[2] not in ("-", "0", "1") else ""))
        else:
            s = UNKNOWN_TIER
            reasons.append("no tier data")
        dp = decision_point(character).get(c["id"])
        if dp:
            s += dp[0]; reasons.append(dp[1])
        adj = V0111.get(character, {}).get(c["id"])
        if adj:
            s += adj[0]; reasons.append(f"{adj[1]} ({adj[0]:+g})")
        for delta, why in boss_fit(c, boss):
            s += delta; reasons.append(f"{why} ({delta:+g})")
        after = metrics(deck + [cid])
        d_dmg, d_block, d_scal = after["dmg"] - base["dmg"], after["block"] - base["block"], after["scaling"] - base["scaling"]
        if "block" in target and base["block"] < target["block"] and d_block >= 0.4:
            s += 0.5; reasons.append(f"block {base['block']:.1f} below the act {act} target {target['block']} (+0.5)")
        if "scaling" in target and base["scaling"] < target["scaling"] and d_scal > 0:
            s += 1.0; reasons.append(f"scaling {base['scaling']} below the act {act} target {target['scaling']} (+1)")
        if act == 1 and floor is not None and floor <= 10 and base["dmg"] < STARTER_DAMAGE and d_dmg >= 0.4:
            s += 0.5; reasons.append("early Act 1: damage for the first elites (+0.5)")
        if (base["dmg"] >= STARTER_DAMAGE and c["type"] == "Attack" and d_scal == 0 and d_block < 0.4
                and "block" in target and base["block"] < target["block"]):
            s -= 0.5; reasons.append("raw damage already enough; block is the gap (-0.5)")
        if eng["strength"] and "multi-hit" in c["tags"]:
            s += 1.0; reasons.append("Strength engine: multi-hit payoff (+1)")
        if eng["exhaust"] and "exhaust-other" in c["tags"]:
            s += 1.0; reasons.append("exhaust engine: exhaust outlet (+1)")
        rows.append({"card": display(c), "id": c["id"], "score": round(s, 2), "reasons": reasons,
                     "d_dmg": d_dmg, "d_block": d_block, "d_scaling": d_scal})
    sim = (simulated_boss_value(sim_deck or deck, offer_ids, boss, hp, max_hp, relics=sim_relics, potions=sim_potions)
           if simulate else None)
    if sim:
        base_rate, deltas = sim
        import simulate_fight as sf
        for r in rows:
            if not sf.models_card(r["id"]):
                r["reasons"].append(f"{boss} simulation skipped: the simulator does not model this card's effect")
                continue
            d = deltas.get("CARD." + r["id"], 0.0)
            # +/-0.1 win-equivalent -> +/-1 tier, capped: in the decision-point analysis one tier is worth roughly
            # 10-15 points of act survival (A-tier picks +17, B about 0).
            adj = max(-1.0, min(1.0, 10 * d))
            r["score"] = round(r["score"] + adj, 2)
            r["reasons"].append(f"{boss} simulation: win plus progress {d:+.2f} against the current deck (base win {base_rate:.0%}) ({adj:+.1f})")
    rows.sort(key=lambda r: -r["score"])
    bar = skip_bar(len(deck))
    pick = rows[0] if rows and rows[0]["score"] > bar else None
    return {"base": base, "target": target, "rows": rows, "skip_bar": bar, "pick": pick, "engines": eng}


def from_state(path):
    """STS2-Agent full /state: run.deck[].card_id, reward card options, run.floor, run.boss_id."""
    return from_state_obj(json.loads(Path(path).read_text()))


def deck_ids_from_state(items, upgrades=False):
    """'CARD.<id>' for each deck item of a live state that is a dict with a string card_id; other items are skipped,
    since live states may carry nulls or wrong types. With upgrades, upgraded cards get a '+' suffix."""
    return ["CARD." + d["card_id"] + ("+" if upgrades and d.get("upgraded") is True else "")
            for d in (items if isinstance(items, list) else [])
            if isinstance(d, dict) and isinstance(d.get("card_id"), str) and d["card_id"]]


def sim_deck_from_state(st):
    """The deck for the fight simulator: like from_state_obj's, with '+' on upgraded cards."""
    st = st.get("data", st)
    return deck_ids_from_state((st.get("run") or {}).get("deck"), upgrades=True)


def sim_potions_from_state(st):
    """Potion IDs held (run.potions[] occupied slots) for the fight simulator."""
    st = st.get("data", st)
    return [x.get("potion_id") for x in (st.get("run") or {}).get("potions") or [] if isinstance(x, dict) and x.get("occupied") and x.get("potion_id")]


def sim_relics_from_state(st):
    """Relic IDs from an STS2-Agent state (run.relics[].relic_id, melted ones left out) for the fight simulator."""
    st = st.get("data", st)
    return [r.get("relic_id") for r in (st.get("run") or {}).get("relics") or []
            if isinstance(r, dict) and r.get("relic_id") and not r.get("is_melted")]


def from_state_obj(st):
    st = st.get("data", st)
    run = st.get("run") or {}
    deck = deck_ids_from_state(run.get("deck"))
    rew = st.get("reward") or {}
    opts = rew.get("card_options") or rew.get("cards") or (st.get("selection") or {}).get("cards") or []
    offer = [c.get("card_id") for c in (opts if isinstance(opts, list) else []) if isinstance(c, dict)]
    from stslib import act_number
    act = act_number(run.get("act_id"), default=None) if run.get("act_id") is not None else None  # act_id is 0-based
    return deck, ["CARD." + o for o in offer if isinstance(o, str) and o], act, run.get("floor"), run.get("boss_id")


def guess_character(deck):
    for d in deck:
        c = dm.CARDS.get(d.split(".", 1)[-1])
        if c and c["owner"] in ("Ironclad", "Necrobinder", "Silent", "Regent", "Defect"):
            return c["owner"].upper()
    return "IRONCLAD"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deck", nargs="*", default=[])
    ap.add_argument("--offer", nargs="*", default=[])
    ap.add_argument("--character")
    ap.add_argument("--act", type=int)
    ap.add_argument("--floor", type=int)
    ap.add_argument("--boss")
    ap.add_argument("--from-state")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--simulate", action="store_true", help="for a simulated boss (Vantom): add each card's simulated win-rate change")
    ap.add_argument("--hp", type=int)
    args = ap.parse_args(argv)
    if args.from_state:
        deck, offer, act, floor, boss = from_state(args.from_state)
        act, floor, boss = args.act or act, args.floor or floor, args.boss or boss
        character = (args.character or guess_character(deck)).upper()
    else:
        character = (args.character or "IRONCLAD").upper()
        deck = expand_deck(args.deck, character)
        offer = []
        for o in args.offer:
            c = resolve(o, character)
            if not c:
                raise SystemExit(f"unknown card: {o}")
            offer.append("CARD." + c["id"])
        act, floor, boss = args.act or 1, args.floor, args.boss
    if not offer:
        raise SystemExit("no offered cards")
    res = score_offer(deck, offer, character, act or 1, floor, boss, simulate=args.simulate, hp=args.hp)
    if args.json:
        print(json.dumps(res, indent=1, default=float))
        return 0
    b = res["base"]
    print(f"{character} deck {b['size']} cards · damage/turn {b['dmg']:.1f} · block/turn {b['block']:.1f} · scaling {b['scaling']}"
          f" · act {act} targets {res['target'] or '-'} · boss {boss or '?'}")
    for r in res["rows"]:
        print(f"  {r['score']:5.2f}  {r['card']:<20} dmg {r['d_dmg']:+.1f} block {r['d_block']:+.1f} scaling {r['d_scaling']:+d}"
              f"  | {'; '.join(r['reasons'])}")
    print(f"  {res['skip_bar']:5.2f}  SKIP (bar for a {b['size']}-card deck)")
    p = res["pick"]
    print(f"Recommendation: {'take ' + p['card'] if p else 'skip'}"
          + (f" ({'; '.join(p['reasons'][:3])})" if p else " (nothing beats the skip bar)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
