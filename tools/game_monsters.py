#!/usr/bin/env python3
"""Monster numbers from the game's own code, compared with our monster data.

Reads the IL of every class in MegaCrit.Sts2.Core.Models.Monsters (through tools/asm/asm.cs) and extracts the numeric
properties (HP, move damage, repeats, amounts), each with its base value and, where the game raises it, the ascension
level and raised value (AscensionHelper.GetValueIfAscension). Writes knowledge/data/game-monsters-<version>.json and
reports/game-check/monsters.md, which lists every number that differs from knowledge/data/extract-2026-09-21/monsters.json.
Run it after every game update (docs/runbooks/game-patch.md).

    python3 -I tools/game_monsters.py            # dump IL (about 30 s), compare, write the report
    python3 -I tools/game_monsters.py --cached   # reuse data/asm/monsters-il.txt

Ascension levels that change monsters: ToughEnemies (A8, more HP), DeadlyEnemies (A9, more damage).
Limits: numbers written inline in move logic (not in a property) and move order are not read here.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "tools"))
from game_cards import GAME_DATA, const, game_build, parse_methods, snake  # noqa: E402

NS = "MegaCrit.Sts2.Core.Models.Monsters."
IL = PROJECT / "data" / "asm" / "monsters-il.txt"
REPORT = PROJECT / "reports" / "game-check" / "monsters.md"
FACTS_DIR = PROJECT / "knowledge" / "data"
EXTRACT = PROJECT / "knowledge" / "data" / "extract-2026-09-21" / "monsters.json"
LEVELS = {1: "SwarmingElites", 2: "WearyTraveler", 3: "Poverty", 4: "TightBelt", 5: "AscendersBane", 6: "Inflation", 7: "Scarcity",
          8: "ToughEnemies", 9: "DeadlyEnemies", 10: "DoubleBoss"}
NUMERIC = re.compile(r"(Damage|Hp|Repeat|Amount|Strength|Count|Block|Heal|Stacks|Times|Gain|Turns|Weak|Vulnerable|Frail|Plating|Dexterity)")


def dump_il():
    IL.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["dotnet", "run", "tools/asm/asm.cs", "--", "il", str(GAME_DATA / "sts2.dll"), NS], cwd=PROJECT,
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or "### " not in r.stdout:
        sys.exit(f"could not read the game assembly: {r.stderr[-400:]}")
    IL.write_text(r.stdout)


def numeric_property(ins):
    """{'base': n} or {'base': n, 'asc': m, 'level': name} for a getter made only of constants, else None."""
    ops = [op for op in ins if op and not re.match(r"(ldarg|ret|nop|conv\.)", op)]
    consts = [const(op) for op in ops]
    if len(ops) == 1 and consts[0] is not None:
        return {"base": consts[0]}
    if len(ops) == 4 and all(c is not None for c in consts[:3]) and ops[3].endswith("AscensionHelper::GetValueIfAscension"):
        return {"base": consts[2], "asc": consts[1], "level": LEVELS.get(consts[0], consts[0])}
    return None


def game_monsters(text):
    out = {}
    methods = parse_methods(text)
    for cls, ms in methods.items():
        cls = cls[len(NS):] if cls.startswith(NS) else cls.split("Models.Monsters.")[-1]
        if "+" in cls or "." in cls:
            continue
        props = {}
        for name, ins in ms.items():
            if not name.startswith("get_") or not NUMERIC.search(name) or name.endswith("Type"):
                continue
            v = numeric_property(ins)
            if v is not None:
                props[name[4:]] = v
        if props:
            out[snake(cls)] = props
    return out


def compare(monsters):
    ours = {m["id"]: m for m in json.loads(EXTRACT.read_text())}
    rows, missing_in_ours = [], []
    for mid, props in sorted(monsters.items()):
        o = ours.get(mid)
        if o is None:
            missing_in_ours.append(mid)
            continue
        diffs = []
        for key, prop in (("min_hp", "MinInitialHp"), ("max_hp", "MaxInitialHp")):
            if prop in props and o.get(key) is not None and int(o[key]) != props[prop]["base"]:
                diffs.append(f"{key}: ours {o[key]}, game {props[prop]['base']}")
        for mv in o.get("moves") or []:
            names = re.findall(r"\(([A-Za-z]+Damage)\b", mv.get("intent") or "")
            m = re.search(r"Deal (\d+) damage", mv.get("effect") or "")
            if names and m and names[0] in props and int(m.group(1)) != props[names[0]]["base"]:
                diffs.append(f"{mv.get('move')}: ours {m.group(1)}, game {props[names[0]]['base']}")
            rep_name = re.search(r"MultiAttackIntent\([A-Za-z]+, ([A-Za-z]+)\)", mv.get("intent") or "")
            m2 = re.search(r"damage (\d+) times", mv.get("effect") or "")
            if rep_name and m2 and rep_name.group(1) in props and int(m2.group(1)) != props[rep_name.group(1)]["base"]:
                diffs.append(f"{mv.get('move')} hits: ours {m2.group(1)}, game {props[rep_name.group(1)]['base']}")
        if diffs:
            rows.append((mid, diffs))
    missing_in_game = sorted(set(ours) - set(monsters))
    return rows, missing_in_ours, missing_in_game


def fmt(v):
    return f"{v['base']}" + (f" ({v['asc']} at {v['level']})" if "asc" in v else "")


def write_report(monsters, rows, missing_in_ours, missing_in_game, build):
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    L = [f"# Monster numbers against the game's code ({build})", "",
         "Generated by `tools/game_monsters.py`. `[GAME]`: numeric properties of `Models.Monsters.*` in the installed game. "
         "\"Ours\" is `knowledge/data/extract-2026-09-21/monsters.json`, which the enemy and boss notes were built from.", "",
         f"- Monsters with numeric properties read: {len(monsters)}", f"- Monsters whose numbers differ from our data: {len(rows)}",
         f"- In the game, not in our data: {len(missing_in_ours)}",
         "", "Ascension: values in brackets apply from that level (ToughEnemies is A8, DeadlyEnemies is A9).", "",
         "## Differences", "", "| Monster | Difference | Game values |", "|---|---|---|"]
    for mid, diffs in rows:
        L.append(f"| {mid} | {'; '.join(diffs)} | {', '.join(f'{k} {fmt(v)}' for k, v in sorted(monsters[mid].items()))} |")
    L += ["", "## In the game, not in our data", "", ", ".join(missing_in_ours) or "none", "",
          "## In our data, without numeric properties in the game (removed, renamed, or numbers written inline)", "",
          ", ".join(missing_in_game) or "none", ""]
    REPORT.write_text("\n".join(L))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cached", action="store_true", help="reuse data/asm/monsters-il.txt")
    a = ap.parse_args(argv)
    if not a.cached or not IL.exists():
        if not (GAME_DATA / "sts2.dll").exists():
            sys.exit("game assembly not found (see docs/environment.md)")
        dump_il()
    monsters = game_monsters(IL.read_text())
    build = game_build()
    facts = {"about": "Monster numbers read from the installed game's code by tools/game_monsters.py: per monster, numeric "
                      "properties as {base, asc, level} (asc applies from that ascension level). [GAME] for this build.",
             "build": build, "monsters": monsters}
    (FACTS_DIR / f"game-monsters-{build.split()[0]}.json").write_text(
        json.dumps(facts, separators=(",", ":")).replace('}},"', '}},\n"') + "\n")
    rows, missing_in_ours, missing_in_game = compare(monsters)
    write_report(monsters, rows, missing_in_ours, missing_in_game, build)
    print(f"{len(monsters)} monsters read from the game ({build}); {len(rows)} differ from our data; "
          f"{len(missing_in_ours)} missing in our data. Report: {REPORT.relative_to(PROJECT)}")
    for mid, diffs in rows:
        if mid.endswith("BOSS") or any(k in mid for k in ("VANTOM", "BEAST", "INSATIABLE", "TEST_SUBJECT", "KNOWLEDGE", "FYSH", "QUEEN",
                                                         "KAISER", "WATERFALL", "LAGAVULIN", "KIN", "BYRDONIS", "ENTOMANCER")):
            print(f"  {mid}: {'; '.join(diffs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
