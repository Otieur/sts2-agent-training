#!/usr/bin/env python3
"""Fight-outcome model (decision 0005 item 4): how a fight is likely to end for a deck, as fought by search.

Input: what is known when a fight starts (encounter, act, room type, ascension, deck with upgrades, relics, potions,
HP, max HP) from `tools/learn/fight_data.py`. Output: the probability that search wins the fight, and the HP fraction
left if it does. Trained on fights the simulator played with search; split by run or spec (`group`), so that fights of
one run never sit on both sides. The report compares the model with base rates per encounter on held-out groups and
shows its calibration; the model replaces planner fights inside rollouts only after a pre-registered comparison.

    .venv-learn/bin/python -I tools/learn/train_fight.py --data data/learn/fights/fights-v1.jsonl --out models/fight-v1
    .venv-learn/bin/python -I tools/learn/train_fight.py --eval models/fight-v1 --data data/learn/fights/fights-v2.jsonl
    .venv-learn/bin/python -I tools/learn/train_fight.py --export models/fight-v1 --data data/learn/fights/fights-v1.jsonl

Only starting situations a player can see are read (FP-1). Weights are saved as a plain state dict and loaded with
`weights_only=True`; vocabularies and settings are in `config.json` beside them.
"""
import argparse
import collections
import hashlib
import json
import math
import random
import subprocess
import sys
import time
from pathlib import Path

import torch
from torch import nn

PROJECT = Path(__file__).resolve().parents[2]
VOCAB = PROJECT / "knowledge" / "data" / "vocab-v0.111.1.json"
BASICS = ("STRIKE_IRONCLAD", "DEFEND_IRONCLAD")
ROOMS = ("Monster", "Elite", "Boss")
MAX_DECK, MAX_RELICS, MAX_POTIONS = 60, 40, 5


def load_rows(path):
    return [json.loads(l) for l in Path(path).open() if l.strip()]


def part_of(group, seed):
    """test, val or train for a group: a fixed 15% / 15% / 70% split by a hash of the group name."""
    h = int(hashlib.sha256(f"{seed}:{group}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "test" if h < 0.15 else "val" if h < 0.30 else "train"


class Encoder:
    def __init__(self, encounters, vocab=None):
        v = vocab or json.loads(VOCAB.read_text())
        self.cards = {c: i for i, c in enumerate(v["cards"])}
        self.relics = {c: i for i, c in enumerate(v["relics"])}
        self.potions = {c: i for i, c in enumerate(v["potions"])}
        self.encounters = {e: i + 2 for i, e in enumerate(sorted(encounters))}       # 0 padding, 1 unknown
        self.sizes = {"cards": len(v["cards"]), "relics": len(v["relics"]), "potions": len(v["potions"]), "encounters": len(self.encounters) + 2}

    def row(self, r):
        deck = [(self.cards.get(c.rstrip("+"), 1), 1.0 if c.endswith("+") else 0.0) for c in r["deck"]][:MAX_DECK]
        relics = [self.relics.get(x, 1) for x in r["relics"]][:MAX_RELICS]
        potions = [self.potions.get(x, 1) for x in r["potions"]][:MAX_POTIONS]
        n = max(1, len(r["deck"]))
        room = r.get("room") if r.get("room") in ROOMS else "Monster"
        scal = [r["hp"] / max(1, r["max_hp"]), r["hp"] / 100.0, r["max_hp"] / 100.0, (r.get("ascension") or 0) / 10.0,
                len(r["deck"]) / 30.0, sum(c.endswith("+") for c in r["deck"]) / n, sum(c.rstrip("+") in BASICS for c in r["deck"]) / n,
                len(r["relics"]) / 10.0, len(r["potions"]) / 3.0,
                *[1.0 if (r.get("act") or 1) == a else 0.0 for a in (1, 2, 3)], *[1.0 if room == x else 0.0 for x in ROOMS],
                1.0 if str(r.get("teacher", "mcw6")).startswith("mcw") else 0.0, 1.0 if r.get("potions_allowed") else 0.0]
        return {"deck": deck, "relics": relics, "potions": potions, "enc": self.encounters.get(r["encounter"], 1), "scal": scal}

    def batch(self, rows):
        e = [self.row(r) for r in rows]
        B = len(e)
        deck = torch.zeros(B, MAX_DECK, dtype=torch.long)
        upg = torch.zeros(B, MAX_DECK)
        relics = torch.zeros(B, MAX_RELICS, dtype=torch.long)
        potions = torch.zeros(B, MAX_POTIONS, dtype=torch.long)
        for i, x in enumerate(e):
            for j, (c, u) in enumerate(x["deck"]):
                deck[i, j], upg[i, j] = c, u
            for j, c in enumerate(x["relics"]):
                relics[i, j] = c
            for j, c in enumerate(x["potions"]):
                potions[i, j] = c
        return {"deck": deck, "upg": upg, "relics": relics, "potions": potions, "enc": torch.tensor([x["enc"] for x in e]),
                "scal": torch.tensor([x["scal"] for x in e], dtype=torch.float32)}


N_SCAL = 17


class FightNet(nn.Module):
    def __init__(self, sizes, d=32, hidden=128, drop=0.2):
        super().__init__()
        self.card = nn.Embedding(sizes["cards"], d, padding_idx=0)
        self.card_up = nn.Embedding(sizes["cards"], d, padding_idx=0)
        self.relic = nn.Embedding(sizes["relics"], d, padding_idx=0)
        self.potion = nn.Embedding(sizes["potions"], d, padding_idx=0)
        self.enc = nn.Embedding(sizes["encounters"], d, padding_idx=0)
        self.body = nn.Sequential(nn.Linear(6 * d + N_SCAL, hidden), nn.ReLU(), nn.Dropout(drop), nn.Linear(hidden, hidden), nn.ReLU(), nn.Dropout(drop))
        self.inter = nn.Bilinear(d, d, 16)      # deck against encounter
        self.win = nn.Linear(hidden + 16, 1)
        self.hp = nn.Linear(hidden + 16, 1)

    def forward(self, b):
        m = (b["deck"] > 0).float().unsqueeze(-1)
        cards = (self.card(b["deck"]) + b["upg"].unsqueeze(-1) * self.card_up(b["deck"])) * m
        n = m.sum(1).clamp(min=1)
        deck_mean, deck_sum = cards.sum(1) / n, cards.sum(1) / 10.0
        relics = self.relic(b["relics"]).sum(1) / 5.0
        potions = self.potion(b["potions"]).sum(1)
        enc = self.enc(b["enc"])
        h = self.body(torch.cat([deck_mean, deck_sum, relics, potions, enc, deck_mean * enc, b["scal"]], dim=1))
        h = torch.cat([h, self.inter(deck_mean, enc)], dim=1)
        return self.win(h).squeeze(-1), torch.sigmoid(self.hp(h)).squeeze(-1)


def targets(rows):
    y = torch.tensor([1.0 if r["won"] else 0.0 for r in rows])
    hp = torch.tensor([min(1.0, r["hp_end"] / max(1, r["max_hp"])) if r["won"] else 0.0 for r in rows])
    return y, hp


def auc(p, y):
    order = sorted(range(len(p)), key=lambda i: p[i])
    pos = sum(y)
    neg = len(y) - pos
    if not pos or not neg:
        return None
    rank_sum, i = 0.0, 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and p[order[j + 1]] == p[order[i]]:
            j += 1
        for k in range(i, j + 1):
            if y[order[k]]:
                rank_sum += (i + j) / 2 + 1
        i = j + 1
    return (rank_sum - pos * (pos + 1) / 2) / (pos * neg)


def scores(p, hp, rows):
    """Brier score, log loss and AUC for the win probability; mean absolute error of HP left (in HP) on won fights."""
    y = [1.0 if r["won"] else 0.0 for r in rows]
    if not rows:
        return {}
    brier = sum((a - b) ** 2 for a, b in zip(p, y)) / len(y)
    ll = -sum(b * math.log(max(1e-6, a)) + (1 - b) * math.log(max(1e-6, 1 - a)) for a, b in zip(p, y)) / len(y)
    won = [i for i, r in enumerate(rows) if r["won"]]
    mae = sum(abs(hp[i] * rows[i]["max_hp"] - rows[i]["hp_end"]) for i in won) / len(won) if won else None
    a = auc(p, y)
    return {"n": len(rows), "win_rate": round(sum(y) / len(y), 3), "brier": round(brier, 4), "log_loss": round(ll, 4),
            "auc": round(a, 3) if a is not None else None, "hp_mae_won": round(mae, 1) if mae is not None else None}


def base_rates(train):
    """Baseline: the win rate and mean HP fraction left of the encounter in the training fights (smoothed towards its room's)."""
    room = collections.defaultdict(lambda: [0, 0, 0.0])
    enc = collections.defaultdict(lambda: [0, 0, 0.0])
    for r in train:
        for d, k in ((room, r["room"]), (enc, r["encounter"])):
            d[k][0] += r["won"]
            d[k][1] += 1
            d[k][2] += r["hp_end"] / max(1, r["max_hp"]) if r["won"] else 0.0

    def predict(rows):
        p, hp = [], []
        for r in rows:
            rw, rn, rh = room.get(r["room"], [1, 2, 0.5])
            ew, en, eh = enc.get(r["encounter"], [0, 0, 0.0])
            p.append((ew + 4 * rw / max(1, rn)) / (en + 4))
            hp.append((eh + 4 * rh / max(1, rw)) / (ew + 4) if (ew + 4) else 0.5)
        return p, hp
    return predict


def calibration(p, rows, bins=5):
    order = sorted(range(len(p)), key=lambda i: p[i])
    out = []
    for b in range(bins):
        idx = order[b * len(order) // bins:(b + 1) * len(order) // bins]
        if idx:
            out.append({"predicted": round(sum(p[i] for i in idx) / len(idx), 3), "observed": round(sum(rows[i]["won"] for i in idx) / len(idx), 3), "n": len(idx)})
    return out


def predict(model, enc, rows, bs=1024):
    model.eval()
    p, hp = [], []
    with torch.no_grad():
        for i in range(0, len(rows), bs):
            lo, h = model(enc.batch(rows[i:i + bs]))
            p += torch.sigmoid(lo).tolist()
            hp += h.tolist()
    return p, hp


def train(rows_tr, rows_va, enc, epochs, lr, wd, seed, log):
    torch.manual_seed(seed)
    model = FightNet(enc.sizes)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    btr, (ytr, htr) = enc.batch(rows_tr), targets(rows_tr)
    best, best_state, bad = 1e9, None, 0
    rng = random.Random(seed)
    for ep in range(epochs):
        model.train()
        idx = list(range(len(rows_tr)))
        rng.shuffle(idx)
        for i in range(0, len(idx), 128):
            j = torch.tensor(idx[i:i + 128])
            b = {k: v[j] for k, v in btr.items()}
            lo, h = model(b)
            y, hp = ytr[j], htr[j]
            loss = nn.functional.binary_cross_entropy_with_logits(lo, y) + 2.0 * ((h - hp) ** 2 * y).sum() / y.sum().clamp(min=1)
            opt.zero_grad()
            loss.backward()
            opt.step()
        p, hp = predict(model, enc, rows_va)
        s = scores(p, hp, rows_va)
        if s["log_loss"] < best - 1e-4:
            best, best_state, bad = s["log_loss"], {k: v.clone() for k, v in model.state_dict().items()}, 0
        else:
            bad += 1
        if log and ep % 5 == 0:
            print(f"epoch {ep}: val log loss {s['log_loss']} brier {s['brier']} auc {s['auc']}", flush=True)
        if bad >= 12:
            break
    model.load_state_dict(best_state)
    return model


def report(model, enc, parts, base):
    out = {}
    for name in ("val", "test"):
        rows = parts[name]
        p, hp = predict(model, enc, rows)
        bp, bhp = base(rows)
        out[name] = {"model": scores(p, hp, rows), "base_rate": scores(bp, bhp, rows),
                     "by_room": {room: {"model": scores([p[i] for i, r in enumerate(rows) if r["room"] == room], [hp[i] for i, r in enumerate(rows) if r["room"] == room], [r for r in rows if r["room"] == room]),
                                        "base_rate": scores([bp[i] for i, r in enumerate(rows) if r["room"] == room], [bhp[i] for i, r in enumerate(rows) if r["room"] == room], [r for r in rows if r["room"] == room])}
                                 for room in ROOMS},
                     "calibration": calibration(p, rows),
                     "calibration_boss": calibration([p[i] for i, r in enumerate(rows) if r["room"] == "Boss"], [r for r in rows if r["room"] == "Boss"])}
    return out


class FightModel:
    """Loaded model for use by other tools: `FightModel.load(folder).predict(rows)` -> [(win probability, HP fraction left if won)]."""
    def __init__(self, model, enc, config):
        self.model, self.enc, self.config = model, enc, config

    @classmethod
    def load(cls, folder):
        folder = Path(folder)
        cfg = json.loads((folder / "config.json").read_text())
        enc = Encoder(cfg["encounters"])
        model = FightNet(enc.sizes)
        model.load_state_dict(torch.load(folder / "model.pt", map_location="cpu", weights_only=True))
        model.eval()
        return cls(model, enc, cfg)

    def predict(self, rows):
        p, hp = predict(self.model, self.enc, rows)
        return list(zip(p, hp))


def export_weights(model, folder):
    """The weights as plain numbers (`weights.json`), for the forward pass without the learning library
    (`tools/learn/fight_predict.py`, used inside rollouts)."""
    sd = {k: [[round(x, 6) for x in row] for row in v.tolist()] if v.dim() == 2 else
             [[[round(x, 6) for x in row] for row in mat] for mat in v.tolist()] if v.dim() == 3 else [round(x, 6) for x in v.tolist()]
          for k, v in model.state_dict().items()}
    (Path(folder) / "weights.json").write_text(json.dumps(sd))


def check_export(folder, rows, n=400):
    """Largest difference between this model's predictions and those of the plain forward pass on `n` rows."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import fight_predict
    fm, fp = FightModel.load(folder), fight_predict.FightPredictor(folder)
    rows = rows[:: max(1, len(rows) // n)][:n]
    a = fm.predict(rows)
    b = [fp.predict(r) for r in rows]
    return {"rows": len(rows), "max_abs_diff_win": max(abs(x[0] - y[0]) for x, y in zip(a, b)), "max_abs_diff_hp": max(abs(x[1] - y[1]) for x, y in zip(a, b))}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=str(PROJECT / "data" / "learn" / "fights" / "fights-v1.jsonl"))
    ap.add_argument("--out")
    ap.add_argument("--eval", help="a trained model folder: report it on --data (all rows) instead of training")
    ap.add_argument("--export", help="a trained model folder: write its weights as plain numbers (weights.json) and check them against --data")
    ap.add_argument("--epochs", type=int, default=80)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--wd", type=float, default=1e-2)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    rows = load_rows(a.data)
    if a.export:
        export_weights(FightModel.load(a.export).model, a.export)
        print(json.dumps(check_export(a.export, rows)))
        return 0
    if a.eval:
        fm = FightModel.load(a.eval)
        p, hp = predict(fm.model, fm.enc, rows)
        print(json.dumps({"all": scores(p, hp, rows), "by_room": {room: scores([p[i] for i, r in enumerate(rows) if r["room"] == room], [hp[i] for i, r in enumerate(rows) if r["room"] == room], [r for r in rows if r["room"] == room]) for room in ROOMS},
                          "calibration": calibration(p, rows)}, indent=1))
        return 0
    parts = {"train": [], "val": [], "test": []}
    for r in rows:
        parts[part_of(r["group"], a.seed)].append(r)
    enc = Encoder({r["encounter"] for r in parts["train"]})
    t0 = time.time()
    model = train(parts["train"], parts["val"], enc, a.epochs, a.lr, a.wd, a.seed, log=True)
    rep = report(model, enc, parts, base_rates(parts["train"]))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out / "model.pt")
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT, capture_output=True, text=True).stdout.strip()
    cfg = {"name": out.name, "created": time.strftime("%Y-%m-%d %H:%M"), "code_commit": head, "data": str(Path(a.data).name),
           "rows": {k: len(v) for k, v in parts.items()}, "groups": {k: len({r["group"] for r in v}) for k, v in parts.items()},
           "encounters": sorted(enc.encounters), "seed": a.seed, "epochs": a.epochs, "lr": a.lr, "wd": a.wd,
           "train_seconds": round(time.time() - t0, 1), "report": rep}
    (out / "config.json").write_text(json.dumps(cfg, indent=1))
    export_weights(model, out)
    print(json.dumps(rep, indent=1))
    print(json.dumps({"export_check": check_export(out, parts["test"] or rows)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
