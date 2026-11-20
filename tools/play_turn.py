#!/usr/bin/env python3
"""One call per decision during live play (P4.E1): execute the chosen plan, wait only as long as the game needs, then
print the advice for the next decision point.

    python3 -I tools/play_turn.py RUN_DIR                      # show the advice for the current screen
    python3 -I tools/play_turn.py RUN_DIR --go safe            # play the top safe plan, then show the next advice
    python3 -I tools/play_turn.py RUN_DIR --act "claim_reward option_index=1" --reason "..."   # one action, then advice

Plans come from tools/advise.py (which calls tools/plan_turn.py); every action goes through tools/sts.py with a reason,
logged to RUN_DIR/decisions.jsonl. Execution stops at the first non-OK reply and at a "# after re-planning" line (a
card that changes the hand), so the next call re-plans from the real hand. No fixed sleeps: after each action the
state is polled until the game accepts the next one.
"""
import argparse
import glob
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
API = "http://127.0.0.1:8080/state"
# The Agent's profile (read-only). The game writes a replay of each fight to replays/latest.mcr when the fight ends
# ([GAME] v0.111.1: CombatReplayWriter is enabled outside TestMode; CombatManager.EndCombatInternal -> RunManager.WriteReplay).
AGENT_PROFILE = str(Path.home() / "Library/Application Support/SlayTheSpire2/steam/*/modded/profile2")
REPLAYS = PROJECT / "data" / "sim" / "replays"  # not in git: replays may hold account identifiers


def keep_replay(run, floor):
    """Copy the game's replay of the fight that just ended into the replay corpus (Phase 7 ground truth). Read-only on
    the save folder; returns the copied path or None."""
    try:
        src = max((Path(p) for p in glob.glob(AGENT_PROFILE + "/replays/latest.mcr")), key=lambda p: p.stat().st_mtime, default=None)
        if src is None or time.time() - src.stat().st_mtime > 180:
            return None  # no replay, or not from the fight that just ended
        out = REPLAYS / Path(run).name / f"floor{int(floor or 0):02d}-{time.strftime('%H%M%S', time.localtime(src.stat().st_mtime))}.mcr"
        if not out.exists():
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, out)
        return out
    except OSError:
        return None


def reload_count():
    """The game's own count of reloads in the current run (SerializableRun.NumReloads), or None. Reads that one field
    of the in-progress save and nothing else: the file also holds the seed and RNG state, which no tool may use
    (docs/simulator-integrity.md FP-2, ML-6)."""
    try:
        src = max((Path(p) for p in glob.glob(AGENT_PROFILE + "/saves/current_run.save")), key=lambda p: p.stat().st_mtime, default=None)
        m = re.search(r'"num_reloads"\s*:\s*(\d+)', src.read_text()) if src else None
        return int(m.group(1)) if m else None
    except OSError:
        return None


def read_state():
    with urllib.request.urlopen(API, timeout=10) as r:
        d = json.load(r)
    return d.get("data", d)


def ready(d):
    """True when the game will accept the next decision."""
    acts = d.get("available_actions") or []
    if d.get("screen") == "COMBAT":
        rd = (d.get("combat") or {}).get("action_readiness") or {}
        return "play_card" in acts and rd.get("can_use_combat_actions", True)
    return bool(set(acts) - {"save_and_quit", "discard_potion"})


def _hand_key(d):
    return [(h.get("card_id"), h.get("index")) for h in (d.get("combat") or {}).get("hand") or []]


def settle(timeout=20.0, poll=0.3):
    """Poll until the game accepts the next decision. In combat the hand and energy must also be unchanged across
    three reads: play_card becomes available while the turn's draw is still animating (seen live 2026-11-19)."""
    t0 = time.time()
    d, prev, same = None, None, 0
    while time.time() - t0 < timeout:
        try:
            d = read_state()
            if ready(d):
                if d.get("screen") != "COMBAT":
                    return d, time.time() - t0
                rd = (d.get("combat") or {}).get("action_readiness") or {}
                key = (_hand_key(d), (d.get("combat") or {}).get("player", {}).get("energy"))
                same = same + 1 if key == prev else 0
                if rd.get("actions_settled", True) and same >= 2:  # unchanged across three reads: a reshuffle pauses the draw
                    return d, time.time() - t0
                prev = key
            else:
                prev, same = None, 0
        except Exception:
            pass
        time.sleep(poll)
    return d or read_state(), time.time() - t0


def advise(run):
    return subprocess.run([sys.executable, "-I", "tools/advise.py", "--live", "--save", f"{run}/state.json"], cwd=PROJECT,
                          capture_output=True, text=True, timeout=300).stdout


def plan_commands(text, mode):
    """The commands advise.py printed for the top plan of a mode, and that plan's two summary lines."""
    lines = text.splitlines()
    hdr = next((i for i, l in enumerate(lines) if l.strip() == f"{mode}:"), None)
    summary = ""
    if hdr is not None and hdr + 2 < len(lines):
        summary = f"{lines[hdr + 1].strip()} ({lines[hdr + 2].strip().split(', energy left')[0]})"
    start = next((i for i, l in enumerate(lines) if l.startswith(f"commands for the top {mode} plan")), None)
    cmds = []
    if start is not None:
        for l in lines[start + 1:]:
            if not l.startswith("  python3"):  # a blank line, the next block, or "# after re-planning"
                break
            cmds.append(l.strip())
    return summary, cmds


def act(run, args_list, reason):
    r = subprocess.run([sys.executable, "-I", "tools/sts.py", "--mod", "sts2agent", "--log", f"{run}/decisions.jsonl", "act"]
                       + args_list + ["--reason", reason[:400]], cwd=PROJECT, capture_output=True, text=True, timeout=60)
    return (r.stdout + r.stderr).strip()


def compact(d):
    """Hand, energy and enemies in a few lines, for judging the advised plans."""
    c = d.get("combat") or {}
    p = c.get("player") or {}
    r = d.get("run") or {}
    out = [f"{d.get('screen')} floor {r.get('floor')} turn {d.get('turn')} · HP {p.get('current_hp', r.get('current_hp'))}/"
           f"{r.get('max_hp')} block {p.get('block')} energy {p.get('energy')} · powers "
           f"{ {x.get('power_id', '').replace('_POWER', ''): x.get('amount') for x in p.get('powers') or []} }"]
    if c.get("hand"):
        out.append("hand: " + " | ".join(
            f"[{h.get('index')}] {h.get('card_id')}{'+' if h.get('upgraded') else ''} ({h.get('energy_cost')})"
            f"{'' if h.get('playable', True) else ' x'} "
            + ",".join(f"{v.get('name')}={v.get('current_value')}" for v in h.get("dynamic_values") or [])
            for h in c["hand"]))
    for e in c.get("enemies") or []:
        if e.get("is_alive", True):
            out.append(f"enemy [{e.get('index')}] {e.get('enemy_id')} {e.get('current_hp')}/{e.get('max_hp')} block {e.get('block')} "
                       f"intent {[(i.get('intent_type'), i.get('damage'), i.get('hits')) for i in e.get('intents') or []]} "
                       f"powers { {x.get('power_id', '').replace('_POWER', ''): x.get('amount') for x in e.get('powers') or []} }")
    pots = [f"[{x.get('index')}] {x.get('potion_id')}" for x in r.get("potions") or [] if x.get("occupied")]
    if pots:
        out.append("potions: " + ", ".join(pots))
    return "\n".join(out)


def show(run, max_lines, was_combat=False, floor=None):
    d, _ = settle(timeout=5)
    if was_combat and d.get("screen") != "COMBAT":  # the fight just ended: keep its replay
        kept = keep_replay(run, floor)
        if kept:
            print(f"replay kept: {kept.relative_to(PROJECT)}")
    n = reload_count()
    if n:
        print(f"WARNING: the game counts {n} reload(s) in this run (scored runs need 0)")
    text = advise(run)
    keep = [l for l in text.splitlines() if not l.startswith("  python3") and not l.startswith("commands for")]
    print(compact(d))
    print("\n".join(keep[:max_lines]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run")
    ap.add_argument("--go", choices=["safe", "balanced"])
    ap.add_argument("--act", help="one action with its parameters, e.g. \"claim_reward option_index=1\"")
    ap.add_argument("--reason", default="")
    ap.add_argument("--lines", type=int, default=30, help="advice lines to print")
    a = ap.parse_args(argv)
    t0 = time.time()
    n, ok = 0, True
    try:
        before = read_state()
    except Exception:  # noqa: BLE001
        before = {}
    was_combat, floor = before.get("screen") == "COMBAT", (before.get("run") or {}).get("floor")
    if a.go:
        summary, cmds = plan_commands(advise(a.run), a.go)
        if not cmds:
            print(f"no commands for the {a.go} plan")
        print(f"PLAN {a.go}: {summary}")
        for c in cmds:
            m = re.search(r'--reason "([^"]*)"', c)
            base = m.group(1) if m else f"Turn plan ({a.go})"
            parts = re.sub(r'--reason "[^"]*"', "", c).split()
            params = parts[parts.index("act") + 1:]
            reason = base + (f"; {a.reason}" if a.reason else "") + (f"; plan: {summary}" if params[0] != "end_turn" else "")
            out = act(a.run, params, reason)
            n += 1
            print(f"  {' '.join(params)} -> {out[:40]}")
            if not out.startswith("OK"):
                print("STOP: non-OK reply")
                ok = False
                break
            settle()
    elif a.act:
        d = read_state()
        name = a.act.split()[0]
        if name not in (d.get("available_actions") or []):  # a menu or overlay opened (seen live 2026-11-19)
            print(f"REFUSED: '{name}' is not available on screen {d.get('screen')} (actions {d.get('available_actions')})")
            return 1
        out = act(a.run, a.act.split(), a.reason or a.act)
        n += 1
        print(f"  {a.act} -> {out[:60]}")
        if not out.startswith("OK"):
            ok = False
        settle()
    show(a.run, a.lines, was_combat, floor)
    print(f"[{n} actions, {time.time() - t0:.1f}s]")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
