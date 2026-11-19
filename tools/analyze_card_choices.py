#!/usr/bin/env python3
"""Card choices at the decision point: for every card offered on a card reward screen, how often the run survived
that act (and won) when the Player picked it, against when the Player passed it on the same kind of screen.

Unlike "win rate with the card in the final deck" (reports/phase1/card-outcomes-*), this compares at the moment of
choice, so cards seen late are not flattered by survivorship. Still confounded by the Player's reasons (a card
picked because the deck needed it, or skipped because the deck was already strong). [PLAYER-DATA, weak]

Also checks the community consensus tiers against these outcomes: does the pick effect rise with the tier?

Outputs reports/phase2/card-choices-<character>.md and data/tables/card_choices_<character>.csv.
Usage: python3 -I tools/analyze_card_choices.py [--character IRONCLAD]
"""
import argparse
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_ancients import fisher_two_sided  # noqa: E402
from stslib import DATA, MAIN_BUILD, PROJECT, connect, md_table, pct, write_csv  # noqa: E402

MIN_EACH = 4  # picks and passes each


def norm(s):
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def load_tiers(character):
    path = PROJECT / "knowledge" / "community" / f"{character.lower()}-tiers.md"
    out = {}
    if path.exists():
        for line in path.read_text().splitlines():
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) == 10 and c[2].startswith("**"):
                out[norm(c[0])] = c[2].strip("*")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", default="IRONCLAD")
    args = ap.parse_args()
    ch = args.character.upper()
    con = connect()
    runs = {r["run_id"]: dict(r) for r in con.execute(
        "SELECT run_id, win, abandoned, ascension FROM runs WHERE n_players = 1 AND build_id = ? AND character = ?",
        [MAIN_BUILD, ch])}
    max_act = {r[0]: r[1] for r in con.execute("SELECT run_id, MAX(act) FROM floors GROUP BY run_id")}
    s = collections.defaultdict(lambda: {"surv": [[0, 0], [0, 0]], "win": [[0, 0], [0, 0]]})  # index 1 = picked
    for r in con.execute("SELECT run_id, act, card_id, picked, source FROM card_offers"):
        run = runs.get(r["run_id"])
        if not run or run["abandoned"] or r["source"] == "shop":
            continue
        cid = r["card_id"].split(".", 1)[-1]
        k = 1 if r["picked"] else 0
        survived = int(bool(run["win"]) or max_act.get(r["run_id"], 0) > r["act"])
        s[cid]["surv"][k][0] += survived
        s[cid]["surv"][k][1] += 1
        s[cid]["win"][k][0] += run["win"]
        s[cid]["win"][k][1] += 1
    tiers = load_tiers(ch)
    rows, csv_rows, by_tier = [], [], collections.defaultdict(list)
    for cid, v in s.items():
        (ps, pn), (cs, cn) = v["surv"][0], v["surv"][1]
        if cn < MIN_EACH or pn < MIN_EACH:
            continue
        diff = cs / cn - ps / pn
        p = fisher_two_sided(cs, cn - cs, ps, pn - ps)
        name = cid.replace("_", " ").title()
        tier = tiers.get(norm(cid.replace("_", " ")), "-")
        by_tier[tier].append((diff, cn + pn))
        rows.append((diff, [name, tier, cn, pn, f"{pct(cs / cn)} ({cs}/{cn})", f"{pct(ps / pn)} ({ps}/{pn})", f"{100 * diff:+.0f} pts",
                            f"{p:.2f}", pct(v["win"][1][0] / v["win"][1][1]), pct(v["win"][0][0] / v["win"][0][1])]))
        csv_rows.append([cid, tier, cn, pn, cs, ps, f"{diff:+.3f}", f"{p:.3f}"])
    rows.sort(key=lambda x: -x[0])
    tier_rows = []
    for t in ("S", "A", "B", "C", "D", "-"):
        xs = by_tier.get(t, [])
        if xs:
            w = sum(n for _, n in xs)
            tier_rows.append([t, len(xs), f"{100 * sum(d * n for d, n in xs) / w:+.1f} pts", f"{100 * sum(d for d, _ in xs) / len(xs):+.1f} pts"])
    write_csv(DATA / "tables" / f"card_choices_{ch.lower()}.csv",
              ["card", "tier", "picked", "passed", "survived_picked", "survived_passed", "survive_diff", "p"], csv_rows)
    L = [f"# Card Choices at the Decision Point ({ch.title()})", "",
         f"Solo {MAIN_BUILD} runs, finished, card reward screens (shop offers excluded). Built by `tools/analyze_card_choices.py`. "
         f"For each card offered {MIN_EACH}+ times picked and {MIN_EACH}+ times passed: act survival when picked against when "
         "passed. `[PLAYER-DATA, weak]`: confounded by why the Player picked; p is a two-sided Fisher exact test, and with "
         f"{len(rows)} cards tested a few p < 0.05 results are expected by chance.", "",
         "## Does the community tier predict the pick effect?", "",
         md_table(["Consensus tier", "Cards", "Mean effect (weighted by offers)", "Mean effect (unweighted)"], tier_rows), "",
         "## Per card (sorted by effect)", "",
         md_table(["Card", "Tier", "Picked", "Passed", "Survived act (picked)", "Survived act (passed)", "Difference", "p",
                   "Won (picked)", "Won (passed)"], [r for _, r in rows]), ""]
    out = PROJECT / f"reports/phase2/card-choices-{ch.lower()}.md"
    out.write_text("\n".join(L))
    print("wrote", out.relative_to(PROJECT), f"({len(rows)} cards)")


if __name__ == "__main__":
    main()
