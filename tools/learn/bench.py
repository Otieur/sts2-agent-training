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
- `qpolicy`: the action-value network (`tools/learn/train_q.py`) scores the planner's candidates; no restore at all.
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


def planner_search(sim, obs, d, done, potions=None):
    return [S.planner_action(pt, obs, "balanced", potions)], [None], 0


def mc_search(k, top=2, mode="balanced", potions=None):
    return lambda sim, obs, d, done: SP.scored_search(sim, obs, mode, k, top, d, done, potions)


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


class QPolicy:
    """No host call beyond listing legal actions: the action-value network scores the planner's candidates."""
    def __init__(self, model_path, top=2):
        import torch
        import encode as E
        import model as M
        torch.set_num_threads(1)
        self.torch, self.M = torch, M
        self.model, _ = M.load(model_path)
        self.enc = E.Encoder()
        self.top = top

    def __call__(self, sim, obs, d, done):
        cands = S.search_candidates(sim, pt, obs, self.top)
        if len(cands) == 1 or any(c["type"] == "choose" for c in cands):
            return cands, [None], 0
        cands = cands[:self.M.MAX_CANDS]
        with self.torch.no_grad():
            q = self.model(self.M.collate([self.enc.encode(obs)]) | self.M.collate_actions([cands]))[0, :len(cands)] * 100
        values = q.tolist()
        return cands, values, max(range(len(cands)), key=lambda i: values[i])


def make_arm(name, model_path, q_path=None, room=None):
    """Arms; a trailing `p` (plannerp, mc6p) lets the planner and its rollouts drink potions at the room's price."""
    if name in ("planner", "plannerp"):
        pots = room if name.endswith("p") else None
        return lambda sim, obs, d, done: planner_search(sim, obs, d, done, pots)
    m = re.fullmatch(r"mc(\d*)(p?)", name)
    if m:
        return mc_search(int(m.group(1) or 6), potions=room if m.group(2) else None)
    m = re.fullmatch(r"vleaf(\d*)", name)
    if m:
        return ValueLeaf(model_path, int(m.group(1) or 6))
    if name == "qpolicy":
        return QPolicy(q_path)
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
    arms = {name: make_arm(name, a.model, a.q_model) for name in a.arms if not name.endswith("p")}
    host = SP.Host()
    try:
        for i, s in jobs:
            if (i, s) in done_jobs or not SP.claim(out, i * 100 + s):
                continue
            spec = fights[i]
            seed = SEED_BASE + i * 10 + s
            rec = {"fight": i, "sample": s, "seed": seed, "encounter": spec["encounter"], "room": spec["room"], "act": spec["act"], "arms": {}}
            job_arms = {n: (arms[n] if n in arms else make_arm(n, a.model, a.q_model, spec["room"])) for n in a.arms}
            for name, search in job_arms.items():
                t0 = time.time()
                try:
                    r = SP.play(host, spec, seed, search)
                    o = r["outcome"]
                    used = o.get("potions_used", 0)
                    rec["arms"][name] = {"status": o["status"], "hp": o["hp"], "enemy_hp_left": o["enemy_hp_left"], "value": value_of(o),
                                         "potions_used": used, "value_priced": value_of(o) - S.POTION_PRICE[spec["room"]] * used,
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


def paired(recs, a, b, reps=4000, seed=0, metric="value"):
    rows = [(r["arms"][a][metric], r["arms"][b][metric]) for r in recs
            if metric in r["arms"].get(a, {}) and metric in r["arms"].get(b, {})
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


def markdown_potions(folder):
    """Section 5 of reports/phase8/potions-in-search.md."""
    recs = load(folder)
    man = json.loads((Path(folder) / "manifest.json").read_text())
    arms = man["arms"]
    L = [f"Run `{man['name']}`: {man['jobs']} jobs, {man['workers']} workers, {man['wall_seconds']} s wall, code `{man['code_commit']}`, "
         f"game {man['game_version']} ({man['game_commit']}).", "",
         "| Arm | Won | Mean priced value | Mean value | Potions used (Monster / Elite / Boss) | Search s per decision |", "|---|---|---|---|---|---|"]
    summ = summarize(recs, arms)
    for n in arms:
        ok = [(r, r["arms"][n]) for r in recs if "value" in r["arms"].get(n, {})]
        used = {room: sum(x.get("potions_used") or 0 for r, x in ok if r["room"] == room) for room in ("Monster", "Elite", "Boss")}
        L.append(f"| {n} | {summ[n]['won']} | {sum(x['value_priced'] for _, x in ok) / max(1, len(ok)):.2f} | {summ[n]['mean_value']:.2f} | "
                 f"{used['Monster']} / {used['Elite']} / {used['Boss']} | {summ[n]['search_seconds_per_decision']:.3f} |")
    L += ["", "| Pair (B − A), priced value | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |", "|---|---|---|---|---|---|---|---|"]
    verdict = {}
    for a_, b_ in [("mc6", "mc6p"), ("planner", "plannerp")]:
        t = paired(recs, a_, b_, metric="value_priced")
        verdict[b_] = t
        L.append(f"| {b_} − {a_} | {t['pairs']} | {t['mean_diff']:.2f} | {t['boot95'][0]:.2f} to {t['boot95'][1]:.2f} | {t['better']} | {t['worse']} | {t['equal']} | {t['sign_p_one_sided']:.4f} |")
    L.append("")
    for h, b_ in (("H1", "mc6p"), ("H2", "plannerp")):
        t = verdict[b_]
        L.append(f"- **{h}** (`{b_}` better on priced value, sign test p < 0.025): p = {t['sign_p_one_sided']:.4f}, mean difference {t['mean_diff']:.2f}: "
                 + ("**holds**." if t["sign_p_one_sided"] < 0.025 and t["mean_diff"] > 0 else "**does not hold**."))
    errs = [(r["fight"], r["sample"], n) for r in recs for n, v in r["arms"].items() if "error" in v]
    L.append(f"\nErrors: {len(errs)}.")
    return "\n".join(L)


def markdown_budget(folder, alpha=0.025):
    """Section 5 of reports/phase8/search-budget.md."""
    recs = load(folder)
    man = json.loads((Path(folder) / "manifest.json").read_text())
    arms = man["arms"]
    summ = summarize(recs, arms)
    L = [f"Run `{man['name']}`: {man['jobs']} jobs, {man['workers']} workers, {man['wall_seconds']} s wall, code `{man['code_commit']}`, "
         f"game {man['game_version']} ({man['game_commit']}).", "",
         "| Arm | Games | Errors | Won | Mean value | HP left after wins | Search s per decision |", "|---|---|---|---|---|---|---|"]
    for n in arms:
        x = summ[n]
        L.append(f"| {n} | {x['games']} | {x['errors']} | {x['won']} | {x['mean_value']:.2f} | {x['mean_hp_if_won']:.2f} | {x['search_seconds_per_decision']:.3f} |")
    L += ["", "| Pair (B − A) | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |", "|---|---|---|---|---|---|---|---|"]
    tests = {}
    for a_, b_ in [("mc6", "mc12"), ("mc12", "mc24"), ("mc6", "mc24")]:
        if a_ in arms and b_ in arms:
            t = tests[(a_, b_)] = paired(recs, a_, b_)
            L.append(f"| {b_} − {a_} | {t['pairs']} | {t['mean_diff']:.2f} | {t['boot95'][0]:.2f} to {t['boot95'][1]:.2f} | {t['better']} | {t['worse']} | {t['equal']} | {t['sign_p_one_sided']:.4f} |")
    L.append("")
    for h, key in (("H1", ("mc6", "mc12")), ("H2", ("mc12", "mc24"))):
        if key in tests:
            t = tests[key]
            L.append(f"- **{h}** (`{key[1]}` better than `{key[0]}`, sign test p < {alpha}): p = {t['sign_p_one_sided']:.4f}, mean difference {t['mean_diff']:.2f}: "
                     + ("**holds**." if t["sign_p_one_sided"] < alpha and t["mean_diff"] > 0 else "**does not hold**."))
    errs = [(r["fight"], r["sample"], n) for r in recs for n, v in r["arms"].items() if "error" in v]
    L.append(f"\nErrors: {len(errs)}.")
    return "\n".join(L)


def markdown(folder, alpha=0.025, h4=False):
    """Section 5 of reports/phase9/value-search-comparison.md: summary table, H1-H3 verdicts, paired tests."""
    recs = load(folder)
    man = json.loads((Path(folder) / "manifest.json").read_text())
    arms = man["arms"]
    summ = summarize(recs, arms)
    L = [f"Run `{man['name']}`: {man['jobs']} jobs, {man['workers']} workers, {man['wall_seconds']} s wall, code `{man['code_commit']}`, "
         f"game {man['game_version']} ({man['game_commit']}), model `{man['model']}`" + (f", action-value model `{man['q_model']}`" if man.get("q_model") else "") + ".", "",
         "| Arm | Games | Errors | Won | Mean value | HP left after wins | Search s per decision | Host restarts |", "|---|---|---|---|---|---|---|---|"]
    for n in arms:
        x = summ[n]
        L.append(f"| {n} | {x['games']} | {x['errors']} | {x['won']} | {x['mean_value']:.2f} | {x['mean_hp_if_won']:.2f} | {x['search_seconds_per_decision']:.3f} | {x['restarts']} |")
    L += ["", "| Pair (B − A) | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |", "|---|---|---|---|---|---|---|---|"]
    tests = {}
    for a_, b_ in [("mc6", "vleaf6"), ("mc6", "vleaf2"), ("planner", "vgreedy"), ("planner", "mc6"), ("mc6", "vgreedy"), ("planner", "qpolicy"), ("mc6", "qpolicy")]:
        if a_ in arms and b_ in arms:
            t = paired(recs, a_, b_)
            tests[(a_, b_)] = t
            L.append(f"| {b_} − {a_} | {t['pairs']} | {t['mean_diff']:.2f} | {t['boot95'][0]:.2f} to {t['boot95'][1]:.2f} | {t['better']} | {t['worse']} | {t['equal']} | {t['sign_p_one_sided']:.4f} |")
    L.append("")
    if ("mc6", "vleaf6") in tests:
        t = tests[("mc6", "vleaf6")]
        L.append(f"- **H1** (`vleaf6` better than `mc6`, sign test p < {alpha}): p = {t['sign_p_one_sided']:.4f}, mean difference {t['mean_diff']:.2f}: "
                 + ("**holds**." if t["sign_p_one_sided"] < alpha and t["mean_diff"] > 0 else "**does not hold**."))
    if ("mc6", "vleaf2") in tests:
        t = tests[("mc6", "vleaf2")]
        ratio = summ["vleaf2"]["search_seconds_per_decision"] / max(summ["mc6"]["search_seconds_per_decision"], 1e-9)
        ok = t["boot95"][0] > -5 and ratio <= 0.4
        L.append(f"- **H2** (`vleaf2` not worse than `mc6` by more than 5, lower bound > −5, time ratio ≤ 0.4): lower bound {t['boot95'][0]:.2f}, "
                 f"time ratio {ratio:.2f}: " + ("**holds**." if ok else "**does not hold**."))
    if ("planner", "vgreedy") in tests:
        t = tests[("planner", "vgreedy")]
        L.append(f"- **H3** (`vgreedy` better than `planner`, sign test p < {alpha}): p = {t['sign_p_one_sided']:.4f}, mean difference {t['mean_diff']:.2f}: "
                 + ("**holds**." if t["sign_p_one_sided"] < alpha and t["mean_diff"] > 0 else "**does not hold**."))
    if h4 and ("planner", "qpolicy") in tests:
        t = tests[("planner", "qpolicy")]
        L.append(f"- **H4** (`qpolicy` better than `planner`, sign test p < {alpha}): p = {t['sign_p_one_sided']:.4f}, mean difference {t['mean_diff']:.2f}: "
                 + ("**holds**." if t["sign_p_one_sided"] < alpha and t["mean_diff"] > 0 else "**does not hold**."))
    errs = [(r["fight"], r["sample"], n, v["error"][:120]) for r in recs for n, v in r["arms"].items() if "error" in v]
    blocked = [(r["fight"], r["sample"], n) for r in recs for n, v in r["arms"].items() if v.get("blocked")]
    L += ["", f"Jobs left out of pairs: {len(errs)} errors, {len(blocked)} blocked." + ("" if not errs else " " + "; ".join(f"fight {f} sample {s_} {n}: {e}" for f, s_, n, e in errs[:10]))]
    by_room = {}
    for r in recs:
        for n in arms:
            v = r["arms"].get(n, {})
            if "value" in v:
                by_room.setdefault((r["room"], n), []).append(v["value"])
    L += ["", "Mean value by room type: " + "; ".join(f"{room} " + ", ".join(f"{n} {sum(by_room.get((room, n), [0])) / max(1, len(by_room.get((room, n), []))):.1f}" for n in arms)
                                               for room in ("Monster", "Elite", "Boss"))]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out")
    ap.add_argument("--arms", nargs="+", default=["planner", "mc", "vleaf"])
    ap.add_argument("--model")
    ap.add_argument("--q-model", help="action-value network for the qpolicy arm")
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--worker", type=int, help=argparse.SUPPRESS)
    ap.add_argument("--limit", type=int, help="only the first N jobs (testing)")
    ap.add_argument("--report", help="print the summary and paired tests of a finished folder")
    ap.add_argument("--baseline", default="mc", help="arm the others are compared with in --report")
    ap.add_argument("--alpha", type=float, default=0.025, help="one-sided significance per directional hypothesis in --markdown")
    ap.add_argument("--h4", action="store_true", help="--markdown also judges H4 (qpolicy better than planner)")
    ap.add_argument("--markdown", action="store_true", help="with --report: the results section of the value-search comparison")
    a = ap.parse_args(argv)
    if a.report and a.markdown:
        man = json.loads((Path(a.report) / "manifest.json").read_text())
        if any(n.endswith("p") for n in man["arms"]):
            print(markdown_potions(a.report))
        elif all(re.fullmatch(r"mc\d+", n) for n in man["arms"]):
            print(markdown_budget(a.report, a.alpha))
        else:
            print(markdown(a.report, a.alpha, a.h4))
        return 0
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
                              + (["--model", a.model] if a.model else []) + (["--q-model", a.q_model] if a.q_model else [])) for w in range(a.workers)]
    codes = [p.wait() for p in procs]
    info = Path.home() / "Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app/Contents/Resources/release_info.json"
    build = json.loads(info.read_text()) if info.exists() else {}
    recs = load(out)
    manifest = {"name": out.name, "created": time.strftime("%Y-%m-%d %H:%M"), "benchmark": str(BENCH.relative_to(PROJECT)),
                "game_version": build.get("version"), "game_commit": build.get("commit"), "code_commit": head, "arms": a.arms,
                "model": a.model, "q_model": a.q_model, "seeds": a.seeds, "seed_base": SEED_BASE, "workers": a.workers, "worker_exit_codes": codes,
                "wall_seconds": round(time.time() - t0), "jobs": len(recs), "summary": summarize(recs, a.arms)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(json.dumps(manifest["summary"], indent=1))
    return 0 if all(c == 0 for c in codes) else 1


if __name__ == "__main__":
    sys.exit(main())
