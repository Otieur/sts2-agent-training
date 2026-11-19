#!/usr/bin/env python3
"""Path planner (P4.E3.S1): enumerate every route from the current map node to the act boss, simulate expected HP
room by room from the Player's history, and rank routes by expected loot against the risk of a fatal fight.

Model per room, by act (all characters on v0.107.1 unless the character has 30+ visits of that kind):
  - HP change: mean net HP change of that room type as a share of max HP          [PLAYER-DATA]
  - Loot: mean cards, relics, potions and gold taken there                          [PLAYER-DATA]
  - Rest sites follow the playbook rule (section 5): rest before a boss below its threshold, before an elite when
    HP minus the elite's p75 would fall under 50%, or under 35% HP; otherwise smith. A rest heals 30% of max HP.
  - Fatal risk: elites by entry HP band (under 50% / 50-70% / 70%+, from the data, the playbook's H5 rule);
    hallway fights the same way; the boss by a logistic fit of fatal against arrival HP for the act.
Score = value - risk_weight x P(run ends on this route). Value counts relics 1, cards 0.3, upgrades 0.3,
potions 0.1, gold 0.004 per gold. Weights are [HYPOTHESIS]. The risk weight is the main lever. Defaults by act,
12 / 16 / 25, come from the history: among runs that survived Act 1, each Act 1 elite (about 1.15 value units)
went with about +3.5 points of final win rate, so one value unit is about 3.5 points; dying forfeits the win
chance of a survivor (about 35% after Act 1, 56% after Act 2, all of it in Act 3). 0.35 / 0.035 = 10 is a lower
bound because stronger decks both take elites and win (confounding), hence 12.

Usage:
  python3 -I tools/path.py --state state.json [--top 5] [--risk-weight 25]   (STS2-Agent full /state on the map)
  python3 -I tools/path.py --map-file map.json --hp 60 --max-hp 80 --act 1 [--ascension 0] [--boss VANTOM_BOSS]
Map file: {"nodes": [{"row", "col", "node_type", "children": [{"row", "col"}]}], "current_node": {"row", "col"} | null,
           "starting_node": {...}, "boss_node": {...}}
"""
import argparse
import collections
import csv
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import DATA, MAIN_BUILD, connect  # noqa: E402

TYPE_MAP = {"monster": "monster", "elite": "elite", "unknown": "unknown", "event": "unknown", "shop": "shop",
            "rest": "rest_site", "restsite": "rest_site", "rest_site": "rest_site", "treasure": "treasure",
            "boss": "boss", "ancient": "ancient", "start": "start"}
SHORT = {"monster": "M", "elite": "E", "unknown": "?", "shop": "$", "rest_site": "R", "treasure": "T", "boss": "B",
         "ancient": "A", "start": "S"}
VALUE = {"relic": 1.0, "card": 0.3, "upgrade": 0.3, "potion": 0.1, "gold": 0.004}
REST_HEAL = 0.30
DEFAULT_RISK_WEIGHT = {1: 12.0, 2: 16.0, 3: 25.0}
MAX_PATHS = 60000


def norm_type(t):
    return TYPE_MAP.get((t or "").replace(" ", "").lower(), "unknown")


# ------------------------------------------------------------------------------------------------ model
class Model:
    def __init__(self, character="IRONCLAD", ascension=0, con=None):
        self.character, self.ascension = character.upper(), ascension
        own_con = con is None
        con = con or connect()
        rows = [dict(r) for r in con.execute("""
            SELECT f.run_id, f.floor, f.act, f.map_point_type AS t, f.room_type, f.hp_before, f.hp_after, f.max_hp,
                   f.gold_gained, r.character, (f.is_last_floor AND NOT r.win AND NOT r.abandoned) AS died
            FROM floors f JOIN runs r USING(run_id)
            WHERE r.n_players = 1 AND r.build_id = ? AND NOT r.abandoned AND f.max_hp > 0""", [MAIN_BUILD])]
        gains = collections.defaultdict(collections.Counter)
        for r in con.execute("SELECT run_id, floor FROM deck_changes WHERE change='gained'"):
            gains[(r["run_id"], r["floor"])]["card"] += 1
        for r in con.execute("SELECT run_id, floor, kind, picked FROM relic_events WHERE kind IN ('offered','bought')"):
            if r["kind"] == "bought" or r["picked"]:
                gains[(r["run_id"], r["floor"])]["relic"] += 1
        for r in con.execute("SELECT run_id, floor, kind, picked FROM potion_events WHERE kind IN ('offered','bought')"):
            if r["kind"] == "bought" or r["picked"]:
                gains[(r["run_id"], r["floor"])]["potion"] += 1
        self.room = {}
        for act in (1, 2, 3):
            for t in ("monster", "elite", "unknown", "shop", "treasure"):
                xs = [x for x in rows if x["act"] == act and x["t"] == t]
                own = [x for x in xs if x["character"] == self.character]
                use = own if len(own) >= 30 else xs
                if not use:
                    continue
                g = [gains[(x["run_id"], x["floor"])] for x in use]
                self.room[(act, t)] = {
                    "hp": sum((x["hp_after"] - x["hp_before"]) / x["max_hp"] for x in use) / len(use),
                    "card": sum(c["card"] for c in g) / len(use), "relic": sum(c["relic"] for c in g) / len(use),
                    "potion": sum(c["potion"] for c in g) / len(use),
                    "gold": sum(x["gold_gained"] or 0 for x in use) / len(use), "n": len(use),
                    "source": self.character.title() if use is own else "all characters"}
        # fatal rates by entry HP band, fights only (elite, monster); boss: logistic per act
        self.band_risk = {}
        for kind in ("elite", "monster"):
            for lo, hi in ((0, .5), (.5, .7), (.7, 9)):
                xs = [x for x in rows if x["room_type"] == kind and lo <= x["hp_before"] / x["max_hp"] < hi]
                self.band_risk[(kind, lo)] = (sum(x["died"] for x in xs) + 0.5) / (len(xs) + 1) if xs else 0.05
        self.boss_curve = {}
        for act in (1, 2, 3):
            pts = [(x["hp_before"] / x["max_hp"], x["died"]) for x in rows if x["room_type"] == "boss" and x["act"] == act]
            self.boss_curve[act] = _fit(pts) if len(pts) >= 10 else (lambda h: 0.25)
        self.elite_p75 = self._elite_p75()
        if own_con:
            con.close()

    def _elite_p75(self):
        path = DATA / "benchmarks" / f"{self.character.lower()}-encounters-v0.107.1.csv"
        vals = collections.defaultdict(list)
        if path.exists():
            for r in csv.DictReader(open(path)):
                if r.get("room") == "elite" or "_ELITE" in r["encounter"]:
                    vals[int(r.get("act") or 0)].append(float(r["p75_dmg"]))
        return {a: (sum(v) / len(v)) for a, v in vals.items() if v}

    def fight_risk(self, kind, hp_frac):
        lo = 0 if hp_frac < .5 else (.5 if hp_frac < .7 else .7)
        return self.band_risk.get((kind, lo), 0.05)

    def boss_threshold(self, act, boss, max_hp):
        """Rest-before-boss threshold in HP (playbook section 5): band median + 10 in Acts 1-2, 70% in Act 3."""
        if act >= 3:
            return 0.70 * max_hp
        band = "A0-4" if self.ascension <= 4 else ("A5-9" if self.ascension <= 9 else "A10")
        med = None
        for fname, by_band in ((f"{self.character.lower()}-encounters-by-band-v0.107.1.csv", True),
                               ("allchars-encounters-by-band-v0.107.1.csv", True)):
            p = DATA / "benchmarks" / fname
            if med is None and p.exists() and boss:
                for r in csv.DictReader(open(p)):
                    if r["encounter"].endswith(boss.replace("ENCOUNTER.", "")) and r["band"] == band and int(r["n"]) >= 5:
                        med = float(r["median_dmg"])
        return (med if med is not None else 40.0) + 10


_MODELS = {}


def get_model(character="IRONCLAD", ascension=0):
    """Cached Model: building one reads the whole history and fits three curves."""
    key = (character.upper(), int(ascension))
    if key not in _MODELS:
        _MODELS[key] = Model(*key)
    return _MODELS[key]


def _fit(points, iters=4000, lr=0.5):
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


# ------------------------------------------------------------------------------------------------ map
def load_map(m):
    nodes = {}
    for n in m.get("nodes") or []:
        nodes[(n["row"], n["col"])] = {"type": norm_type(n.get("node_type")),
                                       "children": [(c["row"], c["col"]) for c in n.get("children") or []]}
    def rc(x):
        return (x["row"], x["col"]) if x else None
    start = rc(m.get("current_node")) or rc(m.get("starting_node"))
    boss = rc(m.get("boss_node"))
    if boss and boss not in nodes:
        nodes[boss] = {"type": "boss", "children": []}
    return nodes, start, boss


def enumerate_paths(nodes, start, boss):
    out, stack = [], [(start, [start])]
    while stack:
        cur, path = stack.pop()
        kids = nodes.get(cur, {}).get("children") or []
        if cur == boss or not kids:
            if cur == boss:
                out.append(path)
            continue
        for k in kids:
            stack.append((k, path + [k]))
        if len(out) > MAX_PATHS:
            break
    return out


def simulate(path, nodes, model, act, hp, max_hp, boss_id):
    """Walk the path (excluding the start node). Returns the outcome dict."""
    types = [nodes[p]["type"] for p in path[1:]]
    hp = float(hp)
    loot = collections.Counter()
    survive, notes, elite_hp, risks = 1.0, [], [], []
    for i, t in enumerate(types):
        frac = hp / max_hp
        if t in ("monster", "elite"):
            r = model.fight_risk(t, frac)
            survive *= 1 - r
            risks.append((t, r))
            if t == "elite":
                elite_hp.append(round(100 * frac))
                if frac < 0.5:
                    notes.append(f"elite at {100 * frac:.0f}% HP")
        if t == "rest_site":
            nxt = next((x for x in types[i + 1:] if x in ("elite", "boss", "rest_site")), "boss")
            p75 = model.elite_p75.get(act, 35.0)
            rest = ((nxt == "boss" and hp < model.boss_threshold(act, boss_id, max_hp))
                    or (nxt == "elite" and hp - p75 < 0.5 * max_hp) or frac < 0.35)
            if rest:
                hp = min(max_hp, hp + math.floor(REST_HEAL * max_hp))
                loot["rest"] += 1
            else:
                loot["upgrade"] += 1
        elif t == "boss":
            r = model.boss_curve[act](frac)
            survive *= 1 - r
            risks.append(("boss", r))
            break
        elif t in ("monster", "elite", "unknown", "shop", "treasure"):
            rv = model.room.get((act, t))
            if rv:
                hp = max(1.0, min(max_hp, hp + rv["hp"] * max_hp))
                for k in ("card", "relic", "potion", "gold"):
                    loot[k] += rv[k]
    value = sum(VALUE[k] * loot[k] for k in VALUE)
    return {"types": types, "seq": "".join(SHORT.get(t, "?") for t in types), "value": value, "loot": loot,
            "p_end": 1 - survive, "boss_hp": round(100 * hp / max_hp) if types and types[-1] == "boss" else None,
            "boss_hp_abs": round(hp), "elite_hp": elite_hp, "notes": notes, "risks": risks,
            "elites": types.count("elite"), "first": path[1] if len(path) > 1 else None}


def rank(paths, nodes, model, act, hp, max_hp, boss_id, risk_weight):
    res, seen = [], set()
    for p in paths:
        o = simulate(p, nodes, model, act, hp, max_hp, boss_id)
        key = (o["first"], o["seq"])
        if key in seen:
            continue
        seen.add(key)
        o["score"] = o["value"] - risk_weight * o["p_end"]
        res.append(o)
    res.sort(key=lambda o: -o["score"])
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state")
    ap.add_argument("--map-file")
    ap.add_argument("--hp", type=int)
    ap.add_argument("--max-hp", type=int)
    ap.add_argument("--act", type=int)
    ap.add_argument("--ascension", type=int, default=0)
    ap.add_argument("--character", default="IRONCLAD")
    ap.add_argument("--boss")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--risk-weight", type=float, default=None, help="default by act: 12 / 16 / 25")
    args = ap.parse_args(argv)
    if args.state:
        st = json.loads(Path(args.state).read_text())
        st = st.get("data", st)
        m, run = st.get("map") or {}, st.get("run") or {}
        hp, max_hp = args.hp or run.get("current_hp"), args.max_hp or run.get("max_hp")
        act = args.act or int(run.get("act_id") or 1)
        asc = args.ascension or int(run.get("ascension") or 0)
        boss = args.boss or run.get("boss_id")
    else:
        m = json.loads(Path(args.map_file).read_text())
        hp, max_hp, act, asc, boss = args.hp, args.max_hp, args.act or 1, args.ascension, args.boss
    if not (hp and max_hp):
        raise SystemExit("need --hp and --max-hp (or a state with run.current_hp/max_hp)")
    nodes, start, boss_rc = load_map(m)
    paths = enumerate_paths(nodes, start, boss_rc)
    if not paths:
        raise SystemExit("no route from the current node to the boss")
    model = get_model(args.character, asc)
    args.risk_weight = args.risk_weight or DEFAULT_RISK_WEIGHT.get(act, 16.0)
    res = rank(paths, nodes, model, act, hp, max_hp, boss, args.risk_weight)
    print(f"{len(paths)} routes, {len(res)} distinct · act {act} · HP {hp}/{max_hp} · A{asc} · boss {boss or '?'} · "
          f"risk weight {args.risk_weight:g}")
    print("Legend: M monster, E elite, ? unknown, $ shop, R rest, T treasure, B boss")
    for o in res[:args.top]:
        L = o["loot"]
        print(f"  score {o['score']:5.2f}  first {o['first']}  {o['seq']}")
        print(f"      elites {o['elites']} (entry HP {o['elite_hp'] or '-'}%), boss arrival {o['boss_hp']}% "
              f"({o['boss_hp_abs']} HP), P(run ends) {100 * o['p_end']:.0f}%, relics {L['relic']:.1f}, cards {L['card']:.1f}, "
              f"upgrades {L['upgrade']:.0f}, rests {L['rest']:.0f}, gold {L['gold']:.0f}"
              + (f"  ! {'; '.join(o['notes'])}" if o["notes"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
