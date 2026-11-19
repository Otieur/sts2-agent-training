#!/usr/bin/env python3
"""Build a normalised community tier list per character and compare it with the Player's priorities.

Source tiers are transcribed (as data, with attribution) from the pages listed in
knowledge/community/sources.md, accessed 2026-11-19. Card names are matched to the extracted game data.

Outputs (per character):
  knowledge/community/<character>-tiers.md   consensus tier per card with per-source tiers
  knowledge/community/discrepancies.md (Ironclad) or discrepancies-<character>.md
                                             cards where the Player's habit and the consensus differ by 2+ tiers

Usage: python3 -I tools/build_community_tiers.py [--character IRONCLAD|NECROBINDER|ALL]
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import PROJECT, md_table, pct  # noqa: E402

# Spire Codex guide "Ironclad Card Tier List": community-submitted runs, main branch as of mid-July 2026
# (v0.107.x era). Win rate when picked vs average. Partial list (cards the guide names).

def _rows(path):
    """CSV rows from a file that is closed straight away (avoids unclosed handles)."""
    import csv as _csv
    with open(path, newline="") as fh:
        return list(_csv.DictReader(fh))

SPIRE_CODEX = {
    "Offering": "A", "Crimson Mantle": "A", "Impervious": "A", "Fiend Fire": "A",
    "Aggression": "B", "Not Yet": "B", "Mangle": "B", "Tear Asunder": "B", "Thrash": "B", "Pact's End": "B",
    "Break": "D", "Cinder": "D",
}
SPIRE_CODEX_WIN = {"Offering": 52.5, "Crimson Mantle": 52.3, "Impervious": 51.6, "Fiend Fire": 50.5}

# Nat 1 Gaming (DoggertQBones), 2026-11-15, based on the 11/12 beta patch (v0.113.x). Expert opinion.
NAT1 = {}
for tier, names in {
    "S": "Offering, Break, Feed",
    "A": "Crimson Mantle, Dominate, Hellraiser, Corruption, Thrash, Impervious, Unmovable, Tear Asunder, Cascade, "
         "Battle Trance, Fiend Fire, Conflagration, Brand, Demon Form, Pommel Strike, Shrug It Off, Bloodletting, "
         "Stomp, Colossus, Stoke, Stampede",
    "B": "Mangle, Primal Force, Flame Barrier, Pact's End, Dismantle, Bludgeon, Demonic Shield, Armaments, Uppercut, "
         "Expect a Fight, Whirlwind, One-Two Punch, Forgotten Ritual, Headbutt, Rupture, Feel No Pain, Taunt, Inferno, "
         "True Grit, Cruelty, Fight Me, Burning Pact, Howl from Beyond, Pyre",
    "C": "Unrelenting, Body Slam, Not Yet, Juggernaut, Barricade, Anger, Second Wind, Rampage, Inflame, Evil Eye, "
         "Spite, Aggression, Breakthrough, Ashen Strike, Molten Fist, Rage, Perfected Strike, Twin Strike, Setup Strike, "
         "Bully, Infernal Blade, Hemokinesis, Pillage, Vicious, Sword Boomerang, Blood Wall, Stone Armor",
    "D": "Dark Embrace, Tremble, Drum of Battle, Juggling, Tank, Thunderclap, Cinder, Iron Wave, Bash",
    "F": "Havoc",
}.items():
    for n in names.split(", "):
        NAT1[n] = tier

# MetaBot Ironclad tier list page, accessed 2026-11-19: win rate of tracked runs containing the card
# (version not stated; no sample sizes; survivorship-biased). Ironclad-owned cards only.
METABOT_WIN = {
    "Offering": 38.3, "Crimson Mantle": 38.0, "Barricade": 36.5, "Stoke": 35.9, "Cascade": 34.5, "Impervious": 34.3,
    "Dark Embrace": 34.3, "Pyre": 33.6, "Unmovable": 33.3, "Not Yet": 33.2, "Conflagration": 32.6, "Corruption": 32.0,
    "One-Two Punch": 31.3, "Juggernaut": 30.9, "Tear Asunder": 30.9, "Aggression": 30.7, "Demon Form": 30.5,
    "Feel No Pain": 30.0, "Brand": 29.8, "Mangle": 29.8, "Pact's End": 29.6, "Cruelty": 29.5, "Battle Trance": 29.0,
    "Dominate": 28.9, "Feed": 28.6, "Hellraiser": 28.5, "Colossus": 28.3, "Drum of Battle": 28.2, "Burning Pact": 28.1,
    "Bully": 27.8, "Second Wind": 27.8, "Fiend Fire": 27.7, "Juggling": 27.6, "Body Slam": 27.3, "Forgotten Ritual": 27.2,
    "Stone Armor": 27.2, "Rupture": 27.2, "Pillage": 27.1, "Thrash": 26.1, "Bloodletting": 26.0, "Ashen Strike": 25.7,
    "Vicious": 25.6, "Expect a Fight": 25.4, "Break": 25.0, "Flame Barrier": 24.1, "True Grit": 24.0, "Tremble": 24.0,
    "Rage": 23.8, "Shrug It Off": 23.7, "Evil Eye": 23.5, "Havoc": 23.4, "Uppercut": 23.3, "Stampede": 23.3,
    "Unrelenting": 23.3, "Taunt": 23.2, "Inferno": 22.9, "Spite": 22.9, "Molten Fist": 22.8, "Pommel Strike": 22.4,
    "Armaments": 22.3, "Inflame": 22.1, "Howl from Beyond": 22.0, "Sword Boomerang": 21.8, "Anger": 21.8,
    "Blood Wall": 21.7, "Headbutt": 21.6, "Infernal Blade": 21.5, "Thunderclap": 21.4, "Fight Me": 21.3,
    "Primal Force": 21.2, "Dismantle": 20.2, "Hemokinesis": 20.2, "Iron Wave": 20.1, "Whirlwind": 19.9,
    "Twin Strike": 19.2, "Breakthrough": 19.1, "Rampage": 19.1, "Setup Strike": 18.2, "Stomp": 18.0,
    "Perfected Strike": 18.0, "Bludgeon": 17.9, "Cinder": 15.5,
}

# ------------------------------------------------------------------------------------------------ Necrobinder
# Spire Codex guide "Necrobinder Tier List", 2026-07-15, main branch mid-July 2026 (v0.107.x era), community runs.
# Letter tiers as given (Glimpse Beyond: "highest-rated card in the game", Codex Score 100, given S here). Shared Fate,
# Banshee's Cry and Misery have win rates but no letter: placed at A from their win rates (between Legion of Bone,
# 52.7% = A, and Neurosurge, 56.5% = S). Reap and Sow are named as the bottom (~30-33%): D, as for Ironclad's bottom.
NECRO_SPIRE_CODEX = {
    "Glimpse Beyond": "S", "Neurosurge": "S", "Shared Fate": "A", "Banshee's Cry": "A", "Misery": "A",
    "Legion of Bone": "A", "Spirit of Ash": "B", "Seance": "B", "Necro Mastery": "B", "Oblivion": "B", "Reanimate": "B",
    "Reap": "D", "Sow": "D",
}
NECRO_SPIRE_CODEX_WIN = {"Glimpse Beyond": 62.0, "Neurosurge": 56.5, "Shared Fate": 55.4, "Banshee's Cry": 54.9,
                         "Legion of Bone": 52.7, "Misery": 52.6}

# Nat 1 Gaming (DoggertQBones), Necrobinder card tier list, 2026-11-15, 11/12 beta patch (no Necrobinder card changes
# in that patch per the article). Expert opinion.
NECRO_NAT1 = {}
for tier, names in {
    "S": "Neurosurge, Friendship",
    "A": "Call of the Void, Glimpse Beyond, Hang, Eradicate, Borrowed Time, Transfigure, No Escape, Banshees Cry, "
         "End of Days, Spirit of Ash, Undeath, Reanimate, Squeeze, Dirge, The Scythe, Deathbringer, Fetch, Defy, Bone Shards",
    "B": "Demesne, Enfeebling Touch, Countdown, Sleight of Flesh, Seance, Protector, High Five, Lethality, Capture Spirit, "
         "Oblivion, Grave Warden, Necro Mastery, Calcify, Misery, Flatten, Deaths Door, Debilitate, Negative Pulse, "
         "Pagestorm, Times Up, Scourge, Rattle, Veilpiercer, Melancholy, Soul Storm, Reaper Form, Forbidden Grimoire, "
         "Shared Fate, Dredge, Shroud, Snap, Unleash, Invoke",
    "C": "Reap, Haunt, Sentry Mode, Spur, Sow, Sculpting Strike, Death March, Severance, Devour Life, Defile, Pull Aggro, "
         "Putrefy, Legion of Bone, Right Hand Hand, Graveblast, Blight Strike, Fear, Reave, Drain Power, Bodyguard, Poke, "
         "Delay, Sacrifice, Pull from Below, Afterlife, Cleanse",
    "D": "Parse, Wisp, Sic Em, Bury, Danse Macabre",
    "F": "Eidolon",
}.items():
    for n in names.split(", "):
        NECRO_NAT1[n] = tier

# MetaBot Necrobinder tier list page, accessed 2026-11-19 (period "November 2026"; version and sample sizes not
# stated; survivorship-biased). Necrobinder-owned cards only; the page also lists colorless and other cards.
NECRO_METABOT_WIN = {
    "Legion of Bone": 48.1, "Glimpse Beyond": 46.8, "Neurosurge": 43.7, "Demesne": 40.2, "Shared Fate": 39.5,
    "Banshee's Cry": 38.1, "Transfigure": 37.0, "Spirit of Ash": 36.8, "Eradicate": 36.8, "Oblivion": 36.3,
    "Debilitate": 35.2, "Pagestorm": 33.7, "Seance": 33.1, "Call of the Void": 33.1, "Enfeebling Touch": 32.9,
    "Pull from Below": 32.6, "Danse Macabre": 32.0, "Friendship": 31.8, "Time's Up": 31.6, "Parse": 31.5,
    "Reanimate": 31.4, "Undeath": 31.2, "Squeeze": 30.9, "Dredge": 30.9, "Necro Mastery": 30.4, "Hang": 30.4,
    "Misery": 30.2, "Putrefy": 30.0, "Sleight of Flesh": 29.9, "Rattle": 29.7, "Lethality": 29.7, "Borrowed Time": 29.5,
    "Reaper Form": 29.4, "Eidolon": 29.4, "Dirge": 29.1, "Bury": 29.1, "Devour Life": 28.8, "End of Days": 28.5,
    "Delay": 28.4, "Sentry Mode": 28.4, "Shroud": 28.1, "Graveblast": 27.9, "Death March": 27.9, "Defy": 27.7,
    "Haunt": 27.5, "The Scythe": 27.4, "Forbidden Grimoire": 27.4, "Death's Door": 27.3, "High Five": 27.1, "Spur": 26.9,
    "Countdown": 26.9, "Capture Spirit": 26.7, "Cleanse": 26.6, "Fetch": 26.4, "No Escape": 26.2, "Soul Storm": 25.8,
    "Right Hand Hand": 25.6, "Invoke": 25.4, "Deathbringer": 25.2, "Wisp": 24.9, "Fear": 24.5, "Severance": 24.5,
    "Veilpiercer": 24.1, "Calcify": 24.1, "Snap": 24.0, "Grave Warden": 23.8, "Sacrifice": 23.6, "Sic 'Em": 23.1,
    "Sculpting Strike": 23.1, "Afterlife": 22.8, "Bone Shards": 22.6, "Melancholy": 22.5, "Protector": 22.2,
    "Scourge": 21.2, "Poke": 21.1, "Flatten": 20.9, "Negative Pulse": 20.6, "Pull Aggro": 20.6, "Defile": 19.9,
    "Drain Power": 19.3, "Reave": 18.8, "Reap": 18.6, "Blight Strike": 17.1, "Sow": 16.8,
}

CHARS = {
    "IRONCLAD": {"owner": "Ironclad", "spire_codex": SPIRE_CODEX, "spire_codex_win": SPIRE_CODEX_WIN, "nat1": NAT1,
                 "metabot": METABOT_WIN, "nat1_version": "11/12 beta patch (v0.113.x), **not our version**",
                 "metabot_version": "Not stated", "codex_note": "partial list",
                 "disc_file": "discrepancies.md"},
    "NECROBINDER": {"owner": "Necrobinder", "spire_codex": NECRO_SPIRE_CODEX, "spire_codex_win": NECRO_SPIRE_CODEX_WIN,
                    "nat1": NECRO_NAT1, "metabot": NECRO_METABOT_WIN,
                    "nat1_version": "11/12 beta patch (v0.113.x; no Necrobinder card changes in that patch), **not our version**",
                    "metabot_version": "Period \"November 2026\"; version not stated",
                    "codex_note": "partial list; three letters derived from win rates",
                    "disc_file": "discrepancies-necrobinder.md"},
}

TIER_SCORE = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
WEIGHTS = {"spire_codex": 2.0, "metabot": 1.0, "nat1": 1.0}


def norm(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def quintile_scores(values):
    """Map a dict name->value to a 0.5..4.5 score by quintile (higher value = higher score)."""
    items = sorted(values.items(), key=lambda kv: kv[1])
    n = len(items)
    # Equal-sized buckets: bucket = floor(5 * rank / n), 0..4. (Before 2026-11-19 01:30 the top bucket absorbed the
    # remainder, e.g. 20 of 84 cards instead of 17.)
    return {k: 0.5 + min(4, (5 * i) // max(1, n)) for i, (k, _) in enumerate(items)}


def tier_of(score):
    if score >= 4.25:
        return "S"
    if score >= 3.5:
        return "A"
    if score >= 2.75:
        return "B"
    if score >= 2.0:
        return "C"
    return "D"


def build(character):
    cfg = CHARS[character]
    SPIRE_CODEX, SPIRE_CODEX_WIN, NAT1, METABOT_WIN = cfg["spire_codex"], cfg["spire_codex_win"], cfg["nat1"], cfg["metabot"]
    title, low = character.title(), character.lower()
    cards = json.loads((PROJECT / "knowledge/data/extract-2026-09-21/cards.json").read_text())
    iron = {norm(re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", c["name"])): c for c in cards if c["owner"] == cfg["owner"]}
    display = {k: re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", c["name"]) for k, c in iron.items()}
    # Prefer a source's spelling (keeps apostrophes, hyphens and lower-case "of"/"the"), most punctuated first.
    def punct(n):
        return (sum(1 for ch in n if not ch.isalnum() and ch != " "), sum(1 for w in n.split()[1:] if w[:1].islower()))
    for src in (NAT1, SPIRE_CODEX, METABOT_WIN):
        for n in src:
            k = norm(n)
            if k in display and punct(n) > punct(display[k]):
                display[k] = n

    unmatched = sorted({n for src in (SPIRE_CODEX, NAT1, METABOT_WIN) for n in src if norm(n) not in iron})
    mb = quintile_scores({norm(k): v for k, v in METABOT_WIN.items() if norm(k) in iron})

    # Player: Bradley-Terry strength quintiles among cards with 10+ comparisons
    player, player_n, picks = {}, {}, {}
    for r in _rows(PROJECT / f"reports/phase1/card-ranking-{low}.csv"):
        if r["card"] != "SKIP" and int(r["comparisons"]) >= 10:
            player[norm(r["card"].replace("_", " "))] = float(r["strength"])
            player_n[norm(r["card"].replace("_", " "))] = int(r["comparisons"])
    for r in _rows(PROJECT / f"reports/phase1/card-picks-{low}.csv"):
        picks[norm(r["card"].replace("_", " "))] = (int(r["picked"]), int(r["offered"]))
    pq = quintile_scores(player)

    rows = []
    for k, c in iron.items():
        if c["rarity"] == "Basic":
            continue
        parts, wsum, ssum = {}, 0.0, 0.0
        sc = next((t for n, t in SPIRE_CODEX.items() if norm(n) == k), None)
        n1 = next((t for n, t in NAT1.items() if norm(n) == k), None)
        if sc:
            parts["Spire Codex"] = sc
            ssum += WEIGHTS["spire_codex"] * TIER_SCORE[sc]
            wsum += WEIGHTS["spire_codex"]
        if k in mb:
            parts["MetaBot"] = tier_of(mb[k])
            ssum += WEIGHTS["metabot"] * mb[k]
            wsum += WEIGHTS["metabot"]
        if n1:
            parts["Nat1 (beta)"] = n1
            ssum += WEIGHTS["nat1"] * TIER_SCORE[n1]
            wsum += WEIGHTS["nat1"]
        if not wsum:
            continue
        score = ssum / wsum
        src_scores = [TIER_SCORE[v] if v in TIER_SCORE else 0 for v in parts.values()]
        spread = max(src_scores) - min(src_scores) if len(src_scores) > 1 else 0
        ptier = tier_of(pq[k]) if k in pq else None
        pk, off = picks.get(k, (0, 0))
        rows.append({"key": k, "card": display[k], "rarity": c["rarity"], "type": c["type"], "tags": c["tags"],
                     "score": score, "tier": tier_of(score), "parts": parts, "n_sources": len(parts), "spread": spread,
                     "player_tier": ptier, "player_strength": player.get(k), "player_n": player_n.get(k, 0),
                     "picked": pk, "offered": off})
    rows.sort(key=lambda r: -r["score"])

    out = PROJECT / "knowledge/community"
    out.mkdir(parents=True, exist_ok=True)
    L = [f"# {title} Community Tiers (normalised)", "",
         "Built by `tools/build_community_tiers.py` on 2026-11-19. Label: `[COMMUNITY]`. Sources and their versions are "
         "in `sources.md`.", "",
         "| Source | Kind | Version | Weight |", "|---|---|---|---|",
         f"| Spire Codex guide | Win rate when picked, community-submitted runs; {cfg['codex_note']} | Main branch, mid-July 2026 (v0.107.x era) | 2 |",
         f"| MetaBot | Win rate of tracked runs containing the card (survivorship-biased, no sample sizes); converted to quintiles | {cfg['metabot_version']} | 1 |",
         f"| Nat 1 Gaming | Expert opinion | {cfg['nat1_version']} | 1 |", "",
         "Consensus = weighted mean of tier scores (S=5 … F=0; MetaBot quintiles 0.5–4.5), mapped back: S ≥ 4.25, A ≥ 3.5, "
         "B ≥ 2.75, C ≥ 2.0, D below. **Spread** is the gap in tiers between the most and least favourable source; 2 or more "
         "means the sources disagree. The Player column is the quintile of the Player's own head-to-head score (habit, "
         "cards with 10+ comparisons).", "",
         md_table(["Card", "Rarity", "Consensus", "Score", "Spire Codex", "MetaBot", "Nat1 (beta)", "Spread", "Player habit", "Player picked"],
                  [[r["card"], r["rarity"], f"**{r['tier']}**", f"{r['score']:.2f}", r["parts"].get("Spire Codex", "-"),
                    r["parts"].get("MetaBot", "-"), r["parts"].get("Nat1 (beta)", "-"),
                    r["spread"] if r["n_sources"] > 1 else "-", r["player_tier"] or "-",
                    f"{r['picked']}/{r['offered']}" if r["offered"] else "-"] for r in rows]), "",
         "Spire Codex win rates when picked (main branch, mid-July 2026): " +
         ", ".join(f"{k} {v}%" for k, v in SPIRE_CODEX_WIN.items()) + ".", "",
         f"Names in sources that are not {title} cards in the extracted game data (ignored): {', '.join(unmatched) or 'none'}.", ""]
    (out / f"{low}-tiers.md").write_text("\n".join(L))

    disc = [r for r in rows if r["player_tier"] and abs(TIER_SCORE[r["tier"]] - TIER_SCORE[r["player_tier"]]) >= 2]
    disc.sort(key=lambda r: -abs(TIER_SCORE[r["tier"]] - TIER_SCORE[r["player_tier"]]))
    D = [f"# Discrepancies: Player Habit against Community Consensus ({title})", "",
         "Cards whose consensus tier and the Player's habit tier differ by 2 or more tiers. Built by "
         "`tools/build_community_tiers.py`. Neither side is right by default (see `docs/README.md` precedence): these are "
         "questions for Phase 4 experiments. Roles come from the extracted game data.", "",
         md_table(["Card", "Roles", "Consensus", "Player habit", "Player picked", "Player score (n)", "Direction"],
                  [[r["card"], ", ".join(t for t in r["tags"] if not t.startswith("kw-")), r["tier"], r["player_tier"],
                    f"{r['picked']}/{r['offered']}", f"{r['player_strength']:+.2f} ({r['player_n']})",
                    "Player rates higher" if TIER_SCORE[r["player_tier"]] > TIER_SCORE[r["tier"]] else "Player rates lower"]
                   for r in disc]), ""]
    (out / cfg["disc_file"]).write_text("\n".join(D))
    print(f"{title}: {len(rows)} cards tiered; {len(disc)} discrepancies; unmatched names: {unmatched}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", default="ALL", choices=["ALL", *CHARS])
    args = ap.parse_args()
    for ch in (CHARS if args.character == "ALL" else [args.character]):
        build(ch)


if __name__ == "__main__":
    main()
