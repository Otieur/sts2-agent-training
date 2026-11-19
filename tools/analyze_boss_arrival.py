#!/usr/bin/env python3
"""How arrival HP relates to dying at the act boss, and what resting right before the boss did.

All characters, solo, v0.107.1, finished runs. Observational: strong decks both keep HP high and win, so the
curves overstate the causal value of HP. Use them to calibrate pre-boss rest thresholds, then test in Phase 4.

Usage: python3 -I tools/analyze_boss_arrival.py
Writes reports/phase2/boss-arrival-hp.md
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import MAIN_BUILD, PROJECT, connect, md_table, pct  # noqa: E402

BUCKETS = [(0, .4, "under 40%"), (.4, .5, "40–50%"), (.5, .6, "50–60%"), (.6, .7, "60–70%"), (.7, .8, "70–80%"),
           (.8, .9, "80–90%"), (.9, 1.01, "90–100%")]


def fit(points, iters=20000, lr=0.5):
    a = b = 0.0
    for _ in range(iters):
        ga = gb = 0.0
        for x, y in points:
            p = 1 / (1 + math.exp(-(a + b * x)))
            ga += y - p
            gb += (y - p) * x
        a += lr * ga / len(points)
        b += lr * gb / len(points)
    return lambda x: 1 / (1 + math.exp(-(a + b * x)))


def main():
    con = connect()
    rows = [dict(r) for r in con.execute("""
        SELECT f.run_id, f.floor, f.act, f.model_id AS enc, f.hp_before * 1.0 / f.max_hp AS hp, r.character,
               (f.is_last_floor AND NOT r.win AND NOT r.abandoned) AS died
        FROM floors f JOIN runs r USING(run_id)
        WHERE r.n_players = 1 AND r.build_id = ? AND f.room_type = 'boss' AND NOT r.abandoned""", [MAIN_BUILD])]
    L = ["# Boss Arrival HP and Pre-Boss Rest Sites", "",
         f"All characters, solo runs on {MAIN_BUILD}, finished runs only. Built by `tools/analyze_boss_arrival.py`. "
         "`[PLAYER-DATA]`, observational: decks that keep HP high are also stronger, so these curves overstate how much "
         "HP alone buys. They calibrate hypothesis H1; Phase 4 tests it.", ""]
    curves = {}
    for act in (1, 2, 3):
        xs = [x for x in rows if x["act"] == act]
        f = fit([(x["hp"], x["died"]) for x in xs])
        curves[act] = f
        L += [f"## Act {act} bosses (n={len(xs)}, fatal {sum(x['died'] for x in xs)})", "",
              md_table(["Arrival HP", "Fights", "Fatal", "Rate"],
                       [[label, len(s), sum(x["died"] for x in s), pct(sum(x["died"] for x in s) / len(s))]
                        for lo, hi, label in BUCKETS for s in [[x for x in xs if lo <= x["hp"] < hi]] if s]), "",
              "Logistic fit, P(fatal | arrival HP): " + ", ".join(f"{int(h * 100)}% → {pct(f(h))}" for h in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)), ""]
    # Value of a heal at each arrival level, by act. A heal is floor(30% of max HP), about 0.29 of max after rounding.
    L += ["## What a pre-boss heal is worth on the fitted curves", "",
          "A rest heals 30% of max HP rounded down (237 of 297 rests match exactly; about 29% after rounding, used here). Reduction in fitted fatal-fight probability from healing at "
          "each HP level (capped at 100%):", "",
          md_table(["HP at the rest site", "Act 1", "Act 2", "Act 3"],
                   [[f"{int(h * 100)}%"] + [f"−{100 * (curves[a](h) - curves[a](min(1.0, h + 0.29))):.0f} pts" for a in (1, 2, 3)]
                    for h in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8)]), "",
          "These are upper bounds (see Reading the evidence). An upgrade's value cannot be read from these data.", ""]
    # Actual pre-boss rest choices
    rests = [dict(r) for r in con.execute("""
        SELECT c.choice, c.hp_before * 1.0 / c.max_hp AS hp, c.act,
               (SELECT g.is_last_floor AND NOT r.win AND NOT r.abandoned FROM floors g WHERE g.run_id = c.run_id AND g.floor = c.floor + 1) AS died
        FROM rest_choices c JOIN runs r USING(run_id)
        WHERE r.n_players = 1 AND r.build_id = ? AND c.next_is_boss = 1 AND c.choice IN ('HEAL','SMITH') AND NOT r.abandoned""", [MAIN_BUILD])]
    table = []
    for lo, hi, label in ((0, .5, "under 50%"), (.5, .7, "50–70%"), (.7, 1.01, "70%+")):
        row = [label]
        for ch in ("HEAL", "SMITH"):
            s = [x for x in rests if lo <= x["hp"] < hi and x["choice"] == ch]
            row.append(f"{sum(x['died'] for x in s)}/{len(s)} ({pct(sum(x['died'] for x in s) / len(s)) if s else '-'})")
        table.append(row)
    L += ["## What the Player actually did right before a boss", "",
          md_table(["HP at the rest site", "Healed: fatal at boss", "Smithed: fatal at boss"], table), "",
          "Choices are confounded: the Player smiths at low HP mainly when the deck already looks strong.", "",
          "## Reading the evidence", "",
          "- **The arrival curve says HP matters:** fatal rates fall from about 30–40% (under 50% HP) to about 10–15% "
          "(80%+) in Acts 1–2, and more steeply in Act 3.",
          "- **The Player's own choices say a heal bought little:** at the same HP, healing and smithing were followed by "
          "almost the same boss death rate (under 50%: 31% against 30%; 50–70%: 25% against 24%).",
          "- The two are confounded in opposite directions. The curve credits HP with what strong decks do. The direct "
          "comparison hides the heal's value, because the Player smithed mostly when the deck was already strong. The true "
          "value of a pre-boss heal is probably smaller than the heal table above suggests (treat it as an upper bound), "
          "but not zero.", "",
          "## Rule to test (H1, revised)", "",
          "- **Acts 1–2:** rest before the boss if HP is below the boss's median damage + 10 (playbook section 10; "
          "typically 40–60% of max). Otherwise smith.",
          "- **Act 3 and the A10 double boss:** rest if HP is below **70%**. Act 3 shows the steepest arrival effect, and "
          "A10 adds a second boss.",
          "- Phase 4 records arrival HP, the rest choice and the outcome for every boss, so the rule can be checked "
          "against the Player's baseline (equally likely to heal or smith at 37% HP before a boss).", ""]
    out = PROJECT / "reports/phase2/boss-arrival-hp.md"
    out.write_text("\n".join(L))
    print("wrote", out.relative_to(PROJECT))


if __name__ == "__main__":
    main()
