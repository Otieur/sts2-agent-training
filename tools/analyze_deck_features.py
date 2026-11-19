#!/usr/bin/env python3
"""Compare deck features on arrival between survived and fatal fights, per boss and elite.

Joins the Phase 1 deck snapshots (data/runs.db) with card roles from the extracted game data
(knowledge/data/extract-2026-09-21/cards.json). Evidence is [PLAYER-DATA] with small samples:
every difference is a hypothesis, not a rule.

Usage: python3 -I tools/analyze_deck_features.py [--build v0.107.1] [--min-deaths 2]
Writes reports/phase2/deck-features-by-encounter.md and .csv
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import MAIN_BUILD, PROJECT, connect, md_table, mean, median, short, write_csv  # noqa: E402

import deck_metrics  # noqa: E402

deck_metrics.apply_patches("v0.107.1")  # the history's version; the extract predates it
CARDS = deck_metrics.CARDS
FEATURES = [
    ("multi_hit", "Multi-hit attacks"), ("aoe", "Hit-all attacks"), ("aoe_single_hit", "Single-hit hit-all attacks"),
    ("cheap_attack", "Attacks costing 0–1"), ("block", "Block cards"), ("draw", "Draw cards"), ("energy", "Energy cards"),
    ("strength", "Strength cards"), ("vulnerable", "Vulnerable cards"), ("weak", "Weak cards"), ("power", "Powers"),
    ("hits_per_card", "Hit instances per card"), ("deck_size", "Deck size"),
]


def card_hits(card):
    if not card or card["type"] != "Attack":
        return 0
    e = card["effect"] or ""
    m = re.search(r"damage (\d+) times", e)
    if m:
        return int(m.group(1))
    if re.search(r"damage (\?|X[^;]*) times", e):
        return 3
    return 1 if "damage" in e else 0


def deck_features(snapshot):
    f = collections.Counter()
    size = 0
    hits = 0
    for cid, n in snapshot:
        size += n
        c = CARDS.get(cid.split(".", 1)[-1])
        if not c:
            continue
        tags = set(c["tags"])
        h = card_hits(c)
        hits += h * n
        if h >= 2:
            f["multi_hit"] += n
        if "aoe" in tags and c["type"] == "Attack":
            f["aoe"] += n
            if h <= 1:
                f["aoe_single_hit"] += n
        if c["type"] == "Attack" and c["cost"] is not None and 0 <= c["cost"] <= 1:
            f["cheap_attack"] += n
        for t in ("block", "draw", "energy", "strength", "vulnerable", "weak", "power"):
            if t in tags:
                f[t] += n
    f["deck_size"] = size
    f["hits_per_card"] = hits / size if size else 0
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=MAIN_BUILD)
    ap.add_argument("--min-deaths", type=int, default=2)
    args = ap.parse_args()
    con = connect()
    fights = [dict(r) for r in con.execute("""
        SELECT f.run_id, f.floor, f.model_id AS enc, f.damage_taken, r.character, r.win, r.abandoned, f.is_last_floor
        FROM floors f JOIN runs r USING(run_id)
        WHERE r.n_players = 1 AND r.build_id = ? AND f.room_type IN ('elite','boss')""", [args.build])]
    by_enc = collections.defaultdict(list)
    for x in fights:
        by_enc[x["enc"]].append(x)
    rows_csv, L = [], ["# Deck Features on Arrival: Survived against Fatal Fights", "",
                       f"All characters, solo runs on {args.build}. Bosses and elites with at least {args.min_deaths} fatal fights. "
                       "Features count cards in the deck at the start of the fight floor, with card roles from the extracted game "
                       "data `[GAME-EXTRACT]`. Evidence is `[PLAYER-DATA]` from small samples: each difference is a hypothesis to test. "
                       "Different characters' decks are pooled, which hides character-specific effects.", "",
                       "Script: `tools/analyze_deck_features.py`.", ""]
    for enc, xs in sorted(by_enc.items(), key=lambda kv: -sum(1 for x in kv[1] if x["is_last_floor"] and not x["win"] and not x["abandoned"])):
        groups = {"survived": [], "died": []}
        for x in xs:
            snap = [(r["card_id"], r["n"]) for r in con.execute(
                "SELECT card_id, SUM(count) AS n FROM deck_snapshots WHERE run_id=? AND floor=? GROUP BY card_id",
                (x["run_id"], x["floor"] - 1))]
            died = x["is_last_floor"] and not x["win"] and not x["abandoned"]
            groups["died" if died else "survived"].append((x, deck_features(snap)))
        if len(groups["died"]) < args.min_deaths:
            continue
        table = []
        for key, label in FEATURES:
            s = mean([f[key] for _, f in groups["survived"]]) if groups["survived"] else float("nan")
            d = mean([f[key] for _, f in groups["died"]])
            fmt = (lambda v: f"{v:.2f}") if key == "hits_per_card" else (lambda v: f"{v:.1f}")
            table.append([label, fmt(s), fmt(d), f"{d - s:+.2f}" if key == "hits_per_card" else f"{d - s:+.1f}"])
            rows_csv.append([short(enc), key, round(s, 3), round(d, 3), len(groups["survived"]), len(groups["died"])])
        L += [f"## {short(enc)}", "",
              f"Survived {len(groups['survived'])} (median damage {median([x['damage_taken'] for x, _ in groups['survived']]) if groups['survived'] else '-'}), "
              f"fatal {len(groups['died'])} (median damage {median([x['damage_taken'] for x, _ in groups['died']])}). "
              f"Characters: {', '.join(f'{k.title()} {v}' for k, v in collections.Counter(x['character'] for x in xs).most_common())}.", "",
              md_table(["Feature (cards in deck)", "Survived (mean)", "Fatal (mean)", "Fatal − survived"], table), ""]
    out = PROJECT / "reports/phase2"
    out.mkdir(parents=True, exist_ok=True)
    (out / "deck-features-by-encounter.md").write_text("\n".join(L))
    write_csv(out / "deck-features-by-encounter.csv", ["encounter", "feature", "survived_mean", "fatal_mean", "n_survived", "n_fatal"], rows_csv)
    print(f"wrote {len(set(r[0] for r in rows_csv))} encounters")


if __name__ == "__main__":
    main()
