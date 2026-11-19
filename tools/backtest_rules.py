#!/usr/bin/env python3
"""Backtest playbook rules against the run history, split by ascension band (all characters, solo, finished runs).

H4: removing a Strike/Defend in Act 1 vs Act 1 survival, among runs that had the chance (an Act 1 shop with 75+ gold).
H5: elite fights in Acts 1-2 that ended the run, by HP on arrival (<50% vs >=50%).
H1: pre-boss rest sites: the playbook's rest rule (section 5, the same thresholds as tools/path.py) against the
Player's choice, and the boss fight's outcome.

Observational evidence; confounders noted in the report.
Usage: python3 -I tools/backtest_rules.py   → reports/phase2/rule-backtests.md
"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import MAIN_BUILD, PROJECT, asc_band, connect, md_table, pct  # noqa: E402

BANDS = ("A0-4", "A5-9", "A10")


def fmt(k, n):
    return f"{k}/{n} ({pct(k / n)})" if n else "-"


def main():
    con = connect()
    runs = {r["run_id"]: dict(r) for r in con.execute(
        "SELECT * FROM runs WHERE n_players = 1 AND build_id = ? AND abandoned = 0", [MAIN_BUILD])}
    h4 = collections.defaultdict(lambda: [0, 0, 0, 0])
    for rid, r in runs.items():
        shops = [s[0] for s in con.execute("SELECT gold_before FROM shop_visits WHERE run_id=? AND act=1", (rid,))]
        if not shops or max(shops) < 75:
            continue
        removed = con.execute("""SELECT COUNT(*) FROM deck_changes WHERE run_id=? AND change='removed' AND floor<=17
                                 AND (card_id LIKE 'CARD.STRIKE%' OR card_id LIKE 'CARD.DEFEND%')""", (rid,)).fetchone()[0]
        max_act = con.execute("SELECT MAX(act) FROM floors WHERE run_id=?", (rid,)).fetchone()[0]
        survived = int(max_act >= 2 or r["win"])
        for b in (asc_band(r["ascension"]), "All"):
            i = 0 if removed else 2
            h4[b][i] += survived
            h4[b][i + 1] += 1
    elites = [dict(x) for x in con.execute("""
        SELECT r.ascension, f.hp_before * 1.0 / f.max_hp AS hp, (f.is_last_floor AND NOT r.win AND NOT r.abandoned) AS died
        FROM floors f JOIN runs r USING(run_id)
        WHERE r.n_players = 1 AND r.build_id = ? AND f.room_type = 'elite' AND f.act IN (1, 2) AND NOT r.abandoned""", [MAIN_BUILD])]
    h5 = []
    for b in BANDS + ("All",):
        xs = elites if b == "All" else [x for x in elites if asc_band(x["ascension"]) == b]
        lo = [x for x in xs if x["hp"] < 0.5]
        hi = [x for x in xs if x["hp"] >= 0.5]
        h5.append([b, fmt(sum(x["died"] for x in lo), len(lo)), fmt(sum(x["died"] for x in hi), len(hi))])
    # H1: pre-boss rests against the rule
    import path as pathmod
    h1 = collections.defaultdict(lambda: [0, 0])
    for r in con.execute("""
        SELECT c.run_id, c.floor, c.act, c.choice, c.hp_before, c.max_hp, r.character, r.ascension,
               (SELECT g.model_id FROM floors g WHERE g.run_id = c.run_id AND g.floor = c.floor + 1) AS boss,
               (SELECT g.is_last_floor AND NOT r.win FROM floors g WHERE g.run_id = c.run_id AND g.floor = c.floor + 1) AS died
        FROM rest_choices c JOIN runs r USING(run_id)
        WHERE r.n_players = 1 AND r.build_id = ? AND NOT r.abandoned AND c.next_is_boss = 1 AND c.choice IN ('HEAL','SMITH')""",
            [MAIN_BUILD]):
        if r["died"] is None or not r["boss"]:
            continue
        model = pathmod.get_model(r["character"], r["ascension"])
        thr = model.boss_threshold(r["act"], r["boss"], r["max_hp"])
        rule = "HEAL" if r["hp_before"] < thr else "SMITH"
        case = f"rule {rule.lower()}, Player {r['choice'].lower()}"
        h1[case][0] += r["died"]
        h1[case][1] += 1
        key = "matched" if rule == r["choice"] else "differed"
        h1[key][0] += r["died"]
        h1[key][1] += 1
    L = ["# Rule Backtests", "",
         f"All characters, solo, {MAIN_BUILD}, finished runs. Built by `tools/backtest_rules.py`. `[PLAYER-DATA]`, observational.", "",
         "## H4: remove a basic card in Act 1", "",
         "Only runs that reached an Act 1 shop with at least 75 gold (they had the chance). Outcome: survived Act 1.", "",
         md_table(["Band", "Removed a Strike/Defend in Act 1", "Did not"], [[b, fmt(h4[b][0], h4[b][1]), fmt(h4[b][2], h4[b][3])] for b in BANDS + ("All",)]), "",
         "Reading: a clear gap at A5–9 and A10, none at A0–4. Remaining confounders: gold amount and shop timing (richer runs can "
         "both remove and buy), and the Player's choice to remove when the deck already looked good. Supports testing H4 "
         "at A5 and above.", "",
         "## H5: elites under 50% HP", "",
         md_table(["Band", "Entered under 50% HP: fatal", "Entered at 50% or more: fatal"], h5), "",
         "Reading: the danger holds in every band and is strongest at A5 and above (about 3–5 times the fatal rate). Kept as a rule.", "",
         "## H1: rest before the boss by the playbook rule", "",
         "Pre-boss rest sites where the Player chose HEAL or SMITH. The rule: Acts 1–2 rest below the boss's band median + 10, "
         "Act 3 below 70% (playbook section 5; thresholds from `tools/path.py`). Outcome: the boss fight ended the run.", "",
         md_table(["Case", "Boss fights", "Fatal"], [[k, v[1], fmt(v[0], v[1])] for k, v in sorted(h1.items())]), "",
         "Reading: if following the rule helps, \"rule heal, Player smith\" should be the most dangerous row. Arrival HP and "
         "deck strength are confounded with the choice, so treat this as a consistency check, not proof.", ""]
    out = PROJECT / "reports/phase2/rule-backtests.md"
    out.write_text("\n".join(L))
    print("wrote", out.relative_to(PROJECT))


if __name__ == "__main__":
    main()
