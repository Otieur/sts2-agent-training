#!/usr/bin/env python3
"""Fight situations from simulated whole runs (P9.E3.S2: self-play from realistic run states, not only the history).

Whole runs are played in the simulator from new seeds. Card rewards are taken with the draft scorer
(`tools/draft.py score_offer`, skipping below its bar), everything else with the simple run policy of `tools/sim.py`.
At the start of every fight the situation is recorded as a fight spec in the format of `tools/fight_specs.py`:
encounter, act, floor, room type, ascension, deck, relics, potions, HP and max HP.

With `--test-hp` (default on) runs get a large max HP so that they reach acts 2 and 3 and their bosses (the planner
alone rarely survives act 1); the recorded HP is then re-drawn: max HP is 80 plus whatever relics added, and current HP
is 45-100% of it. The deck, relics, potions and encounters are the run's own.

    python3 -I tools/run_specs.py --runs 40 --workers 2 --out data/learn/specs/run-specs-ironclad.json

The source of each spec is `sim-<seed>`; training puts every `sim-` source in the training split, so the held-out
test split stays the Player's history runs only.
"""
import argparse
import json
import random
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "tools"))
import plan_turn as pt  # noqa: E402
import sim as S  # noqa: E402

TEST_HP = 2000
BASE_MAX_HP = 80


def draft_policy(obs, acts, rng):
    """Card rewards by the draft scorer; everything else by the simple run policy."""
    if obs.get("screen") == "choice" and (obs.get("choice") or {}).get("kind") == "CardReward":
        import draft
        ch = obs["choice"]
        picks = [x for x in acts if x.get("type") == "choose" and x.get("cards")]
        offers = [(x, str(x.get("card_id", ""))) for x in picks if not str(x.get("card_id", "")).startswith("alt:")]
        if offers:
            deck = [c.rstrip("+") for c in obs["player"]["deck"]]
            res = draft.score_offer(deck, [cid.rstrip("+") for _, cid in offers], "IRONCLAD", obs.get("act"), obs.get("floor"), None)
            if res["pick"]:
                return next(x for x, cid in offers if cid.rstrip("+") == res["pick"]["id"])
            skip = [x for x in acts if x.get("type") == "choose" and not x.get("cards")]
            if skip:
                return skip[0]
    return S.run_policy(pt, obs, acts, rng)


def play_run(sim, seed, ascension, rng, room_types, test_hp, max_steps=4000):
    spec = {"seed": seed, "character": "IRONCLAD", "ascension": ascension}
    if test_hp:
        spec["test_max_hp"] = TEST_HP
    obs = sim.call(cmd="new_run", spec=spec, timeout=120)["obs"]
    specs, seen = [], set()
    for _ in range(max_steps):
        scr = obs["screen"]
        if scr == "game_over":
            break
        if scr == "combat" and obs.get("encounter") and (obs["act"], obs["floor"]) not in seen and obs.get("turn") == 1:
            seen.add((obs["act"], obs["floor"]))
            p = obs["player"]
            mx = BASE_MAX_HP + (p["max_hp"] - TEST_HP if test_hp else 0) if test_hp else p["max_hp"]
            hp = max(1, int(round(mx * rng.uniform(0.45, 1.0)))) if test_hp else p["hp"]
            specs.append({"source": {"run": f"sim-{seed}", "floor": obs["floor"], "build": "simulated", "run_won": None},
                          "act": obs["act"], "room": room_types.get(obs["encounter"], "Monster"), "encounter": obs["encounter"],
                          "ascension": ascension, "character": "IRONCLAD", "deck": list(p["deck"]), "relics": list(p["relics"]),
                          "potions": [x for x in p["potions"] if x], "hp": hp, "max_hp": mx, "valid": True})
        acts = sim.call(cmd="run_legal")["actions"]
        if not acts:
            break
        try:
            obs = sim.call(cmd="run_step", action=draft_policy(obs, acts, rng), timeout=120)["obs"]
        except S.SimError:
            break
    return specs, obs


def worker(a):
    out = []
    rng = random.Random(a.seed * 1000 + a.worker)
    with S.Sim() as sim:
        room_types = {e["id"]: e["room_type"] for e in sim.encounters()}
        for k in range(a.worker, a.runs, a.workers):
            seed = f"RSPEC{a.seed:02d}{k:05d}"
            asc = rng.randint(0, 10)
            t0 = time.time()
            try:
                specs, end = play_run(sim, seed, asc, rng, room_types, a.test_hp)
            except S.SimError as e:
                print(f"w{a.worker} {seed}: error {str(e)[:120]}", flush=True)
                continue
            out.extend(specs)
            print(f"w{a.worker} {seed} A{asc}: {len(specs)} fights, ended act {end.get('act')} floor {end.get('floor')} ({time.time() - t0:.0f} s)", flush=True)
            Path(a.out + f".part{a.worker}").write_text(json.dumps(out))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=int, default=40)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default=str(PROJECT / "data" / "learn" / "specs" / "run-specs-ironclad.json"))
    ap.add_argument("--no-test-hp", dest="test_hp", action="store_false")
    ap.add_argument("--worker", type=int, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.worker is not None:
        return worker(a)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    procs = [subprocess.Popen([sys.executable, "-I", __file__, "--worker", str(w), "--workers", str(a.workers), "--runs", str(a.runs),
                               "--seed", str(a.seed), "--out", a.out] + ([] if a.test_hp else ["--no-test-hp"])) for w in range(a.workers)]
    codes = [p.wait() for p in procs]
    specs = []
    for w in range(a.workers):
        part = Path(a.out + f".part{w}")
        if part.exists():
            specs.extend(json.loads(part.read_text()))
            part.unlink()
    about = {"source": "simulated whole runs (tools/run_specs.py)", "created": time.strftime("%Y-%m-%d %H:%M"), "runs": a.runs,
             "seed": a.seed, "test_hp": a.test_hp, "drafting": "tools/draft.py score_offer (skip below its bar); other screens tools/sim.py run_policy",
             "hp": "45-100% of 80 plus relic gains" if a.test_hp else "as played", "fights": len(specs),
             "by_act": {act: sum(1 for s in specs if s["act"] == act) for act in (1, 2, 3)},
             "by_room": {r: sum(1 for s in specs if s["room"] == r) for r in ("Monster", "Elite", "Boss")}, "worker_exit_codes": codes}
    Path(a.out).write_text(json.dumps({"about": about, "specs": specs}, indent=0))
    print(json.dumps(about, indent=1))
    return 0 if all(c == 0 for c in codes) else 1


if __name__ == "__main__":
    sys.exit(main())
