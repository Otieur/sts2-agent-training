#!/usr/bin/env python3
"""Bridge to the simulator host (sim/, Phase 7): the game's own combat logic running outside the game.

    python3 -I tools/sim.py smoke [REPLAY]      # start the host, position a recorded fight, step and roll out
    python3 -I tools/sim.py fidelity            # replay every recorded fight and compare with the game's recorded states
    python3 -I tools/sim.py fairplay [REPLAY]   # sanitizer, determinism, invariance and leak-canary tests
    python3 -I tools/sim.py planner [REPLAY] [--point K] [--seeds N] [--mode safe|balanced]
                                                # tools/plan_turn.py as the policy inside the simulator

The host must be built first (.NET 9 SDK): STS2_DATA_DIR=<game data folder> dotnet build sim -c Release
Start-up takes 20-40 s (it replaces the game's UI classes). Rules: docs/simulator-integrity.md. Decision mode only
steps a sanitized state (every random generator re-seeded, draw pile shuffled); the recorded fight's true random state
is used only to reach the present and for the fidelity comparison.
"""
import argparse
import json
import os
import re
import select
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
REPLAYS = PROJECT / "data" / "sim" / "replays"
REPORTS = PROJECT / "reports" / "phase7"


class SimError(Exception):
    pass


class Sim:
    """One host process. Requests and replies are JSON lines; replies start with '@@'."""

    def __init__(self, start_timeout=600, log=False):
        self.proc = subprocess.Popen([str(PROJECT / "sim" / "run.sh"), "serve"] + (["log"] if log else []), cwd=PROJECT,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.noise = []
        self.info = self._read(start_timeout)
        if not self.info.get("ready"):
            raise SimError(f"host did not start: {self.info}")

    def _read(self, timeout):
        end = time.time() + timeout
        buf = b""
        while time.time() < end:
            ready, _, _ = select.select([self.proc.stdout], [], [], max(0.0, min(1.0, end - time.time())))
            if not ready:
                if self.proc.poll() is not None:
                    raise SimError(f"host exited with code {self.proc.returncode}; last output: {self.noise[-3:]}")
                continue
            chunk = os.read(self.proc.stdout.fileno(), 65536)
            if not chunk:
                raise SimError(f"host closed its output; last output: {self.noise[-3:]}")
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                text = line.decode("utf-8", "replace")
                if text.startswith("@@"):
                    self._rest = buf
                    return json.loads(text[2:])
                self.noise.append(text)
        raise SimError("host did not answer in time")

    def call(self, timeout=60, **req):
        self.proc.stdin.write((json.dumps(req) + "\n").encode())
        self.proc.stdin.flush()
        r = self._read(timeout)
        if not r.get("ok"):
            raise SimError(f"{req.get('cmd')}: {r.get('error')} ({r.get('where', '')[:300]})")
        return r

    def load(self, path):
        return self.call(cmd="load", path=str(path))

    def points(self):
        return self.call(cmd="points")["decision_points"]

    def reset(self, events, seed=None):
        return self.call(cmd="reset", events=events, seed=seed)

    def new_fight(self, encounter, seed="SIMSEED00001", sample_seed=1, character="IRONCLAD", ascension=0, deck=None, relics=None,
                  potions=None, hp=None):
        """A fight from nothing: a new run for `seed`, the starting deck and relics unless replaced, then the encounter."""
        spec = {"encounter": encounter, "seed": seed, "character": character, "ascension": ascension}
        for k, v in (("deck", deck), ("relics", relics), ("potions", potions), ("hp", hp)):
            if v is not None:
                spec[k] = v
        return self.call(cmd="new_fight", spec=spec, sample_seed=sample_seed, timeout=120)

    def encounters(self):
        return self.call(cmd="encounters")["encounters"]

    def observe(self):
        return self.call(cmd="observe")["obs"]

    def legal(self):
        return self.call(cmd="legal")["actions"]

    def step(self, action):
        return self.call(cmd="step", action=action)["obs"]

    def hidden(self):
        return self.call(cmd="hidden")["hidden"]

    def rollout(self, policy="first", seed=0, max_steps=400):
        return self.call(cmd="rollout", policy=policy, seed=seed, max_steps=max_steps, timeout=120)

    def stats(self):
        return self.call(cmd="stats")

    def close(self):
        try:
            self.call(cmd="quit", timeout=5)
        except Exception:  # noqa: BLE001
            pass
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def installed_build_replays():
    """Recorded fights from the installed game build, and the skipped ones as (path, version) (headers name the build)."""
    sys.path.insert(0, str(PROJECT / "tools"))
    import keep_replays
    info = Path(os.environ.get("STS2_DATA_DIR", str(Path.home() / "Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64"))).parent / "release_info.json"
    installed = json.loads(info.read_text()).get("commit") if info.exists() else None
    files, skipped = [], []
    for f in sorted(REPLAYS.glob("*/*.mcr")):
        h = keep_replays.read_header(f.read_bytes()[:128])
        if installed and h and h[1] != installed:
            skipped.append((f.relative_to(REPLAYS), h[0]))
        else:
            files.append(f)
    return files, skipped


def default_replay():
    files, _ = installed_build_replays()
    if not files:
        sys.exit("no recorded fights under data/sim/replays (tools/play_turn.py keeps them during live play)")
    return files[-1]


def brief(obs):
    c = obs["combat"]
    p = c["player"]
    hand = ", ".join(f"{h['card_id']}{'+' if h['upgraded'] else ''}({h['energy_cost']})" for h in c["hand"])
    foes = ", ".join(f"{e['enemy_id']} {e['current_hp']}/{e['max_hp']}"
                     + "".join(f" [{i['intent_type']}{' ' + str(i['damage']) + 'x' + str(i['hits']) if 'damage' in i else ''}]" for i in e["intents"])
                     for e in c["enemies"] if e["is_alive"])
    return (f"{obs['status']} turn {obs['turn']} HP {p['current_hp']}/{p['max_hp']} block {p['block']} energy {p['energy']} | hand: {hand} | "
            f"{foes} | draw {c['draw_pile_count']} discard {c['discard_pile_count']}")


def cmd_smoke(a):
    t0 = time.time()
    with Sim() as sim:
        print(f"host ready in {time.time() - t0:.1f} s: game {sim.info['game_version']} {sim.info['game_commit']}, model-id hash {sim.info['model_id_hash']}")
        r = sim.load(a.replay or default_replay())
        pts = sim.points()
        print(f"replay loaded: {r['events']} events, {len(pts)} decision points {pts[:8]}...")
        obs = sim.reset(pts[0], seed=1)["obs"]
        print("start      :", brief(obs))
        acts = sim.legal()
        print(f"legal      : {len(acts)} actions, e.g. {acts[:3]}")
        obs = sim.step(acts[0])
        print("after step :", brief(obs))
        t1 = time.time()
        results = []
        for seed in range(1, 11):
            sim.reset(pts[0], seed=seed)
            r = sim.rollout(policy="random", seed=seed)
            results.append((r["obs"]["status"], r["obs"]["combat"]["player"]["current_hp"], r["steps"]))
        dt = time.time() - t1
        print(f"10 random rollouts from the first decision point: {results}")
        st = sim.stats()
        print(f"{sum(x[2] for x in results)} steps in {dt:.2f} s ({1000 * dt / max(1, sum(x[2] for x in results)):.2f} ms per step including the bridge); "
              f"sanitize {st['sanitize_ms']:.2f} ms; host memory {st['managed_mb']} MB")
    return 0


def cmd_fairplay(a):
    """P7.E6: what the sanitizer must guarantee, checked on a recorded fight."""
    results = []

    def check(name, ok, detail=""):
        results.append(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {name}{': ' + detail if detail else ''}")

    with Sim() as sim:
        sim.load(a.replay or default_replay())
        pts = sim.points()
        probes = [p for p in pts][:: max(1, len(pts) // 8)][:8]
        same_obs = changed = det = 0
        top_matches = top_trials = 0
        order_changes = order_trials = 0
        for k in probes:
            true_obs = sim.reset(k, seed=None)["obs"]
            true_hidden = sim.hidden()
            first = None
            for seed in range(1, a.seeds + 1):
                r = sim.reset(k, seed=seed)
                obs, hidden = r["obs"], sim.hidden()
                strip = lambda o: {x: v for x, v in o.items() if x != "sanitized"}  # noqa: E731
                same_obs += strip(obs) == strip(true_obs)
                changed += all(g not in set(true_hidden["generators"]) for g in hidden["generators"]) and r["generators_reseeded"] == len(hidden["generators"])
                if seed == 1:
                    first = hidden
                    again = sim.reset(k, seed=1)
                    det += sim.hidden() == first and again["obs"] == obs
                n = len(true_hidden["draw_order"])
                if n >= 6:
                    order_trials += 1
                    order_changes += hidden["draw_order"] != true_hidden["draw_order"]
                    top_trials += 1
                    top_matches += hidden["draw_order"][:3] == true_hidden["draw_order"][:3] or hidden["draw_order"][-3:] == true_hidden["draw_order"][-3:]
        total = len(probes) * a.seeds
        check("observation unchanged by sanitizing (the player sees the same fight)", same_obs == total, f"{same_obs} of {total}")
        check("every reachable generator re-seeded, none keeps its state (FP-2)", changed == total, f"{changed} of {total}")
        check("same sample seed gives the same hidden state and observation (determinism)", det == len(probes), f"{det} of {len(probes)}")
        if order_trials:
            check("draw order changes with the sample seed (FP-1)", order_changes >= 0.9 * order_trials, f"{order_changes} of {order_trials}")
            check("leak canary: the true next three draws are not reproduced more often than chance (FP-15)",
                  top_matches <= max(2, 0.15 * top_trials), f"{top_matches} of {top_trials} samples matched the true top or bottom three")
        else:
            print("skip draw-order checks: no probe had a draw pile of six or more cards")
        # invariance of a policy that sees only the observation: the rule planner must choose the same play for every sample seed
        sys.path.insert(0, str(PROJECT / "tools"))
        import plan_turn as pt
        inv = 0
        for k in probes:
            picks = set()
            for seed in range(1, min(a.seeds, 5) + 1):
                picks.add(json.dumps(planner_action(pt, sim.reset(k, seed=seed)["obs"], "safe"), sort_keys=True))
            inv += len(picks) == 1
        check("invariance: the planner's choice does not depend on the sample seed (FP-1)", inv == len(probes), f"{inv} of {len(probes)} decision points")
        try:
            sim.reset(probes[0], seed=None)
            sim.step({"type": "end_turn"})
            check("decision mode refuses an unsanitized state (FP-3)", False, "a step was accepted")
        except SimError as e:
            check("decision mode refuses an unsanitized state (FP-3)", "sanitized" in str(e))
        # FP-5: a card the player put on top (Headbutt returns Bash from the discard pile) stays on top in every
        # sample of the hidden state, while the order below it varies.
        name = "known draw-pile positions: a card the player put on top stays on top in every sample (FP-5)"
        deck = ["STRIKE_IRONCLAD"] * 4 + ["DEFEND_IRONCLAD"] * 4 + ["BASH", "HEADBUTT"]
        for k in range(1, 80):
            sim.new_fight("SLIMES_WEAK", seed=f"FPFIVE{k:06d}", sample_seed=k, deck=deck)
            acts = sim.legal()
            if not {"BASH", "HEADBUTT"} <= {x.get("card_id") for x in acts if x["type"] == "play"}:
                continue
            sim.step(next(x for x in acts if x.get("card_id") == "BASH"))
            sim.step(next(x for x in sim.legal() if x.get("card_id") == "HEADBUTT"))
            ch = sim.observe().get("choice")
            if ch:
                sim.step({"type": "choose", "cards": [ch["options"].index("BASH")]})
            known = sim.hidden()["known"]
            before = sim.call(cmd="stats")
            tops, orders = 0, set()
            for s2 in range(12):
                sim.call(cmd="resample", sample_seed=1000 + s2)
                h = sim.hidden()
                tops += h["draw_order"][0] == "BASH"
                orders.add(tuple(h["draw_order"][1:]))
            st = sim.call(cmd="stats")
            fb = st["draw_fallbacks"] - before["draw_fallbacks"]
            check(name, known["known_top"][:1] == ["BASH"] and tops == 12 and len(orders) > 1 and fb == 0,
                  f"known top {known['known_top']}; Bash on top in {tops} of 12 samples; {len(orders)} distinct orders below it; "
                  f"{fb} fallbacks to a full shuffle")
            break
        else:
            check(name, False, "no opening hand with Bash and Headbutt in 79 seeds")
    print(f"{sum(results)} of {len(results)} fair-play checks passed")
    return 0 if all(results) else 1


def _fight_from_run(run, sim, k, rng, via_run=False):
    """For `clone --from-save`: play a whole run in `run` (simple run policy) to a decision some way into its first,
    second or third fight, export that fight and rebuild it in `sim` from the saved run state (`fight_from_save`).
    Returns the encounter label, or None when the run ended first."""
    if str(PROJECT / "tools") not in sys.path:
        sys.path.insert(0, str(PROJECT / "tools"))
    import plan_turn as pt
    obs = run.call(cmd="new_run", spec={"seed": f"CLONESAVE{k:05d}", "character": "IRONCLAD", "ascension": 0, "record_fights": True}, timeout=120)["obs"]
    want_fight, want_decision = 1 + k % 3, rng.randint(0, 12)
    nf, prev, actions = 0, False, []
    for _ in range(4000):
        if obs["screen"] == "game_over":
            return None
        in_fight = obs["screen"] == "combat" or (obs["screen"] == "choice" and bool(obs.get("combat")))
        if in_fight and not prev:
            nf, actions = nf + 1, []
        acts = run.call(cmd="run_legal")["actions"]
        if in_fight and nf == want_fight and len(actions) >= want_decision:
            if via_run:       # through the run clone: the room-entry save plus the run actions since
                ex = run.call(cmd="run_export")["export"]
                got = sim.call(cmd="fight_from_run", data=ex["save_b64"], actions=ex["actions"], sample_seed=k + 1, timeout=120)["obs"]
            else:
                data = run.call(cmd="export_fight")["replay_b64"]
                got = sim.call(cmd="fight_from_save", data=data, actions=actions, sample_seed=k + 1, timeout=120)["obs"]
            return "/".join(e["enemy_id"] for e in (got.get("combat") or {}).get("enemies", []))[:36] or "?"
        action = run_policy(pt, obs, acts, rng)
        if in_fight:
            actions.append(action)
        prev = in_fight
        obs = run.call(cmd="run_step", action=action, timeout=120)["obs"]
    return None


def cmd_clone(a):
    """State cloning (P7.E4.S4): snapshot a decision-mode fight, play on, restore, and check the restored state equals
    the snapshot (observation, draw order, every generator) and that the same actions then lead to the same result.
    `--from-save`: the fights are rebuilt from the saved state of fights inside simulated runs (`fight_from_save`)."""
    import contextlib
    import random
    ok, times = 0, []
    with Sim() as sim, (Sim() if a.from_save or a.from_run else contextlib.nullcontext()) as run:
        encs = [e["id"] for e in sim.encounters() if e["room_type"] in ("Monster", "Elite", "Boss")]
        rng = random.Random(7)
        for k in range(a.fights):
            if a.from_save or a.from_run:
                enc = _fight_from_run(run, sim, k, rng, via_run=a.from_run)
                if enc is None:
                    continue
            else:
                enc = encs[(k * 7) % len(encs)]
                sim.new_fight(enc, seed=f"CLONE{k:07d}", sample_seed=k + 1)
            for _ in range(rng.randint(2, 8)):          # play into the fight a little
                acts = sim.legal()
                if not acts or sim.observe()["status"] != "in_progress":
                    break
                sim.step(rng.choice(acts))
            if sim.observe()["status"] != "in_progress":
                continue
            if k % 3 == 0:
                sim.call(cmd="resample", sample_seed=500 + k)   # a re-sample is part of the recipe too
            snap = sim.call(cmd="snapshot")["id"]
            want_obs, want_hidden = sim.observe(), sim.hidden()
            line = []
            for _ in range(10):
                acts = sim.legal()
                if not acts or sim.observe()["status"] != "in_progress":
                    break
                act = rng.choice(acts)
                line.append(act)
                sim.step(act)
            end_obs = sim.observe()
            r = sim.call(cmd="restore", id=snap)
            times.append(r["restore_ms"])
            got_obs, got_hidden = sim.observe(), sim.hidden()
            same_now = got_obs == want_obs and got_hidden["draw_order"] == want_hidden["draw_order"] and got_hidden["generators"] == want_hidden["generators"]
            for act in line:
                sim.step(act)
            same_after = sim.observe() == end_obs
            ok += same_now and same_after
            print(f"{'ok  ' if same_now and same_after else 'FAIL'} {enc:36s} restored equal {same_now}, same line same result {same_after}, {r['restore_ms']:.1f} ms")
    n = len(times)
    print(f"{ok} of {n} restores exact; restore time median {sorted(times)[n // 2] if n else 0:.1f} ms")
    return 0 if ok == n and n > 0 else 1


_VOLATILE = {"applied_events", "sanitized", "handled_messages", "sent", "status", "waiting_for_choice", "blocked", "draw_order", "generators"}


def _visible_run(o):
    """A run observation without host bookkeeping fields (for clone comparisons)."""
    if isinstance(o, dict):
        return {k: _visible_run(v) for k, v in o.items() if k not in _VOLATILE}
    if isinstance(o, list):
        return [_visible_run(x) for x in o]
    return o


def _run_future(host, obs, rng, n):
    """What a player would see over the next n steps of the simple run policy: encounters, card offers, events, and the
    maps of acts entered later (for sampler checks)."""
    sys.path.insert(0, str(PROJECT / "tools"))
    import plan_turn as pt
    sig, act = [], obs.get("act")
    for _ in range(n):
        if obs["screen"] == "game_over":
            sig.append(("over", obs.get("floor")))
            break
        obs = host.call(cmd="run_step", action=run_policy(pt, obs, host.call(cmd="run_legal")["actions"], rng), timeout=120)["obs"]
        if obs.get("act") != act:
            act = obs.get("act")
            sig.append(("map", act, tuple(sorted((p["col"], p["row"], p["type"]) for p in host.call(cmd="map")["map"]["points"]))))
        if obs.get("encounter") and (not sig or sig[-1] != ("enc", obs["encounter"])):
            sig.append(("enc", obs["encounter"]))
        ch = obs.get("choice") or {}
        if ch.get("kind") == "CardReward":
            sig.append(("cards", tuple(ch.get("options", []))))
        if obs.get("event_id") and (not sig or sig[-1] != ("event", obs["event_id"])):
            sig.append(("event", obs["event_id"]))
    return sig


def cmd_runclone(a):
    """Run-level clones and the run sampler (P7.E8.S4, FP-16). (1) Exact rebuilds: along whole runs, the run is exported
    (the room-entry save the game makes, kept in memory, plus the run actions since) and rebuilt in a second host; the
    visible state must be equal and the same actions must then give the same observations. (2) Sampler: at decision
    points on the map (test-HP runs, so later acts are reached), rebuilds with sample seeds keep the visible state, the
    same seed gives the same future, other seeds and the true future differ, and acts not yet entered get other maps.
    (3) Leak canary: over many sample seeds the true next encounter is not reproduced more often than chance."""
    import random
    sys.path.insert(0, str(PROJECT / "tools"))
    import plan_turn as pt
    fails = 0
    with Sim() as run, Sim() as cl:
        exact, cont = 0, 0
        for k in range(a.runs):
            rng = random.Random(k)
            obs = run.call(cmd="new_run", spec={"seed": f"RUNCLONE{k:04d}", "character": "IRONCLAD", "ascension": 5}, timeout=120)["obs"]
            for step in range(1500):
                if obs["screen"] == "game_over":
                    break
                if step % 19 == 7:
                    ex = run.call(cmd="run_export")["export"]
                    o = cl.call(cmd="run_from_save", data=ex["save_b64"], actions=ex["actions"], test_hp=ex["test_hp"], timeout=120)["obs"]
                    same = _visible_run(o) == _visible_run(obs)
                    line_ok = same
                    if same:          # the same five actions from both hosts give the same observations
                        r2 = random.Random(step)
                        o1, o2 = obs, o
                        for _ in range(5):
                            if o1["screen"] == "game_over":
                                break
                            act = run_policy(pt, o1, run.call(cmd="run_legal")["actions"], r2)
                            o1 = run.call(cmd="run_step", action=act, timeout=120)["obs"]
                            o2 = cl.call(cmd="run_step", action=act, timeout=120)["obs"]
                            line_ok = line_ok and _visible_run(o1) == _visible_run(o2)
                        obs = o1
                    exact += same
                    cont += line_ok
                    fails += not line_ok
                    if not line_ok:
                        print(f"FAIL run {k} step {step} floor {obs.get('floor')} {obs['screen']}: rebuilt equal {same}, same line {line_ok}")
                    continue
                obs = run.call(cmd="run_step", action=run_policy(pt, obs, run.call(cmd="run_legal")["actions"], rng), timeout=120)["obs"]
        n_exact = exact if exact else 0
        print(f"exact rebuilds: {exact} equal, {cont} with the same continuation")
        for k, floor in enumerate((6, 12)):
            rng = random.Random(100 + k)
            obs = run.call(cmd="new_run", spec={"seed": f"RUNSAMPLE{k:04d}", "character": "IRONCLAD", "ascension": 0, "test_max_hp": 999}, timeout=120)["obs"]
            while obs.get("floor", 0) < floor or obs["screen"] != "map":
                obs = run.call(cmd="run_step", action=run_policy(pt, obs, run.call(cmd="run_legal")["actions"], rng), timeout=120)["obs"]
            ex = run.call(cmd="run_export")["export"]
            truth = _run_future(run, obs, random.Random(7), 500)
            futs, vis = {}, True
            for sd in (11, 22, 11):
                o = cl.call(cmd="run_from_save", data=ex["save_b64"], actions=ex["actions"], test_hp=ex["test_hp"], sample_seed=sd, timeout=120)["obs"]
                vis = vis and _visible_run(o) == _visible_run(obs)
                futs.setdefault(sd, []).append(_run_future(cl, o, random.Random(7), 500))
            maps = lambda f: [x for x in f if x[0] == "map"]
            checks = {"visible state kept": vis, "same seed, same future": futs[11][0] == futs[11][1],
                      "other seed, other future": futs[11][0] != futs[22][0], "true future not reproduced": futs[11][0] != truth,
                      "later maps re-sampled": maps(futs[11][0]) != maps(truth) and maps(futs[22][0]) != maps(truth)}
            if not maps(truth):
                checks.pop("later maps re-sampled")
                print(f"     sampler at floor {obs['floor']}: no later act reached in the future played, maps not compared")
            for name, ok in checks.items():
                print(f"{'ok  ' if ok else 'FAIL'} sampler at floor {obs['floor']}: {name}")
                fails += not ok
        # no repeated encounters within an act in sampled futures (the game does not repeat while others remain)
        def act_encounters(host, o, r, log):
            act = o.get("act")
            for _ in range(600):
                if o["screen"] == "game_over" or o.get("act") != act:
                    break
                legal = host.call(cmd="run_legal")["actions"]
                if not legal:
                    break
                o = host.call(cmd="run_step", action=run_policy(pt, o, legal, r), timeout=120)["obs"]
                e = o.get("encounter")
                if e and o["screen"] == "combat" and (not log or log[-1] != e):
                    log.append(e)
        rep = {"true": [0, 0], "sampled": [0, 0]}
        for k in range(4):
            rng = random.Random(200 + k)
            obs = run.call(cmd="new_run", spec={"seed": f"RUNREPEAT{k:03d}", "character": "IRONCLAD", "ascension": 0, "test_max_hp": 999}, timeout=120)["obs"]
            seen = []
            while obs.get("floor", 0) < 5 or obs["screen"] != "map":
                obs = run.call(cmd="run_step", action=run_policy(pt, obs, run.call(cmd="run_legal")["actions"], rng), timeout=120)["obs"]
                e = obs.get("encounter")
                if e and obs["screen"] == "combat" and (not seen or seen[-1] != e):
                    seen.append(e)
            ex = run.call(cmd="run_export")["export"]
            futs = [("true", run, obs)] + [("sampled", cl, cl.call(cmd="run_from_save", data=ex["save_b64"], actions=ex["actions"],
                                                                     test_hp=ex["test_hp"], sample_seed=sd, timeout=120)["obs"]) for sd in (1, 2)]
            for name, host, o in futs:
                log = []
                act_encounters(host, o, random.Random(5), log)
                met = set(seen)
                for e in log:
                    rep[name][0] += e in met and not e.endswith("_BOSS")
                    met.add(e)
                rep[name][1] += len(log)
        rate = {k: v[0] / max(1, v[1]) for k, v in rep.items()}
        ok = rate["sampled"] <= rate["true"] + 0.02
        print(f"{'ok  ' if ok else 'FAIL'} repeated encounters within the act: true {rep['true'][0]}/{rep['true'][1]}, sampled {rep['sampled'][0]}/{rep['sampled'][1]}")
        fails += not ok
        # leak canary: the next normal encounter after a decision point, true against sampled
        rng = random.Random(9)
        obs = run.call(cmd="new_run", spec={"seed": "RUNCANARY01", "character": "IRONCLAD", "ascension": 0, "test_max_hp": 999}, timeout=120)["obs"]
        while obs.get("floor", 0) < 4 or obs["screen"] != "map":
            obs = run.call(cmd="run_step", action=run_policy(pt, obs, run.call(cmd="run_legal")["actions"], rng), timeout=120)["obs"]
        ex = run.call(cmd="run_export")["export"]
        first = lambda f: next((x[1] for x in f if x[0] == "enc" and x[1].endswith("_NORMAL")), None)
        true_next = first(_run_future(run, obs, random.Random(3), 120))
        hits = 0
        for sd in range(a.canary):
            o = cl.call(cmd="run_from_save", data=ex["save_b64"], actions=ex["actions"], test_hp=ex["test_hp"], sample_seed=1000 + sd, timeout=120)["obs"]
            hits += first(_run_future(cl, o, random.Random(3), 120)) == true_next
        ok = hits < 0.6 * a.canary
        print(f"{'ok  ' if ok else 'FAIL'} leak canary: the true next normal encounter ({true_next}) in {hits} of {a.canary} sampled futures")
        fails += not ok
    print(f"{'all run-clone checks passed' if not fails else f'{fails} run-clone checks failed'}")
    return 0 if not fails else 1


def cmd_sandbox(a):
    """SA-1, SA-2 (P7.E3.S3), automated: over fights from nothing and whole runs, the host leaves the game's save folder
    unchanged (compared by size, time and hash, read only), writes nothing into its sandbox home, and opens no network
    connection (its process is polled with lsof while it works)."""
    import hashlib, random, re, threading
    sys.path.insert(0, str(PROJECT / "tools"))
    import plan_turn as pt
    saves = Path.home() / "Library" / "Application Support" / "SlayTheSpire2"
    sandbox = PROJECT / "data" / "sim" / "sandbox-home"
    mask = lambda x: re.sub(r"\d{10,}", "<id>", x)          # Steam ids never appear in output

    def tree(root):
        out = {}
        if root.exists():
            for f in sorted(root.rglob("*")):
                if f.is_file() and not f.is_symlink():
                    st = f.stat()
                    out[str(f.relative_to(root))] = (st.st_size, st.st_mtime_ns, hashlib.sha1(f.read_bytes()).hexdigest() if st.st_size < 50_000_000 else "")
        return out

    game_running = subprocess.run(["pgrep", "-f", "SlayTheSpire2.app/Contents/MacOS"], capture_output=True).returncode == 0
    before, sand_before = tree(saves), tree(sandbox)
    sockets, polls, stop = [], [0], threading.Event()
    t0 = time.time()
    with Sim() as sim:
        pid = sim.proc.pid

        def watch():
            while not stop.is_set():
                r = subprocess.run(["lsof", "-a", "-i", "-n", "-P", "-p", str(pid)], capture_output=True, text=True)
                polls[0] += 1
                sockets.extend(l for l in r.stdout.splitlines()[1:] if l.strip())
                stop.wait(0.5)

        th = threading.Thread(target=watch, daemon=True)
        th.start()
        encs = [e["id"] for e in sim.encounters()]
        for k in range(a.fights):
            sim.new_fight(encs[(k * 11) % len(encs)], seed=f"SANDBOX{k:05d}", sample_seed=k + 1)
            sim.rollout(policy="random", seed=k + 1, max_steps=600)
        rng = random.Random(1)
        for k in range(a.runs):
            obs = sim.call(cmd="new_run", spec={"seed": f"SANDRUN{k:05d}", "character": "IRONCLAD", "ascension": 0}, timeout=120)["obs"]
            for _ in range(3000):
                if obs["screen"] == "game_over":
                    break
                acts = sim.call(cmd="run_legal")["actions"]
                if not acts:
                    break
                obs = sim.call(cmd="run_step", action=run_policy(pt, obs, acts, rng), timeout=120)["obs"]
        stop.set()
        th.join()
    after, sand_after = tree(saves), tree(sandbox)
    changed = sorted(mask(k) for k in set(before) | set(after) if before.get(k) != after.get(k))
    sand_new = sorted(k for k in set(sand_before) | set(sand_after) if sand_before.get(k) != sand_after.get(k))
    results = []

    def check(name, good, detail):
        results.append(good)
        print(f"{'ok  ' if good else 'FAIL'} {name}: {detail}")

    if game_running:
        print("skip save-folder comparison: the game is running and may write its own files")
    else:
        check("save folder unchanged (SA-1)", not changed, f"{len(before)} files compared; changed: {changed[:5]}")
    check("nothing written into the sandbox home (SA-1)", not sand_new, f"{len(sand_after)} files; new or changed: {sand_new[:5]}")
    check("no network connection opened (SA-2)", not sockets and polls[0] > 3, f"{polls[0]} polls over {time.time() - t0:.0f} s; sockets seen: {len(sockets)}")
    print(f"{sum(results)} of {len(results)} sandbox checks passed")
    return 0 if all(results) else 1


# Price of spending a potion in a fight, in HP, by room type: the planner's potion cost (plan_turn.POTION_COST,
# [HYPOTHESIS]). Used when search and rollouts may drink potions (`potions=<room>`), so that a fight value counts a
# spent potion as lost HP instead of free.
POTION_PRICE = {"Monster": 25.0, "Elite": 6.0, "Boss": 2.0}


def _act_from(card, ref):
    act = {"type": "potion", "slot": card.index} if card.potion else {"type": "play", "card": card.index}
    if card.target == "AnyEnemy" and ref is not None:
        act["target"] = ref
    return act


def _same_action(a, b):
    return all(a.get(k) == b.get(k) for k in ("type", "card", "slot", "target", "cards"))


def potions_held(obs):
    return sum(1 for p in ((obs.get("run") or {}).get("potions") or []) if p.get("occupied"))


def _hand_for(pt, obs, potions):
    """Planner inputs; potion slots are kept only when potions may be used (`potions` = room type for the price)."""
    hand, player, enemies = pt.from_state(obs)
    if not potions:
        hand = [c for c in hand if not c.potion]
    return hand, player, enemies


def _rank(pt, results, mode, potions):
    return pt.rank(results, mode, potion_cost=POTION_PRICE[potions]) if potions else pt.rank(results, mode)


def search_candidates(sim, pt, obs, top, potions=None):
    """First actions of the rule planner's top plans in both modes, plus ending the turn; only legal ones. With
    `potions` (the room type), the plans may drink potions at that room's price."""
    if obs.get("choice"):
        return [planner_action(pt, obs, "safe")]
    hand, player, enemies = _hand_for(pt, obs, potions)
    cands = []
    if enemies and hand:
        for mode in ("safe", "balanced"):
            for plan in _rank(pt, pt.plans(hand, player, enemies), mode, potions)[:top]:
                seq = plan.get("seq") or []
                a = _act_from(*seq[0]) if seq else {"type": "end_turn"}
                if not any(_same_action(a, c) for c in cands):
                    cands.append(a)
    if not any(c["type"] == "end_turn" for c in cands):
        cands.append({"type": "end_turn"})
    legal = sim.legal()
    return [c for c in cands if any(_same_action(c, l) for l in legal)] or [{"type": "end_turn"}]


def search_candidates_wide(sim, pt, obs, top, cap=8, potions=None, all_potions=False):
    """The planner's candidates first, then every other legal card play, one per distinct card (id and upgrade) and
    target, up to `cap` candidates in all; ending the turn is always included. Lets search find moves the planner's
    own plans never propose. With `all_potions` (and `potions` set to the room type), every usable potion (one per
    distinct potion and target) is added on top of the cap, so search judges potions by simulation rather than by the
    planner's potion model (which knows 17 potions)."""
    base = search_candidates(sim, pt, obs, top, potions)
    if obs.get("choice") or any(c["type"] == "choose" for c in base):
        return base
    hand = (obs.get("combat") or {}).get("hand") or []
    def key(a):
        if a["type"] != "play":
            return (a["type"], a.get("slot"), a.get("target"))
        h = hand[a["card"]] if a["card"] < len(hand) else {}
        return ("play", h.get("card_id"), h.get("upgraded"), a.get("target"))
    seen = {key(a) for a in base}
    out = [a for a in base if a["type"] != "end_turn"]
    legal = sim.legal()
    for l in legal:
        if len(out) >= cap - 1:
            break
        if l.get("type") != "play":
            continue
        a = {k: l[k] for k in ("type", "card", "target") if k in l}
        if key(a) not in seen:
            seen.add(key(a))
            out.append(a)
    if potions and all_potions:
        pots = {}
        for l in legal:
            if l.get("type") == "potion":
                k2 = (l.get("potion_id"), l.get("target"))
                if k2 not in pots and not any(c.get("type") == "potion" and c.get("slot") == l["slot"] and c.get("target") == l.get("target") for c in out):
                    pots[k2] = {k: l[k] for k in ("type", "slot", "target") if k in l}
        out += list(pots.values())
    return out + [{"type": "end_turn"}]


def _finish_with_planner(sim, pt, obs, mode, limit=300, potions=None):
    for _ in range(limit):
        if obs["status"] != "in_progress" or obs.get("blocked"):
            break
        try:
            obs = sim.step(planner_action(pt, obs, mode, potions))
        except SimError:
            obs = sim.step({"type": "end_turn"})
    return obs


# Above this, an enemy's HP is a placeholder for a phase that cannot be won by damage (the Waterfall Giant's HP becomes
# about 10^9 once its 240 HP are gone and the fight turns into surviving); such HP is not counted as HP left.
UNKILLABLE_HP = 10_000


def _enemy_hp_left(obs):
    return sum(e.get("current_hp", 0) for e in (obs.get("combat") or {}).get("enemies", [])
               if 0 < e.get("current_hp", 0) <= UNKILLABLE_HP)


def _value(obs, spent=0, price=0.0):
    """HP left after a win; after a loss, -100 minus the enemies' HP left (losing closer to a win is better); minus
    `price` HP per potion spent when potions are in play."""
    base = obs["combat"]["player"]["current_hp"] if obs["status"] == "won" else -100 - _enemy_hp_left(obs)
    return base - price * spent


def search_action(sim, pt, obs, mode, k, top, decision):
    """Flat Monte Carlo over the planner's candidate first actions (P8 first experiment). Each candidate is scored on
    k re-sampled worlds (restore the snapshot, re-sample the hidden state, play the candidate, finish with the planner);
    all candidates share the same sample seeds. Only the past is restored; the future is re-sampled (FP-15)."""
    cands = search_candidates(sim, pt, obs, top)
    if len(cands) == 1:
        return cands[0], 0
    snap = sim.call(cmd="snapshot")["id"]
    best, best_v, sims = cands[0], None, 0
    for a in cands:
        total = 0
        for j in range(k):
            sim.call(cmd="restore", id=snap)
            sim.call(cmd="resample", sample_seed=1_000_003 * (decision + 1) + j)
            try:
                o = sim.step(a)
            except SimError:
                total += -1000
                continue
            total += _value(_finish_with_planner(sim, pt, o, mode))
            sims += 1
        if best_v is None or total > best_v:
            best, best_v = a, total
    sim.call(cmd="restore", id=snap)       # back to the real fight
    return best, sims


def cmd_search(a):
    """First search experiment: the rule planner alone against flat Monte Carlo over its candidate actions, on the same
    fights from nothing (same encounter, run seed and sample seed). Reports HP left and wins per policy."""
    sys.path.insert(0, str(PROJECT / "tools"))
    import plan_turn as pt
    rows = []
    t0 = time.time()
    with Sim() as sim:
        encs = [e["id"] for e in sim.encounters() if e["room_type"] in a.rooms.split(",") and not e["weak"]]
        picked = encs[:: max(1, len(encs) // a.fights)][: a.fights]
        for enc in picked:
            for s in range(a.seeds):
                res = {}
                for policy in ("planner", "search"):
                    obs = sim.new_fight(enc, seed=f"SEARCH{s:06d}", sample_seed=s + 1)["obs"]
                    t1, decision, sims = time.time(), 0, 0
                    while obs["status"] == "in_progress" and not obs.get("blocked") and decision < 300:
                        if policy == "planner":
                            act = planner_action(pt, obs, a.mode)
                        else:
                            act, n = search_action(sim, pt, obs, a.mode, a.k, a.top, decision)
                            sims += n
                        try:
                            obs = sim.step(act)
                        except SimError:
                            obs = sim.step({"type": "end_turn"})
                        decision += 1
                    res[policy] = (obs["status"], obs["combat"]["player"]["current_hp"], decision, sims, time.time() - t1, _enemy_hp_left(obs))
                rows.append((enc, s, res))
                p, q = res["planner"], res["search"]
                print(f"{enc:34s} s{s}  planner {p[0]:5s} HP {p[1]:3d} (enemy {p[5]:3d}) | search {q[0]:5s} HP {q[1]:3d} (enemy {q[5]:3d}) ({q[3]} rollouts, {q[4]:.0f} s)", flush=True)
    n = len(rows)
    def summ(pol):
        wins = sum(1 for r in rows if r[2][pol][0] == "won")
        hp = sum(r[2][pol][1] for r in rows) / max(n, 1)
        return wins, hp
    pw, ph = summ("planner"); sw, sh = summ("search")
    def val(t):
        return t[1] if t[0] == "won" else -100 - t[5]
    better = sum(1 for r in rows if val(r[2]["search"]) > val(r[2]["planner"]))
    worse = sum(1 for r in rows if val(r[2]["search"]) < val(r[2]["planner"]))
    L = ["# First search experiment: rule planner against flat Monte Carlo", "",
         f"Generated by `tools/sim.py search` on {time.strftime('%Y-%m-%d %H:%M')}. Fights from nothing (Ironclad starting deck, "
         f"80 HP), {len(set(r[0] for r in rows))} encounters (room types {a.rooms}, not the weak pool) × {a.seeds} seeds; both "
         f"policies play the same fight (same run seed and sample seed). Planner mode `{a.mode}`. Search: at every decision, the "
         f"first actions of the planner's top {a.top} plans in both modes plus ending the turn, each scored on {a.k} re-sampled "
         f"worlds (restore, re-sample the hidden state, play it, finish with the planner; value = HP left, or -100 minus the enemies' HP left for a loss), "
         f"with shared sample seeds across candidates. Decisions use only what the player can see (FP-15).", "",
         "**Exploratory** unless run from a filled `templates/comparison.md` (P8.E1.S3, ML-10); fights from nothing with the "
         "starting deck are not the benchmark set (P8.E1.S1).", "",
         f"- Planner: won {pw} of {n}, mean HP left {ph:.1f}",
         f"- Search: won {sw} of {n}, mean HP left {sh:.1f}",
         f"- Search better in {better} fights, worse in {worse}, equal in {n - better - worse}",
         f"- Total time {time.time() - t0:.0f} s", "",
         "| Encounter | Seed | Planner | Search | Search rollouts | Search seconds |", "|---|---|---|---|---|---|"]
    def cell(t):
        return f"{t[0]} {t[1]} HP" + (f" (enemies {t[5]} HP left)" if t[0] != "won" else "")
    L += [f"| {r[0]} | {r[1]} | {cell(r[2]['planner'])} | {cell(r[2]['search'])} | {r[2]['search'][3]} | {r[2]['search'][4]:.0f} |" for r in rows]
    out = PROJECT / "reports" / "phase8" / a.report
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n")
    print(f"planner won {pw}/{n} (HP {ph:.1f}); search won {sw}/{n} (HP {sh:.1f}); better {better}, worse {worse}. Report: {out.relative_to(PROJECT)}")
    return 0


def baseline_action(sim, pt, obs, policy, rng):
    """Baseline policies (P8.E1.S2). random: a uniform legal action. greedy: the play with the most immediate damage
    (the planner's one-card simulation), else the most block, else end the turn."""
    acts = sim.legal()
    if policy == "random" or obs.get("choice"):
        return rng.choice(acts) if acts else {"type": "end_turn"}
    hand, player, enemies = pt.from_state(obs)
    by_index = {c.index: c for c in hand if not c.potion}
    best, best_key = {"type": "end_turn"}, (0, 0)
    for a in acts:
        if a.get("type") != "play" or a.get("card") not in by_index:
            continue
        c = by_index[a["card"]]
        # the host's target is the enemy's combat index; the planner's simulation wants its position in the list
        pos = next((i for i, e in enumerate(enemies) if e.ref == a.get("target")), None) if a.get("target") is not None else None
        if a.get("target") is not None and pos is None:
            continue
        o = pt.simulate([c], [pos], player, enemies)
        if not o:
            continue
        key = (o["dealt"], o.get("block", 0))
        if key > best_key:
            best, best_key = a, key
    return best


def cmd_baselines(a):
    """The rule planner, a greedy and a random policy on the same fights from nothing (P8.E1.S2)."""
    import random
    sys.path.insert(0, str(PROJECT / "tools"))
    import plan_turn as pt
    pols = ["planner", "greedy", "random"]
    rows = []
    with Sim() as sim:
        encs = [e["id"] for e in sim.encounters() if e["room_type"] in a.rooms.split(",") and not e["weak"]]
        picked = encs[:: max(1, len(encs) // a.fights)][: a.fights]
        for enc in picked:
            for s in range(a.seeds):
                res = {}
                for pol in pols:
                    rng = random.Random(s)
                    obs = sim.new_fight(enc, seed=f"SEARCH{s:06d}", sample_seed=s + 1)["obs"]
                    for _ in range(400):
                        if obs["status"] != "in_progress" or obs.get("blocked"):
                            break
                        act = planner_action(pt, obs, "balanced") if pol == "planner" else baseline_action(sim, pt, obs, pol, rng)
                        try:
                            obs = sim.step(act)
                        except SimError:
                            obs = sim.step({"type": "end_turn"})
                    res[pol] = (obs["status"], obs["combat"]["player"]["current_hp"], _enemy_hp_left(obs))
                rows.append((enc, s, res))
                print(f"{enc:34s} s{s} " + " | ".join(f"{p} {res[p][0]} {res[p][1]}" for p in pols), flush=True)
    n = len(rows)
    L = ["# Baseline policies on fights from nothing", "",
         f"Generated by `tools/sim.py baselines` on {time.strftime('%Y-%m-%d %H:%M')}: the same fights as `tools/sim.py search` "
         f"(room types {a.rooms}, {a.fights} encounters × {a.seeds} seeds, Ironclad starting deck, 80 HP). Exploratory, not the "
         f"benchmark set (P8.E1.S1).", ""]
    for p in pols:
        wins = sum(1 for r in rows if r[2][p][0] == "won")
        hp = sum(r[2][p][1] for r in rows) / max(n, 1)
        L.append(f"- {p}: won {wins} of {n}, mean HP left {hp:.1f}")
    L += ["", "| Encounter | Seed | " + " | ".join(pols) + " |", "|---|---|" + "---|" * len(pols)]
    L += [f"| {r[0]} | {r[1]} | " + " | ".join(f"{r[2][p][0]} {r[2][p][1]}" for p in pols) + " |" for r in rows]
    out = PROJECT / "reports" / "phase8" / "baselines.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n")
    print(f"Report: {out.relative_to(PROJECT)}")
    return 0


def planner_action(pt, obs, mode, potions=None):
    """The rule planner's next action for a simulated observation: the first play of its top plan, or end the turn.
    Potions are used only when `potions` names the room type (their price in the planner's ranking)."""
    if obs.get("choice"):  # the planner has no view on card choices yet: take the first options
        return {"type": "choose", "cards": list(range(max(1, obs["choice"]["min"]) if obs["choice"]["max"] else 0))}
    hand, player, enemies = _hand_for(pt, obs, potions)
    if not enemies or not hand:
        return {"type": "end_turn"}
    best = _rank(pt, pt.plans(hand, player, enemies), mode, potions)[0]
    seq = best.get("seq") or []
    if not seq:
        return {"type": "end_turn"}
    return _act_from(*seq[0])


def cmd_planner(a):
    """tools/plan_turn.py as the policy inside the simulator (a first baseline for Phase 8)."""
    sys.path.insert(0, str(PROJECT / "tools"))
    import plan_turn as pt
    with Sim() as sim:
        sim.load(a.replay or default_replay())
        pts = sim.points()
        k = pts[a.point] if a.point < len(pts) else pts[0]
        outcomes, t0, steps, refused = [], time.time(), 0, 0
        for seed in range(1, a.seeds + 1):
            obs = sim.reset(k, seed=seed)["obs"]
            for _ in range(600):
                if obs["status"] != "in_progress" or obs.get("blocked"):
                    break
                act = planner_action(pt, obs, a.mode)
                try:
                    obs = sim.step(act)
                except SimError:
                    refused += 1
                    obs = sim.step({"type": "end_turn"})
                steps += 1
            outcomes.append((obs["status"], obs["combat"]["player"]["current_hp"], obs["turn"], obs.get("blocked")))
        dt = time.time() - t0
    won = [o for o in outcomes if o[0] == "won"]
    stuck = sum(1 for o in outcomes if o[3])
    print(f"planner ({a.mode}) from decision point {a.point} (event {k}), {a.seeds} sampled futures: won {len(won)}, lost {sum(1 for o in outcomes if o[0] == 'lost')}, "
          f"blocked by a prompt the host does not handle {stuck}; final HP when won: {sorted(o[1] for o in won)}")
    print(f"{steps} decisions in {dt:.1f} s ({1000 * dt / max(1, steps):.1f} ms per decision: planner plus simulator); actions the host refused: {refused}")
    return 0


def cmd_sweep(a):
    """P7.E4.S1: every encounter in the game started from nothing and played to the end by a random policy. Finds
    encounters the host cannot start or finish (a missing stub, a prompt it does not handle)."""
    rows = []
    t0 = time.time()
    with Sim() as sim:
        encs = sorted(sim.encounters(), key=lambda e: (e["room_type"], e["id"]))
        if a.only:
            encs = [e for e in encs if a.only in e["id"]]
        for e in encs:
            res = []
            for k in range(a.rollouts):
                try:
                    sim.new_fight(e["id"], seed=f"SWEEP{k:07d}", sample_seed=k + 1, deck=a.deck.split(",") if a.deck else None)
                    out = sim.rollout(policy="random", seed=k + 1, max_steps=600)
                    o = out["obs"]
                    if out.get("game_exceptions"):
                        res.append("ERROR game exception: " + out.get("last_exception", "")[:110])
                        continue
                    res.append("blocked" if o.get("blocked") else ("unfinished" if o["status"] == "in_progress" else o["status"]))
                except SimError as err:
                    res.append("ERROR " + str(err).split("(")[0][:110])
            rows.append((e, res))
            bad = [r for r in res if r not in ("won", "lost")]
            print(f"{'ok  ' if not bad else 'FAIL'} {e['room_type']:8s} {e['id']:38s} {dict((x, res.count(x)) for x in sorted(set(res)))}"[:230])
    ok = sum(1 for _, res in rows if all(r in ("won", "lost") for r in res))
    REPORTS.mkdir(parents=True, exist_ok=True)
    L = ["# Encounter sweep: every fight started from nothing", "",
         f"Generated by `tools/sim.py sweep` on {time.strftime('%Y-%m-%d')}: each encounter started from a new run (Ironclad, "
         f"{'deck ' + a.deck if a.deck else 'starting deck'}) and played to the end by a random policy, {a.rollouts} time(s) with different seeds. "
         "A fight passes when every attempt ends in a win or a loss. Losses are expected: the policy is random.", "",
         f"**{ok} of {len(rows)} encounters pass.** Total time {time.time() - t0:.0f} s.", "",
         "| Room | Encounter | Results |", "|---|---|---|"]
    L += [f"| {e['room_type']} | {e['id']} | {', '.join(f'{x} x{res.count(x)}' for x in sorted(set(res)))} |" for e, res in rows]
    (REPORTS / "encounter-sweep.md").write_text("\n".join(L) + "\n")
    print(f"{ok} of {len(rows)} encounters pass. Report: reports/phase7/encounter-sweep.md")
    return 0 if ok == len(rows) else 1


def run_policy(pt, obs, acts, rng, mode="safe", potions=None):
    """A simple whole-run policy for exercising the simulator (not a strong player): the rule planner in fights, the
    first card of each card reward, rest when below 60% HP, smith otherwise, the first move on the map, and the first
    option elsewhere. Every decision uses only the observation (FP-1). With `potions` (the fight's room type) the
    planner may drink potions at that room's price."""
    scr = obs["screen"]
    if scr == "combat":
        a = planner_action(pt, obs, mode, potions)
        if a in acts:
            return a
        # the legal actions carry extra fields (card_id, potion_id): match the planner's action on what it decides,
        # the target included (until 2026-11-21 the target was ignored here, so multi-enemy fights hit the first enemy)
        key = "slot" if a.get("type") == "potion" else "card"
        same = [x for x in acts if x.get("type") == a.get("type") and x.get(key) == a.get(key)]
        exact = [x for x in same if x.get("target") == a.get("target")]
        return (exact or same)[0] if same else next(x for x in acts if x["type"] == "end_turn")
    if scr == "choice":
        picks = [x for x in acts if x.get("cards")]
        cards = [x for x in picks if not str(x.get("card_id", "")).startswith("alt:")]
        return (cards or picks or acts)[0]
    if scr == "rest":
        hp, mx = obs["player"]["hp"], obs["player"]["max_hp"]
        want = "HEAL" if hp < 0.6 * mx else "SMITH"
        for x in acts:
            if str(x.get("option", "")).upper() == want:
                return x
        return acts[0]
    if scr == "shop":
        return next(x for x in acts if x["type"] == "leave")
    if scr == "rewards":
        take = [x for x in acts if x["type"] == "take_reward"]
        return take[0] if take else acts[0]
    if scr == "treasure":
        return acts[0]
    return acts[0]


def cmd_runs(a):
    """Whole runs in the simulator, each from a new seed, played by run_policy. Reports floors reached and speed."""
    sys.path.insert(0, str(PROJECT / "tools"))
    import random
    import plan_turn as pt
    rows, t0 = [], time.time()
    screens = {}
    with Sim() as sim:
        t_ready = time.time()
        for k in range(a.count):
            seed = f"{a.prefix}{k:06d}"
            rng = random.Random(k)
            t1 = time.time()
            try:
                spec = {"seed": seed, "character": "IRONCLAD", "ascension": a.ascension}
                if a.test_max_hp:
                    spec["test_max_hp"] = a.test_max_hp  # flow test only: a weak driver reaches every room type
                obs = sim.call(cmd="new_run", spec=spec, timeout=120)["obs"]
            except SimError as e:
                rows.append((seed, "error", 0, 0, 0, 0, str(e)[:120])); print(f"{seed}: ERROR {str(e)[:200]}"); continue
            steps, reason = 0, ""
            while steps < a.max_steps:
                scr = obs["screen"]
                screens[scr] = screens.get(scr, 0) + 1
                if scr == "game_over":
                    break
                acts = sim.call(cmd="run_legal")["actions"]
                if not acts:
                    reason = f"no legal action on {scr}: " + "; ".join(sim.call(cmd="diag", last=2)["problems"])[:160]
                    break
                try:
                    obs = sim.call(cmd="run_step", action=run_policy(pt, obs, acts, rng), timeout=120)["obs"]
                except SimError as e:
                    reason = f"step failed on {scr}: {str(e)[:160]}"
                    break
                steps += 1
            won = obs["screen"] == "game_over" and obs["player"]["hp"] > 0
            result = "won" if won else ("died" if obs["screen"] == "game_over" else ("stuck" if reason else "step limit"))
            rows.append((seed, result, obs["act"], obs["floor"], steps, time.time() - t1, reason))
            print(f"{seed}: {result:10s} act {obs['act']} floor {obs['floor']:2d} HP {obs['player']['hp']:3d} steps {steps:4d} {time.time() - t1:5.1f} s {reason}", flush=True)
    dt = time.time() - t0
    play = sum(r[5] for r in rows)
    decisions = sum(r[4] for r in rows)
    REPORTS.mkdir(parents=True, exist_ok=True)
    done = [r for r in rows if r[1] in ("won", "died")]
    L = ["# Whole runs in the simulator", "",
         f"Generated by `tools/sim.py runs` on {time.strftime('%Y-%m-%d %H:%M')}: {len(rows)} runs, each from a new seed (`{a.prefix}000000` on), "
         f"{'**Flow test: started with max HP ' + str(a.test_max_hp) + ' (test-only switch); results say nothing about play.** ' if a.test_max_hp else ''}"
         f"Ironclad A{a.ascension}, played by `run_policy` (the rule planner in fights, simple rules elsewhere; it is a test driver, not a strong player).", "",
         f"- Finished (won or died): {len(done)} of {len(rows)}; won {sum(1 for r in rows if r[1] == 'won')}",
         f"- Stuck or failed: {sum(1 for r in rows if r[1] in ('stuck', 'error'))}; stopped at the step limit: {sum(1 for r in rows if r[1] == 'step limit')}",
         f"- Total time {dt:.0f} s, of which host start {t_ready - t0:.0f} s; {decisions} decisions; "
         f"{1000 * play / max(decisions, 1):.1f} ms per decision including the Python driver; {3600 * len(rows) / max(play, 1):.0f} runs per hour on one host "
         + ("(most runs ended early, so this overstates the rate for full-length runs)" if sum(r[3] for r in rows) < 30 * max(len(rows), 1) else ""),
         f"- Screens visited (decisions): " + ", ".join(f"{k} {v}" for k, v in sorted(screens.items(), key=lambda x: -x[1])), "",
         "| Seed | Result | Act | Floor | Decisions | Seconds | Note |", "|---|---|---|---|---|---|---|"]
    L += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]:.1f} | {r[6]} |" for r in rows]
    (REPORTS / (a.report or "whole-runs.md")).write_text("\n".join(L) + "\n")
    print(f"{len(done)} of {len(rows)} runs finished in {dt:.0f} s. Report: reports/phase7/{a.report or 'whole-runs.md'}")
    return 0


TYPE_MAP = {"ancient": "Ancient", "monster": "Monster", "unknown": "Unknown", "shop": "Shop", "rest_site": "RestSite",
            "treasure": "Treasure", "elite": "Elite", "boss": "Boss"}


def strip_id(x):
    return str(x or "").split(".", 1)[-1]


def find_path(mp, types):
    """A path from the act's starting point whose point types follow `types` (the recorded floors after the Ancient)."""
    pts = {(p["col"], p["row"]): p for p in mp["points"]}
    start = tuple(mp["start"])

    def dfs(at, k):
        if k == len(types):
            return []
        for c in sorted(pts[at]["children"], key=lambda c: c[0]):
            c = tuple(c)
            if pts[c]["type"] == types[k]:
                rest = dfs(c, k + 1)
                if rest is not None:
                    return [c] + rest
        return None
    return dfs(start, 0)


def cmd_runcheck(a):
    """Stage 3: a recorded run replayed from its seed in the simulator, following the recorded choices. Compares what
    the game generated (map, encounters, card rewards, shop stock, chest relics, events, Ancient options) floor by floor.
    Fights are played by the rule planner, so HP differs from the real run; the comparison is about generation."""
    sys.path.insert(0, str(PROJECT / "tools"))
    import random
    import plan_turn as pt
    rec = json.loads(Path(a.run_file).read_text())
    seed, asc = rec["seed"], rec.get("ascension", 0)
    floors = [f for act in rec["map_point_history"] for f in act]
    acts_types = [[TYPE_MAP[f["map_point_type"]] for f in act] for act in rec["map_point_history"]]
    rows = {}   # floor -> list of (check, ok, detail)

    def note(fl, check, ok, detail=""):
        rows.setdefault(fl, []).append((check, ok, detail))

    rng = random.Random(0)
    with Sim() as sim:
        spec = {"seed": seed, "character": "IRONCLAD", "ascension": asc}
        if a.test_max_hp:
            spec["test_max_hp"] = a.test_max_hp
        replays = sorted((REPLAYS / Path(a.run_file).parent.name).glob("*.mcr"))
        if replays and not a.all_unlocks:
            spec["unlocks_from"] = str(replays[0])   # the profile's unlock state at the time of the run (FI-5)
        obs = sim.call(cmd="new_run", spec=spec, timeout=120)["obs"]
        unlock_source = obs.get("unlocks")
        path, path_act, used = [], 0, {}
        steps = 0
        while obs["screen"] != "game_over" and steps < 6000:
            steps += 1
            act_list = rec["map_point_history"][obs["act"] - 1] if obs["act"] <= len(rec["map_point_history"]) else []
            k = obs["act_floor"] - 1
            fl = sum(len(x) for x in rec["map_point_history"][:obs["act"] - 1]) + obs["act_floor"]   # floor number as recorded
            r = act_list[k] if 0 <= k < len(act_list) else {"player_stats": [{}], "rooms": [{}], "map_point_type": "?"}
            ps = r["player_stats"][0]
            q = used.setdefault(fl, {"cards": [c for c in ps.get("card_choices", [])], "events": list(ps.get("event_choices", [])), "checked": set()})
            scr = obs["screen"]
            acts = sim.call(cmd="run_legal")["actions"]
            if a.rng_trace and (fl, scr) != q.get("last_rng"):
                q["last_rng"] = (fl, scr)
                print(f"  [rng] floor {fl} {scr}: " + " ".join(f"{k}={v}" for k, v in sim.call(cmd="debug_rng")["counters"].items() if v))
            if a.trace and fl in a.trace and scr != "combat":
                print(f"  [floor {fl}] {scr}: event={obs.get('event', {}).get('options') if obs.get('event') else None} choice={obs.get('choice')} rewards={obs.get('rewards')} acts={[x.get('type') + ':' + str(x.get('card_id') or x.get('key') or x.get('reward') or '') for x in acts][:8]}")
            if not acts:
                note(fl, "stuck", False, scr); break
            act = None
            if "room" not in q["checked"] and scr != "map":
                q["checked"].add("room")
                want = strip_id(r["rooms"][0].get("model_id")) if r.get("rooms") else ""
                got = obs.get("encounter") or obs.get("event_id") or ""
                if want.startswith(("EVENT", )) or r["rooms"][0].get("room_type") in ("event", "monster", "elite", "boss"):
                    note(fl, "room", want == got, f"recorded {want}, simulated {got}")
            if scr == "event":
                opts = obs["event"]["options"]
                if obs["event"]["ancient"]:
                    pick = next((x["choice"] for x in ps.get("relic_choices", []) if x.get("was_picked")), None)
                    if "ancient" not in q["checked"]:
                        q["checked"].add("ancient")
                        offered = sorted(strip_id(x["TextKey"]) for x in ps.get("ancient_choice", []))
                        note(fl, "ancient options", offered == sorted(o["relic"] or "" for o in opts), f"recorded {offered}, simulated {sorted(o['relic'] or '' for o in opts)}")
                    idx = next((i for i, o in enumerate(opts) if o["relic"] == strip_id(pick)), 0)
                else:
                    idx = 0
                    if q["events"]:
                        key = q["events"][0]["title"]["key"].rsplit(".title", 1)[0]
                        m = [i for i, o in enumerate(opts) if o["key"] == key]
                        if m:
                            idx = m[0]
                            q["events"].pop(0)
                act = next((x for x in acts if x.get("index") == idx and x["type"] == "event_option"), acts[0])
            elif scr == "choice":
                ch = obs["choice"]
                labels = ch["options"]
                want = None
                if ch["kind"] == "CardReward":
                    if "cards" not in q["checked"] and q["cards"]:
                        offer = [strip_id(c["card"]["id"]) for c in q["cards"][:3]]
                        shown = [x.rstrip("+") for x in labels if not x.startswith("alt:")]
                        picked = next((strip_id(c["card"]["id"]) for c in q["cards"][:3] if c.get("was_picked")), None)
                        # the run file lists the picked card first, the others in the order shown
                        as_recorded = ([picked] + [x for x in shown if x != picked]) if picked in shown else shown
                        note(fl, "card reward", offer == as_recorded, f"recorded {offer}, simulated {shown}")
                        q["cards"] = q["cards"][3:]
                        want = picked
                    else:
                        want = None
                else:
                    pool = [strip_id(x.get("id") if isinstance(x, dict) else x) for x in ps.get("upgraded_cards", []) + ps.get("cards_removed", [])]
                    pool += [strip_id(x["original_card"]["id"]) for x in ps.get("cards_transformed", [])]
                    pool += [strip_id(x["id"]) for x in ps.get("cards_gained", [])]
                    pool += [strip_id(x["choice"]) for x in ps.get("relic_choices", []) if x.get("was_picked")]
                    want = next((p for p in pool if any(l.rstrip("+") == p for l in labels)), None)
                i = next((i for i, l in enumerate(labels) if l.rstrip("+") == want), None) if want else None
                if i is not None:
                    act = next((x for x in acts if x.get("cards") == [i]), acts[0])
                else:
                    act = next((x for x in acts if x.get("cards") == []), None) or acts[0]
            elif scr == "rewards":
                wanted_potions = {strip_id(x["choice"]) for x in ps.get("potion_choices", []) if x.get("was_picked")}
                take = None
                for x in acts:
                    if x["type"] != "take_reward":
                        continue
                    rw = obs["rewards"][x["index"]]
                    if rw["type"] == "PotionReward" and rw["detail"] not in wanted_potions:
                        continue
                    take = x
                    break
                act = take or next((x for x in acts if x["type"] == "skip_rewards"), acts[0])
            elif scr == "combat":
                act = run_policy(pt, obs, acts, rng)
            elif scr == "rest":
                want = (ps.get("rest_site_choices") or ["HEAL"])[0]
                act = next((x for x in acts if str(x.get("option", "")).upper() == want), acts[0])
            elif scr == "shop":
                if "shop" not in q["checked"]:
                    q["checked"].add("shop")
                    stock = obs.get("shop", [])
                    rel = sorted(s["item"][6:] for s in stock if s["item"].startswith("relic:"))
                    pot = sorted(s["item"][7:] for s in stock if s["item"].startswith("potion:"))
                    rr = sorted(strip_id(x["choice"]) for x in ps.get("relic_choices", []))
                    rp = sorted(strip_id(x["choice"]) for x in ps.get("potion_choices", []))
                    note(fl, "shop relics", rel == rr, f"recorded {rr}, simulated {rel}")
                    note(fl, "shop potions", pot == rp, f"recorded {rp}, simulated {pot}")
                    cards = sorted(s["item"][5:] for s in stock if s["item"].startswith("card:"))
                    # the run file keeps the shop cards not bought in card_choices and the bought ones in cards_gained
                    rc_ = sorted([strip_id(c["card"]["id"]) for c in ps.get("card_choices", [])] + [strip_id(c["id"]) for c in ps.get("cards_gained", [])])
                    if rc_:
                        note(fl, "shop cards", cards == rc_, f"recorded {rc_}, simulated {cards}")
                        q["cards"] = []
                buys = {"relic:" + strip_id(x) for x in ps.get("bought_relics", [])} | {"potion:" + strip_id(x) for x in ps.get("bought_potions", [])}
                buys |= {"card:" + strip_id(x) for x in ps.get("bought_colorless", [])}
                buys |= {"card:" + strip_id(x["id"]) for x in ps.get("cards_gained", [])}   # character cards bought here
                if ps.get("cards_removed"):
                    buys.add("removal")
                done = q.setdefault("bought", set())
                act = next((x for x in acts if x["type"] == "buy" and x["item"] in buys - done), None)
                if act:
                    done.add(act["item"])
                else:
                    act = next(x for x in acts if x["type"] == "leave")
            elif scr == "treasure":
                if any(x["type"] == "open_chest" for x in acts):
                    act = next(x for x in acts if x["type"] == "open_chest")
                else:
                    if "chest" not in q["checked"]:
                        q["checked"].add("chest")
                        rr = sorted(strip_id(x["choice"]) for x in ps.get("relic_choices", []))
                        note(fl, "chest relics", sorted(obs.get("chest", [])) == rr, f"recorded {rr}, simulated {sorted(obs.get('chest', []))}")
                    pick = next((strip_id(x["choice"]) for x in ps.get("relic_choices", []) if x.get("was_picked")), None)
                    act = next((x for x in acts if x.get("relic") == pick), None) or next(x for x in acts if x["type"] == "leave")
            elif scr == "map":
                if any(x["type"] == "next_act" for x in acts):
                    act = next(x for x in acts if x["type"] == "next_act")
                else:
                    if path_act != obs["act"]:
                        mp = sim.call(cmd="map")["map"]
                        path = find_path(mp, acts_types[obs["act"] - 1][1:]) or []
                        if path and mp.get("here") is None:
                            path = [tuple(mp["start"])] + path   # acts 2 and 3: walk onto the Ancient first
                        note(fl, f"act {obs['act']} map path", bool(path), f"{len(path)} floors matching the recorded room types")
                        path_act = obs["act"]
                    if path:
                        c, rrow = path.pop(0)
                        obs = sim.call(cmd="move_to", col=c, row=rrow, timeout=120)["obs"]
                        continue
                    act = acts[0]
            try:
                obs = sim.call(cmd="run_step", action=act or acts[0], timeout=120)["obs"]
            except SimError as e:
                note(fl, "step", False, str(e)[:160])
                break
        final = obs
    checks = [(fl, c, ok, d) for fl in sorted(rows) for c, ok, d in rows[fl]]
    good = sum(1 for x in checks if x[2])
    REPORTS.mkdir(parents=True, exist_ok=True)
    L = ["# Run-level fidelity: a recorded run replayed from its seed", "",
         f"Generated by `tools/sim.py runcheck` on {time.strftime('%Y-%m-%d %H:%M')}. Recorded run: `{Path(a.run_file).name}` (seed {seed}, A{asc}, "
         f"{len(floors)} floors, won). The simulator starts a new run from the same seed and follows the recorded choices (Ancient relic, path, "
         "event options, card picks, rest-site choices, purchases, chest relic). Fights are played by the rule planner, so HP and the course "
         "of each fight differ from the real run; the checks compare what the game generated." +
         (f" **Flow aid: started with max HP {a.test_max_hp} (test-only switch) so the replay is not cut short by a lost fight.**" if a.test_max_hp else ""), "",
         f"Unlock state: {unlock_source}.", "",
         f"**{good} of {len(checks)} checks match.** Simulated run ended on floor {final['floor']} ({final['screen']}).", "",
         "| Floor | Check | Match | Detail |", "|---|---|---|---|"]
    L += [f"| {fl} | {c} | {'yes' if ok else '**no**'} | {d} |" for fl, c, ok, d in checks]
    (REPORTS / "run-fidelity.md").write_text("\n".join(L) + "\n")
    for fl, c, ok, d in checks:
        if not ok:
            print(f"floor {fl}: {c} differs: {d}")
    print(f"{good} of {len(checks)} checks match; simulated run ended on floor {final['floor']} ({final['screen']}). Report: reports/phase7/run-fidelity.md")
    return 0 if good == len(checks) else 1


def cmd_fidelity(a):
    """P7.E5.S1: replay every recorded fight in fidelity mode and compare the host's states with the game's. Recordings
    from another game build (their header names the build) are skipped and counted, not failed."""
    files, skipped = installed_build_replays()
    for f, v in skipped:
        print(f"skip {f}: recorded on {v}, not the installed build")
    rows = []
    for f in files:
        r = subprocess.run([str(PROJECT / "sim" / "run.sh"), "replay", str(f), "once"], cwd=PROJECT, capture_output=True, text=True, timeout=600)
        out = r.stdout
        m = re.search(r"checksums: (\d+) generated, (\d+) states equal to the game's, (\d+) different, (\d+) without a recorded partner; recorded (\d+)", out)
        ev = re.search(r"events applied (\d+) of (\d+).*combat in progress: (\w+); final HP (\d+)/(\d+)", out)
        ver = re.search(r"replay (\S+) (\S+); model-id hash replay (\d+), host (\d+): (\w+)", out)
        ok = bool(m and ev and int(m.group(3)) == 0 and int(m.group(2)) == int(m.group(1)) > 0 and ev.group(1) == ev.group(2))
        rows.append((f.relative_to(REPLAYS), ver.group(1) if ver else "?", ver.group(5) if ver else "?", ev.groups() if ev else None, m.groups() if m else None, ok,
                     "" if ok else (re.search(r"FAIL .*", out) or re.search(r"STATE DIFFERS[^\n]*", out) or [out[-200:]])[0] if not ok else ""))
        print(f"{'ok  ' if ok else 'FAIL'} {f.relative_to(REPLAYS)}: {m.group(2) if m else '?'} of {m.group(1) if m else '?'} states equal, final HP {ev.group(4) if ev else '?'}")
    # Second check per fight: the same recording replayed with the host's own play and end-turn actions (the path
    # decision mode uses) must end the same way.
    own = {}
    if files:
        with Sim() as sim:
            for f in files:
                try:
                    sim.load(f)
                    own[f.relative_to(REPLAYS)] = sim.call(cmd="selfcheck", timeout=120)["result"]
                except SimError as e:
                    own[f.relative_to(REPLAYS)] = {"status": "error: " + str(e)[:80], "hp": None, "own_actions": 0}
    for i, r in enumerate(rows):
        o = own.get(r[0], {})
        # the recorded ending: lost at 0 HP, won when the fight is over with HP left, else still in progress
        expected = None if not r[3] else ("lost" if r[3][3] == "0" else ("won" if r[3][2] == "False" else "in_progress"))
        same_end = bool(r[3]) and o.get("hp") is not None and str(o["hp"]) == r[3][3] and o.get("status") == expected
        rows[i] = r[:5] + (r[5] and same_end, r[6] or ("" if same_end else f"own-action replay ended differently: {o}")) + (o,)
        print(f"{'ok  ' if same_end else 'FAIL'} {r[0]}: own-action replay {o.get('status')} at HP {o.get('hp')} ({o.get('own_actions')} own actions)")
    REPORTS.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for r in rows if r[5])
    L = ["# Fidelity of the simulator host against recorded fights", "",
         f"Generated by `tools/sim.py fidelity` on {time.strftime('%Y-%m-%d')}. Each recorded fight (`data/sim/replays/`, the game's own `latest.mcr` "
         "kept by `tools/play_turn.py`) is replayed in fidelity mode with its true random state. The host's full combat state at every turn boundary is "
         "compared, as text with the anonymised player id masked, with the state the game stored in the recording.", "",
         f"**{passed} of {len(rows)} recorded fights reproduce exactly.** Phase 7 exit gate: at least 99% of at least 100 fights (M11).", "",
         "Not compared: the checkpoints the game takes after every single action (the host does not produce them).", "",
         f"Sources: the Agent's runs (kept by `tools/play_turn.py`) and the Player's own play (kept read-only by `tools/keep_replays.py`, folders "
         f"`player-*`). Skipped: {len(skipped)} recording(s) from another game build"
         + (" (" + ", ".join(f"{f} on {v}" for f, v in skipped) + ")." if skipped else "."), "",
         "A second replay uses the host's own card-play and end-turn actions, the path decision mode steps with, and must end in the same result.", "",
         "| Fight | Game | Model ids | Events applied | Fight over | Final HP | States equal | Different | Own-action replay | Result |", "|---|---|---|---|---|---|---|---|---|---|"]
    for name, ver, hashes, ev, m, ok, why, o in rows:
        L.append(f"| {name} | {ver} | {hashes} | {ev[0] + ' of ' + ev[1] if ev else '?'} | {'yes' if ev and ev[2] == 'False' else 'no'} | {ev[3] + '/' + ev[4] if ev else '?'} | "
                 f"{m[1] + ' of ' + m[0] if m else '?'} | {m[2] if m else '?'} | {o.get('status')} at HP {o.get('hp')}, {o.get('own_actions')} own actions | {'exact' if ok else 'FAILED: ' + why[:120]} |")
    (REPORTS / "fidelity.md").write_text("\n".join(L) + "\n")
    print(f"{passed} of {len(rows)} fights exact. Report: reports/phase7/fidelity.md")
    return 0 if passed == len(rows) and rows else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    rc = sub.add_parser("runcheck")
    rc.set_defaults(fn=cmd_runcheck)
    rc.add_argument("run_file", nargs="?", default=str(PROJECT / "runs" / "2026-11-19-1ZWEN4BFQUZL" / "run.run"))
    rc.add_argument("--test-max-hp", type=int)
    rc.add_argument("--all-unlocks", action="store_true", help="ignore the profile's unlock state from its recorded fights")
    rc.add_argument("--trace", type=int, nargs="*", help="print every non-combat decision on these floors")
    rc.add_argument("--rng-trace", action="store_true", help="fidelity debugging: print the random-stream counters at each screen")
    rp = sub.add_parser("runs")
    rp.set_defaults(fn=cmd_runs)
    rp.add_argument("--count", type=int, default=5)
    rp.add_argument("--prefix", default="SIMRUN")
    rp.add_argument("--ascension", type=int, default=0)
    rp.add_argument("--max-steps", type=int, default=4000)
    rp.add_argument("--test-max-hp", type=int, help="flow test only: start with this max HP so a weak driver reaches every room type")
    rp.add_argument("--report", help="report file name under reports/phase7/")
    sw = sub.add_parser("sweep")
    sw.set_defaults(fn=cmd_sweep)
    sw.add_argument("--rollouts", type=int, default=2)
    sw.add_argument("--only", help="substring of the encounter id")
    sw.add_argument("--deck", help="comma-separated card ids replacing the starting deck")
    bl = sub.add_parser("baselines")
    bl.set_defaults(fn=cmd_baselines)
    bl.add_argument("--fights", type=int, default=12)
    bl.add_argument("--seeds", type=int, default=3)
    bl.add_argument("--rooms", default="Monster,Elite")
    se = sub.add_parser("search")
    se.set_defaults(fn=cmd_search)
    se.add_argument("--fights", type=int, default=12, help="number of encounters")
    se.add_argument("--seeds", type=int, default=2)
    se.add_argument("--k", type=int, default=3, help="re-sampled worlds per candidate")
    se.add_argument("--top", type=int, default=2, help="plans per planner mode")
    se.add_argument("--mode", default="balanced")
    se.add_argument("--rooms", default="Monster,Elite,Boss", help="room types of the encounters, comma-separated")
    se.add_argument("--report", default="search-first-experiment.md")
    sb = sub.add_parser("sandbox")
    sb.set_defaults(fn=cmd_sandbox)
    sb.add_argument("--fights", type=int, default=20)
    sb.add_argument("--runs", type=int, default=5)
    rc = sub.add_parser("runclone")
    rc.set_defaults(fn=cmd_runclone)
    rc.add_argument("--runs", type=int, default=3)
    rc.add_argument("--canary", type=int, default=20)
    cl = sub.add_parser("clone")
    cl.set_defaults(fn=cmd_clone)
    cl.add_argument("--fights", type=int, default=12)
    cl.add_argument("--from-save", action="store_true", help="rebuild the fights from fights inside simulated runs (fight_from_save)")
    cl.add_argument("--from-run", action="store_true", help="rebuild the fights inside simulated runs through the run clone (fight_from_run)")
    for name, fn in (("smoke", cmd_smoke), ("fairplay", cmd_fairplay), ("planner", cmd_planner), ("fidelity", cmd_fidelity)):
        p = sub.add_parser(name)
        p.set_defaults(fn=fn)
        if name != "fidelity":
            p.add_argument("replay", nargs="?")
        if name in ("fairplay", "planner"):
            p.add_argument("--seeds", type=int, default=12)
        if name == "planner":
            p.add_argument("--point", type=int, default=0, help="index of the decision point to start from")
            p.add_argument("--mode", choices=["safe", "balanced"], default="safe")
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
