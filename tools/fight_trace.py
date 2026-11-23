#!/usr/bin/env python3
"""One fight replayed with the runs' fight search, with every decision's candidates and values kept.

For a boss the Agent loses far more often than the Player: before any rule is tried, look at how one such fight is
lost (decision 0006). This is how the defect in the value of a lost rollout against the Test Subject was found
(`reports/phase9/boss-replay-2.md`, section 6): the trace showed the search ending turns with energy unspent, and the
values showed why.

    python3 -I tools/fight_trace.py data/learn/runs/run-bench-16 TEST_SUBJECT_BOSS 0
    python3 -I tools/fight_trace.py data/learn/runs/run-bench-16 QUEEN_BOSS 4 --out trace.json --loss-value m
    python3 -I tools/fight_trace.py --specs data/sim/benchmark-v1.json QUEEN_BOSS 0

The fight is one of the encounter's fights recorded in a run benchmark folder (sorted by seed and policy; the list is
printed with `--list`) or in a fight set (`--specs`). It is started fresh from its spec, so the hidden state differs
from the original fight. Search as in a boss room of a run benchmark: every distinct legal move, `--k` sampled worlds
each, rollouts to the end of the fight by the rule planner, every usable potion a candidate. `--loss-value` switches on
or off the options of `tools/sim.py` for the value of a lost rollout (`f`: forms to come, `m`: minions left out,
`none`: neither); without it the fight is searched as the runs search it.

Prints, per turn: the player's HP, block and energy, each enemy's HP, intent and powers, and the hand; per decision:
the action chosen by name (the card, the potion, the options taken at a choice), the best and worst candidate value,
and `ALL LOST` when every candidate's rollouts ended in a loss.

Beside each decision the trace keeps what the rule planner makes of the same state (`planner_view`): the planner
plays every rollout to its end, so where the search follows it the fight is played by the planner's judgement. Its
next action is printed where it differs from the search's, and where both end a turn its best plan with a card is
printed beside its plan that plays none. `--obs` keeps every decision's full observation in the `--out` file, so that
a later question about the planner can be answered from the file without playing the fight again
(`tools/trace_read.py` reads a folder of these files)."""
import argparse
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan_turn as pt  # noqa: E402
import selfplay as SP  # noqa: E402
import sim as S  # noqa: E402

# What a plan of the rule planner says of the turn it plans (tools/plan_turn.py `plans`); the terms its ranking uses.
PLAN_FIELDS = ("plays", "dealt", "block", "incoming", "hp_lost", "dies", "powers", "kills", "all_dead", "energy_left", "draws", "potions",
               "doom_dealt", "stun_bonus", "sandpit_bonus", "hex_loss", "hive_cards", "slippery_stripped")


def fights_of(folder, specs, encounter):
    out = []
    if specs:
        for f in json.loads(Path(specs).read_text())["fights"]:
            if f.get("encounter") == encounter:
                out.append((str((f.get("source") or {}).get("run")), str((f.get("source") or {}).get("policy") or ""), {"spec": f}))
        return out
    for path in sorted(glob.glob(f"{folder}/shard-*.jsonl")):
        for line in open(path):
            if line.strip():
                r = json.loads(line)
                for pol, v in r["policies"].items():
                    for ft in v.get("fights") or []:
                        if ft.get("encounter") == encounter and ft.get("spec"):
                            out.append((r["seed"], pol, ft))
    return sorted(out, key=lambda x: (x[0], x[1]))


def card_name(h):
    return str(h.get("card_id")) + ("+" if h.get("upgraded") else "")


def named(act, obs):
    """An action with the names a reader needs: the card played, the potion drunk, the options of a choice."""
    c = obs.get("combat") or {}
    hand = c.get("hand") or []
    target = f" -> {act['target']}" if act.get("target") is not None else ""
    if act.get("type") == "play" and isinstance(act.get("card"), int) and act["card"] < len(hand):
        return f"play {card_name(hand[act['card']])}{target}"
    if act.get("type") == "potion":
        pots = (obs.get("run") or {}).get("potions") or []
        slot = act.get("slot")
        name = pots[slot].get("potion_id") or pots[slot].get("id") or pots[slot].get("name") if isinstance(slot, int) and slot < len(pots) else slot
        return f"potion {name}{target}"
    if act.get("type") == "choose":
        ch = obs.get("choice") or {}
        opts = ch.get("options") or []
        picks = [str(opts[i].get("card_id") if isinstance(opts[i], dict) else opts[i]) if i < len(opts) else str(i) for i in act.get("cards") or []]
        return f"choose ({ch.get('kind')}) {', '.join(picks) if picks else 'nothing'}"
    return str(act.get("type"))


def plan_summary(plan):
    return None if plan is None else {k: plan[k] for k in PLAN_FIELDS if k in plan}


def planner_view(obs, mode="balanced", room=None):
    """What the rule planner makes of a decision state, as the rollouts of a `room` fight ask it (`mode`, potions at the
    room's price): its next action; its top plan; its best plan that plays at least one card and its plan that plays
    none, with the place of the latter in the ranking (0 = ending the turn is its first choice); the hand as it reads
    it (hand index or potion slot, card, cost, playable, potion) and the cards it leaves out as not simulated. None at a card choice, where
    the planner has no view."""
    if obs.get("choice") or not obs.get("combat"):
        return None
    hand, player, enemies = S._hand_for(pt, obs, room)
    view = {"action": S.planner_action(pt, obs, mode, room), "plans": 0, "top": None, "best_play": None, "end": None, "end_rank": None,
            "cards": [[c.index, c.card_id, c.cost, bool(c.playable), bool(c.potion)] for c in hand],
            "unsimulated": [card_name(h) for h in obs["combat"].get("hand") or [] if str(h.get("card_id")).rstrip("+") in S.UNSIMULATED]}
    if not enemies or not hand:
        return view
    ranked = S._rank(pt, pt.plans(hand, player, enemies), mode, room)
    end_rank = next((i for i, p in enumerate(ranked) if not p.get("seq")), None)
    view.update(plans=len(ranked), top=plan_summary(ranked[0]) if ranked else None, best_play=plan_summary(next((p for p in ranked if p.get("seq")), None)),
                end=plan_summary(ranked[end_rank]) if end_rank is not None else None, end_rank=end_rank)
    return view


def same_action(a, b, hand):
    """The search's action and the planner's are the same move: both end the turn, the same card play (or a second
    copy of the card at the same target), or the same potion at the same target."""
    if a.get("type") != b.get("type"):
        return False
    if a.get("type") == "play":
        return SP._same_play(a, b, hand)
    if a.get("type") == "potion":
        return a.get("slot") == b.get("slot") and a.get("target") == b.get("target")
    return a.get("type") == "end_turn"


def plan_line(p):
    return (f"{', '.join(p['plays']) or 'no card'}: dealt {p.get('dealt')}, HP lost {p.get('hp_lost')}" + (", dies" if p.get("dies") else "")
            + (f", powers {p['powers']}" if p.get("powers") else "") + (f", potions {p['potions']}" if p.get("potions") else ""))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("folder", nargs="?", help="run benchmark folder (or use --specs)")
    ap.add_argument("encounter")
    ap.add_argument("index", type=int, nargs="?", default=0)
    ap.add_argument("--specs", help="a fight set ({'fights': [fight specs]}) instead of a run benchmark folder")
    ap.add_argument("--list", action="store_true", help="list the encounter's fights and stop")
    ap.add_argument("--seed", type=int, default=1, help="sample seed")
    ap.add_argument("--k", type=int, default=6, help="sampled worlds per candidate")
    ap.add_argument("--room", default="Boss", choices=["Monster", "Elite", "Boss"], help="room type for the potions' price")
    ap.add_argument("--loss-value", help="'f', 'm', 'fm' or 'none' (tools/sim.py LOSS_COUNTS_FORMS, LOSS_SKIPS_MINIONS); default: as the runs play")
    ap.add_argument("--end-turn-z", type=float, help="check the end of a turn against the planner at this many standard errors "
                    "(tools/selfplay.py END_TURN_Z); default: as the runs play; 0 switches it off")
    ap.add_argument("--choices", choices=["on", "off"], help="search the answers to a card choice inside the fight, or take the first option "
                    "(tools/sim.py SEARCH_CHOICES); default: as the runs play")
    ap.add_argument("--out", help="write the decisions (turn, HP, enemies, chosen action, values, the planner's view) as JSON")
    ap.add_argument("--obs", action="store_true", help="keep every decision's full observation in the --out file")
    a = ap.parse_args(argv)
    if a.specs and a.folder and a.encounter.isdigit():      # `--specs file ENCOUNTER index`: the positional folder is the encounter
        a.folder, a.encounter, a.index = None, a.folder, int(a.encounter)
    fights = fights_of(a.folder, a.specs, a.encounter)
    if a.list or not fights:
        for i, (seed, pol, ft) in enumerate(fights):
            sp = ft["spec"]
            print(f"#{i}: {seed} {pol}: HP {sp.get('hp')}/{sp.get('max_hp')}" + (f" -> {ft['hp_end']}" if "hp_end" in ft else "") +
                  f", {len(sp['deck'])} cards, {len(sp['relics'])} relics, {len(sp.get('potions') or [])} potions")
        print(len(fights), "fights of", a.encounter)
        return 0 if fights else 1
    seed_id, pol, ft = fights[a.index]
    spec = ft["spec"]
    print(f"{a.encounter} #{a.index} of {len(fights)}: {seed_id} {pol}; HP {spec.get('hp')}/{spec.get('max_hp')}" + (f", in the run it ended at {ft['hp_end']}" if "hp_end" in ft else ""))
    print("deck", len(spec["deck"]), sorted(spec["deck"]))
    print("relics", spec["relics"], "potions", spec.get("potions"))
    if a.loss_value is not None:
        S.LOSS_COUNTS_FORMS, S.LOSS_SKIPS_MINIONS = "f" in a.loss_value.replace("none", ""), "m" in a.loss_value.replace("none", "")
    if a.end_turn_z is not None:
        SP.END_TURN_Z = a.end_turn_z or None
    if a.choices is not None:
        S.SEARCH_CHOICES = a.choices == "on"
    print("value of a lost rollout: forms to come counted", S.LOSS_COUNTS_FORMS, "| minions left out", S.LOSS_SKIPS_MINIONS,
          "| end of a turn checked against the planner at", SP.END_TURN_Z, "standard errors" if SP.END_TURN_Z else "(off)",
          "| card choices searched", S.SEARCH_CHOICES, flush=True)
    host = SP.Host()
    try:
        rec = SP.play(host, spec, a.seed, lambda sim, obs, d, done: SP.scored_search(sim, obs, "balanced", a.k, 2, d, done, potions=a.room, wide=True,
                                                                                      all_potions=a.room in ("Elite", "Boss")),
                      stuck_log=lambda x: print("  stuck", x, flush=True))
    finally:
        host.close()
    turn = None
    for dec in rec["decisions"]:
        o = dec["obs"]
        c = o["combat"]
        if o.get("turn") != turn:
            turn = o.get("turn")
            en = "; ".join(f"{e.get('name')} {e.get('current_hp')}/{e.get('max_hp')} block {e.get('block', 0)} intent {json.dumps(e.get('intent') or e.get('intents'))[:70]} "
                           f"powers {json.dumps(e.get('powers'))[:160]}" for e in c["enemies"])
            print(f"turn {turn}: HP {c['player']['current_hp']} block {c['player'].get('block', 0)} energy {c['player'].get('energy')} | {en}")
            print("  hand " + " ".join(card_name(h) for h in c.get("hand") or []))
        act = dec["candidates"][dec["chosen"]]
        vals = [v for v in dec["values"] if v is not None]
        tag = f" values best {max(vals):.0f} worst {min(vals):.0f} of {len(vals)}" + (" ALL LOST" if max(vals) < -100 else "") if vals else ""
        pv = dec["planner"] = planner_view(o, "balanced", a.room)
        if pv and not same_action(act, pv["action"], c.get("hand") or []):
            tag += f" | planner: {named(pv['action'], o)}"
        print(f"    {named(act, o)}{tag}")
        if pv and act.get("type") == "end_turn" and pv["action"].get("type") == "end_turn" and pv["best_play"]:
            print(f"      the planner ends the turn too (rank of ending {pv['end_rank']} of {pv['plans']} plans); its best plan with a card: {plan_line(pv['best_play'])}"
                  + (f"; ending: {plan_line(pv['end'])}" if pv["end"] else ""))
    print("outcome", json.dumps(rec["outcome"]))
    if a.out:
        json.dump({"source": [seed_id, pol], "encounter": a.encounter, "loss_value": a.loss_value, "end_turn_z": SP.END_TURN_Z, "search_choices": S.SEARCH_CHOICES, "end_checks": dict(SP.END_CHECKS), "outcome": rec["outcome"],
                   "decisions": [{"turn": d["obs"].get("turn"), "hp": d["obs"]["combat"]["player"]["current_hp"],
                                  "enemies": [[e.get("name"), e.get("current_hp"), e.get("max_hp")] for e in d["obs"]["combat"]["enemies"]],
                                  "energy": d["obs"]["combat"]["player"].get("energy"), "block": d["obs"]["combat"]["player"].get("block", 0),
                                  "hand": [card_name(h) for h in d["obs"]["combat"].get("hand") or []],
                                  "hand_cost": [h.get("energy_cost") for h in d["obs"]["combat"].get("hand") or []],
                                  "hand_playable": [bool(h.get("playable")) for h in d["obs"]["combat"].get("hand") or []],
                                  "enemy_powers": [[str(x.get("power_id")) for x in e.get("powers") or []] for e in d["obs"]["combat"]["enemies"]],
                                  "incoming": sum(i.get("total_damage") or 0 for e in d["obs"]["combat"]["enemies"] for i in e.get("intents") or [] if isinstance(i, dict)),
                                  "chosen_named": named(d["candidates"][d["chosen"]], d["obs"]),
                                  "chosen": d["candidates"][d["chosen"]], "candidates": d["candidates"], "values": d["values"],
                                  "planner": d.get("planner") and dict(d["planner"], named=named(d["planner"]["action"], d["obs"]),
                                                                       same=same_action(d["candidates"][d["chosen"]], d["planner"]["action"], d["obs"]["combat"].get("hand") or [])),
                                  **({"obs": d["obs"]} if a.obs else {})} for d in rec["decisions"]]}, open(a.out, "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
