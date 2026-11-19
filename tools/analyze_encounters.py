#!/usr/bin/env python3
"""Phase 1 E3: encounter danger statistics and the frozen combat benchmark.

Usage: python3 -I tools/analyze_encounters.py [--character IRONCLAD] [--build v0.107.1] [--out reports/phase1]
Writes:
  <out>/encounters-<character>.csv, <out>/encounters-all.csv, <out>/danger-<character>.md
  data/benchmarks/<character>-encounters-<build>.csv (only if it does not exist yet)
"""
import argparse
import collections
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import (CAUTIONS, DATA, MAIN_BUILD, PROJECT, asc_band, connect, md_table, mean,  # noqa: E402
                    median, num, pct, quantile, short, write_csv)


def pool_of(enc):
    for suffix in ("_WEAK", "_NORMAL", "_ELITE", "_BOSS"):
        if enc.endswith(suffix):
            return suffix[1:].lower()
    return "event" if "EVENT_ENCOUNTER" in enc else "other"


def load_fights(con, build, character=None):
    q = """SELECT f.run_id, f.floor, f.act, f.model_id AS enc, f.damage_taken, f.max_hp, f.hp_before,
                  f.turns_taken, f.is_last_floor, r.win, r.abandoned, r.ascension, r.character,
                  r.killed_by_encounter
           FROM floors f JOIN runs r USING(run_id)
           WHERE r.n_players = 1 AND r.build_id = ? AND f.room_type IN ('monster','elite','boss')"""
    params = [build]
    if character:
        q += " AND r.character = ?"
        params.append(character)
    return [dict(r) for r in con.execute(q, params)]


def summarise(fights):
    by = collections.defaultdict(list)
    for f in fights:
        by[f["enc"]].append(f)
    rows = []
    for enc, fs in by.items():
        dmg = [f["damage_taken"] for f in fs]
        dmg_pct = [f["damage_taken"] / f["max_hp"] for f in fs if f["max_hp"]]
        turns = [f["turns_taken"] for f in fs if f["turns_taken"]]
        deaths = sum(1 for f in fs if f["is_last_floor"] and not f["win"] and not f["abandoned"]
                     and f["killed_by_encounter"] == enc)
        acts = collections.Counter(f["act"] for f in fs)
        rows.append({
            "encounter": enc, "pool": pool_of(enc), "act": acts.most_common(1)[0][0],
            "acts_seen": ",".join(str(a) for a in sorted(acts)), "n": len(fs),
            "median_dmg": median(dmg), "mean_dmg": mean(dmg), "p75_dmg": quantile(dmg, 0.75),
            "p90_dmg": quantile(dmg, 0.9), "median_dmg_pct": median(dmg_pct),
            "median_turns": median(turns) if turns else float("nan"), "deaths": deaths,
            "death_rate": deaths / len(fs),
        })
    rows.sort(key=lambda r: (r["act"], r["pool"], -r["median_dmg"]))
    return rows


COLS = ["encounter", "pool", "act", "acts_seen", "n", "median_dmg", "mean_dmg", "p75_dmg", "p90_dmg",
        "median_dmg_pct", "median_turns", "deaths", "death_rate"]


def to_csv_rows(rows):
    out = []
    for r in rows:
        out.append([r[c] if not isinstance(r[c], float) else round(r[c], 3) for c in COLS])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", default="IRONCLAD")
    ap.add_argument("--build", default=MAIN_BUILD)
    ap.add_argument("--out", default=str(PROJECT / "reports/phase1"))
    args = ap.parse_args()
    ch = args.character.upper()
    out = Path(args.out)
    con = connect()

    fights_ch = load_fights(con, args.build, ch)
    fights_all = load_fights(con, args.build)
    rows_ch = summarise(fights_ch)
    rows_all = summarise(fights_all)
    write_csv(out / f"encounters-{ch.lower()}.csv", COLS, to_csv_rows(rows_ch))
    write_csv(out / "encounters-all.csv", COLS, to_csv_rows(rows_all))

    # By ascension band (character only)
    band_rows = []
    for band in ("A0-4", "A5-9", "A10"):
        sub = [f for f in fights_ch if asc_band(f["ascension"]) == band]
        for r in summarise(sub):
            band_rows.append([band] + to_csv_rows([r])[0])
    write_csv(out / f"encounters-{ch.lower()}-by-band.csv", ["band"] + COLS, band_rows)

    # Benchmark (frozen)
    bench = DATA / "benchmarks" / f"{ch.lower()}-encounters-{args.build}.csv"
    if not bench.exists():
        bcols = ["encounter", "pool", "act", "n", "median_dmg", "p75_dmg", "p90_dmg", "median_turns",
                 "benchmark_grade"]
        brows = [[r["encounter"], r["pool"], r["act"], r["n"], round(r["median_dmg"], 1),
                  round(r["p75_dmg"], 1), round(r["p90_dmg"], 1),
                  r["median_turns"] if r["median_turns"] == r["median_turns"] else "",
                  "yes" if r["n"] >= 5 else "no"] for r in rows_ch]
        write_csv(bench, bcols, brows)
        n_runs = len({f["run_id"] for f in fights_ch})
        bench.with_suffix(".meta.json").write_text(json.dumps({
            "created": datetime.date.today().isoformat(), "character": ch, "build": args.build,
            "source_runs": n_runs, "source_fights": len(fights_ch),
            "note": "Frozen. Never edit; create a new file for a new benchmark.",
        }, indent=2) + "\n")
        bench_msg = f"wrote {bench.relative_to(PROJECT)}"
    else:
        bench_msg = f"benchmark exists, left unchanged: {bench.relative_to(PROJECT)}"

    # Danger report
    n_runs = len({f["run_id"] for f in fights_ch})
    lines = [f"# Encounter Danger: {ch.title()} ({args.build})", "",
             f"Source: {len(fights_ch)} fights from {n_runs} solo runs. Damage is HP lost on the floor. "
             "Death rate = deaths ÷ times the fight was reached.", "", CAUTIONS, ""]
    for act in sorted({r["act"] for r in rows_ch}):
        lines.append(f"## Act {act}")
        for pool, title, limit in (("weak", "Hallway (weak pool)", 10), ("normal", "Hallway (normal pool)", 10),
                                   ("elite", "Elites", 10), ("boss", "Bosses", 10), ("event", "Event fights", 5)):
            sub = [r for r in rows_ch if r["act"] == act and r["pool"] == pool]
            if not sub:
                continue
            sub.sort(key=lambda r: -r["median_dmg"])
            lines += ["", f"### {title}", "",
                      md_table(["Encounter", "n", "Median dmg", "p90 dmg", "Median % max HP", "Median turns", "Deaths"],
                               [[short(r["encounter"]), r["n"], num(r["median_dmg"], 0), num(r["p90_dmg"], 0),
                                 pct(r["median_dmg_pct"]), num(r["median_turns"], 0), r["deaths"]]
                                for r in sub[:limit]])]
        lines.append("")

    # Cross-character comparison for the deadliest
    killers = collections.Counter(f["enc"] for f in fights_ch if f["is_last_floor"] and not f["win"]
                                  and not f["abandoned"] and f["killed_by_encounter"] == f["enc"])
    all_by = {r["encounter"]: r for r in rows_all}
    ch_by = {r["encounter"]: r for r in rows_ch}
    lines += ["## Deadliest encounters, compared with all characters", "",
              md_table(["Encounter", f"{ch.title()} deaths", f"{ch.title()} n", f"{ch.title()} median dmg",
                        "All chars n", "All chars median dmg"],
                       [[short(e), k, ch_by[e]["n"], num(ch_by[e]["median_dmg"], 0), all_by[e]["n"],
                         num(all_by[e]["median_dmg"], 0)] for e, k in killers.most_common(10)]), ""]
    (out / f"danger-{ch.lower()}.md").write_text("\n".join(lines))
    print(f"{ch}: {len(rows_ch)} encounters, {len(fights_ch)} fights; {bench_msg}")


if __name__ == "__main__":
    main()
