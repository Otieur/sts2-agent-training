#!/usr/bin/env python3
"""Paired benchmark of combat policies on `data/sim/benchmark-v1.json` (P8.E1.S3, P9.E2.S2).

Each job is one benchmark fight with one sample seed; the worker that claims it plays the fight once with every policy
in turn, so the policies meet the same fight, the same seeds and the same machine load (decision times are comparable).

    .venv-learn/bin/python -I tools/learn/bench.py --out data/learn/bench/vsearch-1 --arms planner mc vleaf \
        --model models/value-v1/model.pt --seeds 2 --workers 6
    .venv-learn/bin/python -I tools/learn/bench.py --report data/learn/bench/vsearch-1

Policies (arms):
- `planner`: the rule planner (`tools/plan_turn.py`, balanced).
- `mc`: flat Monte Carlo over the planner's candidates, k re-sampled worlds each, rollouts to the end of the fight with
  the planner (the current self-play teacher, `tools/selfplay.py scored_search`).
- `vleaf`: the same candidates and re-sampled worlds, but each rollout stops at the start of the next player turn (the
  planner plays the rest of the current turn) and the value network scores the position; positions where the fight has
  ended are scored exactly. Leaves are scored in one batch per decision.
- `vleafK` (for example `vleaf2`): `vleaf` with K worlds per candidate.
- `vgreedy` / `vgreedyK`: one ply; each candidate played on K re-sampled worlds (default 1) and the position right after
  it scored by the network. The fast policy.

Cost note (measured 2026-11-20): a restore rebuilds the fight from its start and costs about 100 ms under load, while a
planner rollout to the end of the fight costs about 2 ms per step, so search time is driven by the number of restores
(candidates × worlds), not by rollout depth.

Only what the player can see is used: search restores the past and re-samples the hidden future (FP-15); the network
reads the observation encoder alone (FP-10). Writes `shard-<w>.jsonl` (one job per line) and `manifest.json`.
"""
import argparse
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "tools"))
sys.path.insert(0, str(PROJECT / "tools" / "learn"))
import plan_turn as pt  # noqa: E402
import selfplay as SP  # noqa: E402
import sim as S  # noqa: E402

BENCH = PROJECT / "data" / "sim" / "benchmark-v1.json"
SEED_BASE = 7_000_000


def planner_search(sim, obs, d, done):
    return [S.planner_action(pt, obs, "balanced")], [None], 0


def mc_search(k, top=2, mode="balanced"):
    return lambda sim, obs, d, done: SP.scored_search(sim, obs, mode, k, top, d, done)


def _to_next_turn(sim, obs, limit=80):
    """Play the planner until the next player turn starts or the fight ends."""
    t0 = obs.get("turn")
    for _ in range(limit):
        if obs["status"] != "in_progress" or obs.get("blocked") or obs.get("turn") != t0:
            break
        try:
            obs = sim.step(S.planner_action(pt, obs, "balanced"))
        except S.SimError:
            obs = sim.step({"type": "end_turn"})
    return obs


class ValueLeaf:
    def __init__(self, model_path, k, top=2):
        import torch
        import encode as E
        import model as M
        torch.set_num_threads(1)
        self.torch, self.M = torch, M
        self.model, self.meta = M.load(model_path)
        self.enc = E.Encoder()
        self.k, self.top = k, top

    def values(self, obs_list):
        if not obs_list:
            return []
        with self.torch.no_grad():
            out = self.model(self.M.collate([self.enc.encode(o) for o in obs_list]))
            return self.M.expected_value(out).tolist()

    def __call__(self, sim, obs, d, done):
        cands = S.search_candidates(sim, pt, obs, self.top)
        if len(cands) == 1:
            return cands, [None], 0
        snap = sim.call(cmd="snapshot")["id"]
        for ci, a in enumerate(cands):
            for j in range(self.k):
                if (ci, j) in done:
                    continue
                if sim.call(cmd="restore", id=snap)["obs"]["status"] != "in_progress":
                    raise SP.Tainted("restore did not give back the decision state")
                sim.call(cmd="resample", sample_seed=1_000_003 * (d + 1) + j)
                try:
                    o = sim.step(a)
                except S.SimError:
                    done[(ci, j)] = -1000.0
                    continue
                f = _to_next_turn(sim, o)
                if f["status"] == "in_progress" and (f.get("blocked") or f.get("turn") == o.get("turn")):
                    done[(ci, j)] = None
                    raise SP.Tainted(f"rollout stuck (candidate {ci}, sample {j}, blocked {bool(f.get('blocked'))})")
                done[(ci, j)] = float(S._value(f)) if f["status"] != "in_progress" else ("leaf", f)
        if sim.call(cmd="restore", id=snap)["obs"]["status"] != "in_progress":
            raise SP.Tainted("restore did not give back the decision state")
        leaves = [key for key, v in done.items() if isinstance(v, tuple)]
        for key, v in zip(leaves, self.values([done[key][1] for key in leaves])):
            done[key] = v
        values = []
        for ci in range(len(cands)):
            vals = [done[(ci, j)] for j in range(self.k) if done.get((ci, j)) is not None]
            values.append(sum(vals) / len(vals) if vals else -1000.0)
        return cands, values, max(range(len(cands)), key=lambda i: values[i])


class ValueGreedy(ValueLeaf):
    """One ply: each candidate is played on k re-sampled worlds (default 1) and the position right after it is scored
    by the network. One restore per candidate and world instead of a rollout; the fast policy for live play."""
    def __call__(self, sim, obs, d, done):
        cands = S.search_candidates(sim, pt, obs, self.top)
        if len(cands) == 1:
            return cands, [None], 0
        snap = sim.call(cmd="snapshot")["id"]
        leaves = {}
        for ci, a in enumerate(cands):
            for j in range(self.k):
                if sim.call(cmd="restore", id=snap)["obs"]["status"] != "in_progress":
                    raise SP.Tainted("restore did not give back the decision state")
                sim.call(cmd="resample", sample_seed=1_000_003 * (d + 1) + j)
                try:
                    o = sim.step(a)
                except S.SimError:
                    leaves[(ci, j)] = -1000.0
                    continue
                if o.get("blocked"):
                    raise SP.Tainted(f"step stuck (candidate {ci}, sample {j})")
                leaves[(ci, j)] = float(S._value(o)) if o["status"] != "in_progress" else ("leaf", o)
        if sim.call(cmd="restore", id=snap)["obs"]["status"] != "in_progress":
            raise SP.Tainted("restore did not give back the decision state")
        keys = [key for key, v in leaves.items() if isinstance(v, tuple)]
        for key, v in zip(keys, self.values([leaves[key][1] for key in keys])):
            leaves[key] = v
        values = [sum(leaves[(ci, j)] for j in range(self.k)) / self.k for ci in range(len(cands))]
        return cands, values, max(range(len(cands)), key=lambda i: values[i])


def make_arm(name, model_path):
    if name == "planner":
        return planner_search
    m = re.fullmatch(r"mc(\d*)", name)
    if m:
        return mc_search(int(m.group(1) or 6))
    m = re.fullmatch(r"vleaf(\d*)", name)
    if m:
        return ValueLeaf(model_path, int(m.group(1) or 6))
    m = re.fullmatch(r"vgreedy(\d*)", name)
    if m:
        return ValueGreedy(model_path, int(m.group(1) or 1))
    raise ValueError(f"unknown arm {name}")


def value_of(o):
    return o["hp"] if o["status"] == "won" else -100 - o["enemy_hp_left"]


def worker(a):
    out = Path(a.out)
    shard = out / f"shard-{a.worker:02d}.jsonl"
    fights = json.loads(BENCH.read_text())["fights"]
    jobs = [(i, s) for s in range(a.seeds) for i in range(len(fights))][:a.limit or None]
    done_jobs = set()
    for f in out.glob("shard-*.jsonl"):
        for line in f.open():
            r = json.loads(line)
            done_jobs.add((r["fight"], r["sample"]))
    arms = {name: make_arm(name, a.model) for name in a.arms}
    host = SP.Host()
    try:
        for i, s in jobs:
            if (i, s) in done_jobs or not SP.claim(out, i * 100 + s):
                continue
            spec = fights[i]
            seed = SEED_BASE + i * 10 + s
            rec = {"fight": i, "sample": s, "seed": seed, "encounter": spec["encounter"], "room": spec["room"], "act": spec["act"], "arms": {}}
            for name, search in arms.items():
                t0 = time.time()
                try:
                    r = SP.play(host, spec, seed, search)
                    o = r["outcome"]
                    rec["arms"][name] = {"status": o["status"], "hp": o["hp"], "enemy_hp_left": o["enemy_hp_left"], "value": value_of(o),
                                         "decisions": o["decisions"], "turns": o["turns"], "seconds": round(time.time() - t0, 2),
                                         "search_seconds": o["search_seconds"], "restarts": o["host_restarts"], "blocked": o["blocked"]}
                except S.SimError as e:
                    rec["arms"][name] = {"error": str(e)[:300], "seconds": round(time.time() - t0, 2)}
                    host.restart()
            with shard.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(f"w{a.worker} fight {i} sample {s} {spec['encounter']}: "
                  + ", ".join(f"{n} {v.get('value', 'error')} ({v.get('seconds')} s)" for n, v in rec["arms"].items()), flush=True)
    finally:
        host.close()
    return 0


def load(folder):
    return [json.loads(l) for f in sorted(Path(folder).glob("shard-*.jsonl")) for l in f.open()]


def sign_test(better, worse):
    n = better + worse
    if n == 0:
        return 1.0
    return sum(math.comb(n, i) for i in range(better, n + 1)) / 2 ** n


def paired(recs, a, b, reps=4000, seed=0):
    rows = [(r["arms"][a]["value"], r["arms"][b]["value"]) for r in recs
            if "value" in r["arms"].get(a, {}) and "value" in r["arms"].get(b, {})
            and not r["arms"][a].get("blocked") and not r["arms"][b].get("blocked")]
    diffs = [y - x for x, y in rows]
    better, worse = sum(1 for d in diffs if d > 0), sum(1 for d in diffs if d < 0)
    rng = random.Random(seed)
    boots = sorted(sum(rng.choice(diffs) for _ in diffs) / len(diffs) for _ in range(reps)) if diffs else [0]
    return {"pairs": len(diffs), "mean_diff": sum(diffs) / len(diffs) if diffs else 0, "better": better, "worse": worse,
            "equal": len(diffs) - better - worse, "sign_p_one_sided": sign_test(better, worse),
            "boot95": [boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]]}


def summarize(recs, arms):
    out = {}
    for n in arms:
        rs = [r["arms"][n] for r in recs if n in r["arms"]]
        ok = [x for x in rs if "value" in x]
        dec = sum(x["decisions"] for x in ok)
        out[n] = {"games": len(rs), "errors": len(rs) - len(ok), "won": sum(1 for x in ok if x["status"] == "won"),
                  "mean_value": sum(x["value"] for x in ok) / max(len(ok), 1),
                  "mean_hp_if_won": sum(x["hp"] for x in ok if x["status"] == "won") / max(1, sum(1 for x in ok if x["status"] == "won")),
                  "seconds": round(sum(x["seconds"] for x in ok), 1),
                  "search_seconds_per_decision": round(sum(x["search_seconds"] for x in ok) / max(dec, 1), 3),
                  "restarts": sum(x.get("restarts", 0) for x in ok)}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out")
    ap.add_argument("--arms", nargs="+", default=["planner", "mc", "vleaf"])
    ap.add_argument("--model")
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--worker", type=int, help=argparse.SUPPRESS)
    ap.add_argument("--limit", type=int, help="only the first N jobs (testing)")
    ap.add_argument("--report", help="print the summary and paired tests of a finished folder")
    ap.add_argument("--baseline", default="mc", help="arm the others are compared with in --report")
    a = ap.parse_args(argv)
    if a.report:
        recs = load(a.report)
        man = json.loads((Path(a.report) / "manifest.json").read_text()) if (Path(a.report) / "manifest.json").exists() else {}
        arms = man.get("arms") or sorted({n for r in recs for n in r["arms"]})
        res = {"summary": summarize(recs, arms), "paired_vs_" + a.baseline: {n: paired(recs, a.baseline, n) for n in arms if n != a.baseline}}
        print(json.dumps(res, indent=1))
        return 0
    if a.worker is not None:
        return worker(a)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(out / "claims", ignore_errors=True)
    (out / "claims").mkdir()
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT, capture_output=True, text=True).stdout.strip()
    t0 = time.time()
    procs = [subprocess.Popen([sys.executable, "-I", __file__, "--worker", str(w), "--out", str(out), "--seeds", str(a.seeds), "--arms", *a.arms]
                              + (["--limit", str(a.limit)] if a.limit else [])
                              + (["--model", a.model] if a.model else [])) for w in range(a.workers)]
    codes = [p.wait() for p in procs]
    info = Path.home() / "Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app/Contents/Resources/release_info.json"
    build = json.loads(info.read_text()) if info.exists() else {}
    recs = load(out)
    manifest = {"name": out.name, "created": time.strftime("%Y-%m-%d %H:%M"), "benchmark": str(BENCH.relative_to(PROJECT)),
                "game_version": build.get("version"), "game_commit": build.get("commit"), "code_commit": head, "arms": a.arms,
                "model": a.model, "seeds": a.seeds, "seed_base": SEED_BASE, "workers": a.workers, "worker_exit_codes": codes,
                "wall_seconds": round(time.time() - t0), "jobs": len(recs), "summary": summarize(recs, a.arms)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(json.dumps(manifest["summary"], indent=1))
    return 0 if all(c == 0 for c in codes) else 1


if __name__ == "__main__":
    sys.exit(main())
