#!/usr/bin/env python3
"""Self-play data for the combat models (P9.E1.S2): fights in the simulator with the search policy as the teacher.

Each fight comes from a generated spec (act, room type, encounter, ascension, deck, HP) and is played by flat Monte
Carlo search over the rule planner's candidate actions (`tools/sim.py search_action`, with the values of every
candidate kept). Every decision is recorded with the observation, the candidates, their sampled values and the chosen
action; the fight's outcome is added when it ends. Several host processes run in parallel and take fights from a shared
list (claim files), so a slow worker does not hold up the batch; a stopped batch resumes where it left off (records of
fights that failed are dropped and replayed). A rollout that gets stuck on a prompt the host does not handle leaves the
host unable to restore, so the worker restarts the host, replays the fight to the current decision (checked against the
recorded state) and skips that rollout; such events are logged in `stuck-<worker>.jsonl`.

    python3 -I tools/selfplay.py --workers 6 --fights 120 --out data/learn/combat-v1
    python3 -I tools/selfplay.py --summary data/learn/combat-v1

Output (ignored by git except the manifest): `shard-<worker>.jsonl`, one fight per line, and `manifest.json` (game
build, host commit, fidelity result, teacher settings, spec generator, seeds, counts). Decisions use only what the
player can see: search restores the past and re-samples the hidden future (FP-15); the teacher is not privileged.

Generated specs are synthetic (spec generator v1, recorded in the manifest): the starting deck plus cards drawn from
the character's card pool by rarity, more cards, more upgrades and a few Strikes removed in later acts; HP 40–100% of
80; the starting relic only; no potions; ascension 0–10; encounters from the act's pools (encounters outside the
default act list belong to the other act 1 and count as act 1).
"""
import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "tools"))
import plan_turn as pt  # noqa: E402
import sim as S  # noqa: E402

SPEC_VERSION = "v1"
STARTER = {"IRONCLAD": ["STRIKE_IRONCLAD"] * 5 + ["DEFEND_IRONCLAD"] * 4 + ["BASH"]}
RARITY_WEIGHT = {"Common": 0.55, "Uncommon": 0.35, "Rare": 0.10}
ADDED = {1: (2, 6), 2: (6, 11), 3: (10, 16)}
UPGRADED = {1: 0.10, 2: 0.30, 3: 0.50}
REMOVED = {1: (0, 0), 2: (0, 2), 3: (1, 3)}


def make_spec(rng, encounters, pool, character="IRONCLAD"):
    act = rng.choices([1, 2, 3], weights=[0.4, 0.35, 0.25])[0]
    room = rng.choices(["Monster", "Elite", "Boss"], weights=[0.7, 0.2, 0.1])[0]
    cands = [e["id"] for e in encounters if e["room_type"] == room and not e["weak"] and (act in e["acts"] or (not e["acts"] and act == 1))]
    deck = list(STARTER[character])
    for _ in range(rng.randint(*REMOVED[act])):
        if "STRIKE_IRONCLAD" in deck:
            deck.remove("STRIKE_IRONCLAD")
    draws = [c for c in pool if c["rarity"] in RARITY_WEIGHT]
    weights = [RARITY_WEIGHT[c["rarity"]] for c in draws]
    deck += [c["id"] for c in rng.choices(draws, weights=weights, k=rng.randint(*ADDED[act]))]
    deck = [c + "+" if rng.random() < UPGRADED[act] else c for c in deck]
    return {"act": act, "room": room, "encounter": rng.choice(cands), "ascension": rng.randint(0, 10), "deck": deck,
            "hp": int(80 * rng.uniform(0.4, 1.0)), "character": character}


class Tainted(Exception):
    """A rollout got stuck on a prompt the host does not handle (`blocked`). The host cannot restore after that (the
    stuck game action keeps the action executor busy), so the worker restarts the host and replays the fight."""


class Host:
    """A simulator host that can be replaced after it gets stuck."""
    def __init__(self):
        self.sim = S.Sim()
        self.restarts = 0

    def restart(self):
        try:
            self.sim.close()
        except Exception:
            pass
        self.sim = S.Sim()
        self.restarts += 1

    def close(self):
        self.sim.close()


AUGMENT_VERSION = "a1"


def augment(spec, rng, pool):
    """A variant of a history spec (augmentation a1), so that a network sees many decks and relic sets per source run
    instead of memorizing about thirty: remove 0-3 random cards (deck kept at 8 or more), add 0-3 cards drawn from the
    character's pool by rarity (upgraded with probability 0.3), drop each relic but the first (the starting relic) with
    probability 0.25 and each potion with probability 0.3, scale HP by 0.75-1.15 (at least 1, at most max HP). The source
    is kept, so splits by source run and the benchmark exclusion still hold."""
    s = json.loads(json.dumps(spec))
    deck = list(s["deck"])
    for _ in range(rng.randint(0, 3)):
        if len(deck) > 8:
            deck.pop(rng.randrange(len(deck)))
    draws = [c for c in pool if c["rarity"] in RARITY_WEIGHT]
    added = [c["id"] + ("+" if rng.random() < 0.3 else "") for c in rng.choices(draws, weights=[RARITY_WEIGHT[c["rarity"]] for c in draws], k=rng.randint(0, 3))]
    s["deck"] = deck + added
    relics = s.get("relics") or []
    s["relics"] = relics[:1] + [r for r in relics[1:] if rng.random() >= 0.25]
    s["potions"] = [p for p in (s.get("potions") or []) if rng.random() >= 0.3]
    mx = s.get("max_hp") or 80
    s["hp"] = max(1, min(mx, int(round((s.get("hp") or mx) * rng.uniform(0.75, 1.15)))))
    s["augmented"] = {"version": AUGMENT_VERSION, "added": added, "deck_size_before": len(spec["deck"])}
    return s


# The end of a turn checked against the rule planner (boss replay 3, `reports/phase9/boss-replay-3.md`). In a fight
# whose rollouts are all lost a candidate's value is the enemies' HP left at death, and its mean over six sampled
# worlds moves by tens of points, more than a card is worth: on the Agent's 22 traced Test Subject fights 62 of 199
# turns were ended with a playable card in hand that the energy left pays for, by a median margin of 23 points. With the check on, ending
# the turn is taken over the planner's next card only where the search is clear about it: the mean of the per-world
# differences (the two candidates share their sample seeds) has to exceed END_TURN_Z of its standard errors. Inside
# that noise the planner's card is played, and the next decision is searched as before. The check is asked only where
# a sampled world of either candidate was lost: where every world of both is won the values are HP left, which six
# worlds tell apart, and the search's choice stands as before. Off unless a search arm or the environment switches it
# on (`SIM_END_TURN_Z=2`); `0` or unset is off.
END_TURN_Z = float(os.environ.get("SIM_END_TURN_Z") or 0) or None
END_CHECKS = {"asked": 0, "kept": 0, "played": 0, "absent": 0}     # since the caller last cleared them
LOST_AT_MOST = -100.0      # tools/sim.py _value: a lost rollout is -100 minus the enemies' HP left, a won one the HP left


def _same_play(a, b, hand):
    """The same card play: the same hand index, or two copies of one card (id and upgrade), at the same target."""
    if a.get("type") != "play" or b.get("type") != "play" or a.get("target") != b.get("target"):
        return False
    if a.get("card") == b.get("card"):
        return True
    ia, ib = a.get("card"), b.get("card")
    if not (isinstance(ia, int) and isinstance(ib, int) and ia < len(hand) and ib < len(hand)):
        return False
    return (hand[ia].get("card_id"), hand[ia].get("upgraded")) == (hand[ib].get("card_id"), hand[ib].get("upgraded"))


def end_turn_checked(cands, done, k, best, planned, hand, z, counts=None):
    """The candidate to take when the search's best is ending the turn and the planner would play a card (`planned`,
    its next action without potions): the planner's card, unless ending the turn beats it by more than `z` standard
    errors of the per-world difference. Unchanged when the best is not ending the turn, when the planner would end it
    too or its card is not a candidate, when every world of both was won, and when fewer than three worlds scored both."""
    counts = END_CHECKS if counts is None else counts
    if z is None or cands[best].get("type") != "end_turn" or not planned or planned.get("type") != "play":
        return best
    pi = next((i for i, c in enumerate(cands) if _same_play(c, planned, hand)), None)
    scored = [done[(ci, j)] for ci in (best,) + (() if pi is None else (pi,)) for j in range(k) if done.get((ci, j)) is not None]
    if not any(v <= LOST_AT_MOST for v in scored):
        return best
    counts["asked"] += 1
    if pi is None:
        counts["absent"] += 1
        return best
    diffs = [done[(best, j)] - done[(pi, j)] for j in range(k) if done.get((best, j)) is not None and done.get((pi, j)) is not None]
    if len(diffs) < 3:
        counts["kept"] += 1
        return best
    mean = sum(diffs) / len(diffs)
    se = (sum((x - mean) ** 2 for x in diffs) / (len(diffs) - 1) / len(diffs)) ** 0.5
    if mean > z * se:
        counts["kept"] += 1
        return best
    counts["played"] += 1
    return pi


def scored_search(sim, obs, mode, k, top, decision, done=None, potions=None, wide=False, cand_fn=None, all_potions=False):
    """search_action with every candidate's mean value kept (the teacher's distribution). `done` maps (candidate,
    sample) to a value already computed, or None for a rollout that got stuck; it survives a host restart, so the search
    resumes where it stopped and skips the stuck rollout. Stuck rollouts are left out of the means."""
    done = {} if done is None else done
    cands = (cand_fn(sim, obs) if cand_fn else
             S.search_candidates_wide(sim, pt, obs, top, potions=potions, all_potions=all_potions) if wide else S.search_candidates(sim, pt, obs, top, potions))
    if len(cands) == 1:
        return cands, [None], 0
    held = S.potions_held(obs)
    price = S.POTION_PRICE[potions] if potions else 0.0
    snap = sim.call(cmd="snapshot")["id"]
    for ci, a in enumerate(cands):
        for j in range(k):
            if (ci, j) in done:
                continue
            if sim.call(cmd="restore", id=snap)["obs"]["status"] != "in_progress":
                raise Tainted("restore did not give back the decision state")
            sim.call(cmd="resample", sample_seed=1_000_003 * (decision + 1) + j)
            try:
                o = sim.step(S.choice_in(sim.observe(), obs, a) if a.get("type") == "choose" else a)
            except S.SimError:
                done[(ci, j)] = -1000.0
                continue
            f = S._finish_with_planner(sim, pt, o, mode, potions=potions)
            if f["status"] == "in_progress":
                done[(ci, j)] = None
                raise Tainted(f"rollout stuck (candidate {ci}, sample {j}, blocked {bool(f.get('blocked'))})")
            done[(ci, j)] = float(S._value(f, max(0, held - S.potions_held(f)), price))
    if sim.call(cmd="restore", id=snap)["obs"]["status"] != "in_progress":
        raise Tainted("restore did not give back the decision state")
    values = []
    for ci in range(len(cands)):
        vals = [done[(ci, j)] for j in range(k) if done.get((ci, j)) is not None]
        values.append(sum(vals) / len(vals) if vals else -1000.0)
    best = max(range(len(cands)), key=lambda i: values[i])
    if END_TURN_Z is not None and cands[best].get("type") == "end_turn" and not obs.get("choice"):
        best = end_turn_checked(cands, done, k, best, S.planner_action(pt, obs, mode), (obs.get("combat") or {}).get("hand") or [], END_TURN_Z)
    return cands, values, best


def start_fight(sim, spec, seed):
    req = {k2: spec[k2] for k2 in ("encounter", "character", "ascension", "deck", "relics", "potions", "hp", "max_hp") if spec.get(k2) is not None}
    req["seed"] = f"SELF{seed:08d}"
    if "source" in spec:
        req["relic_pickup"] = False          # situations from a recorded run already include the pickup effects
    return sim.call(cmd="new_fight", spec=req, sample_seed=seed + 1, timeout=120)["obs"]


def _same_state(a, b):
    def key(o):
        c = o["combat"]
        return ([h["card_id"] for h in c["hand"]], c["player"]["current_hp"], c["player"]["energy"], [e["current_hp"] for e in c["enemies"]], o.get("turn"))
    return key(a) == key(b)


def play_fight(host, spec, seed, k, top, mode, stuck_log=None, max_restarts=3):
    """One fight played by the flat Monte Carlo teacher (see `play`)."""
    return play(host, spec, seed, lambda sim, obs, d, done: scored_search(sim, obs, mode, k, top, d, done), stuck_log, max_restarts)


def play(host, spec, seed, search, stuck_log=None, max_restarts=3):
    """One fight; `search(sim, obs, decision, done)` returns (candidates, values, best index). After a stuck rollout
    the host is restarted and the fight replayed to the current decision (decision mode is deterministic given the seeds
    and the actions); the replayed state is checked, and `done` keeps the rollouts already scored."""
    obs = start_fight(host.sim, spec, seed)
    if obs["status"] != "in_progress":
        raise S.SimError(f"the fight did not start (status {obs['status']})")
    held_at_start = S.potions_held(obs)
    decisions, applied, d, restarts, stuck = [], [], 0, 0, 0
    done = {}
    t_search = 0.0
    while obs["status"] == "in_progress" and not obs.get("blocked") and d < 300:
        t0 = time.time()
        try:
            cands, values, best = search(host.sim, obs, d, done)
        except Tainted as e:
            stuck += 1
            restarts += 1
            if stuck_log:
                stuck_log({"seed": seed, "decision": d, "reason": str(e), "spec": spec.get("source") or spec.get("encounter")})
            if restarts > max_restarts:
                raise S.SimError(f"too many host restarts ({e})")
            host.restart()
            o2 = start_fight(host.sim, spec, seed)
            for a in applied:
                o2 = host.sim.step(a)
            if not _same_state(o2, obs):
                raise S.SimError("replay after a host restart did not reproduce the decision state")
            obs = o2
            continue
        t_search += time.time() - t0
        chosen = best if values[0] is not None else 0
        decisions.append({"obs": obs, "candidates": cands, "values": values, "chosen": chosen})
        try:
            obs = host.sim.step(cands[chosen])
            applied.append(cands[chosen])
        except S.SimError:
            obs = host.sim.step({"type": "end_turn"})
            applied.append({"type": "end_turn"})
        d += 1
        done = {}
    outcome = {"status": obs["status"], "hp": obs["combat"]["player"]["current_hp"], "enemy_hp_left": S._enemy_hp_left(obs),
               "turns": obs.get("turn"), "decisions": d, "blocked": bool(obs.get("blocked")), "host_restarts": restarts,
               "stuck_rollouts": stuck, "search_seconds": round(t_search, 2),
               "potions_used": max(0, held_at_start - S.potions_held(obs)),
               "enemies": [[e.get("name"), e.get("current_hp"), e.get("max_hp")] for e in obs["combat"].get("enemies", [])]}
    return {"spec": spec, "seed": seed, "outcome": outcome, "decisions": decisions}


def valid_record(r):
    """A record worth keeping: the fight started and was played (the zero-decision 'won' records came from a host
    that could no longer start fights after a stuck rollout, before the restart logic existed)."""
    o = r.get("outcome")
    return bool(o) and bool(r.get("decisions"))


def claim(out, i):
    """Dynamic work sharing: the first worker to create the claim file plays fight i."""
    try:
        fd = os.open(out / "claims" / f"{i:06d}", os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        return False


def done_seeds(out):
    seeds = set()
    for f in out.glob("shard-*.jsonl"):
        for line in f.open():
            r = json.loads(line)
            if valid_record(r):
                seeds.add(r["seed"])
    return seeds


def compact(out):
    """Drop invalid records (errors, fights that never started) so a resumed batch replays them."""
    dropped = 0
    for f in out.glob("shard-*.jsonl"):
        lines = f.read_text().splitlines()
        keep = [l for l in lines if valid_record(json.loads(l))]
        dropped += len(lines) - len(keep)
        if len(keep) != len(lines):
            f.write_text("".join(l + "\n" for l in keep))
    return dropped


def worker(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    shard = out / f"shard-{a.worker:02d}.jsonl"
    stuck_file = out / f"stuck-{a.worker:02d}.jsonl"

    def stuck_log(rec):
        with stuck_file.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")

    finished = done_seeds(out)
    teacher = None
    if a.teacher != "mc":
        sys.path.insert(0, str(PROJECT / "tools" / "learn"))
        import bench                                   # needs the project's PyTorch environment (.venv-learn)
        teacher = bench.make_arm(a.teacher, a.model)
    host = Host()
    try:
        history = load_specs(a.specs) if a.specs else None
        if not history or a.augment:
            encounters = host.sim.encounters()
            pool = host.sim.call(cmd="card_pool", character="IRONCLAD")["cards"]
        order = list(range(len(history))) if history else []
        random.Random(a.seed).shuffle(order)
        for i in range(a.fights):
            seed = a.seed * 1_000_000 + i
            if seed in finished or not claim(out, i):
                continue
            rng = random.Random(seed)
            spec = history[order[i % len(order)]] if history else make_spec(rng, encounters, pool)
            if history and a.augment:
                spec = augment(spec, rng, pool)
            t0 = time.time()
            rec = None
            for attempt in range(2):
                try:
                    if teacher is None and a.wide:
                        room = (spec.get("room") if spec.get("room") in S.POTION_PRICE else "Monster") if a.potions else None
                        rec = play(host, spec, seed, lambda sim, obs, d, done: scored_search(sim, obs, a.mode, a.k, a.top, d, done, potions=room, wide=True,
                                                                                             all_potions=room in ("Elite", "Boss")), stuck_log)
                    elif teacher is None:
                        rec = play_fight(host, spec, seed, a.k, a.top, a.mode, stuck_log)
                    else:
                        rec = play(host, spec, seed, teacher, stuck_log)
                    break
                except S.SimError as e:
                    rec = {"spec": spec, "seed": seed, "error": str(e)[:300], "decisions": []}
                    host.restart()
                    if "host restarts" in str(e) or "did not reproduce" in str(e):
                        break                        # deterministic: a retry would fail the same way
            rec["seconds"] = round(time.time() - t0, 1)
            with shard.open("a") as fh:
                fh.write(json.dumps(rec, separators=(",", ":")) + "\n")
            o = rec.get("outcome", {})
            print(f"w{a.worker} fight {i}: act {spec['act']} {spec['encounter']} A{spec['ascension']} -> {o.get('status', 'error')} "
                  f"HP {o.get('hp')} ({len(rec['decisions'])} decisions, {rec['seconds']} s, restarts {o.get('host_restarts', '-')})", flush=True)
    finally:
        host.close()
    return 0


def load_specs(path):
    """Valid fight specs from tools/fight_specs.py (situations from the Player's history)."""
    data = json.loads(Path(path).read_text())
    return [s for s in data["specs"] if s.get("valid", True)]


def summary(path):
    fights = [json.loads(l) for f in sorted(Path(path).glob("shard-*.jsonl")) for l in f.open()]
    ok = [f for f in fights if "outcome" in f]
    won = sum(1 for f in ok if f["outcome"]["status"] == "won")
    decisions = sum(len(f["decisions"]) for f in ok)
    return {"fights": len(fights), "errors": len(fights) - len(ok), "won": won, "decisions": decisions,
            "host_restarts": sum(f["outcome"].get("host_restarts", 0) for f in ok),
            "blocked_fights": sum(1 for f in ok if f["outcome"].get("blocked")),
            "by_act": {act: sum(1 for f in ok if f["spec"]["act"] == act) for act in (1, 2, 3)},
            "seconds": round(sum(f.get("seconds", 0) for f in fights), 1)}


def git_commit():
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "sim", "tools"], cwd=PROJECT, capture_output=True, text=True).stdout.strip()
    return head + ("-dirty" if dirty else "")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(PROJECT / "data" / "learn" / "combat-v1"))
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--fights", type=int, default=60)
    ap.add_argument("--k", type=int, default=6, help="re-sampled worlds per candidate")
    ap.add_argument("--top", type=int, default=2, help="plans per planner mode")
    ap.add_argument("--mode", default="balanced")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--specs", help="fight specs from tools/fight_specs.py (default: the synthetic generator)")
    ap.add_argument("--teacher", default="mc", help="mc (flat Monte Carlo, k worlds) or a value-network arm of tools/learn/bench.py "
                    "(vleafK, vgreedyK; needs --model and .venv-learn/bin/python)")
    ap.add_argument("--model", help="value network checkpoint for a value-network teacher")
    ap.add_argument("--wide", action="store_true", help="flat Monte Carlo teacher over the wide candidate set (tools/sim.py search_candidates_wide)")
    ap.add_argument("--augment", action="store_true", help="play an augmented variant of each history spec (augment)")
    ap.add_argument("--potions", action="store_true", help="with --wide: the teacher may drink potions as search does inside runs with the `pot` "
                    "component (every usable potion a candidate in elite and boss fights, the planner's potion plans in hallways, priced by room)")
    ap.add_argument("--worker", type=int, help=argparse.SUPPRESS)
    ap.add_argument("--summary", help="print the summary of a dataset folder")
    a = ap.parse_args(argv)
    if a.summary:
        print(json.dumps(summary(a.summary), indent=1))
        return 0
    if a.worker is not None:
        return worker(a)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    dropped = compact(out)
    shutil.rmtree(out / "claims", ignore_errors=True)
    (out / "claims").mkdir()
    if dropped:
        print(f"resuming: dropped {dropped} invalid records; {len(done_seeds(out))} fights already done", flush=True)
    t0 = time.time()
    procs = [subprocess.Popen([sys.executable, "-I", __file__, "--worker", str(w), "--workers", str(a.workers), "--fights", str(a.fights),
                               "--k", str(a.k), "--top", str(a.top), "--mode", a.mode, "--seed", str(a.seed), "--out", str(out),
                               "--teacher", a.teacher] + (["--model", a.model] if a.model else []) + (["--augment"] if a.augment else []) + (["--wide"] if a.wide else []) + (["--potions"] if a.potions else [])
                              + (["--specs", a.specs] if a.specs else []))
             for w in range(a.workers)]
    codes = [p.wait() for p in procs]
    info = Path.home() / "Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app/Contents/Resources/release_info.json"
    build = json.loads(info.read_text()) if info.exists() else {}
    fid = next((l.strip("* ") for l in (PROJECT / "reports/phase7/fidelity.md").read_text().splitlines() if l.startswith("**")), "")
    manifest = {
        "dataset": out.name, "created": time.strftime("%Y-%m-%d %H:%M"), "game_version": build.get("version"), "game_commit": build.get("commit"),
        "host_commit": git_commit(), "fidelity": fid, "encoder": "none (raw observations, docs/observation-spec.md)",
        "teacher": ({"policy": ("flat Monte Carlo over the wide candidate set (tools/sim.py search_candidates_wide)" if a.wide else
                                "flat Monte Carlo over the rule planner's candidates (tools/sim.py search_action)"), "k": a.k, "top": a.top,
                     "rollout_policy": f"plan_turn.py {a.mode}", "potions": bool(a.potions), "privileged": False} if a.teacher == "mc" else
                    {"policy": f"{a.teacher} (tools/learn/bench.py)", "model": a.model, "privileged": False}),
        "spec_source": ({"file": (str(Path(a.specs).resolve().relative_to(PROJECT)) if Path(a.specs).resolve().is_relative_to(PROJECT) else Path(a.specs).name), "about": json.loads(Path(a.specs).read_text())["about"],
                         "augmentation": AUGMENT_VERSION if a.augment else None}
                        if a.specs else "synthetic generator (spec_generator)"),
        "spec_generator": {"version": SPEC_VERSION, "starter": STARTER, "rarity_weight": RARITY_WEIGHT, "added_cards": ADDED,
                           "upgraded_share": UPGRADED, "strikes_removed": REMOVED, "hp": "40-100% of 80", "relics": "starting relic only",
                           "potions": "none", "ascension": "0-10 uniform", "act_weights": [0.4, 0.35, 0.25],
                           "room_weights": {"Monster": 0.7, "Elite": 0.2, "Boss": 0.1}},
        "seed": a.seed, "workers": a.workers, "worker_exit_codes": codes, "wall_seconds": round(time.time() - t0),
        "summary": summary(out),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(json.dumps(manifest["summary"]))
    return 0 if all(c == 0 for c in codes) else 1


if __name__ == "__main__":
    sys.exit(main())
