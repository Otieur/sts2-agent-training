#!/usr/bin/env python3
"""Phase 1 E5: death table, deep dives on the top killers, HP trajectories.

Usage: python3 -I tools/analyze_deaths.py [--character IRONCLAD] [--build v0.107.1] [--out reports/phase1]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import (CAUTIONS, DATA, MAIN_BUILD, PROJECT, asc_band, connect, is_starter, md_table,  # noqa: E402
                    mean, median, num, pct, short, write_csv)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", default="IRONCLAD")
    ap.add_argument("--build", default=MAIN_BUILD)
    ap.add_argument("--out", default=str(PROJECT / "reports/phase1"))
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()
    ch = args.character.upper()
    out = Path(args.out)
    con = connect()
    run_filter = "r.n_players = 1 AND r.build_id = ? AND r.character = ?"
    P = [args.build, ch]
    runs = {r["run_id"]: dict(r) for r in con.execute(f"SELECT * FROM runs r WHERE {run_filter}", P)}
    floors = collections.defaultdict(dict)
    for f in con.execute(f"SELECT f.* FROM floors f JOIN runs r USING(run_id) WHERE {run_filter}", P):
        floors[f["run_id"]][f["floor"]] = dict(f)
    snap = collections.defaultdict(lambda: collections.defaultdict(list))  # run -> floor -> [(card, lvl, n)]
    for s in con.execute(f"SELECT s.* FROM deck_snapshots s JOIN runs r USING(run_id) WHERE {run_filter}", P):
        snap[s["run_id"]][s["floor"]].append((s["card_id"], s["upgrade_level"], s["count"]))
    relics = collections.defaultdict(list)
    for r in con.execute(f"SELECT x.* FROM final_relics x JOIN runs r USING(run_id) WHERE {run_filter}", P):
        relics[r["run_id"]].append((r["relic_id"], r["floor_added"] or 0))

    def deck_at(run_id, floor):
        """Deck at the start of `floor` as a Counter of card IDs, plus number of upgraded cards."""
        rows = snap[run_id].get(floor - 1, [])
        c = collections.Counter()
        upg = 0
        for cid, lvl, n in rows:
            c[cid] += n
            if lvl:
                upg += n
        return c, upg

    # --- S1: death table ----------------------------------------------------------------
    deaths = []
    for rid, r in runs.items():
        if r["win"] or r["abandoned"]:
            continue
        last = max(floors[rid])
        f = floors[rid][last]
        deck, upg = deck_at(rid, last)
        raw = json.loads((DATA / "raw" / f"{rid}.run").read_text())
        deaths.append({
            "run_id": rid, "ascension": r["ascension"], "floor": last, "act": f["act"],
            "encounter": r["killed_by_encounter"] or r["killed_by_event"] or f["model_id"],
            "hp_before": f["hp_before"], "max_hp": f["max_hp"],
            "hp_pct": f["hp_before"] / f["max_hp"] if f["max_hp"] else 0,
            "deck_size": sum(deck.values()), "upgraded": upg,
            "relics": sum(1 for _, fl in relics[rid] if fl <= last),
            "potions_held": len(raw["players"][0].get("potions", [])),
            "turns": f["turns_taken"],
        })
    deaths.sort(key=lambda d: (d["act"], d["floor"]))
    write_csv(out / f"deaths-{ch.lower()}.csv", list(deaths[0].keys()), [list(d.values()) for d in deaths])

    by_act = collections.Counter(d["act"] for d in deaths)
    pool = collections.Counter()
    for d in deaths:
        e = d["encounter"] or ""
        pool["boss" if e.endswith("_BOSS") else "elite" if e.endswith("_ELITE") else "hallway"] += 1

    L = [f"# Deaths: {ch.title()} ({args.build})", "",
         f"{len(deaths)} deaths in {len(runs)} solo runs ({sum(r['win'] for r in runs.values())} wins, "
         f"{sum(r['abandoned'] for r in runs.values())} abandoned).", "", CAUTIONS, "",
         "## Where runs end", "",
         md_table(["Act", "Deaths", "Share"], [[a, n, pct(n / len(deaths))] for a, n in sorted(by_act.items())]), "",
         f"By fight type: bosses {pool['boss']}, elites {pool['elite']}, hallway {pool['hallway']}.", "",
         "## Every death", "",
         md_table(["Floor", "Act", "Asc", "Killed by", "HP entering", "Deck", "Upgraded", "Relics", "Turns"],
                  [[d["floor"], d["act"], d["ascension"], short(d["encounter"]),
                    f"{d['hp_before']}/{d['max_hp']} ({pct(d['hp_pct'])})", d["deck_size"], d["upgraded"], d["relics"],
                    d["turns"]] for d in deaths]), ""]

    # --- S2: deep dives -----------------------------------------------------------------
    killers = collections.Counter(d["encounter"] for d in deaths)
    L += ["## Deep dives on the top killers", "",
          "For every fight against the encounter: the floor stats on arrival, comparing fights the Player survived "
          "with fights that ended the run.", ""]
    dive_rows = []
    for enc, k in killers.most_common(args.top):
        fights = [(rid, fl, f) for rid, fs in floors.items() for fl, f in fs.items() if f["model_id"] == enc]
        groups = {"survived": [], "died": []}
        for rid, fl, f in fights:
            r = runs[rid]
            died = (f["is_last_floor"] and not r["win"] and not r["abandoned"])
            deck, upg = deck_at(rid, fl)
            groups["died" if died else "survived"].append({
                "hp_pct": f["hp_before"] / f["max_hp"], "hp": f["hp_before"], "dmg": f["damage_taken"],
                "turns": f["turns_taken"], "deck": deck, "deck_size": sum(deck.values()), "upg": upg,
                "relics": sum(1 for _, fa in relics[rid] if fa < fl), "asc": r["ascension"],
            })
        rows = []
        for g in ("survived", "died"):
            xs = groups[g]
            if not xs:
                continue
            rows.append([g, len(xs), pct(median([x["hp_pct"] for x in xs])), num(median([x["hp"] for x in xs]), 0),
                         num(median([x["dmg"] for x in xs]), 0), num(median([x["turns"] for x in xs]), 0),
                         num(median([x["deck_size"] for x in xs]), 0), num(median([x["upg"] for x in xs]), 0),
                         num(median([x["relics"] for x in xs]), 0), num(mean([x["asc"] for x in xs]), 1)])
        # card presence difference
        diff = []
        if groups["survived"] and groups["died"]:
            cards = set()
            for g in groups.values():
                for x in g:
                    cards |= {c for c in x["deck"] if not is_starter(c, ch)}
            for c in cards:
                ps = mean([1 if x["deck"].get(c) else 0 for x in groups["survived"]])
                pd = mean([1 if x["deck"].get(c) else 0 for x in groups["died"]])
                diff.append((c, ps, pd))
            diff.sort(key=lambda t: -(t[1] - t[2]))
        L += [f"### {short(enc)} ({k} deaths, {len(fights)} fights)", "",
              md_table(["Outcome", "Fights", "Median HP% in", "Median HP in", "Median dmg", "Median turns",
                        "Median deck", "Median upgraded", "Median relics", "Mean asc"], rows), ""]
        if diff:
            L += ["Cards most over-represented in survived fights compared with fatal ones (share of decks containing the card):", "",
                  md_table(["Card", "Survived", "Died"],
                           [[short(c), pct(a), pct(b)] for c, a, b in diff[:6]]), "",
                  "Cards most over-represented in fatal fights:", "",
                  md_table(["Card", "Survived", "Died"],
                           [[short(c), pct(a), pct(b)] for c, a, b in sorted(diff, key=lambda t: t[1] - t[2])[:4]]), ""]
        for g in ("survived", "died"):
            for x in groups[g]:
                dive_rows.append([short(enc), g, round(x["hp_pct"], 3), x["hp"], x["dmg"], x["turns"], x["deck_size"],
                                  x["upg"], x["relics"], x["asc"]])
    write_csv(out / f"killer-fights-{ch.lower()}.csv",
              ["encounter", "outcome", "hp_pct_in", "hp_in", "dmg", "turns", "deck_size", "upgraded", "relics", "asc"],
              dive_rows)

    # --- S3: HP trajectories ------------------------------------------------------------
    traj = collections.defaultdict(lambda: collections.defaultdict(list))  # outcome -> floor -> [hp%]
    traj_band = collections.defaultdict(lambda: collections.defaultdict(list))
    for rid, fs in floors.items():
        r = runs[rid]
        if r["abandoned"]:
            continue
        outcome = "win" if r["win"] else "loss"
        for fl, f in fs.items():
            if f["max_hp"]:
                traj[outcome][fl].append(f["hp_after"] / f["max_hp"])
                traj_band[asc_band(r["ascension"])][fl].append(f["hp_after"] / f["max_hp"])
    max_floor = max(max(v) for v in traj.values() if v)
    traj_rows = []
    for fl in range(1, max_floor + 1):
        traj_rows.append([fl,
                          round(median(traj["win"][fl]), 3) if traj["win"][fl] else "", len(traj["win"][fl]),
                          round(median(traj["loss"][fl]), 3) if traj["loss"][fl] else "", len(traj["loss"][fl])])
    write_csv(out / f"hp-trajectory-{ch.lower()}.csv",
              ["floor", "win_median_hp_pct", "win_n", "loss_median_hp_pct", "loss_n"], traj_rows)
    cum = []
    total = len(deaths)
    running = 0
    death_floor = collections.Counter(d["floor"] for d in deaths)
    for fl in range(1, max_floor + 1):
        running += death_floor.get(fl, 0)
        cum.append((fl, running))
    sample = [r for r in traj_rows if r[0] in (2, 5, 8, 10, 12, 15, 17, 18, 20, 23, 25, 28, 31, 33, 35, 38, 41, 45, 48, 50)]
    L += ["## HP trajectories", "",
          "Median HP% after each floor, in finished runs. Full series in `hp-trajectory-<character>.csv`. Loss "
          "medians at later floors only include runs still alive.", "",
          md_table(["Floor", "Wins: median HP%", "n", "Losses: median HP%", "n", "Cumulative deaths"],
                   [[r[0], pct(r[1]) if r[1] != "" else "-", r[2], pct(r[3]) if r[3] != "" else "-", r[4],
                     f"{dict(cum)[r[0]]}/{total}"] for r in sample]), ""]

    (out / f"deaths-{ch.lower()}.md").write_text("\n".join(L))
    print(f"{ch}: {len(deaths)} deaths; by act {dict(by_act)}; top killers {killers.most_common(3)}")


if __name__ == "__main__":
    main()
