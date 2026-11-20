#!/usr/bin/env python3
"""Train and evaluate a combat value network (P9.E2.S1) on self-play datasets (`tools/selfplay.py`).

    .venv-learn/bin/python -I tools/learn/train_value.py --data data/learn/combat-v1 --name value-v1

Every decision state of every finished fight is an example; its targets are the fight's final result under the
generating policy (won or lost, HP left after a win, enemy HP left after a loss). Splits are by source run of the
Player's history, so no run sits on both sides (`--split-seed`); the benchmark's (source run, floor) pairs
(`data/sim/benchmark-v1.json`) never enter training or validation and are reported as their own test set. Model
choices use the validation split only; the test splits are read once, after training.

Reported against three baselines on the same states: the training mean, a linear model on the encoder's global
features (stand-in for the hand-made leaf heuristic of P8.E3.S1, which does not exist yet), and the search's own
estimate stored with each decision (k planner rollouts of the chosen action; slow, so not usable at search leaves).

Writes `models/<name>/model.pt` (ignored), `models/<name>/metrics.json` and `models/<name>/MODEL_CARD.md`.
"""
import argparse
import json
import math
import random
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "tools" / "learn"))
import torch  # noqa: E402

import encode as E  # noqa: E402
import model as M  # noqa: E402

BENCH = PROJECT / "data" / "sim" / "benchmark-v1.json"


def value_of(outcome):
    """The search's value scale (tools/sim.py _value)."""
    return outcome["hp"] if outcome["status"] == "won" else -100 - outcome["enemy_hp_left"]


def load_examples(folders, enc):
    bench = {(f["source"]["run"], f["source"]["floor"]) for f in json.loads(BENCH.read_text())["fights"]}
    ex, fights, skipped = [], 0, 0
    for folder in folders:
        for shard in sorted(Path(folder).glob("shard-*.jsonl")):
            for line in shard.open():
                r = json.loads(line)
                o = r.get("outcome")
                if not o or o.get("blocked") or o["status"] not in ("won", "lost") or not r["decisions"]:
                    skipped += 1
                    continue
                src = r["spec"].get("source") or {}
                run = src.get("run", f"synthetic-{r['seed']}")
                fid = f"{Path(folder).name}/{r['seed']}"
                fights += 1
                for d_i, d in enumerate(r["decisions"]):
                    search = d["values"][d["chosen"]] if d["values"] and d["values"][0] is not None else None
                    ex.append({"enc": enc.encode(d["obs"]), "won": 1.0 if o["status"] == "won" else 0.0, "hp": o["hp"] / 100.0,
                               "left": o["enemy_hp_left"] / 100.0, "value": float(value_of(o)), "search": search, "run": run,
                               "bench": (run, src.get("floor")) in bench, "fight": fid, "d": d_i, "n": len(r["decisions"]),
                               "act": r["spec"].get("act"), "room": r["spec"].get("room")})
    return ex, fights, skipped


def split(ex, seed, test_share=0.15, val_share=0.15):
    runs = sorted({e["run"] for e in ex})
    random.Random(seed).shuffle(runs)
    n_test, n_val = max(1, round(len(runs) * test_share)), max(1, round(len(runs) * val_share))
    test_runs, val_runs = set(runs[:n_test]), set(runs[n_test:n_test + n_val])
    parts = {"train": [], "val": [], "test": [], "bench": []}
    for e in ex:
        if e["bench"]:
            parts["bench"].append(e)
        elif e["run"] in test_runs:
            parts["test"].append(e)
        elif e["run"] in val_runs:
            parts["val"].append(e)
        else:
            parts["train"].append(e)
    return parts, {"test_runs": sorted(test_runs), "val_runs": sorted(val_runs), "runs": len(runs)}


def tensors(part):
    b = M.collate([e["enc"] for e in part])
    y = torch.tensor([[e["won"], e["hp"], e["left"]] for e in part], dtype=torch.float32)
    return b, y


def loss_fn(out, y):
    won = y[:, 0]
    l_win = torch.nn.functional.binary_cross_entropy_with_logits(out[:, 0], won)
    l_hp = ((out[:, 1] - y[:, 1]) ** 2 * won).sum() / won.sum().clamp(min=1)
    l_left = ((out[:, 2] - y[:, 2]) ** 2 * (1 - won)).sum() / (1 - won).sum().clamp(min=1)
    return l_win + l_hp + l_left


def predict(model, b, device, bs=2048):
    model.eval()
    outs = []
    with torch.no_grad():
        n = b["glob"].shape[0]
        for i in range(0, n, bs):
            idx = torch.arange(i, min(i + bs, n))
            outs.append(model(M.to_device(M.index_batch(b, idx), device)).cpu())
    return torch.cat(outs) if outs else torch.zeros(0, 3)


def train(model, tr, va, device, epochs, lr, wd, bs, patience, log):
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    (btr, ytr), (bva, yva) = tr, va
    n = ytr.shape[0]
    best, best_state, bad = float("inf"), None, 0
    g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        total = 0.0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            out = model(M.to_device(M.index_batch(btr, idx), device))
            loss = loss_fn(out, ytr[idx].to(device))
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item() * len(idx)
        vl = loss_fn(predict(model, bva, device), yva).item()
        log(f"epoch {ep + 1}: train {total / n:.4f} val {vl:.4f}")
        if vl < best - 1e-4:
            best, bad = vl, 0
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                break
    model.load_state_dict(best_state)
    return best, ep + 1


class Linear(torch.nn.Module):
    """Baseline: linear in the encoder's global features (same three outputs as the network)."""
    def __init__(self, width):
        super().__init__()
        self.lin = torch.nn.Linear(width, 3)
        self.config = {"kind": "linear on glob"}

    def forward(self, b):
        return self.lin(b["glob"])


def auc(scores, labels):
    pairs = sorted(zip(scores, labels))
    pos = sum(labels)
    neg = len(labels) - pos
    if not pos or not neg:
        return None
    rank_sum, i = 0.0, 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        avg = (i + j + 1) / 2
        rank_sum += avg * sum(l for _, l in pairs[i:j])
        i = j
    return (rank_sum - pos * (pos + 1) / 2) / (pos * neg)


def metrics(pred_v, pred_p, part):
    """Value error on the search's scale and win-probability quality."""
    y = [e["value"] for e in part]
    w = [e["won"] for e in part]
    n = len(y)
    if not n:
        return {}
    err = [p - t for p, t in zip(pred_v, y)]
    out = {"states": n, "fights": len({e["fight"] for e in part}), "value_mae": sum(abs(x) for x in err) / n,
           "value_rmse": math.sqrt(sum(x * x for x in err) / n), "value_r": pearson(pred_v, y)}
    if pred_p is not None:
        eps = 1e-6
        out["win_brier"] = sum((p - t) ** 2 for p, t in zip(pred_p, w)) / n
        out["win_logloss"] = -sum(t * math.log(max(p, eps)) + (1 - t) * math.log(max(1 - p, eps)) for p, t in zip(pred_p, w)) / n
        out["win_auc"] = auc(pred_p, w)
    return out


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb) if va and vb else None


def calibration(pred_p, part, bins=10):
    rows = []
    for k in range(bins):
        lo, hi = k / bins, (k + 1) / bins
        sel = [(p, e["won"]) for p, e in zip(pred_p, part) if lo <= p < hi or (k == bins - 1 and p == 1.0)]
        if sel:
            rows.append({"bin": f"{lo:.1f}-{hi:.1f}", "states": len(sel), "predicted": sum(p for p, _ in sel) / len(sel),
                         "observed": sum(w for _, w in sel) / len(sel)})
    return rows


def bootstrap_diff(abs_a, abs_b, part, reps=2000, seed=0):
    """95% interval of mean(|err_a|) - mean(|err_b|), resampling fights (states of one fight are correlated)."""
    by_fight = {}
    for i, e in enumerate(part):
        by_fight.setdefault(e["fight"], []).append(i)
    fights = list(by_fight)
    rng = random.Random(seed)
    diffs = []
    for _ in range(reps):
        idx = [i for f in (rng.choice(fights) for _ in fights) for i in by_fight[f]]
        diffs.append(sum(abs_a[i] - abs_b[i] for i in idx) / len(idx))
    diffs.sort()
    return [diffs[int(0.025 * reps)], diffs[int(0.975 * reps)]]


def model_card(m):
    """MODEL_CARD.md from the training record (P9.E2.S4, ML-9)."""
    def row(name, r):
        f = lambda k: f"{r[k]:.3f}" if isinstance(r.get(k), float) else "–"
        return f"| {name} | {r.get('states', '–')} | {f('value_mae')} | {f('value_rmse')} | {f('value_r')} | {f('win_brier')} | {f('win_auc')} |"
    lines = [f"# Model card: {m['name']}", "",
             f"Combat value network (P9.E2.S1). Trained {m['created']} at code commit `{m['code_commit']}` with PyTorch {m['torch']} on {m['device']}; "
             f"{m['parameters']} parameters; encoder {m['encoder']}; vocabulary of game {m['vocab'].get('game_version')} ({m['vocab'].get('game_commit')}).", "",
             "## What it predicts",
             "From one combat observation: the chance to win the fight, the HP left if it wins, and the enemies' HP left if it loses, under the "
             "policy that generated the data (the search teacher below). `model.expected_value` combines them on the search's value scale "
             "(HP left after a win; -100 minus enemy HP left after a loss). The last two outputs are residuals on the current HP and the current enemy HP.", "",
             "## Inputs (FP-10)",
             "The observation encoder only (`tools/learn/encode.py`, `docs/observation-spec.md`): what a player can see. No seed, generator state, "
             "draw order or future intent is an input; the observation contains none. The training targets are fight outcomes, which are not inputs at play time.", "",
             "## Data (ML-2)"]
    for d in m["data"]:
        man = d["manifest"]
        lines.append(f"- `{d['folder']}`: {man.get('summary', {}).get('fights', '?')} fights, created {man.get('created', '?')}, game {man.get('game_version', '?')}, "
                     f"host `{man.get('host_commit', '?')}`, teacher {json.dumps(man.get('teacher', {}))}.")
    sp = m["split"]
    lines += [f"- Split by source run of the Player's history (seed {m['settings']['split_seed']}; {sp['runs']} runs): states {sp['sizes']}, fights {sp['fights']}. "
              "The benchmark's (source run, floor) pairs are a separate test split and never trained on.", "",
              "## Training", f"- Settings: {json.dumps(m['settings'])}; epochs run {m['epochs_run']} (early stopping on validation loss {m['best_val_loss']:.4f}); "
              f"{m['train_seconds']} s.", "",
              "## Evaluation", "Errors are on the search's value scale against the realized outcome of each state's fight. "
              "Baselines: the training mean; a linear model on the encoder's global features (stand-in for the hand-made leaf heuristic of P8.E3.S1, not built); "
              "the search's own estimate stored with each decision (6 planner rollouts of the chosen action, about 2 s per decision).", ""]
    for split_name, res in m["results"].items():
        lines += [f"### {split_name}", "", "| Model | States | Value MAE | RMSE | r | Win Brier | Win AUC |", "|---|---|---|---|---|---|---|",
                  row("network", res["network"]), row("linear", res["linear"]), row("mean", res["mean"])]
        ss = res.get("search_estimate_subset") or {}
        if ss.get("search"):
            lines += [row("network (states with a search estimate)", ss["network"]), row("search estimate", ss["search"])]
        ci = m["bootstrap_95"].get(split_name, {})
        lines += ["", "Bootstrap 95% intervals (fights resampled): " + "; ".join(f"{k} {v[0]:.2f} to {v[1]:.2f}" for k, v in ci.items()), ""]
        cal = m["calibration"].get(split_name) or []
        if cal:
            lines += ["Calibration of the win probability: " + "; ".join(f"{c['bin']}: predicted {c['predicted']:.2f}, observed {c['observed']:.2f} ({c['states']})" for c in cal), ""]
    sp_ms = m["speed_ms"]
    lines += ["## Speed (P9.E2.S3)", f"CPU, one thread per process under load: one state {sp_ms['single_state']} ms, a batch of 64 {sp_ms['batch_64']} ms, "
              f"turning one encoding into tensors {sp_ms['collate_one']} ms.", "",
              "## Known limits",
              "- It predicts outcomes under the teacher's play, not under perfect play; positions the teacher misplays are valued pessimistically.",
              "- Trained on simulated fights only; the simulator's known differences (`docs/simulator-integrity.md`) carry over. Live use needs pile contents, "
              "which the live state does not list (`piles_known` = 0 there); not yet checked on live fights.",
              "- Fight specs come from the Player's history (mostly v0.107.1 runs) replayed on v0.111.1: enchantments missing, relics removed before a fight missing, potions capped at 3.",
              "- Ids added by a later patch map to the unknown entry until the vocabulary is rebuilt and the model retrained (P9.E7.S1).", ""]
    return "\n".join(lines) + "\n"


def git_commit():
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT, capture_output=True, text=True).stdout.strip()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--split-seed", type=int, default=7)
    ap.add_argument("--epochs", type=int, default=80)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--wd", type=float, default=1e-4)
    ap.add_argument("--bs", type=int, default=256)
    ap.add_argument("--patience", type=int, default=8)
    ap.add_argument("--hidden", type=int, default=256)
    ap.add_argument("--card-dim", type=int, default=32)
    ap.add_argument("--drop", type=float, default=0.1)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--dev", action="store_true", help="development run: report the validation split only (test splits stay unread)")
    a = ap.parse_args(argv)
    torch.set_num_threads(a.threads)
    torch.manual_seed(0)
    out_dir = PROJECT / "models" / a.name
    out_dir.mkdir(parents=True, exist_ok=True)
    log_lines = []

    def log(msg):
        print(msg, flush=True)
        log_lines.append(msg)

    t0 = time.time()
    enc = E.Encoder()
    ex, fights, skipped = load_examples(a.data, enc)
    parts, split_info = split(ex, a.split_seed)
    log(f"{len(ex)} states from {fights} fights ({skipped} skipped); " + ", ".join(f"{k} {len(v)}" for k, v in parts.items())
        + f"; unknown ids {len(enc.unknown)}")
    data = {k: tensors(v) for k, v in parts.items() if v}

    lin = Linear(len(E.GLOBAL_FIELDS))
    lin_val, lin_epochs = train(lin, data["train"], data["val"], "cpu", 300, 1e-2, 0.0, 512, 20, lambda m: None)
    log(f"linear baseline: val loss {lin_val:.4f} after {lin_epochs} epochs")

    model = M.ValueNet(enc.sizes(), a.card_dim, a.hidden, a.drop).to(a.device)
    params = sum(p.numel() for p in model.parameters())
    log(f"value network: {params} parameters on {a.device}")
    best_val, epochs = train(model, data["train"], data["val"], a.device, a.epochs, a.lr, a.wd, a.bs, a.patience, log)
    train_seconds = round(time.time() - t0)
    model = model.cpu()

    mean_v = sum(e["value"] for e in parts["train"]) / len(parts["train"])
    mean_w = sum(e["won"] for e in parts["train"]) / len(parts["train"])
    results, calib, cis = {}, {}, {}
    for name in (("val",) if a.dev else ("val", "test", "bench")):
        part = parts.get(name) or []
        if not part:
            continue
        b, _ = data[name]
        out_n = predict(model, b, "cpu")
        out_l = predict(lin, b, "cpu")
        vn, pn = M.expected_value(out_n).tolist(), torch.sigmoid(out_n[:, 0]).tolist()
        vl, pl = M.expected_value(out_l).tolist(), torch.sigmoid(out_l[:, 0]).tolist()
        res = {"network": metrics(vn, pn, part), "linear": metrics(vl, pl, part),
               "mean": metrics([mean_v] * len(part), [mean_w] * len(part), part)}
        with_search = [i for i, e in enumerate(part) if e["search"] is not None]
        sub = [part[i] for i in with_search]
        res["search_estimate_subset"] = {"network": metrics([vn[i] for i in with_search], None, sub),
                                         "search": metrics([part[i]["search"] for i in with_search], None, sub)}
        first = [i for i, e in enumerate(part) if e["d"] == 0]
        res["fight_start"] = {"network": metrics([vn[i] for i in first], [pn[i] for i in first], [part[i] for i in first]),
                              "linear": metrics([vl[i] for i in first], [pl[i] for i in first], [part[i] for i in first])}
        results[name] = res
        calib[name] = calibration(pn, part)
        err_n = [abs(v - e["value"]) for v, e in zip(vn, part)]
        err_l = [abs(v - e["value"]) for v, e in zip(vl, part)]
        cis[name] = {"network_minus_linear_mae": bootstrap_diff(err_n, err_l, part)}
        if with_search:
            err_s = [abs(part[i]["search"] - part[i]["value"]) for i in with_search]
            cis[name]["network_minus_search_mae"] = bootstrap_diff([err_n[i] for i in with_search], err_s, sub)

    # speed: batch inference on CPU
    b, _ = data["test"] if "test" in data else data["val"]
    one = M.index_batch(b, torch.arange(1))
    many = M.index_batch(b, torch.arange(min(64, b["glob"].shape[0])))
    with torch.no_grad():
        for _ in range(5):
            model(one)
        t = time.time()
        for _ in range(200):
            model(one)
        single_ms = (time.time() - t) / 200 * 1000
        t = time.time()
        for _ in range(50):
            model(many)
        batch_ms = (time.time() - t) / 50 * 1000
    enc_t = time.time()
    for e in parts["val"][:500]:
        M.collate([e["enc"]])
    collate_ms = (time.time() - enc_t) / max(1, min(500, len(parts["val"]))) * 1000

    manifests = []
    for folder in a.data:
        mf = Path(folder) / "manifest.json"
        manifests.append(json.loads(mf.read_text()) if mf.exists() else {"dataset": Path(folder).name, "manifest": "missing (batch still running)"})
    meta = {"name": a.name, "created": time.strftime("%Y-%m-%d %H:%M"), "code_commit": git_commit(), "encoder": E.ENCODER_VERSION,
            "vocab": enc.about, "torch": torch.__version__, "device": a.device, "parameters": params,
            "settings": {k: getattr(a, k) for k in ("epochs", "lr", "wd", "bs", "patience", "hidden", "card_dim", "drop", "split_seed")},
            "epochs_run": epochs, "best_val_loss": best_val, "train_seconds": train_seconds,
            "data": [{"folder": str(Path(f).resolve().relative_to(PROJECT)), "manifest": m} for f, m in zip(a.data, manifests)],
            "split": split_info | {"sizes": {k: len(v) for k, v in parts.items()}, "fights": {k: len({e["fight"] for e in v}) for k, v in parts.items()}},
            "baselines": {"mean_value": mean_v, "mean_win": mean_w, "linear_val_loss": lin_val},
            "results": results, "calibration": calib, "bootstrap_95": cis,
            "speed_ms": {"single_state": round(single_ms, 3), "batch_64": round(batch_ms, 3), "collate_one": round(collate_ms, 3)},
            "log": log_lines}
    if not a.dev:
        (out_dir / "MODEL_CARD.md").write_text(model_card(meta))
    M.save(model, out_dir / "model.pt", {"name": a.name, "encoder": E.ENCODER_VERSION, "vocab_version": enc.about.get("game_version")})
    (out_dir / "metrics.json").write_text(json.dumps(meta, indent=1))
    log(json.dumps({k: {m: {x: round(y, 3) if isinstance(y, float) else y for x, y in v.items()} for m, v in r.items() if m in ("network", "linear", "mean")}
                    for k, r in results.items()}, indent=1))
    log(f"wrote {out_dir.relative_to(PROJECT)}/model.pt and metrics.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
