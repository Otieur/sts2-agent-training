#!/usr/bin/env python3
"""Import the STS2-Agent decompiled game-knowledge index into structured JSON with role tags.

Source: vendor/STS2-Agent/docs/game-knowledge/*.md (generated 2026-09-21 from decompiled game data by
the STS2-Agent project; the build may differ from v0.107.1). Output is labelled [GAME-EXTRACT].

Writes knowledge/data/extract-2026-09-21/{cards,monsters,relics,potions,powers,events,characters}.json
and a README with provenance.

Usage: python3 -I tools/import_extract.py [--src vendor/STS2-Agent/docs/game-knowledge]
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import PROJECT  # noqa: E402

DEFAULT_SRC = PROJECT / "vendor/STS2-Agent/docs/game-knowledge"
OUT = PROJECT / "knowledge/data/extract-2026-09-21"


def to_id(name):
    """CamelCase class name -> UPPER_SNAKE id as used in run files (AshenStrike -> ASHEN_STRIKE)."""
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name)
    return s.upper()


def parse_tables(path):
    """Return a list of tables, each a list of dicts keyed by the header row."""
    tables, header, rows = [], None, []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if header is None:
                header = cells
            elif set("".join(cells)) <= set("-: "):
                continue
            else:
                rows.append(dict(zip(header, cells)))
        else:
            if header is not None:
                tables.append(rows)
            header, rows = None, []
    if header is not None:
        tables.append(rows)
    return tables


def num(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def card_tags(c):
    e = c.get("Effect", "")
    t = set()
    cost = num(c.get("Cost"))
    playable_type = c.get("Type") in ("Attack", "Skill", "Power")
    if "X (energy spent)" in e or " X " in e or (cost is not None and cost < 0 and playable_type):
        t.add("x-cost")  # the extract records X-cost cards such as Cascade with cost -1
    elif cost == 0:
        t.add("zero-cost")
    if cost is not None and cost < 0 and not playable_type:
        t.add("unplayable")
    if re.search(r"damage (\d+|\?|X[^;]*) times", e):
        t.add("multi-hit")
    if "ALL enemies" in e or c.get("Target") == "AllEnemies":
        t.add("aoe")
    if c.get("Target") == "RandomEnemy":
        t.add("random-target")
    if "Deal" in e and "damage" in e:
        t.add("damage")
    if "Block" in e:
        t.add("block")
    if re.search(r"Draw \d+|Draw \?|Put a card into your hand", e):
        t.add("draw")
    if re.search(r"Gain (\d+|\?) Energy", e):
        t.add("energy")
    if "Strength" in e:
        t.add("strength")
    if "Vulnerable" in e:
        t.add("vulnerable")
    if "Weak" in e:
        t.add("weak")
    if re.search(r"Lose \d+ HP|Lose \? HP", e):
        t.add("self-damage")
    if "Exhaust a card" in e or "Exhaust " in e.split("keywords:")[0]:
        t.add("exhaust-other")
    kw = e.split("keywords:")[1] if "keywords:" in e else ""
    for k in ("Exhaust", "Ethereal", "Innate", "Retain", "Unplayable", "Eternal", "Sly"):
        if k in kw:
            t.add("kw-" + k.lower())
    if c.get("Type") == "Power":
        t.add("power")
    if "Upgrade a card" in e:
        t.add("upgrade")
    if "HP" in e and ("Heal" in e or "heal" in e):
        t.add("heal")
    return sorted(t)


def split_moves(s):
    moves = []
    for part in [p.strip() for p in s.split("; ") if p.strip()]:
        m = re.match(r"([A-Z0-9_]+)=(.*?)(?: -> (.*))?$", part)
        if m:
            moves.append({"move": m.group(1), "intent": m.group(2), "effect": m.group(3) or ""})
        else:
            moves.append({"move": None, "intent": None, "effect": part})
    return moves


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC)
    args = ap.parse_args()
    src = args.src
    if not src.exists():
        raise SystemExit(f"{src} not found (clone STS2-Agent into vendor/ first)")
    OUT.mkdir(parents=True, exist_ok=True)

    cards = {r["Name"]: r for r in parse_tables(src / "cards.md")[0]}
    beh = {r["Name"]: r for r in parse_tables(src / "card-behaviors.md")[0]}
    out_cards = []
    for name, c in cards.items():
        b = beh.get(name, {})
        rec = {"id": to_id(name), "name": name, "cost": num(c.get("Cost")), "type": c.get("Type"),
               "rarity": c.get("Rarity"), "target": c.get("Target"), "owner": c.get("Owner"),
               "effect": c.get("Effect"), "vars": b.get("Vars"), "on_play": b.get("OnPlay"),
               "on_upgrade": b.get("OnUpgrade")}
        rec["tags"] = card_tags(c)
        out_cards.append(rec)

    mons = {r["Name"]: r for r in parse_tables(src / "monsters.md")[0]}
    mbeh = {r["Name"]: r for r in parse_tables(src / "monster-behaviors.md")[0]}
    out_mons = []
    for name in sorted(set(mons) | set(mbeh)):
        m, b = mons.get(name, {}), mbeh.get(name, {})
        out_mons.append({"id": to_id(name), "name": name, "min_hp": num(m.get("MinHp")), "max_hp": num(m.get("MaxHp")),
                         "moves": split_moves(b.get("Moves", "")), "passive": b.get("Passive", "")})

    def simple(fname, keymap):
        rows = parse_tables(src / fname)[0]
        return [{"id": to_id(r["Name"]), **{k: r.get(v) for k, v in keymap.items()}} for r in rows]

    relics = simple("relics.md", {"name": "Name", "rarity": "Rarity", "owner": "Owner", "effect": "Effect"})
    powers = simple("powers.md", {"name": "Name", "type": "Type", "stack_type": "StackType", "hook": "Hook", "effect": "Effect"})
    pot = {r["Name"]: r for r in parse_tables(src / "potions.md")[0]}
    pbeh_tables = parse_tables(src / "potion-behaviors.md")
    pbeh = {r["Name"]: r for r in pbeh_tables[0]} if pbeh_tables else {}
    potions = [{"id": to_id(n), "name": n, "rarity": r.get("Rarity"), "usage": r.get("Usage"), "target": r.get("Target"),
                "behavior": {k: v for k, v in pbeh.get(n, {}).items() if k != "Name"}} for n, r in pot.items()]
    ev_tables = parse_tables(src / "events.md")
    events = [{"id": to_id(r["Name"]), **{k.lower(): v for k, v in r.items()}} for r in ev_tables[0]]
    event_options = [dict(r) for t in ev_tables[1:] for r in t]
    chars = [{"id": to_id(r["Name"]), **{k.lower(): v for k, v in r.items()}} for r in parse_tables(src / "characters.md")[0]]

    files = {"cards": out_cards, "monsters": out_mons, "relics": relics, "potions": potions, "powers": powers,
             "events": events, "event_options": event_options, "characters": chars}
    for k, v in files.items():
        (OUT / f"{k}.json").write_text(json.dumps(v, indent=1, ensure_ascii=False) + "\n")
    (OUT / "README.md").write_text(
        "# Extracted game data (2026-09-21)\n\n"
        "Label: `[GAME-EXTRACT]`. Parsed by `tools/import_extract.py` from the STS2-Agent project's "
        "`docs/game-knowledge` index (vendor/STS2-Agent, commit 5d7c306), which that project generated on "
        "2026-09-21 from decompiled game data. The game build behind it is not stated; the project targeted "
        "v0.111.0 (beta) at the time, so numbers may differ from v0.107.1. Verify against the live game's "
        "`/data` export in Phase 2 before treating anything as `[GAME]`.\n\n"
        "Numbers are base (unupgraded, non-ascension) values. `?` means computed at play time.\n\n"
        "| File | Records |\n|---|---|\n" + "".join(f"| {k}.json | {len(v)} |\n" for k, v in files.items()) +
        "\nCard `tags` are derived by keyword rules in the importer (multi-hit, aoe, zero-cost, x-cost, draw, "
        "energy, block, strength, vulnerable, weak, self-damage, exhaust-other, power, kw-*). They are a "
        "convenience, not game data.\n")
    print({k: len(v) for k, v in files.items()})


if __name__ == "__main__":
    main()
