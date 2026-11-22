#!/usr/bin/env python3
"""The fight-outcome model without the learning library: its forward pass in plain Python (decision 0005 item 4).

`tools/learn/train_fight.py` trains the model and writes its weights as numbers (`weights.json` beside `model.pt`).
This module loads them and predicts, for a fight's starting situation, the probability that search wins the fight and
the HP fraction left if it does. It is what the rollouts use (`tools/run_eval.py`): run benchmark workers run on the
standard library alone, and a worker makes one prediction per fight of a rollout (about 60,000 multiplications).

    python3 -I tools/learn/fight_predict.py models/fight-v1b --data data/learn/fights/fights-v1b.jsonl --rows 5

The encoding is the one of `train_fight.Encoder`; `train_fight.py --check-export` compares the two on real rows.
Only what a player can see at the start of a fight is read (FP-1).
"""
import argparse
import json
import math
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
VOCAB = PROJECT / "knowledge" / "data" / "vocab-v0.111.1.json"
BASICS = ("STRIKE_IRONCLAD", "DEFEND_IRONCLAD")
ROOMS = ("Monster", "Elite", "Boss")
MAX_DECK, MAX_RELICS, MAX_POTIONS = 60, 40, 5


def _dot(w, x):
    return sum(a * b for a, b in zip(w, x))


class FightPredictor:
    def __init__(self, folder):
        folder = Path(folder)
        self.folder = folder
        self.config = json.loads((folder / "config.json").read_text())
        w = json.loads((folder / "weights.json").read_text())
        v = json.loads(VOCAB.read_text())
        self.cards = {c: i for i, c in enumerate(v["cards"])}
        self.relics = {c: i for i, c in enumerate(v["relics"])}
        self.potions = {c: i for i, c in enumerate(v["potions"])}
        self.encounters = {e: i + 2 for i, e in enumerate(sorted(self.config["encounters"]))}      # 0 padding, 1 unknown
        self.w = w
        self.d = len(w["card.weight"][0])
        # the bilinear layer as one matrix per output, rows over the deck vector
        self.inter = w["inter.weight"]

    def scalars(self, r):
        n = max(1, len(r["deck"]))
        room = r.get("room") if r.get("room") in ROOMS else "Monster"
        return [r["hp"] / max(1, r["max_hp"]), r["hp"] / 100.0, r["max_hp"] / 100.0, (r.get("ascension") or 0) / 10.0,
                len(r["deck"]) / 30.0, sum(c.endswith("+") for c in r["deck"]) / n, sum(c.rstrip("+") in BASICS for c in r["deck"]) / n,
                len(r["relics"]) / 10.0, len(r["potions"]) / 3.0,
                *[1.0 if (r.get("act") or 1) == a else 0.0 for a in (1, 2, 3)], *[1.0 if room == x else 0.0 for x in ROOMS],
                1.0 if str(r.get("teacher", "mcw6")).startswith("mcw") else 0.0, 1.0 if r.get("potions_allowed") else 0.0]

    def predict(self, r):
        """(win probability, HP fraction left if won) for one fight row or spec (encounter, act, room, ascension, deck,
        relics, potions, hp, max_hp; optional teacher and potions_allowed)."""
        w, d = self.w, self.d
        zero = [0.0] * d
        deck_sum, n = list(zero), 0
        for c in r["deck"][:MAX_DECK]:
            i = self.cards.get(c.rstrip("+"), 1)
            if i == 0:
                continue                          # index 0 is padding: the trained model masks it out
            e = w["card.weight"][i]
            if c.endswith("+"):
                u = w["card_up.weight"][i]
                e = [a + b for a, b in zip(e, u)]
            deck_sum = [a + b for a, b in zip(deck_sum, e)]
            n += 1
        n = max(1, n)
        deck_mean, deck_tenth = [x / n for x in deck_sum], [x / 10.0 for x in deck_sum]
        relics = list(zero)
        for x in r["relics"][:MAX_RELICS]:
            i = self.relics.get(x, 1)
            if i:
                relics = [a + b for a, b in zip(relics, w["relic.weight"][i])]
        relics = [x / 5.0 for x in relics]
        potions = list(zero)
        for x in [p for p in r["potions"] if p][:MAX_POTIONS]:
            i = self.potions.get(x, 1)
            if i:
                potions = [a + b for a, b in zip(potions, w["potion.weight"][i])]
        enc = w["enc.weight"][self.encounters.get(r["encounter"], 1)]
        x = deck_mean + deck_tenth + relics + potions + enc + [a * b for a, b in zip(deck_mean, enc)] + self.scalars(r)
        h = [max(0.0, _dot(row, x) + b) for row, b in zip(w["body.0.weight"], w["body.0.bias"])]
        h = [max(0.0, _dot(row, h) + b) for row, b in zip(w["body.3.weight"], w["body.3.bias"])]
        inter = [sum(dm * _dot(row, enc) for dm, row in zip(deck_mean, mat)) + b for mat, b in zip(self.inter, w["inter.bias"])]
        h = h + inter
        logit = _dot(w["win.weight"][0], h) + w["win.bias"][0]
        hp = _dot(w["hp.weight"][0], h) + w["hp.bias"][0]
        sig = lambda z: 1.0 / (1.0 + math.exp(-z)) if z > -700 else 0.0
        return sig(logit), sig(hp)


def spec_from_obs(obs, ascension, potions_allowed):
    """A fight's starting situation from a run observation at the fight's first decision (the fields the fight specs of
    `tools/run_bench.py` hold)."""
    p = obs["player"]
    enc = str(obs.get("encounter") or "")
    room = "Boss" if enc.endswith("_BOSS") else "Elite" if enc.endswith("_ELITE") else "Monster"
    return {"encounter": enc, "act": obs.get("act"), "room": room, "ascension": ascension, "deck": list(p.get("deck", [])),
            "relics": list(p.get("relics", [])), "potions": [x for x in p.get("potions", []) if x], "hp": p["hp"], "max_hp": p["max_hp"],
            "teacher": "mcw6", "potions_allowed": bool(potions_allowed)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--data", required=True)
    ap.add_argument("--rows", type=int, default=5)
    a = ap.parse_args(argv)
    import time
    fp = FightPredictor(a.folder)
    rows = [json.loads(l) for l in Path(a.data).open() if l.strip()][:a.rows]
    t0 = time.time()
    for r in rows:
        p, hp = fp.predict(r)
        print(f"{r['encounter']:34s} hp {r['hp']:3d}/{r['max_hp']:3d} deck {len(r['deck']):2d}: win {p:.3f}, HP left if won {hp:.3f} | search: {'won' if r['won'] else 'lost'}, HP {r['hp_end']}")
    print(f"{(time.time() - t0) / max(1, len(rows)) * 1000:.1f} ms per prediction")
    return 0


if __name__ == "__main__":
    sys.exit(main())
