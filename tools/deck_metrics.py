#!/usr/bin/env python3
"""Deck-strength proxies from card data, and how they relate to boss outcomes.

For a deck (list of card IDs) this estimates, by Monte Carlo over random 5-card hands with 3 energy:
  - damage per turn (greedy: play the highest damage-per-energy attacks the energy allows)
  - block per turn (greedy on block)
Card numbers come from the extracted game data (base values; '?' values count as 0, so cards like Body Slam,
Perfected Strike and Ashen Strike are undervalued). Ignores Strength, powers, relics, synergies and upgrades:
it measures the deck's raw "attack" and "defence" corners, not its scaling.

Usage:
  python3 -I tools/deck_metrics.py                      # boss-outcome report → reports/phase2/deck-strength.md
  python3 -I tools/deck_metrics.py --deck CARD.STRIKE_IRONCLAD CARD.BASH ...   # metrics for one deck
"""
import argparse
import collections
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import MAIN_BUILD, PROJECT, connect, md_table, mean, median, pct  # noqa: E402

CARDS = {c["id"]: c for c in json.loads((PROJECT / "knowledge/data/extract-2026-09-21/cards.json").read_text())}
PATCHES = PROJECT / "knowledge" / "data" / "card-patches.json"
APPLIED = []


def apply_patches(upto):
    """Bring CARDS from the extract (pre-v0.107.1) up to game version `upto` ("v0.107.1" or "v0.111.1"), in place.
    Idempotent per version; versions are applied in order. See knowledge/data/card-patches.json."""
    spec = json.loads(PATCHES.read_text())
    order = spec["versions"]
    if upto not in order:
        raise ValueError(f"unknown version {upto}; known: {order}")
    for v in order[: order.index(upto) + 1]:
        if v in APPLIED:
            continue
        for pt in spec["patches"]:
            if pt["version"] != v or pt["id"] not in CARDS:
                continue
            c = dict(CARDS[pt["id"]])
            for old, new in pt.get("replace", []):
                c["effect"] = (c.get("effect") or "").replace(old, new)
            c.update(pt.get("set", {}))
            c["patched"] = v
            CARDS[pt["id"]] = c
        APPLIED.append(v)
    return list(APPLIED)
HAND, ENERGY, SIMS = 5, 3, 300


def card_numbers(cid):
    c = CARDS.get(cid.split(".", 1)[-1])
    if not c:
        return None
    e = c["effect"] or ""
    cost = c["cost"]
    if cost is None or (cost < 0 and c["type"] not in ("Attack", "Skill", "Power")):
        return {"playable": False}
    if cost < 0 or "X (energy spent)" in e:
        cost = ENERGY  # X-cost: assume it takes the whole turn's energy
    hits = 1
    m = re.search(r"damage (\d+) times", e)
    if m:
        hits = int(m.group(1))
    elif "X (energy spent) times" in e:
        hits = ENERGY
    dmg = sum(int(x) for x in re.findall(r"Deal (\d+) damage", e)) * hits
    block = sum(int(x) for x in re.findall(r"(?:Gain|Give(?: the target)?) (\d+) Block", e))
    draw = sum(int(x) for x in re.findall(r"Draw (\d+) card", e))
    energy = sum(int(x) for x in re.findall(r"Gain (\d+) Energy", e))
    unplayable = "Unplayable" in e or c["type"] in ("Status", "Curse")
    return {"playable": not unplayable, "cost": cost, "dmg": dmg, "block": block, "draw": draw, "energy": energy}


def simulate(deck, mode, sims=SIMS, seed=7):
    rng = random.Random(seed)
    nums = [card_numbers(c) for c in deck]
    nums = [n for n in nums if n is not None]
    if not nums:
        return 0.0
    total = 0.0
    key = "dmg" if mode == "damage" else "block"
    for _ in range(sims):
        pile = nums[:]
        rng.shuffle(pile)
        hand, pile = pile[:HAND], pile[HAND:]
        energy, value = ENERGY, 0
        while True:
            playable = [c for c in hand if c["playable"] and c["cost"] <= energy]
            if not playable:
                break
            # prefer free energy/draw, then the best value per energy
            def score(c):
                if c["energy"] > 0 or (c["draw"] > 0 and c["cost"] == 0):
                    return (2, 0)
                return (1, (c[key] / c["cost"]) if c["cost"] else c[key] * 10)
            best = max(playable, key=score)
            if best[key] == 0 and best["energy"] == 0 and best["draw"] == 0:
                break
            hand.remove(best)
            energy += best["energy"] - best["cost"]
            value += best[key]
            for _ in range(best["draw"]):
                if pile:
                    hand.append(pile.pop(0))
        total += value
    return total / sims


def scaling_count(deck):
    """Cards that grow over a fight: Powers, plus non-power cards that grant Strength."""
    n = 0
    for cid in deck:
        c = CARDS.get(cid.split(".", 1)[-1])
        if c and (c["type"] == "Power" or "strength" in c["tags"]):
            n += 1
    return n


def deck_at(con, run_id, floor):
    deck = []
    for r in con.execute("SELECT card_id, count FROM deck_snapshots WHERE run_id=? AND floor=?", (run_id, floor - 1)):
        deck += [r["card_id"]] * r["count"]
    return deck


def report():
    con = connect()
    fights = [dict(r) for r in con.execute("""
        SELECT f.run_id, f.floor, f.act, f.model_id AS enc, f.damage_taken, r.character, r.ascension,
               (f.is_last_floor AND NOT r.win AND NOT r.abandoned) AS died
        FROM floors f JOIN runs r USING(run_id)
        WHERE r.n_players = 1 AND r.build_id = ? AND f.room_type = 'boss' AND NOT r.abandoned""", [MAIN_BUILD])]
    for f in fights:
        deck = deck_at(con, f["run_id"], f["floor"])
        f["size"] = len(deck)
        f["scaling"] = scaling_count(deck)
        f["dmg"] = simulate(deck, "damage")
        f["blk"] = simulate(deck, "block")
    L = ["# Deck Strength at the Boss", "",
         f"All characters, solo, {MAIN_BUILD}, finished runs: every boss fight with the deck at the start of the boss floor. "
         "Built by `tools/deck_metrics.py`. Proxies: average damage and block per turn from random 5-card hands with 3 "
         "energy, using base card numbers `[GAME-EXTRACT]` brought to v0.107.1 with `knowledge/data/card-patches.json` "
         "(the extract predates v0.107.1). They ignore Strength, powers, relics, upgrades and cards whose "
         "numbers are computed at play time, so they measure the raw attack and defence corners, not scaling. "
         "`[PLAYER-DATA]`, observational.", ""]
    rows = []
    for act in (1, 2, 3):
        xs = [f for f in fights if f["act"] == act]
        s = [f for f in xs if not f["died"]]
        d = [f for f in xs if f["died"]]
        rows.append([act, len(s), len(d), f"{median([f['dmg'] for f in s]):.1f}", f"{median([f['dmg'] for f in d]):.1f}",
                     f"{median([f['blk'] for f in s]):.1f}", f"{median([f['blk'] for f in d]):.1f}",
                     f"{median([f['size'] for f in s]):.0f}", f"{median([f['size'] for f in d]):.0f}"])
    L += ["## Survived against fatal boss fights (medians)", "",
          md_table(["Act", "Survived", "Fatal", "Damage/turn (survived)", "Damage/turn (fatal)", "Block/turn (survived)",
                    "Block/turn (fatal)", "Deck size (survived)", "Deck size (fatal)"], rows), ""]
    # Fatal rate by damage tercile per act
    L += ["## Fatal rate by damage per turn (terciles within each act)", ""]
    for act in (1, 2, 3):
        xs = sorted([f for f in fights if f["act"] == act], key=lambda f: f["dmg"])
        n = len(xs)
        parts = [xs[: n // 3], xs[n // 3: 2 * n // 3], xs[2 * n // 3:]]
        L.append(f"- **Act {act}:** " + " · ".join(
            f"{lab} ({min(p, key=lambda f: f['dmg'])['dmg']:.0f}–{max(p, key=lambda f: f['dmg'])['dmg']:.0f}): "
            f"{sum(f['died'] for f in p)}/{len(p)} fatal ({pct(sum(f['died'] for f in p) / len(p))})"
            for lab, p in zip(("low", "middle", "high"), parts)))
    L.append("")
    L += ["## Fatal rate by block per turn (terciles within each act)", ""]
    for act in (1, 2, 3):
        xs = sorted([f for f in fights if f["act"] == act], key=lambda f: f["blk"])
        n = len(xs)
        parts = [xs[: n // 3], xs[n // 3: 2 * n // 3], xs[2 * n // 3:]]
        L.append(f"- **Act {act}:** " + " · ".join(
            f"{lab} ({min(p, key=lambda f: f['blk'])['blk']:.0f}–{max(p, key=lambda f: f['blk'])['blk']:.0f}): "
            f"{sum(f['died'] for f in p)}/{len(p)} fatal ({pct(sum(f['died'] for f in p) / len(p))})"
            for lab, p in zip(("low", "middle", "high"), parts)))
    L.append("")
    L += ["## Fatal rate by scaling cards in the deck (Powers + Strength cards)", ""]
    for act in (1, 2, 3):
        xs = [f for f in fights if f["act"] == act]
        parts = []
        for lo, hi, lab in ((0, 1, "0"), (1, 2, "1"), (2, 4, "2–3"), (4, 99, "4+")):
            p = [f for f in xs if lo <= f["scaling"] < hi]
            if p:
                parts.append(f"{lab}: {sum(f['died'] for f in p)}/{len(p)} fatal ({pct(sum(f['died'] for f in p) / len(p))})")
        L.append(f"- **Act {act}:** " + " · ".join(parts))
    L.append("")
    iron = [f for f in fights if f["character"] == "IRONCLAD"]
    L += ["## Ironclad only", "",
          md_table(["Act", "Fights", "Fatal", "Damage/turn survived vs fatal", "Block/turn survived vs fatal"],
                   [[a, len(xs), sum(f["died"] for f in xs),
                     f"{median([f['dmg'] for f in xs if not f['died']]) if [f for f in xs if not f['died']] else float('nan'):.1f} vs "
                     f"{median([f['dmg'] for f in xs if f['died']]) if [f for f in xs if f['died']] else float('nan'):.1f}",
                     f"{median([f['blk'] for f in xs if not f['died']]) if [f for f in xs if not f['died']] else float('nan'):.1f} vs "
                     f"{median([f['blk'] for f in xs if f['died']]) if [f for f in xs if f['died']] else float('nan'):.1f}"]
                    for a in (1, 2, 3) for xs in [[f for f in iron if f["act"] == a]] if xs]), "",
          "Starter Ironclad deck for reference: " + f"{simulate(['CARD.STRIKE_IRONCLAD'] * 5 + ['CARD.DEFEND_IRONCLAD'] * 4 + ['CARD.BASH'], 'damage'):.1f} damage/turn, "
          f"{simulate(['CARD.STRIKE_IRONCLAD'] * 5 + ['CARD.DEFEND_IRONCLAD'] * 4 + ['CARD.BASH'], 'block'):.1f} block/turn.", ""]
    elites = [dict(r) for r in con.execute("""
        SELECT f.run_id, f.floor, f.act, f.damage_taken * 1.0 / f.max_hp AS dmgp,
               (f.is_last_floor AND NOT r.win AND NOT r.abandoned) AS died
        FROM floors f JOIN runs r USING(run_id)
        WHERE r.n_players = 1 AND r.build_id = ? AND f.room_type = 'elite' AND f.act IN (1, 2) AND NOT r.abandoned""", [MAIN_BUILD])]
    for f in elites:
        deck = deck_at(con, f["run_id"], f["floor"])
        f["dmg"] = simulate(deck, "damage", sims=150)
        f["blk"] = simulate(deck, "block", sims=150)
    L += ["## Elites (Acts 1–2): the same proxies", ""]
    for act in (1, 2):
        for key, name in (("dmg", "damage"), ("blk", "block")):
            xs = sorted([f for f in elites if f["act"] == act], key=lambda f: f[key])
            n = len(xs)
            parts = [xs[: n // 3], xs[n // 3: 2 * n // 3], xs[2 * n // 3:]]
            L.append(f"- **Act {act}, {name} per turn:** " + " · ".join(
                f"{lab} ({min(p, key=lambda f: f[key])[key]:.0f}–{max(p, key=lambda f: f[key])[key]:.0f}): "
                f"{sum(f['died'] for f in p)}/{len(p)} fatal, median HP lost {pct(median([f['dmgp'] for f in p]))}"
                for lab, p in zip(("low", "middle", "high"), parts)))
    L += ["", "In Act 1, elites go the other way from bosses: the highest raw-damage tercile had the fewest fatal elite "
          "fights. Low block had the most. Act 2 elites show no clear pattern.", ""]
    def terc(act, key):
        xs = sorted([f for f in fights if f["act"] == act], key=lambda f: f[key])
        n = len(xs)
        return [sum(f["died"] for f in p) / len(p) for p in (xs[: n // 3], xs[n // 3: 2 * n // 3], xs[2 * n // 3:])]

    def rate(act, lo, hi):
        p = [f for f in fights if f["act"] == act and lo <= f["scaling"] < hi]
        return sum(f["died"] for f in p) / len(p) if p else float("nan")

    d1, d2, b1, b3 = terc(1, "dmg"), terc(2, "dmg"), terc(1, "blk"), terc(3, "blk")
    i1 = [f for f in iron if f["act"] == 1]
    med = lambda xs, k: median([f[k] for f in xs]) if xs else float("nan")  # noqa: E731
    L += ["## Reading", "",
          "Numbers in this section are computed from the tables above.", "",
          f"- **Raw damage does not protect you at bosses.** Decks in the highest damage tercile died more often than the "
          f"lowest (Act 1: {pct(d1[2])} against {pct(d1[0])}; Act 2: {pct(d2[2])} against {pct(d2[0])}). High raw damage "
          "usually means a deck of attacks with few powers and block, which wins hallways and loses long boss fights.",
          f"- **Block and scaling do.** Act 1: highest block tercile {pct(b1[2])} fatal against {pct(b1[0])} for the lowest; "
          f"Act 3: {pct(b3[2])} against {pct(b3[0])}. Scaling cards: Act 1 decks with 2–3 had {pct(rate(1, 2, 4))} fatal "
          f"against {pct(rate(1, 0, 2))} with 0–1; Act 2 decks with 4+ had {pct(rate(2, 4, 99))} against {pct(rate(2, 1, 2))} with 1.",
          f"- **Ironclad:** fatal Act 1 boss decks had more raw damage ({med([f for f in i1 if f['died']], 'dmg'):.1f} against "
          f"{med([f for f in i1 if not f['died']], 'dmg'):.1f} per turn) and less block ({med([f for f in i1 if f['died']], 'blk'):.1f} "
          f"against {med([f for f in i1 if not f['died']], 'blk'):.1f}).",
          "- Proposed corner targets on arrival at the boss `[HYPOTHESIS H9]`:",
          "  - Act 1: block per turn at least 10, and 2 or more scaling cards",
          "  - Act 2: 4 or more scaling cards",
          "  - Act 3: block per turn at least 8",
          "  Raw damage per turn should not fall below the starter deck's 15 without scaling to replace it.", ""]
    out = PROJECT / "reports/phase2/deck-strength.md"
    out.write_text("\n".join(L))
    print("wrote", out.relative_to(PROJECT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", nargs="*")
    ap.add_argument("--version", default=None, help="card values: v0.107.1 (default for the history report) or v0.111.1 (default for --deck)")
    args = ap.parse_args()
    args.version = args.version or ("v0.111.1" if args.deck else "v0.107.1")
    apply_patches(args.version)
    if args.deck:
        ids = [d if d.startswith("CARD.") else "CARD." + d for d in args.deck]
        print(f"damage/turn {simulate(ids, 'damage'):.1f}  block/turn {simulate(ids, 'block'):.1f}  cards {len(ids)}")
    else:
        report()


if __name__ == "__main__":
    main()
