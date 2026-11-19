#!/usr/bin/env python3
"""Phase 1 E6: cluster final decks into archetypes (Jaccard distance, average-linkage agglomerative).

Usage: python3 -I tools/analyze_archetypes.py [--character IRONCLAD] [--build v0.107.1] [--k N] [--out reports/phase1]
"""
import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import (CAUTIONS, MAIN_BUILD, PROJECT, connect, is_starter, md_table, median, num, pct,  # noqa: E402
                    short, write_csv)


def jaccard(a, b):
    if not a and not b:
        return 0.0
    return 1 - len(a & b) / len(a | b)


def agglomerate(items, dist):
    """Average linkage. Returns the merge history so any k can be cut."""
    clusters = {i: [i] for i in range(len(items))}
    d = {}
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            d[(i, j)] = dist[i][j]
    history = []
    next_id = len(items)
    while len(clusters) > 1:
        (a, b), best = min(d.items(), key=lambda kv: kv[1])
        merged = clusters.pop(a) + clusters.pop(b)
        d = {k: v for k, v in d.items() if a not in k and b not in k}
        for c, members in clusters.items():
            avg = sum(dist[x][y] for x in merged for y in members) / (len(merged) * len(members))
            d[(min(c, next_id), max(c, next_id))] = avg
        clusters[next_id] = merged
        history.append(dict(clusters))
        next_id += 1
    return history


def cut(history, n_items, k):
    if k >= n_items:
        return [[i] for i in range(n_items)]
    snapshot = history[n_items - k - 1]
    return list(snapshot.values())


def silhouette(clusters, dist):
    label = {}
    for ci, members in enumerate(clusters):
        for m in members:
            label[m] = ci
    scores = []
    for i, ci in label.items():
        own = [j for j in clusters[ci] if j != i]
        if not own:
            scores.append(0.0)
            continue
        a = sum(dist[i][j] for j in own) / len(own)
        b = min(sum(dist[i][j] for j in members) / len(members)
                for cj, members in enumerate(clusters) if cj != ci)
        scores.append((b - a) / max(a, b) if max(a, b) else 0.0)
    return sum(scores) / len(scores)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", default="IRONCLAD")
    ap.add_argument("--build", default=MAIN_BUILD)
    ap.add_argument("--k", type=int, default=0, help="number of clusters (0 = best silhouette in 3..6)")
    ap.add_argument("--min-cards", type=int, default=5)
    ap.add_argument("--out", default=str(PROJECT / "reports/phase1"))
    args = ap.parse_args()
    ch = args.character.upper()
    out = Path(args.out)
    con = connect()
    run_filter = "r.n_players = 1 AND r.build_id = ? AND r.character = ?"
    P = [args.build, ch]
    runs = {r["run_id"]: dict(r) for r in con.execute(f"SELECT * FROM runs r WHERE {run_filter}", P)}
    decks = collections.defaultdict(set)
    floor_added = collections.defaultdict(dict)
    for r in con.execute(f"SELECT d.* FROM final_deck d JOIN runs r USING(run_id) WHERE {run_filter}", P):
        if is_starter(r["card_id"], ch) or not r["card_id"].startswith("CARD."):
            continue
        decks[r["run_id"]].add(r["card_id"])
        fa = r["floor_added"] or 0
        floor_added[r["run_id"]][r["card_id"]] = min(fa, floor_added[r["run_id"]].get(r["card_id"], 999))
    ids = [rid for rid in runs if len(decks[rid]) >= args.min_cards]
    items = [decks[rid] for rid in ids]
    n = len(items)
    dist = [[jaccard(items[i], items[j]) for j in range(n)] for i in range(n)]
    history = agglomerate(items, dist)
    sil = {k: silhouette(cut(history, n, k), dist) for k in range(2, 9)}
    k = args.k or max(range(3, 7), key=lambda kk: sil[kk])
    clusters = sorted(cut(history, n, k), key=len, reverse=True)

    overall = collections.Counter(c for d in items for c in d)
    L = [f"# Deck Archetypes: {ch.title()} ({args.build})", "",
         f"{n} final decks with {args.min_cards}+ non-starter cards, clustered by card overlap (Jaccard distance, "
         f"average linkage). k = {k}, chosen by silhouette among 3–6. Silhouette scores: "
         + ", ".join(f"k={kk}: {s:.2f}" for kk, s in sil.items()) + ".", "",
         "Low silhouette scores (under about 0.25) mean the clusters overlap a lot: the Player's decks blend "
         "archetypes more than they commit to one. Names below are working labels from the defining cards; they "
         "get checked against card text in Phase 2.", "", CAUTIONS, ""]
    rows_csv = []
    for ci, members in enumerate(clusters, 1):
        rids = [ids[m] for m in members]
        cnt = collections.Counter(c for m in members for c in items[m])
        lift = []
        for c, x in cnt.items():
            share = x / len(members)
            base = overall[c] / n
            if share >= 0.3 and x >= 2:
                lift.append((c, share, base, share - base))
        lift.sort(key=lambda t: -t[3])
        finished = [r for r in rids if not runs[r]["abandoned"]]
        wins = sum(runs[r]["win"] for r in finished)
        floors = [runs[r]["floors_reached"] for r in rids]
        key_cards = [c for c, *_ in lift[:2]]
        commit = []
        for c in key_cards:
            fl = [floor_added[r][c] for r in rids if c in floor_added[r]]
            commit.append(f"{short(c)} median floor {num(median(fl), 0)}")
        L += [f"## Cluster {ci}: {' / '.join(short(c) for c, *_ in lift[:3]) or 'mixed'} ({len(members)} decks)", "",
              f"Wins: {wins}/{len(finished)} finished runs ({pct(wins / len(finished)) if finished else '-'}). "
              f"Median floors reached: {num(median(floors), 0)}. Mean ascension: "
              f"{num(sum(runs[r]['ascension'] for r in rids) / len(rids), 1)}.", "",
              "Defining cards (share of decks in this cluster vs all decks):", "",
              md_table(["Card", "In cluster", "Overall", "Lift"],
                       [[short(c), pct(s), pct(b), f"{100 * l:+.0f} pts"] for c, s, b, l in lift[:8]]), "",
              f"Commit signals: {'; '.join(commit) or '-'}.", ""]
        for r in rids:
            rows_csv.append([ci, r, runs[r]["ascension"], runs[r]["win"], runs[r]["floors_reached"],
                             " ".join(sorted(short(c) for c in decks[r]))])
    write_csv(out / f"archetypes-{ch.lower()}.csv", ["cluster", "run_id", "ascension", "win", "floors", "cards"], rows_csv)
    (out / f"archetypes-{ch.lower()}.md").write_text("\n".join(L))
    print(f"{ch}: {n} decks, k={k}, silhouettes {', '.join(f'{kk}:{s:.2f}' for kk, s in sil.items())}")


if __name__ == "__main__":
    main()
