#!/usr/bin/env python3
"""Deck check before a boss and at each act start (P4.E3.S4): measure the deck against the corner targets
(playbook section 2.1, H9) and the boss plan's checklist items that can be counted from card data.

Counts use card values for v0.111.1 (knowledge/data/card-patches.json). Each check prints OK or GAP with the
number found, so the journal can record the gaps and the plan to close them.

Usage:
  python3 -I tools/deck_check.py --deck STRIKE_IRONCLAD:4 DEFEND_IRONCLAD:4 BASH TWIN_STRIKE INFLAME --act 1 --boss VANTOM
  python3 -I tools/deck_check.py --state state.json          (STS2-Agent full state: deck, act, boss)
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import draft  # noqa: E402  (applies the v0.111.1 card patches)

dm = draft.dm


def card(cid):
    return dm.CARDS.get(cid.split(".", 1)[-1]) or {}


def count(deck, pred):
    return sum(1 for d in deck if pred(card(d)))


def is_attack(c):
    return c.get("type") == "Attack"


def cheap(c):
    return c.get("cost") is not None and 0 <= c["cost"] <= 1


# Boss checklist items that can be counted (from knowledge/bosses/*.md "Deck checklist"). [HYPOTHESIS] thresholds.
# Death review (reports/phase2/death-review-ironclad.md): these flagged 38% of fatal and 38% of survived Ironclad boss
# fights, so as thresholded they do not discriminate yet. The corner targets (H9) did: 88% against 69%.
BOSS_CHECKS = {
    "VANTOM": [
        ("cheap (0-1 cost) or multi-hit attack cards", lambda d: count(d, lambda c: is_attack(c) and ("multi-hit" in c.get("tags", []) or cheap(c))), 6,
         "9 Slippery stacks; each hit removes one, Strikes count"),
        ("single-hit hit-all attacks", lambda d: count(d, lambda c: is_attack(c) and draft.is_single_hit_aoe(c)), -1,
         "wasted on Slippery; fatal Vantom decks had more (H2)"),
    ],
    "KNOWLEDGE_DEMON": [
        ("scaling cards (powers, Strength, energy)", lambda d: count(d, lambda c: c.get("type") == "Power" or "strength" in c.get("tags", []) or "energy" in c.get("tags", [])), 4,
         "about 60 damage per turn over 7 turns (H7)"),
    ],
    "THE_KIN": [("hit-all attacks", lambda d: count(d, lambda c: is_attack(c) and "aoe" in c.get("tags", [])), 2, "followers stack Strength")],
    "CEREMONIAL_BEAST": [("attacks dealing 10+ damage", lambda d: count(d, lambda c: is_attack(c) and (dm.card_numbers("CARD." + c["id"]) or {}).get("dmg", 0) >= 10), 3,
                          "front-load 150 damage to trigger Plow's stun")],
    "SOUL_FYSH": [("exhaust outlets", lambda d: count(d, lambda c: "exhaust-other" in c.get("tags", [])), 1, "exhaust the Beckon cards (unblockable HP loss)")],
    "WATERFALL_GIANT": [("block cards", lambda d: count(d, lambda c: "block" in c.get("tags", [])), 6, "bank block for the death explosion")],
    "KAISER_CRAB": [("single-target attacks", lambda d: count(d, lambda c: is_attack(c) and c.get("target") == "AnyEnemy"), 6, "focus one claw (Rocket)")],
    "THE_INSATIABLE": [("energy or draw cards", lambda d: count(d, lambda c: "energy" in c.get("tags", []) or "draw" in c.get("tags", [])), 2, "play the Frantic Escape cards and still fight")],
    "AEONGLASS": [("zero-cost non-power cards", lambda d: count(d, lambda c: c.get("cost") == 0 and c.get("type") != "Power"), -3, "each card played counts toward Wither (every 6 cards)")],
    "QUEEN": [("draw cards", lambda d: count(d, lambda c: "draw" in c.get("tags", [])), 2, "You're Mine: 99 Weak, Vulnerable, Frail")],
    "LAGAVULIN_MATRIARCH": [("powers to set up during sleep", lambda d: count(d, lambda c: c.get("type") == "Power"), 2, "use the sleep turns")],
    "TEST_SUBJECT": [("block cards", lambda d: count(d, lambda c: "block" in c.get("tags", [])), 7, "phase 2 needs full block; 45-damage Big Pounce")],
}


def check(deck, act, boss):
    out = []
    mt = draft.metrics(deck)
    tgt = draft.TARGETS.get(act, {})
    out.append(f"Deck {mt['size']} cards · damage/turn {mt['dmg']:.1f} · block/turn {mt['block']:.1f} · scaling {mt['scaling']}")
    for k, v in tgt.items():
        have = mt["block"] if k == "block" else mt["scaling"]
        out.append(f"  {'OK ' if have >= v else 'GAP'}  {k} {have:.1f} (act {act} target {v}, H9)")
    if mt["dmg"] < draft.STARTER_DAMAGE and mt["scaling"] < 2:
        out.append(f"  GAP  damage/turn {mt['dmg']:.1f} below the starter's {draft.STARTER_DAMAGE} without scaling to replace it")
    key = next((k for k in BOSS_CHECKS if boss and k in boss.upper()), None)
    if key:
        out.append(f"Boss checklist: {key} (knowledge/bosses/{key}_BOSS.md)")
        for label, fn, need, why in BOSS_CHECKS[key]:
            have = fn(deck)
            ok = have <= -need if need < 0 else have >= need
            bound = f"at most {-need}" if need < 0 else f"at least {need}"
            out.append(f"  {'OK ' if ok else 'GAP'}  {label}: {have} ({bound}; {why})")
    elif boss:
        out.append(f"No countable checklist for {boss}; read its boss note.")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deck", nargs="*", default=[])
    ap.add_argument("--act", type=int)
    ap.add_argument("--boss")
    ap.add_argument("--character", default="IRONCLAD")
    ap.add_argument("--state")
    args = ap.parse_args(argv)
    if args.state:
        deck, _, act, _, boss = draft.from_state(args.state)
        act, boss = args.act or act or 1, args.boss or boss
    else:
        deck, act, boss = draft.expand_deck(args.deck, args.character.upper()), args.act or 1, args.boss
    print(check(deck, act, boss))
    return 0


if __name__ == "__main__":
    sys.exit(main())
