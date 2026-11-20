#!/usr/bin/env python3
"""Train and evaluate the action-value network (P9.E3.S1) on the search teacher's candidate values.

    .venv-learn/bin/python -I tools/learn/train_q.py --data data/learn/combat-v1 --name q-v1

Examples are decisions with at least two candidates; targets are the teacher's mean value per candidate (search value
scale / 100, clipped to [-4, 1.2]) and its choice. Loss: squared error on the values plus a cross-entropy term that
asks the highest predicted value to be the teacher's choice. Splits as in `train_value.py` (by source run; the
benchmark's (source run, floor) pairs held out). Reported: agreement with the teacher's choice and the regret of the
network's pick measured with the teacher's own values (how much search value is given up), against picking the first
candidate (the planner's safe-mode plan) and a random candidate. `--dev` reports the validation split only.
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "tools" / "learn"))
import torch  # noqa: E402

import encode as E  # noqa: E402
import model as M  # noqa: E402
import train_value as TV  # noqa: E402


def load(folders, enc):
    bench = {(f["source"]["run"], f["source"]["floor"]) for f in json.loads(TV.BENCH.read_text())["fights"]}
    ex = []
    for folder in folders:
        for shard in sorted(Path(folder).glob("shard-*.jsonl")):
            for line in shard.open():
                r = json.loads(line)
                if not r.get("outcome") or not r["decisions"]:
                    continue
                src = r["spec"].get("source") or {}
                run = src.get("run", f"synthetic-{r['seed']}")
                for d in r["decisions"]:
                    cands, vals = d["candidates"][:M.MAX_CANDS], d["values"][:M.MAX_CANDS]
                    if len(cands) < 2 or vals[0] is None or any(c["type"] == "choose" for c in cands):
                        continue
                    ex.append({"enc": enc.encode(d["obs"]), "cands": cands, "vals": [max(-4.0, min(1.2, v / 100.0)) for v in vals],
                               "chosen": d["chosen"], "run": run, "bench": (run, src.get("floor")) in bench, "fight": f"{Path(folder).name}/{r['seed']}"})
    return ex


def tensors(part):
    b = M.collate([e["enc"] for e in part]) | M.collate_actions([e["cands"] for e in part])
    q = torch.zeros(len(part), M.MAX_CANDS)
    mask = torch.zeros(len(part), M.MAX_CANDS)
    for i, e in enumerate(part):
        q[i, :len(e["vals"])] = torch.tensor(e["vals"])
        mask[i, :len(e["vals"])] = 1
    chosen = torch.tensor([e["chosen"] for e in part])
    return b, (q, mask, chosen)


def loss_fn(pred, y, ce_weight=0.3, temp=0.1):
    q, mask, chosen = y
    mse = (((pred - q) ** 2) * mask).sum() / mask.sum()
    logits = (pred / temp).masked_fill(mask == 0, -1e9)
    return mse + ce_weight * torch.nn.functional.cross_entropy(logits, chosen)


def predict(model, b, bs=2048):
    model.eval()
    out = []
    with torch.no_grad():
        n = b["glob"].shape[0]
        for i in range(0, n, bs):
            out.append(model(M.index_batch(b, torch.arange(i, min(i + bs, n)))))
    return torch.cat(out)


def evaluate(pred, part, seed=0):
    rng = random.Random(seed)
    res = {"decisions": len(part), "fights": len({e["fight"] for e in part})}
    picks = {"network": [], "first": [], "random": []}
    for i, e in enumerate(part):
        n = len(e["vals"])
        picks["network"].append(max(range(n), key=lambda j: pred[i, j].item()))
        picks["first"].append(0)
        picks["random"].append(rng.randrange(n))
    for name, pk in picks.items():
        agree = sum(1 for p, e in zip(pk, part) if p == e["chosen"]) / len(part)
        regret = sum((max(e["vals"]) - e["vals"][p]) * 100 for p, e in zip(pk, part)) / len(part)
        res[name] = {"agreement": round(agree, 4), "regret": round(regret, 3)}
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--split-seed", type=int, default=7)
    ap.add_argument("--epochs", type=int, default=80)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--wd", type=float, default=1e-3)
    ap.add_argument("--bs", type=int, default=256)
    ap.add_argument("--patience", type=int, default=8)
    ap.add_argument("--hidden", type=int, default=128)
    ap.add_argument("--card-dim", type=int, default=16)
    ap.add_argument("--drop", type=float, default=0.2)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--dev", action="store_true")
    a = ap.parse_args(argv)
    torch.set_num_threads(a.threads)
    torch.manual_seed(0)
    out_dir = PROJECT / "models" / a.name
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    enc = E.Encoder()
    ex = load(a.data, enc)
    parts, split_info = TV.split(ex, a.split_seed)
    print(f"{len(ex)} decisions; " + ", ".join(f"{k} {len(v)}" for k, v in parts.items()), flush=True)
    data = {k: tensors(v) for k, v in parts.items() if v}
    model = M.QNet(enc.sizes(), a.card_dim, a.hidden, a.drop)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=a.wd)
    (btr, ytr), (bva, yva) = data["train"], data["val"]
    n = ytr[0].shape[0]
    best, best_state, bad, g = float("inf"), None, 0, torch.Generator().manual_seed(0)
    for ep in range(a.epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, a.bs):
            idx = perm[i:i + a.bs]
            loss = loss_fn(model(M.index_batch(btr, idx)), tuple(t[idx] for t in ytr))
            opt.zero_grad()
            loss.backward()
            opt.step()
        vl = loss_fn(predict(model, bva), yva).item()
        print(f"epoch {ep + 1}: val {vl:.4f}", flush=True)
        if vl < best - 1e-4:
            best, bad, best_state = vl, 0, {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= a.patience:
                break
    model.load_state_dict(best_state)
    results = {}
    for name in (("val",) if a.dev else ("val", "test", "bench")):
        if parts.get(name):
            results[name] = evaluate(predict(model, data[name][0]), parts[name])
    b1 = M.index_batch(data["val"][0], torch.arange(1))
    with torch.no_grad():
        t = time.time()
        for _ in range(200):
            model(b1)
        single_ms = (time.time() - t) / 200 * 1000
    meta = {"name": a.name, "created": time.strftime("%Y-%m-%d %H:%M"), "code_commit": TV.git_commit(), "encoder": E.ENCODER_VERSION,
            "torch": torch.__version__, "parameters": sum(p.numel() for p in model.parameters()),
            "settings": {k: getattr(a, k) for k in ("epochs", "lr", "wd", "bs", "patience", "hidden", "card_dim", "drop", "split_seed")},
            "epochs_run": ep + 1, "best_val_loss": best, "train_seconds": round(time.time() - t0),
            "data": [str(Path(f).resolve().relative_to(PROJECT)) for f in a.data],
            "split": split_info | {"sizes": {k: len(v) for k, v in parts.items()}}, "results": results, "single_decision_ms": round(single_ms, 3)}
    M.save(model, out_dir / "model.pt", {"name": a.name, "kind": "q", "encoder": E.ENCODER_VERSION})
    (out_dir / "metrics.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(results, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
