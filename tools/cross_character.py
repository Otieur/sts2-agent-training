#!/usr/bin/env python3
"""Compare the Player's characters side by side (Phase 5 groundwork and the co-op pairing decision).

Usage: python3 -I tools/cross_character.py [--build v0.107.1]
Writes reports/phase1/cross-character.md
"""
import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_path import logistic_threshold  # noqa: E402
from stslib import MAIN_BUILD, PROJECT, asc_band, connect, md_table, median, pct, short  # noqa: E402

CHARS = ["IRONCLAD", "SILENT", "NECROBINDER", "REGENT"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=MAIN_BUILD)
    args = ap.parse_args()
    con = connect()
    F = "r.n_players = 1 AND r.build_id = ? AND r.character = ?"
    summary, killers, bosses_rows = [], {}, []
    boss_ids = [r[0] for r in con.execute("SELECT DISTINCT model_id FROM floors WHERE room_type='boss'")]
    boss_stats = collections.defaultdict(dict)
    for ch in CHARS:
        P = [args.build, ch]
        runs = {r["run_id"]: dict(r) for r in con.execute(f"SELECT * FROM runs r WHERE {F}", P)}
        fin = {k: v for k, v in runs.items() if not v["abandoned"]}
        bands = collections.defaultdict(lambda: [0, 0])
        for r in fin.values():
            b = asc_band(r["ascension"])
            bands[b][0] += r["win"]
            bands[b][1] += 1
        deaths = []
        for rid, r in fin.items():
            if r["win"]:
                continue
            last = con.execute("SELECT act, map_point_type, model_id FROM floors WHERE run_id=? AND is_last_floor=1", (rid,)).fetchone()
            deaths.append((last["act"], r["killed_by_encounter"] or last["model_id"]))
        by_act = collections.Counter(a for a, _ in deaths)
        killers[ch] = collections.Counter(k for _, k in deaths).most_common(3)
        rests = [dict(x) for x in con.execute(f"SELECT c.* FROM rest_choices c JOIN runs r USING(run_id) WHERE {F}", P)]
        hs = [(x["hp_before"] / x["max_hp"], int(x["choice"] == "HEAL")) for x in rests if x["choice"] in ("HEAL", "SMITH") and x["max_hp"]]
        hsb = [(x["hp_before"] / x["max_hp"], int(x["choice"] == "HEAL")) for x in rests
               if x["choice"] in ("HEAL", "SMITH") and x["max_hp"] and x["next_is_boss"]]
        elites = [dict(x) for x in con.execute(f"""SELECT f.hp_before*1.0/f.max_hp AS hp,
            f.is_last_floor AND NOT r.win AND NOT r.abandoned AS died FROM floors f JOIN runs r USING(run_id)
            WHERE {F} AND f.room_type='elite' AND f.act IN (1,2) AND NOT r.abandoned""", P)]
        low = [e for e in elites if e["hp"] < 0.5]
        hi = [e for e in elites if e["hp"] >= 0.5]
        hp15 = collections.defaultdict(list)
        for x in con.execute(f"""SELECT f.hp_after*1.0/f.max_hp AS hp, r.win FROM floors f JOIN runs r USING(run_id)
                                 WHERE {F} AND f.floor=15 AND NOT r.abandoned""", P):
            hp15["win" if x["win"] else "loss"].append(x["hp"])
        summary.append([
            ch.title(), len(runs), f"{sum(r['win'] for r in fin.values())}/{len(fin)}",
            " · ".join(f"{b} {bands[b][0]}/{bands[b][1]}" for b in ("A0-4", "A5-9", "A10") if bands[b][1]),
            " / ".join(str(by_act.get(a, 0)) for a in (1, 2, 3)),
            pct(logistic_threshold(hs)[0]), pct(logistic_threshold(hsb)[0]),
            f"{sum(e['died'] for e in low)}/{len(low)} vs {sum(e['died'] for e in hi)}/{len(hi)}",
            f"{pct(median(hp15['win']))} vs {pct(median(hp15['loss']))}" if hp15["win"] and hp15["loss"] else "-",
        ])
        for b in boss_ids:
            xs = [dict(x) for x in con.execute(f"""SELECT f.damage_taken, f.is_last_floor AND NOT r.win AND NOT r.abandoned AS died
                FROM floors f JOIN runs r USING(run_id) WHERE {F} AND f.model_id=?""", P + [b])]
            if xs:
                boss_stats[b][ch] = (len(xs), sum(x["died"] for x in xs), median([x["damage_taken"] for x in xs]))

    L = ["# Cross-Character Comparison", "",
         f"The Player's solo runs on {args.build}, by character. Built by `tools/cross_character.py`. `[PLAYER-DATA]`", "",
         md_table(["Character", "Runs", "Wins / finished", "Wins by band", "Deaths Act 1/2/3", "Heal-vs-smith point",
                   "…before a boss", "Elite deaths: <50% HP vs ≥50%", "HP after floor 15: wins vs losses"], summary), "",
         "## Most frequent killers", ""]
    for ch in CHARS:
        L.append(f"- **{ch.title()}:** " + ", ".join(f"{short(k)} ×{n}" for k, n in killers[ch]))
    L += ["", "## Bosses by character (fights / fatal / median damage)", "",
          md_table(["Boss"] + [c.title() for c in CHARS],
                   [[short(b)] + [f"{boss_stats[b][c][0]} / {boss_stats[b][c][1]} / {boss_stats[b][c][2]:.0f}" if c in boss_stats[b] else "-"
                                  for c in CHARS] for b in sorted(boss_stats)]), "",
          "## Notes for the co-op pairing decision (P5.E6.S2)", "",
          "- The Player's habits are consistent across characters: low rest thresholds and the same elite risk pattern. The playbook rules (rest thresholds, elite HP rule) apply to every character.",
          "- Boss weaknesses differ by character. A pairing where the Agent's character covers the boss the Player's character struggles with is worth more than raw win rate. See the boss table above.",
          "- Character-specific mechanics (Necrobinder's companion, Regent's Stars) need their own Phase 5 knowledge pass before the Agent can play them.", ""]
    out = PROJECT / "reports/phase1/cross-character.md"
    out.write_text("\n".join(L))
    print("wrote", out.relative_to(PROJECT))


if __name__ == "__main__":
    main()
