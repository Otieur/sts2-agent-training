#!/usr/bin/env python3
"""Ancient relic choices: outcome when a relic was picked against when it was offered and passed, at the same
decision point (the act-start Ancient). Comparing at the same point removes the acquisition-time bias that makes
raw "win rate with relic" lists useless (relics found late look strong because only strong runs get there).

Still confounded by the Player's reasons for picking, and samples are small: treat as [PLAYER-DATA, weak].

Outputs reports/phase2/ancient-relics.md and data/tables/ancient_relics.csv (used by tools/advise.py).
Usage: python3 -I tools/analyze_ancients.py
"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import DATA, MAIN_BUILD, PROJECT, connect, md_table, pct, wilson, write_csv  # noqa: E402

MIN_OFFERED = 5


def fisher_two_sided(a, b, c, d):
    """Two-sided Fisher exact test for the 2x2 table [[a, b], [c, d]] (a = picked & survived, b = picked & died,
    c = passed & survived, d = passed & died)."""
    from math import comb
    n1, n2, k = a + b, c + d, a + c
    n = n1 + n2
    def prob(x):
        return comb(n1, x) * comb(n2, k - x) / comb(n, k)
    p0 = prob(a)
    lo, hi = max(0, k - n2), min(k, n1)
    return min(1.0, sum(prob(x) for x in range(lo, hi + 1) if prob(x) <= p0 * (1 + 1e-9)))


def main():
    con = connect()
    runs = {r["run_id"]: dict(r) for r in con.execute(
        "SELECT run_id, win, abandoned, character, ascension FROM runs WHERE n_players = 1 AND build_id = ?", [MAIN_BUILD])}
    max_act = {r[0]: r[1] for r in con.execute("SELECT run_id, MAX(act) FROM floors GROUP BY run_id")}
    rows = [dict(r) for r in con.execute("SELECT run_id, act, ancient_id, option, chosen FROM ancient_choices")]
    stats = collections.defaultdict(lambda: {"offered": 0, "chosen": 0, "acts": collections.Counter(),
                                             "win_c": [0, 0], "win_p": [0, 0], "surv_c": [0, 0], "surv_p": [0, 0],
                                             "ancients": collections.Counter()})
    for r in rows:
        run = runs.get(r["run_id"])
        if not run or run["abandoned"]:
            continue
        s = stats[r["option"]]
        s["offered"] += 1
        s["acts"][r["act"]] += 1
        s["ancients"][r["ancient_id"].replace("EVENT.", "")] += 1
        survived = int(run["win"] or (max_act.get(r["run_id"], 0) > r["act"]))
        key = "c" if r["chosen"] else "p"
        s["chosen"] += r["chosen"]
        s[f"win_{key}"][0] += run["win"]
        s[f"win_{key}"][1] += 1
        s[f"surv_{key}"][0] += survived
        s[f"surv_{key}"][1] += 1
    out_rows, table = [], []
    for opt, s in sorted(stats.items(), key=lambda kv: -kv[1]["offered"]):
        if s["offered"] < MIN_OFFERED:
            continue
        def rate(x):
            return x[0] / x[1] if x[1] else None
        wc, wp, sc, sp = rate(s["win_c"]), rate(s["win_p"]), rate(s["surv_c"]), rate(s["surv_p"])
        diff = (sc - sp) if sc is not None and sp is not None else None
        pval = fisher_two_sided(s["surv_c"][0], s["surv_c"][1] - s["surv_c"][0], s["surv_p"][0], s["surv_p"][1] - s["surv_p"][0]) \
            if s["surv_c"][1] and s["surv_p"][1] else None
        acts = "/".join(str(a) for a in sorted(s["acts"]))
        out_rows.append([opt, acts, s["offered"], s["chosen"], f"{wc:.3f}" if wc is not None else "",
                         f"{wp:.3f}" if wp is not None else "", f"{sc:.3f}" if sc is not None else "",
                         f"{sp:.3f}" if sp is not None else "", f"{diff:+.3f}" if diff is not None else "",
                         f"{pval:.3f}" if pval is not None else ""])
        def fmt(x):
            return f"{pct(x[0] / x[1])} ({x[0]}/{x[1]})" if x[1] else "-"
        table.append([opt.replace("_", " ").title(), acts, s["offered"], s["chosen"], fmt(s["surv_c"]), fmt(s["surv_p"]),
                      f"{100 * diff:+.0f} pts" if diff is not None else "-", f"{pval:.2f}" if pval is not None else "-",
                      fmt(s["win_c"]), fmt(s["win_p"])])
    write_csv(DATA / "tables" / "ancient_relics.csv",
              ["relic", "acts", "offered", "chosen", "win_chosen", "win_passed", "survive_act_chosen", "survive_act_passed",
               "survive_diff", "p_survive"], out_rows)
    L = ["# Ancient Relic Choices", "",
         f"All characters, solo, {MAIN_BUILD}, finished runs. Built by `tools/analyze_ancients.py`. For each option offered "
         f"by an act-start Ancient ({MIN_OFFERED}+ offers): how often the run survived that act, and won, when the Player "
         "picked it against when the Player passed it. Same decision point, so acquisition time is not a bias, unlike raw "
         "relic win rates (MetaBot's relic list puts Burning Blood, carried by every Ironclad from floor 1, at 14%). "
         "`[PLAYER-DATA, weak]`: small samples, and the Player's reasons for picking are a confounder.", "",
         md_table(["Option", "Acts", "Offered", "Picked", "Survived act (picked)", "Survived act (passed)", "Difference",
                   "p (Fisher)", "Won (picked)", "Won (passed)"], table), "",
         "Reading: p is a two-sided Fisher exact test on act survival, picked against passed. With 90 options tested, "
         "about 4–5 would show p < 0.05 by chance, so only large, repeated effects count. Options can be relics, card packs "
         "or other boons, depending on the Ancient.", ""]
    out = PROJECT / "reports/phase2/ancient-relics.md"
    out.write_text("\n".join(L))
    print("wrote", out.relative_to(PROJECT), f"({len(table)} options)")


if __name__ == "__main__":
    main()
