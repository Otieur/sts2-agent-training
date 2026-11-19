#!/usr/bin/env python3
"""Consistency check: recompute the playbook's data-backed figures from data/runs.db and the benchmark files, and
report any figure in playbooks/ironclad.md that no longer matches (Never-idle consistency pass, 2026-11-19).

Each check computes a value and the exact text the playbook should contain. Run after rebuilding the dataset or
editing the playbook:  python3 -I tools/check_playbook.py   (exit code 1 if anything is missing)
"""
import csv
import json
import sqlite3
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import DATA, PROJECT  # noqa: E402

PLAYBOOK = PROJECT / "playbooks" / "ironclad.md"
SOLO_IRON = "r.build_id='v0.107.1' AND r.character='IRONCLAD' AND r.n_players=1"
FATAL = "(r.win=0 AND r.abandoned=0 AND f.is_last_floor=1)"


def checks(con):
    q = lambda sql: con.execute(sql).fetchall()  # noqa: E731
    out = []

    # Section 1: deaths
    d = dict(q(f"SELECT f.act, COUNT(*) FROM runs r JOIN floors f USING(run_id) WHERE {SOLO_IRON} AND {FATAL} GROUP BY f.act"))
    n = sum(d.values())
    out.append(("deaths in Act 1", f"{round(100 * d.get(1, 0) / n)}% of deaths happen in Act 1 ({d.get(1, 0)}/{n})"))
    rt = dict(q(f"SELECT f.room_type, COUNT(*) FROM runs r JOIN floors f USING(run_id) WHERE {SOLO_IRON} AND {FATAL} GROUP BY 1"))
    out.append(("deaths by type", f"{rt.get('boss', 0)} deaths to bosses, {rt.get('elite', 0)} to elites, {rt.get('monster', 0)} in hallways"))

    # Section 4: elites by arrival HP (all characters, Acts 1-2, abandoned runs excluded)
    rows = q("""SELECT r.character, 1.0*f.hp_before/f.max_hp, (r.win=0 AND f.is_last_floor=1) FROM runs r JOIN floors f USING(run_id)
                WHERE r.build_id='v0.107.1' AND r.n_players=1 AND r.abandoned=0 AND f.room_type='elite' AND f.act IN (1,2)""")
    out.append(("elite sample", f"n={len(rows)} elite fights in Acts 1–2"))
    band = lambda h: "lo" if h < 0.5 else ("mid" if h < 0.7 else "hi")  # noqa: E731
    iron = {b: [x[2] for x in rows if x[0] == "IRONCLAD" and band(x[1]) == b] for b in ("lo", "mid", "hi")}
    allc = {b: [x[2] for x in rows if band(x[1]) == b] for b in ("lo", "mid", "hi")}
    out.append(("elites under 50%", f"{round(100 * sum(allc['lo']) / len(allc['lo']))}% of fights entered under 50% HP ended the run (Ironclad {sum(iron['lo'])}/{len(iron['lo'])})"))
    out.append(("elites 50-70%", f"{round(100 * sum(allc['mid']) / len(allc['mid']))}% at 50–70% (Ironclad {sum(iron['mid'])}/{len(iron['mid'])})"))
    out.append(("elites 70%+", f"{round(100 * sum(allc['hi']) / len(allc['hi']))}% at 70% or more (Ironclad {sum(iron['hi'])}/{len(iron['hi'])})"))

    # Section 4 and 10: elite and boss tables (median / p75 from the pooled benchmark, fatal from the database)
    bench = {r["encounter"]: r for r in csv.DictReader(open(DATA / "benchmarks" / "ironclad-encounters-v0.107.1.csv"))}
    fatal = {m: (k, t) for m, k, t in q(f"""SELECT f.model_id, SUM({FATAL}), COUNT(*) FROM runs r JOIN floors f USING(run_id)
                                           WHERE {SOLO_IRON} AND f.room_type IN ('elite','boss') GROUP BY 1""")}
    for enc, label in (("BYGONE_EFFIGY_ELITE", "Bygone Effigy"), ("TERROR_EEL_ELITE", "Terror Eel"), ("BYRDONIS_ELITE", "Byrdonis"),
                       ("PHROG_PARASITE_ELITE", "Phrog Parasite"), ("SKULKING_COLONY_ELITE", "Skulking Colony"),
                       ("PHANTASMAL_GARDENERS_ELITE", "Phantasmal Gardeners"), ("DECIMILLIPEDE_ELITE", "Decimillipede"),
                       ("ENTOMANCER_ELITE", "Entomancer"), ("INFESTED_PRISMS_ELITE", "Infested Prisms"),
                       ("MECHA_KNIGHT_ELITE", "Mecha Knight")):
        b, (k, t) = bench["ENCOUNTER." + enc], fatal["ENCOUNTER." + enc]
        out.append((label, f"| {label} | {float(b['median_dmg']):g} / {float(b['p75_dmg']):g} | {k}/{t} |"))
    for enc, label in (("VANTOM_BOSS", "Vantom"), ("CEREMONIAL_BEAST_BOSS", "Ceremonial Beast"), ("THE_KIN_BOSS", "The Kin"),
                       ("WATERFALL_GIANT_BOSS", "Waterfall Giant"), ("SOUL_FYSH_BOSS", "Soul Fysh"),
                       ("LAGAVULIN_MATRIARCH_BOSS", "Lagavulin Matriarch"), ("KNOWLEDGE_DEMON_BOSS", "Knowledge Demon"),
                       ("KAISER_CRAB_BOSS", "Kaiser Crab"), ("THE_INSATIABLE_BOSS", "The Insatiable"),
                       ("AEONGLASS_BOSS", "Aeonglass"), ("TEST_SUBJECT_BOSS", "Test Subject"), ("QUEEN_BOSS", "Queen")):
        b, (k, t) = bench["ENCOUNTER." + enc], fatal["ENCOUNTER." + enc]
        out.append((label, f"| {float(b['median_dmg']):g} / {float(b['p75_dmg']):g} | {k}/{t} |"))

    # Section 5: rest heal
    heals = q("""SELECT f.hp_healed, f.max_hp, f.hp_before FROM floors f JOIN rest_choices c ON c.run_id=f.run_id AND c.floor=f.floor
                 JOIN runs r ON r.run_id=f.run_id WHERE c.choice='HEAL' AND r.build_id='v0.107.1'""")
    exact = sum(1 for h, m, _ in heals if h == int(m * 0.3))
    out.append(("rest heal", f"{exact} of {len(heals)} heals match exactly"))

    # Section 8: potions per boss and elite fight
    pot = {rt_: (u, n_) for rt_, n_, u in q(f"""SELECT f.room_type, COUNT(DISTINCT f.run_id||'-'||f.floor),
              SUM(p.kind='used') FROM floors f JOIN runs r USING(run_id) LEFT JOIN potion_events p ON p.run_id=f.run_id AND p.floor=f.floor
              WHERE {SOLO_IRON} AND f.room_type IN ('elite','boss') GROUP BY 1""")}
    out.append(("potions", f"about {pot['boss'][0] / pot['boss'][1]:.1f} per boss fight and {pot['elite'][0] / pot['elite'][1]:.1f} per elite"))

    # H8: arrival HP, survived against fatal (all characters, abandoned runs excluded)
    for enc, label in (("QUEEN_BOSS", "Queen"), ("THE_KIN_BOSS", "The Kin"), ("AEONGLASS_BOSS", "Aeonglass"),
                       ("VANTOM_BOSS", "Vantom"), ("WATERFALL_GIANT_BOSS", "Waterfall Giant")):
        xs = q(f"""SELECT 1.0*f.hp_before/f.max_hp, (r.win=0 AND f.is_last_floor=1) FROM floors f JOIN runs r USING(run_id)
                   WHERE r.build_id='v0.107.1' AND r.n_players=1 AND r.abandoned=0 AND f.model_id='ENCOUNTER.{enc}'""")
        s = round(100 * statistics.median([h for h, k in xs if not k]))
        f_ = round(100 * statistics.median([h for h, k in xs if k]))
        out.append((f"H8 {label}", f"{label} {s}% / {f_}%"))
    # Section 2.1 and H9: deck-strength figures, read from the generated report (tools/deck_metrics.py)
    import re
    rep = (PROJECT / "reports" / "phase2" / "deck-strength.md").read_text()
    m = re.search(r"\(Act 1: (\d+%) against (\d+%);", rep)
    out.append(("raw damage Act 1", f"(Act 1: {m.group(1)} against {m.group(2)})" if m else "<pattern not found in deck-strength.md>"))
    m = re.search(r"more raw damage \(([\d.]+) against ([\d.]+) per turn\)", rep)
    out.append(("Ironclad fatal decks", f"more damage ({m.group(1)} against {m.group(2)} per turn)" if m else "<pattern not found in deck-strength.md>"))
    m = re.search(r"- \*\*Act 1:\*\* low \([^)]*\): \d+/\d+ fatal \((\d+%)\) · middle \([^)]*\): \d+/\d+ fatal \((\d+%)\) · high \([^)]*\): \d+/\d+ fatal \((\d+%)\)", rep)
    out.append(("H9 terciles", f"Act 1 fatal {m.group(1)} / {m.group(2)} / {m.group(3)} (low to high)" if m else "<pattern not found in deck-strength.md>"))
    # H2, H3, H7: deck features by encounter (tools/analyze_deck_features.py)
    feat = (PROJECT / "reports" / "phase2" / "deck-features-by-encounter.md").read_text()

    def feature(enc, row):
        sec = feat.split(f"## {enc}", 1)[1].split("\n## ", 1)[0]
        m = re.search(rf"\| {re.escape(row)} \| ([\d.]+) \| ([\d.]+) \|", sec)
        return (m.group(1), m.group(2)) if m else ("?", "?")
    s, f = feature("KNOWLEDGE_DEMON_BOSS", "Powers")
    out.append(("H7 powers", f"powers {f} against {s}"))
    s, f = feature("KNOWLEDGE_DEMON_BOSS", "Energy cards")
    out.append(("H7 energy", f"energy {f} against {s}"))
    s, f = feature("VANTOM_BOSS", "Single-hit hit-all attacks")
    out.append(("H2 hit-all", f"({f} against {s})"))
    s, f = feature("VANTOM_BOSS", "Draw cards")
    out.append(("H2 draw", f"less draw ({f} against {s})"))
    s, f = feature("ENTOMANCER_ELITE", "Attacks costing 0–1")
    out.append(("H3 cheap attacks", f"more cheap attacks ({f} against {s})"))
    # Section 2.2: tier check against decision-point outcomes (tools/analyze_card_choices.py)
    cc = (PROJECT / "reports" / "phase2" / "card-choices-ironclad.md").read_text()
    m = re.search(r"\| A \| \d+ \| ([+-][\d.]+) pts", cc)
    out.append(("A-tier pick effect", f"A-tier picks {float(m.group(1)):+.0f} points" if m else "<pattern not found in card-choices-ironclad.md>"))
    m = re.search(r"\| Breakthrough \| \w \| (\d+) \| \d+ \| (\d+)% \(\d+/\d+\) \| (\d+)% \(\d+/\d+\) \| [+-]\d+ pts \| ([\d.]+)", cc)
    out.append(("Breakthrough", f"picked {m.group(1)} times, survived the act {m.group(2)}% against {m.group(3)}% when passed (p = {m.group(4)})"
                if m else "<pattern not found in card-choices-ironclad.md>"))
    # Section 4: fight model coefficients (tools/fight_model.py)
    fm = json.loads((DATA / "tables" / "fight_model.json").read_text())
    e1, b2, m1 = fm["1:elite"], fm["2:boss"], fm["1:monster"]
    out.append(("fight model block", f"each point of block per turn saves about {abs(100 * e1['blk']):.1f} points in Act 1 elites"))
    out.append(("fight model scaling", f"each scaling card saves about {abs(100 * b2['scaling']):.1f} points at the Act 2 boss but costs about "
                                       f"{100 * m1['scaling']:.1f} points in Act 1 hallways"))
    return out


def main():
    text = PLAYBOOK.read_text()
    con = sqlite3.connect(DATA / "runs.db")
    bad = 0
    for name, expect in checks(con):
        ok = expect in text
        bad += not ok
        print(("ok    " if ok else "MISS  ") + f"{name}: {expect}")
    print(f"\n{bad} mismatch(es)" if bad else "\nall figures match")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
