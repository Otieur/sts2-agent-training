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


def tagged(tag):
    return lambda d: count(d, lambda c: tag in c.get("tags", []))


def attacks_with(pred):
    return lambda d: count(d, lambda c: is_attack(c) and pred(c))


STRENGTH = tagged("strength")
ENERGY = tagged("energy")
DRAW = tagged("draw")
POWERS = lambda d: count(d, lambda c: c.get("type") == "Power")  # noqa: E731
MULTI = attacks_with(lambda c: "multi-hit" in c.get("tags", []))
SINGLE_AOE = attacks_with(draft.is_single_hit_aoe)
HIT_ALL = attacks_with(lambda c: "aoe" in c.get("tags", []))
VULN = tagged("vulnerable")

# Boss checklist items that can be counted. Re-tuned 2026-11-19 from reports/phase2/deck-features-by-encounter.md
# (survived against fatal deck means, all characters, v0.107.1), keeping only features where the data and the
# boss's mechanics agree, with thresholds near the midpoint. Fatal samples are 4-13 per boss: [HYPOTHESIS].
# The first version (pure guesses) flagged 38% of fatal and 38% of survived Ironclad boss fights; this version flags 62%
# against 39% (reports/phase2/death-review-ironclad.md), measured on overlapping data, so the gain is optimistic.
BOSS_CHECKS = {
    "VANTOM": [
        ("single-hit hit-all attacks", SINGLE_AOE, 0, "wasted on Slippery; survived decks 0.3, fatal 0.8"),
        ("draw cards", DRAW, 2, "finds the cheap attacks; survived 2.1, fatal 1.0"),
    ],
    "KNOWLEDGE_DEMON": [
        ("Strength cards", STRENGTH, 1, "survived 0.7, fatal 0.2 (H7)"),
        ("energy cards", ENERGY, 1, "survived 1.6, fatal 0.8 (H7)"),
    ],
    "AEONGLASS": [
        ("Strength cards", STRENGTH, 1, "fewer, bigger hits against Wither; survived 0.8, fatal 0.3"),
        ("multi-hit attacks", MULTI, 1, "damage per card played; survived 1.7, fatal 0.8"),
    ],
    "QUEEN": [("draw cards", DRAW, 3, "You're Mine: 99 Weak, Vulnerable, Frail; survived 3.9, fatal 2.2")],
    "TEST_SUBJECT": [("multi-hit attacks", MULTI, 1, "burst on tangible turns; survived 1.3, fatal 0.6")],
    "CEREMONIAL_BEAST": [("Vulnerable sources", VULN, 1, "front-load 150 damage to trigger Plow; survived 1.2, fatal 0.5")],
    "THE_KIN": [("powers", POWERS, 1, "the longest Act 1 fight; survived 1.0, fatal 0.4"),
                ("hit-all attacks", HIT_ALL, 1, "followers stack Strength (plan)")],
    "KAISER_CRAB": [("single-hit hit-all attacks", SINGLE_AOE, -1, "focus one claw; survived 0.7, fatal 1.4"),
                    ("energy cards", ENERGY, 1, "survived 1.2, fatal 0.6")],
    "LAGAVULIN_MATRIARCH": [("powers to set up during sleep", POWERS, 1, "survived 0.9, fatal 0.5")],
    "SOUL_FYSH": [("exhaust outlets", tagged("exhaust-other"), 1, "exhaust the Beckon cards (plan; no data signal; simulated value small)")],
    "WATERFALL_GIANT": [("block cards", tagged("block"), 6, "bank block for the death explosion (plan; no data signal)")],
    "THE_INSATIABLE": [("energy or draw cards", lambda d: count(d, lambda c: "energy" in c.get("tags", []) or "draw" in c.get("tags", [])), 2,
                        "play the Frantic Escape cards and still fight (plan; no data signal)")],
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
            if need <= 0:  # 0 or negative: an upper bound ("at most -need")
                ok, bound = have <= -need, f"at most {-need}"
            else:
                ok, bound = have >= need, f"at least {need}"
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
