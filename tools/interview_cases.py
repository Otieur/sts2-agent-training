#!/usr/bin/env python3
"""Phase 1 E8.S1: select interview cases from the run history.

Categories:
  A. Picks that go against the Player's own implied ranking (Bradley-Terry from analyze_cards.py)
  B. Rest-site choices right before a death or a boss at low HP
  C. Skips of cards the Player usually takes
  D. Decisions in the floors just before a death
Recent runs are preferred, because the Player is more likely to remember them.

Usage: python3 -I tools/interview_cases.py [--character IRONCLAD] [--build v0.107.1] [--per-category 4]
"""
import argparse
import collections
import csv
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import MAIN_BUILD, PROJECT, connect, is_starter, short  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", default="IRONCLAD")
    ap.add_argument("--build", default=MAIN_BUILD)
    ap.add_argument("--per-category", type=int, default=4)
    ap.add_argument("--out", default=str(PROJECT / "reports/phase1"))
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
    snaps = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    for s in con.execute(f"SELECT s.* FROM deck_snapshots s JOIN runs r USING(run_id) WHERE {run_filter}", P):
        key = short(s["card_id"]) + ("+" if s["upgrade_level"] else "")
        snaps[s["run_id"]][s["floor"]][key] += s["count"]
    relics = collections.defaultdict(list)
    for r in con.execute(f"SELECT x.* FROM final_relics x JOIN runs r USING(run_id) WHERE {run_filter}", P):
        relics[r["run_id"]].append((short(r["relic_id"]), r["floor_added"] or 0))

    rank_file = out / f"card-ranking-{ch.lower()}.csv"
    if not rank_file.exists():
        raise SystemExit("run tools/analyze_cards.py first")
    strength, comps = {}, {}
    with open(rank_file) as f:
        for row in csv.DictReader(f):
            strength[row["card"]] = float(row["strength"])
            comps[row["card"]] = int(row["comparisons"])
    pick_rate = {}
    with open(out / f"card-picks-{ch.lower()}.csv") as f:
        for row in csv.DictReader(f):
            pick_rate[row["card"]] = (float(row["pick_rate"]), int(row["offered"]))
    skip_s = strength["SKIP"]

    def date(rid):
        return datetime.datetime.fromtimestamp(runs[rid]["start_time"]).strftime("%Y-%m-%d")

    def deck_summary(rid, floor):
        d = snaps[rid].get(floor - 1, collections.Counter())
        basics = {k: v for k, v in d.items() if is_starter("CARD." + k.rstrip("+"), ch)}
        others = {k: v for k, v in d.items() if k not in basics}
        b = ", ".join(f"{k}×{v}" if v > 1 else k for k, v in sorted(basics.items()))
        o = ", ".join(f"{k}×{v}" if v > 1 else k for k, v in sorted(others.items()))
        return f"{sum(d.values())} cards. Basics: {b}. Others: {o or 'none'}."

    def relic_summary(rid, floor):
        return ", ".join(r for r, fa in relics[rid] if fa < floor) or "none"

    def outcome(rid, floor):
        r = runs[rid]
        last = max(floors[rid])
        if r["win"]:
            return "Run was won."
        if r["abandoned"]:
            return f"Run was abandoned on floor {last}."
        f = floors[rid][last]
        gap = last - floor
        when = "on the next floor" if gap == 1 else ("on this floor" if gap == 0 else f"{gap} floors later")
        return f"Died {when} (floor {last}) to {short(r['killed_by_encounter'] or f['model_id'])}."

    def header(rid, floor):
        f = floors[rid][floor]
        r = runs[rid]
        return (f"Run {date(rid)}, A{r['ascension']}, floor {floor} (act {f['act']}), "
                f"HP {f['hp_before']}/{f['max_hp']}, gold {f['gold_before']}.")

    def recency(rid):
        return runs[rid]["start_time"]

    cases = {"A": [], "B": [], "C": [], "D": []}

    offers = collections.defaultdict(list)
    for o in con.execute(f"""SELECT o.* FROM card_offers o JOIN runs r USING(run_id)
                             WHERE {run_filter} AND o.source='reward'""", P):
        offers[o["offer_group"]].append(dict(o))

    def describe_offer(os_):
        parts = []
        for o in os_:
            name = short(o["card_id"]) + ("+" if o["upgrade_level"] else "")
            parts.append(f"**{name}**" if o["picked"] else name)
        return ", ".join(parts) + ("  (skipped)" if not any(o["picked"] for o in os_) else "")

    for gid, os_ in offers.items():
        rid, floor = os_[0]["run_id"], os_[0]["floor"]
        picked = [o for o in os_ if o["picked"]]
        best = max(os_, key=lambda o: strength.get(short(o["card_id"]), -9))
        best_s = strength.get(short(best["card_id"]), -9)
        if comps.get(short(best["card_id"]), 0) < 10:
            continue
        if picked:
            p = picked[0]
            ps = strength.get(short(p["card_id"]), -9)
            if best_s - ps >= 1.5 and best is not p:
                cases["A"].append((best_s - ps, recency(rid), rid, floor,
                                   f"Card reward: {describe_offer(os_)}. Took {short(p['card_id'])} over "
                                   f"{short(best['card_id'])}, which the Player usually ranks higher "
                                   f"({best_s:+.1f} vs {ps:+.1f})."))
        else:
            pr, n = pick_rate.get(short(best["card_id"]), (0, 0))
            if best_s - skip_s >= 2.0 and pr >= 0.55 and n >= 10:
                cases["C"].append((pr, recency(rid), rid, floor,
                                   f"Card reward: {describe_offer(os_)}. Skipped, although "
                                   f"{short(best['card_id'])} is usually taken ({pr:.0%} of {n} offers)."))

    for r in con.execute(f"SELECT c.* FROM rest_choices c JOIN runs r USING(run_id) WHERE {run_filter}", P):
        r = dict(r)
        rid, floor = r["run_id"], r["floor"]
        hp_pct = r["hp_before"] / r["max_hp"]
        last = max(floors[rid])
        died_soon = not runs[rid]["win"] and not runs[rid]["abandoned"] and last - floor <= 2
        if r["choice"] == "SMITH" and (r["next_is_boss"] and hp_pct < 0.55 or died_soon and hp_pct < 0.6):
            up = r["upgraded"].replace("CARD.", "") or "?"
            cases["B"].append((1 - hp_pct + (0.5 if died_soon else 0), recency(rid), rid, floor,
                               f"Rest site{' before the boss' if r['next_is_boss'] else ''} at {hp_pct:.0%} HP: "
                               f"chose SMITH ({up}) instead of resting."))

    for rid, r in runs.items():
        if r["win"] or r["abandoned"]:
            continue
        last = max(floors[rid])
        for floor in range(max(2, last - 3), last):
            f = floors[rid][floor]
            if f["map_point_type"] == "shop":
                bought = [short(x["card_id"]) for x in con.execute(
                    "SELECT card_id FROM card_offers WHERE run_id=? AND floor=? AND source='shop' AND picked=1", (rid, floor))]
                rel = [short(x["relic_id"]) for x in con.execute(
                    "SELECT relic_id FROM relic_events WHERE run_id=? AND floor=? AND kind='bought'", (rid, floor))]
                cases["D"].append((0.5, recency(rid), rid, floor,
                                   f"Shop with {f['gold_before']} gold, {last - floor} floor(s) before dying: spent "
                                   f"{f['gold_spent']} (cards: {', '.join(bought) or 'none'}; relics: {', '.join(rel) or 'none'})."))
            if f["map_point_type"] in ("elite",) and f["damage_taken"] / f["max_hp"] >= 0.35:
                cases["D"].append((f["damage_taken"] / f["max_hp"], recency(rid), rid, floor,
                                   f"Took the elite {short(f['model_id'])} and lost {f['damage_taken']} HP "
                                   f"({f['damage_taken'] / f['max_hp']:.0%} of max), {last - floor} floor(s) before dying."))

    chosen = []
    used_runs = collections.Counter()
    for cat in ("B", "A", "C", "D"):
        pool = sorted(cases[cat], key=lambda t: (-t[0], -t[1]))
        taken = 0
        for score, _, rid, floor, text in pool:
            if used_runs[rid] >= 2 or any(c[2] == rid and c[3] == floor for c in chosen):
                continue
            chosen.append((cat, score, rid, floor, text))
            used_runs[rid] += 1
            taken += 1
            if taken >= args.per_category:
                break

    titles = {"A": "Pick against the Player's own ranking", "B": "Rest site before a boss or a death",
              "C": "Skip of a card the Player usually takes", "D": "Decision shortly before a death"}
    L = [f"# Interview Cases: {ch.title()} ({args.build})", "",
         "Selected by `tools/interview_cases.py`. Answers go in `knowledge/player-reasoning.md`, linked by case ID.",
         ""]
    for i, (cat, score, rid, floor, text) in enumerate(chosen, 1):
        L += [f"## Case {i} ({cat}: {titles[cat]})", "",
              f"- **When:** {header(rid, floor)}",
              f"- **Deck:** {deck_summary(rid, floor)}",
              f"- **Relics:** {relic_summary(rid, floor)}",
              f"- **Decision:** {text}",
              f"- **What happened:** {outcome(rid, floor)}",
              f"- **Run ID:** `{rid}`", ""]
    (out / f"interview-cases-{ch.lower()}.md").write_text("\n".join(L))
    print(f"{ch}: candidates A={len(cases['A'])} B={len(cases['B'])} C={len(cases['C'])} D={len(cases['D'])}; "
          f"selected {len(chosen)}")


if __name__ == "__main__":
    main()
