#!/usr/bin/env python3
"""Rollout decisions for the run choices that card and route rollouts leave to rules (run benchmarks 9 and 10).

Used by `tools/run_bench.py` components:
- `ropt`: events (Neow and the Ancients included; every page with two or more options), rest sites (heal, smith and
  any other site option; not leaving empty-handed) and card choices outside fights (upgrade, remove, transform,
  enchant, choose a card, and the like). With the `smith` rule in the policy, rest sites and upgrade choices are left
  to that rule.
- `rshop`: shop screens, one purchase at a time: leave, or buy one affordable item (card, relic, potion, card removal);
  after a purchase the shop is judged again, until leaving wins.
- `rshop2`: the same with room for every item of a shop (`MAX_SHOP_OPTIONS`). With `rshop`, a shop where more than
  `MAX_OPTIONS` - 1 items are affordable is left to the rules, which leave: in run benchmark 11 that is every shop
  entered with more than about 180 gold (no decision with more than 176 gold, no relic ever among the options, 503
  gold left at the end of a run). And when the rollouts cannot tell a shop's options apart (every option has the same
  value, typically because every sampled future ends at the same boss fight), `rshop2` does not leave with its gold:
  it buys the cheapest affordable relic, else the card removal, and leaves only when neither is for sale.

Each option is played forward over the same sampled futures by `tools/run_eval.py` (the run rebuilt from its room-entry
save with the unseen future re-sampled, the option taken, then the run's rule policy to the end of the act with the rule
planner fighting), and the best mean value is taken. Exact ties and failures go to what the run's rules would do.
Identical options (the same card id, the same item) are judged once. Screens with more than `MAX_OPTIONS` distinct
options (`MAX_SHOP_OPTIONS` in shops with `rshop2`) are left to the rules. Only what the player can see is used.
"""
import sys

MAX_OPTIONS = 12
MAX_SHOP_OPTIONS = 24       # a shop sells at most 7 cards, 3 relics, 3 potions and a card removal; leaving is one more
DECK_KINDS = ("FromDeck", "FromChooseACardScreen", "FromSimpleGrid")
_EVALUATOR = None


def close():
    global _EVALUATOR
    if _EVALUATOR is not None:
        _EVALUATOR.close()
        _EVALUATOR = None


def _key(a):
    """Options that do the same thing get the same key (five Strikes to upgrade are one option)."""
    t = a.get("type")
    if t == "choose":
        return ("choose", a.get("card_id") or tuple(a.get("cards") or ()))
    if t == "buy":
        return ("buy", a.get("item"))
    if t == "event_option":
        return ("event", a.get("key"), a.get("index"))
    if t == "rest_option":
        return ("rest", a.get("option"))
    return (t,)


def _distinct(opts):
    seen, out = set(), []
    for a in opts:
        k = _key(a)
        if k not in seen:
            seen.add(k)
            out.append(a)
    return out


def options(parts, obs, acts):
    """The options judged by rollouts on this screen, or [] when the screen is left to the rules."""
    scr = obs["screen"]
    ch = obs.get("choice") or {}
    opts = []
    if "ropt" in parts:
        smith = "smith" in parts        # with the `smith` rule, rest sites and upgrade choices follow the rule
        if scr == "event":
            opts = [x for x in acts if x.get("type") == "event_option"]
        elif scr == "rest" and not smith:
            opts = [x for x in acts if x.get("type") == "rest_option"]
        elif scr == "choice" and not obs.get("combat") and str(ch.get("kind", "")).startswith(DECK_KINDS) \
                and ch.get("kind") not in ("CardReward",) and not (smith and str(ch.get("kind", "")).startswith("FromDeckForUpgrade")):
            opts = [x for x in acts if x.get("type") == "choose"]
    cap = MAX_OPTIONS
    if ("rshop" in parts or "rshop2" in parts) and scr == "shop":
        if "rshop2" in parts:
            cap = MAX_SHOP_OPTIONS
        gold = obs["player"].get("gold", 0)
        buys = [x for x in acts if x.get("type") == "buy" and x.get("cost", 1e9) <= gold]
        leave = [x for x in acts if x.get("type") == "leave"]
        order = lambda x: (0 if "remov" in str(x.get("item", "")).lower() else 1 if str(x.get("item", "")).startswith("relic:")
                           else 2 if str(x.get("item", "")).startswith("card:") else 3)
        opts = leave[:1] + sorted(buys, key=order)
    opts = _distinct(opts)
    return opts if 2 <= len(opts) <= cap else []


def blind_buy(opts):
    """Index of the purchase `rshop2` makes when rollouts cannot tell a shop's options apart: the cheapest relic, else
    the card removal; None when neither is among the options. Neither can weaken the deck, and gold buys nothing else."""
    relics = [i for i, o in enumerate(opts) if o.get("type") == "buy" and str(o.get("item", "")).startswith("relic:")]
    if relics:
        return min(relics, key=lambda i: opts[i].get("cost", 0))
    return next((i for i, o in enumerate(opts) if o.get("type") == "buy" and "remov" in str(o.get("item", "")).lower()), None)


def rule_action(policy, obs, acts, rng, sim):
    """What the run's rules alone would do here (the policy without `ropt` and `rshop`), leaving its state as it was."""
    saved = (set(policy.bought), policy.pending)
    policy.rule_mode = True
    try:
        return policy.act(obs, acts, rng, sim)
    finally:
        policy.rule_mode = False
        policy.bought, policy.pending = saved


def pick(policy, obs, acts, rng, sim):
    global _EVALUATOR
    opts = options(policy.parts, obs, acts)
    if not opts:
        return None
    import run_eval
    rb = sys.modules[type(policy).__module__]
    rule = rule_action(policy, obs, acts, rng, sim)
    # share the route rollouts' evaluation host when its rollouts are the same (same rule policy and value): one host
    # fewer per worker; otherwise keep an own one
    ev = rb._ROUTE_EVALUATOR
    if ev is None:
        ev = rb._ROUTE_EVALUATOR = run_eval.RolloutEvaluator(k=rb.ROLLOUTS_K, rollout_policy=policy.route_rollout_policy(),
                                                             seed_base=8_800_000, boss_credit=policy.boss_credit())
    if (ev.rollout_policy, ev.boss_credit, ev.k) != (policy.rule_policy(), policy.boss_credit(), rb.ROLLOUTS_K):
        if _EVALUATOR is None:
            _EVALUATOR = run_eval.RolloutEvaluator(k=rb.ROLLOUTS_K, rollout_policy=policy.rule_policy(), seed_base=7_300_000,
                                                   boss_credit=policy.boss_credit())
        ev = _EVALUATOR
    vals = ev.evaluate(sim, obs, opts)
    name = "rshop" if obs["screen"] == "shop" else "ropt"
    st = policy.stats
    if any(v is None for v in vals):
        st[name + "_failed"] = st.get(name + "_failed", 0) + 1
        return None
    rk = _key(rule) if rule else None
    best = max(range(len(opts)), key=lambda i: (vals[i], _key(opts[i]) == rk))
    if name == "rshop" and "rshop2" in policy.parts and max(vals) - min(vals) < 1e-9:
        blind = blind_buy(opts)
        if blind is not None:
            best = blind
            st["rshop_blind_buys"] = st.get("rshop_blind_buys", 0) + 1
    policy.note("shop" if name == "rshop" else "opt", obs, opts, vals, best, next((i for i, o in enumerate(opts) if _key(o) == rk), None))
    st[name + "_decisions"] = st.get(name + "_decisions", 0) + 1
    st[name + "_disagree"] = st.get(name + "_disagree", 0) + (_key(opts[best]) != rk)
    if name == "rshop":
        st["rshop_buys"] = st.get("rshop_buys", 0) + (opts[best].get("type") == "buy")
    return opts[best]
