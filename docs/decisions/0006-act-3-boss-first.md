# 0006: The act 3 boss first: the fight search where it misjudges a fight, then decks for long fights

Date: 2026-11-22 · Status: **accepted** (the Player, 2026-11-22, after run benchmark 16 and the look at its act 3 boss fights: do all of it as proposed and adjust the plan; he also allowed guides from the web as a source of ideas for particular bosses). Amends decision 0005: its ladder, its primary metric and its gates stay; the order of work changes.

## Context
- Run benchmark 16 is the first on a simulator where chest relics reach the player. 8 wins in 104 runs at A0 (7.7%); the best of its four policies 4 of 26. Of 104 runs, 103 reach the act 1 boss and 93 beat it, 77 reach the act 2 boss and 56 beat it, 42 reach the act 3 boss and 8 beat it. The act 3 boss ends 34 of the 96 lost runs.
- At the act 3 boss the Agent holds about what the Player holds in deck size, HP, relics and potions, and wins 19% of the fights where the Player won 13 of 15: Test Subject 3 of 24, Queen 0 of 9, Aeonglass 5 of 9.
- Two causes are in sight (`reports/phase9/boss-replay-2.md`). (1) The fight search valued a lost rollout by the HP of the Test Subject's form alive, so it kept away from killing the first form and died in front of it; a correction exists and is being measured. (2) The decks differ in kind from the Player's: seven more attacks, five fewer skills, a quarter of the energy cards, five fewer upgrades, twice the bottom-tier cards.
- Card rollouts are played to the end of the act by the rule planner, which rewards cards that help the next few hallway fights.
- A whole-run test is a weak instrument for one boss: about a quarter of runs meet the Test Subject, so 30 seeds give about seven such fights per arm.

## Decision
1. **Work goes where the runs end.** After every run benchmark the funnel is read (reached and beaten per act boss, by boss), and the stage that loses the most runs is next. Now: the act 3 boss.
2. **A trace before a rule.** For a boss the Agent loses far more often than the Player, one or two lost fights are replayed with every decision's values kept (`tools/fight_trace.py`) before any rule or model is tried for it.
3. **Fight-search corrections are judged on fights, not on runs.** A change to how the search values or plays a fight is tested as a registered fight benchmark on the situations it concerns (the Agent's from the last run benchmark, the Player's from the history), paired by fight and sample seed. If it passes its registered rule it becomes the default for everything started afterwards, and later run benchmarks show the level. No room type gets less search than it has (decision 0005, item 5, unchanged).
4. **Everything that stands for "distance to a win" or "the fight is over" is checked against the game's code:** enemies that revive or change form, minions, powers that keep a fight going after a death (Adaptable, Infested, Stock, Surprise, Steam Eruption), segments that reattach. The same check is added to the game-update runbook.
5. **Then decks for long fights, one registered run benchmark at a time,** on the stack that the benchmark before it leaves. Candidates, in this order unless a result changes it: credit for progress against the act boss inside rollout values (run benchmark 17, registered); bottom-tier cards kept out of late card rewards (`[COMMUNITY]` tiers; a hypothesis); more upgrades before act 3; cards and relics that give energy; what a card rollout is played to and judged by.
6. **Guides from the web are a source of hypotheses for particular bosses,** labelled `[COMMUNITY]` with the page and date, written into the boss's note, and adopted only after a test. Where a guide and the game's code disagree, the code stands.
7. **Gates unchanged.** Gate G1's 60 seeds are spent when a 30-seed run benchmark shows at least 12 wins.

## Consequences
- Boss replay 2 decides the two options for the value of a lost rollout. Its registration said the next run-benchmark slot would measure the forms option in whole runs; by item 3 it is instead switched on for everything started after it passes, and run benchmark 17 keeps its slot (amended before its start if the option is adopted by then).
- Run benchmark 20 (the first deck experiment after 17) is registered before run benchmark 17 ends.
- `tools/fight_trace.py` is the trace tool; `docs/runbooks/game-patch.md` gains the check of item 4.
- The estimate for gate G1 depends on the Test Subject correction: if most Test Subject fights turn, the A0 win rate is near 20% without any change to the decks; the rest has to come from the decks, at one seven-hour experiment a step.
