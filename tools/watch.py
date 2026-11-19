#!/usr/bin/env python3
"""Decision-point watcher for shadowing (P3.E1.S2). Polls the game state and exits with a short summary
when the Player reaches a decision worth a call: a reward, map, shop, rest, event or treasure screen, turn 1
of an elite or boss fight, or a turn with incoming damage of at least 30% of current HP.

Run it in the background; the Agent is re-invoked when it exits, posts its call, then starts it again.
It remembers the last fired state (--memo) so it never fires twice for the same screen.

UNTESTED AGAINST THE LIVE GAME (STS2MCP format).

Usage: python3 -I tools/watch.py [--port 15526] [--interval 1.0] [--timeout 3600] [--memo runs/current/.watch_memo]
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sts  # noqa: E402
from stsstate import compact, decision_point, fingerprint  # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent


def watch(adapter, memo_path, interval=1.0, timeout=3600, clock=time.time, sleep=time.sleep):
    memo = Path(memo_path)
    last = memo.read_text().strip() if memo.exists() else ""
    deadline = clock() + timeout
    while clock() < deadline:
        try:
            st = adapter.state()
        except sts.ModError:
            sleep(interval * 3)
            continue
        c = compact(st)
        reason = decision_point(c)
        if reason:
            # Fire once per screen: fingerprint the screen identity, not every animation frame
            key = fingerprint({k: c.get(k) for k in ("screen", "floor", "round", "options", "turn")})
            if key != last:
                memo.parent.mkdir(parents=True, exist_ok=True)
                memo.write_text(key)
                return reason, st
        sleep(interval)
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=15526)
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--timeout", type=float, default=3600)
    ap.add_argument("--memo", default=str(PROJECT / "runs/current/.watch_memo"))
    args = ap.parse_args()
    reason, st = watch(sts.Sts2McpAdapter(args.port), args.memo, args.interval, args.timeout)
    if reason is None:
        print("watch: timeout, no decision point")
        sys.exit(3)
    print(f"WAKE: {reason}")
    print(sts.brief_sts2mcp(st))


if __name__ == "__main__":
    main()
