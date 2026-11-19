#!/usr/bin/env python3
"""Does deck strength predict HP lost in a fight? Fits, per act and room type (monster, elite, boss), an ordinary
least-squares model of HP lost (share of max HP) on the deck's damage per turn, block per turn and scaling count
at the start of the fight (tools/deck_metrics.py proxies, v0.107.1 card values), plus the ascension level.

Outputs reports/phase2/fight-model.md and data/tables/fight_model.json (coefficients, used by tools/path.py when
present). Features are cached in data/tables/fight_features.csv (rebuild with --rebuild).
[PLAYER-DATA, observational]: decks are not assigned at random.

Usage: python3 -I tools/fight_model.py [--rebuild]
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deck_metrics as dm  # noqa: E402
from stslib import DATA, MAIN_BUILD, PROJECT, connect, md_table  # noqa: E402

FEATURES = DATA / "tables" / "fight_features.csv"
COEF = DATA / "tables" / "fight_model.json"
X_NAMES = ["dmg", "blk", "scaling", "ascension"]


def build_features():
    dm.apply_patches("v0.107.1")
    con = connect()
    rows = [dict(r) for r in con.execute("""
        SELECT f.run_id, f.floor, f.act, f.room_type, f.model_id, f.damage_taken, f.max_hp, f.hp_before, r.ascension,
               r.character, (f.is_last_floor AND NOT r.win AND NOT r.abandoned) AS died
        FROM floors f JOIN runs r USING(run_id)
        WHERE r.n_players = 1 AND r.build_id = ? AND NOT r.abandoned AND f.room_type IN ('monster','elite','boss')
          AND f.max_hp > 0""", [MAIN_BUILD])]
    out = []
    for i, f in enumerate(rows):
        deck = dm.deck_at(con, f["run_id"], f["floor"])
        out.append({**{k: f[k] for k in ("run_id", "floor", "act", "room_type", "model_id", "ascension", "character", "died")},
                    "hp_lost": round(f["damage_taken"] / f["max_hp"], 4), "hp_before": round(f["hp_before"] / f["max_hp"], 4),
                    "dmg": round(dm.simulate(deck, "damage", sims=120), 2), "blk": round(dm.simulate(deck, "block", sims=120), 2),
                    "scaling": dm.scaling_count(deck), "size": len(deck)})
    con.close()
    FEATURES.parent.mkdir(parents=True, exist_ok=True)
    with open(FEATURES, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    return out


def load_features():
    with open(FEATURES, newline="") as fh:
        return [{k: (float(v) if k not in ("run_id", "room_type", "model_id", "character") else v) for k, v in r.items()}
                for r in csv.DictReader(fh)]


def ols(X, y):
    """Least squares with an intercept via the normal equations (Gauss-Jordan). Returns (beta, r2, se)."""
    n, k = len(X), len(X[0]) + 1
    A = [[1.0] + list(x) for x in X]
    XtX = [[sum(A[r][i] * A[r][j] for r in range(n)) for j in range(k)] for i in range(k)]
    Xty = [sum(A[r][i] * y[r] for r in range(n)) for i in range(k)]
    M = [row[:] + [Xty[i]] + [1.0 if i == j else 0.0 for j in range(k)] for i, row in enumerate(XtX)]
    for c in range(k):
        piv = max(range(c, k), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        pv = M[c][c]
        if abs(pv) < 1e-12:
            raise ValueError("singular design")
        M[c] = [v / pv for v in M[c]]
        for r in range(k):
            if r != c and M[r][c]:
                fct = M[r][c]
                M[r] = [a - fct * b for a, b in zip(M[r], M[c])]
    beta = [M[i][k] for i in range(k)]
    inv = [M[i][k + 1:] for i in range(k)]
    pred = [sum(b * a for b, a in zip(beta, row)) for row in A]
    resid = [yy - p for yy, p in zip(y, pred)]
    ybar = sum(y) / n
    ss_res, ss_tot = sum(r * r for r in resid), sum((yy - ybar) ** 2 for yy in y)
    sigma2 = ss_res / max(1, n - k)
    se = [(sigma2 * inv[i][i]) ** 0.5 for i in range(k)]
    return beta, 1 - ss_res / ss_tot if ss_tot else 0.0, se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    rows = build_features() if args.rebuild or not FEATURES.exists() else load_features()
    models, table = {}, []
    for act in (1, 2, 3):
        for room in ("monster", "elite", "boss"):
            xs = [r for r in rows if int(r["act"]) == act and r["room_type"] == room]
            if len(xs) < 40:
                continue
            X = [[float(r[k]) for k in X_NAMES] for r in xs]
            y = [float(r["hp_lost"]) for r in xs]
            beta, r2, se = ols(X, y)
            means = {k: sum(float(r[k]) for r in xs) / len(xs) for k in X_NAMES}
            models[f"{act}:{room}"] = {"intercept": beta[0], **{k: b for k, b in zip(X_NAMES, beta[1:])}, "r2": r2, "n": len(xs),
                                       "mean_hp_lost": sum(y) / len(y), "means": means,
                                       "significant": [k for k, b, s in zip(X_NAMES, beta[1:], se[1:]) if s and abs(b / s) >= 2]}
            def cell(i):
                b, s = beta[i], se[i]
                star = "*" if s and abs(b / s) >= 2 else ""
                return f"{100 * b:+.2f}{star}"
            table.append([act, room, len(xs), f"{100 * sum(y) / len(y):.1f}%", cell(1), cell(2), cell(3), cell(4), f"{r2:.2f}"])
    COEF.write_text(json.dumps(models, indent=1))
    L = ["# Fight Model: Deck Strength against HP Lost", "",
         f"All characters, solo, {MAIN_BUILD}, finished runs. Built by `tools/fight_model.py`. Ordinary least squares per act "
         "and room type: HP lost in the fight (percent of max HP) on the deck's damage per turn, block per turn and scaling "
         "count at the start of the fight (deck_metrics proxies, v0.107.1 card values) and the ascension level. Coefficients "
         "are percentage points of max HP per unit; * marks |coefficient| at least twice its standard error. "
         "`[PLAYER-DATA, observational]`.", "",
         md_table(["Act", "Room", "Fights", "Mean HP lost", "per damage/turn", "per block/turn", "per scaling card",
                   "per ascension level", "R²"], table), "",
         "## Reading", "",
         "- A negative coefficient means more of that feature went with less HP lost. Block per turn is the feature to watch: "
         "the corner targets (H9) say block matters at bosses.",
         "- R² is low in every cell: most of a fight's HP loss is the draw, the enemy roll and decisions, not the deck "
         "proxies. Use the coefficients for small adjustments (tools/path.py applies them relative to the average deck), not "
         "as predictions for one fight.", ""]
    out = PROJECT / "reports/phase2/fight-model.md"
    out.write_text("\n".join(L))
    print("wrote", out.relative_to(PROJECT))


if __name__ == "__main__":
    main()
