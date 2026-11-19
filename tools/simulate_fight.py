#!/usr/bin/env python3
"""Monte Carlo boss-fight simulator: play a deck against a boss's documented move cycle, choosing each turn's plays
with tools/plan_turn.py (boss weights), and report HP lost, death rate and fight length over many shuffles.

Use it to compare draft options against a specific boss (for example: does Twin Strike or Shrug It Off do more
against Vantom?). It is a model, not the game: [HYPOTHESIS] results, useful for relative comparisons.

Modelled across turns: draw 5 (reshuffle), 3 energy, block resets, Strength (Inflame, persistent) and Demon Form
(+Strength each turn), Vulnerable and Weak durations on the boss, Slippery stacks, the boss's Strength gains and
status cards (Vantom's Wounds), exhaust, Anger's copy, draw cards (re-plan after drawing with the energy left).
Not modelled: relics, potions, other powers' effects, upgrades, card-specific conditions.

Bosses: VANTOM (cycle from knowledge/bosses/VANTOM_BOSS.md: Ink Blot 7, Inky Lance 6x2, Dismember 27 + 3 Wounds,
Prepare +2 Strength; 173 HP; 9 Slippery); LAGAVULIN_MATRIARCH (asleep 3 turns behind 12 Plating, wakes stunned when
damaged; Slash 19, Slash 2 12 + 12 block, Disembowel 9x2, Soul Siphon); CEREMONIAL_BEAST (Stamp, Plow 18 + 2 Strength
until 150 HP lost, stun, then Beast Cry, Stomp 15, Crush 17 + 3 Strength); SOUL_FYSH (Beckon, De-Gas 16, Gaze 7,
Fade, Scream 13 + 3 Vulnerable; held Beckons cost 6 HP); WATERFALL_GIANT (Pressurize, Stomp 15 + Weak, Ram 10, Siphon,
Pressure Gun 20 (+5 a use), Pressure Up 13, +3 Steam Eruption a move; stun at 0 HP, then the explosion); KNOWLEDGE_DEMON, ENTOMANCER, BYRDONIS. Cycles other than
Vantom's are [HYPOTHESIS]: declaration order in the extract plus community notes (see each move function).

Usage: python3 -I tools/simulate_fight.py --deck STRIKE_IRONCLAD:5 DEFEND_IRONCLAD:4 BASH [--vs TWIN_STRIKE ANGER] \\
           [--boss VANTOM] [--hp 60] [--max-hp 80] [--runs 300]
  --vs adds alternative card sets: each set is added to the base deck and compared.
"""
import argparse
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calc  # noqa: E402
import plan_turn as pt  # noqa: E402
from draft import expand_deck  # noqa: E402

def _move(kind="attack", dmg=0, hits=1, status=0, boss_block=0, boss_str=0, p_str=0, p_dex=0, heal=0, ringing=False,
          status_draw=0, p_vuln=0, p_weak=0, intangible=0, p_frail=0):
    return {"kind": kind, "dmg": dmg, "hits": hits, "status": status, "boss_block": boss_block, "boss_str": boss_str,
            "p_str": p_str, "p_dex": p_dex, "heal": heal, "ringing": ringing, "status_draw": status_draw, "p_vuln": p_vuln,
            "p_weak": p_weak, "intangible": intangible, "p_frail": p_frail}


def vantom_move(b, turn):
    cycle = [_move(dmg=7), _move(dmg=6, hits=2), _move(dmg=27, status=3), _move("buff", boss_str=2)]
    return cycle[(turn - 1) % 4]


def lagavulin_move(b, turn):
    """Asleep 3 turns behind 12 Plating unless damaged (then it wakes stunned); then Slash 19, Slash 2 12 + 12 block,
    Disembowel 9x2, Soul Siphon (-2 Strength and -2 Dexterity on you, +2 Strength for it). [COMMUNITY] cycle,
    declaration order in the extract."""
    if b.get("stunned"):
        b["stunned"] = False
        return _move("stun")
    if b.get("asleep", 0) > 0:
        b["asleep"] -= 1
        return _move("sleep")
    i = b.get("cycle", 0)
    b["cycle"] = i + 1
    return [_move(dmg=19), _move(dmg=12, boss_block=12), _move(dmg=9, hits=2), _move("debuff", boss_str=2, p_str=-2, p_dex=-2)][i % 4]


def lagavulin_damaged(b, lost):
    if lost > 0 and b.get("asleep", 0) > 0:
        b["asleep"] = 0
        b["stunned"] = True
        b["plating"] = 0


def beast_move(b, turn):
    """Stamp (Plow 150) on turn 1; Plow 18 + 2 Strength each turn until its HP drops to 150 (community guides; the first
    model used 150 damage taken and failed calibration), then a stun turn with its Strength removed; then Beast Cry
    (Ringing: you may play one card next turn), Stomp 15, Crush 17 + 3 Strength. Order `[HYPOTHESIS]`."""
    if turn == 1:
        b["plow"] = 150
        return _move("buff")
    if b.get("stunned"):
        b["stunned"] = False
        return _move("stun")
    if b.get("plow", 0) > 0:
        return _move(dmg=18, boss_str=2)
    i = b.get("cycle", 0)
    b["cycle"] = i + 1
    return [_move("debuff", ringing=True), _move(dmg=15), _move(dmg=17, boss_str=3)][i % 3]


def beast_damaged(b, lost):
    if b.get("plow", 0) > 0 and b["hp"] <= b["plow"]:  # Plow 150 = the HP at which it triggers
        b["plow"] = 0
        b["stunned"] = True
        b["strength"] = 0


CURSE_OFFERS = ("MIND_ROT", "SLOTH", "WASTE_AWAY")  # each offer is Disintegration or this card (one guide, 2026-03-24)


def demon_move(b, turn):
    """Knowledge Demon (379 HP): Curse of Knowledge, Slap 17, Knowledge Overwhelming 8x3, Ponder 11 + heal 30 + 2 Strength,
    three times; then Slap, Knowledge Overwhelming, Ponder repeating. Two guides agree on the moves and numbers. Each
    Curse of Knowledge offers Disintegration (6, 7, then 8 damage at the end of each of your turns; the power's amounts
    add up) or Mind Rot, then Sloth, then Waste Away. The strategy b['curse'] is a 3-tuple of picks, one per offer
    (or one card name taken whenever possible, the older pure strategies)."""
    if turn <= 12:
        i = (turn - 1) % 4
        if i == 0:
            b["curses"] = b.get("curses", 0) + 1
            return _move("curse")
        return [None, _move(dmg=17), _move(dmg=8, hits=3), _move(dmg=11, boss_str=2, heal=30)][i]
    return [_move(dmg=17), _move(dmg=8, hits=3), _move(dmg=11, boss_str=2, heal=30)][(turn - 13) % 3]


def entomancer_move(b, turn):
    """Entomancer (elite, 145 HP): Beeeees! 3x7, Spear! 18, Pheromone Spit (+1 Personal Hive and +1 Strength; +2 Strength
    instead once Personal Hive is at 3), repeating; Personal Hive starts at 1 and adds that many Dazed to your draw pile
    per attack hit (slaythespire.wiki.gg page, v0.111.1 history) `[COMMUNITY]`. The first model used the extract's
    declaration order with +3 Strength and failed badly."""
    i = (turn - 1) % 3
    if i == 2:
        hive = b.get("hive", 1)
        if hive >= 3:
            return _move("buff", boss_str=2)
        b["hive"] = hive + 1
        return _move("buff", boss_str=1)
    return [_move(dmg=3, hits=7), _move(dmg=18)][i]


def byrdonis_move(b, turn):
    """Byrdonis (elite, 91 HP): Peck 3x3 and Swoop 16 alternating; Territorial: +1 Strength at the end of each of its
    turns. Order and Territorial amount are [HYPOTHESIS] (the extract lists the two moves and the power only)."""
    m = _move(dmg=3, hits=3, boss_str=1) if turn % 2 == 1 else _move(dmg=16, boss_str=1)
    return m


def fysh_move(b, turn):
    """Soul Fysh (211 HP): Beckon (a Beckon into your draw pile and one into your discard pile), De-Gas 16, Gaze 7 + a
    Beckon into your discard pile, Fade (Intangible for your next turn), Scream 13 + 3 Vulnerable on you, repeating.
    Order: two community guides agree (turn 4 Intangible, turn 5 Vulnerable); Scream 13 is the v0.107.1 value; the card
    Gaze adds is assumed to be a Beckon; Intangible 2 is modelled as lasting your next turn (the power ticks down at
    every turn end, and the guides say "for one turn") `[HYPOTHESIS]`."""
    return [_move("status", status=1, status_draw=1), _move(dmg=16), _move(dmg=7, status=1), _move("buff", intangible=1),
            _move(dmg=13, p_vuln=3)][(turn - 1) % 5]


def giant_move(b, turn):
    """Waterfall Giant (250 HP): Pressurize (+15 Steam Eruption) on turn 1, then Stomp 15 + Weak, Ram 10, Siphon (heal
    10), Pressure Gun 20 (+5 each use), Pressure Up 13, repeating, each +3 Steam Eruption. At 0 HP it is stunned for its
    next turn, then explodes for its Steam Eruption while invulnerable (Weak on it lowers the explosion); surviving that
    wins. Cycle: one guide (selphie1999gaming, 2026-04-05; an earlier guide gave the first three moves); heal 10 is the
    lower-ascension value since v0.107.1 (the guide says 15) `[COMMUNITY]` / `[HYPOTHESIS]`."""
    if b.get("exploding") == 2:
        return _move(dmg=b.get("steam", 0))
    if turn == 1:
        return dict(_move("buff"), steam=15)  # Steam is added when the move happens (not if it dies first)
    i = (turn - 2) % 5
    if i == 3:
        gun = b.get("gun", 0)
        b["gun"] = gun + 1
        return dict(_move(dmg=20 + 5 * gun), steam=3)
    return dict([_move(dmg=15, p_weak=1), _move(dmg=10), _move("buff", heal=10), None, _move(dmg=13)][i], steam=3)


def insatiable_move(b, turn):
    """The Insatiable (321 HP): Liquify Ground on turn 1 (4 Sandpit on you; 6 Frantic Escape, 3 into the draw pile and 3
    into the discard pile), then Thrash 8x2, Lunging Bite 28, Salivate +2 Strength, Thrash 8x2, repeating
    (slaythespire.wiki.gg page) `[COMMUNITY]`. Sandpit ticks down at the start of your turn and kills you at 0; each Frantic
    Escape adds 1 and costs 1 more each play (guides)."""
    if turn == 1:
        return dict(_move("status", status=3, status_draw=3), sandpit=4)
    return [_move(dmg=8, hits=2), _move(dmg=28), _move("buff", boss_str=2), _move(dmg=8, hits=2)][(turn - 2) % 4]


def kin_priest_move(b, turn):
    """Kin Priest (190 HP): Orb of Frailty 8 + Frail, Orb of Weakness 8 + Weak, Beam 3x3, Ritual +2 Strength, repeating, in
    the extract's declaration order `[HYPOTHESIS]`."""
    return [_move(dmg=8, p_frail=1), _move(dmg=8, p_weak=1), _move(dmg=3, hits=3), _move("buff", boss_str=2)][(turn - 1) % 4]


def kin_follower_move(a, turn):
    """Kin Follower (58 HP, Minion): Quick Slash 5, Boomerang 2x2, Power Dance +2 Strength, repeating `[HYPOTHESIS]` order."""
    return [_move(dmg=5), _move(dmg=2, hits=2), _move("buff", boss_str=2)][(turn - 1) % 3]


BOSSES = {
    # validated: the model's win rate relative to Vantom roughly matches the Player's record (see report()).
    "VANTOM": {"hp": 173, "slippery": 9, "move": vantom_move, "status_card": "WOUND", "validated": True},
    "LAGAVULIN_MATRIARCH": {"hp": 222, "asleep": 3, "plating": 12, "move": lagavulin_move, "on_damage": lagavulin_damaged,
                            "validated": True},
    "CEREMONIAL_BEAST": {"hp": 252, "move": beast_move, "on_damage": beast_damaged, "validated": False},  # fails calibration
    "KNOWLEDGE_DEMON": {"hp": 379, "move": demon_move, "validated": False, "act": 2},  # calibration in report()
    # Entomancer fails calibration badly (every deck loses by turn 5): the extract's Strength gains and Bees 3x7 cannot all
    # apply from turn 1 in this order; probably ascension-dependent values or another order. Not used; see gap 26.
    # Entomancer with the wiki's cycle: 52% from 60/80 with the Act 2 deck against the Player's 10/13, the same ratio as
    # Vantom's (31% against 4/10); the first model (Spit first, +3 Strength) failed badly.
    "ENTOMANCER": {"hp": 145, "hive": 1, "move": entomancer_move, "validated": True, "encounter": "ENTOMANCER_ELITE", "act": 2},
    # Byrdonis: the 15-card base deck loses about 26-29 HP here, the Player's Ironclad decks lost 25.8 on average.
    "BYRDONIS": {"hp": 91, "move": byrdonis_move, "validated": True, "encounter": "BYRDONIS_ELITE"},
    # Soul Fysh: the model's win rate (about 50% from 60/80 with the base deck) sits close to the Player's 4/7; a small
    # sample, so this only rules out gross errors. Waterfall Giant with the full five-move cycle: 14% from 60/80 against
    # the Player's 3/5, three times too hard relative to Vantom, so not used in drafting (its plan-mode result, safe far
    # ahead of balanced, held under both the three- and five-move cycles). With the Player's own decks both remove a
    # similar share of the boss's HP (about 0.5), well above Vantom (0.26), as the real outcomes suggest.
    "SOUL_FYSH": {"hp": 211, "move": fysh_move, "status_card": "BECKON", "validated": True},
    "WATERFALL_GIANT": {"hp": 250, "move": giant_move, "explodes": True, "validated": False},
    # The Kin: the Priest with two Minion followers; killing the Priest ends the fight (two guides). Cycles [HYPOTHESIS].
    # The Insatiable: cycle and Sandpit from the wiki page; calibration in report()
    "THE_INSATIABLE": {"hp": 321, "move": insatiable_move, "status_card": "FRANTIC_ESCAPE", "validated": False, "act": 2},
    "THE_KIN": {"hp": 190, "move": kin_priest_move, "validated": False, "encounter": "THE_KIN_BOSS",
                "adds": [{"name": "KIN_FOLLOWER", "hp": 58, "move": kin_follower_move, "minion": True}] * 2},
}


MODELLED_POWERS = {"DEMON_FORM", "PYRE", "FEEL_NO_PAIN"}  # plus any Power that gives Strength or Dexterity when played


def models_card(card_id):
    """True if the simulator can see what the card does. For other cards a simulated value only measures a dead card
    (unmodelled Powers such as Hellraiser or Stampede, cards whose numbers the extract shows as ?), so drafting skips it."""
    c = pt.card_from_extract(0, card_id)
    rec = pt.CARDS.get(c.card_id) or {}
    if not rec or rec.get("type") in ("Status", "Curse"):
        return False
    if c.power:
        return c.card_id in MODELLED_POWERS or bool(c.strength or c.dex)
    special = pt.BLOCK_DAMAGE | pt.EXHAUST_HAND | pt.HITS_TWICE_IF_VULNERABLE
    if "?" in (rec.get("effect") or "") and c.card_id not in special:
        return False
    return bool(c.dmg or c.block or c.vuln or c.weak or c.strength or c.energy or c.draw or c.temp_str or c.rage
                or c.free_attacks or c.str_down or c.retaliate or c.card_id in special)


def draw_cards(n, draw, discard, rng):
    out = []
    for _ in range(n):
        if not draw:
            if not discard:
                break
            draw.extend(discard)
            discard.clear()
            rng.shuffle(draw)
        out.append(draw.pop())
    return out


BEST_CURSES = ("MIND_ROT", "SLOTH", "WASTE_AWAY")  # Knowledge Demon: the best combination in report(); the default


SIM_RELICS = {"VAJRA", "ODDLY_SMOOTH_STONE", "ANCHOR", "BAG_OF_PREPARATION", "RED_MASK", "GORGET", "BLOOD_VIAL",
              "FESTIVE_POPPER", "HAPPY_FLOWER", "LIZARD_TAIL", "RED_SKULL"}  # relics the simulator applies (see run_fight)


POTION_SLOT = 100  # potion cards get index POTION_SLOT + n, apart from hand positions
TEMPORARY_POTIONS = {"FLEX_POTION", "SPEED_POTION"}  # their Strength or Dexterity lasts only the turn


def run_fight(deck, boss="VANTOM", hp=80, max_hp=80, seed=0, mode="balanced", max_turns=25, curse=BEST_CURSES, relics=(),
              potions=(), focus_boss=False):
    """relics: relic IDs held; those in SIM_RELICS are applied with their plainest reading of the game data
    [GAME-EXTRACT] + [HYPOTHESIS] (once per fight unless the data says otherwise): Vajra +1 Strength, Oddly Smooth Stone +1
    Dexterity, Anchor 10 Block on turn 1, Bag of Preparation +2 cards on turn 1, Red Mask 1 Weak on the boss at the start,
    Gorget 4 Plating (Block each turn, one less each turn), Blood Vial heal 2 at the start, Festive Popper 9 damage at the
    start, Happy Flower +1 energy every third turn, Lizard Tail revives once at half HP, Red Skull +3 Strength at half HP
    or less. potions: potion IDs held; the planner may use each once (boss potion cost) [HYPOTHESIS]. Bosses with adds
    (spec "adds"): the planner targets as it likes, or every single-target card goes to the boss when focus_boss."""
    spec = BOSSES[boss]
    pots = [str(x).split(".", 1)[-1].upper() for x in potions or () if x]
    R = {str(r).split(".", 1)[-1].upper() for r in relics or ()}
    rng = random.Random(seed)
    draw = [c.split(".", 1)[-1] for c in deck]
    rng.shuffle(draw)
    discard, exhausted = [], []
    strength, demon, dexterity = int("VAJRA" in R), 0, int("ODDLY_SMOOTH_STONE" in R)
    pyre = fnp = 0  # Pyre: +1 energy each turn; Feel No Pain: Block per exhaust (both persist)
    plating_p, lizard = (4 if "GORGET" in R else 0), "LIZARD_TAIL" in R
    if "BLOOD_VIAL" in R:
        hp = min(max_hp, hp + 2)
    # Necrobinder: Bound Phylactery summons 1 at combat start and each turn; Osty absorbs unblocked damage. NOT VALIDATED:
    # a 14-card Necrobinder deck wins 0% against Lagavulin here while the Player survived 15 of 15, so the Osty rules
    # are incomplete (Unleash's damage, revival, what the redirect really covers). Do not use Necrobinder results yet.
    necro = any("NECROBINDER" in c.upper() for c in deck)
    osty = 0
    b = {"hp": spec["hp"], "block": 0, "slippery": spec.get("slippery", 0), "strength": 0, "vuln": 0, "weak": 0,
         "asleep": spec.get("asleep", 0), "plating": spec.get("plating", 0), "curse": curse, "hive": spec.get("hive", 0)}
    sloth = mind_rot = waste = disint = 0
    p_vuln = p_weak = p_frail = 0
    sandpit, fe_played = 0, 0  # The Insatiable's Sandpit on you, Frantic Escapes played (each costs 1 more)
    adds = [{"name": a["name"], "hp": a["hp"], "max": a["hp"], "block": 0, "strength": 0, "vuln": 0, "weak": 0,
             "minion": a.get("minion", False), "move": a["move"], "mv": None} for a in spec.get("adds", [])]
    ringing = False
    if "RED_MASK" in R:
        b["weak"] = 1
    if "FESTIVE_POPPER" in R:
        b["hp"] -= 9

    def survives():
        """False if the run ends; Lizard Tail turns the first death into half HP."""
        nonlocal hp, lizard
        if hp > 0:
            return True
        if lizard:
            lizard, hp = False, max_hp // 2
            return True
        return False
    for turn in range(1, max_turns + 1):
        strength += demon
        if sandpit:  # ticks down at the start of your turn; at 0 you are eaten (no relic saves you)
            sandpit -= 1
            if sandpit <= 0:
                return {"won": False, "hp": 0, "turns": turn, "boss_left": max(0.0, b["hp"] / spec["hp"]), "eaten": True}
        if necro:
            osty += 2 if turn == 1 else 1  # combat start + turn start
        if b.get("asleep", 0) > 0 and b.get("plating"):
            b["block"] = b["plating"]
        mv = spec["move"](b, turn)
        exploding = b.get("exploding") == 2  # Waterfall Giant: invulnerable, its explosion is the only threat
        intent = (mv["dmg"] + (0 if exploding else b["strength"]), mv["hits"]) if mv["kind"] == "attack" else (0, 0)
        raw_intent = intent
        if intent[1] and (b["weak"] > 0 or p_vuln > 0):  # like the game, the shown intent includes Weak and your Vulnerable
            intent = (calc.hit_damage(intent[0], attacker_weak=b["weak"] > 0, target_vulnerable=p_vuln > 0), intent[1])
        for a in adds:  # each add's move and the intent the game would show
            a["mv"] = a["move"](a, turn) if a["hp"] > 0 else _move("dead", hits=0)
            m_ = a["mv"]
            a["intent"] = ((m_["dmg"] + a["strength"], m_["hits"]) if m_["kind"] == "attack" else (0, 0))
            if a["intent"][1] and (a["weak"] > 0 or p_vuln > 0):
                a["intent"] = (calc.hit_damage(a["intent"][0], attacker_weak=a["weak"] > 0, target_vulnerable=p_vuln > 0), a["intent"][1])
        hand_ids = draw_cards(max(1, 5 - mind_rot) + (2 if turn == 1 and "BAG_OF_PREPARATION" in R else 0), draw, discard, rng)
        energy = max(1, 3 + pyre - waste) + (1 if "HAPPY_FLOWER" in R and turn % 3 == 0 else 0)
        block = (10 if turn == 1 and "ANCHOR" in R else 0) + plating_p
        gained_this_turn = 3 if "RED_SKULL" in R and hp <= max_hp // 2 else 0  # Red Skull, recounted each turn
        cards_played = 0
        for _ in range(4):  # plan, play up to a draw, re-plan with what is left
            hand = [pt.card_from_extract(i, cid) for i, cid in enumerate(hand_ids)]
            for c in hand:
                if c.sandpit_add:  # Frantic Escape: 1 more energy for each one already played
                    c.cost = 1 + fe_played
            hand += [pt.card_from_potion(POTION_SLOT + n, pid) for n, pid in enumerate(pots)]
            for c in hand:  # Powers whose effect the simulator does not model earn no future value here (else the
                if c.power and c.card_id not in MODELLED_POWERS and not c.strength and not c.dex:  # planner wastes turns)
                    c.power = False
            enemy = pt.Enemy(0, boss, 999 if exploding else b["hp"], b["block"], intent[0], intent[1], vuln=b["vuln"] > 0,
                             weak=b["weak"] > 0, slippery=b["slippery"], hive=b.get("hive", 0), intangible=b.get("intangible", 0) > 0)
            player = pt.Player(energy=energy, block=block, strength=strength + gained_this_turn, dexterity=dexterity, weak=p_weak > 0, fnp=fnp,
                               frail=p_frail > 0, sandpit=sandpit,
                               max_cards=(1 - cards_played) if ringing else ((3 - cards_played) if sloth else None), hp=hp, osty_hp=osty)
            foes = [enemy] + [pt.Enemy(k + 1, a["name"], max(0, a["hp"]), a["block"], a["intent"][0], a["intent"][1], vuln=a["vuln"] > 0,
                                       weak=a["weak"] > 0, minion=a["minion"]) for k, a in enumerate(adds)]
            res = pt.plans(hand, player, foes)
            if not res:
                break
            turn_mode = mode
            if mode.startswith("hybrid:"):  # safe below the HP fraction, balanced above
                turn_mode = "safe" if hp < float(mode.split(":")[1]) * max_hp else "balanced"
            if exploding:
                turn_mode = "safe"
            best = pt.rank(res, turn_mode, pt.POTION_COST["boss"], pt.POWER_VALUE["boss"])[0]
            seq = best["seq"]
            cut = next((i + 1 for i, (c, _) in enumerate(seq) if c.draw), len(seq))
            order = [c for c, _ in seq[:cut]]
            if not order:
                break
            if adds and not focus_boss:
                targets = [t_ for _, t_ in seq[:cut]]  # the planner's own targets
            else:
                targets = [0 if c.target == "AnyEnemy" else None for c in order]
            out = pt.simulate(order, targets, player, foes)
            if out is None:
                break
            ea = out["enemies_after"][0]
            if exploding:
                ea = dict(ea, hp=0)
            lost = b["hp"] - ea["hp"]
            for _ in range(out.get("hive_cards", 0)):  # Personal Hive: Dazed (Ethereal, Unplayable) into the draw pile
                draw.insert(rng.randrange(len(draw) + 1), "DAZED")
            b["hp"], b["block"], b["slippery"] = ea["hp"], ea["block"], ea["slippery"]
            if spec.get("on_damage"):
                spec["on_damage"](b, lost)
            for k, a in enumerate(adds):
                eak = out["enemies_after"][k + 1]
                a["hp"], a["block"] = eak["hp"], eak["block"]
            for c, t_ in zip(order, targets):
                hit_all = c.target == "AllEnemies"
                for k, st_ in enumerate([b] + adds):
                    if hit_all or t_ == k:
                        if c.vuln:
                            st_["vuln"] = max(st_["vuln"], c.vuln)
                        if c.weak:
                            st_["weak"] = max(st_["weak"], c.weak)
            energy, block = out["energy_left"], out["block"]
            osty = out.get("osty_before_enemy", osty)
            cards_played += sum(1 for c in order if not c.potion)
            hp -= sum(c.hp_cost for c in order)
            names = {c.index: hand_ids[c.index] for c in order if not c.potion}  # hand entries played (keeps the '+')
            hand_ids = [x for i, x in enumerate(hand_ids) if i not in names]
            used = {c.index - POTION_SLOT for c in order if c.potion}
            for c in order:
                if c.potion:
                    if c.heal_pct:  # Blood Potion
                        hp = min(max_hp, hp + max_hp * c.heal_pct // 100)
                    if c.card_id not in TEMPORARY_POTIONS:
                        strength += c.strength
                        dexterity += c.dex
                    continue
            pots = [x for n, x in enumerate(pots) if n not in used]
            escapes = sum(1 for c in order if c.sandpit_add)
            sandpit += escapes
            fe_played += escapes
            for c in order:
                if c.potion:
                    continue
                gained_this_turn += c.strength
                name = names[c.index]
                rec = pt.CARDS.get(c.card_id) or {}
                if c.strength:  # "Gain N Strength" lasts the fight (Inflame, Fight Me, Brand); Setup Strike's is temp_str
                    strength += c.strength
                    gained_this_turn -= c.strength
                gained_this_turn += c.temp_str
                if c.power:
                    if c.card_id == "DEMON_FORM":
                        demon += 3
                    pyre += c.card_id == "PYRE"
                    fnp += c.fnp
                elif "Exhaust" in (rec.get("effect") or ""):
                    exhausted.append(name)
                else:
                    discard.append(name)
                if c.card_id == "ANGER":
                    discard.append("ANGER")
            # Exhausts from hand, after the planned cards have left it: Fiend Fire takes the rest of the hand; True Grit,
            # Burning Pact, Second Wind... take a status or curse if one is held (Beckon first), else a Strike or Defend
            # (True Grit's random pick is approximated the same way) [HYPOTHESIS]
            for c in order:
                rec = pt.CARDS.get(c.card_id) or {}
                if c.card_id in pt.EXHAUST_HAND:
                    exhausted.extend(hand_ids)
                    hand_ids.clear()
                elif "exhaust-other" in (rec.get("tags") or []) and hand_ids:
                    junk = sorted((x for x in hand_ids if (pt.CARDS.get(x) or {}).get("type") in ("Status", "Curse")),
                                  key=lambda x: x != "BECKON")
                    basic = [x for x in hand_ids if x.startswith(("STRIKE", "DEFEND"))]
                    pick = (junk or basic or [None])[0]
                    if pick:
                        hand_ids.remove(pick)
                        exhausted.append(pick)  # (Feel No Pain's Block for it is already in the planner's result)
            if b["hp"] <= 0 and not spec.get("explodes") and all(a["minion"] or a["hp"] <= 0 for a in adds):
                return {"won": True, "hp": hp, "turns": turn, "boss_left": 0.0}
            if b["hp"] <= 0 and not b.get("exploding"):
                b["exploding"] = 1  # stunned on its next turn, explodes on the one after
                break
            if sum(c.draw for c in order) and seq[cut - 1][0].draw:
                hand_ids += draw_cards(sum(c.draw for c in order), draw, discard, rng)
                continue
            break
        hp -= sum(pt.card_from_extract(0, cid).held_loss for cid in hand_ids)  # Beckon: 6 unblockable HP each if held
        ethereal = [x for x in hand_ids if "kw-ethereal" in ((pt.CARDS.get(x.rstrip("+")) or {}).get("tags") or [])]
        exhausted.extend(ethereal)  # Ethereal cards still in hand are exhausted at the end of the turn (Dazed, many Necrobinder cards)
        discard.extend(x for x in hand_ids if x not in ethereal)
        ringing = False
        plating_p = max(0, plating_p - 1)
        if not survives():
            return {"won": False, "hp": 0, "turns": turn, "boss_left": max(0.0, b["hp"] / spec["hp"])}
        b["intangible"] = max(0, b.get("intangible", 0) - 1)
        if b.get("exploding") == 1:  # Waterfall Giant: stunned the turn after it reaches 0 HP
            b["exploding"] = 2
            b["vuln"] = max(0, b["vuln"] - 1)
            b["weak"] = max(0, b["weak"] - 1)
            continue
        # boss turn (adds attack with it; one block pool)
        add_dmg = sum(a["intent"][0] * a["intent"][1] for a in adds if a["hp"] > 0)
        if mv["kind"] == "attack" or add_dmg:
            per = calc.hit_damage(raw_intent[0], attacker_weak=b["weak"] > 0, target_vulnerable=p_vuln > 0) if mv["kind"] == "attack" else 0
            unblocked = max(0, per * (intent[1] if mv["kind"] == "attack" else 0) + add_dmg - block)
            to_osty = min(osty, unblocked)  # Osty takes the unblocked damage first (DIE_FOR_YOU_POWER)
            osty -= to_osty
            hp -= unblocked - to_osty
        for _ in range(mv["status"]):
            discard.append(spec.get("status_card", "WOUND"))
        for _ in range(mv["status_draw"]):
            draw.insert(rng.randrange(len(draw) + 1), spec.get("status_card", "WOUND"))
        if exploding:
            if hp > 0:
                return {"won": True, "hp": hp, "turns": turn, "boss_left": 0.0}
            return {"won": False, "hp": 0, "turns": turn, "boss_left": 0.0}
        p_vuln, p_weak = max(0, p_vuln - 1) + mv["p_vuln"], max(0, p_weak - 1) + mv["p_weak"]
        p_frail = max(0, p_frail - 1) + mv["p_frail"]
        for a in adds:
            if a["hp"] > 0:
                a["strength"] += a["mv"]["boss_str"]
                p_weak += a["mv"]["p_weak"]
            a["vuln"], a["weak"] = max(0, a["vuln"] - 1), max(0, a["weak"] - 1)
        if mv["intangible"]:
            b["intangible"] = mv["intangible"]
        b["steam"] = b.get("steam", 0) + mv.get("steam", 0)
        if mv.get("sandpit"):
            sandpit = mv["sandpit"]
        b["strength"] += mv["boss_str"]
        if mv.get("ringing"):
            ringing = True
        b["hp"] = min(spec["hp"], b["hp"] + mv.get("heal", 0))
        strength += mv["p_str"]
        dexterity += mv["p_dex"]
        if mv["kind"] == "curse":  # the chosen curse stays for the rest of the fight
            k = b.get("curses", 1) - 1
            pick = b["curse"][k] if isinstance(b["curse"], (tuple, list)) else b["curse"]
            if pick == "SLOTH":
                sloth = 1
            elif pick == "MIND_ROT":
                mind_rot += 1
            elif pick == "WASTE_AWAY":
                waste += 1
            elif pick == "DISINTEGRATION":
                disint += 6 + k  # 6, 7, 8 by offer; a Counter power, so taking it twice deals 6 + 7 [GAME-EXTRACT]
        if disint:
            hp -= disint  # at the end of your turn
        if not survives():
            return {"won": False, "hp": 0, "turns": turn, "boss_left": max(0.0, b["hp"] / spec["hp"])}
        b["vuln"] = max(0, b["vuln"] - 1)
        b["weak"] = max(0, b["weak"] - 1)
        b["block"] = mv["boss_block"]
    return {"won": False, "hp": hp, "turns": max_turns, "timeout": True, "boss_left": max(0.0, b["hp"] / spec["hp"])}


def evaluate(deck, boss, hp, max_hp, runs, mode="balanced", curse=BEST_CURSES, relics=(), potions=(), focus_boss=False):
    rs = [run_fight(deck, boss, hp, max_hp, seed=s, mode=mode, curse=curse, relics=relics, potions=potions, focus_boss=focus_boss)
          for s in range(runs)]
    wins = [r for r in rs if r["won"]]
    return {"win_rate": len(wins) / runs, "hp_lost": statistics.mean(hp - r["hp"] for r in rs),
            "hp_lost_wins": statistics.mean(hp - r["hp"] for r in wins) if wins else float("nan"),
            "turns": statistics.median(r["turns"] for r in rs), "timeouts": sum(1 for r in rs if r.get("timeout")),
            "progress": statistics.mean(1 - r.get("boss_left", 0.0) for r in rs)}


def potions_at(con, run_id, floor):
    """Potions held at the start of a floor: picked (non-shop) or bought before it, minus used or discarded before it."""
    held = []
    for r in con.execute("""SELECT floor, kind, source, potion_id, picked FROM potion_events WHERE run_id = ? AND floor < ?
                            ORDER BY floor, CASE kind WHEN 'used' THEN 1 WHEN 'discarded' THEN 1 ELSE 0 END""", (run_id, floor)):
        pid = r["potion_id"]
        if (r["kind"] == "offered" and r["picked"] and r["source"] != "shop") or r["kind"] == "bought":
            held.append(pid)
        elif r["kind"] in ("used", "discarded") and pid in held:
            held.remove(pid)
    return held


def calibrate_real(runs=40, character="IRONCLAD", bosses=None):
    """The Player's own decks on arrival at each modelled fight (v0.107.1, solo, finished runs), simulated from the
    arrival HP with the better of the two plans, the deck's upgrades, the relics in SIM_RELICS and the potions held. Returns {boss: (mean
    simulated win rate, survived, fights, mean share of the boss's HP removed)}. Other relics,
    potions or upgrades, so the model should be pessimistic by a similar amount for every boss."""
    from deck_metrics import deck_at
    from stslib import connect
    con = connect()
    out = {}
    for key in bosses or BOSSES:
        enc = "ENCOUNTER." + BOSSES[key].get("encounter", key + "_BOSS")
        rows = con.execute("""SELECT f.run_id, f.floor, f.hp_before, f.max_hp, (f.is_last_floor AND NOT r.win) AS died
                              FROM floors f JOIN runs r USING(run_id) WHERE r.build_id = 'v0.107.1' AND r.character = ?
                              AND r.n_players = 1 AND NOT r.abandoned AND f.model_id = ?""", (character, enc)).fetchall()
        sims, prog = [], []
        for r in rows:
            deck = deck_at(con, r["run_id"], r["floor"], upgrades=True)
            rel = [x["relic_id"] for x in con.execute("SELECT relic_id FROM relic_events WHERE run_id = ? AND floor < ? AND picked = 1",
                                                      (r["run_id"], r["floor"]))]
            hp, mx = r["hp_before"] or r["max_hp"], r["max_hp"] or 80
            pots = potions_at(con, r["run_id"], r["floor"])
            best = max((evaluate(deck, key, hp, mx, runs, m, relics=rel, potions=pots) for m in ("balanced", "safe")),
                       key=lambda x: (x["win_rate"], x["progress"]))
            sims.append(best["win_rate"])
            prog.append(best["progress"])
        if rows:
            out[key] = (statistics.mean(sims), sum(1 for r in rows if not r["died"]), len(rows), statistics.mean(prog))
    con.close()
    return out


def beast_sensitivity(runs=150):
    """Gap 25: which single Ceremonial Beast assumption, if softer, brings the model near the Player's record (5/6)?
    Each row changes one assumption; base deck from 60/80 HP, the better plan."""
    M = _move

    def make(plow_str=2, ringing=True, stun_turns=1, plow_hp=150, plow_dmg=18, cycle=None):
        cyc = cycle or [M("debuff", ringing=ringing), M(dmg=15), M(dmg=17, boss_str=3)]

        def mv(b, turn):
            if turn == 1:
                b["plow"] = plow_hp
                return M("buff")
            if b.get("stunned"):
                b["stunned"] = b["stunned"] - 1 if b["stunned"] > 1 else 0
                return M("stun")
            if b.get("plow", 0) > 0:
                return M(dmg=plow_dmg, boss_str=plow_str)
            i = b.get("cycle", 0)
            b["cycle"] = i + 1
            return cyc[i % len(cyc)]

        def dmg(b, lost):
            if b.get("plow", 0) > 0 and b["hp"] <= b["plow"]:
                b["plow"], b["stunned"], b["strength"] = 0, stun_turns, 0
        return mv, dmg
    variants = [("current model", {}), ("no Ringing", {"ringing": False}), ("Plow gains no Strength", {"plow_str": 0}),
                ("stun lasts 2 turns", {"stun_turns": 2}), ("Plow triggers at 180 HP", {"plow_hp": 180}),
                ("Plow deals 12", {"plow_dmg": 12}),
                ("after the stun: Stomp, Crush, Beast Cry", {"cycle": [M(dmg=15), M(dmg=17, boss_str=3), M("debuff", ringing=True)]})]
    deck = expand_deck(EXPERIMENT_BASE, "IRONCLAD")
    spec = BOSSES["CEREMONIAL_BEAST"]
    saved = spec["move"], spec["on_damage"]
    out = []
    try:
        for name, kw in variants:
            spec["move"], spec["on_damage"] = make(**kw)
            r = max((evaluate(deck, "CEREMONIAL_BEAST", 60, 80, runs, m) for m in ("balanced", "safe")), key=lambda x: x["win_rate"])
            out.append((name, r["win_rate"], r["turns"]))
    finally:
        spec["move"], spec["on_damage"] = saved
    return out


EXPERIMENT_BASE = ["STRIKE_IRONCLAD:4", "DEFEND_IRONCLAD:4", "BASH", "POMMEL_STRIKE", "SHRUG_IT_OFF", "IRON_WAVE", "UPPERCUT",
                   "ANGER", "INFLAME"]
EXPERIMENT_VARIANTS = [("base deck (15 cards)", []), ("+ Twin Strike, Sword Boomerang (multi-hit)", ["TWIN_STRIKE", "SWORD_BOOMERANG"]),
                       ("+ Pommel Strike, Battle Trance (draw)", ["POMMEL_STRIKE", "BATTLE_TRANCE"]),
                       ("+ Shrug It Off, Flame Barrier (block)", ["SHRUG_IT_OFF", "FLAME_BARRIER"]),
                       ("+ Demon Form, Shrug It Off (scaling)", ["DEMON_FORM", "SHRUG_IT_OFF"]),
                       ("+ Strike x2 (control)", ["STRIKE_IRONCLAD:2"]),
                       ("+ Thunderclap, Breakthrough (single-hit hit-all)", ["THUNDERCLAP", "BREAKTHROUGH"]),
                       ("+ Breakthrough x2 (single-hit hit-all)", ["BREAKTHROUGH:2"])]


def report(runs=300):
    """Fixed Vantom experiment (H6, H2) -> reports/phase2/vantom-simulation.md."""
    from stslib import PROJECT, md_table
    rows, R = [], {}
    for name, add in EXPERIMENT_VARIANTS:
        deck = expand_deck(EXPERIMENT_BASE + add, "IRONCLAD")
        cells = [name]
        for mode in ("balanced", "safe"):
            r = evaluate(deck, "VANTOM", 80, 80, runs, mode)
            R[(name.split(" (")[0], mode)] = r["win_rate"]
            cells += [f"{r['win_rate']:.0%}", f"{r['hp_lost']:.1f}"]
        rows.append(cells)

    def w(key, mode):
        return R[(key, mode)]
    base, multi, demon = "base deck", "+ Twin Strike, Sword Boomerang", "+ Demon Form, Shrug It Off"
    ctrl, brk2, thb = "+ Strike x2", "+ Breakthrough x2", "+ Thunderclap, Breakthrough"
    draw_, block_ = "+ Pommel Strike, Battle Trance", "+ Shrug It Off, Flame Barrier"
    ranked = sorted(((k, w(k, "balanced") + w(k, "safe")) for (k, m) in R if m == "balanced"), key=lambda x: -x[1])
    L = ["# Boss Simulations (Vantom, Knowledge Demon)", "",
         f"Built by `tools/simulate_fight.py --report` ({runs} simulated fights per row and mode, from 80/80 HP). Each turn's plays "
         "are chosen by `tools/plan_turn.py`; Vantom follows its documented cycle (Ink Blot 7, Inky Lance 6x2, Dismember 27 + 3 "
         "Wounds, Prepare +2 Strength; 173 HP; 9 Slippery). Card values are v0.111.1. No relics, potions or upgrades. "
         "`[HYPOTHESIS]`: a model, useful for comparing additions to the same deck, not for absolute win rates.", "",
         md_table(["Base deck + two cards", "Win (balanced)", "HP lost (balanced)", "Win (safe)", "HP lost (safe)"], rows), "",
         "## Reading (computed from the table above; seeds are fixed, so the run reproduces)", "",
         f"- **Best additions** (both plans together): {ranked[0][0].lstrip('+ ')} and {ranked[1][0].lstrip('+ ')}. Multi-hit: "
         f"{w(multi, 'balanced'):.0%} balanced / {w(multi, 'safe'):.0%} safe against the base deck's {w(base, 'balanced'):.0%} / "
         f"{w(base, 'safe'):.0%}; Demon Form with Shrug It Off {w(demon, 'balanced'):.0%} / {w(demon, 'safe'):.0%}.",
         f"- **Two Breakthroughs against two plain Strikes**: {w(brk2, 'balanced'):.0%} against {w(ctrl, 'balanced'):.0%} balanced, "
         f"{w(brk2, 'safe'):.0%} against {w(ctrl, 'safe'):.0%} safe (Breakthrough's 9 is capped to 1 while Slippery lasts, and it "
         f"costs HP). Thunderclap with Breakthrough: {w(thb, 'balanced'):.0%} / {w(thb, 'safe'):.0%}.",
         f"- **Draw and block**: draw {w(draw_, 'balanced'):.0%} / {w(draw_, 'safe'):.0%}, block {w(block_, 'balanced'):.0%} / "
         f"{w(block_, 'safe'):.0%}, against the base {w(base, 'balanced'):.0%} / {w(base, 'safe'):.0%}: their value depends on the plan.",
         "- Plan choice: see the plan-mode section below.", ""]
    kd_deck = expand_deck(["STRIKE_IRONCLAD:2", "DEFEND_IRONCLAD:3", "BASH", "POMMEL_STRIKE", "SHRUG_IT_OFF:2", "UPPERCUT", "ANGER",
                           "INFLAME:2", "TWIN_STRIKE:2", "FLAME_BARRIER", "BATTLE_TRANCE", "BLUDGEON", "DEMON_FORM",
                           "SWORD_BOOMERANG", "IMPERVIOUS", "OFFERING"], "IRONCLAD")
    # Calibration: the experiment's base deck (Act 1 bosses) or the Act 2 deck (Knowledge Demon) at 60/80 HP, the
    # better plan, versus the Player's record
    import sqlite3
    con = sqlite3.connect(PROJECT / "data" / "runs.db")
    cal = []
    for key in BOSSES:
        cal_deck = kd_deck if BOSSES[key].get("act") == 2 else expand_deck(EXPERIMENT_BASE, "IRONCLAD")
        r = max((evaluate(cal_deck, key, 60, 80, runs // 2, m) for m in ("balanced", "safe")), key=lambda x: x["win_rate"])
        s, n = con.execute("""SELECT SUM(NOT (f.is_last_floor AND NOT r.win)), COUNT(*) FROM floors f JOIN runs r USING(run_id)
                              WHERE r.build_id='v0.107.1' AND r.character='IRONCLAD' AND r.n_players=1 AND NOT r.abandoned
                              AND f.model_id = ?""", ["ENCOUNTER." + BOSSES[key].get("encounter", key + "_BOSS")]).fetchone()
        cal.append([key.replace("_", " ").title(), f"{r['win_rate']:.0%}", f"{s}/{n} ({s / n:.0%})" if n else "-",
                    "yes" if BOSSES[key].get("validated") else "**no**"])
    con.close()
    L += ["## Calibration against the Player's record", "",
          "The 15-card base deck for Act 1 fights and the 22-card Act 2 deck for Act 2 fights (Knowledge Demon, Entomancer), at 60/80 HP, the better plan; "
          "the Player's Ironclad boss fights on v0.107.1 (real decks are bigger and have relics, potions and upgrades, so the "
          "model is expected to be pessimistic; what matters is the ratio between bosses). A boss marked **no** is not used by "
          "`tools/draft.py`.", "",
          md_table(["Boss", "Model win", "The Player survived", "Used in drafting"], cal), ""]
    # Calibration with the Player's own decks
    real = calibrate_real(runs=max(10, runs // 10))
    rc = [[k.replace("_", " ").title(), n, f"{m:.0%}", f"{pr:.2f}", f"{s}/{n} ({s / n:.0%})"] for k, (m, s, n, pr) in real.items()]
    L += ["## Calibration with the Player's own decks", "",
          "Each of the Player's Ironclad fights against a modelled boss or elite (v0.107.1, solo, finished runs), replayed with "
          "the deck the run had on arrival (with its upgrades), its arrival HP, the potions it held and the relics the simulator "
          "applies (`SIM_RELICS`: Vajra, Anchor, Gorget and others), the better of the two plans. It has no other relics and only "
          "the card effects `tools/plan_turn.py` reads (Powers other than Strength, Dexterity, Demon Form, Pyre and Feel No Pain "
          "do nothing), and the planner looks one turn ahead, so its boss win rates for real decks are far too low; the share of "
          "the boss's HP removed is the more useful comparison between bosses. The short elite fight (Byrdonis) comes out close "
          "to the record, so the gap grows with fight length, as missing scaling effects would make it.", "",
          md_table(["Fight", "Fights", "Model win", "Boss HP removed (model)", "The Player survived"], rc), "",
          "Reading: absolute win rates from the simulator mean little for real decks; use it to compare additions to the same "
          "deck. A boss whose share removed is low while the Player usually survived (Ceremonial Beast, Entomancer, Knowledge "
          "Demon) is modelled too hard.", ""]
    # Plan mode: balanced, a switch to safe below half HP, or safe, with the survival guard in plan_turn.rank
    pm = []
    base_deck = expand_deck(EXPERIMENT_BASE, "IRONCLAD")
    plus2 = expand_deck(EXPERIMENT_BASE + ["TWIN_STRIKE", "SHRUG_IT_OFF"], "IRONCLAD")
    safer, level = [], []
    for key, d, name in (("VANTOM", base_deck, "Vantom, base deck"), ("VANTOM", plus2, "Vantom, base + Twin Strike + Shrug It Off"),
                         ("LAGAVULIN_MATRIARCH", base_deck, "Lagavulin Matriarch, base deck"),
                         ("SOUL_FYSH", base_deck, "Soul Fysh, base deck"), ("WATERFALL_GIANT", base_deck, "Waterfall Giant, base deck")):
        for start in (80, 60):
            wr = [evaluate(d, key, start, 80, runs // 2, m)["win_rate"] for m in ("balanced", "hybrid:0.5", "safe")]
            pm.append([name, f"{start}/80"] + [f"{x:.0%}" for x in wr])
            (safer if wr[2] - wr[0] >= 0.10 else level).append(f"{name} {start}/80")
    by_boss = sorted({s.split(",")[0] for s in safer})
    L += ["## Which plan to follow in a boss fight", "",
          "Win rate when every turn follows the balanced plan, the safe plan below half HP and balanced above, or the safe plan. "
          "Plans that would leave you at 0 HP are ranked last in every mode (survival guard).", "",
          md_table(["Fight", "Start HP", "Balanced", "Safe below 50%", "Safe"], pm), "",
          "Reading (computed): the safe plan beat the balanced plan by 10 points or more in "
          + (f"{len(safer)} rows ({', '.join(by_boss)})" if safer else "no row")
          + f"; in the other {len(level)} rows the balanced plan was better, level, or within 10 points.", ""]
    # Soul Fysh and Waterfall Giant: which additions help, under each boss's better plan
    sw = []
    for name, add in EXPERIMENT_VARIANTS + [("+ True Grit, Burning Pact (exhaust)", ["TRUE_GRIT", "BURNING_PACT"]),
                                            ("+ Pyre, Feel No Pain (powers)", ["PYRE", "FEEL_NO_PAIN"])]:
        deck = expand_deck(EXPERIMENT_BASE + add, "IRONCLAD")
        cells = [name]
        for key in ("SOUL_FYSH", "WATERFALL_GIANT"):
            r = max((evaluate(deck, key, 60, 80, runs // 3, m) for m in ("balanced", "safe")), key=lambda x: x["win_rate"])
            cells += [f"{r['win_rate']:.0%}", f"{r['hp_lost']:.1f}"]
        sw.append(cells)
    L += ["## Soul Fysh and Waterfall Giant: which additions help", "",
          "From 60/80 HP, the better of the balanced and safe plans per row. Soul Fysh: Beckon (a 6 HP Beckon into the draw and "
          "discard piles), De-Gas 16, Gaze 7 + Beckon, Fade (Intangible for your next turn), Scream 13 + 3 Vulnerable on you; "
          "a held Beckon costs 6 HP at the end of your turn and can be played for 1 energy. Waterfall Giant: Pressurize (+15 "
          "Steam Eruption), then Stomp 15 + Weak, Ram 10, Siphon (heal 10), Pressure Gun 20 (+5 a use), Pressure Up 13, each "
          "+3 Steam; at 0 HP a stun turn, then an explosion for its Steam Eruption. Cycles `[COMMUNITY]` (Waterfall Giant: one "
          "guide for the full cycle). Exhaust cards remove a held Beckon (or another status or curse) first.", "",
          md_table(["Base deck + two cards", "Soul Fysh win", "HP lost", "Waterfall Giant win", "HP lost"], sw), ""]
    # Byrdonis: plan choice against an elite that gains Strength every turn
    by = []
    weak_deck = expand_deck(["STRIKE_IRONCLAD:5", "DEFEND_IRONCLAD:4", "BASH", "TWIN_STRIKE", "POMMEL_STRIKE"], "IRONCLAD")
    for name, d in (("starter + Twin Strike + Pommel Strike (12 cards)", weak_deck), ("base deck (15 cards)", base_deck)):
        for start in (56, 70):
            cells = [name, f"{start}/80"]
            for m in ("balanced", "hybrid:0.5", "safe"):
                r = evaluate(d, "BYRDONIS", start, 80, runs * 2 // 3, m)
                cells.append(f"{r['win_rate']:.0%} ({r['hp_lost']:.0f} HP)")
            by.append(cells)
    L += ["## Byrdonis: which plan against an elite that scales", "",
          "Byrdonis (91 HP; Peck 3x3 and Swoop 16 alternating; +1 Strength each turn, order and amount `[HYPOTHESIS]`). "
          "Calibration: the base deck loses about 26–29 HP here; the Player's Ironclad decks lost 25.8 on average (10 fights).", "",
          md_table(["Deck", "Start HP", "Balanced: win (HP lost)", "Safe below 50%", "Safe"], by), "",
          "Reading: blocking instead of attacking lets the Strength snowball. With a weak deck the safe plan collapses; with a "
          "strong deck it saves a few HP. Against enemies that scale every turn, follow the balanced plan.", ""]
    # The Kin: race the Priest or let the planner target (it clears followers with hit-all cards)
    kin = []
    hitall = expand_deck(EXPERIMENT_BASE + ["THUNDERCLAP", "CONFLAGRATION"], "IRONCLAD")
    kres = {}
    for name, d in (("base deck (15 cards)", base_deck), ("+ Thunderclap, Conflagration (hit-all)", hitall)):
        cells = [name]
        for focus in (True, False):
            r = max((evaluate(d, "THE_KIN", 80, 80, runs // 3, m, focus_boss=focus) for m in ("balanced", "safe")),
                    key=lambda x: x["win_rate"])
            kres[(name, focus)] = r["win_rate"]
            cells.append(f"{r['win_rate']:.0%} ({r['hp_lost']:.0f} HP)")
        kin.append(cells)
    (n1, n2) = ("base deck (15 cards)", "+ Thunderclap, Conflagration (hit-all)")
    L += ["## The Kin: race the Priest or clear the followers", "",
          "Kin Priest (190 HP; Orb of Frailty 8 + Frail, Orb of Weakness 8 + Weak, Beam 3x3, Ritual +2 Strength) with two Minion "
          "followers (58 HP; Quick Slash 5, Boomerang 2x2, Power Dance +2 Strength); killing the Priest ends the fight. Cycles "
          "`[HYPOTHESIS]`; the model is far too hard for this boss (the Player survived 8 of 8), so read only the comparison. "
          "From full HP, the better plan per row.", "",
          md_table(["Deck", "Every single-target card at the Priest", "The planner's own targets"], kin), "",
          f"Reading (computed): single-target deck: racing the Priest {kres[(n1, True)]:.0%} against {kres[(n1, False)]:.0%}; "
          f"with two hit-all cards: the planner's targets (clearing followers) {kres[(n2, False)]:.0%} against racing "
          f"{kres[(n2, True)]:.0%}.", ""]
    # Knowledge Demon: the Curse of Knowledge choice, all eight combinations of the three offers
    import itertools
    kd, res = [], {}
    for plan in itertools.product(*[(c, "DISINTEGRATION") for c in CURSE_OFFERS]):
        r = max((evaluate(kd_deck, "KNOWLEDGE_DEMON", 80, 80, runs // 2, m, plan) for m in ("balanced", "safe")),
                key=lambda x: x["win_rate"])
        res[plan] = r
        kd.append([" / ".join(x.replace("_", " ").title() for x in plan), f"{r['win_rate']:.0%}", f"{r['hp_lost']:.1f}", r["turns"]])
    best = max(res, key=lambda k: (res[k]["win_rate"], -res[k]["hp_lost"]))
    per = []
    for i, c in enumerate(CURSE_OFFERS):  # each offer, the other two held at the best plan
        alt = tuple(("DISINTEGRATION" if best[i] == c else c) if j == i else best[j] for j in range(3))
        per.append(f"offer {i + 1}: {best[i].replace('_', ' ').title()} ({res[best]['win_rate']:.0%}) over "
                   f"{alt[i].replace('_', ' ').title()} ({res[alt]['win_rate']:.0%})")
    L += ["## Knowledge Demon: which curse to take", "",
          "A 22-card end-of-Act-2 deck (two Inflames, Demon Form, two Twin Strikes, Impervious, Offering and others) at 80/80 HP. "
          "Each Curse of Knowledge offers Disintegration or one other card: Mind Rot, then Sloth, then Waste Away (one guide); "
          "the table tries all eight combinations. Disintegration deals 6, 7 or 8 at the end of each turn depending on the "
          "offer, and the amounts add up if taken more than once. Cycle (two guides): Curse of Knowledge, Slap 17, Knowledge "
          "Overwhelming 8x3, Ponder 11 + heal 30 + 2 Strength, three times, then the last three repeating.", "",
          md_table(["Offer 1 / offer 2 / offer 3", "Win", "HP lost", "Median turns"], kd), "",
          f"Reading (computed): best combination {' / '.join(x.replace('_', ' ').title() for x in best)}; " + "; ".join(per) + ".", ""]
    out = PROJECT / "reports/phase2/vantom-simulation.md"
    out.write_text("\n".join(L))
    print("wrote", out.relative_to(PROJECT))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deck", nargs="+", default=["STRIKE_IRONCLAD:5", "DEFEND_IRONCLAD:4", "BASH"])
    ap.add_argument("--vs", nargs="*", action="append", default=[], help="a set of cards to add (repeatable)")
    ap.add_argument("--boss", default="VANTOM", choices=list(BOSSES))
    ap.add_argument("--hp", type=int, default=80)
    ap.add_argument("--max-hp", type=int, default=80)
    ap.add_argument("--runs", type=int, default=300)
    ap.add_argument("--character", default="IRONCLAD")
    ap.add_argument("--report", action="store_true", help="run the fixed Vantom experiment and write reports/phase2/vantom-simulation.md")
    ap.add_argument("--beast-sensitivity", action="store_true", help="gap 25: one-assumption variants of the Ceremonial Beast model")
    args = ap.parse_args(argv)
    if args.beast_sensitivity:
        for name, w, turns in beast_sensitivity(args.runs if args.runs != 300 else 150):
            print(f"  {name:<42} base deck from 60/80: {w:4.0%} wins (median {turns} turns)")
        return 0
    if args.report:
        report(args.runs)
        return 0
    base = expand_deck(args.deck, args.character.upper())
    variants = [("base deck", base)] + [(" + ".join(v), base + expand_deck(v, args.character.upper())) for v in args.vs if v]
    print(f"{args.boss}: {args.runs} simulated fights per deck from {args.hp}/{args.max_hp} HP (model, [HYPOTHESIS])")
    for name, deck in variants:
        r = evaluate(deck, args.boss, args.hp, args.max_hp, args.runs)
        print(f"  {name:<40} win {r['win_rate']:5.0%} · HP lost {r['hp_lost']:5.1f} (in wins {r['hp_lost_wins']:5.1f}) · "
              f"median turns {r['turns']}" + (f" · {r['timeouts']} timeouts" if r["timeouts"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
