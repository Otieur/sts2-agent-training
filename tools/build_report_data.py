#!/usr/bin/env python3
"""Build the JSON data files for the Phase 1 visual report (one file per chart dataset).

Reads data/runs.db (built by tools/extract_runs.py) and reports/phase1/card-ranking-<character>.csv
(built by tools/analyze_cards.py). Writes reports/phase1/dashboard/<dataset>.json as {"rows": [...], "meta": [...]}.

Usage: python3 -I tools/build_report_data.py [--character IRONCLAD] [--build v0.107.1]
"""
import argparse
import collections
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_path import logistic_threshold  # noqa: E402
from stslib import MAIN_BUILD, PROJECT, connect, median, quantile  # noqa: E402

SELF = Path(__file__).resolve()


def pretty(enc):
    name = enc.split(".", 1)[-1]
    for suffix in ("_BOSS", "_ELITE", "_NORMAL", "_WEAK"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name.replace("_", " ").title()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", default="IRONCLAD")
    ap.add_argument("--build", default=MAIN_BUILD)
    args = ap.parse_args()
    ch = args.character.upper()
    out = PROJECT / "reports/phase1/dashboard"
    out.mkdir(parents=True, exist_ok=True)
    con = connect()
    F = "r.n_players = 1 AND r.build_id = ?"
    FC = F + " AND r.character = ?"
    P1, P2 = [args.build], [args.build, ch]

    runs = {r["run_id"]: dict(r) for r in con.execute(f"SELECT * FROM runs r WHERE {FC}", P2)}
    floors = collections.defaultdict(dict)
    for f in con.execute(f"SELECT f.* FROM floors f JOIN runs r USING(run_id) WHERE {FC}", P2):
        floors[f["run_id"]][f["floor"]] = dict(f)

    datasets = {}

    # deaths and HP trajectory
    deaths = []
    for rid, r in runs.items():
        if r["win"] or r["abandoned"]:
            continue
        last = max(floors[rid])
        deaths.append(floors[rid][last])
    max_floor = max(max(fs) for fs in floors.values())
    by_floor = collections.Counter(d["floor"] for d in deaths)
    act_of_floor = {}
    for fs in floors.values():
        for fl, f in fs.items():
            act_of_floor.setdefault(fl, f["act"])
    cum, rows = 0, []
    for fl in range(1, max_floor + 1):
        cum += by_floor.get(fl, 0)
        rows.append({"floor": fl, "act": act_of_floor.get(fl), "deaths": by_floor.get(fl, 0), "cumulative": cum})
    datasets["deaths_by_floor"] = rows

    traj = collections.defaultdict(lambda: collections.defaultdict(list))
    for rid, fs in floors.items():
        r = runs[rid]
        if r["abandoned"]:
            continue
        key = "win" if r["win"] else "loss"
        for fl, f in fs.items():
            if f["max_hp"]:
                traj[key][fl].append(f["hp_after"] / f["max_hp"])
    datasets["hp_trajectory"] = [{
        "floor": fl,
        "win_median": round(median(traj["win"][fl]), 4) if traj["win"][fl] else None, "win_n": len(traj["win"][fl]),
        "loss_median": round(median(traj["loss"][fl]), 4) if len(traj["loss"][fl]) >= 3 else None,
        "loss_n": len(traj["loss"][fl]),
    } for fl in range(1, max_floor + 1)]

    # boss and elite danger, character vs all characters
    def fight_stats(params, filt):
        by = collections.defaultdict(list)
        q = f"""SELECT f.model_id, f.damage_taken, f.act, f.is_last_floor, r.win, r.abandoned, r.killed_by_encounter
                FROM floors f JOIN runs r USING(run_id) WHERE {filt} AND f.room_type IN ('elite','boss')"""
        for x in con.execute(q, params):
            by[x["model_id"]].append(dict(x))
        return by
    mine, allc = fight_stats(P2, FC), fight_stats(P1, F)
    rows = []
    for enc, fs in mine.items():
        if len(fs) < 5:
            continue
        d = [x["damage_taken"] for x in fs]
        a = [x["damage_taken"] for x in allc[enc]]
        rows.append({
            "encounter": enc.split(".", 1)[-1], "name": pretty(enc), "pool": "boss" if enc.endswith("_BOSS") else "elite",
            "act": fs[0]["act"], "n": len(fs), "median_dmg": median(d), "p90_dmg": round(quantile(d, 0.9), 1),
            "deaths": sum(1 for x in fs if x["is_last_floor"] and not x["win"] and not x["abandoned"]
                          and x["killed_by_encounter"] == enc),
            "all_n": len(a), "all_median_dmg": median(a),
        })
    rows.sort(key=lambda r: (r["pool"] != "boss", r["act"], -r["median_dmg"]))
    datasets["boss_elite_danger"] = rows

    # rest-site choices by HP on arrival
    rests = [dict(x) for x in con.execute(f"SELECT c.* FROM rest_choices c JOIN runs r USING(run_id) WHERE {FC}", P2)]
    buckets = [(0, .3, "0–30%"), (.3, .5, "30–50%"), (.5, .7, "50–70%"), (.7, .9, "70–90%"), (.9, 1.01, "90–100%")]
    rows = []
    for i, (lo, hi, label) in enumerate(buckets):
        sub = [x for x in rests if x["max_hp"] and lo <= x["hp_before"] / x["max_hp"] < hi]
        c = collections.Counter(x["choice"] for x in sub)
        n = len(sub)
        rows.append({"bucket": label, "order": i, "visits": n, "heal": c["HEAL"], "smith": c["SMITH"],
                     "other": n - c["HEAL"] - c["SMITH"],
                     "heal_share": round(c["HEAL"] / n, 4) if n else None,
                     "smith_share": round(c["SMITH"] / n, 4) if n else None,
                     "other_share": round((n - c["HEAL"] - c["SMITH"]) / n, 4) if n else None})
    datasets["rest_by_hp"] = rows

    # elite fights in Acts 1-2 by HP on arrival, character and all characters
    rows = []
    for scope, filt, params in ((ch.title(), FC, P2), ("All characters", F, P1)):
        xs = [dict(x) for x in con.execute(f"""SELECT f.hp_before*1.0/f.max_hp AS hp, f.act,
                f.is_last_floor AND NOT r.win AND NOT r.abandoned AS died, r.win, r.abandoned,
                (SELECT MAX(act) FROM floors g WHERE g.run_id = f.run_id) AS max_act
                FROM floors f JOIN runs r USING(run_id)
                WHERE {filt} AND f.room_type = 'elite' AND f.act IN (1, 2)""", params)]
        for i, (lo, hi, label) in enumerate(((0, .5, "Under 50%"), (.5, .7, "50–70%"), (.7, 1.01, "70% and up"))):
            sub = [x for x in xs if lo <= x["hp"] < hi and not x["abandoned"]]
            died = sum(x["died"] for x in sub)
            surv = sum(1 for x in sub if x["max_act"] > x["act"] or x["win"])
            rows.append({"scope": scope, "bucket": label, "order": i, "n": len(sub), "died": died,
                         "died_rate": round(died / len(sub), 4) if sub else None,
                         "survived_act_rate": round(surv / len(sub), 4) if sub else None})
    datasets["elite_by_hp"] = rows

    # card ranking: top 15, SKIP, bottom 10 (cards with 10+ comparisons)
    rank = []
    with open(PROJECT / f"reports/phase1/card-ranking-{ch.lower()}.csv") as f:
        for r in csv.DictReader(f):
            rank.append({"card": r["card"], "strength": float(r["strength"]), "comparisons": int(r["comparisons"])})
    offers = collections.defaultdict(lambda: [0, 0])
    for o in con.execute(f"""SELECT o.card_id, o.picked FROM card_offers o JOIN runs r USING(run_id)
                             WHERE {FC} AND o.source = 'reward'""", P2):
        k = o["card_id"].split(".", 1)[-1]
        offers[k][0] += 1
        offers[k][1] += o["picked"]
    rank = [r for r in rank if r["comparisons"] >= 10]
    rank.sort(key=lambda r: -r["strength"])
    skip = next(r for r in rank if r["card"] == "SKIP")
    cards = [r for r in rank if r["card"] != "SKIP"]
    chosen = cards[:15] + [skip] + [r for r in cards if r["strength"] < skip["strength"]][-10:]
    rows = []
    for r in chosen:
        off, pick = offers.get(r["card"], (0, 0))
        rows.append({"card": r["card"].replace("_", " ").title() if r["card"] != "SKIP" else "Skip",
                     "strength": round(r["strength"], 3), "comparisons": r["comparisons"],
                     "offered": off if r["card"] != "SKIP" else None, "picked": pick if r["card"] != "SKIP" else None,
                     "pick_rate": round(pick / off, 4) if off else None,
                     "group": "skip" if r["card"] == "SKIP" else ("above" if r["strength"] > skip["strength"] else "below")})
    datasets["card_ranking"] = rows

    # skip rates by act and deck size
    groups = collections.defaultdict(list)
    for o in con.execute(f"""SELECT o.offer_group, o.act, o.deck_size_before, o.picked FROM card_offers o
                             JOIN runs r USING(run_id) WHERE {FC} AND o.source = 'reward'""", P2):
        groups[o["offer_group"]].append(dict(o))
    acts, sizes = collections.defaultdict(lambda: [0, 0]), collections.defaultdict(lambda: [0, 0])
    size_order = ["Under 15", "15–19", "20–24", "25–29", "30+"]
    for os_ in groups.values():
        skipped = not any(o["picked"] for o in os_)
        a = f"Act {os_[0]['act']}"
        s = os_[0]["deck_size_before"]
        b = size_order[0 if s < 15 else 1 if s < 20 else 2 if s < 25 else 3 if s < 30 else 4]
        acts[a][0] += 1
        acts[a][1] += skipped
        sizes[b][0] += 1
        sizes[b][1] += skipped
    rows = [{"dimension": "act", "bucket": k, "order": i, "screens": v[0], "skipped": v[1], "rate": round(v[1] / v[0], 4)}
            for i, (k, v) in enumerate(sorted(acts.items()))]
    rows += [{"dimension": "deck", "bucket": k, "order": i, "screens": sizes[k][0], "skipped": sizes[k][1],
              "rate": round(sizes[k][1] / sizes[k][0], 4)} for i, k in enumerate(size_order) if sizes[k][0]]
    datasets["skip_rates"] = rows

    # summary figures quoted in sentences
    act1 = sum(1 for d in deaths if d["act"] == 1)
    act1_boss = sum(1 for d in deaths if d["act"] == 1 and d["map_point_type"] == "boss")
    pools = collections.Counter("boss" if (runs[d["run_id"]]["killed_by_encounter"] or "").endswith("_BOSS")
                                else "elite" if (runs[d["run_id"]]["killed_by_encounter"] or "").endswith("_ELITE")
                                else "hallway" for d in deaths)
    hs = [(x["hp_before"] / x["max_hp"], 1 if x["choice"] == "HEAL" else 0) for x in rests
          if x["choice"] in ("HEAL", "SMITH") and x["max_hp"]]
    hsb = [(x["hp_before"] / x["max_hp"], 1 if x["choice"] == "HEAL" else 0) for x in rests
           if x["choice"] in ("HEAL", "SMITH") and x["max_hp"] and x["next_is_boss"]]
    hp15 = next(r for r in datasets["hp_trajectory"] if r["floor"] == 15)
    removal_runs = con.execute(f"""SELECT COUNT(DISTINCT c.run_id) FROM deck_changes c JOIN runs r USING(run_id)
                                  WHERE {FC} AND c.change = 'removed'""", P2).fetchone()[0]
    vantom = next((r for r in datasets["boss_elite_danger"] if r["encounter"] == "VANTOM_BOSS"), None)
    elite_all = {r["bucket"]: r for r in datasets["elite_by_hp"] if r["scope"] == "All characters"}
    summary = [
        ("runs", len(runs), "Solo runs on this version"),
        ("wins", sum(r["win"] for r in runs.values()), "Wins"),
        ("deaths", len(deaths), "Runs that ended in death"),
        ("act1_deaths", act1, "Deaths in Act 1"),
        ("act1_death_share", round(act1 / len(deaths), 4), "Share of deaths in Act 1"),
        ("act1_boss_deaths", act1_boss, "Deaths at the Act 1 boss"),
        ("boss_deaths", pools["boss"], "Deaths to bosses"),
        ("elite_deaths", pools["elite"], "Deaths to elites"),
        ("hallway_deaths", pools["hallway"], "Deaths in hallway fights"),
        ("vantom_fights", vantom["n"] if vantom else None, "Vantom fights"),
        ("vantom_deaths", vantom["deaths"] if vantom else None, "Vantom deaths"),
        ("vantom_median", vantom["median_dmg"] if vantom else None, "Vantom median damage"),
        ("vantom_all_median", vantom["all_median_dmg"] if vantom else None, "Vantom median damage, all characters"),
        ("rest_threshold", round(logistic_threshold(hs)[0], 4), "HP at which heal and smith are equally likely"),
        ("rest_threshold_boss", round(logistic_threshold(hsb)[0], 4), "Same, right before a boss"),
        ("hp15_win", hp15["win_median"], "Median HP after floor 15, wins"),
        ("hp15_loss", hp15["loss_median"], "Median HP after floor 15, losses"),
        ("removal_runs", removal_runs, "Runs with at least one card removal"),
        ("elite_low_died", elite_all["Under 50%"]["died_rate"], "Elite fights entered under 50% HP that ended the run, all characters"),
        ("elite_high_died", elite_all["70% and up"]["died_rate"], "Same, entered at 70% HP or more"),
        ("elite_low_n", elite_all["Under 50%"]["n"], "Elite fights entered under 50% HP, all characters"),
    ]
    datasets["summary"] = [{"metric": m, "value": v, "label": l} for m, v, l in summary]

    code = SELF.read_text()
    for name, rows in datasets.items():
        meta = [{"label": SELF.name, "value": code, "type": "code", "lang": "python"},
                {"label": "Input", "value": f"data/runs.db (run history, {ch.title()} {args.build}, solo runs)"}]
        if name == "card_ranking":
            meta.append({"label": "Input", "value": f"reports/phase1/card-ranking-{ch.lower()}.csv (Bradley-Terry fit)"})
        (out / f"{name}.json").write_text(json.dumps({"rows": rows, "meta": meta}, ensure_ascii=False))
        print(f"{name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
