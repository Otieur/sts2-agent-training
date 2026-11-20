#!/usr/bin/env python3
"""Damage and block calculator for Slay the Spire 2 turn planning (P4.E2.S2).

Rules follow knowledge/mechanics.md. Multipliers come from the extracted power definitions ([GAME-EXTRACT]:
Vulnerable x1.5, Weak x0.75, Frail x0.75). The order (additive then multiplicative) and per-hit flooring are
Slay the Spire 1 conventions that still need checking in a v0.107.1 fight (mechanics.md checklist items 1-7).
Until then every result is [HYPOTHESIS].

Library use:
    from calc import attack, block_gain, incoming_hp_loss, strip_slippery
CLI:
    python3 -I tools/calc.py attack 6 --hits 2 --strength 2 --vulnerable
    python3 -I tools/calc.py block 5 --dexterity 1 --frail
    python3 -I tools/calc.py incoming 27 --weak --block 20
    python3 -I tools/calc.py slippery 9 --hits 1 1 2 3
"""
import argparse
import math
from dataclasses import dataclass, field
from typing import List, Optional

VULNERABLE = 1.5
WEAK = 0.75
FRAIL = 0.75


@dataclass
class AttackResult:
    per_hit: List[int]
    total: int
    hp_lost: int = 0
    block_left: int = 0
    notes: List[str] = field(default_factory=list)


def hit_damage(base: float, strength: int = 0, vigor: int = 0, attacker_weak: bool = False,
               target_vulnerable: bool = False, extra_mult: float = 1.0, cap: Optional[int] = None,
               vulnerable_mult: float = VULNERABLE, weak_mult: float = WEAK) -> int:
    """Damage of one hit before block. Additive (Strength, Vigor) first, then multipliers, then floor, then cap.
    [GAME] v0.111.1 Hooks.Hook.ModifyDamage: additions, then multiplications, then truncation to an integer, floor 0.
    vulnerable_mult and weak_mult change with Cruelty (+amount/100), Paper Phrog (+0.25), Paper Krane (Weak 0.60) and
    Debilitate (doubles the effect): VulnerablePower and WeakPower.ModifyDamageMultiplicative."""
    d = base + strength + vigor
    if d < 0:
        d = 0
    mult = extra_mult
    if target_vulnerable:
        mult *= vulnerable_mult
    if attacker_weak:
        mult *= weak_mult
    d = math.floor(d * mult + 1e-9)
    if cap is not None:
        d = min(d, cap)
    return max(0, d)


def attack(base: float, hits: int = 1, strength: int = 0, vigor: int = 0, attacker_weak: bool = False,
           target_vulnerable: bool = False, extra_mult: float = 1.0, cap: Optional[int] = None,
           target_block: int = 0) -> AttackResult:
    """A multi-hit attack against a target with block. Vigor applies to the first hit only."""
    per_hit = []
    for i in range(hits):
        per_hit.append(hit_damage(base, strength, vigor if i == 0 else 0, attacker_weak, target_vulnerable, extra_mult, cap))
    hp_lost, block = 0, target_block
    for d in per_hit:
        absorbed = min(block, d)
        block -= absorbed
        hp_lost += d - absorbed
    return AttackResult(per_hit=per_hit, total=sum(per_hit), hp_lost=hp_lost, block_left=block)


def block_gain(base: float, dexterity: int = 0, frail: bool = False, unmovable: bool = False) -> int:
    """Block from one card: (base + Dexterity) x 0.75 if Frail x 2 if Unmovable, floored."""
    b = max(0.0, base + dexterity)
    if frail:
        b *= FRAIL
    if unmovable:
        b *= 2
    return math.floor(b + 1e-9)


def incoming_hp_loss(intents: List[tuple], player_block: int = 0, player_vulnerable: bool = False,
                     weak_enemies: Optional[List[bool]] = None) -> AttackResult:
    """intents: list of (damage_per_hit_as_shown_without_your_vulnerable, hits). The game's intent numbers
    usually already include the enemy's Strength and Weak; pass shown numbers and only flag your own Vulnerable
    if the intent display does not include it (to verify, mechanics.md item 3)."""
    weak_enemies = weak_enemies or [False] * len(intents)
    per_hit = []
    for (dmg, hits), weak in zip(intents, weak_enemies):
        for _ in range(hits):
            per_hit.append(hit_damage(dmg, attacker_weak=weak, target_vulnerable=player_vulnerable))
    hp_lost, block = 0, player_block
    for d in per_hit:
        absorbed = min(block, d)
        block -= absorbed
        hp_lost += d - absorbed
    return AttackResult(per_hit=per_hit, total=sum(per_hit), hp_lost=hp_lost, block_left=block)


def strip_slippery(stacks: int, hits_per_card: List[int]) -> dict:
    """Simulate Slippery (Vantom): each damage instance deals 1 and removes a stack.
    hits_per_card: hit counts of the attacks you play, in order. Returns stacks left and cards needed."""
    played = 0
    for h in hits_per_card:
        if stacks <= 0:
            break
        stacks = max(0, stacks - h)
        played += 1
    return {"stacks_left": stacks, "cards_played": played, "cleared": stacks == 0}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("attack")
    a.add_argument("base", type=float)
    a.add_argument("--hits", type=int, default=1)
    a.add_argument("--strength", type=int, default=0)
    a.add_argument("--vigor", type=int, default=0)
    a.add_argument("--weak", action="store_true", help="attacker is Weak")
    a.add_argument("--vulnerable", action="store_true", help="target is Vulnerable")
    a.add_argument("--cap", type=int, default=None, help="per-hit cap (Slippery/Intangible = 1)")
    a.add_argument("--block", type=int, default=0, help="target block")
    b = sub.add_parser("block")
    b.add_argument("base", type=float)
    b.add_argument("--dexterity", type=int, default=0)
    b.add_argument("--frail", action="store_true")
    b.add_argument("--unmovable", action="store_true")
    i = sub.add_parser("incoming")
    i.add_argument("damage", type=float)
    i.add_argument("--hits", type=int, default=1)
    i.add_argument("--weak", action="store_true", help="the enemy is Weak")
    i.add_argument("--vulnerable", action="store_true", help="you are Vulnerable (if not already in the intent)")
    i.add_argument("--block", type=int, default=0)
    s = sub.add_parser("slippery")
    s.add_argument("stacks", type=int)
    s.add_argument("--hits", type=int, nargs="+", required=True, help="hit counts of attacks played, in order")
    args = ap.parse_args()
    if args.cmd == "attack":
        r = attack(args.base, args.hits, args.strength, args.vigor, args.weak, args.vulnerable, cap=args.cap, target_block=args.block)
        print(f"per hit {r.per_hit} total {r.total} | HP lost {r.hp_lost}, block left {r.block_left}")
    elif args.cmd == "block":
        print(block_gain(args.base, args.dexterity, args.frail, args.unmovable))
    elif args.cmd == "incoming":
        r = incoming_hp_loss([(args.damage, args.hits)], args.block, args.vulnerable, [args.weak])
        print(f"per hit {r.per_hit} total {r.total} | HP lost {r.hp_lost}, block left {r.block_left}")
    elif args.cmd == "slippery":
        print(strip_slippery(args.stacks, args.hits))


if __name__ == "__main__":
    main()
