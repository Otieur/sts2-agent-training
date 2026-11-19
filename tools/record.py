#!/usr/bin/env python3
"""State recorder for shadowing (P3.E4.S1). Polls the game state and appends a compact snapshot to a gzipped
JSONL file whenever the state changes (deduplicated by fingerprint). Run in the background for a whole run.

UNTESTED AGAINST THE LIVE GAME (both mods' formats via stsstate.compact; --mod sts2agent by default).

Usage: python3 -I tools/record.py --out runs/shadow-01/states.jsonl.gz [--mod sts2agent|sts2mcp] [--port N] [--combat-interval 0.5]
       [--interval 1.0] [--max-hours 4]
"""
import argparse
import gzip
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sts  # noqa: E402
from stsstate import COMBAT_SCREENS, compact, fingerprint  # noqa: E402


def record(adapter, out_path, interval=1.0, combat_interval=0.5, max_seconds=4 * 3600, clock=time.time,
           sleep=time.sleep, max_snapshots=None):
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    last, n = None, 0
    deadline = clock() + max_seconds
    with gzip.open(out, "at", encoding="utf-8") as f:
        while clock() < deadline:
            try:
                st = adapter.state()
            except sts.ModError:
                sleep(interval * 3)
                continue
            c = compact(st)
            fp = fingerprint(c)
            if fp != last:
                f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), **c}) + "\n")
                f.flush()
                last, n = fp, n + 1
                if max_snapshots and n >= max_snapshots:
                    break
            sleep(combat_interval if c.get("screen") in COMBAT_SCREENS else interval)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mod", choices=["sts2agent", "sts2mcp"], default="sts2agent")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--combat-interval", type=float, default=0.5)
    ap.add_argument("--max-hours", type=float, default=4)
    args = ap.parse_args()
    adapter = (sts.Sts2AgentAdapter(args.port or 8080) if args.mod == "sts2agent" else sts.Sts2McpAdapter(args.port or 15526))
    n = record(adapter, args.out, args.interval, args.combat_interval, args.max_hours * 3600)
    print(f"recorded {n} snapshots to {args.out}")


if __name__ == "__main__":
    main()
