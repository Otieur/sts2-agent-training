#!/usr/bin/env python3
"""Backtest tools/draft.py on the Player's card reward screens: agreement with the Player's pick, and act survival
when the Player's choice matched the tool's recommendation against when it did not.

Caveats: draft.py uses v0.111.1 card values and today's tier file, both applied to v0.107.1 screens; the deck is
reconstructed at the start of the floor; the decision-point signal in draft.py was fitted on these same screens
(only Breakthrough), so it is switched off here to avoid testing on the training data. [PLAYER-DATA, observational]

Outputs reports/phase2/draft-backtest.md. Usage: python3 -I tools/backtest_draft.py [--character IRONCLAD]
"""
import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import draft  # noqa: E402
from deck_metrics import deck_at  # noqa: E402
from analyze_ancients import fisher_two_sided  # noqa: E402
from stslib import MAIN_BUILD, PROJECT, connect, md_table, pct  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", default="IRONCLAD")
    args = ap.parse_args()
    ch = args.character.upper()
    draft._DP[ch] = {}  # no decision-point signal: it was fitted on these screens
    con = connect()
    runs = {r["run_id"]: dict(r) for r in con.execute(
        "SELECT run_id, win, abandoned, ascension FROM runs WHERE n_players = 1 AND build_id = ? AND character = ? AND NOT abandoned",
        [MAIN_BUILD, ch])}
    max_act = {r[0]: r[1] for r in con.execute("SELECT run_id, MAX(act) FROM floors GROUP BY run_id")}
    bosses = collections.defaultdict(dict)
    for r in con.execute("SELECT run_id, act, model_id FROM floors WHERE room_type = 'boss'"):
        bosses[r["run_id"]].setdefault(r["act"], r["model_id"])
    screens = collections.defaultdict(list)
    for r in con.execute("SELECT run_id, floor, act, offer_group, card_id, picked, source FROM card_offers"):
        if r["run_id"] in runs and r["source"] != "shop":
            screens[(r["run_id"], r["floor"], r["offer_group"])].append(dict(r))
    agree = collections.Counter()
    outcome = {True: [0, 0], False: [0, 0]}
    by_kind = collections.defaultdict(lambda: [0, 0])
    examples = []
    for (run_id, floor, _), offers in screens.items():
        act = offers[0]["act"]
        deck = deck_at(con, run_id, floor)
        offer_ids = ["CARD." + o["card_id"].split(".", 1)[-1] for o in offers if o["card_id"].split(".", 1)[-1] in draft.dm.CARDS]
        if not offer_ids or not deck:
            continue
        res = draft.score_offer(deck, offer_ids, ch, act, floor, bosses[run_id].get(act, ""))
        tool = res["pick"]["id"] if res["pick"] else "SKIP"
        picked = next((o["card_id"].split(".", 1)[-1] for o in offers if o["picked"]), "SKIP")
        same = tool == picked
        kind = ("both skip" if same and tool == "SKIP" else "same card" if same else
                "tool skips, Player picks" if tool == "SKIP" else "Player skips, tool picks" if picked == "SKIP" else "different cards")
        agree[kind] += 1
        survived = int(bool(runs[run_id]["win"]) or max_act.get(run_id, 0) > act)
        outcome[same][0] += survived
        outcome[same][1] += 1
        by_kind[kind][0] += survived
        by_kind[kind][1] += 1
        if not same and len(examples) < 15 and picked != "SKIP" and tool != "SKIP":
            examples.append([run_id.split("-")[-1], floor, picked.replace("_", " ").title(), tool.replace("_", " ").title(),
                             "; ".join(res["rows"][0]["reasons"][:2])])
    con.close()
    n = sum(agree.values())
    a, b = outcome[True], outcome[False]
    p = fisher_two_sided(a[0], a[1] - a[0], b[0], b[1] - b[0])
    L = [f"# Draft Backtest ({ch.title()})", "",
         f"`tools/draft.py` replayed on {n} of the Player's card reward screens ({MAIN_BUILD}, solo, finished runs). Built by "
         "`tools/backtest_draft.py`. Caveats: v0.111.1 card values and the current tier file applied to v0.107.1 screens; "
         "the decision-point signal is switched off (it was fitted on these screens). `[PLAYER-DATA, observational]`", "",
         f"**Agreement:** {pct((agree['same card'] + agree['both skip']) / n)} of screens "
         f"({agree['same card']} same card, {agree['both skip']} both skip).", "",
         md_table(["Case", "Screens", "Survived the act"], [[k, v, f"{pct(by_kind[k][0] / by_kind[k][1])} ({by_kind[k][0]}/{by_kind[k][1]})"]
                                                            for k, v in agree.most_common()]), "",
         f"**Act survival when the Player matched the tool:** {pct(a[0] / a[1])} ({a[0]}/{a[1]}); when not: {pct(b[0] / b[1])} "
         f"({b[0]}/{b[1]}); Fisher p = {p:.2f}.", "",
         "Reading: a higher survival rate when the Player happened to choose what the tool recommends is weak support for "
         "the tool (confounded: easy screens may produce both agreement and survival). The disagreement table shows "
         "where the tool and the Player differ most.", "",
         "## Sample disagreements (both picked a card)", "",
         md_table(["Seed", "Floor", "Player picked", "Tool picks", "Tool's main reasons"], examples), ""]
    out = PROJECT / f"reports/phase2/draft-backtest-{ch.lower()}.md"
    out.write_text("\n".join(L))
    print("wrote", out.relative_to(PROJECT), f"({n} screens)")


if __name__ == "__main__":
    main()
