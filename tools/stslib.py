"""Shared helpers for the Slay the Spire 2 analysis scripts (standard library only)."""
import csv
import math
import sqlite3
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DATA = PROJECT / "data"
DB_PATH = DATA / "runs.db"
REPORTS = PROJECT / "reports"
MAIN_BUILD = "v0.107.1"

STARTER_CARDS = {
    "STRIKE", "DEFEND", "BASH", "NEUTRALIZE", "SURVIVOR", "ZAP", "DUALCAST",
    "BODYGUARD", "UNLEASH", "FALLING_STAR", "VENERATE", "FOOLISH_SHOT",
    "ASCENDERS_BANE",
}


def connect():
    if not DB_PATH.exists():
        raise SystemExit(f"{DB_PATH} not found; run tools/extract_runs.py first")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def short(card_or_relic_id):
    """CARD.PERFECTED_STRIKE -> PERFECTED_STRIKE"""
    if card_or_relic_id is None:
        return None
    return card_or_relic_id.split(".", 1)[-1]


def is_starter(card_id, character):
    s = short(card_id)
    if s == "ASCENDERS_BANE":
        return True
    suffix = "_" + character
    base = s[: -len(suffix)] if s.endswith(suffix) else s
    return base in STARTER_CARDS


def wilson(k, n, z=1.96):
    """95% Wilson score interval for k successes out of n."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def quantile(values, q):
    """Linear-interpolated quantile, q in [0, 1]."""
    v = sorted(values)
    if not v:
        return float("nan")
    pos = (len(v) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


def median(values):
    return quantile(values, 0.5)


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else float("nan")


def asc_band(a):
    if a is None:
        return "?"
    if a <= 4:
        return "A0-4"
    if a <= 9:
        return "A5-9"
    return "A10"


def pct(x, digits=0):
    if x != x:  # NaN
        return "-"
    return f"{100 * x:.{digits}f}%"


def num(x, digits=1):
    if isinstance(x, float) and x != x:
        return "-"
    if isinstance(x, float):
        return f"{x:.{digits}f}"
    return str(x)


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def write_csv(path, headers, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)


CAUTIONS = """> **Statistical cautions.** (1) Selection bias: what gets offered depends on earlier picks and relics.
> (2) Survivorship: late-floor numbers come only from runs that got there. (3) Ascension confounds
> everything; compare within bands. (4) Small samples: show n next to every rate; win correlations are
> hypotheses. (5) Multiple comparisons: with ~100 cards, some will look significant by chance."""
