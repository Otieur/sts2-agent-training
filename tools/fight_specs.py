#!/usr/bin/env python3
"""Fight specs from the Player's history: realistic starting points for the benchmark set (P8.E1.S1) and for
self-play training data (P9.E1.S2).

For each of the character's fights in `data/runs.db`: the encounter, act, floor, room type, ascension, the deck before
the fight (the snapshot after the previous floor), the relics obtained before it, the potions held before it, HP before
it and max HP. The Player's history is used as a source of situations and outcomes only, never as moves to imitate
(project instructions, goal reminder). Exam seeds are excluded (ML-7).

    python3 -I tools/fight_specs.py --character IRONCLAD                 # writes data/learn/specs/fight-specs-ironclad.json
    python3 -I tools/fight_specs.py --character IRONCLAD --validate      # also starts every fight in the simulator

Known approximations, recorded in the output: enchantments are not in the deck snapshots; relics removed before the
fight are missing; potion slots are capped at 3; the max HP is the floor's recorded value; source runs are from older
game builds (mostly v0.107.1), so ids the installed game does not know are dropped (counted by `--validate`).
"""
import argparse
import json
import re
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DB = PROJECT / "data" / "runs.db"
OUT = PROJECT / "data" / "learn" / "specs"


def exam_seeds():
    text = (PROJECT / "metrics" / "exam-seeds.md").read_text()
    return set(re.findall(r"\|\s*\d+\s*\|\s*`([A-Z0-9]{8,14})`", text))


def build(character, db=DB):
    con = sqlite3.connect(db)
    exams = exam_seeds()
    runs = {r[0]: r for r in con.execute("SELECT run_id, seed, ascension, build_id, win FROM runs WHERE character = ? AND abandoned = 0", [character])}
    snaps = {}
    for run_id, floor, cid, lvl, n in con.execute("SELECT run_id, floor, card_id, upgrade_level, count FROM deck_snapshots"):
        if run_id in runs:
            snaps.setdefault((run_id, floor), []).extend([(cid, lvl)] * n)
    relics = {}
    for run_id, rid, fl in con.execute("SELECT run_id, relic_id, floor_added FROM final_relics"):
        relics.setdefault(run_id, []).append((fl, rid))
    pots = {}
    for run_id, fl, kind, pid, picked in con.execute("SELECT run_id, floor, kind, potion_id, picked FROM potion_events"):
        pots.setdefault(run_id, []).append((fl, kind, pid, picked))
    specs, skipped = [], Counter()
    q = """SELECT run_id, floor, act, room_type, model_id, hp_before, max_hp FROM floors
           WHERE room_type IN ('monster', 'elite', 'boss') ORDER BY run_id, floor"""
    for run_id, floor, act, room, model, hp, max_hp in con.execute(q):
        if run_id not in runs:
            continue
        _, seed, asc, build_id, win = runs[run_id]
        if seed in exams:
            skipped["exam seed"] += 1
            continue
        prev = max((f for (r, f) in snaps if r == run_id and f < floor), default=None) if (run_id, floor - 1) not in snaps else floor - 1
        if prev is None or not model or not hp:
            skipped["no deck snapshot or encounter"] += 1
            continue
        deck = [strip(cid) + ("+" if lvl and lvl > 0 else "") for cid, lvl in snaps[(run_id, prev)]]
        held = Counter()
        for fl, kind, pid, picked in sorted(pots.get(run_id, [])):
            if fl >= floor:
                break
            if (kind == "offered" and picked) or kind == "bought":
                held[strip(pid)] += 1
            elif kind in ("used", "discarded") and held[strip(pid)] > 0:
                held[strip(pid)] -= 1
        potions = [p for p, n in held.items() for _ in range(n)][:3]
        specs.append({
            "source": {"run": run_id, "floor": floor, "build": build_id, "run_won": bool(win)},
            "act": act, "room": room.capitalize(), "encounter": strip(model), "ascension": asc, "character": character,
            "deck": deck, "relics": [strip(r) for fl, r in sorted(relics.get(run_id, [])) if fl < floor],
            "potions": potions, "hp": hp, "max_hp": max_hp or None,
        })
    return specs, skipped


def strip(model_id):
    return model_id.split(".", 1)[1] if model_id and "." in model_id else model_id


def validate(specs):
    sys.path.insert(0, str(PROJECT / "tools"))
    import sim as S
    ok, errors = 0, Counter()
    with S.Sim() as sim:
        for i, s in enumerate(specs):
            try:
                sim.call(cmd="new_fight", spec={k: s[k] for k in ("encounter", "character", "ascension", "deck", "relics", "potions", "hp", "max_hp")}
                         | {"seed": f"SPEC{i:07d}", "relic_pickup": False}, sample_seed=i + 1, timeout=120)
                s["valid"] = True
                ok += 1
            except S.SimError as e:
                s["valid"] = False
                msg = str(e).split("(")[0]
                s["invalid_reason"] = msg[:160]
                errors[re.sub(r"'[^']*'", "'…'", msg)[:90]] += 1
    return ok, errors


BENCHMARK_QUOTA = {("Monster", 1): 10, ("Monster", 2): 10, ("Monster", 3): 10, ("Elite", 1): 7, ("Elite", 2): 7, ("Elite", 3): 6,
                   ("Boss", 1): 4, ("Boss", 2): 3, ("Boss", 3): 3}


def benchmark(specs, seed=1):
    """A fixed, stratified selection (P8.E1.S1): 30 hallway, 20 elite and 10 boss fights across the three acts, the
    scarcest groups first, at most two fights per source run (the Ironclad history has about 50 runs, 14 reaching act 3),
    chosen with a fixed seed. Training must leave out every (source run, floor) listed here."""
    import random
    rng = random.Random(seed)
    valid = [s for s in specs if s.get("valid")]
    rng.shuffle(valid)
    avail = {k: sum(1 for s in valid if (s["room"], s["act"]) == k) for k in BENCHMARK_QUOTA}
    picked, per_run = [], {}
    for key in sorted(BENCHMARK_QUOTA, key=lambda k: avail[k] / BENCHMARK_QUOTA[k]):
        n = BENCHMARK_QUOTA[key]
        for s in valid:
            if n == 0:
                break
            run = s["source"]["run"]
            if (s["room"], s["act"]) == key and per_run.get(run, 0) < 2:
                picked.append(s)
                per_run[run] = per_run.get(run, 0) + 1
                n -= 1
    return sorted(picked, key=lambda s: (s["act"], s["room"], s["source"]["run"], s["source"]["floor"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--character", default="IRONCLAD")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--benchmark", action="store_true", help="also write data/sim/benchmark-v1.json (needs --validate)")
    a = ap.parse_args(argv)
    specs, skipped = build(a.character)
    report = {"character": a.character, "created": time.strftime("%Y-%m-%d %H:%M"), "fights": len(specs), "skipped": dict(skipped),
              "by_act": dict(Counter(s["act"] for s in specs)), "by_room": dict(Counter(s["room"] for s in specs)),
              "approximations": ["no enchantments", "relics removed before the fight are missing", "potions capped at 3",
                                 "max HP as recorded for the floor", "source builds older than the installed game"]}
    if a.validate:
        ok, errors = validate(specs)
        report["valid"] = ok
        report["invalid"] = dict(errors.most_common(12))
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"fight-specs-{a.character.lower()}.json"
    out.write_text(json.dumps({"about": report, "specs": specs}, indent=0))
    print(json.dumps(report, indent=1))
    print(f"wrote {out.relative_to(PROJECT)}")
    if a.benchmark:
        info = Path.home() / "Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app/Contents/Resources/release_info.json"
        build_info = json.loads(info.read_text()) if info.exists() else {}
        picked = benchmark(specs)
        bench = {"about": {"name": "benchmark-v1", "created": report["created"], "game_version": build_info.get("version"),
                           "game_commit": build_info.get("commit"), "source": "the Player's history via tools/fight_specs.py (agreed 2026-11-20)",
                           "selection": "stratified by room type and act, scarcest groups first, at most two fights per source run, seed 1", "quota": {f"{r} act {a2}": n for (r, a2), n in BENCHMARK_QUOTA.items()},
                           "exam_seeds": "excluded", "training_rule": "datasets used for training leave out every (source run, floor) listed here; fights from the same runs at other floors may remain (the history is too small to drop whole runs)",
                           "approximations": report["approximations"], "fights": len(picked)},
                 "fights": picked}
        bout = PROJECT / "data" / "sim" / "benchmark-v1.json"
        bout.write_text(json.dumps(bench, indent=1))
        print(f"wrote {bout.relative_to(PROJECT)} ({len(picked)} fights)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
