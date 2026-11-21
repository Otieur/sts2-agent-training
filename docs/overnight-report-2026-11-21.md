# Overnight report, 2026-11-21

Agent session working alone from 00:50 to about 10:00 while the Player slept. Branch `overnight/2026-11-21-whole-runs`, pushed after every stage; `master` fast-forwarded for the front page. Detailed timeline: `docs/overnight-log.md`.

## In short
- **Search now plays every fight inside whole simulated runs.** Each fight is rebuilt in a second simulator from the run's own save at the fight's start, with the unseen future re-sampled; 26,747 searched moves in run benchmark 2, no state mismatch, 0.6% left to the planner (fights started by events, now also fixable, see below). Milestone M15 is done.
- **The hand-made deck-building rules lose at A5, even with search fighting.** Taking the first card of every reward reaches 2.4 floors more than the draft scorer with the shop and rest rules (36 runs better, 9 worse). The route planner is the one rule that helps: +2.7 floors (p = 0.002). No policy gets past the act 2 boss; the act 1 boss is the wall at A5, and The Kin is the worst of the three (2 wins in 21 fights).
- **A run can now be copied at any decision point with its future unknown.** The host keeps the game's own room-entry save in memory and re-samples everything a player cannot see (future encounters, events, rewards, later maps and bosses, relic order). Checked: exact copies, repeatability per sample seed, different futures across seeds, and a leak canary.
- **Card rewards chosen by playing ahead beat the hand-made rules by 6.6 floors** (run benchmark 3: each option played forward over six re-sampled futures; 44 seeds better, 7 worse, p = 6e-8). Act 1 boss wins rise from 7 to 23 of 60, the first act 2 boss wins (4) appear, and one run reaches the act 3 boss. Map routes by the same method: run benchmark 4, results below.
- **Comparison 5 is negative:** the learned candidate filter saves 30% of search time but loses 10 value per fight (mostly in elites); the fast learned policy is no better than the planner. Full wide search stays.

## Results
### Run benchmark 2: deck-building components with search in every fight (A5, 60 seeds)
| Policy | Mean floor | Reached the act 1 boss | Beat it | Final deck |
|---|---|---|---|---|
| `base` (first card, first map move) | 16.37 | 36 | 10 | 20.4 cards |
| `draft+shop+rest` (hand-made deck rules) | 13.98 | 17 | 8 | 16.8 |
| `draft+shop+rest+path` (plus the route planner) | 16.65 | 34 | 14 | 16.7 |

H1 (deck rules beat first card): does not hold, reversed (−2.38 floors, interval −4.32 to −0.52). H2 (route planner helps): holds (+2.67, interval 0.55 to 4.85, p = 0.0016). The scorer's decks are smaller, stack True Grit (45 copies in 60 decks) and die in early elites (floors 7–9: 19 runs against 11). Report: `reports/phase9/run-bench-2.md`. Consequence applied: simulated-run fight specs now use the first card and the route planner.

### Run benchmark 3: card rewards by sampled rollouts (A5, 60 seeds)
| Policy | Mean floor | Reached the act 1 boss | Beat it | Act 2 boss reached / beaten | Final deck | Seconds per run |
|---|---|---|---|---|---|---|
| `draft+shop+rest` (draft scorer) | 13.12 | 15 | 7 | 0 / 0 | 16.4 cards | 117 |
| `rdraft+shop+rest` (rollouts) | 19.75 | 41 | 23 | 7 / 4 | 20.1 | 326 |

H1 (rollouts beat the scorer) holds: +6.63 floors (interval 4.25 to 9.27; 44 better, 7 worse; p = 6e-8). The rollouts disagree with the scorer in 65% of 610 rewards and skip in 18%; their decks are larger and attack-heavy (Anger, Perfected Strike, Twin Strike, Molten Fist). The Kin: 5 wins in 13 fights (1 in 6 for the scorer). One run reached the act 3 boss (floor 48). Search fallbacks 0.6%, almost all in two seeds (a card choice the rebuilt fight does not have; one failed observation). Report: `reports/phase9/run-bench-3.md`. Consequence: rollout evaluation becomes the method for strategic decisions.

### Run benchmark 4: map routes by sampled rollouts (A5, 60 seeds)
Pending (starts after run benchmark 3).

### Comparison 5: learned candidate filter and fast policy (fight benchmark)
`mcwq6` − `mcw6` −10.3 value per fight (interval −18.5 to −3.4) at 0.70 of the time; `qpolicy` − planner +2.2 (p 0.46). Neither hypothesis holds. Report: `reports/phase9/value-search-comparison-5.md`.

## What was built
- **Search in every fight of a run:** three host faults fixed in the save-based fight rebuild (save bookkeeping on load, the act map not yet generated, recordings changed in place by the game's load), and card choices during a fight (Armaments) are now part of the fight.
- **Run clones and the run sampler** (P7.E8.S4): `run_export`, `run_from_save`, `sim/RunSampler.cs`; `tools/sim.py runclone`. The current act's boss is visible in the game and now in the run observation (`act_boss`).
- **Fights rebuilt through the run clone** (`fight_from_run`), which also rebuilds fights started by events; `run_bench.py --fight-rebuild save+run` (off until the Release host is next rebuilt).
- **Decision-time evaluation** (`tools/run_eval.py`) and two run-benchmark components that use it: `rdraft` (card rewards) and `rpath` (map moves).
- **Run benchmark tooling:** per-fight records (room, enemies, HP), where runs die, a deadline stop, a host-error flag, and a shared event rule.
- **Checks on the Release host before run benchmark 3:** clone 12/12, clone from saves 11/11, runclone all passed, fair play 8/8, sandbox 3/3, fidelity 11/11.

## Problems found
- The simple policy's first option in events wrecked runs: in Tablet of Truth it kept deciphering until max HP fell from 80 to 1. Before run benchmark 2, the shared event rule became the Player's most frequent choice at that point in the history (same for every arm; recorded in the registration).
- Fights started by events cannot be rebuilt from the fight's own save (the load re-enters the event); the planner played them in run benchmarks 2–4. Fixed on the Debug host (`fight_from_run`); not yet in the Release build used overnight.
- FI-7d: reviving Osty (e.g. the card Afterlife) calls scene nodes that are inert in the simulator, so the step fails. It matters for the Necrobinder in co-op.

## Next
To be completed with run benchmarks 3 and 4.
