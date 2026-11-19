#!/usr/bin/env python3
"""Generate the facts sheet for a finished run (P4.E4.S1).

Works on any game run-history file (.run), so it can be tested on the Player's runs now and used on the
Agent's runs in Phase 4. If the run folder holds decisions.jsonl (the Agent's decision log), decision counts
by screen are added.

Usage:
  python3 -I tools/postmortem.py <path to .run file> [--out <folder>] [--character IRONCLAD]
  python3 -I tools/postmortem.py runs/<date>-<seed>/          (uses run.run and decisions.jsonl in that folder)
Writes <out>/facts.md (default: the run folder, or runs/postmortem-<run_id>/ for a bare .run file).
"""
import argparse
import collections
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import DATA, PROJECT, md_table, pct, short  # noqa: E402

FIGHT_ROOMS = {"monster", "elite", "boss"}


def load_benchmark(character):
    path = DATA / "benchmarks" / f"{character.lower()}-encounters-v0.107.1.csv"
    bench = {}
    if path.exists():
        for r in csv.DictReader(open(path)):
            bench[r["encounter"]] = r
    return bench


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--character", default=None)
    args = ap.parse_args()
    folder = None
    if args.path.is_dir():
        folder = args.path
        run_file = folder / "run.run"
    else:
        run_file = args.path
    run = json.loads(run_file.read_text())
    player = run["players"][0]
    character = (args.character or player["character"].split(".", 1)[-1]).upper()
    run_id = f"{run.get('start_time')}-{run.get('seed')}"
    out = args.out or folder or (PROJECT / "runs" / f"postmortem-{run_id}")
    out.mkdir(parents=True, exist_ok=True)
    bench = load_benchmark(character)

    floor = 0
    curve, fights, potions_used, rests, elites_by_act = [], [], [], [], collections.Counter()
    prev_hp = None
    for ai, act in enumerate(run["map_point_history"], 1):
        for pt in act:
            floor += 1
            s = (pt.get("player_stats") or [{}])[0]
            rooms = pt.get("rooms", [])
            fight = next((r for r in rooms if r.get("room_type") in FIGHT_ROOMS), None)
            hp, mx = s.get("current_hp"), s.get("max_hp")
            hp_before = mx if prev_hp is None else prev_hp
            curve.append((floor, ai, pt.get("map_point_type"), hp, mx))
            if fight:
                enc = fight.get("model_id")
                b = bench.get(enc, {})
                med = float(b["median_dmg"]) if b.get("median_dmg") else None
                p75 = float(b["p75_dmg"]) if b.get("p75_dmg") else None
                dmg = s.get("damage_taken", 0)
                fights.append({"floor": floor, "act": ai, "enc": enc, "type": fight.get("room_type"),
                               "turns": fight.get("turns_taken"), "hp_before": hp_before, "dmg": dmg,
                               "median": med, "p75": p75, "over_p75": p75 is not None and dmg > p75,
                               "potions": s.get("potion_used", [])})
                if fight.get("room_type") == "elite":
                    elites_by_act[ai] += 1
            potions_used += [(floor, p) for p in s.get("potion_used", [])]
            for c in s.get("rest_site_choices", []):
                rests.append((floor, c, hp_before, mx, ",".join(x.split(".", 1)[-1] for x in s.get("upgraded_cards", []))))
            prev_hp = hp

    result = "Won" if run.get("win") else ("Abandoned" if run.get("was_abandoned") else
                                            f"Died on floor {floor} to {short(run.get('killed_by_encounter') or fights[-1]['enc'] if fights else '?')}")
    held = [short(p["id"]) for p in player.get("potions", [])]
    deck = collections.Counter((short(c["id"]) + ("+" if c.get("current_upgrade_level") else "")) for c in player["deck"])
    relics = [short(r["id"]) for r in player.get("relics", [])]

    decisions = collections.Counter()
    if folder and (folder / "decisions.jsonl").exists():
        for line in (folder / "decisions.jsonl").read_text().splitlines():
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            decisions[d.get("screen") or d.get("action", {}).get("action") or "?"] += 1

    L = [f"# Facts: run {run_id}", "",
         f"{character.title()} · A{run.get('ascension')} · build {run.get('build_id')} · **{result}** · floors {floor} · "
         f"run time {round((run.get('run_time') or 0) / 60)} min", "",
         "## HP after each floor", "",
         md_table(["Floor", "Act", "Room", "HP", "HP%"], [[f, a, t, f"{h}/{m}", pct(h / m if m else 0)] for f, a, t, h, m in curve]), "",
         "## Fights against the benchmark", "",
         f"Benchmark: `data/benchmarks/{character.lower()}-encounters-v0.107.1.csv` (the Player's history). "
         "**Over p75** marks fights that cost more than three quarters of the Player's fights against the same encounter.", "",
         md_table(["Floor", "Encounter", "Type", "Turns", "HP before", "Damage", "Benchmark median", "p75", "Flag", "Potions"],
                  [[x["floor"], short(x["enc"]), x["type"], x["turns"], x["hp_before"], x["dmg"],
                    x["median"] if x["median"] is not None else "-", x["p75"] if x["p75"] is not None else "-",
                    "**over p75**" if x["over_p75"] else "", ", ".join(short(p) for p in x["potions"]) or "-"] for x in fights]), "",
         f"- Fights: {len(fights)}. Over p75: {sum(x['over_p75'] for x in fights)}. Total damage taken in fights: {sum(x['dmg'] for x in fights)}.",
         f"- Elites per act: {', '.join(f'Act {a}: {n}' for a, n in sorted(elites_by_act.items())) or 'none'}.",
         f"- Potions used: {len(potions_used)} ({', '.join(f'f{f} {short(p)}' for f, p in potions_used) or 'none'}). Held at the end: {', '.join(held) or 'none'}.", "",
         "## Rest sites", "",
         md_table(["Floor", "Choice", "HP before", "Upgraded"], [[f, c, f"{h}/{m} ({pct(h / m if m else 0)})", u or "-"] for f, c, h, m, u in rests]) if rests else "None.", "",
         "## Deck and relics at the end", "",
         f"Deck ({sum(deck.values())}): " + ", ".join(f"{k}×{v}" if v > 1 else k for k, v in sorted(deck.items())), "",
         f"Relics ({len(relics)}): " + ", ".join(relics), ""]
    if decisions:
        L += ["## Decisions logged", "", md_table(["Screen or action", "Count"], decisions.most_common()), ""]
    (out / "facts.md").write_text("\n".join(L))
    print(f"wrote {out / 'facts.md'}: {result}; {len(fights)} fights, {sum(x['over_p75'] for x in fights)} over p75")


if __name__ == "__main__":
    main()
