#!/usr/bin/env python3
"""Run-level benchmark for deck-building policies (P9.E4): whole runs in the simulator from fixed seeds, the same
combat policy throughout, only the strategic decisions changed. Policies meet the same seeds (paired).

    python3 -I tools/run_bench.py --out data/learn/runs/draft-1 --policies base draft --seeds 60 --ascension 0
    python3 -I tools/run_bench.py --report data/learn/runs/draft-1

A policy is a `+`-joined list of components; anything not named keeps the simple run policy of `tools/sim.py`
(first card of each reward, leave shops, rest below 60% HP else smith the first card, first map move):
- `base`: the simple run policy alone.
- `draft`: card rewards by the draft scorer (`tools/draft.py score_offer`, skipping below its bar).
- `shop`: in shops, buy the card removal first (curses, then Strikes, then Defends), then the best card the draft
  scorer would take if gold allows.
- `rest`: heal below 50% HP (below 70% before a boss), otherwise smith; the upgrade goes to the first card in an
  upgrade priority list (Bash, then the deck's highest-tier cards by the draft scorer's tiers, Strikes and Defends last).

Combat is played by the rule planner (fast; run-level states cannot be cloned for search yet, FP-16). Every decision
uses only the observation; the seed's future (map, offers, encounters) is never read (FP-1).

Metrics per run: floor reached, act reached, act bosses beaten, won. Primary: floor reached, paired by seed.
"""
import argparse
import json
import math
import random
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "tools"))
import plan_turn as pt  # noqa: E402
import sim as S  # noqa: E402

REMOVE_ORDER = ["CURSE", "STRIKE_IRONCLAD", "DEFEND_IRONCLAD"]


def is_curse(card_id):
    import draft
    c = draft.dm.CARDS.get(card_id.rstrip("+"))
    return bool(c) and c.get("type") == "Curse"


def draft_pick(obs, acts):
    import draft
    picks = [x for x in acts if x.get("type") == "choose" and x.get("cards")]
    offers = [(x, str(x.get("card_id", ""))) for x in picks if not str(x.get("card_id", "")).startswith("alt:")]
    if not offers:
        return None
    deck = [c.rstrip("+") for c in obs["player"]["deck"]]
    res = draft.score_offer(deck, [cid.rstrip("+") for _, cid in offers], "IRONCLAD", obs.get("act"), obs.get("floor"), None)
    if res["pick"]:
        return next(x for x, cid in offers if cid.rstrip("+") == res["pick"]["id"])
    skip = [x for x in acts if x.get("type") == "choose" and not x.get("cards")]
    return skip[0] if skip else None


class Policy:
    def __init__(self, name):
        self.name = name
        self.parts = set(name.split("+")) - {"base"}
        self.pending = None           # what a choice screen opened by our own action is for
        self.bought = set()

    def act(self, obs, acts, rng):
        scr = obs["screen"]
        ch = obs.get("choice") or {}
        if scr == "choice" and ch.get("kind") == "CardReward" and "draft" in self.parts:
            a = draft_pick(obs, acts)
            if a is not None:
                return a
        if scr == "choice" and ch.get("kind") == "FromDeckForRemoval" and "shop" in self.parts:
            opts = ch.get("options") or []
            for want in REMOVE_ORDER:
                for i, cid in enumerate(opts):
                    if (want == "CURSE" and is_curse(cid)) or cid.rstrip("+") == want:
                        a = next((x for x in acts if x.get("cards") == [i]), None)
                        if a:
                            return a
        if scr == "choice" and ch.get("kind", "").startswith("FromDeckForUpgrade") and "rest" in self.parts:
            a = self.upgrade_pick(obs, ch, acts)
            if a:
                return a
        if scr == "shop" and "shop" in self.parts:
            a = self.shop_pick(obs, acts)
            if a:
                return a
        if scr == "rest" and "rest" in self.parts:
            hp, mx = obs["player"]["hp"], obs["player"]["max_hp"]
            boss_next = obs.get("act_floor", 0) >= 15
            want = "HEAL" if hp < (0.7 if boss_next else 0.5) * mx else "SMITH"
            for x in acts:
                if str(x.get("option", "")).upper() == want:
                    return x
        return S.run_policy(pt, obs, acts, rng)

    def shop_pick(self, obs, acts):
        gold = obs["player"]["gold"]
        key = (obs.get("act"), obs.get("floor"))
        removal = [x for x in acts if x.get("type") == "buy" and "remov" in str(x.get("item", "")).lower() and x.get("cost", 1e9) <= gold]
        if removal and (key, "remove") not in self.bought:
            self.bought.add((key, "remove"))
            return removal[0]
        cards = [x for x in acts if x.get("type") == "buy" and str(x.get("item", "")).startswith("card:") and x.get("cost", 1e9) <= gold]
        if cards and (key, "card") not in self.bought:
            import draft
            deck = [c.rstrip("+") for c in obs["player"]["deck"]]
            ids = [x["item"].split(":", 1)[1] for x in cards]
            res = draft.score_offer(deck, ids, "IRONCLAD", obs.get("act"), obs.get("floor"), None)
            self.bought.add((key, "card"))
            if res["pick"]:
                return next(x for x in cards if x["item"].split(":", 1)[1] == res["pick"]["id"])
        return None

    def upgrade_pick(self, obs, ch, acts):
        import draft
        opts = ch.get("options") or []
        tiers = draft.load_tiers("IRONCLAD")
        def rank(cid):
            base = cid.rstrip("+")
            if base == "BASH":
                return 100
            if base in ("STRIKE_IRONCLAD", "DEFEND_IRONCLAD"):
                return -10
            c = draft.dm.CARDS.get(base)
            t = tiers.get(draft.norm(c["name"])) if c else None
            return draft.TIER_SCORE.get(t[0], 0) if t else 0
        order = sorted(range(len(opts)), key=lambda i: -rank(opts[i]))
        for i in order:
            a = next((x for x in acts if x.get("cards") == [i]), None)
            if a:
                return a
        return None


def play_run(sim, seed, ascension, policy, rng, max_steps=6000):
    obs = sim.call(cmd="new_run", spec={"seed": seed, "character": "IRONCLAD", "ascension": ascension}, timeout=120)["obs"]
    bosses, steps, last_act = 0, 0, 1
    for steps in range(max_steps):
        if obs["screen"] == "game_over":
            break
        acts = sim.call(cmd="run_legal")["actions"]
        if not acts:
            break
        try:
            obs = sim.call(cmd="run_step", action=policy.act(obs, acts, rng), timeout=120)["obs"]
        except S.SimError:
            break
        if obs.get("act", 1) > last_act:
            bosses += obs["act"] - last_act
            last_act = obs["act"]
    won = obs["screen"] == "game_over" and obs["player"]["hp"] > 0
    return {"floor": obs.get("floor"), "act": obs.get("act"), "bosses": bosses + (1 if won else 0), "won": won, "steps": steps,
            "deck": len(obs["player"]["deck"]), "gold": obs["player"].get("gold")}


def worker(a):
    out = Path(a.out)
    with S.Sim() as sim:
        for k in range(a.worker, a.seeds, a.workers):
            seed = f"RB{a.seed_base:03d}{k:05d}"
            rec = {"seed": seed, "ascension": a.ascension, "policies": {}}
            for name in a.policies:
                t0 = time.time()
                try:
                    r = play_run(sim, seed, a.ascension, Policy(name), random.Random(k))
                except S.SimError as e:
                    r = {"error": str(e)[:200]}
                r["seconds"] = round(time.time() - t0, 1)
                rec["policies"][name] = r
            with (out / f"shard-{a.worker:02d}.jsonl").open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(f"w{a.worker} {seed}: " + ", ".join(f"{n} floor {v.get('floor')}{' WON' if v.get('won') else ''}" for n, v in rec["policies"].items()), flush=True)
    return 0


def sign_p(better, worse):
    n = better + worse
    return sum(math.comb(n, i) for i in range(better, n + 1)) / 2 ** n if n else 1.0


def report(folder, baseline):
    recs = [json.loads(l) for f in sorted(Path(folder).glob("shard-*.jsonl")) for l in f.open()]
    names = list(recs[0]["policies"]) if recs else []
    out = {"runs": len(recs), "policies": {}}
    for n in names:
        rs = [r["policies"][n] for r in recs if "floor" in r["policies"][n]]
        out["policies"][n] = {"runs": len(rs), "mean_floor": round(sum(x["floor"] for x in rs) / max(len(rs), 1), 2),
                              "act1_boss": sum(1 for x in rs if x["bosses"] >= 1), "act2_boss": sum(1 for x in rs if x["bosses"] >= 2),
                              "won": sum(1 for x in rs if x["won"])}
    for n in names:
        if n == baseline:
            continue
        d = [r["policies"][n]["floor"] - r["policies"][baseline]["floor"] for r in recs
             if "floor" in r["policies"][n] and "floor" in r["policies"][baseline]]
        b, w = sum(1 for x in d if x > 0), sum(1 for x in d if x < 0)
        rng = random.Random(0)
        boots = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(4000)) if d else [0]
        out["policies"][n]["vs_" + baseline] = {"pairs": len(d), "mean_floor_diff": round(sum(d) / max(len(d), 1), 2), "better": b, "worse": w,
                                                "equal": len(d) - b - w, "sign_p_one_sided": sign_p(b, w), "boot95": [boots[100], boots[3899]]}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out")
    ap.add_argument("--policies", nargs="+", default=["base", "draft"])
    ap.add_argument("--seeds", type=int, default=60)
    ap.add_argument("--seed-base", type=int, default=1)
    ap.add_argument("--ascension", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--worker", type=int, help=argparse.SUPPRESS)
    ap.add_argument("--report")
    ap.add_argument("--baseline", default="base")
    a = ap.parse_args(argv)
    if a.report:
        print(json.dumps(report(a.report, a.baseline), indent=1))
        return 0
    if a.worker is not None:
        return worker(a)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    procs = [subprocess.Popen([sys.executable, "-I", __file__, "--worker", str(w), "--workers", str(a.workers), "--seeds", str(a.seeds),
                               "--seed-base", str(a.seed_base), "--ascension", str(a.ascension), "--out", str(out), "--policies", *a.policies])
             for w in range(a.workers)]
    codes = [p.wait() for p in procs]
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT, capture_output=True, text=True).stdout.strip()
    man = {"name": out.name, "created": time.strftime("%Y-%m-%d %H:%M"), "code_commit": head, "policies": a.policies, "seeds": a.seeds,
           "seed_base": a.seed_base, "ascension": a.ascension, "combat": "rule planner", "worker_exit_codes": codes,
           "wall_seconds": round(time.time() - t0), "report": report(out, a.baseline)}
    (out / "manifest.json").write_text(json.dumps(man, indent=1))
    print(json.dumps(man["report"], indent=1))
    return 0 if all(c == 0 for c in codes) else 1


if __name__ == "__main__":
    sys.exit(main())
