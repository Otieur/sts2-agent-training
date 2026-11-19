#!/usr/bin/env python3
"""Extract Slay the Spire 2 run history into a dataset.

Reads the game's save folder (read-only) and writes:
  data/raw/<run_id>.run      one copy of each unique run
  data/runs.db               SQLite database (schema below)
  data/tables/<table>.csv    CSV copy of every table

Usage:
  python3 -I tools/extract_runs.py [--save-root PATH]
"""
import argparse
import collections
import csv
import json
import shutil
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import DATA, DB_PATH  # noqa: E402

DEFAULT_SAVE_ROOT = Path.home() / "Library/Application Support/SlayTheSpire2/steam"
FIGHT_ROOMS = {"monster", "elite", "boss"}
SOURCE_PREFERENCE = {"main": 0, "modded": 1, "backup": 2}

SCHEMA = """
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY, seed TEXT, start_time INTEGER, build_id TEXT, character TEXT,
  ascension INTEGER, win INTEGER, abandoned INTEGER, killed_by_encounter TEXT, killed_by_event TEXT,
  floors_reached INTEGER, acts TEXT, run_time INTEGER, n_players INTEGER, game_mode TEXT,
  is_custom INTEGER, source_folders TEXT, has_ascenders_bane INTEGER,
  deck_match_ids INTEGER, deck_match_levels INTEGER, deck_diff TEXT);
CREATE TABLE floors (
  run_id TEXT, floor INTEGER, act INTEGER, act_floor INTEGER, map_point_type TEXT,
  room_type TEXT, room_types TEXT, model_id TEXT, all_models TEXT, monster_ids TEXT,
  turns_taken INTEGER, hp_before INTEGER, hp_after INTEGER, max_hp INTEGER, damage_taken INTEGER,
  hp_healed INTEGER, max_hp_gained INTEGER, max_hp_lost INTEGER, gold_before INTEGER,
  gold_after INTEGER, gold_gained INTEGER, gold_spent INTEGER, gold_lost INTEGER,
  gold_stolen INTEGER, deck_size_before INTEGER, is_last_floor INTEGER,
  PRIMARY KEY (run_id, floor));
CREATE TABLE card_offers (
  run_id TEXT, floor INTEGER, act INTEGER, offer_group TEXT, source TEXT, position INTEGER,
  card_id TEXT, upgrade_level INTEGER, picked INTEGER, deck_size_before INTEGER);
CREATE TABLE deck_changes (
  run_id TEXT, floor INTEGER, change TEXT, card_id TEXT, upgrade_level INTEGER, detail TEXT);
CREATE TABLE deck_snapshots (
  run_id TEXT, floor INTEGER, card_id TEXT, upgrade_level INTEGER, count INTEGER);
CREATE TABLE relic_events (
  run_id TEXT, floor INTEGER, kind TEXT, source TEXT, relic_id TEXT, picked INTEGER);
CREATE TABLE potion_events (
  run_id TEXT, floor INTEGER, kind TEXT, source TEXT, potion_id TEXT, picked INTEGER);
CREATE TABLE rest_choices (
  run_id TEXT, floor INTEGER, act INTEGER, choice TEXT, hp_before INTEGER, max_hp INTEGER,
  next_is_boss INTEGER, upgraded TEXT);
CREATE TABLE shop_visits (
  run_id TEXT, floor INTEGER, act INTEGER, gold_before INTEGER, gold_spent INTEGER,
  cards_bought INTEGER, colorless_bought INTEGER, relics_bought INTEGER, potions_bought INTEGER,
  removals INTEGER, removed TEXT);
CREATE TABLE event_choices (
  run_id TEXT, floor INTEGER, act INTEGER, event_id TEXT, choice_key TEXT, hp_change INTEGER,
  gold_change INTEGER, max_hp_change INTEGER);
CREATE TABLE ancient_choices (
  run_id TEXT, floor INTEGER, act INTEGER, ancient_id TEXT, option TEXT, chosen INTEGER);
CREATE TABLE final_deck (run_id TEXT, card_id TEXT, upgrade_level INTEGER, enchantment TEXT,
  floor_added INTEGER);
CREATE TABLE final_relics (run_id TEXT, relic_id TEXT, floor_added INTEGER);
CREATE INDEX idx_floors_run ON floors(run_id);
CREATE INDEX idx_offers_run ON card_offers(run_id);
CREATE INDEX idx_snap_run ON deck_snapshots(run_id, floor);
"""


def source_label(path: Path) -> str:
    parts = path.parts
    if "modded" in parts:
        return "modded"
    if any(p.startswith("back_prof") for p in parts):
        return "backup"
    return "main"


def none_if_null(v):
    return None if v in (None, "NONE.NONE") else v


def lvl(card: dict) -> int:
    return int(card.get("current_upgrade_level", 0) or 0)


def group_offers(n: int):
    """Split a reward screen's card list into reward groups (positions)."""
    if n in (6, 9):
        size = 3
    elif n == 8:
        size = 4
    else:
        size = n
    return [list(range(i, min(i + size, n))) for i in range(0, n, size)]


class Deck:
    """Multiset of [card_id, upgrade_level] instances replayed floor by floor."""

    def __init__(self, cards):
        self.cards = [[c, l] for c, l in cards]
        self.problems = []

    def size(self):
        return len(self.cards)

    def add(self, cid, level):
        self.cards.append([cid, level])

    def remove(self, cid, level, floor):
        for i, (c, l) in enumerate(self.cards):
            if c == cid and l == level:
                del self.cards[i]
                return
        for i, (c, l) in enumerate(self.cards):
            if c == cid:
                del self.cards[i]
                return
        self.problems.append(f"f{floor}: remove {cid} not in deck")

    def upgrade(self, cid, floor, delta=1):
        candidates = [x for x in self.cards if x[0] == cid]
        if not candidates:
            self.problems.append(f"f{floor}: upgrade {cid} not in deck")
            return
        target = min(candidates, key=lambda x: x[1]) if delta > 0 else max(candidates, key=lambda x: x[1])
        target[1] = max(0, target[1] + delta)

    def counter(self):
        return collections.Counter((c, l) for c, l in self.cards)


def inferred_starter(run):
    """Final deck minus all logged gains plus all logged losses."""
    d = collections.Counter(c["id"] for c in run["players"][0]["deck"])
    for act in run["map_point_history"]:
        for pt in act:
            for s in pt.get("player_stats", [])[:1]:
                for c in s.get("cards_gained", []):
                    d[c["id"]] -= 1
                for c in s.get("cards_removed", []):
                    d[c["id"]] += 1
                for c in s.get("cards_transformed", []):
                    d[c["final_card"]["id"]] -= 1
                    d[c["original_card"]["id"]] += 1
    return d


def process_run(run_id, run, sources, tables):
    players = run.get("players", [])
    n_players = len(players)
    character = players[0]["character"].split(".", 1)[-1] if players else None
    mph = run.get("map_point_history", [])
    floors_reached = sum(len(a) for a in mph)
    starter = inferred_starter(run)
    has_bane = int(starter.get("CARD.ASCENDERS_BANE", 0) > 0)

    run_row = {
        "run_id": run_id, "seed": str(run.get("seed")), "start_time": run.get("start_time"),
        "build_id": run.get("build_id"), "character": character, "ascension": run.get("ascension"),
        "win": int(bool(run.get("win"))), "abandoned": int(bool(run.get("was_abandoned"))),
        "killed_by_encounter": none_if_null(run.get("killed_by_encounter")),
        "killed_by_event": none_if_null(run.get("killed_by_event")),
        "floors_reached": floors_reached, "acts": json.dumps(run.get("acts", [])),
        "run_time": run.get("run_time"), "n_players": n_players, "game_mode": run.get("game_mode"),
        "is_custom": int(bool(run.get("is_custom_game"))), "source_folders": ",".join(sorted(sources)),
        "has_ascenders_bane": has_bane, "deck_match_ids": None, "deck_match_levels": None,
        "deck_diff": None,
    }

    for c in players[0].get("deck", []) if players else []:
        ench = c.get("enchantment", {})
        tables["final_deck"].append((run_id, c["id"], lvl(c), ench.get("id") if ench else None,
                                     c.get("floor_added_to_deck")))
    for r in players[0].get("relics", []) if players else []:
        tables["final_relics"].append((run_id, r["id"], r.get("floor_added_to_deck")))

    if n_players != 1:
        # Co-op runs: per-player attribution is ambiguous; keep only the run row.
        tables["runs"].append(run_row)
        return

    deck = Deck([(cid, 0) for cid, n in starter.items() for _ in range(max(0, n))])
    floor = 0
    prev_hp = prev_gold = None
    flat_points = [(ai, pi, pt) for ai, act in enumerate(mph, 1) for pi, pt in enumerate(act, 1)]
    for idx, (ai, pi, pt) in enumerate(flat_points):
        floor += 1
        s = (pt.get("player_stats") or [{}])[0]
        rooms = pt.get("rooms", [])
        mtype = pt.get("map_point_type")
        fight = next((r for r in rooms if r.get("room_type") in FIGHT_ROOMS), None)
        primary = fight or (rooms[0] if rooms else {})
        room_type = primary.get("room_type")
        model_id = primary.get("model_id")
        hp_after = s.get("current_hp")
        max_hp = s.get("max_hp")
        dmg = s.get("damage_taken", 0) or 0
        healed = s.get("hp_healed", 0) or 0
        if prev_hp is None:
            hp_before = max_hp
        else:
            hp_before = prev_hp
        gold_after = s.get("current_gold")
        if prev_gold is None:
            gold_before = (gold_after or 0) - (s.get("gold_gained", 0) or 0) + (s.get("gold_spent", 0) or 0) \
                + (s.get("gold_lost", 0) or 0) + (s.get("gold_stolen", 0) or 0)
        else:
            gold_before = prev_gold
        deck_before = deck.size()
        next_type = flat_points[idx + 1][2].get("map_point_type") if idx + 1 < len(flat_points) else None

        tables["floors"].append((
            run_id, floor, ai, pi, mtype, room_type, ",".join(r.get("room_type", "") for r in rooms),
            model_id, ",".join(r.get("model_id", "") for r in rooms if r.get("model_id")),
            json.dumps(primary.get("monster_ids", [])) if fight else None,
            sum((r.get("turns_taken") or 0) for r in rooms) if fight else None,
            hp_before, hp_after, max_hp, dmg, healed, s.get("max_hp_gained", 0), s.get("max_hp_lost", 0),
            gold_before, gold_after, s.get("gold_gained", 0), s.get("gold_spent", 0), s.get("gold_lost", 0),
            s.get("gold_stolen", 0), deck_before, int(idx == len(flat_points) - 1)))

        # Card offers
        cc = s.get("card_choices") or []
        if cc:
            if mtype in ("monster", "elite", "boss") or (mtype == "unknown" and fight):
                source = "reward"
            elif mtype == "shop":
                source = "shop"
            elif mtype == "ancient":
                source = "ancient"
            else:
                source = "event"
            groups = group_offers(len(cc)) if source == "reward" else [list(range(len(cc)))]
            for gi, positions in enumerate(groups):
                gid = f"{run_id}:{floor}:{gi}"
                for pos in positions:
                    c = cc[pos]
                    tables["card_offers"].append((run_id, floor, ai, gid, source, pos, c["card"]["id"],
                                                  lvl(c["card"]), int(bool(c.get("was_picked"))), deck_before))
        if mtype == "shop":
            # The shop's card list usually holds only the stock left unsold; purchases appear in
            # cards_gained. Add each bought card as an offered-and-picked row unless already marked.
            already = collections.Counter(c["card"]["id"] for c in cc if c.get("was_picked"))
            gid = f"{run_id}:{floor}:0"
            for pos, c in enumerate(s.get("cards_gained", []), start=len(cc)):
                if already[c["id"]] > 0:
                    already[c["id"]] -= 1
                    continue
                tables["card_offers"].append((run_id, floor, ai, gid, "shop", pos, c["id"], lvl(c), 1, deck_before))

        # Deck changes, applied in order: gains, transforms, upgrades, downgrades, removals
        for c in s.get("cards_gained", []):
            deck.add(c["id"], lvl(c))
            tables["deck_changes"].append((run_id, floor, "gained", c["id"], lvl(c), mtype))
        for t in s.get("cards_transformed", []):
            o, fcard = t["original_card"], t["final_card"]
            deck.remove(o["id"], lvl(o), floor)
            deck.add(fcard["id"], lvl(fcard))
            tables["deck_changes"].append((run_id, floor, "transformed_from", o["id"], lvl(o), fcard["id"]))
            tables["deck_changes"].append((run_id, floor, "transformed_to", fcard["id"], lvl(fcard), o["id"]))
        for cid in s.get("upgraded_cards", []):
            deck.upgrade(cid, floor, +1)
            tables["deck_changes"].append((run_id, floor, "upgraded", cid, None, mtype))
        for cid in s.get("downgraded_cards", []):
            deck.upgrade(cid, floor, -1)
            tables["deck_changes"].append((run_id, floor, "downgraded", cid, None, mtype))
        for c in s.get("cards_removed", []):
            deck.remove(c["id"], lvl(c), floor)
            tables["deck_changes"].append((run_id, floor, "removed", c["id"], lvl(c), mtype))
        for e in s.get("cards_enchanted", []):
            tables["deck_changes"].append((run_id, floor, "enchanted", e["card"]["id"], lvl(e["card"]),
                                           e.get("enchantment")))

        for (cid, level), n in deck.counter().items():
            tables["deck_snapshots"].append((run_id, floor, cid, level, n))

        # Relics
        for rc in s.get("relic_choices", []):
            tables["relic_events"].append((run_id, floor, "offered", mtype, rc["choice"], int(bool(rc.get("was_picked")))))
        for rid in s.get("bought_relics", []):
            tables["relic_events"].append((run_id, floor, "bought", mtype, rid, 1))
        for rid in s.get("relics_removed", []):
            tables["relic_events"].append((run_id, floor, "removed", mtype, rid, None))

        # Potions
        for pc in s.get("potion_choices", []):
            tables["potion_events"].append((run_id, floor, "offered", mtype, pc["choice"], int(bool(pc.get("was_picked")))))
        for pid in s.get("potion_used", []):
            tables["potion_events"].append((run_id, floor, "used", room_type or mtype, pid, None))
        for pid in s.get("potion_discarded", []):
            tables["potion_events"].append((run_id, floor, "discarded", room_type or mtype, pid, None))
        for pid in s.get("bought_potions", []):
            tables["potion_events"].append((run_id, floor, "bought", mtype, pid, 1))

        # Rest sites
        for choice in s.get("rest_site_choices", []):
            tables["rest_choices"].append((run_id, floor, ai, choice, hp_before, max_hp,
                                           int(next_type == "boss"), ",".join(s.get("upgraded_cards", []))))

        # Shops
        if mtype == "shop":
            colorless = len(s.get("bought_colorless", []))
            class_cards = max(0, len(s.get("cards_gained", [])) - colorless)
            tables["shop_visits"].append((run_id, floor, ai, gold_before, s.get("gold_spent", 0), class_cards,
                                          len(s.get("bought_colorless", [])), len(s.get("bought_relics", [])),
                                          len(s.get("bought_potions", [])), len(s.get("cards_removed", [])),
                                          ",".join(c["id"] for c in s.get("cards_removed", []))))

        # Events (non-Ancient)
        if mtype != "ancient":
            event_room = next((r for r in rooms if str(r.get("model_id", "")).startswith("EVENT.")), None)
            for ec in s.get("event_choices", []):
                key = ec.get("title", {}).get("key")
                tables["event_choices"].append((run_id, floor, ai, event_room.get("model_id") if event_room else None,
                                                key, (hp_after or 0) - (hp_before or 0), (gold_after or 0) - (gold_before or 0),
                                                (s.get("max_hp_gained", 0) or 0) - (s.get("max_hp_lost", 0) or 0)))

        # Ancients
        if mtype == "ancient":
            for ac in s.get("ancient_choice", []):
                tables["ancient_choices"].append((run_id, floor, ai, model_id, ac.get("TextKey"),
                                                  int(bool(ac.get("was_chosen")))))

        prev_hp, prev_gold = hp_after, gold_after

    # Validate reconstruction against the recorded final deck
    recorded = collections.Counter((c["id"], lvl(c)) for c in players[0]["deck"])
    rebuilt = deck.counter()
    rec_ids = collections.Counter(c for c, _ in recorded.elements())
    reb_ids = collections.Counter(c for c, _ in rebuilt.elements())
    run_row["deck_match_ids"] = int(rec_ids == reb_ids)
    run_row["deck_match_levels"] = int(recorded == rebuilt)
    if recorded != rebuilt or deck.problems:
        diff = {"missing": [f"{c}+{l}" for (c, l), n in (recorded - rebuilt).items() for _ in range(n)],
                "extra": [f"{c}+{l}" for (c, l), n in (rebuilt - recorded).items() for _ in range(n)],
                "problems": deck.problems}
        run_row["deck_diff"] = json.dumps(diff)
    tables["runs"].append(run_row)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--save-root", type=Path, default=DEFAULT_SAVE_ROOT)
    args = ap.parse_args()

    files = sorted(args.save_root.glob("**/saves/history/*.run"))
    if not files:
        raise SystemExit(f"No .run files under {args.save_root}")

    unique = {}  # key -> (preference, path, run, sources)
    for f in files:
        try:
            run = json.loads(f.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"skip unreadable {f.name}: {e}", file=sys.stderr)
            continue
        key = (str(run.get("seed")), run.get("start_time"))
        label = source_label(f)
        if key in unique:
            pref, path, r, sources = unique[key]
            sources.add(label)
            if SOURCE_PREFERENCE[label] < pref:
                unique[key] = (SOURCE_PREFERENCE[label], f, run, sources)
        else:
            unique[key] = (SOURCE_PREFERENCE[label], f, run, {label})

    raw_dir = DATA / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    tables = collections.defaultdict(list)
    for (seed, start), (_, path, run, sources) in sorted(unique.items(), key=lambda kv: kv[0][1] or 0):
        run_id = f"{start}-{seed}"
        shutil.copyfile(path, raw_dir / f"{run_id}.run")
        process_run(run_id, run, sources, tables)

    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    run_cols = ["run_id", "seed", "start_time", "build_id", "character", "ascension", "win", "abandoned",
                "killed_by_encounter", "killed_by_event", "floors_reached", "acts", "run_time", "n_players",
                "game_mode", "is_custom", "source_folders", "has_ascenders_bane", "deck_match_ids",
                "deck_match_levels", "deck_diff"]
    con.executemany(f"INSERT INTO runs VALUES ({','.join('?' * len(run_cols))})",
                    [tuple(r[c] for c in run_cols) for r in tables["runs"]])
    for name, rows in tables.items():
        if name == "runs" or not rows:
            continue
        con.executemany(f"INSERT INTO {name} VALUES ({','.join('?' * len(rows[0]))})", rows)
    con.commit()

    out = DATA / "tables"
    out.mkdir(parents=True, exist_ok=True)
    for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        cur = con.execute(f"SELECT * FROM {name}")
        with open(out / f"{name}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow([d[0] for d in cur.description])
            w.writerows(cur)

    counts = {name: con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
              for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    con.close()
    print(f"files scanned: {len(files)}  unique runs: {len(unique)}")
    for k, v in counts.items():
        print(f"  {k:16s} {v}")


if __name__ == "__main__":
    main()
