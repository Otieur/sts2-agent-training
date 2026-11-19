#!/usr/bin/env python3
"""Sanity checks for data/runs.db. Exit code 1 if any hard check fails.

Usage: python3 -I tools/validate_data.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import connect  # noqa: E402

EXPECTED_SOLO = {"IRONCLAD": 57, "NECROBINDER": 59, "REGENT": 53, "SILENT": 52, "DEFECT": 7, "FOOL": 4}


def main():
    con = connect()
    results = []  # (name, ok, hard, detail)

    def check(name, ok, detail="", hard=True):
        results.append((name, bool(ok), hard, detail))

    total = con.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
    check("unique runs = 233 (as of 2026-11-18; more is fine)", total >= 233, f"found {total}")

    got = dict(con.execute("SELECT character, COUNT(*) FROM runs WHERE n_players=1 GROUP BY character"))
    for ch, n in EXPECTED_SOLO.items():
        check(f"solo {ch} runs >= {n}", got.get(ch, 0) >= n, f"found {got.get(ch, 0)}")

    neg = con.execute("SELECT COUNT(*) FROM floors WHERE damage_taken < 0 OR hp_healed < 0").fetchone()[0]
    check("no negative damage or healing", neg == 0, f"{neg} rows")

    over = con.execute("SELECT COUNT(*) FROM floors WHERE hp_after > max_hp").fetchone()[0]
    check("hp_after never above max_hp", over == 0, f"{over} rows")

    # hp_after should equal hp_before - damage + healed, except when max HP changed on the floor
    rows = con.execute("""SELECT COUNT(*),
        SUM(CASE WHEN hp_after = hp_before - damage_taken + hp_healed THEN 1 ELSE 0 END)
        FROM floors WHERE floor > 1 AND max_hp_gained = 0 AND max_hp_lost = 0""").fetchone()
    rate = rows[1] / rows[0]
    check("HP arithmetic consistent on >= 99% of floors", rate >= 0.99, f"{rows[1]}/{rows[0]} = {rate:.2%}")

    bad_wins = con.execute("""SELECT COUNT(*) FROM runs r WHERE win = 1 AND n_players = 1 AND NOT EXISTS (
        SELECT 1 FROM floors f WHERE f.run_id = r.run_id AND f.is_last_floor = 1 AND f.map_point_type = 'boss')""").fetchone()[0]
    check("every solo win ends on a boss floor", bad_wins == 0, f"{bad_wins} runs")

    m = con.execute("SELECT COUNT(*), SUM(deck_match_ids), SUM(deck_match_levels) FROM runs WHERE n_players=1").fetchone()
    check("deck reconstruction matches final deck (ids) in >= 95% of runs", m[1] / m[0] >= 0.95, f"{m[1]}/{m[0]}")
    check("deck reconstruction matches including upgrade levels in >= 95%", m[2] / m[0] >= 0.95, f"{m[2]}/{m[0]}")

    zero_turn = con.execute("""SELECT COUNT(*) FROM floors WHERE room_type IN ('monster','elite','boss')
        AND (turns_taken IS NULL OR turns_taken = 0)""").fetchone()[0]
    check("every fight has turns_taken > 0", zero_turn == 0, f"{zero_turn} fights", hard=False)

    suffix = con.execute("""SELECT COUNT(*) FROM floors WHERE room_type IN ('monster','elite','boss')
        AND model_id NOT LIKE '%\\_WEAK' ESCAPE '\\' AND model_id NOT LIKE '%\\_NORMAL' ESCAPE '\\'
        AND model_id NOT LIKE '%\\_ELITE' ESCAPE '\\' AND model_id NOT LIKE '%\\_BOSS' ESCAPE '\\'""").fetchone()[0]
    check("every encounter ID has a pool suffix", suffix == 0, f"{suffix} fights", hard=False)

    multi = con.execute("SELECT COUNT(*) FROM floors WHERE room_types LIKE '%,%'").fetchone()[0]
    check("map points with more than one room (informational)", True, f"{multi} floors", hard=False)

    width = max(len(r[0]) for r in results)
    failed_hard = 0
    for name, ok, hard, detail in results:
        tag = "PASS" if ok else ("FAIL" if hard else "WARN")
        failed_hard += (not ok) and hard
        print(f"{tag}  {name.ljust(width)}  {detail}")
    sys.exit(1 if failed_hard else 0)


if __name__ == "__main__":
    main()
