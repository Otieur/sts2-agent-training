#!/usr/bin/env python3
"""Replay the Player's deaths through the playbook's checks: for every run that died, which rules would have
flagged the danger before the fatal fight? Quantifies where following the playbook could beat the baseline.

Checks per fatal fight (playbooks/ironclad.md):
  - H5: an elite entered under 50% HP
  - H1: the last rest site before a fatal boss: the rule said rest and the Player smithed
  - H9: at a fatal boss, the deck missed the act's corner targets (block per turn, scaling count)
  - Boss checklist: countable items from tools/deck_check.py (for example Vantom's single-hit hit-all count)
Flags are not proof that following the rule would have saved the run. [PLAYER-DATA, observational]

Output: reports/phase2/death-review-<character>.md. Usage: python3 -I tools/death_review.py [--character IRONCLAD]
"""
import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deck_check  # noqa: E402
import draft  # noqa: E402
import path as pathmod  # noqa: E402
from deck_metrics import deck_at  # noqa: E402
from stslib import MAIN_BUILD, PROJECT, connect, md_table, pct  # noqa: E402


def boss_flags(con, ch, run_id, floor, act, model_id, ascension):
    """Flags for one boss fight (fatal or not): H1 rest-rule violation, H9 corner-target gaps, boss checklist gaps."""
    flags = []
    enc = (model_id or "").replace("ENCOUNTER.", "")
    rest = con.execute("SELECT choice, hp_before, max_hp FROM rest_choices WHERE run_id = ? AND floor = ?", (run_id, floor - 1)).fetchone()
    if rest and rest["choice"] in ("HEAL", "SMITH"):
        thr = pathmod.get_model(ch, ascension).boss_threshold(act, model_id, rest["max_hp"])
        if rest["hp_before"] < thr and rest["choice"] == "SMITH":
            flags.append(f"H1: smithed at {rest['hp_before']} HP, rule said rest (below {thr:.0f})")
    deck = deck_at(con, run_id, floor)
    for ln in deck_check.check(deck, act, enc).splitlines():
        ln = ln.strip()
        if ln.startswith("GAP"):
            g = ln[5:]
            flags.append(("H9: " if ("H9" in g or g.startswith("damage/turn")) else "Boss checklist: ") + g.split(" (")[0])
    return flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", default="IRONCLAD")
    args = ap.parse_args()
    ch = args.character.upper()
    con = connect()
    deaths = [dict(r) for r in con.execute("""
        SELECT r.run_id, r.ascension, f.floor, f.act, f.room_type, f.model_id, f.hp_before, f.max_hp
        FROM runs r JOIN floors f ON f.run_id = r.run_id AND f.is_last_floor = 1
        WHERE r.build_id = ? AND r.character = ? AND r.n_players = 1 AND NOT r.win AND NOT r.abandoned
          AND f.room_type IN ('monster','elite','boss')""", [MAIN_BUILD, ch])]
    rows, flag_counts = [], collections.Counter()
    for d in deaths:
        flags = []
        frac = d["hp_before"] / d["max_hp"]
        enc = (d["model_id"] or "").replace("ENCOUNTER.", "")
        if d["room_type"] == "elite" and frac < 0.5:
            flags.append(f"H5: elite at {frac:.0%} HP")
        if d["room_type"] == "monster" and frac < 0.4:
            flags.append(f"H11: hallway fight at {frac:.0%} HP")
        if d["room_type"] == "boss":
            flags += boss_flags(con, ch, d["run_id"], d["floor"], d["act"], d["model_id"], d["ascension"])
        for kind in {f.split(":")[0] for f in flags}:
            flag_counts[kind] += 1
        rows.append([d["run_id"].split("-")[-1], f"A{d['ascension']}", d["floor"], d["room_type"], enc.replace("_", " ").title(),
                     f"{frac:.0%}", "; ".join(flags) or "none"])
    # Base rates: the same boss checks on every boss fight, survived or fatal
    base = {True: collections.Counter(), False: collections.Counter()}
    nb = {True: 0, False: 0}
    for b in con.execute("""
        SELECT r.run_id, r.ascension, f.floor, f.act, f.model_id, (f.is_last_floor AND NOT r.win) AS died
        FROM runs r JOIN floors f USING(run_id)
        WHERE r.build_id = ? AND r.character = ? AND r.n_players = 1 AND NOT r.abandoned AND f.room_type = 'boss'""", [MAIN_BUILD, ch]):
        fl = boss_flags(con, ch, b["run_id"], b["floor"], b["act"], b["model_id"], b["ascension"])
        died = bool(b["died"])
        nb[died] += 1
        kinds = {f.split(":")[0] for f in fl}
        for k in kinds | ({"any"} if kinds else set()):
            base[died][k] += 1
    con.close()
    flagged = sum(1 for r in rows if r[-1] != "none")
    n = len(rows)
    by_type = collections.Counter(r[3] for r in rows)
    flagged_by_type = collections.Counter(r[3] for r in rows if r[-1] != "none")
    L = [f"# Death Review ({ch.title()})", "",
         f"The Player's {n} {ch.title()} deaths on {MAIN_BUILD} (solo, finished runs), replayed through the playbook's checks "
         "before the fatal fight. Built by `tools/death_review.py`. A flag means the playbook would have warned; it does not "
         "prove the run would have survived. `[PLAYER-DATA, observational]`", "",
         f"**{flagged} of {n} deaths ({pct(flagged / n)}) had at least one flag.**", "",
         md_table(["Fight type", "Deaths", "Flagged"], [[t, by_type[t], flagged_by_type[t]] for t in ("boss", "elite", "monster") if by_type[t]]), "",
         md_table(["Check", "Deaths flagged"], [[k, v] for k, v in flag_counts.most_common()]), "",
         "**Base rate at bosses** (the same checks on every boss fight; a check is informative only if it flags fatal "
         "fights more often than survived ones):", "",
         md_table(["Check", f"Fatal boss fights (n={nb[True]})", f"Survived boss fights (n={nb[False]})"],
                  [[k, pct(base[True][k] / nb[True]) if nb[True] else "-", pct(base[False][k] / nb[False]) if nb[False] else "-"]
                   for k in ("any", "H1", "H9", "Boss checklist")]), "",
         "## Every death", "",
         md_table(["Seed", "Asc", "Floor", "Room", "Encounter", "Entry HP", "Flags"], rows), "",
         "H11 (hallway fights under 40% HP) covers hallway deaths since 2026-11-19. Boss checklist items are the countable ones in "
         "`tools/deck_check.py`; card values are v0.111.1, applied to v0.107.1 decks.", ""]
    out = PROJECT / f"reports/phase2/death-review-{ch.lower()}.md"
    out.write_text("\n".join(L))
    print("wrote", out.relative_to(PROJECT), f"{flagged}/{n} flagged")


if __name__ == "__main__":
    main()
