"""Offline tests for the parsers in tools/game_cards.py, tools/game_monsters.py and the game-number overlay in
tools/build_encounter_notes.py. They use short IL listings in the format tools/asm/asm.cs prints; the game is not needed."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_encounter_notes as ben  # noqa: E402
import game_cards as gc  # noqa: E402
import game_monsters as gm  # noqa: E402

NS = "MegaCrit.Sts2.Core.Models.Cards."
DV = "MegaCrit.Sts2.Core.Localization.DynamicVars."
IL = f"""### {NS}Bash::.ctor
  0000 ldarg.0
  0001 ldc.i4.2
  0002 ldc.i4.1
  0003 ldc.i4.1
  0004 ldc.i4.2
  0005 ldc.i4.1
  0006 call MegaCrit.Sts2.Core.Models.CardModel::.ctor
  000B ret
### {NS}Bash::get_CanonicalVars
  0000 ldc.i4.2
  0001 newarr {DV}DynamicVar
  0006 dup
  0007 ldc.i4.0
  0008 ldc.i4.8
  0009 newobj new:System.Decimal::.ctor
  000E ldc.i4.8
  000F newobj new:{DV}DamageVar::.ctor
  0014 stelem.ref
  0015 dup
  0016 ldc.i4.1
  0017 ldc.i4.2
  0018 newobj new:System.Decimal::.ctor
  001D newobj new:{DV}PowerVar`1<MegaCrit.Sts2.Core.Models.Powers.VulnerablePower>::.ctor
  0022 stelem.ref
  0023 newobj new:<>z__ReadOnlyArray`1<{DV}DynamicVar>::.ctor
  0028 ret
### {NS}Bash::OnUpgrade
  0000 ldarg.0
  0001 call MegaCrit.Sts2.Core.Models.CardModel::get_DynamicVars
  0006 callvirt {DV}DynamicVarSet::get_Damage
  000B ldc.i4.2
  000C newobj new:System.Decimal::.ctor
  0011 callvirt {DV}DynamicVar::UpgradeValueBy
  0016 ldarg.0
  0017 call MegaCrit.Sts2.Core.Models.CardModel::get_DynamicVars
  001C ldstr str:VulnerablePower
  0021 callvirt {DV}DynamicVarSet::get_Item
  0026 ldsfld f:System.Decimal::One
  002B callvirt {DV}DynamicVar::UpgradeValueBy
  0030 ret
### {NS}BodySlam::.ctor
  0000 ldarg.0
  0001 ldc.i4.1
  0002 ldc.i4.1
  0003 ldc.i4.2
  0004 ldc.i4.2
  0005 ldc.i4.1
  0006 call MegaCrit.Sts2.Core.Models.CardModel::.ctor
### {NS}BodySlam::OnUpgrade
  0000 ldarg.0
  0001 call MegaCrit.Sts2.Core.Models.CardModel::get_EnergyCost
  0006 ldc.i4.m1
  0007 callvirt MegaCrit.Sts2.Core.Entities.Cards.CardEnergyCost::UpgradeBy
  000C ret
### {NS}Bash+<OnPlay>d__5::MoveNext
  0000 ldarg.0
"""


class TestGameCards(unittest.TestCase):
    def test_constants_and_names(self):
        self.assertEqual([gc.const(x) for x in ("ldc.i4.3", "ldc.i4.m1", "ldc.i4.s 25", "ldc.i4 183", "ldarg.0")], [3, -1, 25, 183, None])
        self.assertEqual((gc.snake("StrikeIronclad"), gc.snake("FTLDrive"), gc.snake("OneTwoPunch")), ("STRIKE_IRONCLAD", "FTL_DRIVE", "ONE_TWO_PUNCH"))

    def test_card_facts(self):
        cards = gc.game_cards(IL)
        self.assertEqual(set(cards), {"BASH", "BODY_SLAM"})                      # nested state machines are not cards
        bash = cards["BASH"]
        self.assertEqual((bash["cost"], bash["type"], bash["rarity"], bash["target"]), (2, "Attack", "Basic", "AnyEnemy"))
        self.assertEqual(bash["vars"], [("DamageVar", None, 8), ("PowerVar<VulnerablePower>", None, 2)])
        self.assertEqual(bash["upgrade"], [("Damage", 2), ("VulnerablePower", 1)])
        self.assertEqual(cards["BODY_SLAM"]["upgrade"], [("EnergyCost", -1)])

    def test_decimal_with_scale_and_named_var(self):
        ins = ["ldstr str:DamageIncrease", "ldc.i4.s 15", "ldc.i4.0", "ldc.i4.0", "ldc.i4.0", "ldc.i4.1",
               "newobj new:System.Decimal::.ctor", f"newobj new:{DV}DynamicVar::.ctor"]
        self.assertEqual(gc.decimals_and_vars(ins), [("DynamicVar", "DamageIncrease", 1.5)])
        self.assertEqual(gc.extract_vars("DamageVar(8m, ValueProp.Move), PowerVar<VulnerablePower>(2m)"),
                         [("DamageVar", 8.0), ("PowerVar<VulnerablePower>", 2.0)])

    def test_facts_file_matches_the_planner_loader(self):
        path = Path(__file__).resolve().parent.parent.parent / "knowledge" / "data" / "game-cards-v0.111.1.json"
        cards = json.loads(path.read_text())["cards"]
        self.assertEqual(cards["STRIKE_IRONCLAD"]["vars"][0][:1] + cards["STRIKE_IRONCLAD"]["vars"][0][2:], ["DamageVar", 6])
        self.assertIn(["EnergyCost", -1], cards["BODY_SLAM"]["upgrade"])


class TestGameMonsters(unittest.TestCase):
    def test_numeric_property(self):
        asc = ["ldc.i4.s 9", "ldc.i4.s 30", "ldc.i4.s 26", "call MegaCrit.Sts2.Core.Helpers.AscensionHelper::GetValueIfAscension", "ret"]
        self.assertEqual(gm.numeric_property(asc), {"base": 26, "asc": 30, "level": "DeadlyEnemies"})
        self.assertEqual(gm.numeric_property(["ldc.i4.2", "ret"]), {"base": 2})
        self.assertIsNone(gm.numeric_property(["ldarg.0", "call Something::Else", "ret"]))

    def test_monsters_from_il(self):
        ns = "MegaCrit.Sts2.Core.Models.Monsters."
        text = (f"### {ns}Vantom::get_DismemberDamage\n  0000 ldc.i4.s 9\n  0002 ldc.i4.s 30\n  0004 ldc.i4.s 26\n"
                "  0006 call MegaCrit.Sts2.Core.Helpers.AscensionHelper::GetValueIfAscension\n  000B ret\n"
                f"### {ns}Vantom::get_TakeDamageSfxType\n  0000 ldc.i4.5\n  0001 ret\n"
                f"### {ns}Vantom::get_MinInitialHp\n  0000 ldc.i4.8\n  0001 ldc.i4 183\n  0006 ldc.i4 173\n"
                "  000B call MegaCrit.Sts2.Core.Helpers.AscensionHelper::GetValueIfAscension\n  0010 ret\n")
        self.assertEqual(gm.game_monsters(text), {"VANTOM": {"DismemberDamage": {"base": 26, "asc": 30, "level": "DeadlyEnemies"},
                                                             "MinInitialHp": {"base": 173, "asc": 183, "level": "ToughEnemies"}}})

    def test_move_lists_from_il(self):
        ns = "MegaCrit.Sts2.Core.Models.Monsters."
        mi = "MegaCrit.Sts2.Core.MonsterMoves."
        text = (f"### {ns}Vantom::GenerateMoveStateMachine\n"
                "  0000 ldstr str:INKY_LANCE_MOVE\n  0005 ldarg.0\n  0006 ldc.i4.1\n"
                f"  0007 newarr {mi}Intents.AbstractIntent\n  000C dup\n  000D ldc.i4.0\n"
                f"  000E call {ns}Vantom::get_InkyLanceDamage\n  0013 ldc.i4.2\n"
                f"  0014 newobj new:{mi}Intents.MultiAttackIntent::.ctor\n  0019 stelem.ref\n"
                f"  001A newobj new:{mi}MonsterMoveStateMachine.MoveState::.ctor\n"
                "  001F ldstr str:DISMEMBER_MOVE\n  0024 ldc.i4.2\n"
                f"  0025 newarr {mi}Intents.AbstractIntent\n  002A dup\n  002B ldc.i4.0\n"
                f"  002C call {ns}Vantom::get_DismemberDamage\n  0031 newobj new:{mi}Intents.SingleAttackIntent::.ctor\n  0036 stelem.ref\n"
                f"  0037 dup\n  0038 ldc.i4.1\n  0039 ldc.i4.3\n  003A newobj new:{mi}Intents.StatusIntent::.ctor\n  003F stelem.ref\n"
                f"  0040 newobj new:{mi}MonsterMoveStateMachine.MoveState::.ctor\n")
        self.assertEqual(gm.game_moves(text), {"VANTOM": [
            {"id": "INKY_LANCE_MOVE", "intents": [["MultiAttack", "InkyLanceDamage", 2]]},
            {"id": "DISMEMBER_MOVE", "intents": [["SingleAttack", "DismemberDamage", None], ["Status", 3, None]]}]})


class TestNoteOverlay(unittest.TestCase):
    PROPS = {"MinInitialHp": {"base": 173, "asc": 183, "level": "ToughEnemies"}, "RadiateBlock": {"base": 11, "asc": 13, "level": "DeadlyEnemies"},
             "DismemberDamage": {"base": 26, "asc": 30, "level": "DeadlyEnemies"}, "WhirlwindDamage": {"base": 5}, "WhirlwindRepeat": {"base": 3}}

    def test_hp_and_effects(self):
        self.assertEqual(ben.game_hp(self.PROPS), "173 (183 at A8+)")
        self.assertIsNone(ben.game_hp({}))
        mv = {"move": "DISMEMBER_MOVE", "intent": "SingleAttackIntent(DismemberDamage)+StatusIntent(3)", "effect": "Deal 27 damage, add 3 Wounds"}
        self.assertEqual(ben.game_effect(self.PROPS, mv), "Deal 26 (30 at A9+) damage, add 3 Wounds")
        mv = {"move": "WHIRLWIND_MOVE", "intent": "MultiAttackIntent(WhirlwindDamage, WhirlwindRepeat)", "effect": "Deal 9 damage 4 times"}
        self.assertEqual(ben.game_effect(self.PROPS, mv), "Deal 5 damage 3 times")
        mv = {"move": "RADIATE_MOVE", "intent": "DefendIntent", "effect": "Gain 16 Block"}
        self.assertEqual(ben.game_effect(self.PROPS, mv), "Gain 11 (13 at A9+) Block")
        mv = {"move": "UNKNOWN_MOVE", "intent": "BuffIntent", "effect": "Gain 2 Strength"}
        self.assertEqual(ben.game_effect(self.PROPS, mv), "Gain 2 Strength")       # no game number: the text is kept

    def test_move_lines_from_game_moves(self):
        saved = dict(ben.GAME_MOVES)
        ben.GAME_MOVES.clear()
        ben.GAME_MOVES["X"] = [{"id": "DISMEMBER_MOVE", "intents": [["SingleAttack", "DismemberDamage", None], ["Status", 3, None]]},
                               {"id": "INERTIA_MOVE", "intents": [["SingleAttack", "WhirlwindDamage", None], ["Buff", None, None]]},
                               {"id": "NEW_MOVE", "intents": [["MultiAttack", "WhirlwindDamage", "WhirlwindRepeat"]]}]
        m = {"moves": [{"move": "DISMEMBER_MOVE", "intent": "SingleAttackIntent(DismemberDamage)+StatusIntent(3)", "effect": "Deal 27 damage"},
                       {"move": "INERTIA_MOVE", "intent": "DefendIntent+BuffIntent", "effect": "Gain 10 Block"},
                       {"move": "OLD_MOVE", "intent": "BuffIntent", "effect": "Gain 2 Strength"}]}
        try:
            lines = ben.move_lines("X", m, self.PROPS)
        finally:
            ben.GAME_MOVES.clear(); ben.GAME_MOVES.update(saved)
        self.assertEqual(lines[0], "  - `DISMEMBER_MOVE` Attack 26 (30 at A9+) + Status x3 → Deal 26 (30 at A9+) damage")
        self.assertIn("intents changed since the extract: was Defend+Buff", lines[1])
        self.assertIn("`NEW_MOVE` Attack 5 x 3 `[GAME]` (not in the extract", lines[2])
        self.assertIn("~~`OLD_MOVE`~~ not in the installed game", lines[3])
        self.assertEqual(ben.move_lines("UNKNOWN", {"moves": m["moves"][:1]}, self.PROPS), ["  - `DISMEMBER_MOVE` SingleAttackIntent(DismemberDamage)+StatusIntent(3) → Deal 26 (30 at A9+) damage"])


if __name__ == "__main__":
    unittest.main()
