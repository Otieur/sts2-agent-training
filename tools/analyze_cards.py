#!/usr/bin/env python3
"""Phase 1 E2: card pick rates, implied priority ranking (Bradley-Terry), context effects,
outcome association, upgrade and removal priorities.

Usage: python3 -I tools/analyze_cards.py [--character IRONCLAD] [--build v0.107.1] [--out reports/phase1]
"""
import argparse
import collections
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import (CAUTIONS, MAIN_BUILD, PROJECT, asc_band, connect, is_starter, md_table,  # noqa: E402
                    median, num, pct, short, wilson, write_csv)

SKIP = "SKIP"


def bradley_terry(groups, iters=500, prior=1.0):
    """groups: list of (items, winners). Each winner beats every non-winner in its group.
    A virtual opponent with fixed strength 1 gives each item `prior` wins and losses (regularisation).
    Returns {item: (log_strength, n_comparisons, wins)}."""
    wins = collections.Counter()
    pair_n = collections.Counter()
    comps = collections.Counter()
    for items, winners in groups:
        losers = [i for i in items if i not in winners]
        for w in winners:
            for l in losers:
                wins[w] += 1
                pair_n[frozenset((w, l))] += 1
                comps[w] += 1
                comps[l] += 1
    items = sorted(comps)
    p = {i: 1.0 for i in items}
    neighbours = collections.defaultdict(list)
    for pair, n in pair_n.items():
        a, b = tuple(pair)
        neighbours[a].append((b, n))
        neighbours[b].append((a, n))
    for _ in range(iters):
        new = {}
        for i in items:
            denom = sum(n / (p[i] + p[j]) for j, n in neighbours[i]) + 2 * prior / (p[i] + 1.0)
            new[i] = (wins[i] + prior) / denom
        # normalise to geometric mean 1
        g = math.exp(sum(math.log(v) for v in new.values()) / len(new))
        p = {i: v / g for i, v in new.items()}
    return {i: (math.log(p[i]), comps[i], wins[i]) for i in items}


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

    offers = [dict(r) for r in con.execute(f"""
        SELECT o.*, r.ascension FROM card_offers o JOIN runs r USING(run_id)
        WHERE {run_filter} AND o.source = 'reward'""", P)]

    # Deck copies of each card at the start of each floor (snapshot of floor-1)
    snaps = collections.defaultdict(collections.Counter)
    for r in con.execute(f"""SELECT s.run_id, s.floor, s.card_id, SUM(s.count) AS n FROM deck_snapshots s
                             JOIN runs r USING(run_id) WHERE {run_filter}
                             GROUP BY s.run_id, s.floor, s.card_id""", P):
        snaps[(r["run_id"], r["floor"])][r["card_id"]] = r["n"]

    def copies_before(run_id, floor, card_id):
        snap = snaps.get((run_id, floor - 1))
        if snap is None:  # floor 1: starter deck
            return 0
        return snap.get(card_id, 0)

    # --- S1: offer / pick table -------------------------------------------------------
    stat = collections.defaultdict(lambda: {"off": 0, "pick": 0, "act": collections.Counter(),
                                            "act_pick": collections.Counter(), "upg_off": 0, "upg_pick": 0,
                                            "dup_off": 0, "dup_pick": 0})
    for o in offers:
        s = stat[o["card_id"]]
        s["off"] += 1
        s["pick"] += o["picked"]
        s["act"][o["act"]] += 1
        s["act_pick"][o["act"]] += o["picked"]
        if o["upgrade_level"]:
            s["upg_off"] += 1
            s["upg_pick"] += o["picked"]
        if copies_before(o["run_id"], o["floor"], o["card_id"]) > 0:
            s["dup_off"] += 1
            s["dup_pick"] += o["picked"]

    pick_rows = []
    for cid, s in stat.items():
        lo, hi = wilson(s["pick"], s["off"])
        row = [short(cid), s["off"], s["pick"], round(s["pick"] / s["off"], 3), round(lo, 3), round(hi, 3)]
        for a in (1, 2, 3):
            n = s["act"][a]
            row += [n, round(s["act_pick"][a] / n, 3) if n else ""]
        pick_rows.append(row)
    pick_rows.sort(key=lambda r: (-r[3], -r[1]))
    write_csv(out / f"card-picks-{ch.lower()}.csv",
              ["card", "offered", "picked", "pick_rate", "ci_low", "ci_high",
               "act1_offered", "act1_rate", "act2_offered", "act2_rate", "act3_offered", "act3_rate"], pick_rows)

    # --- S2: Bradley-Terry ranking ------------------------------------------------------
    groups = collections.defaultdict(list)
    for o in offers:
        groups[o["offer_group"]].append(o)
    bt_groups = []
    skip_by_act = collections.Counter()
    screens_by_act = collections.Counter()
    skip_by_size = collections.Counter()
    screens_by_size = collections.Counter()
    for gid, os_ in groups.items():
        items = [o["card_id"] for o in os_] + [SKIP]
        winners = [o["card_id"] for o in os_ if o["picked"]] or [SKIP]
        bt_groups.append((items, winners))
        act = os_[0]["act"]
        size = os_[0]["deck_size_before"]
        bucket = "<15" if size < 15 else "15-19" if size < 20 else "20-24" if size < 25 else "25-29" if size < 30 else "30+"
        screens_by_act[act] += 1
        screens_by_size[bucket] += 1
        if winners == [SKIP]:
            skip_by_act[act] += 1
            skip_by_size[bucket] += 1
    bt = bradley_terry(bt_groups)
    skip_strength = bt[SKIP][0]
    ranked = sorted(bt.items(), key=lambda kv: -kv[1][0])
    enough = [(c, v) for c, v in ranked if v[1] >= 5]
    thin = [(c, v) for c, v in ranked if v[1] < 5]

    rank_lines = [f"# Implied Card Priority: {ch.title()} ({args.build})", "",
                  f"From {len(bt_groups)} card reward screens in {len(runs)} runs. Each screen counts as head-to-head "
                  "wins for the picked card over each card left behind, plus a win over **SKIP**. A skipped screen "
                  "counts as SKIP beating every card. Strength comes from a Bradley-Terry model (log scale, "
                  "0 = average, regularised with one virtual win and loss per card).", "",
                  "This describes **what the Player picks**, not what wins.", "", CAUTIONS, "",
                  f"**SKIP sits at {skip_strength:+.2f}.** Cards below SKIP are ones the Player would rather skip than take.", "",
                  "## Ranking (5 or more comparisons)", "",
                  md_table(["#", "Card", "Strength", "Comparisons", "Picked", "Offered", "Pick rate", "vs SKIP"],
                           [[i + 1, short(c) if c != SKIP else "**SKIP**", f"{v[0]:+.2f}", v[1],
                             stat[c]["pick"] if c != SKIP else sum(skip_by_act.values()),
                             stat[c]["off"] if c != SKIP else len(bt_groups),
                             pct(stat[c]["pick"] / stat[c]["off"]) if c != SKIP else pct(sum(skip_by_act.values()) / len(bt_groups)),
                             "above" if v[0] > skip_strength else ("—" if c == SKIP else "below")]
                            for i, (c, v) in enumerate(enough)]), "",
                  "## Insufficient data (fewer than 5 comparisons)", "",
                  ", ".join(f"{short(c)} ({v[1]})" for c, v in thin) or "None", ""]
    (out / f"card-ranking-{ch.lower()}.md").write_text("\n".join(rank_lines))
    write_csv(out / f"card-ranking-{ch.lower()}.csv", ["card", "strength", "comparisons", "wins"],
              [[short(c) if c != SKIP else SKIP, round(v[0], 3), v[1], v[2]] for c, v in ranked])

    # --- S3: context effects ------------------------------------------------------------
    upg = [(short(c), s["upg_off"], s["upg_pick"], s["off"] - s["upg_off"], s["pick"] - s["upg_pick"])
           for c, s in stat.items() if s["upg_off"] >= 5 and s["off"] - s["upg_off"] >= 5]
    dup = [(short(c), s["off"] - s["dup_off"], s["pick"] - s["dup_pick"], s["dup_off"], s["dup_pick"])
           for c, s in stat.items() if s["dup_off"] >= 5 and s["off"] - s["dup_off"] >= 5]
    tot_upg_off = sum(s["upg_off"] for s in stat.values())
    tot_upg_pick = sum(s["upg_pick"] for s in stat.values())
    tot_base_off = sum(s["off"] - s["upg_off"] for s in stat.values())
    tot_base_pick = sum(s["pick"] - s["upg_pick"] for s in stat.values())
    tot_dup_off = sum(s["dup_off"] for s in stat.values())
    tot_dup_pick = sum(s["dup_pick"] for s in stat.values())
    tot_new_off = sum(s["off"] - s["dup_off"] for s in stat.values())
    tot_new_pick = sum(s["pick"] - s["dup_pick"] for s in stat.values())

    # --- S4: outcome association --------------------------------------------------------
    finished = {rid: r for rid, r in runs.items() if not r["abandoned"]}
    final = collections.defaultdict(set)
    for r in con.execute(f"SELECT d.run_id, d.card_id FROM final_deck d JOIN runs r USING(run_id) WHERE {run_filter}", P):
        if r["run_id"] in finished:
            final[r["card_id"]].add(r["run_id"])
    outcome_rows = []
    for cid, rids in final.items():
        if is_starter(cid, ch) or len(rids) < 10:
            continue
        with_w = sum(finished[r]["win"] for r in rids)
        without = [r for r in finished if r not in rids]
        wo_w = sum(finished[r]["win"] for r in without)
        bands = []
        for band in ("A0-4", "A5-9", "A10"):
            bw = [r for r in rids if asc_band(finished[r]["ascension"]) == band]
            bo = [r for r in without if asc_band(finished[r]["ascension"]) == band]
            bands.append(f"{sum(finished[r]['win'] for r in bw)}/{len(bw)} vs {sum(finished[r]['win'] for r in bo)}/{len(bo)}")
        outcome_rows.append([short(cid), len(rids), with_w, round(with_w / len(rids), 3), len(without), wo_w,
                             round(wo_w / len(without), 3) if without else ""] + bands)
    outcome_rows.sort(key=lambda r: -(r[3] - (r[6] or 0)))
    write_csv(out / f"card-outcomes-{ch.lower()}.csv",
              ["card", "runs_with", "wins_with", "winrate_with", "runs_without", "wins_without", "winrate_without",
               "A0-4 (with vs without)", "A5-9", "A10"], outcome_rows)

    # --- S5: upgrades and removals ------------------------------------------------------
    ups = [dict(r) for r in con.execute(f"""SELECT c.run_id, c.floor, c.card_id, c.detail FROM deck_changes c
        JOIN runs r USING(run_id) WHERE {run_filter} AND c.change = 'upgraded' ORDER BY c.run_id, c.floor""", P)]
    smith_ups = [u for u in ups if u["detail"] == "rest_site"]
    order = collections.defaultdict(list)
    for u in smith_ups:
        order[u["run_id"]].append(u["card_id"])
    first = collections.Counter(v[0] for v in order.values() if len(v) >= 1)
    second = collections.Counter(v[1] for v in order.values() if len(v) >= 2)
    third = collections.Counter(v[2] for v in order.values() if len(v) >= 3)
    all_smith = collections.Counter(u["card_id"] for u in smith_ups)
    rems = [dict(r) for r in con.execute(f"""SELECT c.run_id, c.floor, c.card_id, c.detail FROM deck_changes c
        JOIN runs r USING(run_id) WHERE {run_filter} AND c.change = 'removed'""", P)]
    rem_counter = collections.Counter(r["card_id"] for r in rems)
    first_rem = {}
    for r in rems:
        first_rem[r["run_id"]] = min(first_rem.get(r["run_id"], 999), r["floor"])
    rem_source = collections.Counter(r["detail"] for r in rems)

    # Shop card purchases
    shop = [dict(r) for r in con.execute(f"""SELECT o.card_id, o.picked FROM card_offers o JOIN runs r USING(run_id)
        WHERE {run_filter} AND o.source = 'shop'""", P)]
    shop_stat = collections.defaultdict(lambda: [0, 0])
    for o in shop:
        shop_stat[o["card_id"]][0] += 1
        shop_stat[o["card_id"]][1] += o["picked"]

    # --- Report -------------------------------------------------------------------------
    top = [r for r in pick_rows if r[1] >= 8][:20]
    bottom = sorted([r for r in pick_rows if r[1] >= 8], key=lambda r: (r[3], -r[1]))[:15]
    L = [f"# Card Analysis: {ch.title()} ({args.build})", "",
         f"Runs: {len(runs)} solo ({len(finished)} finished, {sum(r['win'] for r in runs.values())} wins). "
         f"Card reward screens: {len(bt_groups)}. Cards offered: {len(offers)}.", "", CAUTIONS, "",
         "## Most-picked cards (offered 8+ times)", "",
         md_table(["Card", "Offered", "Picked", "Pick rate", "95% CI"],
                  [[r[0], r[1], r[2], pct(r[3]), f"{pct(r[4])}–{pct(r[5])}"] for r in top]), "",
         "## Least-picked cards (offered 8+ times)", "",
         md_table(["Card", "Offered", "Picked", "Pick rate", "95% CI"],
                  [[r[0], r[1], r[2], pct(r[3]), f"{pct(r[4])}–{pct(r[5])}"] for r in bottom]), "",
         f"Full table: `card-picks-{ch.lower()}.csv`. Head-to-head ranking: `card-ranking-{ch.lower()}.md`.", "",
         "## Skips", "",
         md_table(["Act", "Screens", "Skipped", "Skip rate"],
                  [[a, screens_by_act[a], skip_by_act[a], pct(skip_by_act[a] / screens_by_act[a])]
                   for a in sorted(screens_by_act)]), "",
         md_table(["Deck size", "Screens", "Skipped", "Skip rate"],
                  [[b, screens_by_size[b], skip_by_size[b], pct(skip_by_size[b] / screens_by_size[b])]
                   for b in ("<15", "15-19", "20-24", "25-29", "30+") if screens_by_size[b]]), "",
         "## Context effects", "",
         f"- **Upgraded offers:** picked {pct(tot_upg_pick / tot_upg_off)} of the time (n={tot_upg_off}), against "
         f"{pct(tot_base_pick / tot_base_off)} for base versions (n={tot_base_off}).",
         f"- **Duplicates:** a card already in the deck is picked {pct(tot_dup_pick / tot_dup_off)} of the time "
         f"(n={tot_dup_off}), against {pct(tot_new_pick / tot_new_off)} for new cards (n={tot_new_off}).", "",
         "Cards whose pick rate changes most when a copy is already in the deck (5+ offers each way):", "",
         md_table(["Card", "First copy: offered", "First copy: pick rate", "Already owned: offered",
                   "Already owned: pick rate"],
                  [[c, a, pct(b / a), d, pct(e / d)] for c, a, b, d, e in
                   sorted(dup, key=lambda x: -(x[2] / x[1] - x[4] / x[3]))[:12]]), "",
         "Card types (attack, skill, power) are not in the run files. Context rules by card type wait for the "
         "game data in Phase 2.", "",
         "## Outcome association (weak evidence, `[PLAYER-DATA]`)", "",
         f"Win rate of finished runs whose **final deck** contains the card, against those that do not. "
         f"Cards in 10+ finished runs. Per-band cells read wins/runs with the card vs wins/runs without it.", "",
         md_table(["Card", "Runs with", "Win rate with", "Win rate without", "A0-4", "A5-9", "A10"],
                  [[r[0], r[1], pct(r[3]), pct(r[6]) if r[6] != "" else "-", r[7], r[8], r[9]]
                   for r in outcome_rows[:15]]), "",
         "Survivorship warning: cards picked late only appear in runs that got far, so they look like winners. "
         "Treat every row as a hypothesis.", "",
         "## Upgrade priorities (rest-site Smith)", "",
         md_table(["Card", "Smith upgrades (all)", "As 1st upgrade", "As 2nd", "As 3rd"],
                  [[short(c), n, first.get(c, 0), second.get(c, 0), third.get(c, 0)]
                   for c, n in all_smith.most_common(15)]), "",
         f"Upgrades from other sources (events, relics, Ancients): {len(ups) - len(smith_ups)}.", "",
         "## Removals", "",
         md_table(["Card", "Removed"], [[short(c), n] for c, n in rem_counter.most_common(10)]), "",
         f"Removal sources: {', '.join(f'{k} {v}' for k, v in rem_source.most_common())}. "
         f"Runs with at least one removal: {len(first_rem)}/{len(runs)}; median floor of the first removal: "
         f"{num(median(list(first_rem.values())), 0) if first_rem else '-'}.", "",
         "## Shop card purchases", "",
         md_table(["Card", "Seen in shop", "Bought"],
                  [[short(c), v[0], v[1]] for c, v in sorted(shop_stat.items(), key=lambda kv: -kv[1][1])[:12] if v[1]]),
         ""]
    (out / f"cards-{ch.lower()}.md").write_text("\n".join(L))
    print(f"{ch}: {len(bt_groups)} reward screens, {len(stat)} distinct cards, SKIP strength {skip_strength:+.2f}")


if __name__ == "__main__":
    main()
