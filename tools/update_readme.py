#!/usr/bin/env python3
"""Refresh the generated parts of README.md and the benchmark chart from tracked files only.

    python3 -I tools/update_readme.py           # rewrite README.md sections and assets/benchmark-*.svg
    python3 -I tools/update_readme.py --check   # exit 1 if anything would change (nothing is written)

Sections are delimited by `<!-- auto:NAME:start -->` and `<!-- auto:NAME:end -->`; text outside them is hand-written
and left alone. Sources: `reports/phase1/SUMMARY.md` (human runs), `reports/phase7/fidelity.md` and
`reports/phase7/run-fidelity.md` (simulator fidelity), `data/learn/*/manifest.json` (self-play datasets),
`data/learn/bench/*/manifest.json` (benchmark runs), `metrics/scoreboard.csv` (real runs), `docs/STATUS.md` (phase
states) and the game version in `docs/environment.md`.

Benchmark runs that share the benchmark file, seed base and seed count play the same 120 jobs, so their arms are
comparable; for each arm the latest run that contains it is used. The chart shows the rule planner, the search arms,
the action-value policy, and any value-network arm that wins at least as often as the planner.
"""
import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
README = PROJECT / "README.md"

ARM_LABELS = {
    "planner": ("Rule planner", "hand-written turn planner"),
    "qpolicy": ("Action-value network", "learned, no simulation"),
    "vgreedy": ("Value network, one step", "learned, one simulated move"),
}
PHASES = {
    0: "Setup: game version, mods (security-reviewed), save safety, live interface",
    1: "History analysis: encounter danger, deaths, card choices, playbook v1",
    2: "Knowledge base: mechanics, enemies, bosses, community strategy",
    3: "Shadowing: the agent calls each decision before the human makes it",
    4: "Solo practice: full runs in the real game, journals and post-mortems",
    5: "Second character (Necrobinder)",
    6: "Co-op: the agent as a teammate controlling its own character",
    7: "Engine simulator: the game's combat and whole runs in our own process",
    8: "Combat search and autopilot",
    9: "Learned models and reinforcement learning",
}


def label(arm):
    if arm in ARM_LABELS:
        return ARM_LABELS[arm]
    m = re.fullmatch(r"mc(\d+)", arm)
    if m:
        return ("Monte Carlo search", f"{m.group(1)} sampled futures per move")
    m = re.fullmatch(r"mcw(\d+)", arm)
    if m:
        return ("Monte Carlo search, wide", f"all distinct moves, {m.group(1)} futures each")
    m = re.fullmatch(r"vleaf(\d+)", arm)
    if m:
        return ("Search with value network", f"{m.group(1)} futures, network at the leaves")
    return (arm, "")


def read(path):
    p = PROJECT / path
    return p.read_text() if p.exists() else ""


def facts():
    f = {}
    m = re.search(r"Source: (\d+) solo Ironclad runs", read("reports/phase1/SUMMARY.md"))
    f["human_runs"] = int(m.group(1)) if m else None
    m = re.search(r"\*\*(\d+) of (\d+) recorded fights reproduce exactly", read("reports/phase7/fidelity.md"))
    f["fidelity"] = (int(m.group(1)), int(m.group(2))) if m else None
    m = re.search(r"\*\*(\d+) of (\d+) checks match", read("reports/phase7/run-fidelity.md"))
    f["run_fidelity"] = (int(m.group(1)), int(m.group(2))) if m else None
    m = re.search(r"v\d+\.\d+\.\d+", read("docs/environment.md"))
    f["game_version"] = m.group(0) if m else None
    datasets = []
    for mf in sorted((PROJECT / "data" / "learn").glob("*/manifest.json")):
        d = json.loads(mf.read_text())
        s = d.get("summary") or {}
        datasets.append({"name": d.get("dataset", mf.parent.name), "fights": s.get("fights", 0), "decisions": s.get("decisions", 0),
                         "teacher": (d.get("teacher") or {}).get("policy", "")})
    f["datasets"] = datasets
    f["decisions"] = sum(d["decisions"] for d in datasets)
    f["fights"] = sum(d["fights"] for d in datasets)
    runs = []
    for mf in (PROJECT / "data" / "learn" / "bench").glob("*/manifest.json"):
        runs.append(json.loads(mf.read_text()))
    runs.sort(key=lambda r: r.get("created", ""))
    f["bench_runs"] = runs
    rows = list(csv.DictReader(read("metrics/scoreboard.csv").splitlines())) if read("metrics/scoreboard.csv") else []
    f["real_runs"] = rows
    f["phases"] = phase_states(read("docs/STATUS.md"))
    return f


def phase_states(text):
    states, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"## Phase (\d+):", line)
        if m:
            cur = int(m.group(1))
            states[cur] = []
            continue
        m = re.match(r"\| P(\d+)\.E\d+ \|[^|]*\| ([^|]+)\|", line)
        if m and cur is not None and int(m.group(1)) == cur:
            states[cur].append(m.group(2).strip())
    out = {}
    for ph, sts in states.items():
        if sts and all(s.startswith("Done") for s in sts):
            out[ph] = "●"
        elif sts and all(s.startswith("Todo") for s in sts):
            out[ph] = "○"
        else:
            out[ph] = "◐"
    return out


def latest_arms(runs):
    """Arm -> (summary, run) for the latest run with each arm, among runs of the newest job set that has a planner."""
    key = lambda r: (r.get("benchmark"), r.get("seed_base"), r.get("seeds"))
    with_planner = [r for r in runs if "planner" in r.get("arms", [])]
    if not with_planner:
        return {}, None
    jobs = key(with_planner[-1])
    arms = {}
    for r in runs:
        if key(r) != jobs:
            continue
        for a in r.get("arms", []):
            if a.endswith("p") and a != "planner":
                continue                                   # potion arms belong to their own comparison
            if a in r.get("summary", {}):
                arms[a] = (r["summary"][a], r)
    return arms, with_planner[-1]


def chart_arms(arms):
    if "planner" not in arms:
        return []
    base = arms["planner"][0]["won"]
    pick = ["planner"]
    pick += [a for a in arms if a == "qpolicy"]
    pick += [a for a in arms if re.fullmatch(r"(vleaf\d+|vgreedy)", a) and arms[a][0]["won"] >= base]
    pick += sorted((a for a in arms if re.fullmatch(r"mcw?\d+", a)), key=lambda a: (a.startswith("mcw"), int(re.sub(r"\D", "", a))))
    return pick


def speed(sec):
    return f"{sec * 1000:.0f} ms" if sec < 1 else f"{sec:.1f} s"


def chart_svg(theme, arms, picks, jobs):
    c = {"dark": dict(panel="#161b22", text="#e6edf3", muted="#8b949e", grid="#30363d", base="#6e7681", learned="#4cc2ff", search="#ff8a3d"),
         "light": dict(panel="#f6f8fa", text="#1f2328", muted="#57606a", grid="#d0d7de", base="#8c959f", learned="#0a7bbd", search="#d9621e")}[theme]
    font = "ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
    W, row = 880, 50
    H = 140 + row * len(picks)
    games = max(arms[a][0]["games"] for a in picks)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Benchmark wins out of {games}: '
         + ", ".join(f"{label(a)[0]} ({a}) {arms[a][0]['won']}" for a in picks) + '">',
         f'<rect width="{W}" height="{H}" rx="14" fill="{c["panel"]}"/>',
         f'<text x="32" y="44" font-family="{font}" font-size="20" font-weight="700" fill="{c["text"]}">Fights won on the benchmark</text>',
         f'<text x="32" y="68" font-family="{font}" font-size="14" fill="{c["muted"]}">{jobs} fights taken from real runs (hallways, elites, bosses; A0–A10), 2 seeds each = {games} games per policy</text>']
    x0, x1 = 300, 760
    scale = (x1 - x0) / games
    top, bottom = 92, 92 + row * len(picks)
    for v in range(0, games + 1, 30):
        x = x0 + v * scale
        o.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="{c["grid"]}" stroke-width="1"/>')
        o.append(f'<text x="{x:.1f}" y="{bottom + 20}" font-family="{font}" font-size="12" text-anchor="middle" fill="{c["muted"]}">{v}</text>')
    for i, a in enumerate(picks):
        s = arms[a][0]
        name, sub = label(a)
        y = top + 12 + i * row
        color = c["base"] if a == "planner" else (c["search"] if a.startswith("mc") else c["learned"])
        o.append(f'<text x="32" y="{y + 15}" font-family="{font}" font-size="15" font-weight="600" fill="{c["text"]}">{name}</text>')
        o.append(f'<text x="32" y="{y + 33}" font-family="{font}" font-size="12" fill="{c["muted"]}">{sub}</text>')
        w = s["won"] * scale
        o.append(f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="30" rx="6" fill="{color}"/>')
        o.append(f'<text x="{x0 + w + 10:.1f}" y="{y + 20}" font-family="{font}" font-size="15" font-weight="700" fill="{c["text"]}">{s["won"]}</text>')
        o.append(f'<text x="{W - 32}" y="{y + 20}" font-family="{font}" font-size="12" text-anchor="end" fill="{c["muted"]}">{speed(s["search_seconds_per_decision"])}/move</text>')
    o.append(f'<text x="{(x0 + x1) / 2:.0f}" y="{bottom + 40}" font-family="{font}" font-size="12" text-anchor="middle" fill="{c["muted"]}">games won (of {games})</text>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


def sections(f):
    s = {}
    fid = f["fidelity"]
    arms, _ = latest_arms(f["bench_runs"])
    search = [a for a in arms if re.fullmatch(r"mcw?\d+", a)]
    best = max(search, key=lambda a: arms[a][0]["mean_value"]) if search else None
    gain = (arms[best][0]["mean_value"] - arms["planner"][0]["mean_value"]) if best and "planner" in arms else None
    cards = [
        (f"{f['human_runs']}" if f["human_runs"] else "–", "human runs analysed", "deaths, damage per encounter, card picks"),
        (f"{fid[0]} / {fid[1]}" if fid else "–", "recorded fights replayed exactly", "by the simulator, every state equal"),
        (f"{gain:+.0f}" if gain is not None else "–", "value per fight from search", f"best search ({best}) over the rule planner, {arms[best][0]['games'] if best else 0} games"),
        (f"{f['decisions']:,}", "self-play decisions", f"from {f['fights']:,} simulated fights"),
    ]
    s["numbers"] = "<table>\n<tr>\n" + "\n".join(
        f'<td align="center" width="25%"><h3>{big}</h3>{what}<br><sub>{sub}</sub></td>' for big, what, sub in cards) + "\n</tr>\n</table>"
    rows = []
    for a in sorted(arms, key=lambda a: arms[a][0]["won"], reverse=True):
        sm, run = arms[a]
        model = run.get("q_model") if a == "qpolicy" else (run.get("model") if a.startswith("v") else None)
        model = f"`{Path(model).parent.name}`" if model else "–"
        rows.append(f"| {label(a)[0]} (`{a}`) | {sm['won']} of {sm['games']} | {sm['mean_value']:.1f} | {speed(sm['search_seconds_per_decision'])} | {model} | [`{run['name']}`](data/learn/bench/{run['name']}/manifest.json) {run.get('created', '')[:10]} |")
    s["latest"] = ("| Policy | Fights won | Mean value | Time per move | Model | Run |\n|---|---|---|---|---|---|\n" + "\n".join(rows)) if rows else "_No benchmark run yet._"
    real = f["real_runs"]
    if real:
        wins = [r for r in real if r.get("win") == "1"]
        best = max((int(r["ascension"]) for r in wins), default=None)
        last = real[-1]
        s["realruns"] = (f"**Real game:** {len(real)} full runs by the agent, {len(wins)} won" + (f" (highest Ascension won: {best})" if best is not None else "")
                         + f". Latest: {last['date']}, Ascension {last['ascension']}, " + ("won" if last.get("win") == "1" else f"reached act {last.get('act_reached')} floor {last.get('floor_reached')}")
                         + ". Details in the [scoreboard](metrics/scoreboard.csv) and [run journals](runs/).")
    s["roadmap"] = "| Phase | What it delivers | State |\n|:---:|---|:---:|\n" + "\n".join(
        f"| **{p}** | {PHASES[p]} | {f['phases'].get(p, '○')} |" for p in sorted(PHASES))
    s["updated"] = f"<sub>Generated sections last refreshed {time.strftime('%Y-%m-%d')} · game {f['game_version'] or '?'} · `python3 -I tools/update_readme.py`</sub>"
    return s


def apply(text, secs):
    for name, body in secs.items():
        pat = re.compile(rf"<!-- auto:{name}:start -->.*?<!-- auto:{name}:end -->", re.S)
        if not pat.search(text):
            raise SystemExit(f"README.md has no auto:{name} section")
        text = pat.sub(lambda m: f"<!-- auto:{name}:start -->\n{body}\n<!-- auto:{name}:end -->", text)
    return text


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    f = facts()
    secs = sections(f)
    old = README.read_text()
    new = apply(old, secs)
    arms, run = latest_arms(f["bench_runs"])
    picks = chart_arms(arms)
    jobs = len(json.loads((PROJECT / run["benchmark"]).read_text())["fights"]) if run else 0
    charts = {t: chart_svg(t, arms, picks, jobs) for t in ("dark", "light")} if picks else {}
    changed = []
    strip = lambda t: re.sub(r"last refreshed \d{4}-\d{2}-\d{2}", "", t)
    if strip(new) != strip(old):
        changed.append("README.md")
    for t, svg in charts.items():
        p = PROJECT / "assets" / f"benchmark-{t}.svg"
        if not p.exists() or p.read_text() != svg:
            changed.append(str(p.relative_to(PROJECT)))
    if a.check:
        print("would change: " + (", ".join(changed) if changed else "nothing"))
        return 1 if changed else 0
    if "README.md" in changed:
        README.write_text(new)
    for t, svg in charts.items():
        (PROJECT / "assets" / f"benchmark-{t}.svg").write_text(svg)
    print("updated: " + (", ".join(changed) if changed else "nothing"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
