#!/usr/bin/env python3
"""Game logic that only screen code calls: candidates for state the simulator host never sets.

The simulator host runs the game's logic without its scene nodes. Anything a screen does on the logic's behalf is
missing there unless the host does it itself: a shop's card removal was marked as used only by the shop screen, so
the host kept selling it (docs/simulator-integrity.md, FI-7e). This lists every method of the game's logic that has
callers, all of them screen code or methods listed here themselves (a fixed point), from the call graph of
`tools/asm/asm.cs` (`data/asm/sts2-calls.tsv`: caller, tab, callees joined by `|`).

    python3 -I tools/asm/ui_only.py                      # run, room, reward, combat, shop and model logic
    python3 -I tools/asm/ui_only.py --match 'Rooms\\.'    # any part of the logic, by regular expression
    python3 -I tools/asm/ui_only.py --namespaces         # counts by namespace
    python3 -I tools/asm/ui_only.py --setters            # setters of logic properties that screen code calls

Each line: the method, the fields it touches, the screen methods that call it, and `host` when the host's source
(`sim/*.cs`) names the method. Read the list after every game update and look at each new line: what does the method
change, and does the host do the same?

Limits. The graph holds direct calls only: an override is reached through its base method and never listed, and a
handler reached through an event or a delegate is listed although logic raises the event. Getters, event
subscriptions and constructors are left out. Screen code is every type under `.Nodes.`, the debug console, the test
support and the game's own auto-player."""
import argparse
import collections
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CALLS = ROOT / "data" / "asm" / "sts2-calls.tsv"
PREFIX = "MegaCrit.Sts2.Core."
PLAY = r"Core\.(Entities|Runs|Rooms|Rewards|Combat|Map|Odds|Random|Hooks|Commands|CardSelection|MonsterMoves|GameActions|Unlocks|Models|Events)\."
PRESENTATION = re.compile(r"::\w*(Icon|Texture|Path|Loc|Title|Description|HoverTip|Sfx|Vfx|Anim|Visual|Color|Portrait|Image|Scene|Asset|Text|Label|"
                          r"Banner|Material|Sprite|Frame|Outline|Audio|Music|Layout|Background|Spine|Skin|Name|Format|String|Dialogue|Line|Preview|"
                          r"Display|Glow|Shader|Particle|Font)\w*$")
NOT_PLAY = re.compile(r"\.(Saves|Platform|Multiplayer|Localization|Assets|Bindings|Settings|Audio|Animation|HoverTips|Logging|Modding|Leaderboard|"
                      r"Daily|Timeline|ControllerInput|Helpers)\.")


def norm(m):
    """A compiler-generated method (async state machine, lambda, local function) counts as the method that owns it."""
    t, _, name = m.partition("::")
    while True:
        k = re.match(r"^(.*)\+<(\w+)>d__\d+$", t)
        if k:
            t, name = k.group(1), k.group(2)
            continue
        k = re.match(r"^(.*)\+<>c(__DisplayClass\d+_\d+)?$", t)
        if k:
            t = k.group(1)
            n = re.match(r"^<(\w+)>b__", name)
            name = n.group(1) if n else name
            continue
        break
    n = re.match(r"^<(\w+)>[bg]__", name)
    return t + "::" + (n.group(1) if n else name)


def is_screen(m):
    t = m.split("::")[0]
    return ".Nodes." in t or t.startswith("Godot.") or ".Debug" in t or ".DevConsole" in t or ".TestSupport" in t or ".AutoSlay" in t


def short(m):
    return m.split("::")[0].split(".")[-1] + "::" + m.split("::")[1]


def load(path):
    callers, uses, raw = collections.defaultdict(set), collections.defaultdict(set), []
    for line in open(path):
        a = line.rstrip("\n").split("\t")
        if len(a) < 2:
            continue
        src = norm(a[0])
        for c in a[1].split("|"):
            if not c or c.startswith("str:"):
                continue
            c = c[4:] if c.startswith("new:") else c
            if c.startswith("f:"):
                uses[src].add(c[2:].split("::")[-1])
                continue
            dst = norm(c)
            raw.append((src, c))
            if dst != src:
                callers[dst].add(src)
    return callers, uses, raw


def screen_only(callers):
    found, changed = set(), True
    while changed:
        changed = False
        for m, cs in callers.items():
            if m not in found and m.startswith("MegaCrit.Sts2.") and not is_screen(m) and all(is_screen(c) or c in found for c in cs):
                found.add(m)
                changed = True
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--calls", default=str(CALLS))
    ap.add_argument("--match", default=PLAY, help="regular expression on the method's full name")
    ap.add_argument("--all-names", action="store_true", help="keep methods whose names say presentation (icons, text, effects)")
    ap.add_argument("--namespaces", action="store_true")
    ap.add_argument("--setters", action="store_true")
    a = ap.parse_args()
    callers, uses, raw = load(a.calls)
    host = "\n".join(p.read_text() for p in sorted((ROOT / "sim").glob("*.cs")))
    if a.setters:
        by = collections.defaultdict(set)
        for src, c in raw:
            t, _, n = c.partition("::")
            if is_screen(src) and ".Nodes." in src and c.startswith(PREFIX) and not is_screen(c) and n.startswith("set_") and not NOT_PLAY.search(t + "."):
                by[c.replace(PREFIX, "")].add(short(src))
        for k in sorted(by):
            print(k, "| from", sorted(by[k])[:4])
        print(len(by), "setters of logic properties called from screen code")
        return
    found = screen_only(callers)
    if a.namespaces:
        for k, v in collections.Counter(".".join(m.split("::")[0].split(".")[:4]) for m in found).most_common():
            print(v, k)
        print(len(found), "methods of the logic that only screen code calls")
        return
    pat, n = re.compile(a.match), 0
    for m in sorted(found):
        name = m.partition("::")[2]
        if name.startswith(("get_", "add_", "remove_", ".c")) or not pat.search(m) or (not a.all_names and PRESENTATION.search(m)):
            continue
        fields = sorted(f for f in uses.get(m, ()) if not f.startswith("<>"))
        screens = sorted(short(c) for c in callers[m] if is_screen(c))
        print(m.replace(PREFIX, ""), "| fields", fields[:6], "| from", screens[:4], "| host" if re.search(r"\b%s\b" % re.escape(name), host) else "")
        n += 1
    print(n, "methods")


if __name__ == "__main__":
    main()
