#!/usr/bin/env python3
"""Read a folder of fight traces (tools/fight_trace.py --out): how turns end, and who ended them.

    python3 -I tools/trace_read.py data/learn/traces/boss-replay-2-g-ts [more folders] [--fights]

Per folder: fights and their outcomes; turns ended with a playable card in hand that the energy left pays for (status
and curse cards left out) and the margin by which ending the turn was scored above the best card there; decisions where
every candidate's rollouts were lost; the gap between the best and the second-best candidate; attacks played into an
Intangible enemy.

Where the traces keep the rule planner's view of each decision (traces made since 2026-11-23), also: how often the
search's action is the planner's; and each turn ended with a paid-for card split by who ended it. The search ended it
against the planner when the planner's next action was a card or a potion. The planner ended it too when its first
plan plays nothing; then the cards left are split into those the planner cannot play as it reads the hand (not in its
hand, unplayable, or dearer than the energy) and those it can play and ranks behind ending the turn, with what its best
plan with a card would deal and cost in HP beside ending. The reverse case is counted as well: the search plays on
where the planner would end the turn.

Where the traces keep the observations (`fight_trace.py --obs`), also: the turns ended with a paid-for card while no
enemy could be hit (a boss between two forms: nothing to attack, so no early end at all); and the card choices answered
inside the fights (Headbutt, True Grit+, a potion's cards, the Knowledge Demon's curse): how many, how many had more
than one distinct option, how many were searched and took another answer than the first option, what asked for them,
and the curse taken at each Knowledge Demon offer. For every folder: the share of a fight's decisions with every
candidate lost, for won and for lost fights, and the lost fights in which that was so from the first turn on.

A description of recorded fights, not a test: it says where to look before a rule is written (decision 0006)."""
import argparse
import glob
import json
import statistics as st
import sys
from collections import Counter, defaultdict

OFFER = {"MIND_ROT": 1, "SLOTH": 2, "WASTE_AWAY": 3}      # the card offered beside Disintegration at each Curse of Knowledge
DEAD = ("WOUND", "BURN", "DAZED", "SLIMED", "VOID", "REGRET", "SHAME", "DOUBT", "INJURY", "CLUMSY", "DECAY", "NORMALITY", "PAIN", "PARASITE", "WRITHE", "CURSE")


def dead(name):
    return any(name.upper().startswith(x) for x in DEAD)


def paid_for(x):
    """(hand index, card name) of the cards a decision's hand holds that are playable and that the energy pays for."""
    e = x.get("energy") or 0
    return [(i, n) for i, (n, c, ok) in enumerate(zip(x["hand"], x.get("hand_cost") or [], x.get("hand_playable") or []))
            if ok and not dead(n) and isinstance(c, int) and c <= e]


def planner_can(x, index):
    """The planner reads the card at this hand index as playable for the energy left."""
    e = x.get("energy") or 0
    return any(c[0] == index and not c[4] and c[3] and isinstance(c[2], int) and c[2] <= e for c in x["planner"].get("cards") or [])


def can_hit(x):
    """An enemy can be hit at this decision; None where the trace keeps no observation."""
    c = (x.get("obs") or {}).get("combat")
    return None if not c else any(e.get("is_alive") and e.get("is_hittable") for e in c.get("enemies") or [])


def choice_of(x, before):
    """A card choice answered at this decision (from the kept observation), or None: its kind, what asked for it (the
    action before), whether it had more than one distinct option, was searched, and took another answer than the first."""
    ch = (x.get("obs") or {}).get("choice")
    if not ch:
        return None
    opts = ch.get("options") or []
    taken = [opts[i] for i in x["chosen"].get("cards") or [] if i < len(opts)]
    offered = [o for o in opts if o in OFFER]
    asked = (before or "?").replace("play ", "").split(" -> ")[0].rstrip("+")
    return {"kind": ch.get("kind"), "asked": "end of turn" if asked == "end_turn" else asked, "real": len(set(opts)) > 1, "searched": len(x["candidates"]) > 1,
            "other": x["chosen"].get("cards") != x["candidates"][0].get("cards"), "taken": taken,
            "offer": OFFER[offered[0]] if "DISINTEGRATION" in opts and offered else None}


def read_fight(path):
    d = json.load(open(path))
    ds = d["decisions"]
    r = {"path": path, "status": d["outcome"]["status"], "left": d["outcome"].get("enemies"), "turns": len({x["turn"] for x in ds}),
         "ends": 0, "early": [], "scored": 0, "lost_all": 0, "gaps": [], "into_intangible": 0,
         "viewed": 0, "same": 0, "against": [], "with": [], "plays_on": 0, "plays_on_lost": 0, "choices": [], "first_turn_lost": None}
    before, first_turn = None, None
    for x in ds:
        act = x["chosen"]
        vals = [v for v in x["values"] if v is not None]
        ch = choice_of(x, before)
        if ch:
            r["choices"].append(ch)
        before = x.get("chosen_named")
        if len(vals) > 1:
            r["scored"] += 1
            r["lost_all"] += max(vals) < -100
            top = sorted(vals, reverse=True)
            r["gaps"].append(top[0] - top[1])
            first_turn = x["turn"] if first_turn is None else first_turn
            if x["turn"] == first_turn:
                r["first_turn_lost"] = max(vals) < -100 and r["first_turn_lost"] is not False
        if act["type"] == "play" and act.get("target") is not None and any("INTANGIBLE" in p for ps in x.get("enemy_powers") or [] for p in ps):
            r["into_intangible"] += 1
        pv = x.get("planner")
        if pv:
            r["viewed"] += 1
            r["same"] += bool(pv.get("same"))
            if act["type"] != "end_turn" and pv["action"]["type"] == "end_turn":
                r["plays_on"] += 1
                r["plays_on_lost"] += bool(vals) and max(vals) < -100
        if act["type"] != "end_turn":
            continue
        r["ends"] += 1
        left = paid_for(x)
        if not left:
            continue
        end_value = next((v for c, v in zip(x["candidates"], x["values"]) if c["type"] == "end_turn"), None)
        plays = [v for c, v in zip(x["candidates"], x["values"]) if c["type"] == "play" and v is not None]
        margin = end_value - max(plays) if plays and end_value is not None else None
        e = {"turn": x["turn"], "energy": x.get("energy") or 0, "cards": [n for _, n in left], "margin": margin, "lost": bool(vals) and max(vals) < -100,
             "no_target": can_hit(x) is False}
        r["early"].append(e)
        if not pv:
            continue
        if pv["action"]["type"] != "end_turn":
            r["against"].append(dict(e, planner=pv.get("named")))
        else:
            can = [n for i, n in left if planner_can(x, i)]
            bp, end = pv.get("best_play"), pv.get("end")
            r["with"].append(dict(e, can=can, cannot=[n for i, n in left if not planner_can(x, i)],
                                  dealt=bp["dealt"] - end["dealt"] if bp and end else None, hp_lost=bp["hp_lost"] - end["hp_lost"] if bp and end else None,
                                  dies=bool(bp and bp.get("dies")), best=bp["plays"] if bp else None))
    return r


def med(v):
    return f"{st.median(v):.1f}" if v else "n/a"


def report(folder, per_fight):
    paths = sorted(glob.glob(f"{folder}/trace-*.json"), key=lambda p: int(p.rsplit("-", 1)[1].split(".")[0]))
    rows = [read_fight(p) for p in paths]
    if not rows:
        print(f"{folder}: no traces")
        return 1
    if per_fight:
        for r in rows:
            print(f"  {r['path'].rsplit('/', 1)[1]}: {r['status']} {r['left']} in {r['turns']} turns; turns ended with a paid-for card {len(r['early'])} of {r['ends']}"
                  + (f" (against the planner {len(r['against'])}, with it {len(r['with'])}); plays on where the planner ends {r['plays_on']}" if r["viewed"] else "")
                  + f"; all lost at {r['lost_all']} of {r['scored']} decisions")
    ends, early = sum(r["ends"] for r in rows), [e for r in rows for e in r["early"]]
    margins = [e["margin"] for e in early if e["margin"] is not None]
    gaps = [g for r in rows for g in r["gaps"]]
    print(f"{folder}: {len(rows)} fights, {sum(r['status'] == 'won' for r in rows)} won, {sum(r['turns'] for r in rows)} turns")
    print(f"  turns ended {ends}; with a playable card that the energy pays for: {len(early)} ({len(early) / max(ends, 1):.0%}), in {sum(bool(r['early']) for r in rows)} fights; "
          f"with energy left {sum(e['energy'] > 0 for e in early)}; on turn 1 {sum(e['turn'] == 1 for e in early)}")
    print(f"  margin of ending the turn over the best card there: median {med(margins)}, under 30 points in {sum(m < 30 for m in margins)} of {len(margins)}")
    print(f"  decisions with every candidate lost: {sum(r['lost_all'] for r in rows)} of {sum(r['scored'] for r in rows)}; "
          f"gap best to second-best: median {med(gaps)}" + (f", quartiles {[round(q, 1) for q in st.quantiles(gaps, n=4)]}" if len(gaps) > 3 else ""))
    print(f"  attacks played into an Intangible enemy: {sum(r['into_intangible'] for r in rows)}")
    for status in ("won", "lost"):
        share = [r["lost_all"] / r["scored"] for r in rows if r["status"] == status and r["scored"]]
        if share:
            print(f"  share of a fight's decisions with every candidate lost, {status} fights ({len(share)}): median {st.median(share):.2f}, from {min(share):.2f} to {max(share):.2f}"
                  f"; so at every decision of the first turn in {sum(bool(r['first_turn_lost']) for r in rows if r['status'] == status)}")
    if any(e["no_target"] for e in early):
        print(f"  of the turns ended with a paid-for card, with no enemy that could be hit: {sum(e['no_target'] for e in early)}")
    choices = [c for r in rows for c in r["choices"]]
    if choices:
        print(f"  card choices inside the fights: {len(choices)} ({len(choices) / len(rows):.1f} a fight); with more than one distinct option {sum(c['real'] for c in choices)}; "
              f"searched {sum(c['searched'] for c in choices)}; another answer than the first option {sum(c['other'] for c in choices)}")
        print(f"    asked by: {Counter(c['asked'] for c in choices).most_common(10)}")
        curse = defaultdict(Counter)
        for c in choices:
            if c["offer"]:
                curse[c["offer"]]["+".join(c["taken"]) or "nothing"] += 1
        for offer in sorted(curse):
            print(f"    Curse of Knowledge, offer {offer}: {dict(curse[offer])}")
    viewed = sum(r["viewed"] for r in rows)
    if not viewed:
        print("  (these traces keep no planner view)")
        return 0
    against, with_ = [e for r in rows for e in r["against"]], [e for r in rows for e in r["with"] if not e["no_target"]]
    dead = sum(e["no_target"] for r in rows for e in r["with"])
    print(f"  the search's action is the planner's at {sum(r['same'] for r in rows)} of {viewed} decisions ({sum(r['same'] for r in rows) / viewed:.0%})")
    print(f"  turns ended with a paid-for card, by who ended them: the search against the planner {len(against)}, the planner too {len(with_)}"
          + (f" (and {dead} with no enemy that could be hit, where the planner has no plan)" if dead else ""))
    if against:
        m = [e["margin"] for e in against if e["margin"] is not None]
        print(f"    against the planner: margin median {med(m)}, under 30 points in {sum(x < 30 for x in m)} of {len(m)}; every candidate lost in {sum(e['lost'] for e in against)}; "
              f"the planner's card: {Counter((e['planner'] or '').split(' -> ')[0] for e in against).most_common(8)}")
    if with_:
        none = [e for e in with_ if not e["can"]]
        some = [e for e in with_ if e["can"]]
        print(f"    the planner too: it can play none of the cards left in {len(none)} (cards: {Counter(n for e in none for n in e['cannot']).most_common(8)})")
        dealt, hp = [e["dealt"] for e in some if e["dealt"] is not None], [e["hp_lost"] for e in some if e["hp_lost"] is not None]
        print(f"    the planner too: it can play a card left and ranks ending first in {len(some)} (cards: {Counter(n for e in some for n in e['can']).most_common(8)})")
        print(f"      its best plan with a card beside ending: damage dealt {med(dealt)} more at the median, HP lost {med(hp)} more; costs HP in {sum(x > 0 for x in hp)} of {len(hp)}, "
              f"deals nothing more in {sum(x <= 0 for x in dealt)} of {len(dealt)}, dies in {sum(e['dies'] for e in some)}")
    print(f"  the search plays on where the planner would end the turn: {sum(r['plays_on'] for r in rows)} decisions ({sum(r['plays_on_lost'] for r in rows)} with every candidate lost)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("folders", nargs="+")
    ap.add_argument("--fights", action="store_true", help="a line for each fight")
    a = ap.parse_args(argv)
    return max(report(f, a.fights) for f in a.folders)


if __name__ == "__main__":
    sys.exit(main())
