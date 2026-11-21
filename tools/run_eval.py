#!/usr/bin/env python3
"""Decision-time evaluation of run-level choices by sampled rollouts (decision 0004 steps 3-4).

At a decision point the run host exports its state (the room-entry save plus the run actions since). For each option,
an evaluation host rebuilds that state with the hidden future re-sampled (`run_from_save` with a sample seed; FP-9,
FP-16), takes the option, and plays on with a fast rollout policy (rule planner in fights, the rule tools elsewhere)
to the end of the current act or death. The same sample seeds are used for every option (common random numbers), so
options are compared on the same sampled futures. The option with the best mean rollout value is chosen.

Rollout value: floors climbed from the decision point, plus, if the act's boss is beaten, 5 and 5 times the HP fraction
left. With `boss_credit` w > 0 (run benchmark 7), a rollout that dies in a boss fight also gets w times the fraction of
the boss fight's enemy HP it removed (dying with the boss nearly dead is worth nearly as much as beating it; the rule
planner that fights in rollouts rarely beats bosses, so without this most rollouts that reach the boss score alike),
and a won run counts as beating the act's boss (in act 3 the act never advances). Only what the player can see is
used: the rollouts play in worlds whose unseen parts are freshly sampled.

    python3 -I tools/run_eval.py --demo --seed RB90000001 --ascension 5     # one run, card rewards by rollouts, timings
"""
import argparse
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim as S  # noqa: E402


# a decision whose first rollouts all fail is given up after this many failures (see RolloutEvaluator.evaluate)
GIVE_UP_AFTER = 3

# enemies above this HP cannot be killed (for example a boss that turns the fight into surviving); not counted
UNKILLABLE_HP = 10_000


def rollout_value(start, end, start_act, boss=None, boss_credit=0.0):
    """`boss`: (enemy HP at the start of the last boss fight, enemy HP left at its last observation), or None."""
    climbed = (end.get("floor") or 0) - (start.get("floor") or 0)
    alive = end["screen"] != "game_over" or end["player"]["hp"] > 0
    beat_boss = alive and ((end.get("act") or 1) > start_act or (boss_credit > 0 and end["screen"] == "game_over"))
    bonus = 5 + 5 * end["player"]["hp"] / max(1, end["player"]["max_hp"]) if beat_boss else 0
    if boss_credit > 0 and not alive and boss and boss[0] > 0:
        bonus += boss_credit * max(0.0, min(1.0, 1 - boss[1] / boss[0]))
    return climbed + bonus


def boss_fight_hp(obs):
    """Enemy HP in a boss fight observation (killable enemies only), or None outside boss fights."""
    in_fight = obs["screen"] == "combat" or (obs["screen"] == "choice" and bool(obs.get("combat")))
    if not in_fight or not str(obs.get("encounter") or "").endswith("_BOSS"):
        return None
    es = [e for e in (obs.get("combat") or {}).get("enemies", []) if e.get("max_hp", 0) <= UNKILLABLE_HP]
    return sum(e.get("max_hp", 0) for e in es), sum(max(0, e.get("current_hp", 0)) for e in es if e.get("is_alive", True))


class RolloutEvaluator:
    """Owns an evaluation host. `evaluate(run_sim, obs, options)` returns the mean rollout value of each option."""

    def __init__(self, k=6, max_steps=3000, rollout_policy="draft+shop+rest", seed_base=7_700_000, boss_credit=0.0):
        self.k, self.max_steps, self.seed_base, self.boss_credit = k, max_steps, seed_base, boss_credit
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
        done, failed, give_up = 0, 0, False
        for j in range(self.k):
            if give_up:
                break
            seed = self.seed_base + 1000 * self._n + j          # the same sampled futures for every option
            for i, opt in enumerate(options):
                try:
                    o = h.call(cmd="run_from_save", data=ex["save_b64"], actions=ex["actions"], test_hp=ex["test_hp"],
                               sample_seed=seed, timeout=120)["obs"]
                    o = h.call(cmd="run_step", action=opt, timeout=120)["obs"]
                    pol, rng = RB.Policy(self.rollout_policy), random.Random(seed)
                    boss, prev = None, None                 # (enemy HP at the boss fight's start, enemy HP left)
                    for _ in range(self.max_steps):
                        if o["screen"] == "game_over" or (o.get("act") or 1) > start_act:
                            break
                        if self.boss_credit > 0:
                            bh = boss_fight_hp(o)
                            if bh is not None:
                                boss = (bh[0] if prev is None else max(boss[0], bh[0]), bh[1])
                            prev = bh
                        acts = h.call(cmd="run_legal")["actions"]
                        if not acts:
                            break
                        o = h.call(cmd="run_step", action=pol.act(o, acts, rng, h), timeout=120)["obs"]
                    values[i].append(rollout_value(obs, o, start_act, boss, self.boss_credit))
                    if self.boss_credit > 0 and boss is not None and o["screen"] == "game_over" and o["player"]["hp"] <= 0:
                        self.stats["boss_deaths"] = self.stats.get("boss_deaths", 0) + 1
                        self.stats["boss_hp_removed"] = self.stats.get("boss_hp_removed", 0.0) + max(0.0, min(1.0, 1 - boss[1] / max(1, boss[0])))
                    self.stats["rollouts"] += 1
                    done += 1
                except S.SimError as e:
                    self.stats["errors"] += 1
                    failed += 1
                    if self.stats["errors"] <= 5 or self.stats["errors"] % 50 == 0:      # failures are counted and sampled (EN-5)
                        print(f"  rollout error {self.stats['errors']} (decision {self._n}, option {i}, sample {j}, floor {obs.get('floor')}, "
                              f"{obs.get('screen')}): {str(e)[:300]}", flush=True)
                    self.close()
                    h = self._host()
                    if done == 0 and failed >= GIVE_UP_AFTER:
                        # nothing can be rolled out from this state (each failure costs a host restart): the decision
                        # goes to the rule now, not after every option and sample has failed
                        self.stats["given_up"] = self.stats.get("given_up", 0) + 1
                        give_up = True
                        break
        self.stats["decisions"] += 1
        self.stats["seconds"] += time.time() - t0
        return [sum(v) / len(v) if v and not give_up else None for v in values]


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
