#!/usr/bin/env python3
"""Freeze per-encounter damage benchmarks split by ascension band (A0-4, A5-9, A10).

The pooled Ironclad benchmark is dominated by the Player's A7-A10 runs, so it is too harsh for comparing
low-ascension runs. These files let post-mortems and milestone M4 compare like with like.

Writes (only if absent; frozen):
  data/benchmarks/ironclad-encounters-by-band-v0.107.1.csv
  data/benchmarks/allchars-encounters-by-band-v0.107.1.csv
Usage: python3 -I tools/build_band_benchmarks.py
"""
import collections
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import DATA, MAIN_BUILD, asc_band, connect, median, quantile, write_csv  # noqa: E402


def build(con, character=None):
    q = """SELECT f.model_id AS enc, f.damage_taken, f.turns_taken, r.ascension
           FROM floors f JOIN runs r USING(run_id)
           WHERE r.n_players = 1 AND r.build_id = ? AND f.room_type IN ('monster','elite','boss')"""
    params = [MAIN_BUILD]
    if character:
        q += " AND r.character = ?"
        params.append(character)
    by = collections.defaultdict(list)
    for r in con.execute(q, params):
        by[(asc_band(r["ascension"]), r["enc"])].append(r)
    rows = []
    for (band, enc), xs in sorted(by.items()):
        d = [x["damage_taken"] for x in xs]
        t = [x["turns_taken"] for x in xs if x["turns_taken"]]
        rows.append([band, enc, len(xs), round(median(d), 1), round(quantile(d, 0.75), 1), round(quantile(d, 0.9), 1),
                     median(t) if t else "", "yes" if len(xs) >= 5 else "no"])
    return rows


def main():
    con = connect()
    cols = ["band", "encounter", "n", "median_dmg", "p75_dmg", "p90_dmg", "median_turns", "benchmark_grade"]
    for name, ch in (("ironclad", "IRONCLAD"), ("allchars", None)):
        path = DATA / "benchmarks" / f"{name}-encounters-by-band-{MAIN_BUILD}.csv"
        if path.exists():
            print(f"exists, left unchanged: {path.name}")
            continue
        rows = build(con, ch)
        write_csv(path, cols, rows)
        path.with_suffix(".meta.json").write_text(json.dumps({
            "created": datetime.date.today().isoformat(), "character": ch or "ALL", "build": MAIN_BUILD,
            "rows": len(rows), "note": "Frozen. Never edit; create a new file for a new benchmark.",
        }, indent=2) + "\n")
        print(f"wrote {path.name}: {len(rows)} band×encounter rows")


if __name__ == "__main__":
    main()
