#!/usr/bin/env python3
"""Build a readable card reference for one character from the extracted game data, joined with the
Player's pick statistics (Phase 1). Output: knowledge/cards/<character>.md

Usage: python3 -I tools/build_card_reference.py [--character IRONCLAD] [--owner Ironclad]
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import PROJECT, md_table, pct  # noqa: E402


def _rows(path):
    """CSV rows from a file that is closed straight away (avoids unclosed handles)."""
    import csv as _csv
    with open(path, newline="") as fh:
        return list(_csv.DictReader(fh))

EXTRACT = PROJECT / "knowledge/data/extract-2026-09-21"
import re


def spaced(name):
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", name)


RARITY_ORDER = {"Basic": 0, "Common": 1, "Uncommon": 2, "Rare": 3, "Ancient": 4}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", default="IRONCLAD")
    ap.add_argument("--owner", default=None, help="owner name in the extract (defaults to the character, title case)")
    args = ap.parse_args()
    ch = args.character.upper()
    owner = args.owner or ch.title()
    import deck_metrics  # noqa: E402  (card values brought to the target game version)
    deck_metrics.apply_patches("v0.111.1")
    cards = [c for c in deck_metrics.CARDS.values() if c["owner"] == owner]

    picks, ranks = {}, {}
    pfile = PROJECT / f"reports/phase1/card-picks-{ch.lower()}.csv"
    rfile = PROJECT / f"reports/phase1/card-ranking-{ch.lower()}.csv"
    if pfile.exists():
        for r in _rows(pfile):
            picks[r["card"]] = (int(r["offered"]), int(r["picked"]))
    if rfile.exists():
        for r in _rows(rfile):
            ranks[r["card"]] = (float(r["strength"]), int(r["comparisons"]))
    skip = ranks.get("SKIP", (None, 0))[0]

    def row(c):
        off, pk = picks.get(c["id"], (0, 0))
        s, n = ranks.get(c["id"], (None, 0))
        cost = "X" if "x-cost" in c["tags"] else ("—" if c["cost"] is not None and c["cost"] < 0 else c["cost"])
        rank = "-" if s is None or n < 5 else (f"{s:+.2f}" + (" ▲" if skip is not None and s > skip else " ▼"))
        mark = f" **[{c['patched']}]**" if c.get("patched") else ""
        return [spaced(c["name"]) + mark, cost, c["type"], c["rarity"], (c["effect"] or "").replace("|", "/"),
                ", ".join(t for t in c["tags"] if not t.startswith("kw-")) or "-",
                f"{pk}/{off}" if off else "-", pct(pk / off) if off else "-", rank]

    cards.sort(key=lambda c: (RARITY_ORDER.get(c["rarity"], 9), c["type"] or "", c["name"]))
    L = [f"# {owner} Cards", "",
         "Source: `knowledge/data/extract-2026-09-21/cards.json` `[GAME-EXTRACT]` (decompiled game data, build not "
         "stated; it predates v0.107.1), with the card changes of v0.107.1 and v0.111.1 applied from "
         "`knowledge/data/card-patches.json` (marked **[v0.107.1]** or **[v0.111.1]**), so values are for v0.111.1. "
         "Numbers are base values; `?` is computed at play time. "
         "Picked/offered and the head-to-head score come from the Player's card reward screens (Phase 1, v0.107.1) "
         "`[PLAYER-DATA]` and describe habit, not strength. ▲ = scored above skipping, ▼ = below.", "",
         "Tags are derived from the effect text by `tools/import_extract.py` (multi-hit, aoe, zero-cost, x-cost, "
         "draw, energy, block, strength, vulnerable, weak, self-damage, exhaust-other, power, upgrade).", ""]
    for rarity in ("Basic", "Common", "Uncommon", "Rare", "Ancient"):
        sub = [c for c in cards if c["rarity"] == rarity]
        if not sub:
            continue
        L += [f"## {rarity} ({len(sub)})", "",
              md_table(["Card", "Cost", "Type", "Rarity", "Effect (base)", "Roles", "Picked", "Pick rate", "Player score"],
                       [row(c) for c in sub]), ""]
    other = [c for c in cards if c["rarity"] not in RARITY_ORDER]
    if other:
        L += ["## Other", "", md_table(["Card", "Cost", "Type", "Rarity", "Effect (base)", "Roles", "Picked", "Pick rate",
                                        "Player score"], [row(c) for c in other]), ""]

    # Role summaries used by playbook hypotheses
    def names(tag):
        return [c for c in cards if tag in c["tags"] and c["rarity"] != "Basic"]
    L += ["## Role index", ""]
    for tag, title in (("multi-hit", "Multi-hit attacks"), ("aoe", "Hits all enemies"),
                       ("zero-cost", "0-cost cards"), ("x-cost", "X-cost cards"), ("draw", "Card draw"),
                       ("energy", "Energy"), ("strength", "Strength"), ("vulnerable", "Applies Vulnerable"),
                       ("weak", "Applies Weak"), ("self-damage", "Costs HP"), ("power", "Powers")):
        cs = names(tag)
        if cs:
            items = []
            for c in cs:
                off, pk = picks.get(c["id"], (0, 0))
                items.append(f"{spaced(c['name'])} ({pk}/{off})" if off else spaced(c["name"]))
            L.append(f"- **{title}:** " + ", ".join(items))
    L.append("")
    out = PROJECT / f"knowledge/cards/{ch.lower()}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L))
    print(f"{owner}: {len(cards)} cards -> {out.relative_to(PROJECT)}")


if __name__ == "__main__":
    main()
