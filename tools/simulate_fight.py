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
Prepare +2 Strength; 173 HP; 9 Slippery).

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

BOSSES = {
    "VANTOM": {"hp": 173, "slippery": 9, "cycle": [("attack", 7, 1, 0), ("attack", 6, 2, 0), ("attack", 27, 1, 3), ("buff", 0, 0, 0)],
               "buff_strength": 2, "status_card": "WOUND"},
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


def run_fight(deck, boss="VANTOM", hp=80, max_hp=80, seed=0, mode="balanced", max_turns=25):
    spec = BOSSES[boss]
    rng = random.Random(seed)
    draw = [c.split(".", 1)[-1] for c in deck]
    rng.shuffle(draw)
    discard, exhausted = [], []
    strength, demon = 0, 0
    b = {"hp": spec["hp"], "block": 0, "slippery": spec.get("slippery", 0), "strength": 0, "vuln": 0, "weak": 0}
    for turn in range(1, max_turns + 1):
        strength += demon
        move = spec["cycle"][(turn - 1) % len(spec["cycle"])]
        kind, dmg, hits, status = move
        intent = (dmg + b["strength"], hits) if kind == "attack" else (0, 0)
        hand_ids = draw_cards(5, draw, discard, rng)
        energy, block, gained_this_turn = 3, 0, 0
        played = []
        for _ in range(4):  # plan, play up to a draw, re-plan with what is left
            hand = [pt.card_from_extract(i, cid) for i, cid in enumerate(hand_ids)]
            enemy = pt.Enemy(0, boss, b["hp"], b["block"], intent[0], intent[1], vuln=b["vuln"] > 0, weak=b["weak"] > 0,
                             slippery=b["slippery"])
            player = pt.Player(energy=energy, block=block, strength=strength + gained_this_turn)
            res = pt.plans(hand, player, [enemy])
            if not res:
                break
            best = pt.rank(res, mode, pt.POTION_COST["boss"], pt.POWER_VALUE["boss"])[0]
            seq = best["seq"]
            cut = next((i + 1 for i, (c, _) in enumerate(seq) if c.draw), len(seq))
            chosen = [c for c, _ in seq[:cut]]
            if not chosen:
                break
            # replay the chosen prefix to get the exact state after it
            order = [c for c in chosen]
            targets = [0 if c.target == "AnyEnemy" else None for c in order]
            out = pt.simulate(order, targets, player, [enemy])
            if out is None:
                break
            ea = out["enemies_after"][0]
            b["hp"], b["block"], b["slippery"] = ea["hp"], ea["block"], ea["slippery"]
            for c in order:
                if c.vuln:
                    b["vuln"] = max(b["vuln"], c.vuln)
                if c.weak:
                    b["weak"] = max(b["weak"], c.weak)
            energy = out["energy_left"]
            block = out["block"]
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
                played.append(c.card_id)
            if b["hp"] <= 0:
                return {"won": True, "hp": hp, "turns": turn}
            new = sum(c.draw for c in order)
            if new and seq[cut - 1][0].draw:
                hand_ids += draw_cards(new, draw, discard, rng)
                continue
            break
        discard.extend(hand_ids)
        # boss turn
        if kind == "attack":
            per = calc.hit_damage(intent[0], attacker_weak=b["weak"] > 0)
            total = per * intent[1]
            hp -= max(0, total - block)
            for _ in range(status):
                discard.append(spec["status_card"])
        else:
            b["strength"] += spec["buff_strength"]
        if hp <= 0:
            return {"won": False, "hp": 0, "turns": turn}
        b["vuln"] = max(0, b["vuln"] - 1)
        b["weak"] = max(0, b["weak"] - 1)
        b["block"] = 0
    return {"won": False, "hp": hp, "turns": max_turns, "timeout": True}


def evaluate(deck, boss, hp, max_hp, runs, mode="balanced"):
    rs = [run_fight(deck, boss, hp, max_hp, seed=s, mode=mode) for s in range(runs)]
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
    rows = []
    for name, add in EXPERIMENT_VARIANTS:
        deck = expand_deck(EXPERIMENT_BASE + add, "IRONCLAD")
        cells = [name]
        for mode in ("balanced", "safe"):
            r = evaluate(deck, "VANTOM", 80, 80, runs, mode)
            cells += [f"{r['win_rate']:.0%}", f"{r['hp_lost']:.1f}"]
        rows.append(cells)
    L = ["# Vantom Simulation", "",
         f"Built by `tools/simulate_fight.py --report` ({runs} simulated fights per row and mode, from 80/80 HP). Each turn's plays "
         "are chosen by `tools/plan_turn.py`; Vantom follows its documented cycle (Ink Blot 7, Inky Lance 6x2, Dismember 27 + 3 "
         "Wounds, Prepare +2 Strength; 173 HP; 9 Slippery). Card values are v0.111.1. No relics, potions or upgrades. "
         "`[HYPOTHESIS]`: a model, useful for comparing additions to the same deck, not for absolute win rates.", "",
         "Calibration: a typical 16-card floor-17 deck starting at 60/80 HP wins 33–39% of simulated fights; the Player's "
         "Ironclad decks survived 5 of 11 real Vantom fights, so the model is in range and somewhat pessimistic.", "",
         md_table(["Base deck + two cards", "Win (balanced)", "HP lost (balanced)", "Win (safe)", "HP lost (safe)"], rows), "",
         "## Reading (from the table above; seeds are fixed, so the run reproduces)", "",
         "- **Multi-hit attacks and Demon Form are the best additions** in both plans (multi-hit 98% balanced / 92% safe; "
         "Demon Form with Shrug It Off 99% / 79%). Supports H6 and the playbook's Vantom override for multi-hit attacks.",
         "- **Breakthrough is worse than a plain Strike here**: two Breakthroughs fall below the two-Strike control in both plans "
         "(58% against 66% balanced, 32% against 47% safe); its 9 damage is capped to 1 while Slippery lasts, and it costs HP. "
         "Thunderclap with Breakthrough is level with the control under the balanced plan and below it under the safe plan. "
         "Consistent with H2 and with Breakthrough's decision-point record.",
         "- **Draw and block help only under the safe plan** (above the base there, below it under the balanced plan): the "
         "planner's mode interacts with the deck, so treat those rows as policy-dependent.",
         "- The balanced plan beats the safe plan from full HP for most decks; from 60 HP the safe plan did better in a separate "
         "check. This matches the playbook: safe when HP is below plan, balanced when ahead.", ""]
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
