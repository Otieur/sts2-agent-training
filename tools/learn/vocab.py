#!/usr/bin/env python3
"""Vocabularies for the learned models (P9.E1.S1), built from the installed game's model database.

The game names every card, relic, power, potion and monster by its class name turned into upper snake case
(`BurningBlood` -> `BURNING_BLOOD`, `PlatingPower` -> `PLATING_POWER`); the same ids appear in the observation. This
script reads the class list from the assembly index (`data/asm/sts2-index.txt`, written by `tools/asm`) and the enum
values the observation uses (intent types, target types, card types), and writes one JSON file per game version:

    python3 -I tools/learn/vocab.py            # writes knowledge/data/vocab-<version>.json

Index 0 is padding and index 1 is "unknown" in every list, so ids added by a later patch still encode (they share the
unknown entry until the vocabulary is rebuilt and the models retrained, P9.E7.S1). Lists are sorted, so a rebuild on
the same game version gives the same indexes.
"""
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
INDEX = PROJECT / "data" / "asm" / "sts2-index.txt"
OUT_DIR = PROJECT / "knowledge" / "data"
RELEASE = Path.home() / "Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app/Contents/Resources/release_info.json"

PAD, UNK = "<pad>", "<unk>"
MODEL_KINDS = {"cards": "CardModel", "relics": "RelicModel", "powers": "PowerModel", "potions": "PotionModel", "monsters": "MonsterModel"}
ENUMS = {"intent_types": "MegaCrit.Sts2.Core.MonsterMoves.Intents.IntentType", "target_types": "MegaCrit.Sts2.Core.Entities.Cards.TargetType",
         "card_types": "MegaCrit.Sts2.Core.Entities.Cards.CardType"}


def slug(name):
    """Class name to the game's id form (checked against all 596 card ids of v0.111.1)."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).upper()


def build(index_lines):
    """Concrete classes deriving (directly or through intermediate classes) from each model base."""
    parent, flags = {}, {}
    for line in index_lines:
        m = re.match(r"^T ([A-Za-z0-9_.`<>]+) : ([A-Za-z0-9_.`<>]+) \[([^\]]*)\]", line)
        if m:
            parent[m.group(1)], flags[m.group(1)] = m.group(2), m.group(3)

    def derives(name, base):
        seen = 0
        while name in parent and seen < 50:
            name, seen = parent[name], seen + 1
            if name == base:
                return True
        return False

    vocab = {}
    for key, base in MODEL_KINDS.items():
        full = "MegaCrit.Sts2.Core.Models." + base
        ids = {slug(t.rsplit(".", 1)[-1]) for t in parent
               if "Abstract" not in flags[t] and "+" not in t and not t.rsplit(".", 1)[-1].startswith("Mock") and derives(t, full)}
        vocab[key] = [PAD, UNK] + sorted(ids)
    for key, enum in ENUMS.items():
        pat = re.compile(r"^  F " + re.escape(enum) + r"::([A-Za-z]+) = (\d+) ")
        vals = sorted(((int(m.group(2)), m.group(1)) for m in map(pat.match, index_lines) if m))
        vocab[key] = [PAD, UNK] + [name for _, name in vals]
    return vocab


def main(argv=None):
    if not INDEX.exists():
        print(f"missing {INDEX.relative_to(PROJECT)}: run tools/asm first", file=sys.stderr)
        return 1
    build_info = json.loads(RELEASE.read_text()) if RELEASE.exists() else {}
    vocab = build(INDEX.read_text().splitlines())
    version = build_info.get("version", "unknown")
    out = OUT_DIR / f"vocab-{version}.json"
    doc = {"about": {"game_version": version, "game_commit": build_info.get("commit"), "source": "data/asm/sts2-index.txt (tools/learn/vocab.py)",
                     "rule": "index 0 = padding, 1 = unknown id; lists sorted", "sizes": {k: len(v) for k, v in vocab.items()}}} | vocab
    out.write_text(json.dumps(doc, indent=0))
    print(json.dumps(doc["about"], indent=1))
    print(f"wrote {out.relative_to(PROJECT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
