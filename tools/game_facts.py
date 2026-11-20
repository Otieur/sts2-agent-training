#!/usr/bin/env python3
"""Checks the facts about the game's code that our tools and rules depend on.

Each fact was read from sts2.dll v0.111.1 and is cited in docs/simulator-integrity.md, tools/plan_turn.py or
tools/play_turn.py. After a game update a fact may stop being true without any error elsewhere: this script
re-reads them and reports every change. Run it from docs/runbooks/game-patch.md.

    python3 -I tools/game_facts.py            # rebuild the assembly index and call graph (about 40 s), then check
    python3 -I tools/game_facts.py --cached   # reuse data/asm/

Writes reports/game-check/facts.md. Exit code 1 if any fact changed.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "tools"))
from game_cards import GAME_DATA, decimals_and_vars, game_build, parse_methods  # noqa: E402

ASM = PROJECT / "data" / "asm"
REPORT = PROJECT / "reports" / "game-check" / "facts.md"
CORE = "MegaCrit.Sts2.Core."
UI = re.compile(r"MegaCrit\.Sts2\.Core\.(Nodes|AutoSlay|DevConsole|Assets|Debug|RichTextTags|Timeline|Platform|TestSupport)\.")
NOT_LOGIC = re.compile(r"Core\.(Nodes|AutoSlay|TestSupport|Assets|Localization|Logging|Modding|DevConsole|Debug)\.|SfxCmd|VfxCmd")


def asm(mode, *args):
    r = subprocess.run(["dotnet", "run", "tools/asm/asm.cs", "--", mode, str(GAME_DATA / "sts2.dll"), *args], cwd=PROJECT,
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        sys.exit(f"could not read the game assembly: {r.stderr[-300:]}")
    return r.stdout


def short(name):
    name = re.sub(r"\+<([A-Za-z_]+)>d__\d+::MoveNext", r"::\1", name)
    return re.sub(r"\+<>c[^:]*::<([A-Za-z_.]+)>.*", r"::\1", name).replace(CORE, "")


def load(cached):
    ASM.mkdir(parents=True, exist_ok=True)
    idx, calls, moves, powers = ASM / "sts2-index.txt", ASM / "sts2-calls.tsv", ASM / "monsters-il.txt", ASM / "powers-il.txt"
    if not cached or not idx.exists() or not calls.exists():
        asm("index", str(idx))
        asm("calls", str(calls))
    if not cached or not moves.exists():
        moves.write_text(asm("il", CORE + "Models.Monsters."))
    if not cached or not powers.exists():
        powers.write_text(asm("il", CORE + "Models.Powers."))
    graph = {}
    for line in calls.read_text().splitlines():
        n, _, c = line.partition("\t")
        graph.setdefault(n, []).extend(c.split("|") if c else [])
    return idx.read_text(), graph, moves.read_text(), powers.read_text()


def readers(graph, pattern, scope=None, exclude=None):
    rx = re.compile(pattern)
    return sorted({short(n) for n, cs in graph.items()
                   if n.startswith(CORE) and (scope is None or re.search(scope, n)) and not (exclude and exclude.search(n))
                   and any(rx.search(c) for c in cs)})


def multi_attack_moves(il):
    """Moves whose intent list holds more than one attack intent (the planner counts one attack intent per enemy)."""
    out, cur, arr = [], None, None
    for line in il.splitlines():
        if line.startswith("### "):
            cur, arr = line[4:], None
            continue
        op = line.strip().split(" ", 1)[1] if " " in line.strip() else ""
        if cur is None or "GenerateMoveStateMachine" not in cur:
            continue
        if op.startswith("newarr") and "AbstractIntent" in op:
            arr = []
        elif arr is not None and op.startswith("newobj new:") and "Intents." in op:
            arr.append(op.split("Intents.")[1].split("::")[0])
        elif arr is not None and op.startswith("newobj new:") and "MoveState::.ctor" in op:
            if sum(1 for x in arr if "Attack" in x or "DeathBlow" in x) > 1:
                out.append(short(cur.split("::")[0]))
            arr = None
    return sorted(set(out))


def power_var(powers_il, cls, name):
    methods = parse_methods(powers_il).get(CORE + "Models.Powers." + cls, {})
    for _vt, n, v in decimals_and_vars(methods.get("get_CanonicalVars", [])):
        if n == name:
            return v
    return None


def facts(index, graph, moves_il, powers_il):
    """[(fact, where it is used, expected, found)]"""
    def enum(type_name):
        return sorted(re.findall(rf"^  F {re.escape(CORE + type_name)}::([A-Za-z]+ = \d+)", index, re.M))

    def calls_of(method_regex):
        return [c for n, cs in graph.items() if re.search(method_regex, n) for c in cs]

    wait = calls_of(r"Commands\.Cmd\+<Wait>d__\d+::MoveNext$")
    init = calls_of(r"Runs\.RunManager::InitializeShared$")
    end = calls_of(r"Combat\.CombatManager\+<EndCombatInternal>d__\d+::MoveNext$")
    out = [
        ("Hidden fast mode value", "Instant mode (proposals/engine-simulation-spike.md)",
         ["None = 0", "Normal = 1", "Fast = 2", "Instant = 3"], sorted(enum("Settings.FastModeType"), key=lambda s: int(s.split()[-1]))),
        ("Cmd.Wait checks NonInteractiveMode and FastMode", "FI-2b",
         [True, True], [any("NonInteractiveMode::get_IsActive" in c for c in wait), any("PrefsSave::get_FastMode" in c for c in wait)]),
        ("NonInteractiveMode is read only by waits and pauses (outside UI)", "FI-2b",
         ["Combat.CombatManager::Pause", "Combat.CombatManager::Unpause", "Combat.CombatManager::WaitForUnpause", "Commands.Cmd::CustomScaledWait",
          "Commands.Cmd::Wait", "GameActions.ActionExecutor::ExecuteActions", "GameActions.GameAction::Execute"],
         readers(graph, r"NonInteractiveMode::get_IsActive", exclude=re.compile(r"Core\.(Nodes|AutoSlay|TestSupport|Assets)\.|SfxCmd|VfxCmd"))),
        ("Game-logic methods that read TestMode", "FI-1 (never turn TestMode on)", 107,
         len({re.sub(r"\+<>c[^:]*::", "::", re.sub(r"\+<([A-Za-z_]+)>d__\d+::MoveNext", r"::\1", n)) for n, cs in graph.items()
              if n.startswith(CORE) and not NOT_LOGIC.search(n) and any(re.search(r"TestMode::get_Is(On|Off)", c) for c in cs)})),
        ("Replays are recorded whenever TestMode is off, and written when a fight ends", "tools/play_turn.py keep_replay; P7.E2",
         [True, True, True], [any("CombatReplayWriter::set_IsEnabled" in c for c in init), any("TestMode::get_IsOn" in c for c in init),
                              any(c.endswith("RunManager::WriteReplay") for c in end)]),
        ("Run-level random streams", "FP-2",
         ["CombatCardGeneration", "CombatCardSelection", "CombatEnergyCosts", "CombatOrbs", "CombatPotionGeneration", "CombatTargets",
          "MonsterAi", "Niche", "Shuffle", "TreasureRoomRelics", "UnknownMapPoint", "UpFront"],
         sorted(x.split(" = ")[0] for x in enum("Entities.Rngs.RunRngType"))),
        ("Per-player random streams", "FP-2", ["Rewards", "Shops", "Transformations"],
         sorted(x.split(" = ")[0] for x in enum("Entities.Rngs.PlayerRngType"))),
        ("Places that create a random generator (outside UI and debug)", "FP-2 (hidden streams beyond the named ones)",
         ["Combat.CombatState::CreateCreature", "Map.SpoilsActMap::.ctor", "Map.StandardActMap::CreateFor",
          "Models.EncounterModel::DebugRandomizeRng", "Models.EncounterModel::GenerateMonstersWithSlots", "Models.EventModel::BeginEvent",
          "Models.Modifiers.BigGameHunter::ModifyGeneratedMap", "Models.Relics.Byrdpip::AfterObtained", "Models.Relics.FurCoat::AddMarkedRooms",
          "Models.Relics.PaelsLegion::AfterObtained", "Multiplayer.Game.EventSynchronizer::.ctor",
          "Multiplayer.Game.Lobby.StartRunLobby::BeginRunLocally", "Multiplayer.Game.MapSelectionSynchronizer::.ctor",
          "Random.PlayerRngSet::CreateRng", "Random.PlayerRngSet::FromSerializable", "Random.Rng::.cctor", "Runs.NullRunState::get_Odds",
          "Runs.RunRngSet::CreateRng", "Runs.RunRngSet::FromSave", "Runs.RunRngSet::MockRng"],
         readers(graph, r"^new:MegaCrit\.Sts2\.Core\.Random\.Rng::\.ctor$", exclude=UI)),
        ("No unseeded randomness in game logic", "FI-10", [],
         readers(graph, r"new:System\.Random::\.ctor|System\.Random::get_Shared|Guid::NewGuid", exclude=UI)),
        ("Saves written from combat, rooms and run flow", "SA-1 (stubs in the simulator)",
         ["Combat.CombatManager::EndCombatInternal", "Rooms.EventRoom::OnEventStateChanged", "Runs.RunHistoryUtilities::CreateRunHistoryEntry",
          "Runs.RunManager::EnterMapPointInternal"],
         readers(graph, r"SaveManager::Save[A-Za-z]*$", scope=r"Core\.(Combat|Rooms|Runs)\.")),
        ("Achievement check at the end of a fight", "SA-2", [True], [any("AchievementsHelper::" in c for c in end)]),
        ("Monsters with a hidden intent", "FP-7 (move_id must not reveal it)",
         ["Models.Monsters.Architect", "Models.Monsters.BigDummy", "Models.Monsters.DeprecatedMonster",
          "Models.Monsters.Mocks.MockArtifactMonster", "Models.Monsters.Mocks.MockIntangibleMonster",
          "Models.Monsters.Mocks.MockPlatingMonster", "Models.Monsters.Mocks.MockReattachMonster", "Models.Monsters.OneHpMonster",
          "Models.Monsters.TenHpMonster"],
         sorted({short(n).split("::")[0] for n, cs in graph.items() if any("Intents.HiddenIntent::.ctor" in c for c in cs)})),
        ("Damage property flags", "tools/plan_turn.py (Unpowered damage ignores Strength and Vulnerable)",
         ["Move = 8", "SkipHurtAnim = 16", "Unblockable = 2", "Unpowered = 4"], enum("ValueProps.ValueProp")),
        ("Moves with more than one attack intent", "tools/plan_turn.py from_state (one attack intent per enemy)", [], multi_attack_moves(moves_il)),
        ("Vulnerable, Weak and Flutter multipliers", "tools/calc.py, tools/plan_turn.py", [1.5, 0.75, 50],
         [power_var(powers_il, "VulnerablePower", "DamageIncrease"), power_var(powers_il, "WeakPower", "DamageDecrease"),
          power_var(powers_il, "FlutterPower", "DamageDecrease")]),
    ]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cached", action="store_true", help="reuse data/asm/")
    a = ap.parse_args(argv)
    if not (GAME_DATA / "sts2.dll").exists():
        sys.exit("game assembly not found (see docs/environment.md)")
    rows = facts(*load(a.cached))
    build = game_build()
    L = [f"# Facts about the game's code that our tools and rules depend on ({build})", "",
         "Generated by `tools/game_facts.py`. Expected values were read from v0.111.1 (commit cc1f9462). A CHANGED row means a "
         "rule in `docs/simulator-integrity.md` or an assumption in a tool must be re-checked before it is relied on.", "",
         "| Fact | Used by | Status | Detail |", "|---|---|---|---|"]
    changed = 0
    for name, used, expected, found in rows:
        ok = expected == found
        changed += not ok
        if ok:
            detail = f"{len(found)} items" if isinstance(found, list) and len(found) > 4 else str(found)
        elif isinstance(expected, list) and isinstance(found, list):
            detail = f"added: {[x for x in found if x not in expected]}; removed: {[x for x in expected if x not in found]}"
        else:
            detail = f"expected {expected}, found {found}"
        L.append(f"| {name} | {used} | {'ok' if ok else '**CHANGED**'} | {detail} |")
        print(f"{'ok     ' if ok else 'CHANGED'} {name}" + ("" if ok else f": {detail}"))
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(L) + "\n")
    print(f"{len(rows) - changed} of {len(rows)} facts hold for {build}. Report: {REPORT.relative_to(PROJECT)}")
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
