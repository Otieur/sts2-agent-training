#!/usr/bin/env python3
"""Run journal helper (P4.E1.S3, P4.E2.S2). Creates and updates runs/<date>-<seed>/journal.md from
templates/run-journal.md, so the per-floor journal update is one command and the fight log always carries the
benchmark for comparison.

Commands:
  new     --character IRONCLAD --ascension 3 --seed ABCDEF123456 [--exam]
            Create runs/<YYYY-MM-DD>-<seed>/journal.md with the header filled in (playbook version read from the
            playbook). Refuses to overwrite.
  active    List journals that have no postmortem.md (a run in progress; see the project instructions, start of session).
  status  <run dir> (--floor F --act A --hp H --max-hp M --gold G [--potions a,b] | --from-state state.json)
            Rewrite the Status line. --from-state takes a full STS2MCP state or a compact snapshot (stsstate.py).
  floor   <run dir> --floor F --room ROOM --result TEXT --hp-change N --note TEXT
            Append a row to the floor log.
  fight   <run dir> --floor F --encounter ID --turns T --damage D [--potions a,b]
            Append a row to the fight log with the band-matched benchmark median; warns above the p75.
  budget  --encounter ID --character IRONCLAD --ascension N
            Print the benchmark for one encounter.
  summary <run dir>
            Total damage against the benchmark, fights above the p75, and encounters changed on v0.111.1.

Benchmarks come from the Player's v0.107.1 history (data/benchmarks/). Encounters changed on v0.111.1 are
flagged, since their benchmark is not directly comparable (knowledge/version-delta-v0.111.1.md).
"""
import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import DATA, PROJECT  # noqa: E402

TEMPLATE = PROJECT / "templates" / "run-journal.md"
RUNS = PROJECT / "runs"
HEADER_RE = re.compile(r"^# Run (\S+) (\S+): (\w+) A(\d+), playbook v(\S+)", re.M)

# Encounters whose enemies changed between v0.107.1 (benchmarks) and v0.111.1 (the game the Agent plays).
CHANGED_V0111 = {
    "ENCOUNTER.QUEEN_BOSS": "Torch Head Amalgam opens with Strong Tackle 26 (32)",
    "ENCOUNTER.AEONGLASS_BOSS": "Ebb damage 26 (32) -> 22 (26)",
    "ENCOUNTER.MECHA_KNIGHT_ELITE": "Flamethrower turn also deals 8 (12)",
    "ENCOUNTER.ENTOMANCER_ELITE": "HP at A8+ 145 (155) -> 145 (165)",
    "ENCOUNTER.SOUL_FYSH_BOSS": "De-Gas at A9 16 (17) -> 16 (18)",
    "ENCOUNTER.AXEBOTS_NORMAL": "Hammer Uppercut and One-Two buffed; +10 max HP per respawn",
    "ENCOUNTER.EXOSKELETONS_NORMAL": "small A8-A9 buffs",
    "ENCOUNTER.EXOSKELETONS_WEAK": "small A8-A9 buffs",
    "ENCOUNTER.GLOBE_HEAD_NORMAL": "small A8-A9 buffs",
    "ENCOUNTER.LOUSE_PROGENITOR_NORMAL": "small A8-A9 buffs",
}


def band_of(ascension):
    return "A0-4" if ascension <= 4 else ("A5-9" if ascension <= 9 else "A10")


def load_benchmarks(character, ascension, data_dir=DATA):
    """Per encounter, the most comparable benchmark row: the character's band (n >= 5), then all characters in
    the band (n >= 5), then the character's pooled benchmark. Same rule as postmortem.py."""
    band = band_of(ascension)
    b = Path(data_dir) / "benchmarks"
    layers = [(b / f"{character.lower()}-encounters-v0.107.1.csv", f"{character.title()} pooled", False),
              (b / "allchars-encounters-by-band-v0.107.1.csv", f"all characters {band}", True),
              (b / f"{character.lower()}-encounters-by-band-v0.107.1.csv", f"{character.title()} {band}", True)]
    bench = {}
    for path, label, by_band in layers:  # least specific first; later layers overwrite
        if not path.exists():
            continue
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                if by_band and (r.get("band") != band or int(r["n"]) < 5):
                    continue
                bench[r["encounter"]] = dict(r, source=label)
    return bench


def normalize_encounter(name, known):
    """Accept ENCOUNTER.X, X, or a unique case-insensitive fragment (for example 'vantom')."""
    s = name.strip()
    cand = s if s.upper().startswith("ENCOUNTER.") else "ENCOUNTER." + s
    cand = "ENCOUNTER." + cand.split(".", 1)[1].upper()
    if cand in known:
        return cand
    frag = s.upper().replace(" ", "_")
    hits = sorted(k for k in known if frag in k)
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        raise SystemExit(f"'{name}' is ambiguous: {', '.join(hits)}")
    return cand  # unknown encounter: keep the normalized ID, no benchmark


def playbook_version(character):
    p = PROJECT / "playbooks" / f"{character.lower()}.md"
    if not p.exists():
        return "?"
    m = re.search(r"Version: v(\S+?)\s", p.read_text())
    return m.group(1) if m else "?"


def parse_header(text):
    m = HEADER_RE.search(text)
    if not m:
        raise SystemExit("journal header not recognised (expected '# Run <date> <seed>: <Character> A<n>, playbook v<x>')")
    return {"date": m.group(1), "seed": m.group(2), "character": m.group(3).upper(), "ascension": int(m.group(4)),
            "playbook": m.group(5)}


def new_journal(character, ascension, seed, exam=False, runs_dir=RUNS, now=None, template=TEMPLATE):
    now = now or datetime.now()
    run_dir = Path(runs_dir) / f"{now:%Y-%m-%d}-{seed}"
    path = run_dir / "journal.md"
    if path.exists():
        raise SystemExit(f"{path} already exists")
    t = Path(template).read_text()
    pv = playbook_version(character)
    t = t.replace("# Run <YYYY-MM-DD> <seed>: <Character> A<n>, playbook v<x>",
                  f"# Run {now:%Y-%m-%d} {seed}: {character.title()} A{ascension}, playbook v{pv}")
    t = t.replace("Run ID: <start_time>-<seed> · Exam seed: <yes/no> · Started: <time>",
                  f"Run ID: <start_time>-{seed} · Exam seed: {'yes' if exam else 'no'} · Started: {now:%Y-%m-%d %H:%M}")
    run_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(t)
    return path


def active_journals(runs_dir=RUNS):
    out = []
    for j in sorted(Path(runs_dir).glob("*/journal.md")):
        if not (j.parent / "postmortem.md").exists():
            out.append(j)
    return out


def _journal_path(run_dir):
    p = Path(run_dir)
    p = p if p.name == "journal.md" else p / "journal.md"
    if not p.exists():
        raise SystemExit(f"{p} not found")
    return p


def append_row(text, section, cells):
    """Append a markdown table row at the end of the table under '## <section>'."""
    lines = text.split("\n")
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == f"## {section}")
    except StopIteration:
        raise SystemExit(f"section '## {section}' not found")
    i, last = start + 1, None
    while i < len(lines) and not lines[i].startswith("## "):
        if lines[i].startswith("|"):
            last = i
        i += 1
    if last is None:
        raise SystemExit(f"no table under '## {section}'")
    row = "| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in cells) + " |"
    lines.insert(last + 1, row)
    return "\n".join(lines)


def table_rows(text, section):
    lines = text.split("\n")
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == f"## {section}")
    except StopIteration:
        return []
    rows, i = [], start + 1
    while i < len(lines) and not lines[i].startswith("## "):
        l = lines[i]
        if l.startswith("|") and not re.match(r"^\|[-| ]+\|$", l):
            rows.append([c.strip() for c in l.strip().strip("|").split("|")])
        i += 1
    return rows[1:]  # drop the header row


def status_from_state(st):
    """Accept a full STS2-Agent or STS2MCP state, or a compact snapshot."""
    if isinstance(st, dict) and ("screen" in st or "ok" in st):  # STS2-Agent full state
        from stsstate import compact
        c = compact(st)
        return {k: c.get(k) for k in ("floor", "act", "hp", "max_hp", "gold")} | {"potions": c.get("potions") or []}
    if "player" in st:
        p, run = st.get("player") or {}, st.get("run") or {}
        pots = [x.get("id") or x.get("name") for x in p.get("potions") or []]
        return {"floor": run.get("floor"), "act": run.get("act"), "hp": p.get("hp"), "max_hp": p.get("max_hp"),
                "gold": p.get("gold"), "potions": pots}
    return {k: st.get(k) for k in ("floor", "act", "hp", "max_hp", "gold")} | {"potions": st.get("potions") or []}


def set_status(text, s):
    pots = ", ".join(p for p in s.get("potions") or [] if p) or "none"
    line = f"Floor {s['floor']}, act {s['act']}, HP {s['hp']}/{s['max_hp']}, gold {s['gold']}, potions {pots}"
    lines = text.split("\n")
    i = next(i for i, l in enumerate(lines) if l.strip() == "## Status")
    j = i + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    if j < len(lines) and not lines[j].startswith("## "):
        lines[j] = line
    else:
        lines.insert(i + 1, line)
    return "\n".join(lines)


def fight_row(hdr, floor, encounter, turns, damage, potions, bench):
    enc = normalize_encounter(encounter, bench.keys() | CHANGED_V0111.keys())
    b = bench.get(enc)
    med = f"{float(b['median_dmg']):g} ({b['source']}, n={b['n']})" if b else "none"
    flags = []
    if b and damage > float(b["p75_dmg"]):
        flags.append(f"above p75 ({float(b['p75_dmg']):g})")
    if enc in CHANGED_V0111:
        flags.append("changed on v0.111.1")
    pots = ", ".join(potions) if potions else "none"
    return enc, [floor, enc.replace("ENCOUNTER.", ""), turns, damage, med + (" · " + "; ".join(flags) if flags else ""), pots], flags


def summarize(text, bench):
    rows = table_rows(text, "Fight log")
    total = bench_total = 0.0
    above, changed, missing = [], [], []
    for r in rows:
        if len(r) < 4:
            continue
        enc = "ENCOUNTER." + r[1]
        try:
            dmg = float(r[3])
        except ValueError:
            continue
        total += dmg
        b = bench.get(enc)
        if b:
            bench_total += float(b["median_dmg"])
            if dmg > float(b["p75_dmg"]):
                above.append(f"floor {r[0]} {r[1]}: {dmg:g} > p75 {float(b['p75_dmg']):g}")
        else:
            missing.append(r[1])
        if enc in CHANGED_V0111:
            changed.append(r[1])
    return {"fights": len(rows), "damage": total, "benchmark_median_total": bench_total, "above_p75": above,
            "changed_v0111": changed, "no_benchmark": missing}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("new"); a.add_argument("--character", default="IRONCLAD"); a.add_argument("--ascension", type=int, required=True)
    a.add_argument("--seed", required=True); a.add_argument("--exam", action="store_true")
    sub.add_parser("active")
    a = sub.add_parser("status"); a.add_argument("run_dir")
    for k in ("floor", "act", "hp", "max_hp", "gold"):
        a.add_argument("--" + k.replace("_", "-"), type=int)
    a.add_argument("--potions", default=""); a.add_argument("--from-state")
    a = sub.add_parser("floor"); a.add_argument("run_dir"); a.add_argument("--floor", type=int, required=True)
    a.add_argument("--room", required=True); a.add_argument("--result", default=""); a.add_argument("--hp-change", type=int, default=0)
    a.add_argument("--note", default="")
    a = sub.add_parser("fight"); a.add_argument("run_dir"); a.add_argument("--floor", type=int, required=True)
    a.add_argument("--encounter", required=True); a.add_argument("--turns", type=int, required=True)
    a.add_argument("--damage", type=int, required=True); a.add_argument("--potions", default="")
    a = sub.add_parser("budget"); a.add_argument("--encounter", required=True); a.add_argument("--character", default="IRONCLAD")
    a.add_argument("--ascension", type=int, required=True)
    a = sub.add_parser("summary"); a.add_argument("run_dir")
    args = ap.parse_args(argv)

    if args.cmd == "new":
        print(new_journal(args.character.upper(), args.ascension, args.seed, args.exam))
        if len(args.seed) != 12:
            print(f"note: seed has {len(args.seed)} characters; v0.111.1 seeds have 12")
        return 0
    if args.cmd == "active":
        js = active_journals()
        print("\n".join(str(j.relative_to(PROJECT)) for j in js) if js else "no run in progress")
        return 0
    if args.cmd == "budget":
        bench = load_benchmarks(args.character.upper(), args.ascension)
        enc = normalize_encounter(args.encounter, bench.keys() | CHANGED_V0111.keys())
        b = bench.get(enc)
        if not b:
            print(f"{enc}: no benchmark")
        else:
            print(f"{enc} ({b['source']}, n={b['n']}): median {float(b['median_dmg']):g}, p75 {float(b['p75_dmg']):g}, "
                  f"p90 {float(b['p90_dmg']):g}, median turns {float(b['median_turns']):g}")
        if enc in CHANGED_V0111:
            print(f"changed on v0.111.1: {CHANGED_V0111[enc]}")
        return 0

    path = _journal_path(args.run_dir)
    text = path.read_text()
    hdr = parse_header(text)
    if args.cmd == "status":
        if args.from_state:
            s = status_from_state(json.loads(Path(args.from_state).read_text()))
        else:
            missing = [k for k in ("floor", "act", "hp", "max_hp", "gold") if getattr(args, k) is None]
            if missing:
                raise SystemExit("missing: " + ", ".join("--" + m.replace("_", "-") for m in missing))
            s = {k: getattr(args, k) for k in ("floor", "act", "hp", "max_hp", "gold")}
            s["potions"] = [p.strip() for p in args.potions.split(",") if p.strip()]
        text = set_status(text, s)
    elif args.cmd == "floor":
        hp = f"{args.hp_change:+d}" if args.hp_change else "0"
        text = append_row(text, "Floor log", [args.floor, args.room, args.result, hp, args.note])
    elif args.cmd == "fight":
        bench = load_benchmarks(hdr["character"], hdr["ascension"])
        pots = [p.strip() for p in args.potions.split(",") if p.strip()]
        enc, row, flags = fight_row(hdr, args.floor, args.encounter, args.turns, args.damage, pots, bench)
        text = append_row(text, "Fight log", row)
        for f in flags:
            print(f"{enc}: {f}")
    elif args.cmd == "summary":
        s = summarize(text, load_benchmarks(hdr["character"], hdr["ascension"]))
        print(f"{s['fights']} fights, {s['damage']:g} damage taken; benchmark medians for the same fights sum to "
              f"{s['benchmark_median_total']:g}")
        for x in s["above_p75"]:
            print("above p75:", x)
        if s["changed_v0111"]:
            print("changed on v0.111.1 (benchmark less comparable):", ", ".join(s["changed_v0111"]))
        if s["no_benchmark"]:
            print("no benchmark:", ", ".join(s["no_benchmark"]))
        return 0
    path.write_text(text)
    print(f"updated {path.relative_to(PROJECT) if path.is_relative_to(PROJECT) else path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
