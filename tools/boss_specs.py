#!/usr/bin/env python3
"""Boss fights reached in run benchmarks, as a fight set for the fight benchmark (`tools/learn/bench.py --benchmark`).

`tools/run_bench.py` records each boss fight's starting situation (deck, relics, potions, HP, encounter, act,
ascension) as a fight spec in the fight record. This collects them, with the policy that reached the fight and whether
search won it in the run (`source.won_in_run`), so the same boss fights can be replayed with other fight policies:
are the losses the deck's or the fight play's?

    python3 -I tools/boss_specs.py data/learn/runs/run-bench-9 --out data/sim/boss-fights-rb9.json
    python3 -I tools/boss_specs.py data/learn/runs/run-bench-9 --act 1 --out ...    # act 1 bosses only
"""
import argparse
import json
import sys
import time
from pathlib import Path


def collect(folders, act=None):
    fights = []
    for folder in folders:
        for shard in sorted(Path(folder).glob("shard-*.jsonl")):
            for line in shard.open():
                rec = json.loads(line)
                for pol, r in rec["policies"].items():
                    for f in r.get("fights", []):
                        spec = f.get("spec")
                        if not spec or (act and spec.get("act") != act):
                            continue
                        spec = dict(spec)
                        spec["source"] = dict(spec.get("source") or {}, benchmark=Path(folder).name, policy=pol,
                                              won_in_run=f.get("hp_end", 0) > 0 if "hp_end" in f else None)
                        fights.append(spec)
    return fights


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="+")
    ap.add_argument("--act", type=int)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    fights = collect(a.folders, a.act)
    about = {"source": "boss fights reached in run benchmarks (tools/boss_specs.py)", "created": time.strftime("%Y-%m-%d %H:%M"),
             "folders": [Path(f).name for f in a.folders], "act": a.act, "fights": len(fights),
             "won_in_run": sum(1 for f in fights if f["source"].get("won_in_run")),
             "by_encounter": {e: sum(1 for f in fights if f["encounter"] == e) for e in sorted({f["encounter"] for f in fights})}}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps({"about": about, "fights": fights}, indent=0))
    print(json.dumps(about, indent=1))
    return 0 if fights else 1


if __name__ == "__main__":
    sys.exit(main())
