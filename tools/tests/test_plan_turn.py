"""Offline tests for tools/plan_turn.py (base values from the extract)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import plan_turn as pt  # noqa: E402


def hand(*names):
    return [pt.card_from_extract(i, pt.resolve_card(n)) for i, n in enumerate(names)]


def best(h, player, enemies, mode="safe"):
    return pt.rank(pt.plans(h, player, enemies), mode)[0]


class TestPlanTurn(unittest.TestCase):
    def test_parse(self):
        bash = hand("Bash")[0]
        self.assertEqual((bash.dmg, bash.vuln, bash.cost, bash.target), (8, 2, 2, "AnyEnemy"))
        tw = hand("Twin Strike")[0]
        self.assertEqual((tw.dmg, tw.hits), (5, 2))
        off = hand("Offering")[0]
        self.assertEqual((off.energy, off.draw, off.hp_cost), (2, 3, 6))
        e = pt.parse_enemy("Vantom:173:0:7:slippery=9", 0)
        self.assertEqual((e.hp, e.intent_per_hit, e.intent_hits, e.slippery), (173, 7, 1, 9))
        e = pt.parse_enemy("Louse:12:3:5x2:weak", 1)
        self.assertEqual((e.block, e.intent_per_hit, e.intent_hits, e.weak), (3, 5, 2, True))

    def test_vulnerable_ordering(self):
        o = best(hand("Bash", "Strike"), pt.Player(energy=3), [pt.parse_enemy("Worm:40:0:11", 0)], "balanced")
        self.assertEqual(o["dealt"], 17)  # 8, then Strike 6 x 1.5 = 9
        self.assertEqual(o["plays"][0].split(" →")[0], "Bash")

    def test_lethal_first(self):
        o = best(hand("Strike", "Strike", "Defend"), pt.Player(energy=3), [pt.parse_enemy("Louse:12:0:20", 0)])
        self.assertTrue(o["all_dead"])
        self.assertEqual(o["hp_lost"], 0)

    def test_kill_removes_intent_and_focus(self):
        enemies = [pt.parse_enemy("A:10:0:6", 0), pt.parse_enemy("B:12:3:5x2", 1)]
        o = best(hand("Twin Strike", "Strike", "Defend"), pt.Player(energy=3), enemies)
        self.assertEqual(o["enemy_hp"][1], 0)
        self.assertEqual(o["hp_lost"], 1)  # A's 6 against 5 block

    def test_weak_reduces_intent(self):
        o = pt.simulate(hand("Uppercut"), [0], pt.Player(energy=3), [pt.parse_enemy("A:50:0:12", 0)])
        self.assertEqual(o["incoming"], 9)  # 12 x 0.75
        self.assertEqual(o["dealt"], 13)    # own Vulnerable lands after the hit

    def test_slippery(self):
        o = pt.simulate(hand("Twin Strike", "Strike"), [0, 0], pt.Player(energy=3),
                        [pt.parse_enemy("Vantom:173:0:7:slippery=9", 0)])
        self.assertEqual(o["dealt"], 3)
        o = pt.simulate(hand("Strike"), [0], pt.Player(energy=3), [pt.parse_enemy("Vantom:173:0:7:slippery=1", 0)])
        self.assertEqual(o["dealt"], 1)

    def test_strength_and_energy(self):
        o = pt.simulate(hand("Inflame", "Twin Strike"), [None, 0], pt.Player(energy=2), [pt.parse_enemy("A:50:0:0", 0)])
        self.assertEqual(o["dealt"], 14)  # (5 + 2) x 2
        o = pt.simulate(hand("Bloodletting", "Bash", "Bash"), [None, 0, 0], pt.Player(energy=3), [pt.parse_enemy("A:80:0:0", 0)])
        self.assertIsNotNone(o)
        self.assertEqual(o["hp_lost"], 3)
        self.assertIsNone(pt.simulate(hand("Bash", "Bash"), [0, 0], pt.Player(energy=3), [pt.parse_enemy("A:80:0:0", 0)]))

    def test_live_values_from_state(self):
        st = {"data": {"combat": {
            "player": {"current_hp": 50, "energy": 3, "block": 0, "powers": [{"power_id": "STRENGTH_POWER", "amount": 2}]},
            "hand": [{"index": 0, "card_id": "STRIKE_IRONCLAD", "energy_cost": 1, "playable": True,
                      "dynamic_values": [{"name": "Damage", "current_value": 8}]},
                     {"index": 1, "card_id": "DEFEND_IRONCLAD", "energy_cost": 1, "playable": True,
                      "dynamic_values": [{"name": "Block", "current_value": 5}]}],
            "enemies": [{"index": 0, "name": "Cultist", "current_hp": 50, "block": 0, "is_alive": True,
                         "powers": [{"power_id": "VULNERABLE_POWER", "amount": 1}],
                         "intents": [{"intent_type": "Attack", "damage": 6, "hits": 1, "total_damage": 6}]}]}}}
        h, player, enemies = pt.from_state(st)
        self.assertEqual(player.strength, 2)
        self.assertTrue(enemies[0].vuln)
        o = pt.simulate(h[:1], [0], player, enemies)
        self.assertEqual(o["dealt"], 12)  # live 8 already has Strength; x1.5 Vulnerable

    def test_hit_all_and_x_cost(self):
        enemies = [pt.parse_enemy("A:30:0:0", 0), pt.parse_enemy("B:30:0:0", 1)]
        o = pt.simulate(hand("Whirlwind"), [None], pt.Player(energy=3), enemies)
        self.assertEqual(o["dealt"], 30)  # 5 x 3 hits x 2 enemies
        self.assertEqual(o["energy_left"], 0)

    def test_potions(self):
        enemies = [pt.parse_enemy("Byrdonis:30:0:18", 0)]
        h = hand("Strike", "Strike", "Defend") + [pt.card_from_potion(0, "FIRE_POTION")]
        o = best(h, pt.Player(energy=3), enemies)
        self.assertTrue(o["all_dead"])
        self.assertEqual(o["potions"], 1)
        # not needed for lethal -> lethal without the potion ranks first
        h = hand("Bash", "Strike") + [pt.card_from_potion(0, "FIRE_POTION")]
        o = best(h, pt.Player(energy=3), [pt.parse_enemy("Louse:15:0:5", 0)])
        self.assertTrue(o["all_dead"])
        self.assertEqual(o["potions"], 0)
        # flat damage ignores Vulnerable and Strength, but Slippery still caps it
        o = pt.simulate([pt.card_from_potion(0, "FIRE_POTION")], [0], pt.Player(energy=3, strength=3),
                        [pt.parse_enemy("A:50:0:0:vuln", 0)])
        self.assertEqual(o["dealt"], 20)
        o = pt.simulate([pt.card_from_potion(0, "FIRE_POTION")], [0], pt.Player(energy=3), [pt.parse_enemy("V:173:0:7:slippery=9", 0)])
        self.assertEqual(o["dealt"], 1)
        # Dexterity potion raises later block cards
        o = pt.simulate([pt.card_from_potion(0, "DEXTERITY_POTION")] + hand("Defend"), [None, None], pt.Player(energy=3),
                        [pt.parse_enemy("A:50:0:10", 0)])
        self.assertEqual(o["block"], 7)
        self.assertFalse(pt.card_from_potion(0, "MYSTERY_POTION").playable)

    def test_potions_from_state(self):
        st = {"data": {"combat": {"player": {"current_hp": 30, "energy": 1, "block": 0, "powers": []},
                                  "hand": [{"index": 0, "card_id": "STRIKE_IRONCLAD", "energy_cost": 1, "playable": True}],
                                  "enemies": [{"index": 0, "name": "A", "current_hp": 25, "block": 0, "is_alive": True,
                                               "powers": [], "intents": [{"damage": 10, "hits": 1}]}]},
                       "run": {"potions": [{"index": 0, "potion_id": "FIRE_POTION", "occupied": True},
                                           {"index": 1, "potion_id": None, "occupied": False}]}}}
        h, player, enemies = pt.from_state(st)
        self.assertEqual([c.potion for c in h], [False, True])
        o = best(h, player, enemies)
        self.assertTrue(o["all_dead"])

    def test_slow(self):
        e = [pt.parse_enemy("Effigy:100:0:0:slow", 0)]
        # Strike (6) then Bash (8): Bash is played second, x1.1 -> 8; order small-to-big
        o = pt.simulate(hand("Strike", "Bash"), [0, 0], pt.Player(energy=3), e)
        self.assertEqual(o["dealt"], 6 + 8)
        o = pt.simulate(hand("Strike", "Strike", "Strike"), [0, 0, 0], pt.Player(energy=3), e)
        self.assertEqual(o["dealt"], 6 + 6 + 7)  # 6, 6x1.1=6.6->6, 6x1.2=7.2->7

    def test_osty(self):
        poke = hand("Poke")[0]
        self.assertTrue(poke.osty)
        self.assertEqual(poke.dmg, 6)
        e = [pt.parse_enemy("A:50:0:10:vuln", 0)]
        o = pt.simulate([poke], [0], pt.Player(energy=3, strength=5, osty_hp=5), e)
        self.assertEqual(o["dealt"], 9)          # 6 x 1.5; your Strength does not apply
        self.assertEqual(o["hp_lost"], 5)        # 10 unblocked: Osty takes 5, you take 5
        self.assertEqual(o["osty_hp_after"], 0)
        o = pt.simulate([poke], [0], pt.Player(energy=3, osty_hp=0), e)
        self.assertEqual(o["dealt"], 0)          # no Osty, no damage
        o = pt.simulate(hand("Bodyguard", "Poke"), [None, 0], pt.Player(energy=3, osty_hp=0), e)
        self.assertEqual(o["dealt"], 9)          # Summon 5 brings Osty back
        self.assertEqual(o["hp_lost"], 5)        # Osty (5) absorbs half of 10
        best_plan = best(hand("Poke", "Bodyguard"), pt.Player(energy=3, osty_hp=0), e, "balanced")
        self.assertEqual(best_plan["dealt"], 9)  # the planner orders Summon before the Osty attack
        bs = hand("Bone Shards")[0]
        self.assertTrue(bs.kills_osty)

    def test_power_value(self):
        e = [pt.parse_enemy("Boss:300:0:10", 0)]
        h = hand("Demon Form", "Strike", "Strike", "Strike")
        res = pt.plans(h, pt.Player(energy=3), e)
        boss = pt.rank(res, "balanced", pt.POTION_COST["boss"], pt.POWER_VALUE["boss"])[0]
        hall = pt.rank(res, "balanced", pt.POTION_COST["hallway"], pt.POWER_VALUE["hallway"])[0]
        self.assertEqual(boss["powers"], 3)   # Demon Form (3 energy) in a boss fight
        self.assertEqual(hall["powers"], 0)   # three Strikes in a hallway

    def test_commands_adjust_indexes(self):
        h = hand("Strike", "Defend", "Bash")      # indexes 0, 1, 2
        e = [pt.parse_enemy("Worm:40:0:11", 0)]
        e[0].ref = 3                              # the mod's own enemy index
        o = pt.simulate([h[2], h[0]], [0, 0], pt.Player(energy=3), e)   # Bash (index 2), then Strike (index 0)
        cmds = pt.commands(o, h)
        self.assertIn("play_card card_index=2 target_index=3", cmds[0])
        self.assertIn("play_card card_index=0 target_index=3", cmds[1])   # Strike still at 0 after Bash left
        o = pt.simulate([h[0], h[2]], [0, 0], pt.Player(energy=3), e)   # Strike first: Bash shifts from 2 to 1
        cmds = pt.commands(o, h)
        self.assertIn("card_index=0", cmds[0])
        self.assertIn("card_index=1", cmds[1])
        self.assertIn("end_turn", cmds[-1])
        p = pt.card_from_potion(1, "FIRE_POTION")
        o = pt.simulate([p], [0], pt.Player(energy=3), e)
        self.assertIn("use_potion option_index=1 target_index=3", pt.commands(o, h)[0])

    def test_survival_guard(self):
        # 5 HP left, enemy hits for 10: Strike + Defend would leave 0 HP, so balanced must play both Defends
        e = [pt.parse_enemy("A:100:0:10", 0)]
        res = pt.plans(hand("Strike", "Strike", "Defend", "Defend"), pt.Player(energy=2, hp=5), e)
        o = pt.rank(res, "balanced")[0]
        self.assertFalse(o["dies"])
        self.assertEqual(o["block"], 10)

    def test_personal_hive(self):
        e = pt.parse_enemy("Ento:145:0:0", 0)
        e.hive = 1
        o = pt.simulate(hand("Twin Strike"), [0], pt.Player(energy=3), [e])
        self.assertEqual(o["hive_cards"], 2)       # two damage instances, one card each
        e2 = pt.parse_enemy("Ento:145:0:0", 0)
        e2.hive = 1
        res = pt.plans(hand("Twin Strike", "Strike"), pt.Player(energy=1), [e2])
        self.assertEqual(pt.rank(res, "balanced")[0]["plays"][0].split(" →")[0], "Strike")  # Strike 6 - 5 beats Twin Strike 10 - 2 x 5

    def test_existing_weak_not_counted_twice(self):
        # An enemy already Weak shows 9 (from 12); the planner must not reduce it again
        e = pt.parse_enemy("A:50:0:9:weak", 0)
        o = pt.simulate(hand("Strike"), [0], pt.Player(energy=3), [e])
        self.assertEqual(o["incoming"], 9)
        # Weak applied this turn does reduce the shown intent
        o = pt.simulate(hand("Uppercut"), [0], pt.Player(energy=3), [pt.parse_enemy("A:50:0:12", 0)])
        self.assertEqual(o["incoming"], 9)

    def test_slippery_stacks_credited(self):
        # Against 9 Slippery and a 3-damage intent: Strike + Strike (2 dealt, 3 lost, 2 stacks) against Strike + Defend
        # (1 dealt, 0 lost, 1 stack); without the stack credit Strike + Defend wins (1 > -1), with 3 per stack 5 > 4
        e = [pt.parse_enemy("Vantom:173:0:3:slippery=9", 0)]
        res = pt.plans(hand("Strike", "Strike", "Defend"), pt.Player(energy=2, hp=60), e)
        o = pt.rank(res, "balanced")[0]
        self.assertEqual(o["slippery_stripped"], 2)
        self.assertGreater(pt.SLIPPERY_VALUE, 0)

    def test_forgotten_ritual_condition(self):
        ids = lambda *c: [pt.card_from_extract(i, x) for i, x in enumerate(c)]  # noqa: E731
        e = [pt.parse_enemy("A:100:0:10", 0)]
        # v0.111.1 (the card data is patched to it): no exhaust needed
        self.assertFalse(ids("FORGOTTEN_RITUAL")[0].needs_exhaust)
        four = ids("FORGOTTEN_RITUAL", "STRIKE_IRONCLAD", "STRIKE_IRONCLAD", "STRIKE_IRONCLAD")
        self.assertIsNotNone(pt.simulate(four, [None, 0, 0, 0], pt.Player(energy=3), e))
        # the older card: energy only after an exhaust this turn
        four[0].needs_exhaust = True
        self.assertIsNone(pt.simulate(four, [None, 0, 0, 0], pt.Player(energy=3), e))
        h = ids("FORGOTTEN_RITUAL", "TRUE_GRIT", "STRIKE_IRONCLAD", "STRIKE_IRONCLAD", "STRIKE_IRONCLAD")
        h[0].needs_exhaust = True
        o = pt.rank(pt.plans(h, pt.Player(energy=3, hp=50), e), "balanced")[0]
        self.assertEqual([p.split(" →")[0] for p in o["plays"]][:2], ["True Grit", "Forgotten Ritual"])
        self.assertEqual((o["dealt"], o["block"]), (18, 7))

    def test_dismantle_twice_on_vulnerable(self):
        ids = lambda *c: [pt.card_from_extract(i, x) for i, x in enumerate(c)]  # noqa: E731
        self.assertEqual(pt.simulate(ids("DISMANTLE"), [0], pt.Player(energy=3), [pt.parse_enemy("A:100:0:0", 0)])["dealt"], 8)
        self.assertEqual(pt.simulate(ids("DISMANTLE"), [0], pt.Player(energy=3), [pt.parse_enemy("A:100:0:0:vuln", 0)])["dealt"], 24)

    def test_mangle_flame_barrier_body_slam_fiend_fire(self):
        ids = lambda *c: [pt.card_from_extract(i, x) for i, x in enumerate(c)]  # noqa: E731
        o = pt.simulate(ids("MANGLE"), [0], pt.Player(energy=3), [pt.parse_enemy("A:100:0:14", 0)])
        self.assertEqual(o["incoming"], 4)                     # 10 Strength lost this turn: 14 -> 4
        o = pt.simulate(ids("FLAME_BARRIER"), [None], pt.Player(energy=3), [pt.parse_enemy("A:100:0:3x3", 0)])
        self.assertEqual((o["block"], o["dealt"]), (12, 12))  # 4 back on each of 3 hits
        o = pt.rank(pt.plans(ids("BODY_SLAM", "DEFEND_IRONCLAD", "DEFEND_IRONCLAD"), pt.Player(energy=3, hp=50),
                             [pt.parse_enemy("A:100:0:0", 0)]), "balanced")[0]
        self.assertEqual((o["plays"][-1].split(" →")[0], o["dealt"]), ("Body Slam", 10))  # after both Defends
        res = pt.plans(ids("FIEND_FIRE", "STRIKE_IRONCLAD", "WOUND", "DEFEND_IRONCLAD", "BECKON"), pt.Player(energy=3, hp=50),
                       [pt.parse_enemy("A:100:0:0", 0)])
        o = pt.rank(res, "balanced")[0]
        self.assertEqual((o["plays"], o["dealt"], o["hp_lost"]), (["Fiend Fire → A[0]"], 28, 0))  # 4 cards exhausted, Beckon too

    def test_strength_timing_and_setup_cards(self):
        ids = lambda *c: [pt.card_from_extract(i, x) for i, x in enumerate(c)]  # noqa: E731
        e = lambda s="A:100:0:0": [pt.parse_enemy(s, 0)]  # noqa: E731
        self.assertEqual(pt.simulate(ids("FIGHT_ME"), [0], pt.Player(energy=3), e())["dealt"], 10)  # its +2 comes after its hits
        o = pt.rank(pt.plans(ids("STRIKE_IRONCLAD", "SETUP_STRIKE", "STRIKE_IRONCLAD"), pt.Player(energy=3, hp=50), e()), "balanced")[0]
        self.assertEqual((o["plays"][0].split(" →")[0], o["dealt"]), ("Setup Strike", 25))  # 7, then 9 + 9
        o = pt.rank(pt.plans(ids("RAGE", "STRIKE_IRONCLAD", "STRIKE_IRONCLAD", "STRIKE_IRONCLAD"), pt.Player(energy=3, hp=50),
                             e("A:100:0:9")), "safe")[0]
        self.assertEqual(o["block"], 9)                                  # 3 per Attack after Rage
        o = pt.rank(pt.plans(ids("UNRELENTING", "BASH", "STRIKE_IRONCLAD"), pt.Player(energy=3, hp=50), e()), "balanced")[0]
        self.assertEqual(o["dealt"], 31)                                 # Bash free after Unrelenting: 14 + 8 + 9
        self.assertEqual(pt.simulate(ids("FEEL_NO_PAIN", "TRUE_GRIT"), [None, None], pt.Player(energy=3), e())["block"], 10)
        self.assertEqual(pt.simulate(ids("TRUE_GRIT"), [None], pt.Player(energy=3, fnp=4), e())["block"], 11)

    def test_playable_statuses_sandpit_and_toxic(self):
        ids = lambda *c: [pt.card_from_extract(i, x) for i, x in enumerate(c)]  # noqa: E731
        self.assertTrue(all(c.playable for c in ids("FRANTIC_ESCAPE", "TOXIC", "SLIMED", "DEBRIS")))
        self.assertFalse(ids("WOUND")[0].playable)
        h = ids("FRANTIC_ESCAPE", "STRIKE_IRONCLAD", "STRIKE_IRONCLAD")
        o = pt.rank(pt.plans(h, pt.Player(energy=2, hp=50, sandpit=1), [pt.parse_enemy("A:300:0:5", 0)]), "balanced")[0]
        self.assertIn("Frantic Escape", o["plays"])                 # Sandpit 1 at the end of the turn would kill you
        self.assertFalse(o["dies"])
        o = pt.rank(pt.plans(h, pt.Player(energy=2, hp=50, sandpit=3), [pt.parse_enemy("A:300:0:5", 0)]), "balanced")[0]
        self.assertIn("Frantic Escape", o["plays"])                 # builds a buffer while it is cheap
        o = pt.rank(pt.plans(h, pt.Player(energy=2, hp=50, sandpit=4), [pt.parse_enemy("A:300:0:5", 0)]), "balanced")[0]
        self.assertNotIn("Frantic Escape", o["plays"])              # the buffer is full
        h = ids("TOXIC", "DEFEND_IRONCLAD", "STRIKE_IRONCLAD")
        o = pt.rank(pt.plans(h, pt.Player(energy=2, hp=50), [pt.parse_enemy("A:300:0:8", 0)]), "safe")[0]
        self.assertEqual((sorted(o["plays"]), o["hp_lost"]), (["Defend", "Toxic"], 3))  # Toxic held would cost 5 more
        h = [pt.card_from_extract(0, "WITHER"), pt.card_from_extract(1, "DEFEND_IRONCLAD")]  # newer than the extract
        o = pt.rank(pt.plans(h, pt.Player(energy=1, hp=30), [pt.parse_enemy("Aeon:500:0:4", 0)]), "safe")[0]
        self.assertEqual((h[0].playable, o["hp_lost"]), (False, 2))      # Wither 3 + intent 4 - Defend 5
        w = pt.card_from_extract(0, "WITHER", cost=1, playable=True)   # a live state that lets it be played
        o = pt.rank(pt.plans([w], pt.Player(energy=1, hp=30), [pt.parse_enemy("Aeon:500:0:0", 0)]), "safe")[0]
        self.assertEqual((o["plays"], o["hp_lost"]), (["Wither"], 0))

    def test_powers_from_state_limits_enrage_disintegration(self):
        st = {"combat": {"player": {"current_hp": 40, "energy": 3, "block": 0,
                                    "powers": [{"power_id": "DISINTEGRATION_POWER", "amount": 6}, {"power_id": "RINGING_POWER", "amount": 1}]},
                         "hand": [{"index": 0, "card_id": "DEFEND_IRONCLAD", "energy_cost": 1, "playable": True},
                                  {"index": 1, "card_id": "STRIKE_IRONCLAD", "energy_cost": 1, "playable": True}],
                         "enemies": [{"index": 0, "enemy_id": "TEST_SUBJECT", "current_hp": 100, "block": 0, "is_alive": True,
                                      "powers": [{"power_id": "ENRAGE_POWER", "amount": 2}], "intents": [{"damage": 10, "hits": 1}]}]}}
        hand, player, enemies = pt.from_state(st)
        self.assertEqual((player.max_cards, player.end_turn_dmg, enemies[0].enrage), (1, 6, 2))
        o = pt.rank(pt.plans(hand, player, enemies), "safe")[0]
        self.assertEqual((o["plays"], o["incoming"], o["hp_lost"]), (["Defend"], 18, 13))  # 10 + 2 Enrage (a Skill) + 6
        e = [pt.parse_enemy("TS:100:0:10", 0)]
        e[0].enrage = 2
        o = pt.simulate([pt.card_from_extract(0, "STRIKE_IRONCLAD")], [0], pt.Player(energy=1), e)
        self.assertEqual(o["incoming"], 10)                     # an Attack does not feed Enrage

    def test_hardened_shell_thorns_artifact(self):
        ids = lambda *c: [pt.card_from_extract(i, x) for i, x in enumerate(c)]  # noqa: E731
        e = pt.parse_enemy("Colony:60:0:10", 0)
        e.hp_cap = 20
        o = pt.simulate(ids(*["STRIKE_IRONCLAD"] * 4), [0] * 4, pt.Player(energy=4), [e])
        self.assertEqual(o["dealt"], 20)                                   # 24 capped at 20 for the turn
        e = pt.parse_enemy("T:60:0:0", 0)
        e.thorns = 3
        self.assertEqual(pt.simulate(ids("TWIN_STRIKE"), [0], pt.Player(energy=3), [e])["hp_lost"], 6)  # 3 per hit
        e = pt.parse_enemy("A:100:0:10", 0)
        e.artifact = 1
        self.assertEqual(pt.simulate(ids("BASH", "STRIKE_IRONCLAD"), [0, 0], pt.Player(energy=3), [e])["dealt"], 14)  # no Vulnerable
        e = pt.parse_enemy("Exo:40:0:0", 0)
        e.hit_cap = 5
        self.assertEqual(pt.simulate(ids("BASH", "TWIN_STRIKE"), [0, 0], pt.Player(energy=3), [e])["dealt"], 15)  # three hits of 5
        e = pt.parse_enemy("Eel:80:0:20", 0)
        e.shriek = 70
        o = pt.simulate(ids("STRIKE_IRONCLAD"), [0], pt.Player(energy=3), [e])
        self.assertEqual(o["incoming"], 20)                                # 74 HP left: above the threshold
        e = pt.parse_enemy("Eel:80:0:20", 0)
        e.shriek = 70
        o = pt.simulate(ids("STRIKE_IRONCLAD", "STRIKE_IRONCLAD"), [0, 0], pt.Player(energy=3), [e])
        self.assertEqual(o["incoming"], 0)                                 # 68 HP: stunned
        e = pt.parse_enemy("Prism:160:0:15", 0)
        e.taint = 2
        o = pt.simulate(ids("DEFEND_IRONCLAD", "DEFEND_IRONCLAD"), [None, None], pt.Player(energy=2), [e])
        self.assertEqual(o["incoming"], 19)                                # two Skills Tainted 2: 15 + 4
        e = pt.parse_enemy("Gardener:30:0:5", 0)
        e.skittish = 6
        o = pt.simulate(ids("STRIKE_IRONCLAD", "STRIKE_IRONCLAD"), [0, 0], pt.Player(energy=2), [e])
        self.assertEqual(o["dealt"], 6)                                    # the second Strike hits 6 Block
        e = pt.parse_enemy("Phrog:6:0:4x4", 0)
        e.infested = True
        o = pt.simulate(ids("STRIKE_IRONCLAD"), [0], pt.Player(energy=1), [e])
        self.assertFalse(o["all_dead"])                                    # Wrigglers come next
        self.assertEqual((ids("BURN")[0].held_dmg, ids("INFECTION")[0].held_dmg, ids("TOXIC")[0].held_dmg), (2, 3, 5))
        h = ids("DEFEND_IRONCLAD", "STRIKE_IRONCLAD")
        o = pt.rank(pt.plans(h, pt.Player(energy=2, hp=50, hexed=True), [pt.parse_enemy("A:100:0:0", 0)]), "balanced")[0]
        self.assertEqual(len(o["plays"]), 2)        # Hex: play the Defend too rather than lose it
        slugs = [pt.parse_enemy("Slug:6:0:8", 0), pt.parse_enemy("Slug:26:0:3x2", 1)]
        slugs[1].ravenous = True
        o = pt.simulate(ids("STRIKE_IRONCLAD"), [0], pt.Player(energy=1), slugs)
        self.assertEqual(o["incoming"], 0)          # the first slug dies; the other eats it and is stunned
        rock = pt.parse_enemy("Rock:46:0:15", 0)
        rock.imbalanced = True
        o = pt.simulate(ids("DEFEND_IRONCLAD", "DEFEND_IRONCLAD", "DEFEND_IRONCLAD"), [None] * 3, pt.Player(energy=3), [rock])
        self.assertEqual(o["stun_bonus"], 15)       # Headbutt fully blocked: it is stunned next turn

    def test_crab_rage(self):
        ids = lambda *c: [pt.card_from_extract(i, x) for i, x in enumerate(c)]  # noqa: E731
        es = [pt.parse_enemy("Rocket:6:0:10", 0), pt.parse_enemy("Crusher:60:0:6x2", 1)]
        for e in es:
            e.crab_rage = True
        o = pt.simulate(ids("STRIKE_IRONCLAD", "STRIKE_IRONCLAD"), [0, 1], pt.Player(energy=3), es)
        self.assertEqual(o["dealt"], 6)                    # Rocket dies; Crusher gets 99 Block, so the second Strike is wasted
        self.assertEqual(o["incoming"], 22)                # Crusher's 6x2 becomes 11x2

    def test_more_potions(self):
        e = lambda s="A:100:0:20": [pt.parse_enemy(s, 0)]  # noqa: E731
        h = [pt.card_from_potion(0, "BLOOD_POTION"), pt.card_from_extract(1, "STRIKE_IRONCLAD")]
        o = pt.rank(pt.plans(h, pt.Player(energy=1, hp=30, max_hp=80), e()), "balanced", pt.POTION_COST["boss"])[0]
        self.assertEqual(o["hp_lost"], 4)                     # 20 incoming, healed 16 (20% of 80)
        o = pt.rank(pt.plans(h, pt.Player(energy=1, hp=80, max_hp=80), e()), "balanced", pt.POTION_COST["boss"])[0]
        self.assertEqual(o["potions"], 0)                     # nothing to heal at full HP
        self.assertEqual(pt.simulate([pt.card_from_potion(0, "POTION_SHAPED_ROCK")], [0], pt.Player(energy=0),
                                     e("A:100:0:0:vuln"))["dealt"], 15)  # flat: Vulnerable does not apply

    def test_commands_stop_after_hand_changes(self):
        h = [pt.card_from_extract(i, c) for i, c in enumerate(("DEFEND_IRONCLAD", "TRUE_GRIT", "STRIKE_IRONCLAD"))]
        self.assertTrue(h[1].changes_hand)                         # True Grit exhausts a card: later indexes are unknown
        o = pt.simulate(h, [None, None, 0], pt.Player(energy=3), [pt.parse_enemy("A:50:0:0", 0)])
        cmds = pt.commands(o, h)
        self.assertFalse(cmds[1].startswith("#"))
        self.assertTrue(cmds[2].startswith("# after re-planning"))  # the Strike after True Grit waits for a fresh state

    def test_minions_flee_with_their_leader(self):
        ids = lambda *c: [pt.card_from_extract(i, x) for i, x in enumerate(c)]  # noqa: E731
        es = [pt.parse_enemy("Priest:6:0:8", 0), pt.parse_enemy("Follower:58:0:5", 1)]
        es[1].minion = True
        o = pt.simulate(ids("STRIKE_IRONCLAD"), [0], pt.Player(energy=1), es)
        self.assertTrue(o["all_dead"])                                # the Priest dead ends the fight
        self.assertEqual(o["hp_lost"], 0)                             # no enemy turn after the fight ends

    def test_tender(self):
        h = [pt.card_from_extract(i, c) for i, c in enumerate(("STRIKE_IRONCLAD", "STRIKE_IRONCLAD", "DEFEND_IRONCLAD"))]
        o = pt.simulate(h, [0, 0, None], pt.Player(energy=3, tender=1), [pt.parse_enemy("A:100:0:0", 0)])
        self.assertEqual((o["dealt"], o["block"]), (11, 3))  # 6, then 5; Defend after two cards: 5 - 2

    def test_colossus(self):
        h = [pt.card_from_extract(0, "COLOSSUS")]
        self.assertTrue(h[0].colossus)
        o = pt.simulate(h, [None], pt.Player(energy=1), [pt.parse_enemy("A:50:0:20:vuln", 0), pt.parse_enemy("B:50:0:10", 1)])
        self.assertEqual(o["incoming"], 20)                 # 20 halved to 10 (Vulnerable), plus 10 from B

    def test_unleash_and_next_turn_energy(self):
        h = [pt.card_from_extract(0, "BODYGUARD"), pt.card_from_extract(1, "UNLEASH")]
        o = pt.simulate(h, [None, 0], pt.Player(energy=2, osty_hp=3), [pt.parse_enemy("A:100:0:0", 0)])
        self.assertEqual(o["dealt"], 14)                                  # 6 + Osty 3 + Summon 5
        o = pt.simulate([pt.card_from_extract(0, "UNLEASH")], [0], pt.Player(energy=1, osty_hp=0), [pt.parse_enemy("A:100:0:0", 0)])
        self.assertEqual(o["dealt"], 0)                                   # Osty dead: the attack fizzles
        self.assertEqual(pt.card_from_extract(0, "INVOKE").energy, 0)     # "Gain 2 Energy Next Turn" is not this turn's

    def test_doom(self):
        ids = lambda *c: [pt.card_from_extract(i, x) for i, x in enumerate(c)]  # noqa: E731
        o = pt.simulate(ids("SCOURGE"), [0], pt.Player(energy=1, hp=40), [pt.parse_enemy("A:12:0:5", 0)])
        self.assertEqual((o["doomed"], o["doom_dealt"], o["all_dead"], o["incoming"]), (1, 12, False, 5))  # attacks, then dies
        o = pt.simulate(ids("BORROWED_TIME"), [None], pt.Player(energy=1, hp=3), [pt.parse_enemy("A:50:0:0", 0)])
        self.assertTrue(o["dies"])                                     # 3 Doom on you at 3 HP: dead at the end of your turn

    def test_paper_cuts(self):
        e = pt.parse_enemy("Scroll:30:0:4x2", 0)
        e.paper_cuts = 1
        o = pt.simulate([pt.card_from_extract(0, "STRIKE_IRONCLAD")], [0], pt.Player(energy=1), [e])
        self.assertEqual(o["hp_lost"], 8 + 2)                  # 8 damage plus 1 max HP for each of its 2 hits
        o = pt.simulate([pt.card_from_extract(0, "DEFEND_IRONCLAD"), pt.card_from_extract(1, "DEFEND_IRONCLAD")], [None, None],
                        pt.Player(energy=2), [e])
        self.assertEqual(o["hp_lost"], 0)                      # fully blocked: no cuts

    def test_lasting_potions_valued_like_powers(self):
        h = [pt.card_from_potion(0, "STRENGTH_POTION"), pt.card_from_extract(1, "DEFEND_IRONCLAD")]
        e = [pt.parse_enemy("A:100:0:5", 0)]
        boss = pt.rank(pt.plans(h, pt.Player(energy=1, hp=50), e), "balanced", pt.POTION_COST["boss"], pt.POWER_VALUE["boss"])[0]
        hall = pt.rank(pt.plans(h, pt.Player(energy=1, hp=50), e), "balanced", pt.POTION_COST["hallway"], pt.POWER_VALUE["hallway"])[0]
        self.assertEqual((boss["potions"], hall["potions"]), (1, 0))   # drink it in a boss fight, keep it in a hallway

    def test_beckon_held_loss(self):
        h = [pt.card_from_extract(0, "BECKON"), pt.card_from_extract(1, "STRIKE_IRONCLAD")]
        self.assertEqual((h[0].held_loss, h[0].cost, h[0].playable), (6, 1, True))
        e = [pt.parse_enemy("Fysh:211:0:0", 0)]
        res = pt.plans(h, pt.Player(energy=1, hp=50), e)
        o = pt.rank(res, "safe")[0]
        self.assertEqual(o["plays"], ["Beckon"])     # 1 energy: getting rid of Beckon saves 6 HP; Strike saves nothing
        self.assertEqual(o["hp_lost"], 0)
        strike_only = next(x for x in res if x["plays"] and x["plays"][0].startswith("Strike"))
        self.assertEqual(strike_only["hp_lost"], 6)  # Beckon still held at the end of the turn
        # held loss counts toward the survival guard
        res = pt.plans(h, pt.Player(energy=1, hp=6), e)
        self.assertTrue(strike_only and next(x for x in res if x["plays"] and x["plays"][0].startswith("Strike"))["dies"])


if __name__ == "__main__":
    unittest.main()
