#!/usr/bin/env python3
"""Upgrade value table for one character, from the extracted card variables and upgrade operations.

The extract lists each card's variables (DamageVar(6m), BlockVar(5m), CardsVar(1), ...) and its upgrade operations
(UpgradeValueBy(3m), AddKeyword(Innate)). Mapping rule [HYPOTHESIS, checked by eye on Ironclad]: with as many
operations as upgradable variables, apply them in order; with fewer, apply to the main variable in this order:
Damage, Block, Energy, Cards, Power, other. HP-loss variables are never the target. Cards with no listed operation
probably upgrade by cost or keyword in ways the extract does not show (Barricade, Corruption, Body Slam...).

Usage: python3 -I tools/build_upgrade_table.py [--owner Ironclad]
Writes knowledge/cards/<owner>-upgrades.md
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import PROJECT, md_table  # noqa: E402

PRIORITY = ["Damage", "Block", "Energy", "Cards", "Power", "Repeat", "MaxHp"]


def spaced(name):
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", name)


def parse_vars(s):
    out = []
    for m in re.finditer(r"(\w+?)Var(?:<(\w+)>)?\((?:\"(\w+)\",\s*)?([\d.]+)m?", s or ""):
        kind, power, dyn, val = m.group(1), m.group(2), m.group(3), float(m.group(4))
        label = power.replace("Power", "") if power else (dyn or kind)
        out.append({"kind": kind, "label": label, "value": val})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", default="Ironclad")
    args = ap.parse_args()
    cards = [c for c in json.loads((PROJECT / "knowledge/data/extract-2026-09-21/cards.json").read_text()) if c["owner"] == args.owner]
    rows = []
    for c in sorted(cards, key=lambda c: c["name"]):
        vars_ = [v for v in parse_vars(c["vars"]) if v["kind"] not in ("HpLoss", "Calculation", "CalculationBase", "CalculationExtra", "CalculatedDamage")]
        ups = [float(x) for x in re.findall(r"UpgradeValueBy\(([\d.]+)m?\)", c["on_upgrade"] or "")]
        kws = re.findall(r"AddKeyword\((\w+)\)", c["on_upgrade"] or "")
        changes = []
        if ups:
            if len(ups) >= len(vars_):
                targets = vars_
            else:
                ordered = sorted(vars_, key=lambda v: next((i for i, p in enumerate(PRIORITY) if v["kind"].startswith(p)), 99))
                targets = ordered[: len(ups)]
            for v, d in zip(targets, ups):
                pct = f" (+{100 * d / v['value']:.0f}%)" if v["value"] else ""
                note = ""
                others = [o for o in vars_ if o is not v and o not in targets]
                if len(ups) < len(vars_) and not v["kind"].startswith(("Damage", "Block")) and others:
                    note = " (ambiguous: or " + ", ".join(f"{o['label']} +{d:g}" for o in others) + ")"
                changes.append(f"{v['label']} {v['value']:g} → {v['value'] + d:g}{pct}{note}")
        for k in kws:
            changes.append(f"gains {k}")
        if not changes and c["on_upgrade"]:
            changes.append(c["on_upgrade"])
        rows.append([spaced(c["name"]), c["cost"] if c["cost"] is not None and c["cost"] >= 0 else "X", c["type"], c["rarity"],
                     "; ".join(changes) if changes else "not in the extract (probably a cost or text change)"])
    L = [f"# {args.owner} Upgrades", "",
         "Built by `tools/build_upgrade_table.py` from the extracted card data `[GAME-EXTRACT]`. The mapping of upgrade "
         "operations to variables is a heuristic (see the script header) and needs checking in game. "
         "\"Not in the extract\" usually means the upgrade lowers the cost or changes the text, which the extract does not record.", "",
         md_table(["Card", "Cost", "Type", "Rarity", "Upgrade"], rows), ""]
    out = PROJECT / f"knowledge/cards/{args.owner.lower()}-upgrades.md"
    out.write_text("\n".join(L))
    print(f"wrote {out.relative_to(PROJECT)} ({len(rows)} cards)")


if __name__ == "__main__":
    main()
