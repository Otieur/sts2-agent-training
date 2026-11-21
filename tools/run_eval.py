#!/usr/bin/env python3
"""Decision-time evaluation of run-level choices by sampled rollouts (decision 0004 steps 3-4).

At a decision point the run host exports its state (the room-entry save plus the run actions since). For each option,
an evaluation host rebuilds that state with the hidden future re-sampled (`run_from_save` with a sample seed; FP-9,
FP-16), takes the option, and plays on with a fast rollout policy (rule planner in fights, the rule tools elsewhere)
to the end of the current act or death. The same sample seeds are used for every option (common random numbers), so
options are compared on the same sampled futures. The option with the best mean rollout value is chosen.

Rollout value: floors climbed from the decision point, plus, if the act's boss is beaten, 5 and 5 times the HP fraction
left. Only what the player can see is used: the rollouts play in worlds whose unseen parts are freshly sampled.

    python3 -I tools/run_eval.py --demo --seed RB90000001 --ascension 5     # one run, card rewards by rollouts, timings
"""
import argparse
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim as S  # noqa: E402


def rollout_value(start, end, start_act):
    climbed = (end.get("floor") or 0) - (start.get("floor") or 0)
    alive = end["screen"] != "game_over" or end["player"]["hp"] > 0
    beat_boss = alive and (end.get("act") or 1) > start_act
    bonus = 5 + 5 * end["player"]["hp"] / max(1, end["player"]["max_hp"]) if beat_boss else 0
    return climbed + bonus


class RolloutEvaluator:
    """Owns an evaluation host. `evaluate(run_sim, obs, options)` returns the mean rollout value of each option."""

    def __init__(self, k=6, max_steps=3000, rollout_policy="draft+shop+rest", seed_base=7_700_000):
        self.k, self.max_steps, self.seed_base = k, max_steps, seed_base
        self.rollout_policy = rollout_policy
        self.host = None
        self.stats = {"decisions": 0, "rollouts": 0, "errors": 0, "seconds": 0.0}
        self._n = 0

    def _host(self):
        if self.host is None:
            self.host = S.Sim()
            self.host.__enter__()
        return self.host

    def close(self):
        if self.host is not None:
            self.host.__exit__(None, None, None)
            self.host = None

    def evaluate(self, run_sim, obs, options):
        import run_bench as RB
        t0 = time.time()
        ex = run_sim.call(cmd="run_export")["export"]
        h = self._host()
        start_act = obs.get("act") or 1
        self._n += 1
        values = [[] for _ in options]
        for j in range(self.k):
            seed = self.seed_base + 1000 * self._n + j          # the same sampled futures for every option
            for i, opt in enumerate(options):
                try:
                    o = h.call(cmd="run_from_save", data=ex["save_b64"], actions=ex["actions"], test_hp=ex["test_hp"],
                               sample_seed=seed, timeout=120)["obs"]
                    o = h.call(cmd="run_step", action=opt, timeout=120)["obs"]
                    pol, rng = RB.Policy(self.rollout_policy), random.Random(seed)
                    for _ in range(self.max_steps):
                        if o["screen"] == "game_over" or (o.get("act") or 1) > start_act:
                            break
                        acts = h.call(cmd="run_legal")["actions"]
                        if not acts:
                            break
                        o = h.call(cmd="run_step", action=pol.act(o, acts, rng, h), timeout=120)["obs"]
                    values[i].append(rollout_value(obs, o, start_act))
                    self.stats["rollouts"] += 1
                except S.SimError:
                    self.stats["errors"] += 1
                    self.close()
                    h = self._host()
        self.stats["decisions"] += 1
        self.stats["seconds"] += time.time() - t0
        return [sum(v) / len(v) if v else None for v in values]


def card_reward_options(acts):
    """The options of a card reward: each card, and skip (taking none, as the draft scorer skips; the screen's own
    alternative skip button does the same with a different use of the random streams, so it is left out)."""
    cards = [x for x in acts if x.get("type") == "choose" and x.get("cards") and not str(x.get("card_id", "")).startswith("alt:")]
    skip = [x for x in acts if x.get("type") == "choose" and not x.get("cards")]
    return cards + skip[:1]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--seed", default="RB90000001")
    ap.add_argument("--ascension", type=int, default=5)
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--rewards", type=int, default=3, help="card rewards to evaluate in the demo")
    a = ap.parse_args(argv)
    import run_bench as RB
    ev = RolloutEvaluator(k=a.k)
    pol, rng = RB.Policy("draft+shop+rest"), random.Random(0)
    done = 0
    with S.Sim() as run:
        obs = run.call(cmd="new_run", spec={"seed": a.seed, "character": "IRONCLAD", "ascension": a.ascension}, timeout=120)["obs"]
        while obs["screen"] != "game_over" and done < a.rewards:
            acts = run.call(cmd="run_legal")["actions"]
            ch = obs.get("choice") or {}
            if obs["screen"] == "choice" and ch.get("kind") == "CardReward":
                opts = card_reward_options(acts)
                t = time.time()
                vals = ev.evaluate(run, obs, opts)
                scorer = RB.draft_pick(obs, acts)
                print(f"floor {obs['floor']}: " + ", ".join(f"{o.get('card_id', 'skip')} {v:.2f}" for o, v in zip(opts, vals))
                      + f" | scorer: {scorer.get('card_id', 'skip') if scorer else 'skip'} | {time.time() - t:.1f} s", flush=True)
                done += 1
            obs = run.call(cmd="run_step", action=pol.act(obs, acts, rng, run), timeout=120)["obs"]
    print(ev.stats)
    ev.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
