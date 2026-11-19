#!/usr/bin/env python3
"""Build readable references for events, relics and potions: extracted game data joined with the Player's history.

Writes knowledge/events.md, knowledge/relics.md, knowledge/potions.md.
Usage: python3 -I tools/build_misc_reference.py [--build v0.107.1]
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import MAIN_BUILD, PROJECT, connect, md_table, mean, num, pct  # noqa: E402

EX = PROJECT / "knowledge/data/extract-2026-09-21"


def spaced(name):
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", name)


def esc(s, n=140):
    s = (s or "").replace("|", "/").replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def events(con, build):
    ev = {e["id"]: e for e in json.loads((EX / "events.json").read_text())}
    opts = collections.defaultdict(list)
    for o in json.loads((EX / "event_options.json").read_text()):
        opts[o["Event"]].append(o)
    picks = collections.defaultdict(lambda: collections.defaultdict(list))
    visits = collections.Counter()
    for r in con.execute("""SELECT e.event_id, e.choice_key, e.hp_change, e.gold_change, e.max_hp_change, e.run_id, e.floor
                            FROM event_choices e JOIN runs r USING(run_id) WHERE r.n_players=1 AND r.build_id=?""", [build]):
        eid = (r["event_id"] or "").split(".", 1)[-1]
        key = re.sub(r"^[A-Z0-9_]+\.pages\.", "", r["choice_key"] or "")
        key = re.sub(r"\.title$", "", key)
        picks[eid][key].append((r["hp_change"], r["gold_change"], r["max_hp_change"]))
    for r in con.execute("""SELECT DISTINCT e.run_id, e.floor, e.event_id FROM event_choices e JOIN runs r USING(run_id)
                            WHERE r.n_players=1 AND r.build_id=?""", [build]):
        visits[(r["event_id"] or "").split(".", 1)[-1]] += 1
    L = ["# Events", "",
         "Options, effects, costs and risk tags from the extracted game data `[GAME-EXTRACT]` (base values; `?` = computed "
         "in game). The Player's choices are from solo runs on " + build + " `[PLAYER-DATA]`, with the mean net HP, gold and "
         "max-HP change over the event floor. The Player's choices are a baseline, not advice.", "",
         "Risk tags: `lethal-possible` (an option can kill at low HP), `costly`, `none-detected` (no cost found; not a guarantee).", ""]
    for eid in sorted(set(ev) | set(picks), key=lambda e: (-visits.get(e, 0), e)):
        e = ev.get(eid, {})
        L.append(f"## {spaced(e.get('name', eid.title()))} (`{eid}`)")
        L.append("")
        L.append(f"Player visits: {visits.get(eid, 0)} · highest risk: {e.get('highestrisk', '?')} · "
                 f"{'combat event: ' + e['encounter'] if e.get('encounter') not in (None, '-') else 'no combat'}")
        L.append("")
        rows = []
        seen = set()
        for o in opts.get(eid, []):
            key = o["Option"]
            seen.add(key)
            ps = picks[eid].get(key, [])
            rows.append([esc(key.split(".")[-1], 30), esc(o["Effect"], 70), esc(o["Cost"], 60), o["Risk"],
                         len(ps), num(mean([p[0] for p in ps]), 1) if ps else "-", num(mean([p[1] for p in ps]), 0) if ps else "-"])
        for key, ps in picks[eid].items():
            if key not in seen:
                rows.append([esc(key.split(".")[-1], 30), "(not in the extract)", "-", "-", len(ps),
                             num(mean([p[0] for p in ps]), 1), num(mean([p[1] for p in ps]), 0)])
        L.append(md_table(["Option", "Effect", "Cost", "Risk", "Player picks", "Mean HP change", "Mean gold change"], rows) if rows else "No option data.")
        L.append("")
    (PROJECT / "knowledge/events.md").write_text("\n".join(L))
    return len(set(ev) | set(picks))


def relics(con, build):
    rel = json.loads((EX / "relics.json").read_text())
    offered, picked, bought = collections.Counter(), collections.Counter(), collections.Counter()
    for r in con.execute("""SELECT x.kind, x.relic_id, x.picked FROM relic_events x JOIN runs r USING(run_id)
                            WHERE r.n_players=1 AND r.build_id=?""", [build]):
        rid = r["relic_id"].split(".", 1)[-1]
        if r["kind"] == "offered":
            offered[rid] += 1
            picked[rid] += r["picked"] or 0
        elif r["kind"] == "bought":
            bought[rid] += 1
    anc_off, anc_pick = collections.Counter(), collections.Counter()
    for r in con.execute("""SELECT a.option, a.chosen FROM ancient_choices a JOIN runs r USING(run_id)
                            WHERE r.n_players=1 AND r.build_id=?""", [build]):
        anc_off[r["option"]] += 1
        anc_pick[r["option"]] += r["chosen"]
    fin = {r["run_id"]: r["win"] for r in con.execute(
        "SELECT run_id, win FROM runs WHERE n_players=1 AND build_id=? AND abandoned=0", [build])}
    holders = collections.defaultdict(set)
    for r in con.execute("SELECT run_id, relic_id FROM final_relics"):
        if r["run_id"] in fin:
            holders[r["relic_id"].split(".", 1)[-1]].add(r["run_id"])
    base_wr = sum(fin.values()) / len(fin)
    order = {"Starter": 0, "Common": 1, "Uncommon": 2, "Rare": 3, "Shop": 4, "Boss": 5, "Ancient": 6, "Event": 7}
    L = ["# Relics", "",
         "Effects from the extracted game data `[GAME-EXTRACT]` (hook names kept: `AfterSideTurnStart` = at the start of "
         "your turn, `AfterObtained` = when picked up). The Player's offer, pick and purchase counts, Ancient pick rates and "
         f"final-relic win rates come from solo runs on {build} `[PLAYER-DATA]`. Win rates are survivorship-biased (relics "
         f"obtained late appear only in long runs). Baseline win rate of finished runs: {pct(base_wr)}.", ""]
    for rarity in sorted({r["rarity"] for r in rel}, key=lambda x: order.get(x, 9)):
        sub = sorted([r for r in rel if r["rarity"] == rarity], key=lambda r: r["name"])
        rows = []
        for r in sub:
            rid = r["id"]
            h = holders.get(rid, set())
            wr = f"{pct(sum(fin[x] for x in h) / len(h))} (n={len(h)})" if len(h) >= 8 else (f"n={len(h)}" if h else "-")
            off = offered[rid] or anc_off.get(rid, 0)
            pk = picked[rid] or anc_pick.get(rid, 0)
            rows.append([spaced(r["name"]), r["owner"], esc(r["effect"], 110), f"{pk}/{off}" if off else "-", bought[rid] or "-", wr])
        L += [f"## {rarity} ({len(sub)})", "", md_table(["Relic", "Owner", "Effect", "Picked/offered", "Bought", "Final-relic win rate"], rows), ""]
    (PROJECT / "knowledge/relics.md").write_text("\n".join(L))
    return len(rel)


def potions(con, build):
    pots = json.loads((EX / "potions.json").read_text())
    st = collections.defaultdict(collections.Counter)
    for r in con.execute("""SELECT x.kind, x.potion_id, x.picked FROM potion_events x JOIN runs r USING(run_id)
                            WHERE r.n_players=1 AND r.build_id=?""", [build]):
        pid = r["potion_id"].split(".", 1)[-1]
        st[pid][r["kind"]] += 1
        if r["kind"] == "offered":
            st[pid]["taken"] += r["picked"] or 0
    rows = []
    for p in sorted(pots, key=lambda p: ({"Common": 0, "Uncommon": 1, "Rare": 2}.get(p["rarity"], 3), p["name"])):
        s = st.get(p["id"], {})
        rows.append([spaced(p["name"]), p["rarity"], p["usage"], p["target"], esc(p["behavior"].get("OnUse", ""), 90),
                     f"{s.get('taken', 0)}/{s.get('offered', 0)}" if s.get("offered") else "-", s.get("bought", 0) or "-",
                     s.get("used", 0) or "-", s.get("discarded", 0) or "-"])
    L = ["# Potions", "",
         "Properties and on-use commands from the extracted game data `[GAME-EXTRACT]` (command names, not card text). "
         f"The Player's counts come from solo runs on {build} `[PLAYER-DATA]`.", "",
         md_table(["Potion", "Rarity", "Usage", "Target", "On use (game commands)", "Taken/offered", "Bought", "Used", "Discarded"], rows), ""]
    (PROJECT / "knowledge/potions.md").write_text("\n".join(L))
    return len(pots)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=MAIN_BUILD)
    args = ap.parse_args()
    con = connect()
    print("events:", events(con, args.build), "relics:", relics(con, args.build), "potions:", potions(con, args.build))


if __name__ == "__main__":
    main()
