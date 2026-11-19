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
Intangible (each hit deals 1), killing an enemy removes its intent, status cards that cost HP at the end of the
turn while held (Soul Fysh's Beckon: 6 HP, playable for 1 energy to get rid of it) [GAME-EXTRACT] + [COMMUNITY].
Card-specific rules: an Attack's own Strength gain comes after its hits (Fight Me); Setup Strike (Strength this turn),
Rage (Block per later Attack), Unrelenting (next Attack free), Mangle (target's attack lowered this turn), Flame
Barrier (damage back per enemy hit), Body Slam (damage = Block, played after block cards), Fiend Fire (played last,
7 per card left in hand), Dismantle (two hits on a Vulnerable target), Feel No Pain (Block per exhaust), Forgotten
Ritual (energy needs an earlier exhaust only with the pre-v0.111.1 text); boosters are played first. Slippery stacks
stripped earn SLIPPERY_VALUE in the balanced plan.
Enemy powers read from the state: Slippery, Intangible, Slow, Personal Hive, Enrage, Hardened Shell (per-turn cap),
Thorns, Artifact, Hard to Kill (per-hit cap), Shriek (stunned at its HP threshold), Vital Spark (Skills Tainted: more damage per Skill played), Skittish (Block after the first Attack each turn), Infested (its death is not the end), Ravenous (a death stuns the slugs), Imbalanced (a full block stuns it), Flutter (half damage; enough hits stun it), Burrowed (breaking its Block stuns it), Crab Rage (a claw's death: +5 Strength, 99 Block), Minion (killing every
non-minion ends the fight), Doom (it dies after its attack when its HP is at or below its Doom), Paper Cuts (max HP lost when its hits land); player powers: Strength, Dexterity, Weak, Frail, Feel No Pain, Sandpit, Disintegration, Sloth, Ringing, Tender, Colossus, Hex (held cards are lost), Shrink (30% less attack damage), Doom (fatal at the end of your turn if HP is at or below it).
Not modelled: draw (plans with draw say "re-plan after drawing"), other exhaust synergies, powers that trigger later,
relics, other card-specific conditions. Treat results as [HYPOTHESIS]
until the arithmetic is confirmed in game (knowledge/mechanics.md checklist).

Card numbers: live values from the mod when given (STS2-Agent dynamic_values current_value, assumed to include
your Strength, Weak, Dexterity and Frail but not the target's Vulnerable; to verify in Phase 0), otherwise base
values from the extract with calc.py modifiers.

Usage:
  python3 -I tools/plan_turn.py --state state.json [--top 3]          (STS2-Agent full /state in combat)
  python3 -I tools/plan_turn.py --hand Strike Strike Bash Defend Defend --energy 3 \\
      --enemy "Jaw Worm:40:0:11" --enemy "Louse:12:0:6x2:weak" [--strength 2] [--player-block 0] [--player-weak]
  Enemy spec: name:hp:block:intent[:flags], intent = total or per_hit x hits (0 if not attacking),
  flags = vuln, weak (already Weak: give the shown, already reduced intent), slippery=N, intangible, slow
  (separated by ':').
"""
import argparse
import copy
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
    osty: bool = False          # Necrobinder: "Your Osty deals X damage" (not modified by your Strength or Weak)
    summon: int = 0             # Necrobinder: Summon N (adds N to Osty's HP)
    kills_osty: bool = False    # "Kill your own Osty" (Bone Shards, Sacrifice)
    power: bool = False         # a Power card: its value comes in later turns (POWER_VALUE)
    held_loss: int = 0          # HP lost at the end of the turn if still in hand (Beckon 6; unblockable)
    exhausts: bool = False      # playing it exhausts a card (itself or another): enables Forgotten Ritual
    changes_hand: bool = False  # exhausts another card or adds cards to the hand: later hand indexes are unknown
    needs_exhaust: bool = False # its energy needs an exhaust earlier this turn (Forgotten Ritual before v0.111.1)
    str_down: int = 0           # the target loses this much Strength this turn (Mangle): its attack drops per hit
    retaliate: int = 0          # damage dealt back to each enemy hit this turn (Flame Barrier)
    temp_str: int = 0           # Strength for the rest of this turn only (Setup Strike)
    rage: int = 0               # Block for each Attack played later this turn (Rage)
    free_attacks: int = 0       # the next Attack costs 0 (Unrelenting's Free Attack)
    fnp: int = 0                # Feel No Pain gained: Block for each card exhausted later this turn
    held_dmg: int = 0           # damage (blockable) at the end of the turn if still in hand (Toxic 5)
    upgraded: bool = False
    skill: bool = False         # a Skill card (Test Subject's Enrage counts these)
    sandpit_add: int = 0        # adds to the Sandpit counter on you (Frantic Escape +1)
    heal_pct: int = 0           # heals this percent of max HP, at most the HP missing (Blood Potion 20)
    colossus: bool = False      # Colossus: half damage from Vulnerable enemies this turn
    doom: int = 0               # Doom applied to the target (Scourge 13, End of Days 29)
    self_doom: int = 0          # Doom on yourself (Borrowed Time 3)


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
    slow: bool = False          # Bygone Effigy: damage taken x (1 + 0.1 x cards played earlier this turn) [HYPOTHESIS unit]
    ref: Optional[int] = None   # the enemy's index in the mod's state (combat.enemies[].index), for target_index
    hive: int = 0               # Entomancer's Personal Hive: each damage instance it takes adds this many cards to your draw pile
    enrage: int = 0             # Test Subject's Enrage: it gains this much Strength for each Skill you play
    hp_cap: Optional[int] = None  # Hardened Shell: it loses at most this much HP per turn (damage already taken this turn unknown)
    thorns: int = 0             # Thorns: each hit you deal it costs you this much
    artifact: int = 0           # Artifact: each charge cancels one debuff applied to it
    lost_turn: int = 0          # HP it lost this turn (for Hardened Shell)
    hit_cap: Optional[int] = None  # Hard to Kill (Exoskeletons): each hit deals at most this much
    shriek: int = 0             # Shriek (Terror Eel): stunned the first time its HP drops to this or below (70; the wiki)
    taint: int = 0              # Vital Spark (Infested Prism): each Skill you play makes its attacks deal this much more per hit
    skittish: int = 0           # Skittish (Phantasmal Gardener): Block gained after the first Attack that hits it this turn
    infested: bool = False      # Infested (Phrog Parasite): its death summons Wrigglers, so the fight goes on
    ravenous: bool = False      # Ravenous (Corpse Slug): when another enemy dies it eats it and is stunned (attack cancelled)
    imbalanced: bool = False    # Imbalanced (Bowlbug Rock): stunned next turn if its attack is fully blocked
    flutter: int = 0            # Flutter (Thieving Hopper): Attack damage halved; this many more hits stun it
    burrowed: bool = False      # Burrowed (Tunneler): breaking all its Block stuns it (its attack is cancelled)
    crab_rage: bool = False     # Crab Rage (Kaiser Crab claws): when it dies the others gain 5 Strength and 99 Block
    minion: bool = False        # Minion: the fight ends when every non-minion is dead (Kin followers, Queen's Amalgam)
    doom: int = 0               # Doom on it: it dies at the end of its own turn (after attacking) if its HP is at or below it
    paper_cuts: int = 0         # Paper Cuts (Scrolls of Biting): you lose this much max HP each time it damages you


@dataclass
class Player:
    energy: int
    block: int = 0
    strength: int = 0
    dexterity: int = 0
    weak: bool = False
    frail: bool = False
    hp: Optional[int] = None
    osty_hp: int = 0            # Necrobinder's Osty: takes the unblocked damage aimed at you (DIE_FOR_YOU_POWER)
    max_cards: Optional[int] = None  # Sloth (Knowledge Demon's curse): at most this many cards per turn
    fnp: int = 0                # Feel No Pain already on you: Block for each card exhausted
    sandpit: int = 0            # The Insatiable's Sandpit on you: you die when it runs out (0 = none)
    end_turn_dmg: int = 0       # damage at the end of your turn from a power on you (Disintegration), blockable
    max_hp: Optional[int] = None
    tender: int = 0             # Tender (Hunter Killer): each card played costs 1 Strength and 1 Dexterity for the turn
    colossus: bool = False      # Colossus already played this turn
    doom: int = 0               # Doom on you: you die at the end of your turn if your HP is at or below it
    hexed: bool = False         # Hex (Spectral Knight): every card is Ethereal, so cards left in hand are exhausted
    shrunk: bool = False        # Shrink (Shrinker Beetle): your attacks deal 30% less (after Strength)


def parse_effect(c):
    """Structure from the extract's effect text."""
    e = c.get("effect") or ""
    out = {"dmg": 0, "hits": 1, "block": 0, "vuln": 0, "weak": 0, "strength": 0, "energy": 0, "draw": 0, "hp_cost": 0,
           "x_cost": "X (energy spent)" in e or (c.get("cost") is not None and c["cost"] < 0)}
    m = re.search(r"Deal (\d+) damage", e)
    if m:
        out["dmg"] = int(m.group(1))
    m = re.search(r"Your Osty deals (\d+) damage", e)
    out["osty"] = bool(m)
    if m:
        out["dmg"] = int(m.group(1))
    m = re.search(r"Summon (\d+)", e)
    out["summon"] = int(m.group(1)) if m else 0
    out["kills_osty"] = "Kill your own Osty" in e
    m = re.search(r"damage (\d+) times", e)
    if m:
        out["hits"] = int(m.group(1))
    for key, pat in (("block", r"Gain (\d+) Block"), ("vuln", r"Apply (\d+) Vulnerable"), ("weak", r"Apply (\d+) Weak"),
                     ("strength", r"Gain (\d+) Strength(?! Next)"), ("energy", r"Gain (\d+) Energy(?! Next Turn)"), ("draw", r"Draw (\d+) card"),
                     ("hp_cost", r"Lose (\d+) HP")):
        m = re.search(pat, e)
        if m:
            out[key] = int(m.group(1))
    out["unknown"] = "?" in e
    return out


def _upgrade(card, c):
    """Apply an upgrade to base numbers (not live ones) where the extract is unambiguous: one UpgradeValueBy on a card
    whose first variable is Damage, Block or Strength, or two values applied in variable order. [GAME-EXTRACT]"""
    ups = [int(x) for x in re.findall(r"UpgradeValueBy\((\d+)m?\)", c.get("on_upgrade") or "")]
    kinds = re.findall(r"(DamageVar|BlockVar|PowerVar<StrengthPower>|PowerVar<VulnerablePower>|PowerVar<WeakPower>|\w+Var|DynamicVar)",
                       c.get("vars") or "")
    attr = {"DamageVar": "dmg", "BlockVar": "block", "PowerVar<StrengthPower>": "strength",
            "PowerVar<VulnerablePower>": "vuln", "PowerVar<WeakPower>": "weak"}
    pairs = zip(kinds, ups) if len(ups) > 1 else ([(kinds[0], ups[0])] if ups and kinds else [])
    for kind, v in pairs:
        if kind in attr and getattr(card, attr[kind]):
            setattr(card, attr[kind], getattr(card, attr[kind]) + v)
    card.upgraded = True
    return card


_PROTOTYPES = {}


def card_from_extract(index, card_id, live=None, cost=None, playable=True):
    """live: dict of dynamic value name -> current value (STS2-Agent). A trailing '+' on the ID means upgraded
    (applied to base numbers only; live numbers already include it). Cards built from the extract alone are parsed
    once and copied (the simulator builds thousands per draft)."""
    if live is None and cost is None and playable is True:
        key = str(card_id)
        proto = _PROTOTYPES.get(key)
        if proto is None:
            proto = _PROTOTYPES[key] = _card_from_extract(0, card_id)
        card = copy.copy(proto)
        card.index = index
        return card
    return _card_from_extract(index, card_id, live, cost, playable)


def _card_from_extract(index, card_id, live=None, cost=None, playable=True):
    cid = str(card_id or "?").split(".", 1)[-1]
    plus = cid.endswith("+")
    cid = cid.rstrip("+")
    c = CARDS.get(cid)
    if plus and c and not live:
        return _upgrade(_card_from_extract(index, cid, None, cost, playable), c)
    if not c:
        if cid in EXTRA_STATUSES:  # statuses newer than the extract (Aeonglass's Wither) [COMMUNITY]
            # playable only if the state says so (one guide gives Wither Retain and Exhaust); its cost comes from the state
            card = Card(index, cid, cid.replace("_", " ").title(), cost or 0, "Self", playable=bool(playable) and cost is not None,
                        note=EXTRA_STATUSES[cid]["note"])
            card.held_dmg = int((live or {}).get("Damage") or EXTRA_STATUSES[cid]["held_dmg"])
            return card
        return Card(index, cid, cid, cost if cost is not None else 9, "Self", playable=False, note="not in the extract")
    p = parse_effect(c)
    base_cost = c["cost"] if c["cost"] is not None and c["cost"] >= 0 else 0
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", c["name"])
    name = re.sub(r" (Ironclad|Silent|Necrobinder|Regent|Defect)$", "", name)
    is_power = c["type"] == "Power"
    card = Card(index, cid, name, cost if cost is not None else base_cost,
                c.get("target") or "Self", p["dmg"], p["hits"], p["block"], p["vuln"], p["weak"], p["strength"], p["energy"],
                p["draw"], p["hp_cost"], p["x_cost"], playable=playable, osty=p["osty"], summon=p["summon"],
                kills_osty=p["kills_osty"], power=is_power)
    if c["type"] in ("Status", "Curse") or "Unplayable" in (c.get("effect") or ""):
        card.playable = False
    m = re.search(r'"StrengthLoss", (\d+)', c.get("vars") or "")
    card.str_down = int(m.group(1)) if m else 0
    m = re.search(r"Gain (\d+) Flame Barrier", c.get("effect") or "")
    card.retaliate = int(m.group(1)) if m else 0
    eff = c.get("effect") or ""
    for attr, pat in (("temp_str", r"Gain (\d+) Setup Strike"), ("rage", r"Gain (\d+) Rage"),
                      ("free_attacks", r"Gain (\d+) Free Attack"), ("fnp", r"Gain (\d+) Feel No Pain")):
        m = re.search(pat, eff)
        setattr(card, attr, int(m.group(1)) if m else 0)
    card.colossus = bool(re.search(r"Gain \d+ Colossus", eff))
    m = re.search(r"Apply (\d+) Doom", eff)
    card.doom = int(m.group(1)) if m else 0
    m = re.search(r"Gain (\d+) Doom", eff)
    card.self_doom = int(m.group(1)) if m else 0
    if cid in OSTY_HP_DAMAGE:  # Unleash: an Osty attack whose damage grows with Osty's HP (set when played)
        card.osty, card.dmg, card.live = True, OSTY_HP_DAMAGE[cid], False
    card.skill = c["type"] == "Skill"
    card.needs_exhaust = cid in CONDITIONAL_ENERGY and "no card needs to be exhausted" not in (c.get("effect") or "")
    card.exhausts = bool({"kw-exhaust", "exhaust-other"} & set(c.get("tags") or [])) or "Exhaust a card" in (c.get("effect") or "")
    card.changes_hand = ("exhaust-other" in (c.get("tags") or []) or "Exhaust a card" in (c.get("effect") or "")
                         or "to your hand" in (c.get("effect") or ""))
    unplayable = "Unplayable" in (c.get("effect") or "") or "unplayable" in (c.get("tags") or [])
    m = re.search(r"DamageVar\((\d+)m?, ValueProp\.Unpowered", c.get("vars") or "")
    if c["type"] == "Status" and m and "no OnPlay effect" in (c.get("effect") or ""):
        # Burn 2, Infection 3, Toxic 5: damage at the end of your turn while held (blockable) [GAME-EXTRACT]
        card.held_dmg = int(m.group(1))
        card.note = f"{card.held_dmg} damage at end of turn if held"
    if c["type"] == "Status" and c.get("cost") is not None and c["cost"] >= 0 and not unplayable:
        # Playable statuses (game data: Beckon, Debris, Frantic Escape, Slimed, Toxic) follow the game's playable flag
        card.playable = playable
        m = re.search(r"HpLossVar\((\d+)", c.get("vars") or "")
        if m:  # Beckon: 6 HP lost (unblockable) at the end of the turn if held [GAME-EXTRACT] + [COMMUNITY]
            card.held_loss = int(m.group(1))
            card.note = f"loses {card.held_loss} HP at end of turn if held"
        if cid == "TOXIC":  # 5 damage at the end of the turn if held; playing it exhausts it [COMMUNITY]
            card.held_dmg = 5
            card.note = "5 damage at end of turn if held"
        if cid == "FRANTIC_ESCAPE":  # +1 Sandpit per play; its cost rises by 1 each play [COMMUNITY]
            card.sandpit_add = 1
            card.note = "Sandpit +1 (you die when Sandpit runs out)"
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
    "STRENGTH_POTION": dict(target="Self", strength=2, lasting=True),
    "FLEX_POTION": dict(target="Self", strength=5),
    "ENERGY_POTION": dict(target="Self", energy=2),
    "DEXTERITY_POTION": dict(target="Self", dex=2, lasting=True),
    "SPEED_POTION": dict(target="Self", dex=5),
    "SWIFT_POTION": dict(target="Self", draw=3),
    "POTION_SHAPED_ROCK": dict(target="AnyEnemy", dmg=15, flat=True),
    "POTION_OF_BINDING": dict(target="AllEnemies", vuln=1, weak=1),
    "CURE_ALL": dict(target="Self", energy=1, draw=2),
    "RADIANT_TINCTURE": dict(target="Self", energy=1),       # plus 3 Radiance (not modelled)
    "LIQUID_BRONZE": dict(target="Self", retaliate=3),       # 3 Thorns on you for the fight (counted this turn only)
    "BLOOD_POTION": dict(target="Self", heal_pct=20),        # heal 20% of max HP, at most the HP missing
}
# HP-equivalent cost of spending a potion [HYPOTHESIS]. High in hallways (a Fire Potion's 20 damage should not be
# spent on a hallway fight unless it kills or prevents a large loss), low in elites and bosses, where the playbook
# says use potions freely.
# Boss value checked in tools/simulate_fight.py (2026-11-19, Fire, Block and Strength potions, 60 fights per cell): mixed,
# Vantom better at 8 (95% against 85%), Lagavulin and Soul Fysh slightly better at 0-2; kept at 2.
POTION_COST = {"hallway": 25.0, "elite": 6.0, "boss": 2.0}
# Value of playing a Power now, per energy it costs, in damage-or-HP equivalents for the turns still to come
# [HYPOTHESIS]. A Strike deals 6 per energy now; a Power pays back over the rest of the fight: bosses last 6-10 turns
# (playbook section 1), elites about 4-5, hallway fights about 3, and the fight model finds scaling cards cost HP in
# Act 1 hallways but save it at the Act 2 boss. Hence about 10 per energy in bosses, 5 in elites, 1 in hallways.
# Checked in tools/simulate_fight.py (2026-11-19): boss value 3 lost far more fights with Power decks (Lagavulin 55% against
# 100% with Demon Form and Pyre); 20 was no better than 10.
POWER_VALUE = {"hallway": 1.0, "elite": 5.0, "boss": 10.0}


def card_from_potion(slot, potion_id):
    pid = (potion_id or "").split(".", 1)[-1].upper()
    spec = POTIONS.get(pid)
    name = pid.replace("_", " ").title()
    if not spec:
        return Card(slot, pid, name, 0, "Self", playable=False, potion=True, note="potion not modelled")
    card = Card(slot, pid, name, 0, spec["target"], dmg=spec.get("dmg", 0), block=spec.get("block", 0), vuln=spec.get("vuln", 0),
                weak=spec.get("weak", 0), strength=spec.get("strength", 0), energy=spec.get("energy", 0), draw=spec.get("draw", 0),
                potion=True, flat=spec.get("flat", False), dex=spec.get("dex", 0))
    card.retaliate, card.heal_pct = spec.get("retaliate", 0), spec.get("heal_pct", 0)
    card.power = bool(spec.get("lasting"))  # Strength or Dexterity for the whole fight: valued like a 1-energy Power
    return card


def per_hit(card, player, enemy, strength_gained, played_before=0):
    base = card.dmg
    slow = 1 + 0.1 * played_before if enemy.slow else 1.0
    if card.osty and not card.live:
        d = math.floor(base * (calc.VULNERABLE if enemy.vuln else 1.0) * slow + 1e-9)
        if enemy.slippery > 0 or enemy.intangible:
            d = min(d, 1)
        return max(0, d)
    if card.flat:
        d = base
        if enemy.slippery > 0 or enemy.intangible:
            d = min(d, 1)
        return max(0, d)
    if card.live:
        d = base + strength_gained
        d = math.floor(d * (calc.VULNERABLE if enemy.vuln else 1.0) * slow + 1e-9)
    else:
        d = calc.hit_damage(base, player.strength + strength_gained, attacker_weak=player.weak, target_vulnerable=enemy.vuln,
                            extra_mult=slow)
    if enemy.slippery > 0 or enemy.intangible:
        d = min(d, 1)
    if enemy.hit_cap is not None:
        d = min(d, enemy.hit_cap)
    if player.shrunk and not card.live and not card.flat:  # Shrink: 30% less, after Strength (live values include it)
        d = math.floor(d * 0.7 + 1e-9)
    if enemy.flutter > 0:  # Flutter: Attack damage taken halved (the wiki)
        d = d // 2
    return max(0, d)


# Damage-equivalent cost of each card Personal Hive adds to your draw pile [HYPOTHESIS]: an added dead card is likely
# drawn about once in the rest of the fight and replaces a real card play (about a Strike's 6), slightly discounted.
HIVE_COST = 5.0
# Sandpit (The Insatiable): each turn of Sandpit, up to a buffer of SANDPIT_BUFFER, is worth SANDPIT_VALUE damage-equivalents,
# so Frantic Escapes are played while cheap instead of at the last moment. Tuned in tools/simulate_fight.py (22-card Act 2
# deck, 40 fights): eaten 30 times with 0, 21 with 10, 18 with 20, 16 with 40 [HYPOTHESIS].
SANDPIT_VALUE, SANDPIT_BUFFER = 20.0, 4
# Hex (Spectral Knight): a playable card left in hand is exhausted; losing it for the fight is counted as this much [HYPOTHESIS]
HEX_CARD_COST = 2.0
# Slippery (Vantom): every hit while Slippery deals 1 but removes a stack, and each stack removed lets a later hit deal
# full damage, so the balanced plan credits each stack stripped with this many damage-equivalents (tuned in
# tools/simulate_fight.py against Vantom; see reports/phase2/vantom-simulation.md) [HYPOTHESIS].
SLIPPERY_VALUE = 3.0


def fight_over(es):
    """Every enemy dead, or every non-minion dead (minions flee or die with their leader) [GAME-EXTRACT] + [HYPOTHESIS]."""
    if any(e.infested and e.hp <= 0 for e in es):
        return False  # Infested: Wrigglers appear and the fight continues (the wiki)
    leaders = [e for e in es if not e.minion]
    return all(e.hp <= 0 for e in (leaders or es))


def hit(enemy, dmg):
    if enemy.hp <= 0:
        return 0
    if enemy.hive and dmg > 0:
        enemy.hive_added = getattr(enemy, "hive_added", 0) + enemy.hive
    if enemy.slippery > 0:
        enemy.slippery -= 1
    if enemy.flutter > 0:  # every hit counts toward the stun; at 0 it is stunned (attack this turn assumed cancelled)
        enemy.flutter -= 1
        if enemy.flutter == 0:
            enemy.intent_hits = 0
    absorbed = min(enemy.block, dmg)
    enemy.block -= absorbed
    if enemy.burrowed and absorbed > 0 and enemy.block == 0:  # Burrowed Block broken: stunned (the wiki)
        enemy.burrowed = False
        enemy.intent_hits = 0
    dealt = min(enemy.hp, dmg - absorbed)
    if enemy.hp_cap is not None:  # Hardened Shell: HP lost per turn capped [GAME-EXTRACT]
        dealt = max(0, min(dealt, enemy.hp_cap - enemy.lost_turn))
    enemy.hp -= dealt
    enemy.lost_turn += dealt
    if enemy.shriek and enemy.hp <= enemy.shriek:  # Shriek: stunned at the threshold (the wiki); its attack this turn is
        enemy.shriek = 0                           # assumed cancelled, and Terror (99 Vulnerable on you) follows next turn
        enemy.intent_hits = 0
    return dealt


ORDER = {"energy": 0, "strength": 1, "debuff": 2, "attack": 3, "block": 4, "after_block": 4.5, "other": 5, "last": 6}


OSTY_HP_DAMAGE = {"UNLEASH": 6}  # Osty deals this plus his current HP (community card pages; v0.107.1 page)
EXTRA_STATUSES = {  # not in the extract: unplayable, damage at the end of the turn while held (whisperofthehouse, 2026-11-16)
    "WITHER": {"held_dmg": 3, "note": "Wither: unplayable, 3 damage at end of turn while held (more if upgraded)"},
}
CONDITIONAL_ENERGY = {"FORGOTTEN_RITUAL"}       # energy only after an exhaust this turn, unless the card text (patched
                                                # to v0.111.1 in deck_metrics) says no exhaust is needed
HITS_TWICE_IF_VULNERABLE = {"DISMANTLE"}
BLOCK_DAMAGE = {"BODY_SLAM"}                    # deals damage equal to your current Block [GAME-EXTRACT] CalculatedDamage
EXHAUST_HAND = {"FIEND_FIRE"}                   # exhausts the rest of the hand: 7 damage per card exhausted [GAME-EXTRACT]


def phase(card):
    if card.card_id in BLOCK_DAMAGE:
        return "after_block"  # Body Slam: its damage is your Block when played
    if card.energy and not card.dmg:
        return "energy"
    if (card.strength or card.dex or card.summon or card.rage or card.fnp) and not card.dmg:
        return "strength"  # setup before attacks (Summon before Osty attacks, Rage before Attacks, Feel No Pain before exhausts)
    if (card.vuln or card.weak) and card.target in ("AnyEnemy", "AllEnemies"):
        return "debuff"
    if card.dmg:
        return "attack"
    if card.block:
        return "block"
    return "other"


def simulate(cards, targets, player, enemies):
    """Play cards in order with the given targets. Returns the outcome dict, or None if energy runs out."""
    es = [Enemy(**{k: v for k, v in vars(e).items() if k != "eaten"}) for e in enemies]
    for e in es:
        e.eaten = e.hp <= 0  # already dead before this plan: not a new death for Ravenous
    energy, block, strength_gained, hp_cost, dealt, draws = player.energy, player.block, 0, 0, 0, 0
    dex_gained, potions, powers = 0, 0, 0
    osty = player.osty_hp
    log = []
    played = 0
    skills = 0  # Skills played this turn (Test Subject's Enrage)
    seq = []
    exhausted = False  # a card exhausted earlier this turn (cards exhausted before the state was read are not known)
    retaliate = 0      # Flame Barrier: damage back per enemy hit
    rage, free, fnp = 0, 0, player.fnp  # Rage block per Attack, free Attacks, Feel No Pain block per exhaust
    colossus = player.colossus
    my_doom = player.doom
    for card, tgt in zip(cards, targets):
        cost = energy if card.x_cost else card.cost
        is_attack = bool(card.dmg) or card.card_id in BLOCK_DAMAGE
        if free and is_attack and cost > 0 and not card.x_cost:
            cost, free = 0, free - 1  # Unrelenting: the next Attack costs 0
        if cost > energy:
            return None
        energy -= cost
        # Forgotten Ritual before v0.111.1: energy only after an exhaust this turn [COMMUNITY]; v0.111.1 removed the condition
        energy += 0 if (card.needs_exhaust and not exhausted) else card.energy
        hp_cost += card.hp_cost
        if card.heal_pct and player.max_hp and player.hp is not None:  # Blood Potion: heal, at most what is missing
            hp_cost -= min(max(0, player.max_hp - (player.hp - hp_cost)), player.max_hp * card.heal_pct // 100)
        draws += card.draw
        str_before = strength_gained  # an Attack's own Strength gain (Fight Me, Setup Strike) applies after its hits
        strength_gained += card.strength + card.temp_str
        dex_gained += card.dex
        potions += card.potion
        powers += max(1, cost) if card.power else 0  # energy spent on Powers
        alive = [e for e in es if e.hp > 0]
        if card.card_id in BLOCK_DAMAGE:  # damage = Block now (Strength, Vulnerable and Weak still apply)
            card = Card(**{**vars(card), "dmg": block, "live": False})
        if card.card_id in OSTY_HP_DAMAGE:  # Unleash: base plus Osty's HP at this moment (after earlier Summons)
            card = Card(**{**vars(card), "dmg": OSTY_HP_DAMAGE[card.card_id] + max(0, osty), "live": False})
        hits = card.hits * (cost if card.x_cost else 1)
        if card.osty and osty <= 0:
            hits = 0  # Osty is dead: its attacks do nothing
        osty += card.summon
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
                        hp_cost += e.thorns
                        dealt += hit(e, per_hit(card, player, e, str_before, played))
            else:
                for e in victims:
                    # Dismantle: hits twice if the target is Vulnerable [COMMUNITY] (the extract shows "? times")
                    for _ in range(hits * (2 if card.card_id in HITS_TWICE_IF_VULNERABLE and e.vuln else 1)):
                        if e.hp > 0 and e.thorns and not card.osty:
                            hp_cost += e.thorns  # Thorns hit back on each hit (counted as HP lost; block may absorb it)
                        dealt += hit(e, per_hit(card, player, e, str_before, played))
                    if e.skittish and e.hp > 0:  # Skittish: Block after the first Attack that hits it this turn (the wiki)
                        e.block += e.skittish
                        e.skittish = 0
        if any(e.hp <= 0 and not getattr(e, "eaten", False) for e in es):  # Ravenous: slugs eat the dead and are stunned
            for e in es:
                if e.hp <= 0:
                    e.eaten = True
            for o in es:
                if o.ravenous and o.hp > 0:
                    o.intent_hits = 0
        for e in es:  # Crab Rage: a claw that died this card gives the others 5 Strength and 99 Block (this turn)
            if e.crab_rage and e.hp <= 0:
                e.crab_rage = False
                for o in es:
                    if o is not e and o.hp > 0:
                        o.block += 99
                        if o.intent_hits:
                            o.intent_per_hit += 5
        for e in victims:
            for debuff in ("vuln", "weak", "str_down"):
                if not getattr(card, debuff):
                    continue
                if e.artifact > 0:  # Artifact cancels the debuff and loses a charge
                    e.artifact -= 1
                elif debuff == "vuln":
                    e.vuln = True
                elif debuff == "weak":
                    e.weak = True
                elif e.intent_hits:  # Mangle: Strength lost this turn lowers each hit of its attack
                    e.intent_per_hit = max(0, e.intent_per_hit - card.str_down)
        retaliate += card.retaliate
        if is_attack and rage:
            block += rage  # Rage: flat Block for each Attack after it (assumed unaffected by Dexterity) [HYPOTHESIS]
        rage += card.rage
        free += card.free_attacks
        colossus = colossus or card.colossus
        my_doom += card.self_doom
        for e in victims:
            if card.doom and e.hp > 0:
                e.doom += card.doom
        if card.block:
            if card.flat:
                block += card.block
            elif card.live:
                block += card.block + dex_gained
            else:
                block += calc.block_gain(card.block, player.dexterity + dex_gained, player.frail)
        if card.kills_osty:
            osty = 0
        if not card.potion:
            played += 1
            skills += card.skill
        if player.tender and not card.potion:  # Tender: later cards this turn hit and block for less
            strength_gained -= player.tender
            dex_gained -= player.tender
        if card.exhausts:
            exhausted = True
            block += fnp * ((card.hits + 1) if card.card_id in EXHAUST_HAND else 1)  # Feel No Pain, flat
        fnp += card.fnp
        seq.append((card, es[tgt].ref if (card.target == "AnyEnemy" and tgt is not None and es[tgt].ref is not None)
                    else (tgt if card.target == "AnyEnemy" else None)))
        label = (f"potion {card.name} (use_potion slot={card.index})" if card.potion else card.name)
        log.append(label + (f" → {es[tgt].name}[{tgt}]" if card.target == "AnyEnemy" and tgt is not None else ""))
    # Intent numbers already include Weak that was on the enemy when the state was read (the game computes them), so
    # only Weak applied during this turn reduces them further.
    pairs = [(e, o) for e, o in zip(es, enemies) if e.hp > 0 and e.intent_hits]
    # Enrage (Test Subject, phase 1): Strength for every Skill played this turn raises each hit (two guides: Skills only)
    intents = [(e.intent_per_hit + (e.enrage + e.taint) * skills, e.intent_hits) for e, o in pairs]  # Vital Spark: Tainted Skills
    if colossus:  # half damage from Vulnerable enemies this turn [GAME-EXTRACT] + [COMMUNITY]
        intents = [(d // 2 if e.vuln else d, h) for (d, h), (e, o) in zip(intents, pairs)]
    weak = [e.weak and not o.weak for e, o in pairs]
    if player.end_turn_dmg:  # Disintegration hits at the end of your turn, before the enemies, and uses up block first
        intents.append((player.end_turn_dmg, 1))
        weak.append(False)
    inc = calc.incoming_hp_loss(intents, player_block=block, weak_enemies=weak)
    to_osty = min(osty, inc.hp_lost)  # Osty takes the unblocked damage first while alive [GAME-EXTRACT] DIE_FOR_YOU_POWER
    lost = inc.hp_lost - to_osty + hp_cost
    all_dead = fight_over(es)
    if all_dead:  # the fight ends now: no enemy turn (minions flee with their leader)
        lost = hp_cost
    dies = player.hp is not None and lost >= player.hp and not all_dead
    if my_doom and player.hp is not None and player.hp - hp_cost <= my_doom and not all_dead:
        dies = True  # Doom on you is checked at the end of your turn [GAME-EXTRACT] DOOM_POWER
    # Paper Cuts: if attacks get through, each hit of an enemy with it also costs max HP (block is pooled, so this assumes
    # its hits are among those that land) [GAME-EXTRACT]; counted as HP lost because it is permanent
    if inc.hp_lost > 0 and not all_dead:
        cuts = sum(e.paper_cuts * e.intent_hits for e in es if e.hp > 0 and e.paper_cuts and e.intent_hits)
        lost += cuts
    # Imbalanced (Bowlbug Rock): fully blocking every attack (with at least 1 Block) stuns it next turn, worth its next attack
    stun_bonus = 0
    if not all_dead and block > 0 and inc.hp_lost == 0:
        stun_bonus = sum(e.intent_per_hit * e.intent_hits for e in es if e.hp > 0 and e.imbalanced and e.intent_hits)
    # Doom on an enemy: it still attacks this turn, then dies at the end of its turn (most guides) [COMMUNITY]
    doomed = [e for e in es if e.hp > 0 and e.doom and e.hp <= e.doom]
    doom_dealt = sum(e.hp for e in doomed)
    if retaliate:  # Flame Barrier hits back on every enemy hit (assumed even when blocked) [HYPOTHESIS]
        for e in es:
            if e.hp > 0 and e.intent_hits:
                back = min(e.hp, retaliate * e.intent_hits)
                e.hp -= back
                dealt += back
    return {"plays": log, "dealt": dealt, "block": block, "incoming": inc.total, "hp_lost": lost, "dies": dies,
            "osty_hp_after": osty - to_osty, "osty_before_enemy": osty, "powers": powers,  # energy spent on Powers
            "seq": seq,
            "hive_cards": sum(getattr(e, "hive_added", 0) for e in es),
            "slippery_stripped": sum(o.slippery - e.slippery for e, o in zip(es, enemies) if e.hp > 0),
            "doomed": len(doomed), "doom_dealt": doom_dealt, "doom_on_you": my_doom, "stun_bonus": stun_bonus,
            "enemies_after": [{"hp": max(0, e.hp), "block": e.block, "slippery": e.slippery, "vuln": e.vuln, "weak": e.weak} for e in es],
            "kills": sum(1 for e, o in zip(es, enemies) if e.hp <= 0 < o.hp), "all_dead": all_dead,
            "energy_left": energy, "draws": draws, "enemy_hp": [max(0, e.hp) for e in es], "potions": potions}


def _exhaust_before_ritual(ordered):
    """Forgotten Ritual pays only after an exhaust: move a non-attack exhauster to the front, or Ritual after the first."""
    rit = [c for c in ordered if c.needs_exhaust]
    ex = [c for c in ordered if c.exhausts and not c.needs_exhaust]
    if not rit or not ex:
        return ordered
    first = next((c for c in ex if not c.dmg), None)
    if first is not None:
        return [first] + [c for c in ordered if c is not first]
    rest = [c for c in ordered if all(c is not r for r in rit)]
    i = next(k for k, c in enumerate(rest) if c is ex[0])
    return rest[:i + 1] + rit + rest[i + 1:]


def plans(hand, player, enemies):
    playable = [c for c in hand if c.playable]
    alive_idx = [e.index for e in enemies if e.hp > 0]
    results = []
    max_gain = sum(c.energy for c in playable) + (3 if any(c.free_attacks for c in playable) else 0)
    for r in range(len(playable) + 1):
        for subset in itertools.combinations(playable, r):
            if player.max_cards is not None and sum(1 for c in subset if not c.potion) > player.max_cards:
                continue
            if sum(0 if c.x_cost else c.cost for c in subset) > player.energy + max_gain:
                continue
            slow = any(e.slow for e in enemies)  # against Slow, small attacks first and the big one last
            ordered = sorted(subset, key=lambda c: (ORDER[phase(c)], -(c.strength + c.temp_str + 3 * c.free_attacks),  # boosters first
                                                    (c.dmg * c.hits) if slow else -c.dmg * c.hits))
            ordered = _exhaust_before_ritual(ordered)
            fa = next((c for c in ordered if c.free_attacks), None)
            if fa is not None:  # Unrelenting first, so its Free Attack makes the next Attack (even Bash) cost 0
                ordered = [fa] + [c for c in ordered if c is not fa]
            ids = {id(s) for s in subset}
            ff = [c for c in ordered if c.card_id in EXHAUST_HAND]
            if len(ff) > 1:
                continue  # the first Fiend Fire exhausts the second
            if ff:  # Fiend Fire last: it exhausts every card left in hand, 7 damage for each
                n_ex = sum(1 for c in hand if not c.potion and id(c) not in ids)
                ordered = [c for c in ordered if c is not ff[0]] + [Card(**{**vars(ff[0]), "hits": n_ex})]
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
                    left = [c for c in hand if id(c) not in ids] if not ff else []  # Fiend Fire exhausts them
                    if player.hexed:  # Hex: each playable card left in hand is lost for the fight
                        out["hex_loss"] = HEX_CARD_COST * sum(1 for c in left if c.playable and not c.potion)
                    held = sum(c.held_loss for c in left)
                    # Toxic: blockable, taken at the end of your turn before the enemies attack, so it uses up block first
                    held += max(0, sum(c.held_dmg for c in left) - max(0, out["block"] - out["incoming"]))
                    if held:
                        out["hp_lost"] += held
                        out["held_loss"] = held
                        out["dies"] = player.hp is not None and out["hp_lost"] >= player.hp and not out["all_dead"]
                    if player.sandpit:  # Sandpit ticks down before your next turn; at 0 it kills you
                        out["sandpit_after"] = player.sandpit + sum(c.sandpit_add for c in subset)
                        if out["sandpit_after"] <= 1 and not out["all_dead"]:
                            out["dies"] = True
                        # a buffer of turns is worth energy: Frantic Escape may not be in hand when the counter runs low
                        out["sandpit_bonus"] = SANDPIT_VALUE * min(out["sandpit_after"], SANDPIT_BUFFER)
                    results.append(out)
    return results


def commands(o, hand, log="runs/<run>/decisions.jsonl", mode="safe", mod="sts2agent"):
    """sts.py commands (STS2-Agent) for a plan, with hand indexes adjusted as cards leave the hand. Commands after a
    draw card are marked: re-read the state and re-plan after the draw."""
    remaining = [c.index for c in hand if not c.potion]
    out, drawn = [], False
    for card, target in o.get("seq", []):
        if target is None:
            tgt = ""
        elif mod == "sts2mcp":
            tgt = f" target={target}"  # STS2MCP targets by entity_id
        else:
            tgt = f" target_index={target}"
        reason = f"Turn plan ({mode}): {card.name}" + (f" on enemy {target}" if target is not None else "")
        if card.potion:
            cmd = f"act use_potion {'slot' if mod == 'sts2mcp' else 'option_index'}={card.index}{tgt}"
        else:
            pos = remaining.index(card.index)
            remaining.pop(pos)
            cmd = f"act play_card card_index={pos}{tgt}"
        prefix = "# after re-planning: " if drawn else ""
        out.append(f'{prefix}python3 -I tools/sts.py --mod {mod} --log {log} {cmd} --reason "{reason}"')
        if card.draw or card.changes_hand:  # the hand changes in ways the plan cannot index: re-read the state
            drawn = True
    if not drawn:
        out.append(f'python3 -I tools/sts.py --mod {mod} --log {log} act end_turn --reason "Turn plan ({mode}) complete"')
    return out


def rank(results, mode, potion_cost=POTION_COST["elite"], power_value=POWER_VALUE["elite"]):
    """Lethal first (with the fewest potions); then any plan that keeps you alive (needs Player.hp); then the mode's
    objective. Each potion spent counts as potion_cost HP
    lost; each energy spent on Powers counts as power_value (future damage or HP) in the balanced mode and as a
    tie-break in the safe mode."""
    if mode == "safe":
        key = lambda o: (not o["all_dead"], o.get("dies", False), o["potions"] if o["all_dead"] else 0,  # noqa: E731
                         o["hp_lost"] + potion_cost * o["potions"] - o.get("sandpit_bonus", 0) + o.get("hex_loss", 0), o.get("hive_cards", 0),
                         -o.get("powers", 0), -o["kills"],
                         -o["dealt"], o["draws"] == 0)
    else:
        key = lambda o: (not o["all_dead"], o.get("dies", False), o["potions"] if o["all_dead"] else 0,  # noqa: E731
                         -(o["dealt"] + o.get("doom_dealt", 0) + o.get("sandpit_bonus", 0) + o.get("stun_bonus", 0) - o.get("hex_loss", 0)
                           - o["hp_lost"] - potion_cost * o["potions"]
                           + power_value * o.get("powers", 0) - HIVE_COST * o.get("hive_cards", 0)
                           + SLIPPERY_VALUE * o.get("slippery_stripped", 0)),
                         o["hp_lost"], -o["kills"])
    seen, out = set(), []
    for o in sorted(results, key=key):
        sig = tuple(sorted(o["plays"]))
        if sig not in seen:
            seen.add(sig)
            out.append(o)
    return out


# ------------------------------------------------------------------------------------------------ inputs
def _list(x):
    """x if it is a list, else []: live states may carry nulls or wrong types where a list is documented."""
    return x if isinstance(x, list) else []


def _dicts(x):
    """The dict items of x when x is a list (other items skipped), else []."""
    return [i for i in _list(x) if isinstance(i, dict)]


def from_state(st):
    st = st.get("data", st)
    c = st.get("combat") or {}
    p = c.get("player") or {}
    powers = {(x.get("power_id") or x.get("id") or x.get("name") or "").upper(): x.get("amount", x.get("stacks", 1))
              for x in _dicts(p.get("powers"))}
    osty = sum(int(x.get("current_hp") or 0) for x in _dicts(p.get("pets")) if (x.get("pet_id") or "").upper() == "OSTY")
    player = Player(energy=int(p.get("energy") or 0), block=int(p.get("block") or 0), osty_hp=osty,
                    strength=int(powers.get("STRENGTH_POWER", powers.get("STRENGTH", 0)) or 0),
                    dexterity=int(powers.get("DEXTERITY_POWER", powers.get("DEXTERITY", 0)) or 0),
                    weak=any(k.startswith("WEAK") for k in powers), frail=any(k.startswith("FRAIL") for k in powers),
                    hp=p.get("current_hp"), fnp=int(powers.get("FEEL_NO_PAIN_POWER", powers.get("FEEL_NO_PAIN", 0)) or 0),
                    sandpit=int(powers.get("SANDPIT_POWER", powers.get("SANDPIT", 0)) or 0),
                    end_turn_dmg=int(powers.get("DISINTEGRATION_POWER", powers.get("DISINTEGRATION", 0)) or 0),
                    max_hp=p.get("max_hp"), tender=1 if any(k.startswith("TENDER") for k in powers) else 0,
                    colossus=any(k.startswith("COLOSSUS") for k in powers), hexed=any(k.startswith("HEX") for k in powers),
                    shrunk=any(k.startswith("SHRINK") for k in powers),
                    doom=int(powers.get("DOOM_POWER", powers.get("DOOM", 0)) or 0))
    # Card limits: Sloth (at most N cards a turn; cards already played this turn are not in the state, so this assumes
    # none) and Ringing (Ceremonial Beast's Beast Cry: one card this turn [COMMUNITY])
    limits = [int(powers[k] or 3) for k in powers if k.startswith("SLOTH")] + [1 for k in powers if k.startswith("RINGING")]
    if limits:
        player.max_cards = min(limits)
    hand = []
    for h in _dicts(c.get("hand")):
        live = {d["name"]: d.get("current_value") for d in _dicts(h.get("dynamic_values")) if d.get("current_value") is not None}
        cost = int(h.get("energy_cost") or 0)
        idx = h.get("index")
        hand.append(card_from_extract(int(idx) if isinstance(idx, (int, float)) else len(hand), str(h.get("card_id") or "?"), live or None, cost,
                                      bool(h.get("playable", True))))
        if h.get("costs_x"):
            hand[-1].x_cost = True
    enemies = []
    for e in _dicts(c.get("enemies")):
        if not e.get("is_alive", True):
            continue
        pw = {(x.get("power_id") or x.get("id") or x.get("name") or "").upper(): x.get("amount", x.get("stacks", 1))
              for x in _dicts(e.get("powers"))}
        att = [i for i in _dicts(e.get("intents")) if i.get("damage") is not None]
        dmg = sum(int(i["damage"]) for i in att[:1])
        hits = sum(int(i.get("hits") or 1) for i in att[:1])
        raw = e.get("index", len(enemies))  # an int (STS2-Agent) or an entity_id string (STS2MCP via mcp_adapter)
        enemies.append(Enemy(len(enemies), e.get("name") or e.get("enemy_id"), int(e.get("current_hp") or 0),
                             int(e.get("block") or 0), dmg, hits,
                             vuln=any(k.startswith("VULNERABLE") for k in pw), weak=any(k.startswith("WEAK") for k in pw),
                             slippery=int(next((v for k, v in pw.items() if k.startswith("SLIPPERY")), 0) or 0),
                             intangible=any(k.startswith("INTANGIBLE") for k in pw), slow=any(k.startswith("SLOW") for k in pw),
                             ref=raw, hive=int(next((v for k, v in pw.items() if k.startswith("PERSONAL_HIVE")), 0) or 0),
                             enrage=int(next((v for k, v in pw.items() if k.startswith("ENRAGE")), 0) or 0),
                             hp_cap=next((int(v) for k, v in pw.items() if k.startswith("HARDENED_SHELL") and v is not None), None),
                             thorns=int(next((v for k, v in pw.items() if k.startswith("THORNS")), 0) or 0),
                             artifact=int(next((v for k, v in pw.items() if k.startswith("ARTIFACT")), 0) or 0),
                             hit_cap=next((int(v) for k, v in pw.items() if k.startswith("HARD_TO_KILL") and v is not None), None),
                             shriek=int(next((v for k, v in pw.items() if k.startswith("SHRIEK")), 0) or 0),
                             taint=int(next((v for k, v in pw.items() if k.startswith("VITAL_SPARK")), 0) or 0),
                             skittish=int(next((v for k, v in pw.items() if k.startswith("SKITTISH")), 0) or 0),
                             infested=any(k.startswith("INFESTED") for k in pw), ravenous=any(k.startswith("RAVENOUS") for k in pw),
                             imbalanced=any(k.startswith("IMBALANCED") for k in pw),
                             flutter=int(next((v for k, v in pw.items() if k.startswith("FLUTTER")), 0) or 0),
                             burrowed=any(k.startswith("BURROWED") for k in pw),
                             crab_rage=any(k.startswith("CRAB_RAGE") for k in pw),
                             minion=any(k.startswith("MINION") for k in pw),
                             doom=int(next((v for k, v in pw.items() if k.startswith("DOOM")), 0) or 0),
                             paper_cuts=int(next((v for k, v in pw.items() if k.startswith("PAPER_CUTS")), 0) or 0)))
    for i, e in enumerate(enemies):
        e.index = i  # internal position; e.ref keeps the mod's index or entity_id for the action
    run = st.get("run") or {}
    for slot, pot in enumerate(_list(run.get("potions"))):
        if isinstance(pot, dict) and pot.get("occupied") and isinstance(pot.get("potion_id"), str):
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
        elif f == "slow":
            e.slow = True
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
        + (f" · spends {o['potions']} potion(s)" if o.get("potions") else "") \
        + (f" · {o['powers']} energy on Powers" if o.get("powers") else "") \
        + (f" · Doom kills {o['doomed']} after its attack" if o.get("doomed") else "")
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
    ap.add_argument("--osty", type=int, default=0, help="Necrobinder: Osty's current HP")
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--potion", action="append", default=[], help="potion id held, e.g. FIRE_POTION (repeatable)")
    ap.add_argument("--fight", choices=list(POTION_COST), default="elite",
                    help="hallway, elite or boss: sets the cost of spending a potion and the value of playing a Power")
    args = ap.parse_args(argv)
    if args.state:
        hand, player, enemies = from_state(json.loads(Path(args.state).read_text()))
    else:
        hand = [card_from_extract(i, resolve_card(n)) for i, n in enumerate(args.hand or [])]
        player = Player(args.energy, args.player_block, args.strength, args.dexterity, args.player_weak, args.player_frail, args.hp,
                        osty_hp=args.osty)
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
        for o in rank(res, mode, POTION_COST[args.fight], POWER_VALUE[args.fight])[:args.top]:
            print("  " + fmt(o, player.hp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
