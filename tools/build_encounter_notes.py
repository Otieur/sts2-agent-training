#!/usr/bin/env python3
"""Generate the data sections of encounter notes and the encounter catalogue.

For every encounter seen in the run history (default: 3+ fights, v0.107.1, all characters), this writes:
  knowledge/encounters.md                       catalogue table
  knowledge/bosses/<ENCOUNTER>.md               bosses
  knowledge/enemies/<ENCOUNTER>.md              elites, and the most frequent hallway fights (--hallway N)

Each note has an auto-generated block between <!-- AUTO:BEGIN --> and <!-- AUTO:END --> markers. Text outside the
markers is hand-written and is preserved when the script is rerun. A new note gets a hand-written skeleton from the
template sections.

Usage: python3 -I tools/build_encounter_notes.py [--min-fights 3] [--hallway 15] [--deadly 2]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import MAIN_BUILD, PROJECT, connect, md_table, median, num, pct, quantile, short  # noqa: E402

EXTRACT = PROJECT / "knowledge/data/extract-2026-09-21"
BEGIN, END = "<!-- AUTO:BEGIN -->", "<!-- AUTO:END -->"
ALLIES = {"OSTY", "BYRDPIP"}  # player-side summons recorded in monster_ids

BOSS_SKELETON = """
## Plan (hand-written)

### Deck checklist
- TODO

### HP target on arrival
- TODO

### First three turns
1. TODO

### Potion plan
- TODO

### What killed the Player here, and the counter
- TODO

## Sources
- Monster data: `knowledge/data/extract-2026-09-21/monsters.json` `[GAME-EXTRACT]`
- Fight records: `data/runs.db` `[PLAYER-DATA]`
"""

ENEMY_SKELETON = """
## Plan (hand-written)

### Priorities and recommended answers
- TODO

### Ready to fight (elites)
- TODO

## Sources
- Monster data: `knowledge/data/extract-2026-09-21/monsters.json` `[GAME-EXTRACT]`
- Fight records: `data/runs.db` `[PLAYER-DATA]`
"""


def pool_of(enc):
    for s in ("_WEAK", "_NORMAL", "_ELITE", "_BOSS"):
        if enc.endswith(s):
            return s[1:].lower()
    return "event"


def pretty(enc):
    name = short(enc)
    for s in ("_BOSS", "_ELITE", "_NORMAL", "_WEAK", "_EVENT_ENCOUNTER"):
        if name.endswith(s):
            name = name[: -len(s)]
    return name.replace("_", " ").title()


def stats(fs):
    d = [f["damage_taken"] for f in fs]
    t = [f["turns_taken"] for f in fs if f["turns_taken"]]
    deaths = [f for f in fs if f["fatal"]]
    return {"n": len(fs), "median": median(d), "p75": quantile(d, 0.75), "p90": quantile(d, 0.9),
            "turns": median(t) if t else float("nan"), "deaths": len(deaths)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=MAIN_BUILD)
    ap.add_argument("--min-fights", type=int, default=3)
    ap.add_argument("--hallway", type=int, default=15)
    ap.add_argument("--deadly", type=int, default=2, help="also write notes for hallway fights with at least this many fatal fights")
    args = ap.parse_args()
    mons = {m["id"]: m for m in json.loads((EXTRACT / "monsters.json").read_text())}
    con = connect()
    rows = [dict(r) for r in con.execute("""
        SELECT f.run_id, f.floor, f.act, f.model_id AS enc, f.monster_ids, f.damage_taken, f.turns_taken, f.hp_before,
               f.max_hp, r.character, r.ascension, (f.is_last_floor AND NOT r.win AND NOT r.abandoned) AS fatal
        FROM floors f JOIN runs r USING(run_id)
        WHERE r.n_players = 1 AND r.build_id = ? AND f.room_type IN ('monster','elite','boss')""", [args.build])]
    by = collections.defaultdict(list)
    for r in rows:
        by[r["enc"]].append(r)

    hallway = sorted([e for e in by if pool_of(e) in ("weak", "normal")], key=lambda e: -len(by[e]))[: args.hallway]
    hallway += [e for e in by if pool_of(e) in ("weak", "normal") and e not in hallway
                and sum(f["fatal"] for f in by[e]) >= args.deadly]  # rare but deadly hallway fights
    catalogue = []
    written = 0
    for enc, fs in sorted(by.items(), key=lambda kv: (kv[1][0]["act"], pool_of(kv[0]), kv[0])):
        if len(fs) < args.min_fights:
            continue
        pool = pool_of(enc)
        act = collections.Counter(f["act"] for f in fs).most_common(1)[0][0]
        allc = stats(fs)
        iron = [f for f in fs if f["character"] == "IRONCLAD"]
        ic = stats(iron) if iron else None
        monster_counts = collections.Counter()
        for f in fs:
            for m in json.loads(f["monster_ids"] or "[]"):
                if m.split(".", 1)[-1] not in ALLIES:
                    monster_counts[m.split(".", 1)[-1]] += 1
        note_dir = "bosses" if pool == "boss" else "enemies"
        has_note = pool in ("boss", "elite") or enc in hallway
        link = f"[{note_dir}/{short(enc)}.md]({note_dir}/{short(enc)}.md)" if has_note else "-"
        catalogue.append([act, pool, pretty(enc), ", ".join(m.replace("_", " ").title() for m in monster_counts),
                          allc["n"], num(allc["median"], 0), num(allc["p90"], 0), allc["deaths"],
                          ic["n"] if ic else 0, num(ic["median"], 0) if ic else "-", num(ic["p90"], 0) if ic else "-",
                          ic["deaths"] if ic else "-", link])
        if not has_note:
            continue

        # Auto block
        A = [BEGIN, "", f"*Generated by `tools/build_encounter_notes.py` from `data/runs.db` ({args.build}, solo) and "
             "the extracted monster data. Do not edit inside these markers.*", "",
             f"**Act {act} · {pool}** · Encounter ID `{short(enc)}`", "", "### Monsters `[GAME-EXTRACT]`", ""]
        for mid, cnt in monster_counts.most_common():
            m = mons.get(mid)
            if not m:
                A.append(f"- **{mid.replace('_', ' ').title()}**: not in the extracted data.")
                continue
            hp = f"{m['min_hp']}" if m["min_hp"] == m["max_hp"] else f"{m['min_hp']}–{m['max_hp']}"
            A.append(f"- **{mid.replace('_', ' ').title()}** (HP {hp}, base values; seen in {cnt} of {len(fs)} fights)")
            for mv in m["moves"]:
                A.append(f"  - `{mv['move']}` {mv['intent']} → {mv['effect'] or '(no effect read)'}")
            if m["passive"]:
                A.append(f"  - Passive: {m['passive']}")
        surv = [f for f in fs if not f["fatal"]]
        dead = [f for f in fs if f["fatal"]]
        A += ["", "### The Player's record `[PLAYER-DATA]`", "",
              md_table(["Scope", "Fights", "Median dmg", "p75", "p90", "Median turns", "Fatal"],
                       [["All characters", allc["n"], num(allc["median"], 0), num(allc["p75"], 0), num(allc["p90"], 0),
                         num(allc["turns"], 0), allc["deaths"]]] +
                       ([["Ironclad", ic["n"], num(ic["median"], 0), num(ic["p75"], 0), num(ic["p90"], 0),
                          num(ic["turns"], 0), ic["deaths"]]] if ic else [])), ""]
        if dead:
            A.append(f"Arrival HP (all characters): survived fights median {pct(median([f['hp_before'] / f['max_hp'] for f in surv]) if surv else float('nan'))}, "
                     f"fatal fights median {pct(median([f['hp_before'] / f['max_hp'] for f in dead]))}. "
                     f"Characters: {', '.join(f'{k.title()} {v}' for k, v in collections.Counter(f['character'] for f in fs).most_common())}.")
            A.append("")
            A.append("Deck features on arrival, survived against fatal: see `reports/phase2/deck-features-by-encounter.md`.")
            A.append("")
        A.append(END)
        auto = "\n".join(A)

        path = PROJECT / "knowledge" / note_dir / f"{short(enc)}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            text = path.read_text()
            if BEGIN in text and END in text:
                pre, rest = text.split(BEGIN, 1)
                _, post = rest.split(END, 1)
                text = pre + auto + post
            else:
                # Existing hand-written note without markers: insert the auto block after the title block.
                lines = text.split("\n")
                cut = next((i for i, l in enumerate(lines) if l.startswith("## ")), len(lines))
                text = "\n".join(lines[:cut]) + "\n" + auto + "\n\n" + "\n".join(lines[cut:])
        else:
            title = f"# {pretty(enc)} ({short(enc)})\n\nStatus: data only; plan not written yet. Game version target v0.107.1.\n"
            text = title + "\n" + auto + "\n" + (BOSS_SKELETON if pool == "boss" else ENEMY_SKELETON)
        path.write_text(text)
        written += 1

    C = ["# Encounter Catalogue", "",
         f"Every encounter with {args.min_fights}+ fights in the Player's history ({args.build}, solo, all characters), "
         "generated by `tools/build_encounter_notes.py`. Damage is HP lost per fight. Notes exist for every boss and elite "
         f"and the {args.hallway} most frequent hallway fights, plus any hallway fight with {args.deadly}+ fatal fights.", "",
         md_table(["Act", "Pool", "Encounter", "Monsters", "Fights (all)", "Median dmg (all)", "p90 (all)", "Fatal (all)",
                   "Fights (Ironclad)", "Median (Ironclad)", "p90 (Ironclad)", "Fatal (Ironclad)", "Note"], catalogue), ""]
    (PROJECT / "knowledge/encounters.md").write_text("\n".join(C))
    print(f"catalogue: {len(catalogue)} encounters; notes written/updated: {written}")


if __name__ == "__main__":
    main()
