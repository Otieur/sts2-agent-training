#!/usr/bin/env python3
"""Turn planner (P4.E2.S2): search the hand for the best set of plays this turn, with exact arithmetic.

It enumerates every affordable subset of the hand (and, for single-target cards, every target assignment while
that stays small; greedy focus fire otherwise), plays each subset in a fixed order (energy, Strength, debuffs,
attacks, block), and scores the result:
  safe       lethal on every enemy first, then the least HP lost this enemy turn, then the most damage
  balanced   lethal first, then damage dealt minus HP lost (1 HP = 1 damage), then the least HP lost

Modelled: damage and hit counts, block, Strength gained this turn, Vulnerable and Weak applied (Weak reduces that
enemy's intent), hit-all and random-target attacks (random hits spread round-robin, an approximation), energy
gain, HP-loss costs (Offering, Bloodletting), enemy block, Slippery (each hit deals 1 and removes a stack),
Intangible (each hit deals 1), killing an enemy removes its intent.
Not modelled: draw (plans with draw say "re-plan after drawing"), exhaust synergies, powers that trigger later,
Thorns, Hardened Shell's per-turn cap, relics, potions, card-specific conditions. Treat results as [HYPOTHESIS]
until the arithmetic is confirmed in game (knowledge/mechanics.md checklist).

Card numbers: live values from the mod when given (STS2-Agent dynamic_values current_value, assumed to include
your Strength, Weak, Dexterity and Frail but not the target's Vulnerable; to verify in Phase 0), otherwise base
values from the extract with calc.py modifiers.

Usage:
  python3 -I tools/plan_turn.py --state state.json [--top 3]          (STS2-Agent full /state in combat)
  python3 -I tools/plan_turn.py --hand Strike Strike Bash Defend Defend --energy 3 \\
      --enemy "Jaw Worm:40:0:11" --enemy "Louse:12:0:6x2:weak" [--strength 2] [--player-block 0] [--player-weak]
  Enemy spec: name:hp:block:intent[:flags], intent = total or per_hit x hits (0 if not attacking),
  flags = vuln, weak, slippery=N, intangible (comma-free, separated by ':').
"""
import argparse
import itertools
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calc  # noqa: E402
import deck_metrics  # noqa: E402
from deck_metrics import CARDS  # noqa: E402

deck_metrics.apply_patches("v0.111.1")  # live tools use the target game's card values

MAX_ASSIGNMENTS = 729  # per subset; above this, single-target cards focus the weakest enemy


@dataclass
class Card:
    index: int
    card_id: str
    name: str
    cost: int
    target: str                 # Self, AnyEnemy, AllEnemies, RandomEnemy
    dmg: int = 0                # per hit
    hits: int = 1
    block: int = 0
    vuln: int = 0
    weak: int = 0
    strength: int = 0
    energy: int = 0
    draw: int = 0
    hp_cost: int = 0
    x_cost: bool = False
    live: bool = False          # numbers already include the player's own modifiers
    playable: bool = True
    note: str = ""
    potion: bool = False        # a potion slot (index = slot); costs nothing but is spent
    flat: bool = False          # unpowered damage/block: no Strength, Vulnerable, Weak, Dexterity or Frail
    dex: int = 0                # Dexterity gained (applies to later block cards)


@dataclass
class Enemy:
    index: int
    name: str
    hp: int
    block: int = 0
    intent_per_hit: int = 0
    intent_hits: int = 0
    vuln: bool = False
    weak: bool = False
    slippery: int = 0
    intangible: bool = False


@dataclass
class Player:
    energy: int
    block: int = 0
    strength: int = 0
    dexterity: int = 0
    weak: bool = False
    frail: bool = False
    hp: Optional[int] = None


def parse_effect(c):
    """Structure from the extract's effect text."""
    e = c.get("effect") or ""
    out = {"dmg": 0, "hits": 1, "block": 0, "vuln": 0, "weak": 0, "strength": 0, "energy": 0, "draw": 0, "hp_cost": 0,
           "x_cost": "X (energy spent)" in e or (c.get("cost") is not None and c["cost"] < 0)}
    m = re.search(r"Deal (\d+) damage", e)
    if m:
        out["dmg"] = int(m.group(1))
    m = re.search(r"damage (\d+) times", e)
    if m:
        out["hits"] = int(m.group(1))
    for key, pat in (("block", r"Gain (\d+) Block"), ("vuln", r"Apply (\d+) Vulnerable"), ("weak", r"Apply (\d+) Weak"),
                     ("strength", r"Gain (\d+) Strength"), ("energy", r"Gain (\d+) Energy"), ("draw", r"Draw (\d+) card"),
                     ("hp_cost", r"Lose (\d+) HP")):
        m = re.search(pat, e)
        if m:
            out[key] = int(m.group(1))
    out["unknown"] = "?" in e
    return out


def card_from_extract(index, card_id, live=None, cost=None, playable=True):
    """live: dict of dynamic value name -> current value (STS2-Agent)."""
    cid = card_id.split(".", 1)[-1]
    c = CARDS.get(cid)
    if not c:
        return Card(index, cid, cid, cost if cost is not None else 9, "Self", playable=False, note="not in the extract")
    p = parse_effect(c)
    base_cost = c["cost"] if c["cost"] is not None and c["cost"] >= 0 else 0
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", c["name"])
    name = re.sub(r" (Ironclad|Silent|Necrobinder|Regent|Defect)$", "", name)
    card = Card(index, cid, name, cost if cost is not None else base_cost,
                c.get("target") or "Self", p["dmg"], p["hits"], p["block"], p["vuln"], p["weak"], p["strength"], p["energy"],
                p["draw"], p["hp_cost"], p["x_cost"], playable=playable)
    if c["type"] in ("Status", "Curse") or "Unplayable" in (c.get("effect") or ""):
        card.playable = False
    if live:
        card.live = True
        for k in ("CalculatedDamage", "Damage"):
            if k in live:
                card.dmg = int(live[k]); break
        if "Block" in live:
            card.block = int(live["Block"])
        if "Repeat" in live:
            card.hits = int(live["Repeat"])
    elif p["unknown"] and card.dmg == 0 and c["type"] == "Attack":
        card.note = "damage is computed in game (?): counted as 0"
    return card


# Combat potions modelled as zero-cost plays (values from the extract's potions.json, base values) [GAME-EXTRACT].
POTIONS = {
    "FIRE_POTION": dict(target="AnyEnemy", dmg=20, flat=True),
    "EXPLOSIVE_AMPOULE": dict(target="AllEnemies", dmg=10, flat=True),
    "BLOCK_POTION": dict(target="Self", block=12, flat=True),
    "WEAK_POTION": dict(target="AnyEnemy", weak=3),
    "VULNERABLE_POTION": dict(target="AnyEnemy", vuln=3),
    "STRENGTH_POTION": dict(target="Self", strength=2),
    "FLEX_POTION": dict(target="Self", strength=5),
    "ENERGY_POTION": dict(target="Self", energy=2),
    "DEXTERITY_POTION": dict(target="Self", dex=2),
    "SPEED_POTION": dict(target="Self", dex=5),
    "SWIFT_POTION": dict(target="Self", draw=3),
}
POTION_COST = {"hallway": 8.0, "elite": 3.0, "boss": 2.0}  # HP-equivalent cost of spending a potion [HYPOTHESIS]


def card_from_potion(slot, potion_id):
    pid = (potion_id or "").split(".", 1)[-1].upper()
    spec = POTIONS.get(pid)
    name = pid.replace("_", " ").title()
    if not spec:
        return Card(slot, pid, name, 0, "Self", playable=False, potion=True, note="potion not modelled")
    return Card(slot, pid, name, 0, spec["target"], dmg=spec.get("dmg", 0), block=spec.get("block", 0), vuln=spec.get("vuln", 0),
                weak=spec.get("weak", 0), strength=spec.get("strength", 0), energy=spec.get("energy", 0), draw=spec.get("draw", 0),
                potion=True, flat=spec.get("flat", False), dex=spec.get("dex", 0))


def per_hit(card, player, enemy, strength_gained):
    base = card.dmg
    if card.flat:
        d = base
        if enemy.slippery > 0 or enemy.intangible:
            d = min(d, 1)
        return max(0, d)
    if card.live:
        d = base + strength_gained
        d = math.floor(d * (calc.VULNERABLE if enemy.vuln else 1.0) + 1e-9)
    else:
        d = calc.hit_damage(base, player.strength + strength_gained, attacker_weak=player.weak, target_vulnerable=enemy.vuln)
    if enemy.slippery > 0 or enemy.intangible:
        d = min(d, 1)
    return max(0, d)


def hit(enemy, dmg):
    if enemy.hp <= 0:
        return 0
    if enemy.slippery > 0:
        enemy.slippery -= 1
    absorbed = min(enemy.block, dmg)
    enemy.block -= absorbed
    dealt = min(enemy.hp, dmg - absorbed)
    enemy.hp -= dealt
    return dealt


ORDER = {"energy": 0, "strength": 1, "debuff": 2, "attack": 3, "block": 4, "other": 5}


def phase(card):
    if card.energy and not card.dmg:
        return "energy"
    if (card.strength or card.dex) and not card.dmg:
        return "strength"
    if (card.vuln or card.weak) and card.target in ("AnyEnemy", "AllEnemies"):
        return "debuff"
    if card.dmg:
        return "attack"
    if card.block:
        return "block"
    return "other"


def simulate(cards, targets, player, enemies):
    """Play cards in order with the given targets. Returns the outcome dict, or None if energy runs out."""
    es = [Enemy(**vars(e)) for e in enemies]
    energy, block, strength_gained, hp_cost, dealt, draws = player.energy, player.block, 0, 0, 0, 0
    dex_gained, potions = 0, 0
    log = []
    for card, tgt in zip(cards, targets):
        cost = energy if card.x_cost else card.cost
        if cost > energy:
            return None
        energy -= cost
        energy += card.energy
        hp_cost += card.hp_cost
        draws += card.draw
        strength_gained += card.strength
        dex_gained += card.dex
        potions += card.potion
        alive = [e for e in es if e.hp > 0]
        hits = card.hits * (cost if card.x_cost else 1)
        if card.target == "AllEnemies":
            victims = alive
        elif card.target == "AnyEnemy":
            victims = [es[tgt]] if tgt is not None and es[tgt].hp > 0 else []
        else:
            victims = []
        if card.dmg:
            if card.target == "RandomEnemy":
                for h in range(hits):
                    live_now = [e for e in es if e.hp > 0]
                    if live_now:
                        e = live_now[h % len(live_now)]
                        dealt += hit(e, per_hit(card, player, e, strength_gained))
            else:
                for e in victims:
                    for _ in range(hits):
                        dealt += hit(e, per_hit(card, player, e, strength_gained))
        for e in victims:
            if card.vuln:
                e.vuln = True
            if card.weak:
                e.weak = True
        if card.block:
            if card.flat:
                block += card.block
            elif card.live:
                block += card.block + dex_gained
            else:
                block += calc.block_gain(card.block, player.dexterity + dex_gained, player.frail)
        label = (f"potion {card.name} (use_potion slot={card.index})" if card.potion else card.name)
        log.append(label + (f" → {es[tgt].name}[{tgt}]" if card.target == "AnyEnemy" and tgt is not None else ""))
    intents = [(e.intent_per_hit, e.intent_hits) for e in es if e.hp > 0 and e.intent_hits]
    weak = [e.weak for e in es if e.hp > 0 and e.intent_hits]
    inc = calc.incoming_hp_loss(intents, player_block=block, weak_enemies=weak)
    return {"plays": log, "dealt": dealt, "block": block, "incoming": inc.total, "hp_lost": inc.hp_lost + hp_cost,
            "kills": sum(1 for e, o in zip(es, enemies) if e.hp <= 0 < o.hp), "all_dead": all(e.hp <= 0 for e in es),
            "energy_left": energy, "draws": draws, "enemy_hp": [max(0, e.hp) for e in es], "potions": potions}


def plans(hand, player, enemies):
    playable = [c for c in hand if c.playable]
    alive_idx = [e.index for e in enemies if e.hp > 0]
    results = []
    max_gain = sum(c.energy for c in playable)
    for r in range(len(playable) + 1):
        for subset in itertools.combinations(playable, r):
            if sum(0 if c.x_cost else c.cost for c in subset) > player.energy + max_gain:
                continue
            ordered = sorted(subset, key=lambda c: (ORDER[phase(c)], -c.dmg * c.hits))
            single = [i for i, c in enumerate(ordered) if c.target == "AnyEnemy"]
            n_assign = len(alive_idx) ** len(single) if single else 1
            if n_assign <= MAX_ASSIGNMENTS:
                assigns = itertools.product(alive_idx, repeat=len(single)) if single else [()]
            else:
                lowest = min(alive_idx, key=lambda i: enemies[i].hp + enemies[i].block)
                assigns = [tuple([lowest] * len(single))]
            for a in assigns:
                targets = [None] * len(ordered)
                for pos, t in zip(single, a):
                    targets[pos] = t
                out = simulate(ordered, targets, player, enemies)
                if out:
                    results.append(out)
    return results


def rank(results, mode, potion_cost=POTION_COST["elite"]):
    """Lethal first (with the fewest potions); then the mode's objective, where each potion spent counts as
    potion_cost HP lost."""
    if mode == "safe":
        key = lambda o: (not o["all_dead"], o["potions"] if o["all_dead"] else 0,  # noqa: E731
                         o["hp_lost"] + potion_cost * o["potions"], -o["kills"], -o["dealt"], o["draws"] == 0)
    else:
        key = lambda o: (not o["all_dead"], o["potions"] if o["all_dead"] else 0,  # noqa: E731
                         -(o["dealt"] - o["hp_lost"] - potion_cost * o["potions"]), o["hp_lost"], -o["kills"])
    seen, out = set(), []
    for o in sorted(results, key=key):
        sig = tuple(sorted(o["plays"]))
        if sig not in seen:
            seen.add(sig)
            out.append(o)
    return out


# ------------------------------------------------------------------------------------------------ inputs
def from_state(st):
    st = st.get("data", st)
    c = st.get("combat") or {}
    p = c.get("player") or {}
    powers = {(x.get("power_id") or x.get("id") or x.get("name") or "").upper(): x.get("amount", x.get("stacks", 1))
              for x in p.get("powers") or []}
    player = Player(energy=int(p.get("energy") or 0), block=int(p.get("block") or 0),
                    strength=int(powers.get("STRENGTH_POWER", powers.get("STRENGTH", 0)) or 0),
                    dexterity=int(powers.get("DEXTERITY_POWER", powers.get("DEXTERITY", 0)) or 0),
                    weak=any(k.startswith("WEAK") for k in powers), frail=any(k.startswith("FRAIL") for k in powers),
                    hp=p.get("current_hp"))
    hand = []
    for h in c.get("hand") or []:
        live = {d["name"]: d.get("current_value") for d in h.get("dynamic_values") or [] if d.get("current_value") is not None}
        cost = int(h.get("energy_cost") or 0)
        hand.append(card_from_extract(int(h.get("index", len(hand))), h.get("card_id", "?"), live or None, cost,
                                      bool(h.get("playable", True))))
        if h.get("costs_x"):
            hand[-1].x_cost = True
    enemies = []
    for e in c.get("enemies") or []:
        if not e.get("is_alive", True):
            continue
        pw = {(x.get("power_id") or x.get("id") or x.get("name") or "").upper(): x.get("amount", x.get("stacks", 1))
              for x in e.get("powers") or []}
        att = [i for i in e.get("intents") or [] if i.get("damage") is not None]
        dmg = sum(int(i["damage"]) for i in att[:1])
        hits = sum(int(i.get("hits") or 1) for i in att[:1])
        enemies.append(Enemy(int(e.get("index", len(enemies))), e.get("name") or e.get("enemy_id"), int(e.get("current_hp") or 0),
                             int(e.get("block") or 0), dmg, hits,
                             vuln=any(k.startswith("VULNERABLE") for k in pw), weak=any(k.startswith("WEAK") for k in pw),
                             slippery=int(next((v for k, v in pw.items() if k.startswith("SLIPPERY")), 0) or 0),
                             intangible=any(k.startswith("INTANGIBLE") for k in pw)))
    for i, e in enumerate(enemies):
        e.index = i
    run = st.get("run") or {}
    for slot, pot in enumerate(run.get("potions") or []):
        if pot.get("occupied") and pot.get("potion_id"):
            pc = card_from_potion(int(pot.get("index", slot)), pot["potion_id"])
            if pc.playable:
                hand.append(pc)
    return hand, player, enemies


def parse_enemy(spec, index):
    parts = spec.split(":")
    name, hp, block, intent = parts[0], int(parts[1]), int(parts[2]), parts[3]
    if "x" in intent:
        a, b = intent.split("x")
        dmg, hits = int(a), int(b)
    else:
        dmg, hits = int(intent), (1 if int(intent) else 0)
    e = Enemy(index, name, hp, block, dmg, hits)
    for f in parts[4:]:
        if f == "vuln":
            e.vuln = True
        elif f == "weak":
            e.weak = True
        elif f == "intangible":
            e.intangible = True
        elif f.startswith("slippery="):
            e.slippery = int(f.split("=")[1])
    return e


def resolve_card(name):
    key = re.sub(r"[^A-Z0-9]", "", name.upper())
    for cid, c in CARDS.items():
        if re.sub(r"[^A-Z0-9]", "", cid) == key or re.sub(r"[^A-Z0-9]", "", c["name"].upper()) == key:
            return cid
    for suffix in ("IRONCLAD", "SILENT", "NECROBINDER", "REGENT", "DEFECT"):
        if key + suffix in {re.sub(r"[^A-Z0-9]", "", k) for k in CARDS}:
            return next(k for k in CARDS if re.sub(r"[^A-Z0-9]", "", k) == key + suffix)
    raise SystemExit(f"unknown card: {name}")


def fmt(o, hp):
    after = f", HP after {hp - o['hp_lost']}" if hp is not None else ""
    flags = (" · LETHAL" if o["all_dead"] else "") + (f" · re-plan after drawing {o['draws']}" if o["draws"] else "") \
        + (f" · spends {o['potions']} potion(s)" if o.get("potions") else "")
    return (f"{' + '.join(o['plays']) or '(play nothing)'}\n      deal {o['dealt']}, kills {o['kills']}, block {o['block']} "
            f"vs incoming {o['incoming']}, HP lost {o['hp_lost']}{after}, energy left {o['energy_left']}, "
            f"enemy HP {o['enemy_hp']}{flags}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state")
    ap.add_argument("--hand", nargs="*")
    ap.add_argument("--energy", type=int, default=3)
    ap.add_argument("--enemy", action="append", default=[])
    ap.add_argument("--strength", type=int, default=0)
    ap.add_argument("--dexterity", type=int, default=0)
    ap.add_argument("--player-block", type=int, default=0)
    ap.add_argument("--player-weak", action="store_true")
    ap.add_argument("--player-frail", action="store_true")
    ap.add_argument("--hp", type=int)
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--potion", action="append", default=[], help="potion id held, e.g. FIRE_POTION (repeatable)")
    ap.add_argument("--fight", choices=list(POTION_COST), default="elite", help="sets the cost of spending a potion")
    args = ap.parse_args(argv)
    if args.state:
        hand, player, enemies = from_state(json.loads(Path(args.state).read_text()))
    else:
        hand = [card_from_extract(i, resolve_card(n)) for i, n in enumerate(args.hand or [])]
        player = Player(args.energy, args.player_block, args.strength, args.dexterity, args.player_weak, args.player_frail, args.hp)
        enemies = [parse_enemy(s, i) for i, s in enumerate(args.enemy)]
        hand += [card_from_potion(i, pid) for i, pid in enumerate(args.potion)]
    if not enemies:
        raise SystemExit("no enemies")
    for c in hand:
        if c.note:
            print(f"note: {c.name}: {c.note}")
    res = plans(hand, player, enemies)
    for mode in ("safe", "balanced"):
        print(f"{mode}:")
        for o in rank(res, mode, POTION_COST[args.fight])[:args.top]:
            print("  " + fmt(o, player.hp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
