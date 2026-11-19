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
until 150 HP lost, stun, then Beast Cry, Stomp 15, Crush 17 + 3 Strength). The last two cycles are [HYPOTHESIS]:
declaration order in the extract plus community notes.

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

def _move(kind="attack", dmg=0, hits=1, status=0, boss_block=0, boss_str=0, p_str=0, p_dex=0, heal=0):
    return {"kind": kind, "dmg": dmg, "hits": hits, "status": status, "boss_block": boss_block, "boss_str": boss_str,
            "p_str": p_str, "p_dex": p_dex, "heal": heal}


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
    """Stamp (150 Plow) on turn 1; Plow 18 + 2 Strength each turn until 150 HP is lost, then a stun turn with its
    Strength removed; then Beast Cry (Ringing, not modelled), Stomp 15, Crush 17 + 3 Strength. Order from the
    extract's declaration order and the boss note `[HYPOTHESIS]`."""
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
    return [_move("debuff"), _move(dmg=15), _move(dmg=17, boss_str=3)][i % 3]


def beast_damaged(b, lost):
    if b.get("plow", 0) > 0:
        b["plow"] -= lost
        if b["plow"] <= 0:
            b["plow"] = 0
            b["stunned"] = True
            b["strength"] = 0


def demon_move(b, turn):
    """Knowledge Demon (379 HP): Curse of Knowledge, Slap 17, Knowledge Overwhelming 8x3, Ponder 11 + heal 30 + 2 Strength,
    repeating; the curse is chosen three times (cycles 1-3). Order: the extract's declaration order and one guide;
    heal 30 is single-source. The curse strategy is b['curse'] (SLOTH, MIND_ROT, WASTE_AWAY, DISINTEGRATION)."""
    i = (turn - 1) % 4
    if i == 0:
        if b.get("curses", 0) < 3:
            b["curses"] = b.get("curses", 0) + 1
            return _move("curse")
        return _move(dmg=17)  # after three curses: a plain Slap / Overwhelming / Ponder loop (the guide)
    return [None, _move(dmg=17), _move(dmg=8, hits=3), _move(dmg=11, boss_str=2, heal=30)][i]


def entomancer_move(b, turn):
    """Entomancer (elite, 145 HP): Pheromone Spit (+1 Personal Hive, +3 Strength), Bees 3x7, Spear 18, repeating, in the
    extract's declaration order `[HYPOTHESIS]`. Personal Hive starts at 1."""
    i = (turn - 1) % 3
    if i == 0:
        b["hive"] = b.get("hive", 1) + 1
        return _move("buff", boss_str=3)
    return [None, _move(dmg=3, hits=7), _move(dmg=18)][i]


def byrdonis_move(b, turn):
    """Byrdonis (elite, 91 HP): Peck 3x3 and Swoop 16 alternating; Territorial: +1 Strength at the end of each of its
    turns. Order and Territorial amount are [HYPOTHESIS] (the extract lists the two moves and the power only)."""
    m = _move(dmg=3, hits=3, boss_str=1) if turn % 2 == 1 else _move(dmg=16, boss_str=1)
    return m


BOSSES = {
    # validated: the model's win rate relative to Vantom roughly matches the Player's record (see report()).
    "VANTOM": {"hp": 173, "slippery": 9, "move": vantom_move, "status_card": "WOUND", "validated": True},
    "LAGAVULIN_MATRIARCH": {"hp": 222, "asleep": 3, "plating": 12, "move": lagavulin_move, "on_damage": lagavulin_damaged,
                            "validated": True},
    "CEREMONIAL_BEAST": {"hp": 252, "move": beast_move, "on_damage": beast_damaged, "validated": False},  # fails calibration
    "KNOWLEDGE_DEMON": {"hp": 379, "move": demon_move, "validated": False},  # calibration in report()
    # Entomancer fails calibration badly (every deck loses by turn 5): the extract's Strength gains and Bees 3x7 cannot all
    # apply from turn 1 in this order; probably ascension-dependent values or another order. Not used; see gap 26.
    "ENTOMANCER": {"hp": 145, "hive": 1, "move": entomancer_move, "validated": False, "encounter": "ENTOMANCER_ELITE"},
    # Byrdonis: the 15-card base deck loses about 26-29 HP here, the Player's Ironclad decks lost 25.8 on average.
    "BYRDONIS": {"hp": 91, "move": byrdonis_move, "validated": True, "encounter": "BYRDONIS_ELITE"},
}


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


def run_fight(deck, boss="VANTOM", hp=80, max_hp=80, seed=0, mode="balanced", max_turns=25, curse="SLOTH"):
    spec = BOSSES[boss]
    rng = random.Random(seed)
    draw = [c.split(".", 1)[-1] for c in deck]
    rng.shuffle(draw)
    discard, exhausted = [], []
    strength, demon, dexterity = 0, 0, 0
    # Necrobinder: Bound Phylactery summons 1 at combat start and each turn; Osty absorbs unblocked damage. NOT VALIDATED:
    # a 14-card Necrobinder deck wins 0% against Lagavulin here while the Player survived 15 of 15, so the Osty rules
    # are incomplete (Unleash's damage, revival, what the redirect really covers). Do not use Necrobinder results yet.
    necro = any("NECROBINDER" in c.upper() for c in deck)
    osty = 0
    b = {"hp": spec["hp"], "block": 0, "slippery": spec.get("slippery", 0), "strength": 0, "vuln": 0, "weak": 0,
         "asleep": spec.get("asleep", 0), "plating": spec.get("plating", 0), "curse": curse, "hive": spec.get("hive", 0)}
    sloth = mind_rot = waste = disint = 0
    for turn in range(1, max_turns + 1):
        strength += demon
        if necro:
            osty += 2 if turn == 1 else 1  # combat start + turn start
        if b.get("asleep", 0) > 0 and b.get("plating"):
            b["block"] = b["plating"]
        mv = spec["move"](b, turn)
        intent = (mv["dmg"] + b["strength"], mv["hits"]) if mv["kind"] == "attack" else (0, 0)
        raw_intent = intent
        if intent[1] and b["weak"] > 0:  # like the game, the shown intent already includes Weak on the boss
            intent = (calc.hit_damage(intent[0], attacker_weak=True), intent[1])
        hand_ids = draw_cards(max(1, 5 - mind_rot), draw, discard, rng)
        energy, block, gained_this_turn = max(1, 3 - waste), 0, 0
        cards_played = 0
        for _ in range(4):  # plan, play up to a draw, re-plan with what is left
            hand = [pt.card_from_extract(i, cid) for i, cid in enumerate(hand_ids)]
            enemy = pt.Enemy(0, boss, b["hp"], b["block"], intent[0], intent[1], vuln=b["vuln"] > 0, weak=b["weak"] > 0,
                             slippery=b["slippery"], hive=b.get("hive", 0))
            player = pt.Player(energy=energy, block=block, strength=strength + gained_this_turn, dexterity=dexterity,
                               max_cards=(3 - cards_played) if sloth else None, hp=hp, osty_hp=osty)
            res = pt.plans(hand, player, [enemy])
            if not res:
                break
            turn_mode = mode
            if mode.startswith("hybrid:"):  # safe below the HP fraction, balanced above
                turn_mode = "safe" if hp < float(mode.split(":")[1]) * max_hp else "balanced"
            best = pt.rank(res, turn_mode, pt.POTION_COST["boss"], pt.POWER_VALUE["boss"])[0]
            seq = best["seq"]
            cut = next((i + 1 for i, (c, _) in enumerate(seq) if c.draw), len(seq))
            order = [c for c, _ in seq[:cut]]
            if not order:
                break
            targets = [0 if c.target == "AnyEnemy" else None for c in order]
            out = pt.simulate(order, targets, player, [enemy])
            if out is None:
                break
            ea = out["enemies_after"][0]
            lost = b["hp"] - ea["hp"]
            for _ in range(out.get("hive_cards", 0)):  # Personal Hive: dead cards shuffled into the draw pile
                draw.insert(rng.randrange(len(draw) + 1), "WOUND")
            b["hp"], b["block"], b["slippery"] = ea["hp"], ea["block"], ea["slippery"]
            if spec.get("on_damage"):
                spec["on_damage"](b, lost)
            for c in order:
                if c.vuln:
                    b["vuln"] = max(b["vuln"], c.vuln)
                if c.weak:
                    b["weak"] = max(b["weak"], c.weak)
            energy, block = out["energy_left"], out["block"]
            osty = out.get("osty_before_enemy", osty)
            cards_played += sum(1 for c in order if not c.potion)
            hp -= sum(c.hp_cost for c in order)
            for c in order:
                gained_this_turn += c.strength
                hand_ids.remove(c.card_id)
                rec = pt.CARDS.get(c.card_id) or {}
                if c.power:
                    if c.card_id == "DEMON_FORM":
                        demon += 3
                    if c.strength:
                        strength += c.strength
                        gained_this_turn -= c.strength  # now part of persistent strength
                elif "Exhaust" in (rec.get("effect") or ""):
                    exhausted.append(c.card_id)
                else:
                    discard.append(c.card_id)
                if c.card_id == "ANGER":
                    discard.append("ANGER")
            if b["hp"] <= 0:
                return {"won": True, "hp": hp, "turns": turn}
            if sum(c.draw for c in order) and seq[cut - 1][0].draw:
                hand_ids += draw_cards(sum(c.draw for c in order), draw, discard, rng)
                continue
            break
        discard.extend(hand_ids)
        # boss turn
        if mv["kind"] == "attack":
            per = calc.hit_damage(raw_intent[0], attacker_weak=b["weak"] > 0)
            unblocked = max(0, per * intent[1] - block)
            to_osty = min(osty, unblocked)  # Osty takes the unblocked damage first (DIE_FOR_YOU_POWER)
            osty -= to_osty
            hp -= unblocked - to_osty
            for _ in range(mv["status"]):
                discard.append(spec.get("status_card", "WOUND"))
        b["strength"] += mv["boss_str"]
        b["hp"] = min(spec["hp"], b["hp"] + mv.get("heal", 0))
        strength += mv["p_str"]
        dexterity += mv["p_dex"]
        if mv["kind"] == "curse":  # the chosen curse stacks for the rest of the fight
            if b["curse"] == "SLOTH":
                sloth = 1
            elif b["curse"] == "MIND_ROT":
                mind_rot += 1
            elif b["curse"] == "WASTE_AWAY":
                waste += 1
            elif b["curse"] == "DISINTEGRATION":
                disint += 1
        if disint:
            hp -= 5 + disint  # Disintegration: 6, then 7, then 8 at the end of your turn (the guide)
        if hp <= 0:
            return {"won": False, "hp": 0, "turns": turn}
        b["vuln"] = max(0, b["vuln"] - 1)
        b["weak"] = max(0, b["weak"] - 1)
        b["block"] = mv["boss_block"]
    return {"won": False, "hp": hp, "turns": max_turns, "timeout": True}


def evaluate(deck, boss, hp, max_hp, runs, mode="balanced", curse="SLOTH"):
    rs = [run_fight(deck, boss, hp, max_hp, seed=s, mode=mode, curse=curse) for s in range(runs)]
    wins = [r for r in rs if r["won"]]
    return {"win_rate": len(wins) / runs, "hp_lost": statistics.mean(hp - r["hp"] for r in rs),
            "hp_lost_wins": statistics.mean(hp - r["hp"] for r in wins) if wins else float("nan"),
            "turns": statistics.median(r["turns"] for r in rs), "timeouts": sum(1 for r in rs if r.get("timeout"))}


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
        cal_deck = kd_deck if key == "KNOWLEDGE_DEMON" else expand_deck(EXPERIMENT_BASE, "IRONCLAD")
        r = max((evaluate(cal_deck, key, 60, 80, runs // 2, m) for m in ("balanced", "safe")), key=lambda x: x["win_rate"])
        s, n = con.execute("""SELECT SUM(NOT (f.is_last_floor AND NOT r.win)), COUNT(*) FROM floors f JOIN runs r USING(run_id)
                              WHERE r.build_id='v0.107.1' AND r.character='IRONCLAD' AND r.n_players=1 AND NOT r.abandoned
                              AND f.model_id = ?""", ["ENCOUNTER." + BOSSES[key].get("encounter", key + "_BOSS")]).fetchone()
        cal.append([key.replace("_", " ").title(), f"{r['win_rate']:.0%}", f"{s}/{n} ({s / n:.0%})" if n else "-",
                    "yes" if BOSSES[key].get("validated") else "**no**"])
    con.close()
    L += ["## Calibration against the Player's record", "",
          "The 15-card base deck for Act 1 bosses and the 22-card Act 2 deck for Knowledge Demon, at 60/80 HP, the better plan; "
          "the Player's Ironclad boss fights on v0.107.1 (real decks are bigger and have relics, potions and upgrades, so the "
          "model is expected to be pessimistic; what matters is the ratio between bosses). A boss marked **no** is not used by "
          "`tools/draft.py`.", "",
          md_table(["Boss", "Model win", "The Player survived", "Used in drafting"], cal), ""]
    # Plan mode: balanced, a switch to safe below half HP, or safe, with the survival guard in plan_turn.rank
    pm = []
    base_deck = expand_deck(EXPERIMENT_BASE, "IRONCLAD")
    plus2 = expand_deck(EXPERIMENT_BASE + ["TWIN_STRIKE", "SHRUG_IT_OFF"], "IRONCLAD")
    for key, d, name in (("VANTOM", base_deck, "Vantom, base deck"), ("VANTOM", plus2, "Vantom, base + Twin Strike + Shrug It Off"),
                         ("LAGAVULIN_MATRIARCH", base_deck, "Lagavulin Matriarch, base deck")):
        for start in (80, 60):
            pm.append([name, f"{start}/80"] + [f"{evaluate(d, key, start, 80, runs // 2, m)['win_rate']:.0%}" for m in ("balanced", "hybrid:0.5", "safe")])
    L += ["## Which plan to follow in a boss fight", "",
          "Win rate when every turn follows the balanced plan, the safe plan below half HP and balanced above, or the safe plan. "
          "Plans that would leave you at 0 HP are ranked last in every mode (survival guard).", "",
          md_table(["Fight", "Start HP", "Balanced", "Safe below 50%", "Safe"], pm), "",
          "Reading: in these boss fights the balanced plan was best or level in every row; switching to safe at low HP did not help.", ""]
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
    # Knowledge Demon: the Curse of Knowledge choice, as four pure strategies
    kd = []
    for curse in ("SLOTH", "MIND_ROT", "WASTE_AWAY", "DISINTEGRATION"):
        r = max((evaluate(kd_deck, "KNOWLEDGE_DEMON", 80, 80, runs * 2 // 3, m, curse) for m in ("balanced", "safe")),
                key=lambda x: x["win_rate"])
        kd.append([curse.replace("_", " ").title(), f"{r['win_rate']:.0%}", f"{r['hp_lost']:.1f}", r["turns"]])
    L += ["## Knowledge Demon: which curse to take", "",
          "A 22-card end-of-Act-2 deck (two Inflames, Demon Form, two Twin Strikes, Impervious, Offering and others) at 80/80 HP; "
          "each row always takes the same curse when offered (the real choice is one of two each time). Cycle: Curse of "
          "Knowledge, Slap 17, Knowledge Overwhelming 8x3, Ponder 11 + heal 30 + 2 Strength (heal single-source); curses stack "
          "for the rest of the fight; Disintegration modelled as 6, then 7, then 8 at the end of each turn (not summed).", "",
          md_table(["Curse always taken", "Win", "HP lost", "Median turns"], kd), "",
          "Reading: the order matches the playbook's choice rule (Sloth first, Disintegration last).", ""]
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
    args = ap.parse_args(argv)
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
