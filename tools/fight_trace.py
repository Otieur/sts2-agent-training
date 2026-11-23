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
and `ALL LOST` when every candidate's rollouts ended in a loss."""
import argparse
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import selfplay as SP  # noqa: E402
import sim as S  # noqa: E402


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
    ap.add_argument("--out", help="write the decisions (turn, HP, enemies, chosen action, values) as JSON")
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
    print("value of a lost rollout: forms to come counted", S.LOSS_COUNTS_FORMS, "| minions left out", S.LOSS_SKIPS_MINIONS,
          "| end of a turn checked against the planner at", SP.END_TURN_Z, "standard errors" if SP.END_TURN_Z else "(off)", flush=True)
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
        print(f"    {named(act, o)}{tag}")
    print("outcome", json.dumps(rec["outcome"]))
    if a.out:
        json.dump({"source": [seed_id, pol], "encounter": a.encounter, "loss_value": a.loss_value, "end_turn_z": SP.END_TURN_Z, "end_checks": dict(SP.END_CHECKS), "outcome": rec["outcome"],
                   "decisions": [{"turn": d["obs"].get("turn"), "hp": d["obs"]["combat"]["player"]["current_hp"],
                                  "enemies": [[e.get("name"), e.get("current_hp"), e.get("max_hp")] for e in d["obs"]["combat"]["enemies"]],
                                  "energy": d["obs"]["combat"]["player"].get("energy"), "block": d["obs"]["combat"]["player"].get("block", 0),
                                  "hand": [card_name(h) for h in d["obs"]["combat"].get("hand") or []],
                                  "hand_cost": [h.get("energy_cost") for h in d["obs"]["combat"].get("hand") or []],
                                  "hand_playable": [bool(h.get("playable")) for h in d["obs"]["combat"].get("hand") or []],
                                  "enemy_powers": [[str(x.get("power_id")) for x in e.get("powers") or []] for e in d["obs"]["combat"]["enemies"]],
                                  "incoming": sum(i.get("total_damage") or 0 for e in d["obs"]["combat"]["enemies"] for i in e.get("intents") or [] if isinstance(i, dict)),
                                  "chosen_named": named(d["candidates"][d["chosen"]], d["obs"]),
                                  "chosen": d["candidates"][d["chosen"]], "candidates": d["candidates"], "values": d["values"]} for d in rec["decisions"]]}, open(a.out, "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
