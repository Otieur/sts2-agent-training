#!/usr/bin/env python3
"""Build a normalised community tier list for Ironclad and compare it with the Player's priorities.

Source tiers are transcribed (as data, with attribution) from the pages listed in
knowledge/community/sources.md, accessed 2026-11-19. Card names are matched to the extracted game data.

Outputs:
  knowledge/community/ironclad-tiers.md   consensus tier per card with per-source tiers
  knowledge/community/discrepancies.md    cards where the Player's habit and the consensus differ by 2+ tiers

Usage: python3 -I tools/build_community_tiers.py
"""
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stslib import PROJECT, md_table, pct  # noqa: E402

# Spire Codex guide "Ironclad Card Tier List": community-submitted runs, main branch as of mid-July 2026
# (v0.107.x era). Win rate when picked vs average. Partial list (cards the guide names).
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

TIER_SCORE = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
WEIGHTS = {"spire_codex": 2.0, "metabot": 1.0, "nat1": 1.0}


def norm(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def quintile_scores(values):
    """Map a dict name->value to a 0.5..4.5 score by quintile (higher value = higher score)."""
    items = sorted(values.items(), key=lambda kv: kv[1])
    n = len(items)
    return {k: 0.5 + 4 * (i // max(1, n // 5) if i // max(1, n // 5) < 5 else 4) / 4 for i, (k, _) in enumerate(items)}


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


def main():
    cards = json.loads((PROJECT / "knowledge/data/extract-2026-09-21/cards.json").read_text())
    iron = {norm(re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", c["name"])): c for c in cards if c["owner"] == "Ironclad"}
    display = {k: re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", c["name"]) for k, c in iron.items()}

    unmatched = sorted({n for src in (SPIRE_CODEX, NAT1, METABOT_WIN) for n in src if norm(n) not in iron})
    mb = quintile_scores({norm(k): v for k, v in METABOT_WIN.items() if norm(k) in iron})

    # Player: Bradley-Terry strength quintiles among cards with 10+ comparisons
    player, player_n, picks = {}, {}, {}
    for r in csv.DictReader(open(PROJECT / "reports/phase1/card-ranking-ironclad.csv")):
        if r["card"] != "SKIP" and int(r["comparisons"]) >= 10:
            player[norm(r["card"].replace("_", " "))] = float(r["strength"])
            player_n[norm(r["card"].replace("_", " "))] = int(r["comparisons"])
    for r in csv.DictReader(open(PROJECT / "reports/phase1/card-picks-ironclad.csv")):
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
    L = ["# Ironclad Community Tiers (normalised)", "",
         "Built by `tools/build_community_tiers.py` on 2026-11-19. Label: `[COMMUNITY]`. Sources and their versions are "
         "in `sources.md`.", "",
         "| Source | Kind | Version | Weight |", "|---|---|---|---|",
         "| Spire Codex guide | Win rate when picked, community-submitted runs; partial list | Main branch, mid-July 2026 (v0.107.x era) | 2 |",
         "| MetaBot | Win rate of tracked runs containing the card (survivorship-biased, no sample sizes); converted to quintiles | Not stated | 1 |",
         "| Nat 1 Gaming | Expert opinion | 11/12 beta patch (v0.113.x), **not our version** | 1 |", "",
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
         f"Names in sources that are not Ironclad cards in the extracted game data (ignored): {', '.join(unmatched) or 'none'}.", ""]
    (out / "ironclad-tiers.md").write_text("\n".join(L))

    disc = [r for r in rows if r["player_tier"] and abs(TIER_SCORE[r["tier"]] - TIER_SCORE[r["player_tier"]]) >= 2]
    disc.sort(key=lambda r: -abs(TIER_SCORE[r["tier"]] - TIER_SCORE[r["player_tier"]]))
    D = ["# Discrepancies: Player Habit against Community Consensus (Ironclad)", "",
         "Cards whose consensus tier and the Player's habit tier differ by 2 or more tiers. Built by "
         "`tools/build_community_tiers.py`. Neither side is right by default (see `docs/README.md` precedence): these are "
         "questions for Phase 4 experiments. Roles come from the extracted game data.", "",
         md_table(["Card", "Roles", "Consensus", "Player habit", "Player picked", "Player score (n)", "Direction"],
                  [[r["card"], ", ".join(t for t in r["tags"] if not t.startswith("kw-")), r["tier"], r["player_tier"],
                    f"{r['picked']}/{r['offered']}", f"{r['player_strength']:+.2f} ({r['player_n']})",
                    "Player rates higher" if TIER_SCORE[r["player_tier"]] > TIER_SCORE[r["tier"]] else "Player rates lower"]
                   for r in disc]), ""]
    (out / "discrepancies.md").write_text("\n".join(D))
    print(f"{len(rows)} cards tiered; {len(disc)} discrepancies; unmatched names: {unmatched}")


if __name__ == "__main__":
    main()
