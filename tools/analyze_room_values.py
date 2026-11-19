#!/usr/bin/env python3
"""What each room type costs and gives, by act and ascension band (path planning evidence).

Per map point type (monster, elite, ? room, shop, rest site, treasure) and act: mean HP change (% of max), gold,
cards gained, relics gained, potions gained, and how often a ? room turned into a fight. All characters, solo,
finished and unfinished runs alike (a room's cost does not depend on how the run ended).

Usage: python3 -I tools/analyze_room_values.py
Writes reports/phase2/room-values.md
"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import MAIN_BUILD, PROJECT, asc_band, connect, md_table, mean, pct  # noqa: E402

TYPES = ["monster", "elite", "unknown", "shop", "rest_site", "treasure"]


def main():
    con = connect()
    floors = [dict(r) for r in con.execute("""
        SELECT f.run_id, f.floor, f.act, f.map_point_type AS t, f.room_type, f.hp_before, f.hp_after, f.max_hp,
               f.gold_gained, f.gold_spent, r.ascension
        FROM floors f JOIN runs r USING(run_id)
        WHERE r.n_players = 1 AND r.build_id = ? AND f.map_point_type IN ('monster','elite','unknown','shop','rest_site','treasure')""",
        [MAIN_BUILD])]
    gains = collections.defaultdict(lambda: collections.Counter())
    for r in con.execute("SELECT run_id, floor, change FROM deck_changes WHERE change='gained'"):
        gains[(r["run_id"], r["floor"])]["card"] += 1
    for r in con.execute("SELECT run_id, floor, kind, picked FROM relic_events WHERE kind IN ('offered','bought')"):
        if r["kind"] == "bought" or r["picked"]:
            gains[(r["run_id"], r["floor"])]["relic"] += 1
    for r in con.execute("SELECT run_id, floor, kind, picked FROM potion_events WHERE kind IN ('offered','bought')"):
        if r["kind"] == "bought" or r["picked"]:
            gains[(r["run_id"], r["floor"])]["potion"] += 1

    def row(xs, label):
        if not xs:
            return None
        hp = [(x["hp_after"] - x["hp_before"]) / x["max_hp"] for x in xs if x["max_hp"]]
        g = [gains[(x["run_id"], x["floor"])] for x in xs]
        fights = sum(1 for x in xs if x["room_type"] in ("monster", "elite", "boss"))
        return [label, len(xs), pct(mean(hp)), f"{mean([x['gold_gained'] for x in xs]):.0f}",
                f"{mean([c['card'] for c in g]):.2f}", f"{mean([c['relic'] for c in g]):.2f}", f"{mean([c['potion'] for c in g]):.2f}",
                pct(fights / len(xs)) if label.startswith("?") else ""]

    L = ["# Room Values by Act", "",
         f"All characters, solo, {MAIN_BUILD}. Built by `tools/analyze_room_values.py`. `[PLAYER-DATA]`", "",
         "HP change is net over the floor as a share of max HP: fights cost HP, rest sites usually heal, and Burning Blood-style "
         "relics heal after fights. Cards, relics and potions count what was actually taken, so they reflect the Player's "
         "choices as well as the room.", ""]
    headers = ["Room", "Visits", "Mean HP change", "Gold", "Cards", "Relics", "Potions", "Became a fight"]
    names = {"monster": "Monster", "elite": "Elite", "unknown": "? room", "shop": "Shop", "rest_site": "Rest site", "treasure": "Treasure"}
    for act in (1, 2, 3):
        rows = [r for t in TYPES for r in [row([x for x in floors if x["act"] == act and x["t"] == t], names[t])] if r]
        L += [f"## Act {act}", "", md_table(headers, rows), ""]
    L += ["## By ascension band (all acts)", ""]
    for band in ("A0-4", "A5-9", "A10"):
        rows = [r for t in TYPES for r in [row([x for x in floors if asc_band(x["ascension"]) == band and x["t"] == t], names[t])] if r]
        L += [f"### {band}", "", md_table(headers, rows), ""]
    out = PROJECT / "reports/phase2/room-values.md"
    out.write_text("\n".join(L))
    print("wrote", out.relative_to(PROJECT))


if __name__ == "__main__":
    main()
