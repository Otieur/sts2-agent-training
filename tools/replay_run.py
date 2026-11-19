#!/usr/bin/env python3
"""Replay one of the Player's runs through the Agent's decision tools: at every card reward, rest site and Ancient
choice, what the tools recommend against what the Player chose, with the tools' reasons. Uses data/runs.db only.

The deck is reconstructed at the start of each floor; the act boss is the one the run met. Card values are v0.111.1
and the rules are today's playbook, applied to a v0.107.1 run. Map choices cannot be replayed (the run files keep
only the visited nodes). [PLAYER-DATA] facts, [HYPOTHESIS] recommendations.

Usage: python3 -I tools/replay_run.py <run_id or seed> [--out <file.md>]
"""
import argparse
import collections
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import advise  # noqa: E402
import draft  # noqa: E402
import simulate_fight as sf  # noqa: E402
from deck_metrics import deck_at  # noqa: E402
from stslib import DATA, PROJECT, connect, md_table  # noqa: E402


def replay(run_ref):
    con = connect()
    run = con.execute("SELECT * FROM runs WHERE run_id = ? OR seed = ? OR run_id LIKE ?", (run_ref, run_ref, run_ref + "%")).fetchone()
    if not run:
        raise SystemExit(f"run not found: {run_ref}")
    run = dict(run)
    ch, asc, rid = run["character"], run["ascension"], run["run_id"]
    bosses = {r["act"]: r["model_id"] for r in con.execute("SELECT act, model_id FROM floors WHERE run_id = ? AND room_type = 'boss'", (rid,))}
    floors = {r["floor"]: dict(r) for r in con.execute("SELECT * FROM floors WHERE run_id = ?", (rid,))}
    rows = []
    groups = collections.defaultdict(list)
    for r in con.execute("SELECT floor, act, offer_group, card_id, picked, source FROM card_offers WHERE run_id = ? ORDER BY floor", (rid,)):
        if r["source"] != "shop":
            groups[(r["floor"], r["offer_group"])].append(dict(r))
    for (floor, _), offers in sorted(groups.items()):
        act = offers[0]["act"]
        deck = deck_at(con, rid, floor)
        ids = ["CARD." + o["card_id"].split(".", 1)[-1] for o in offers if o["card_id"].split(".", 1)[-1] in draft.dm.CARDS]
        if not ids:
            continue
        boss = (bosses.get(act) or "").replace("ENCOUNTER.", "")
        fl = floors.get(floor, {})
        res = draft.score_offer(deck, ids, ch, act, floor, boss, simulate=(act == 1),  # as advise.py does in Act 1
                                hp=fl.get("hp_after"), max_hp=fl.get("max_hp") or 80, sim_deck=deck_at(con, rid, floor, upgrades=True),
                                sim_relics=[x["relic_id"] for x in con.execute(
                                    "SELECT relic_id FROM relic_events WHERE run_id = ? AND floor < ? AND picked = 1", (rid, floor))],
                                sim_potions=sf.potions_at(con, rid, floor))
        tool = res["pick"]["card"] if res["pick"] else "skip"
        player = next((o["card_id"].split(".", 1)[-1].replace("_", " ").title() for o in offers if o["picked"]), "skip")
        same = tool.replace(" ", "").lower() == player.replace(" ", "").lower()
        why = "; ".join(res["pick"]["reasons"][:2]) if res["pick"] else "nothing beats the skip bar"
        rows.append([floor, "card reward", ", ".join(i.split(".", 1)[-1].replace("_", " ").title() for i in ids), player, tool,
                     "same" if same else "**differs**", why])
    for r in con.execute("SELECT floor, act, choice, hp_before, max_hp, next_is_boss FROM rest_choices WHERE run_id = ? ORDER BY floor", (rid,)):
        if r["choice"] not in ("HEAL", "SMITH"):
            continue
        boss = (bosses.get(r["act"]) or "").replace("ENCOUNTER.", "")
        case = "boss" if r["next_is_boss"] else "other"
        choice, why = advise.rest_rule(r["hp_before"], r["max_hp"], r["act"], asc, boss, ch, case)[case]
        tool = {"rest": "HEAL", "smith": "SMITH"}.get(choice, "either")
        rows.append([r["floor"], "rest site", f"HP {r['hp_before']}/{r['max_hp']}" + (", boss next" if r["next_is_boss"] else ""),
                     r["choice"], tool, "same" if tool in (r["choice"], "either") else "**differs**", why])
    anc = {}
    afile = DATA / "tables" / "ancient_relics.csv"
    if afile.exists():
        with open(afile, newline="") as fh:
            anc = {r["relic"]: r for r in csv.DictReader(fh)}
    by_floor = collections.defaultdict(list)
    for r in con.execute("SELECT floor, option, chosen FROM ancient_choices WHERE run_id = ?", (rid,)):
        by_floor[r["floor"]].append(dict(r))
    for floor, opts in sorted(by_floor.items()):
        def score(o):
            a = anc.get(o["option"])
            if not a or not a["survive_act_chosen"] or not a["survive_act_passed"]:
                return 0.0
            return float(a["survive_diff"]) if float(a.get("p_survive") or 1) < 0.2 else 0.0
        best = max(opts, key=score)
        chosen = next((o["option"] for o in opts if o["chosen"]), "?")
        tool = best["option"] if score(best) > 0 else "no strong signal"
        avoid = [o["option"] for o in opts if score(o) < 0]
        rows.append([floor, "Ancient", ", ".join(o["option"].replace("_", " ").title() for o in opts), chosen.replace("_", " ").title(),
                     tool.replace("_", " ").title(), "**differs**" if chosen in avoid or (score(best) > 0 and chosen != best["option"]) else "no conflict",
                     ("avoid " + ", ".join(a.replace("_", " ").title() for a in avoid)) if avoid else "decision-point record (reports/phase2/ancient-relics.md)"])
    con.close()
    rows.sort(key=lambda r: r[0])
    last = max(floors) if floors else 0
    death = floors.get(last, {})
    return run, rows, death


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    run, rows, death = replay(args.run)
    diffs = sum(1 for r in rows if "differs" in r[5])
    result = "won" if run["win"] else f"died on floor {death.get('floor')} to {(death.get('model_id') or '?').replace('ENCOUNTER.', '')}"
    L = [f"# Agent Replay: run {run['run_id']}", "",
         f"{run['character'].title()} · A{run['ascension']} · {result}. Built by `tools/replay_run.py`: each decision the run "
         "records, with what today's tools recommend. Map choices are not in the run files. `[PLAYER-DATA]` facts, "
         "`[HYPOTHESIS]` recommendations; a different choice is not proof the run would have survived.", "",
         f"**{diffs} of {len(rows)} decisions differ.**", "",
         md_table(["Floor", "Decision", "Options", "The Player", "The tools", "", "The tools' reason"], rows), ""]
    text = "\n".join(L)
    if args.out:
        Path(args.out).write_text(text)
        print("wrote", args.out, f"({diffs}/{len(rows)} differ)")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
