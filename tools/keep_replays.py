#!/usr/bin/env python3
"""Keep the game's fight recordings from the Player's own play (read-only), for the simulator's fidelity suite.

The game writes `replays/latest.mcr` in the active profile at the end of every fight and overwrites it at the next
one. While the Player plays, `watch` copies each new recording into `data/sim/replays/player-<profile>/`, so
`tools/sim.py fidelity` can check the simulator against more of the real game (acts 2 and 3, other characters, rare
cards and relics). The save folder is only read: each recording is opened read-only and copied out; nothing is ever
written, renamed or deleted there (the project instructions, save folder read-only for analysis).

    python3 -I tools/keep_replays.py watch            # until stopped (Ctrl-C), checking every 2 s
    python3 -I tools/keep_replays.py watch --while-game-runs   # stops a minute after the game closes
    python3 -I tools/keep_replays.py once             # copy whatever is new now
    python3 -I tools/keep_replays.py status           # what has been kept, per profile and game build

The Agent's practice profile (`modded/profile2`) is skipped: `tools/play_turn.py` keeps those during Agent runs.
Copies are local only (`data/sim/replays/` is ignored by git). File and folder names carry the profile name, the time
and the game build, never the Steam id.
"""
import argparse
import hashlib
import json
import os
import struct
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SAVE_ROOT = Path.home() / "Library" / "Application Support" / "SlayTheSpire2" / "steam"
DEST = PROJECT / "data" / "sim" / "replays"
INDEX = DEST / "player-index.json"
AGENT_PROFILE = ("modded", "profile2")


def read_header(data):
    """The recording starts with the game version and commit, each a 32-bit little-endian length and UTF-8 text."""
    try:
        n = struct.unpack_from("<i", data, 0)[0]
        version = data[4:4 + n].decode("utf-8")
        m = struct.unpack_from("<i", data, 4 + n)[0]
        commit = data[8 + n:8 + n + m].decode("utf-8")
        if not (0 < n < 32 and 0 < m < 64 and version.startswith("v")):
            return None
        return version, commit
    except (struct.error, UnicodeDecodeError):
        return None


def sources(save_root=SAVE_ROOT):
    """(label, path) of every profile's latest recording except the Agent's. Labels never contain the Steam id."""
    out = []
    for f in sorted(save_root.glob("*/**/replays/latest.mcr")):
        parts = f.relative_to(save_root).parts      # (<id>, [modded,] profileN, replays, latest.mcr)
        profile = parts[1:-2]
        if tuple(profile) == AGENT_PROFILE or not profile or not profile[-1].startswith("profile"):
            continue
        out.append(("-".join(profile), f))
    return out


def _read(path):
    fd = os.open(path, os.O_RDONLY)             # read-only, never a handle that could write
    try:
        chunks = []
        while True:
            b = os.read(fd, 1 << 20)
            if not b:
                break
            chunks.append(b)
        return b"".join(chunks)
    finally:
        os.close(fd)


def load_index(index=INDEX):
    try:
        return json.loads(index.read_text())
    except (OSError, ValueError):
        return {}


def keep_if_new(label, path, dest=DEST, index_file=INDEX, settle=1.0):
    """Copy the recording if it is complete and not kept yet. Returns the kept path, or None."""
    try:
        st1 = path.stat()
        if settle:
            time.sleep(settle)
        st2 = path.stat()
    except OSError:
        return None
    if (st1.st_size, st1.st_mtime_ns) != (st2.st_size, st2.st_mtime_ns) or st2.st_size < 64:
        return None                              # still being written, or empty
    data = _read(path)
    if len(data) != st2.st_size:
        return None
    header = read_header(data)
    if header is None:
        return None
    digest = hashlib.sha256(data).hexdigest()
    index = load_index(index_file)
    if digest in index:
        return None
    stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(st2.st_mtime))
    folder = dest / f"player-{label}"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{stamp}-{header[0]}.mcr"
    k = 1
    while target.exists():
        k += 1
        target = folder / f"{stamp}-{header[0]}-{k}.mcr"
    target.write_bytes(data)
    index[digest] = {"profile": label, "kept_as": str(target.relative_to(dest)), "version": header[0], "commit": header[1],
                     "recorded": stamp, "bytes": len(data)}
    index_file.parent.mkdir(parents=True, exist_ok=True)
    index_file.write_text(json.dumps(index, indent=1, sort_keys=True))
    return target


def game_running():
    return subprocess.run(["pgrep", "-f", "SlayTheSpire2.app/Contents/MacOS"], capture_output=True).returncode == 0


def cmd_once(a):
    kept = [p for label, f in sources() if (p := keep_if_new(label, f))]
    for p in kept:
        print(f"kept {p.relative_to(PROJECT)}")
    if not kept:
        print("nothing new")
    return 0


def cmd_watch(a):
    print(f"watching {len(sources())} profile(s) (the Agent's profile is skipped); Ctrl-C to stop", flush=True)
    last_seen_game = time.time()
    try:
        while True:
            for label, f in sources():
                p = keep_if_new(label, f, settle=0.5)
                if p:
                    print(f"{time.strftime('%H:%M:%S')} kept {p.relative_to(PROJECT)}", flush=True)
            if a.while_game_runs:
                if game_running():
                    last_seen_game = time.time()
                elif time.time() - last_seen_game > 60:
                    print("the game has been closed for a minute: stopping", flush=True)
                    return 0
            time.sleep(a.interval)
    except KeyboardInterrupt:
        return 0


def cmd_status(a):
    index = load_index()
    counts = {}
    for v in index.values():
        key = (v["profile"], v["version"], v["commit"])
        counts[key] = counts.get(key, 0) + 1
    if not counts:
        print("no recordings kept yet")
    for (profile, version, commit), n in sorted(counts.items()):
        print(f"{profile:18s} {version} {commit}: {n} fight(s)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("watch")
    w.add_argument("--interval", type=float, default=2.0)
    w.add_argument("--while-game-runs", action="store_true", help="stop a minute after the game closes")
    w.set_defaults(fn=cmd_watch)
    sub.add_parser("once").set_defaults(fn=cmd_once)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
