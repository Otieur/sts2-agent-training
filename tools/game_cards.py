#!/usr/bin/env python3
"""Card facts from the game's own code, compared with our card data.

Reads the IL of every class in MegaCrit.Sts2.Core.Models.Cards (through tools/asm/asm.cs, runtime libraries only) and
extracts, per card: energy cost, type, rarity, target, the canonical values (DamageVar, BlockVar, PowerVar<X>, ...) and
the upgrade amounts. Compares them with knowledge/data/extract-2026-09-21/cards.json after card-patches.json, and
writes reports/game-check/cards.md. Run it after every game update (docs/runbooks/game-patch.md).

    python3 -I tools/game_cards.py            # dump IL (about 20 s), compare, write the report
    python3 -I tools/game_cards.py --cached   # reuse data/asm/cards-il.txt

Labels: values read here are [GAME] for the installed build (data/asm/ is not in git: it describes the game's code).
Limits: values set outside get_CanonicalVars (calculated damage, hit counts in OnPlay) are not read; the comparison
covers cost, type, rarity, target, canonical values and upgrade amounts.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "tools"))
import deck_metrics as dm  # noqa: E402

GAME_DATA = Path.home() / "Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64"
IL = PROJECT / "data" / "asm" / "cards-il.txt"
OUT_JSON = PROJECT / "data" / "asm" / "cards-game.json"
REPORT = PROJECT / "reports" / "game-check" / "cards.md"
FACTS_DIR = PROJECT / "knowledge" / "data"  # game-cards-<version>.json: the facts tools/plan_turn.py reads
EXTRACT = PROJECT / "knowledge" / "data" / "extract-2026-09-21" / "cards.json"
NS = "MegaCrit.Sts2.Core.Models.Cards."
TYPES = {0: "None", 1: "Attack", 2: "Skill", 3: "Power", 4: "Status", 5: "Curse", 6: "Quest"}
RARITIES = {0: "None", 1: "Basic", 2: "Common", 3: "Uncommon", 4: "Rare", 5: "Ancient", 6: "Event", 7: "Token", 8: "Status",
            9: "Curse", 10: "Quest"}
TARGETS = {0: "None", 1: "Self", 2: "AnyEnemy", 3: "AllEnemies", 4: "RandomEnemy", 5: "AnyPlayer", 6: "AnyAlly", 7: "AllAllies",
           8: "TargetedNoCreature", 9: "Osty"}


def game_build():
    try:
        info = json.loads((GAME_DATA.parent / "release_info.json").read_text())
        return f"{info.get('version', '?')} {str(info.get('commit', ''))[:8]}".strip()
    except Exception:
        return "unknown build"


def dump_il():
    IL.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["dotnet", "run", "tools/asm/asm.cs", "--", "il", str(GAME_DATA / "sts2.dll"), NS], cwd=PROJECT,
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0 or "### " not in r.stdout:
        sys.exit(f"could not read the game assembly: {r.stderr[-400:]}")
    IL.write_text(r.stdout)


def snake(name):
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name)
    return s.upper()


def const(op):
    """Integer loaded by an ldc.i4 instruction, or None."""
    m = re.match(r"ldc\.i4(?:\.s)? (-?\d+)$", op)
    if m:
        return int(m.group(1))
    m = re.match(r"ldc\.i4\.(m1|\d)$", op)
    if m:
        return -1 if m.group(1) == "m1" else int(m.group(1))
    return None


def parse_methods(text):
    """{class: {method: [instruction text, ...]}} for top-level card classes (nested state machines keyed 'Class+Nested')."""
    out, cur = {}, None
    for line in text.splitlines():
        if line.startswith("### "):
            full = line[4:]
            cls, _, meth = full.partition("::")
            cur = out.setdefault(cls[len(NS):] if cls.startswith(NS) else cls, {}).setdefault(meth, [])
        elif cur is not None and line.startswith("  "):
            cur.append(line.strip().split(" ", 1)[1] if " " in line.strip() else "")
    return out


def decimals_and_vars(ins):
    """Walk get_CanonicalVars: returns [(var type, name or None, value)]."""
    res, ints, dec, name = [], [], None, None
    for op in ins:
        c = const(op)
        if c is not None:
            ints.append(c)
        elif op == "dup":
            ints = []
        elif op.startswith("ldstr str:"):
            name = op[len("ldstr str:"):]
        elif op.startswith("ldsfld f:System.Decimal::"):
            dec = {"One": 1, "Zero": 0, "MinusOne": -1}.get(op.rsplit("::", 1)[1])
            ints = []
        elif op.startswith("newobj new:System.Decimal::.ctor"):
            if len(ints) >= 5:
                lo, _mid, _hi, neg, scale = ints[-5:]
                dec = (-lo if neg else lo) / (10 ** scale)
            elif ints:
                dec = ints[-1]
            ints = []
        elif op.startswith("newobj new:") and "DynamicVars." in op and "::.ctor" in op and "z__ReadOnly" not in op:
            vt = op[len("newobj new:"):].split("::")[0].split("DynamicVars.", 1)[-1]
            vt = re.sub(r"MegaCrit\.Sts2\.Core\.[A-Za-z.]+\.", "", vt).replace("`1", "")
            val = dec if dec is not None else (ints[-1] if ints else None)
            res.append((vt, name, val))
            ints, dec, name = [], None, None
    return res


def upgrades(ins):
    """Walk OnUpgrade: [(what, amount)] for UpgradeValueBy and energy cost changes; plus keyword changes."""
    res, ints, dec, target = [], [], None, None
    for op in ins:
        c = const(op)
        if c is not None:
            ints.append(c)
        elif op.startswith("ldstr str:"):
            target = op[len("ldstr str:"):]
        elif "DynamicVarSet::get_" in op and "get_Item" not in op:
            target = op.rsplit("get_", 1)[1]
            ints, dec = [], None
        elif op.startswith("ldsfld f:System.Decimal::"):
            dec = {"One": 1, "Zero": 0, "MinusOne": -1}.get(op.rsplit("::", 1)[1])
        elif op.startswith("newobj new:System.Decimal::.ctor"):
            if len(ints) >= 5:
                lo, _mid, _hi, neg, scale = ints[-5:]
                dec = (-lo if neg else lo) / (10 ** scale)
            elif ints:
                dec = ints[-1]
            ints = []
        elif op.endswith("DynamicVar::UpgradeValueBy"):
            res.append((target or "?", dec if dec is not None else (ints[-1] if ints else None)))
            ints, dec, target = [], None, None
        elif "CardEnergyCost::UpgradeBy" in op or "EnergyCost::UpgradeBy" in op:
            res.append(("EnergyCost", ints[-1] if ints else None))
            ints = []
        elif "AddKeyword" in op or "RemoveKeyword" in op:
            res.append((op.rsplit("::", 1)[1], ints[-1] if ints else None))
            ints = []
    return res


def game_cards(text):
    cards = {}
    for cls, methods in parse_methods(text).items():
        if "+" in cls or "." in cls or ".ctor" not in methods:
            continue  # nested helper types and sub-namespaces (Mocks)
        ctor = methods[".ctor"]
        ints = []
        for op in ctor:
            c = const(op)
            if c is not None:
                ints.append(c)
            elif "CardModel::.ctor" in op:
                break
        else:
            continue  # does not call the CardModel constructor directly (inherits from another card)
        if len(ints) < 4:
            continue
        cost, typ, rarity, target = ints[-5:-1] if len(ints) >= 5 else ints[-4:]
        cards[snake(cls)] = {
            "class": cls, "cost": cost, "type": TYPES.get(typ, typ), "rarity": RARITIES.get(rarity, rarity),
            "target": TARGETS.get(target, target), "vars": decimals_and_vars(methods.get("get_CanonicalVars", [])),
            "upgrade": upgrades(methods.get("OnUpgrade", [])),
        }
    return cards


def extract_vars(s):
    """'DamageVar(8m, ValueProp.Move), PowerVar<VulnerablePower>(2m)' -> [('DamageVar', 8.0), ('PowerVar<VulnerablePower>', 2.0)]"""
    out = []
    for m in re.finditer(r"([A-Za-z]+(?:<[A-Za-z]+>)?)\(([^()]*)\)", s or ""):
        num = re.search(r"(-?\d+(?:\.\d+)?)m?\b", m.group(2))
        out.append((m.group(1), float(num.group(1)) if num else None))
    return out


def norm_vars(vs):
    return sorted((re.sub(r"\s", "", t), None if v is None else float(v)) for t, v in vs)


def compare(cards):
    dm.apply_patches(dm.MAIN_BUILD if hasattr(dm, "MAIN_BUILD") else "v0.111.1")
    ours = {(c.get("id") or k).replace("CARD.", ""): c for k, c in dm.CARDS.items()}
    rows, missing_in_ours, missing_in_game = [], [], []
    for cid, g in sorted(cards.items()):
        o = ours.get(cid)
        if o is None:
            missing_in_ours.append((cid, g))
            continue
        diffs = []
        if o.get("cost") is not None and str(o.get("cost")) not in ("", "X") and int(o["cost"]) != g["cost"]:
            diffs.append(f"cost: ours {o['cost']}, game {g['cost']}")
        if o.get("type") and o["type"] != g["type"]:
            diffs.append(f"type: ours {o['type']}, game {g['type']}")
        if o.get("target") and o["target"] != g["target"]:
            diffs.append(f"target: ours {o['target']}, game {g['target']}")
        if o.get("rarity") and o["rarity"] != g["rarity"]:
            diffs.append(f"rarity: ours {o['rarity']}, game {g['rarity']}")
        gv = norm_vars([(t if t != "DynamicVar" else f"DynamicVar:{n}", v) for t, n, v in g["vars"]])
        ov = norm_vars([(t if t != "DynamicVar" else "DynamicVar:?", v) for t, v in extract_vars(o.get("vars"))])
        gcmp = sorted((re.sub(r"DynamicVar:.*", "DynamicVar", t), v) for t, v in gv)
        ocmp = sorted((re.sub(r"DynamicVar:.*", "DynamicVar", t), v) for t, v in ov)
        if gcmp != ocmp:
            only_g = [x for x in gcmp if x not in ocmp]
            only_o = [x for x in ocmp if x not in gcmp]
            diffs.append(f"values: ours {only_o or '-'}, game {only_g or '-'}")
        gu = sorted(float(a) for _, a in g["upgrade"] if isinstance(a, (int, float)) and _ not in ("AddKeyword", "RemoveKeyword", "EnergyCost"))
        ou = sorted(float(x) for x in re.findall(r"UpgradeValueBy\((-?\d+(?:\.\d+)?)m?\)", o.get("on_upgrade") or ""))
        if gu != ou:
            diffs.append(f"upgrade amounts: ours {ou}, game {gu}")
        if diffs:
            rows.append((cid, o.get("owner"), diffs))
    for cid, o in sorted(ours.items()):
        if cid not in cards:
            missing_in_game.append((cid, o.get("owner")))
    return rows, missing_in_ours, missing_in_game


TOOL_FIELDS = {"DamageVar": ("dmg", "Damage"), "BlockVar": ("block", "Block"), "PowerVar<VulnerablePower>": ("vuln", "Vulnerable"),
               "PowerVar<WeakPower>": ("weak", "Weak"), "PowerVar<StrengthPower>": ("strength", "Strength")}


def compare_tools(cards):
    """Numbers the tools use offline (tools/plan_turn.py card_from_extract, base and upgraded) against the game's.
    Returns [(card, owner, [difference, ...])]. Cards whose damage is calculated in the play logic are skipped for damage."""
    import plan_turn as pt
    ours = {(c.get("id") or k).replace("CARD.", ""): c for k, c in dm.CARDS.items()}
    rows = []
    for cid, g in sorted(cards.items()):
        if cid not in ours:
            continue
        try:
            base, up = pt.card_from_extract(0, cid), pt.card_from_extract(0, cid + "+")
        except (SystemExit, Exception) as e:  # noqa: BLE001
            rows.append((cid, ours[cid].get("owner"), [f"tool could not build the card: {type(e).__name__}"]))
            continue
        diffs = []
        if g["cost"] >= 0 and not base.x_cost and base.cost != g["cost"]:
            diffs.append(f"cost: tools {base.cost}, game {g['cost']}")
        cost_up = sum(a for t, a in g["upgrade"] if t == "EnergyCost" and isinstance(a, (int, float)))
        if g["cost"] >= 0 and not up.x_cost and up.cost != g["cost"] + cost_up:
            diffs.append(f"upgraded cost: tools {up.cost}, game {g['cost'] + cost_up}")
        calculated = any(t.startswith("Calculated") or t.startswith("Extra") for t, _, _ in g["vars"])
        for vt, name, val in g["vars"]:
            if vt not in TOOL_FIELDS or val is None:
                continue
            attr, upname = TOOL_FIELDS[vt]
            if attr == "dmg" and calculated:
                continue
            gup = val + sum(a for t, a in g["upgrade"] if t in (upname, upname + "Power") and isinstance(a, (int, float)))
            ob, ou = getattr(base, attr), getattr(up, attr)
            if attr == "strength" and (ob == 0 and base.temp_str):
                ob, ou = base.temp_str, up.temp_str
            if ob == 0:
                continue  # the tool does not use this value (it means something else: per-turn Strength, an ally's Block)
            if ob != val:
                diffs.append(f"{upname}: tools {ob:g}, game {val:g}")
            elif ou != gup:
                diffs.append(f"{upname} upgraded: tools {ou:g}, game {gup:g}")
        if diffs:
            rows.append((cid, ours[cid].get("owner"), diffs))
    return rows


def write_report(cards, rows, missing_in_ours, missing_in_game, build, tool_rows=()):
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    L = [f"# Card data against the game's code ({build})", "",
         "Generated by `tools/game_cards.py`. `[GAME]`: values read from the installed game's assembly "
         "(`Models.Cards.*`: constructor, `get_CanonicalVars`, `OnUpgrade`). \"Ours\" is "
         "`knowledge/data/extract-2026-09-21/cards.json` after `knowledge/data/card-patches.json`.", "",
         f"- Cards read from the game: {len(cards)}", f"- Cards that differ: {len(rows)}",
         f"- In the game, not in our data: {len(missing_in_ours)}", f"- In our data, not in the game: {len(missing_in_game)}", "",
         "Not compared: values set outside `get_CanonicalVars` (calculated damage, hit counts and conditions in the play "
         "logic) and effect text.", ""]
    L += ["## Numbers the tools use offline (`tools/plan_turn.py`, base and upgraded)", "",
          f"{len(tool_rows)} cards differ. Live play reads card values from the game, so these matter for the fight "
          "simulator, drafting scores and deck metrics.", ""]
    tb = {}
    for cid, owner, diffs in tool_rows:
        tb.setdefault(owner or "?", []).append((cid, diffs))
    for owner in sorted(tb, key=lambda o: (o != "Ironclad", o != "colorless", o)):
        L += [f"### {owner}", "", "| Card | Difference |", "|---|---|"]
        L += [f"| {cid} | {'; '.join(d)} |" for cid, d in tb[owner]]
        L.append("")
    by_owner = {}
    for cid, owner, diffs in rows:
        by_owner.setdefault(owner or "?", []).append((cid, diffs))
    L += ["## Data file differences (extract `vars` and `on_upgrade` strings, cost, type, rarity, target)", ""]
    for owner in sorted(by_owner, key=lambda o: (o != "Ironclad", o)):
        L += [f"### {owner}", "", "| Card | Difference |", "|---|---|"]
        L += [f"| {cid} | {'; '.join(d)} |" for cid, d in by_owner[owner]]
        L.append("")
    L += ["## In the game, not in our data", "", "| Card | Cost | Type | Rarity | Target | Values | Upgrade |", "|---|---|---|---|---|---|---|"]
    for cid, g in missing_in_ours:
        vals = ", ".join(f"{t}{'(' + n + ')' if n else ''} {v:g}" if isinstance(v, (int, float)) else f"{t} ?" for t, n, v in g["vars"])
        ups = ", ".join(f"{t} {a:+g}" if isinstance(a, (int, float)) else str(t) for t, a in g["upgrade"])
        L.append(f"| {cid} | {g['cost']} | {g['type']} | {g['rarity']} | {g['target']} | {vals or '-'} | {ups or '-'} |")
    L += ["", "## In our data, not in the game", "", ", ".join(f"{cid} ({owner})" for cid, owner in missing_in_game) or "none", ""]
    REPORT.write_text("\n".join(L))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cached", action="store_true", help="reuse data/asm/cards-il.txt")
    a = ap.parse_args(argv)
    if not a.cached or not IL.exists():
        if not (GAME_DATA / "sts2.dll").exists():
            sys.exit("game assembly not found (see docs/environment.md)")
        dump_il()
    cards = game_cards(IL.read_text())
    OUT_JSON.write_text(json.dumps(cards, indent=1))
    build = game_build()
    version = build.split()[0]
    facts = {"about": "Card facts read from the installed game's code by tools/game_cards.py: energy cost, type, rarity, target, "
                      "canonical values [type, name, value] and upgrade amounts [target, amount]. [GAME] for this build. "
                      "Values set in the play logic (calculated damage, conditions) are not included.",
             "build": build,
             "cards": {cid: {k: g[k] for k in ("cost", "type", "rarity", "target", "vars", "upgrade")} for cid, g in sorted(cards.items())}}
    (FACTS_DIR / f"game-cards-{version}.json").write_text(json.dumps(facts, separators=(",", ":")).replace('},"', '},\n"') + "\n")
    rows, missing_in_ours, missing_in_game = compare(cards)
    tool_rows = compare_tools(cards)
    write_report(cards, rows, missing_in_ours, missing_in_game, build, tool_rows)
    print(f"{len(cards)} cards read from the game ({build}); data file: {len(rows)} differ; tool numbers: {len(tool_rows)} differ; "
          f"{len(missing_in_ours)} missing in our data, {len(missing_in_game)} only in our data. "
          f"Report: {REPORT.relative_to(PROJECT)}")
    for cid, owner, diffs in tool_rows:
        if owner in ("Ironclad", "colorless"):
            print(f"  {owner} {cid}: {'; '.join(diffs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
