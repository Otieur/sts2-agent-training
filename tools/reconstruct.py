#!/usr/bin/env python3
"""Reconstruct the Player's combat actions from recorded snapshots (P3.E4.S2).

Between two consecutive combat snapshots in the same player turn:
  - cards that left the hand (multiset difference), the energy spent, and enemy HP/block drops identify the card
    played and its likely target;
  - a potion that disappeared means a potion was used;
  - the turn passing to the enemy (or the round advancing) means End Turn.
Every action carries a confidence: high (one card left and the energy matches its cost), medium (several cards
left; one matches the energy spent; others were presumably exhausted or discarded by its effect), low otherwise.

UNTESTED AGAINST THE LIVE GAME. Validation (P3.E4.S3) compares this against narrated fights.

Usage: python3 -I tools/reconstruct.py runs/shadow-01/states.jsonl.gz [--out runs/shadow-01/actions.jsonl]
"""
import argparse
import collections
import gzip
import json
from pathlib import Path

COMBAT = {"monster", "elite", "boss", "combat"}


def _cost(c):
    try:
        return int(c.get("cost"))
    except (TypeError, ValueError):
        return None  # X-cost or unplayable


def diff(prev, nxt):
    """Infer actions between two compact snapshots. Returns a list of action dicts."""
    actions = []
    if prev.get("screen") not in COMBAT or nxt.get("screen") not in COMBAT:
        return actions
    same_turn = prev.get("round") == nxt.get("round") and prev.get("turn") == nxt.get("turn") == "player"
    # potions
    pc, nc = collections.Counter(prev.get("potions") or []), collections.Counter(nxt.get("potions") or [])
    for pot, k in (pc - nc).items():
        for _ in range(k):
            actions.append({"type": "potion", "potion": pot, "confidence": "high"})
    if same_turn:
        ph = collections.Counter((c["id"], c.get("up")) for c in prev.get("hand") or [])
        nh = collections.Counter((c["id"], c.get("up")) for c in nxt.get("hand") or [])
        gone = list((ph - nh).elements())
        spent = (prev.get("energy") or 0) - (nxt.get("energy") or 0)
        if gone:
            costs = {}
            for c in prev.get("hand") or []:
                costs[(c["id"], c.get("up"))] = _cost(c)
            if len(gone) == 1:
                card = gone[0]
                conf = "high" if costs.get(card) in (spent, None) or spent < 0 else "medium"
            else:
                match = [g for g in gone if costs.get(g) == spent]
                card = match[0] if match else gone[0]
                conf = "medium" if match else "low"
            target = _target(prev, nxt)
            actions.append({"type": "play", "card": card[0], "upgraded": bool(card[1]), "target": target,
                            "energy_spent": spent, "also_left_hand": [g[0] for g in gone if g != card], "confidence": conf})
    else:
        if prev.get("turn") == "player" and (nxt.get("turn") != "player" or nxt.get("round") != prev.get("round")):
            actions.append({"type": "end_turn", "confidence": "high"})
    return actions


def _target(prev, nxt):
    best, drop = None, 0
    nmap = {e["id"]: e for e in nxt.get("enemies") or []}
    for e in prev.get("enemies") or []:
        n = nmap.get(e["id"])
        if n is None:
            d = (e.get("hp") or 0) + (e.get("block") or 0)  # died
        else:
            d = ((e.get("hp") or 0) - (n.get("hp") or 0)) + ((e.get("block") or 0) - (n.get("block") or 0))
        if d > drop:
            best, drop = e["id"], d
    return best


def reconstruct(snapshots):
    out = []
    for prev, nxt in zip(snapshots, snapshots[1:]):
        for a in diff(prev, nxt):
            a.update({"floor": prev.get("floor"), "round": prev.get("round"), "ts": nxt.get("ts")})
            out.append(a)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("snapshots", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    opener = gzip.open if args.snapshots.suffix == ".gz" else open
    with opener(args.snapshots, "rt", encoding="utf-8") as f:
        snaps = [json.loads(line) for line in f if line.strip()]
    actions = reconstruct(snaps)
    out = args.out or args.snapshots.with_name("actions.jsonl")
    out.write_text("".join(json.dumps(a) + "\n" for a in actions))
    conf = collections.Counter(a["confidence"] for a in actions)
    print(f"{len(snaps)} snapshots -> {len(actions)} actions ({dict(conf)}) -> {out}")


if __name__ == "__main__":
    main()
