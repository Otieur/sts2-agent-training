#!/usr/bin/env python3
"""Event choices at the decision point: for each event option the Player chose, act survival and win rate against
the other options chosen at the same event, plus the mean HP, gold and max HP change. All characters, solo.

[PLAYER-DATA, weak]: one choice per event visit, small samples, and the Player's reasons are a confounder.
Outputs reports/phase2/event-choices.md and data/tables/event_choices.csv (used by tools/advise.py).
Usage: python3 -I tools/analyze_event_choices.py
"""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_ancients import fisher_two_sided  # noqa: E402
from stslib import DATA, MAIN_BUILD, PROJECT, connect, md_table, pct, write_csv  # noqa: E402

MIN_CHOSEN = 4


def option_key(choice_key):
    """'SUNKEN_STATUE.pages.INITIAL.options.GRAB_SWORD.title' -> 'INITIAL.options.GRAB_SWORD'"""
    k = re.sub(r"\.title$", "", choice_key or "")
    return re.sub(r"^[A-Z0-9_]+\.pages\.", "", k)


def main():
    con = connect()
    runs = {r["run_id"]: dict(r) for r in con.execute(
        "SELECT run_id, win FROM runs WHERE n_players = 1 AND build_id = ? AND NOT abandoned", [MAIN_BUILD])}
    max_act = {r[0]: r[1] for r in con.execute("SELECT run_id, MAX(act) FROM floors GROUP BY run_id")}
    by_event = collections.defaultdict(list)
    for r in con.execute("SELECT run_id, act, event_id, choice_key, hp_change, gold_change, max_hp_change FROM event_choices"):
        if r["run_id"] not in runs:
            continue
        survived = int(bool(runs[r["run_id"]]["win"]) or max_act.get(r["run_id"], 0) > r["act"])
        by_event[r["event_id"].replace("EVENT.", "")].append({**dict(r), "opt": option_key(r["choice_key"]), "surv": survived,
                                                              "win": runs[r["run_id"]]["win"]})
    con.close()
    rows, csv_rows = [], []
    for ev, xs in sorted(by_event.items()):
        opts = collections.Counter(x["opt"] for x in xs)
        if len(opts) < 2:
            continue
        for opt, n in opts.items():
            if n < MIN_CHOSEN:
                continue
            a = [x for x in xs if x["opt"] == opt]
            b = [x for x in xs if x["opt"] != opt]
            sa, sb = sum(x["surv"] for x in a), sum(x["surv"] for x in b)
            p = fisher_two_sided(sa, len(a) - sa, sb, len(b) - sb)
            diff = sa / len(a) - sb / len(b)
            hp = sum(x["hp_change"] or 0 for x in a) / len(a)
            gold = sum(x["gold_change"] or 0 for x in a) / len(a)
            mhp = sum(x["max_hp_change"] or 0 for x in a) / len(a)
            rows.append((p, [ev.replace("_", " ").title(), opt.split(".")[-1].replace("_", " ").title(), len(a), len(b),
                             f"{pct(sa / len(a))} ({sa}/{len(a)})", f"{pct(sb / len(b))} ({sb}/{len(b)})", f"{100 * diff:+.0f} pts",
                             f"{p:.2f}", f"{hp:+.1f}", f"{gold:+.0f}", f"{mhp:+.1f}"]))
            csv_rows.append([ev, opt, len(a), len(b), sa, sb, f"{diff:+.3f}", f"{p:.3f}", f"{hp:+.1f}", f"{gold:+.0f}", f"{mhp:+.1f}"])
    rows.sort(key=lambda x: x[0])
    write_csv(DATA / "tables" / "event_choices.csv",
              ["event", "option", "chosen", "others", "survived_chosen", "survived_others", "survive_diff", "p", "hp", "gold", "max_hp"], csv_rows)
    L = ["# Event Choices at the Decision Point", "",
         f"All characters, solo, {MAIN_BUILD}, finished runs. Built by `tools/analyze_event_choices.py`. For each event option "
         f"chosen {MIN_CHOSEN}+ times: act survival when the Player chose it against when the Player chose another option at "
         "the same event, with the option's mean HP, gold and max HP change. Sorted by p (two-sided Fisher). "
         f"`[PLAYER-DATA, weak]`: with {len(rows)} options tested, a few p < 0.05 results are expected by chance.", "",
         md_table(["Event", "Option", "Chosen", "Other options", "Survived act (this)", "Survived act (others)", "Difference", "p",
                   "HP", "Gold", "Max HP"], [r for _, r in rows]), ""]
    out = PROJECT / "reports/phase2/event-choices.md"
    out.write_text("\n".join(L))
    print("wrote", out.relative_to(PROJECT), f"({len(rows)} options)")


if __name__ == "__main__":
    main()
