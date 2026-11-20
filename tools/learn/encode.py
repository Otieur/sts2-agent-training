#!/usr/bin/env python3
"""Observation encoder for the learned models (P9.E1.S1): one module for training and live play (ML-1).

Input: a combat observation in the format of `docs/observation-spec.md` (the simulator's `obs`), or a live API state
converted with `from_live`. Output: plain Python lists (no numerical library needed), turned into tensors by
`tools/learn/model.py`. Only fields a player can see are read (FP-1, FP-10); the encoder never looks at seeds,
generator state, draw order or future intents, and the observation has none of them.

Layout of one encoding (`ENCODER_VERSION` enc-v1):
- `glob`: fixed-length floats named in `GLOBAL_FIELDS` (scaled; `decode_global` inverts the scaling).
- `hand_ids`, `hand_feats`: card index and per-card floats (`HAND_FEATS`) in hand order.
- `draw_ids`/`draw_upg`, `discard_ids`/`discard_upg`, `exhaust_ids`/`exhaust_upg`: pile contents as sets
  (the observation sorts them; order carries no information).
- `ppow_ids`, `ppow_amt`: the player's powers with (scaled amount, signed log amount).
- `enemy_ids`, `enemy_feats`: one row per enemy slot (`ENEMY_FEATS`), dead ones included with `alive` = 0.
- `epow_ids`, `epow_amt`, `epow_owner`: enemy powers, with the position of their enemy in `enemy_ids`.
- `relic_ids`, `potion_ids`: held relics and occupied potion slots.
- `choice_ids`, `choice_upg`: the cards offered by a pending card choice (empty when none).
- `mates`: one row per teammate (`MATE_FEATS`); empty in solo play. Reserved for co-op (Phase 6), so a co-op
  observation encodes without a format change.

Indexes come from `knowledge/data/vocab-<version>.json` (`tools/learn/vocab.py`): 0 = padding, 1 = unknown id.
"""
import json
import math
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
ENCODER_VERSION = "enc-v1.1"   # same layout as enc-v1; HP above UNKILLABLE_HP is clipped and left out of totals
DEFAULT_VOCAB = PROJECT / "knowledge" / "data" / "vocab-v0.111.1.json"

# Caps: anything beyond is dropped (counts stay exact in `glob`).
MAX_HAND, MAX_PILE, MAX_ENEMIES, MAX_POWERS, MAX_RELICS, MAX_POTIONS, MAX_CHOICE, MAX_MATES = 12, 80, 6, 16, 48, 6, 24, 3

DYN_NAMES = ["Damage", "Block", "Repeat", "Cards", "Energy", "HpLoss", "VulnerablePower", "StrengthPower", "WeakPower",
             "CalculatedDamage", "CalculatedHits", "ExtraDamage"]
HAND_FEATS = (["upgraded", "cost", "cost_unplayable", "playable", "damage_bonus", "block_bonus"]
              + [f"dyn_{n}" for n in DYN_NAMES] + ["target_" + t for t in ("None", "Self", "AnyEnemy", "AllEnemies", "RandomEnemy", "Other")])
ENEMY_FEATS = (["hp", "max_hp", "hp_frac", "block", "alive", "hittable", "slot", "attack_total", "attack_hits", "attack_single"]
               + ["intent_" + t for t in ("Attack", "Buff", "Debuff", "DebuffStrong", "Defend", "Escape", "Heal", "Hidden", "Summon",
                                          "Sleep", "Stun", "StatusCard", "CardDebuff", "DeathBlow", "Unknown", "Other")])
MATE_FEATS = ["hp", "max_hp", "block", "energy", "alive"]

HP_SCALE, BLOCK_SCALE, DMG_SCALE = 100.0, 50.0, 50.0
# An enemy HP above this is a placeholder for a phase won by surviving, not by damage (the Waterfall Giant's HP becomes
# about 10^9); it is clipped to HP_CLIP in the features and left out of the enemy HP total (enc-v1.1).
UNKILLABLE_HP, HP_CLIP = 10_000, 3_000


def _player(o):
    return (o.get("combat") or {}).get("player") or {}


def _enemies(o):
    return (o.get("combat") or {}).get("enemies") or []


def _alive(e):
    return e.get("is_alive", True) and (e.get("current_hp") or 0) > 0


def _incoming(o):
    total = 0
    for e in _enemies(o):
        if _alive(e):
            for i in e.get("intents") or []:
                if i.get("intent_type") == "Attack":
                    total += i.get("total_damage") or (i.get("damage") or 0) * (i.get("hits") or 1)
    return total


def _count(o, pile):
    c = o.get("combat") or {}
    n = c.get(pile + "_count")
    return n if n is not None else len(c.get(pile) or [])


# (name, getter, scale): glob[i] = getter(obs) / scale; decode multiplies back.
GLOBAL_FIELDS = [
    ("turn", lambda o: o.get("turn") or 0, 10.0),
    ("hp", lambda o: _player(o).get("current_hp") or 0, HP_SCALE),
    ("max_hp", lambda o: _player(o).get("max_hp") or 0, HP_SCALE),
    ("hp_frac", lambda o: (_player(o).get("current_hp") or 0) / max(_player(o).get("max_hp") or 1, 1), 1.0),
    ("block", lambda o: _player(o).get("block") or 0, BLOCK_SCALE),
    ("energy", lambda o: _player(o).get("energy") or 0, 5.0),
    ("ascension", lambda o: (o.get("run") or {}).get("ascension") or 0, 10.0),
    ("hand_count", lambda o: len((o.get("combat") or {}).get("hand") or []), 10.0),
    ("draw_count", lambda o: _count(o, "draw_pile"), 40.0),
    ("discard_count", lambda o: _count(o, "discard_pile"), 40.0),
    ("exhaust_count", lambda o: _count(o, "exhaust_pile"), 40.0),
    ("piles_known", lambda o: 1.0 if (o.get("combat") or {}).get("draw_pile") is not None else 0.0, 1.0),
    ("enemies_alive", lambda o: sum(1 for e in _enemies(o) if _alive(e)), 5.0),
    ("enemy_hp_total", lambda o: sum(e.get("current_hp") or 0 for e in _enemies(o) if _alive(e) and (e.get("current_hp") or 0) <= UNKILLABLE_HP), 300.0),
    ("enemy_block_total", lambda o: sum(e.get("block") or 0 for e in _enemies(o) if _alive(e)), BLOCK_SCALE),
    ("incoming", _incoming, DMG_SCALE),
    ("incoming_unblocked", lambda o: max(0, _incoming(o) - (_player(o).get("block") or 0)), DMG_SCALE),
    ("potions_held", lambda o: sum(1 for p in (o.get("run") or {}).get("potions") or [] if p.get("occupied")), 3.0),
    ("potion_slots", lambda o: len((o.get("run") or {}).get("potions") or []), 3.0),
    ("relic_count", lambda o: len((o.get("run") or {}).get("relics") or []), 20.0),
    ("choice_pending", lambda o: 1.0 if o.get("choice") else 0.0, 1.0),
    ("choice_min", lambda o: (o.get("choice") or {}).get("min") or 0, 3.0),
    ("choice_max", lambda o: (o.get("choice") or {}).get("max") or 0, 3.0),
    ("players", lambda o: o.get("players") or 1, 4.0),
]


def _amount_feats(a):
    a = a or 0
    return [max(-3.0, min(3.0, a / 10.0)), math.copysign(math.log1p(abs(a)), a) / 3.0]


class Encoder:
    def __init__(self, vocab_path=DEFAULT_VOCAB):
        doc = json.loads(Path(vocab_path).read_text())
        self.about = doc["about"]
        self.vocab = {k: v for k, v in doc.items() if k != "about"}
        self.index = {k: {name: i for i, name in enumerate(v)} for k, v in self.vocab.items()}
        self.unknown = {}

    def sizes(self):
        return {k: len(v) for k, v in self.vocab.items()}

    def idx(self, kind, name):
        i = self.index[kind].get(name)
        if i is None:
            self.unknown[(kind, name)] = self.unknown.get((kind, name), 0) + 1
            return 1
        return i

    def _pile(self, names):
        names = (names or [])[:MAX_PILE]
        return [self.idx("cards", n.rstrip("+")) for n in names], [1.0 if n.endswith("+") else 0.0 for n in names]

    def _card(self, h):
        dyn = {v.get("name"): v for v in h.get("dynamic_values") or []}
        cost = h.get("energy_cost")
        cost = -1 if cost is None else cost

        def cur(n):
            return float((dyn.get(n) or {}).get("current_value") or 0)

        def bonus(n):
            v = dyn.get(n)
            return float((v.get("current_value") or 0) - (v.get("base_value") or 0)) if v else 0.0

        tt = h.get("target_type") or "None"
        tts = ["None", "Self", "AnyEnemy", "AllEnemies", "RandomEnemy"]
        return ([1.0 if h.get("upgraded") else 0.0, max(cost, 0) / 3.0, 1.0 if cost < 0 else 0.0, 1.0 if h.get("playable", True) else 0.0,
                 bonus("Damage") / 10.0, bonus("Block") / 10.0]
                + [cur(n) / 20.0 for n in DYN_NAMES]
                + [1.0 if tt == t else 0.0 for t in tts] + [0.0 if tt in tts else 1.0])

    def _enemy(self, e, slot):
        intents = e.get("intents") or []
        attack_total = sum(i.get("total_damage") or (i.get("damage") or 0) * (i.get("hits") or 1) for i in intents if i.get("intent_type") == "Attack")
        hits = sum(i.get("hits") or 1 for i in intents if i.get("intent_type") == "Attack")
        single = max([i.get("damage") or 0 for i in intents if i.get("intent_type") == "Attack"] or [0])
        kinds = ENEMY_FEATS[10:-1]
        types = {i.get("intent_type") for i in intents}
        hp, mx = min(e.get("current_hp") or 0, HP_CLIP), min(e.get("max_hp") or 1, HP_CLIP)
        return ([hp / HP_SCALE, mx / HP_SCALE, hp / max(mx, 1), (e.get("block") or 0) / BLOCK_SCALE, 1.0 if _alive(e) else 0.0,
                 1.0 if e.get("is_hittable", True) else 0.0, slot / 5.0, attack_total / DMG_SCALE, hits / 5.0, single / DMG_SCALE]
                + [1.0 if k[len("intent_"):] in types else 0.0 for k in kinds]
                + [1.0 if types - {k[len("intent_"):] for k in kinds} - {None} else 0.0])

    def encode(self, obs):
        c = obs.get("combat") or {}
        run = obs.get("run") or {}
        player = c.get("player") or {}
        enc = {"glob": [float(get(obs)) / scale for _, get, scale in GLOBAL_FIELDS]}
        hand = (c.get("hand") or [])[:MAX_HAND]
        enc["hand_ids"] = [self.idx("cards", h.get("card_id")) for h in hand]
        enc["hand_feats"] = [self._card(h) for h in hand]
        for pile in ("draw", "discard", "exhaust"):
            enc[pile + "_ids"], enc[pile + "_upg"] = self._pile(c.get(pile + "_pile"))
        pp = (player.get("powers") or [])[:MAX_POWERS]
        enc["ppow_ids"] = [self.idx("powers", p.get("power_id")) for p in pp]
        enc["ppow_amt"] = [_amount_feats(p.get("amount")) for p in pp]
        enemies = _enemies(obs)[:MAX_ENEMIES]
        enc["enemy_ids"] = [self.idx("monsters", e.get("enemy_id")) for e in enemies]
        enc["enemy_feats"] = [self._enemy(e, i) for i, e in enumerate(enemies)]
        enc["epow_ids"], enc["epow_amt"], enc["epow_owner"] = [], [], []
        for i, e in enumerate(enemies):
            for p in (e.get("powers") or [])[:MAX_POWERS]:
                enc["epow_ids"].append(self.idx("powers", p.get("power_id")))
                enc["epow_amt"].append(_amount_feats(p.get("amount")))
                enc["epow_owner"].append(i)
        enc["relic_ids"] = [self.idx("relics", r.get("relic_id")) for r in (run.get("relics") or [])[:MAX_RELICS]]
        enc["potion_ids"] = [self.idx("potions", p.get("potion_id")) for p in (run.get("potions") or [])[:MAX_POTIONS] if p.get("occupied")]
        choice = obs.get("choice") or {}
        opts = [o if isinstance(o, str) else (o.get("card_id") or "") for o in (choice.get("options") or [])[:MAX_CHOICE]]
        enc["choice_ids"], enc["choice_upg"] = self._pile(opts)
        enc["mates"] = [[(m.get("current_hp") or 0) / HP_SCALE, (m.get("max_hp") or 0) / HP_SCALE, (m.get("block") or 0) / BLOCK_SCALE,
                         (m.get("energy") or 0) / 5.0, 1.0 if m.get("is_alive", True) else 0.0]
                        for m in (c.get("teammates") or [])[:MAX_MATES]]
        return enc


def decode_global(glob):
    """Scaled global floats back to named values (round-trip check of the numeric fields)."""
    return {name: v * scale for (name, _, scale), v in zip(GLOBAL_FIELDS, glob)}


def from_live(state):
    """A live API state (STS2-Agent) in the observation-spec format. The live state does not list pile contents
    (only counts in some versions), so piles stay unknown (`piles_known` = 0); teammates come from `combat.players`."""
    c = state.get("combat") or {}
    run = state.get("run") or {}
    players = c.get("players") or []
    local = next((p for p in players if p.get("is_local")), None)
    p = dict(c.get("player") or {})
    if local:
        p.setdefault("current_hp", local.get("current_hp"))
        p.setdefault("max_hp", local.get("max_hp"))
    combat = {"player": p, "hand": c.get("hand") or [], "enemies": c.get("enemies") or [],
              "draw_pile": None, "discard_pile": None, "exhaust_pile": None,
              "draw_pile_count": p.get("draw_pile_count"), "discard_pile_count": p.get("discard_pile_count"),
              "exhaust_pile_count": p.get("exhaust_pile_count"),
              "teammates": [m for m in players if not m.get("is_local")]}
    return {"status": "in_progress" if state.get("in_combat", True) else "unknown", "turn": state.get("turn"),
            "players": max(len(players), 1), "player_index": next((i for i, m in enumerate(players) if m.get("is_local")), 0),
            "run": {"ascension": run.get("ascension"), "max_hp": run.get("max_hp"), "current_hp": run.get("current_hp"),
                    "relics": run.get("relics") or [], "potions": run.get("potions") or []},
            "combat": combat, "choice": None}
