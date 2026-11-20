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

    def __init__(self, start_timeout=240, log=False):
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


def default_replay():
    files = sorted(REPLAYS.glob("*/*.mcr"))
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
    print(f"{sum(results)} of {len(results)} fair-play checks passed")
    return 0 if all(results) else 1


def planner_action(pt, obs, mode):
    """The rule planner's next action for a simulated observation: the first play of its top plan, or end the turn."""
    if obs.get("choice"):  # the planner has no view on card choices yet: take the first options
        return {"type": "choose", "cards": list(range(max(1, obs["choice"]["min"]) if obs["choice"]["max"] else 0))}
    hand, player, enemies = pt.from_state(obs)
    hand = [c for c in hand if not c.potion]  # potions are not steppable in the host yet
    if not enemies or not hand:
        return {"type": "end_turn"}
    best = pt.rank(pt.plans(hand, player, enemies), mode)[0]
    seq = best.get("seq") or []
    if not seq:
        return {"type": "end_turn"}
    card, ref = seq[0]
    act = {"type": "play", "card": card.index}
    if card.target == "AnyEnemy" and ref is not None:
        act["target"] = ref
    return act


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


def cmd_fidelity(a):
    """P7.E5.S1: replay every recorded fight in fidelity mode and compare the host's states with the game's."""
    files = sorted(REPLAYS.glob("*/*.mcr"))
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
        same_end = bool(r[3]) and o.get("hp") is not None and str(o["hp"]) == r[3][3] and (o["status"] == "won") == (r[3][2] == "False")
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
