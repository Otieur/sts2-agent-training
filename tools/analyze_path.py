#!/usr/bin/env python3
"""Phase 1 E4: pathing profile, rest-site policy, shops, events, Ancients and potions.

Usage: python3 -I tools/analyze_path.py [--character IRONCLAD] [--build v0.107.1] [--out reports/phase1]
"""
import argparse
import collections
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import (CAUTIONS, DATA, MAIN_BUILD, PROJECT, connect, md_table, mean, median, num,  # noqa: E402
                    pct, short, write_csv)

ROOM_ORDER = ["monster", "elite", "unknown", "shop", "rest_site", "treasure"]


def logistic_threshold(points):
    """points: list of (x, y) with y in {0,1}. Fit p(y=1) = sigmoid(a + b x); return x where p = 0.5."""
    if len(points) < 10:
        return float("nan"), float("nan")
    a, b = 0.0, 0.0
    lr = 0.5
    for _ in range(20000):
        ga = gb = 0.0
        for x, y in points:
            p = 1 / (1 + math.exp(-(a + b * x)))
            ga += (y - p)
            gb += (y - p) * x
        a += lr * ga / len(points)
        b += lr * gb / len(points)
    return (-a / b if b else float("nan")), b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", default="IRONCLAD")
    ap.add_argument("--build", default=MAIN_BUILD)
    ap.add_argument("--out", default=str(PROJECT / "reports/phase1"))
    args = ap.parse_args()
    ch = args.character.upper()
    out = Path(args.out)
    con = connect()
    run_filter = "r.n_players = 1 AND r.build_id = ? AND r.character = ?"
    P = [args.build, ch]
    runs = {r["run_id"]: dict(r) for r in con.execute(f"SELECT * FROM runs r WHERE {run_filter}", P)}
    floors = [dict(r) for r in con.execute(f"SELECT f.* FROM floors f JOIN runs r USING(run_id) WHERE {run_filter} "
                                           "ORDER BY f.run_id, f.floor", P)]
    by_run = collections.defaultdict(list)
    for f in floors:
        by_run[f["run_id"]].append(f)

    L = [f"# Pathing, Rest, Shops, Events and Potions: {ch.title()} ({args.build})", "",
         f"Runs: {len(runs)} solo. Outcome comparisons use finished runs only.", "", CAUTIONS, ""]

    # --- S1: pathing profile ------------------------------------------------------------
    # Only count an act if the run completed it (reached the next act or won)
    act_counts = collections.defaultdict(lambda: collections.defaultdict(list))  # act -> outcome -> [Counter]
    elites_vs_next = collections.defaultdict(lambda: collections.Counter())  # (act, n_elites) -> reached/total
    hp_end_act = collections.defaultdict(lambda: collections.defaultdict(list))
    for rid, fs in by_run.items():
        r = runs[rid]
        if r["abandoned"]:
            continue
        outcome = "win" if r["win"] else "loss"
        max_act = max(f["act"] for f in fs)
        for act in sorted({f["act"] for f in fs}):
            af = [f for f in fs if f["act"] == act]
            completed = act < max_act or r["win"]
            c = collections.Counter(f["map_point_type"] for f in af)
            if completed:
                act_counts[act][outcome].append(c)
                last = af[-1]
                hp_end_act[act][outcome].append(last["hp_after"] / last["max_hp"] if last["max_hp"] else 0)
            # elites fought before the boss, against surviving the act
            n_el = c.get("elite", 0)
            key = (act, min(n_el, 3))
            elites_vs_next[key]["total"] += 1
            elites_vs_next[key]["survived"] += int(completed)

    path_rows = []
    for act in sorted(act_counts):
        for outcome in ("win", "loss"):
            cs = act_counts[act][outcome]
            if not cs:
                continue
            path_rows.append([act, outcome, len(cs)] + [num(mean(c.get(t, 0) for c in cs), 1) for t in ROOM_ORDER]
                             + [pct(median(hp_end_act[act][outcome]))])
    L += ["## Room mix per completed act", "",
          "Means per completed act. An act counts only if the run got past its boss.", "",
          md_table(["Act", "Run outcome", "Acts", "Monsters", "Elites", "? rooms", "Shops", "Rest sites", "Treasure",
                    "Median HP% after boss"], path_rows), "",
          "## Elites fought in an act, against surviving it", "",
          md_table(["Act", "Elites (3 = 3+)", "Acts", "Survived the act", "Rate"],
                   [[a, n, v["total"], v["survived"], pct(v["survived"] / v["total"])]
                    for (a, n), v in sorted(elites_vs_next.items())]), "",
          "Survival here is confounded: strong decks both take more elites and survive. It does not show that "
          "elites are safe.", ""]

    # --- S2: rest-site policy ------------------------------------------------------------
    rests = [dict(r) for r in con.execute(f"SELECT c.* FROM rest_choices c JOIN runs r USING(run_id) WHERE {run_filter}", P)]
    buckets = [(0, 0.3, "0–30%"), (0.3, 0.5, "30–50%"), (0.5, 0.7, "50–70%"), (0.7, 0.9, "70–90%"), (0.9, 1.01, "90–100%")]
    rest_rows = []
    for lo, hi, label in buckets:
        sub = [x for x in rests if x["max_hp"] and lo <= x["hp_before"] / x["max_hp"] < hi]
        c = collections.Counter(x["choice"] for x in sub)
        sub_boss = [x for x in sub if x["next_is_boss"]]
        cb = collections.Counter(x["choice"] for x in sub_boss)
        n = len(sub)
        rest_rows.append([label, n, pct(c["HEAL"] / n) if n else "-", pct(c["SMITH"] / n) if n else "-",
                          n - c["HEAL"] - c["SMITH"], len(sub_boss),
                          pct(cb["HEAL"] / len(sub_boss)) if sub_boss else "-"])
    hs = [(x["hp_before"] / x["max_hp"], 1 if x["choice"] == "HEAL" else 0) for x in rests
          if x["choice"] in ("HEAL", "SMITH") and x["max_hp"]]
    thr, slope = logistic_threshold(hs)
    hs_boss = [(x["hp_before"] / x["max_hp"], 1 if x["choice"] == "HEAL" else 0) for x in rests
               if x["choice"] in ("HEAL", "SMITH") and x["max_hp"] and x["next_is_boss"]]
    thr_boss, _ = logistic_threshold(hs_boss)
    hs_other = [(x["hp_before"] / x["max_hp"], 1 if x["choice"] == "HEAL" else 0) for x in rests
                if x["choice"] in ("HEAL", "SMITH") and x["max_hp"] and not x["next_is_boss"]]
    thr_other, _ = logistic_threshold(hs_other)
    other_choices = collections.Counter(x["choice"] for x in rests if x["choice"] not in ("HEAL", "SMITH"))
    L += ["## Rest sites", "",
          md_table(["HP on arrival", "Visits", "Heal", "Smith", "Other", "Before boss", "Heal before boss"], rest_rows), "",
          f"- **Estimated threshold** (logistic fit, HEAL vs SMITH): the Player is equally likely to heal or smith at "
          f"**{pct(thr)} HP** (n={len(hs)}).",
          f"  - Right before a boss: {pct(thr_boss)} (n={len(hs_boss)}). Other rest sites: {pct(thr_other)} (n={len(hs_other)}).",
          f"- Other options used: {', '.join(f'{k} ×{v}' for k, v in other_choices.most_common()) or 'none'}.", ""]

    # --- S3: shops ----------------------------------------------------------------------
    shops = [dict(r) for r in con.execute(f"SELECT s.* FROM shop_visits s JOIN runs r USING(run_id) WHERE {run_filter}", P)]
    bought_relics = collections.Counter(r["relic_id"] for r in con.execute(
        f"SELECT e.relic_id FROM relic_events e JOIN runs r USING(run_id) WHERE {run_filter} AND e.kind='bought'", P))
    bought_potions = collections.Counter(r["potion_id"] for r in con.execute(
        f"SELECT e.potion_id FROM potion_events e JOIN runs r USING(run_id) WHERE {run_filter} AND e.kind='bought'", P))
    shop_rows = []
    for act in (1, 2, 3):
        sub = [s for s in shops if s["act"] == act]
        if not sub:
            continue
        shop_rows.append([act, len(sub), num(median([s["gold_before"] for s in sub]), 0),
                          num(median([s["gold_spent"] for s in sub]), 0),
                          pct(sum(1 for s in sub if s["gold_spent"] == 0) / len(sub)),
                          sum(s["cards_bought"] for s in sub), sum(s["colorless_bought"] for s in sub),
                          sum(s["relics_bought"] for s in sub), sum(s["potions_bought"] for s in sub),
                          sum(s["removals"] for s in sub)])
    L += ["## Shops", "",
          md_table(["Act", "Visits", "Median gold on arrival", "Median spent", "Bought nothing", "Cards", "Colorless",
                    "Relics", "Potions", "Removals"], shop_rows), "",
          "Most bought relics: " + (", ".join(f"{short(k)} ×{v}" for k, v in bought_relics.most_common(10)) or "none") + ".", "",
          "Most bought potions: " + (", ".join(f"{short(k)} ×{v}" for k, v in bought_potions.most_common(8)) or "none") + ".", ""]

    # --- S4: events and Ancients --------------------------------------------------------
    ev = [dict(r) for r in con.execute(f"SELECT e.* FROM event_choices e JOIN runs r USING(run_id) WHERE {run_filter}", P)]
    by_event = collections.defaultdict(list)
    for e in ev:
        by_event[e["event_id"] or "?"].append(e)
    ev_rows = []
    for eid, es in sorted(by_event.items(), key=lambda kv: -len(kv[1])):
        choices = collections.Counter(".".join((e["choice_key"] or "?").split(".")[-2:-1]) or e["choice_key"] for e in es)
        ev_rows.append([short(eid), len(es), "; ".join(f"{k} ×{v}" for k, v in choices.most_common(4)),
                        num(mean(e["hp_change"] for e in es), 1), num(mean(e["gold_change"] for e in es), 0)])
    anc = [dict(r) for r in con.execute(f"SELECT a.* FROM ancient_choices a JOIN runs r USING(run_id) WHERE {run_filter}", P)]
    anc_stat = collections.defaultdict(lambda: [0, 0])
    anc_by = collections.Counter()
    for a in anc:
        anc_stat[a["option"]][0] += 1
        anc_stat[a["option"]][1] += a["chosen"]
        anc_by[short(a["ancient_id"])] += a["chosen"]
    anc_rows = sorted(([k, v[0], v[1], pct(v[1] / v[0])] for k, v in anc_stat.items() if v[0] >= 3),
                      key=lambda r: (-(r[2] / r[1]), -r[1]))
    L += ["## Events", "",
          "Choice names are the option keys from the game's localisation. The HP and gold columns are mean net "
          "changes over the floor.", "",
          md_table(["Event", "Visits", "Choices", "Mean HP change", "Mean gold change"], ev_rows[:25]), "",
          "## Ancients", "",
          f"Ancient visits by Ancient: {', '.join(f'{k} ×{v}' for k, v in anc_by.most_common())}.", "",
          "Options offered 3+ times, by how often the Player took them:", "",
          md_table(["Option", "Offered", "Chosen", "Rate"], anc_rows[:30]), ""]

    # --- S5: potions --------------------------------------------------------------------
    pe = [dict(r) for r in con.execute(f"SELECT e.* FROM potion_events e JOIN runs r USING(run_id) WHERE {run_filter}", P)]
    used_where = collections.Counter(e["source"] for e in pe if e["kind"] == "used")
    discarded = collections.Counter(e["potion_id"] for e in pe if e["kind"] == "discarded")
    offered = [e for e in pe if e["kind"] == "offered"]
    off_stat = collections.defaultdict(lambda: [0, 0])
    for e in offered:
        off_stat[e["potion_id"]][0] += 1
        off_stat[e["potion_id"]][1] += e["picked"] or 0
    fights_by_type = collections.Counter(f["room_type"] for f in floors if f["room_type"] in ("monster", "elite", "boss"))
    # potions held at death: from raw files
    held = []
    for rid, r in runs.items():
        if r["win"] or r["abandoned"]:
            continue
        raw = json.loads((DATA / "raw" / f"{rid}.run").read_text())
        held.append(len(raw["players"][0].get("potions", [])))
    L += ["## Potions", "",
          md_table(["Room type", "Potions used", "Fights", "Potions per fight"],
                   [[t, used_where.get(t, 0), fights_by_type.get(t, 0),
                     num(used_where.get(t, 0) / fights_by_type[t], 2) if fights_by_type.get(t) else "-"]
                    for t in ("monster", "elite", "boss")]), "",
          f"- Potions still held at death: mean {num(mean(held), 1)}, and {sum(1 for h in held if h >= 1)}/{len(held)} "
          f"deaths had at least one unused potion.",
          f"- Discarded: {', '.join(f'{short(k)} ×{v}' for k, v in discarded.most_common(6)) or 'none'}.", "",
          "Potion rewards most often left behind (offered 4+ times):", "",
          md_table(["Potion", "Offered", "Taken", "Rate"],
                   sorted(([short(k), v[0], v[1], pct(v[1] / v[0])] for k, v in off_stat.items() if v[0] >= 4),
                          key=lambda r: (r[2] / r[1], -r[1]))[:10]), ""]

    (out / f"path-{ch.lower()}.md").write_text("\n".join(L))
    write_csv(out / f"rest-{ch.lower()}.csv", ["run_id", "floor", "act", "choice", "hp_before", "max_hp", "next_is_boss"],
              [[x["run_id"], x["floor"], x["act"], x["choice"], x["hp_before"], x["max_hp"], x["next_is_boss"]] for x in rests])
    print(f"{ch}: rest threshold {thr:.2f} (boss {thr_boss:.2f}, other {thr_other:.2f}); {len(shops)} shops; {len(ev)} event choices")


if __name__ == "__main__":
    main()
