#!/usr/bin/env python3
"""Fight-outcome dataset (decision 0005 item 4): one row per fight played by search, with its starting situation.

A row holds what is known when a fight starts (encounter, act, room type, ascension, deck, relics, potions, HP, max
HP) and how the fight ended under search (won, HP left, enemy HP left when lost). Sources, all from the simulator:
- self-play datasets (`data/learn/combat-*`, `tools/selfplay.py`): fights started from fight specs;
- run benchmarks (`data/learn/runs/*`, `tools/run_bench.py`): fights inside whole runs, where a spec was recorded;
- fight benchmarks (`data/learn/bench/*`, `tools/learn/bench.py`): the `mcw6` arm on its fight set.

`group` names the run or spec a fight came from, so that a split by group keeps a run's fights on one side. The model
trained on this (`tools/learn/train_fight.py`) predicts the outcome of a fight for a deck, as fought by search, and is
meant to replace planner fights inside rollouts. Only starting situations a player can see are used (FP-1).

    python3 -I tools/learn/fight_data.py --out data/learn/fights/fights-v1.jsonl
"""
import argparse
import collections
import json
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
KEYS = ("encounter", "act", "room", "ascension", "deck", "relics", "potions", "hp", "max_hp")
DEC = json.JSONDecoder()


def row(spec, won, hp_end, enemy_hp_left, teacher, potions_allowed, src, group):
    if not spec or any(spec.get(k) is None for k in ("encounter", "deck", "hp", "max_hp")):
        return None
    r = {k: spec.get(k) for k in KEYS}
    r["potions"] = [p for p in (r["potions"] or []) if p]
    r["relics"] = list(r["relics"] or [])
    r |= {"won": bool(won), "hp_end": max(0, int(hp_end or 0)) if won else 0, "enemy_hp_left": enemy_hp_left,
          "teacher": teacher, "potions_allowed": bool(potions_allowed), "src": src, "group": group}
    return r


def from_selfplay(folder):
    man = json.loads((folder / "manifest.json").read_text()) if (folder / "manifest.json").exists() else {}
    t = man.get("teacher") or {}
    wide = "wide" in str(t.get("policy", ""))
    teacher = f"mc{'w' if wide else ''}{t.get('k', '?')}"
    for shard in sorted(folder.glob("shard-*.jsonl")):
        for line in shard.open():
            # the decisions (observations) make lines large; only the spec and the outcome are decoded
            try:
                i = line.index('"spec":') + 7
                spec, j = DEC.raw_decode(line, i + (line[i] == " "))
                k = line.index('"outcome":', j) + 10
                out, _ = DEC.raw_decode(line, k + (line[k] == " "))
            except ValueError:
                continue
            if out.get("blocked") or out.get("status") not in ("won", "lost"):
                continue
            src = spec.get("source") or {}
            yield row(spec, out["status"] == "won", out.get("hp"), out.get("enemy_hp_left"), teacher, bool(t.get("potions")),
                      f"selfplay/{folder.name}", f"{src.get('run')}")


def from_runs(folder):
    for shard in sorted(folder.glob("shard-*.jsonl")):
        for line in shard.open():
            rec = json.loads(line)
            for pol, r in rec["policies"].items():
                for f in r.get("fights", []):
                    if not f.get("spec") or "hp_end" not in f:
                        continue
                    won = f["hp_end"] > 0
                    yield row(f["spec"], won, f["hp_end"], None, rec.get("combat") or "planner", "pot" in pol.split("+"),
                              f"runs/{folder.name}", f"{folder.name}/{rec['seed']}/{pol}")


def from_bench(folder):
    mf = folder / "manifest.json"
    if not mf.exists():
        return
    man = json.loads(mf.read_text())
    bench = PROJECT / man.get("benchmark", "")
    if not bench.is_file():
        return
    fights = json.loads(bench.read_text())["fights"]
    for shard in sorted(folder.glob("shard-*.jsonl")):
        for line in shard.open():
            r = json.loads(line)
            for arm in ("mcw6", "mcw12", "mcw24"):
                o = r["arms"].get(arm)
                if not o or o.get("status") not in ("won", "lost") or o.get("blocked"):
                    continue
                spec = fights[r["fight"]]
                yield row(spec, o["status"] == "won", o.get("hp"), o.get("enemy_hp_left"), arm, False, f"bench/{folder.name}",
                          f"bench/{bench.name}/{r['fight']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(PROJECT / "data" / "learn" / "fights" / "fights-v1.jsonl"))
    ap.add_argument("--teachers", nargs="+", default=["mcw6"], help="keep fights played by these search settings")
    ap.add_argument("--runs", nargs="+", help="only the fights of these run benchmark folders (to check a model on fights it has not seen)")
    a = ap.parse_args(argv)
    L = PROJECT / "data" / "learn"
    rows = []
    if a.runs:
        for folder in a.runs:
            rows += [r for r in from_runs(Path(folder)) if r]
    else:
        for folder in sorted(L.glob("combat-*")):
            rows += [r for r in from_selfplay(folder) if r]
        for folder in sorted((L / "runs").glob("run-bench-*")):
            rows += [r for r in from_runs(folder) if r]
        for folder in sorted((L / "bench").iterdir()):
            if folder.is_dir():
                rows += [r for r in from_bench(folder) if r]
    kept = [r for r in rows if r["teacher"] in a.teachers]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as fh:
        for r in kept:
            fh.write(json.dumps(r) + "\n")
    c = collections.Counter
    about = {"created": time.strftime("%Y-%m-%d %H:%M"), "rows": len(kept), "rows_all_teachers": len(rows), "teachers": a.teachers,
             "by_teacher_all": dict(c(r["teacher"] for r in rows)), "by_source": dict(c(r["src"] for r in kept)),
             "by_room": dict(c(r["room"] for r in kept)), "by_ascension": dict(sorted(c(r["ascension"] for r in kept).items())),
             "won_by_room": {room: f"{sum(r['won'] for r in kept if r['room'] == room)}/{sum(1 for r in kept if r['room'] == room)}"
                             for room in ("Monster", "Elite", "Boss")},
             "groups": len({r["group"] for r in kept}), "potions_allowed": sum(r["potions_allowed"] for r in kept)}
    out.with_suffix(".about.json").write_text(json.dumps(about, indent=1))
    print(json.dumps(about, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
