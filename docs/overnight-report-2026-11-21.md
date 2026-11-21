# Overnight report, 2026-11-21

Agent session working alone from 00:50 to 09:15 while the Player slept (run benchmark 7 continues into the day). Branch `overnight/2026-11-21-whole-runs`, pushed after every stage; `master` fast-forwarded for the front page. Detailed timeline: `docs/overnight-log.md`.

## In short
- **Search now plays every fight inside whole simulated runs.** Each fight is rebuilt in a second simulator from the run's own save at the fight's start, with the unseen future re-sampled; 26,747 searched moves in run benchmark 2, no state mismatch, 0.6% left to the planner (fights started by events, now also fixable, see below). Milestone M15 is done.
- **The hand-made deck-building rules lose at A5, even with search fighting.** Taking the first card of every reward reaches 2.4 floors more than the draft scorer with the shop and rest rules (36 runs better, 9 worse). The route planner is the one rule that helps: +2.7 floors (p = 0.002). No policy gets past the act 2 boss; the act 1 boss is the wall at A5, and The Kin is the worst of the three (2 wins in 21 fights).
- **A run can now be copied at any decision point with its future unknown.** The host keeps the game's own room-entry save in memory and re-samples everything a player cannot see (future encounters, events, rewards, later maps and bosses, relic order). Checked: exact copies, repeatability per sample seed, different futures across seeds, and a leak canary.
- **Card rewards chosen by playing ahead beat the hand-made rules by 6.6 floors** (run benchmark 3: each option played forward over six re-sampled futures; 44 seeds better, 7 worse, p = 6e-8). Act 1 boss wins rise from 7 to 23 of 60, the first act 2 boss wins (4) appear, and one run reaches the act 3 boss. Against the strongest card rule known (the first card), card rollouts still gain 5.5 floors (run benchmark 5: 32 better, 8 worse, p = 9e-5), with 23 act 1 boss wins against 10, 12 runs at the act 2 boss against 1, and search playing every move of every fight (no fallbacks). Map routes by the same method (run benchmark 4) gain about one floor (p = 0.04), only by avoiding elites, with no more boss wins.
- **At Ascension 10, the target, rollouts help but the act 1 boss is the wall.** Card and route rollouts together gain 2.8 floors over the rules (run benchmark 6: 32 better, 7 worse, p = 4e-5), all by reaching the act 1 boss twice as often (48 of 60 runs against 24). They beat it in 5 of 48 fights; the Player's A10 runs beat it in 12 of 19. The Kin: 0 wins in 19 fights. Run benchmark 7 then found that crediting boss progress in the rollout value does not help (−0.45 floors, p = 0.70; 3 act 1 boss wins in 99 fights).
- **At Ascension 0, no wins yet in 30 whole new runs** (run benchmark 8; the Player won 5 of 8 at A0–4). Every run reaches the act 1 boss and 60% beat it, but bosses end 21 of the 30 runs, in all three acts, and runs finish with 462 gold unspent because shops are left.
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
| Policy | Mean floor | Reached the act 1 boss | Beat it | Act 2 boss reached / beaten | Elites per run | Seconds per run |
|---|---|---|---|---|---|---|
| `path` (route planner) | 18.08 | 46 | 14 | 5 / 0 | 1.83 | 146 |
| `rpath` (rollouts) | 19.17 | 55 | 13 | 5 / 0 | 0.97 | 178 |

H1 (route rollouts beat the route planner) holds narrowly by the registered sign test: +1.08 floors (22 better, 11 worse, p = 0.040), but the bootstrap interval (−0.50 to 2.65) includes zero. The gain is all in reaching the act 1 boss: rollouts fight half as many elites and die in elites 5 times instead of 18, but beat the boss no more often (13 against 14). Likely cause: the rule planner fights inside the rollouts and rarely beats elites or bosses, so rollout values reward surviving to the boss floor and miss what elites give for the boss fight. Report: `reports/phase9/run-bench-4.md`.

### Run benchmark 5: card rewards by sampled rollouts against the first card (A5, 60 seeds)
| Policy | Mean floor | Reached the act 1 boss | Beat it | Act 2 boss reached / beaten | Act 3 boss reached | Elites per run | Seconds per run |
|---|---|---|---|---|---|---|---|
| `path` (first card, route planner) | 16.53 | 40 | 10 | 1 / 1 | 0 | 1.60 | 140 |
| `rcard+path` (card rollouts, route planner) | 22.03 | 52 | 23 | 12 / 5 | 2 | 2.00 | 279 |

H1 (card rollouts beat the first card) holds: +5.50 floors (interval 3.12 to 8.13; 32 better, 8 worse; p = 9e-5). So run benchmark 3's gain was not mainly undoing the scorer's mistakes. Rollouts differ from the first card in 59% of 596 rewards and skip in 15%; their decks lose a quarter less HP per won elite (24.3 against 32.6). The Kin is not helped (4 of 15 against 4 of 14), and bosses are now where most rollout runs die (38 of 60). Search: 19,750 moves, 0 fallbacks; 50 fights rebuilt through the run clone. Report: `reports/phase9/run-bench-5.md`. Consequence: card rewards move to rollouts in the run policy; `tools/run_specs.py --policy` can now record fight specs from such runs (without the test HP).

### Run benchmark 6: card and route rollouts at Ascension 10 (60 seeds)
| Policy | Mean floor | Reached the act 1 boss | Beat it | Act 2 boss reached / beaten | Elites per run | Seconds per run |
|---|---|---|---|---|---|---|
| `path` (first card, route planner) | 13.97 | 24 | 4 | 2 / 0 | 1.42 | 111 |
| `rcard+rpath` (card and route rollouts) | 16.78 | 48 | 5 | 0 / 0 | 0.85 | 219 |
| *the Player, A10 (25 finished runs, v0.107.1; reference only)* | 23.8 | 19 | 12 | 9 / 4 | | |

H1 (rollouts beat the rules at A10) holds: +2.82 floors (interval 1.03 to 4.55; 32 better, 7 worse; p = 3.5e-5). The gain is all in reaching the act 1 boss (elite deaths 14 against 33); boss wins barely move (5 of 48 against 4 of 24), and no rollout run reaches the act 2 boss. The rollout policy reaches the act 1 boss about as often as the Player (80% of runs against 76%) but beats it in 10% of fights against 63%; The Kin 0 of 19. Search: 14,682 moves, 0 fallbacks. Report: `reports/phase9/run-bench-6.md`. Consequence: `rcard+rpath` is the default run policy for A10 work; next steps aim at the boss fight.

### Comparison 5: learned candidate filter and fast policy (fight benchmark)
`mcwq6` − `mcw6` −10.3 value per fight (interval −18.5 to −3.4) at 0.70 of the time; `qpolicy` − planner +2.2 (p 0.46). Neither hypothesis holds. Report: `reports/phase9/value-search-comparison-5.md`.

## What was built
- **Search in every fight of a run:** three host faults fixed in the save-based fight rebuild (save bookkeeping on load, the act map not yet generated, recordings changed in place by the game's load), and card choices during a fight (Armaments) are now part of the fight.
- **Run clones and the run sampler** (P7.E8.S4): `run_export`, `run_from_save`, `sim/RunSampler.cs`; `tools/sim.py runclone`. The current act's boss is visible in the game and now in the run observation (`act_boss`).
- **Fights rebuilt through the run clone** (`fight_from_run`), which also rebuilds fights started by events and fights that open with a choice; `run_bench.py --fight-rebuild save+run`, used from run benchmark 5 on (second Release build `sim/bin/Release2`, all checks passed): 0 fallbacks.
- **Decision-time evaluation** (`tools/run_eval.py`) and three run-benchmark components that use it: `rdraft` and `rcard` (card rewards, rollouts played by the draft scorer or by the first card) and `rpath` (map moves); rollouts never start rollouts of their own.
- **Run benchmark tooling:** per-fight records (room, enemies, HP), where runs die, a deadline stop, a host-error flag, and a shared event rule.
- **Checks on the Release host before run benchmark 3:** clone 12/12, clone from saves 11/11, runclone all passed, fair play 8/8, sandbox 3/3, fidelity 11/11.

## Problems found
- The simple policy's first option in events wrecked runs: in Tablet of Truth it kept deciphering until max HP fell from 80 to 1. Before run benchmark 2, the shared event rule became the Player's most frequent choice at that point in the history (same for every arm; recorded in the registration).
- Fights started by events cannot be rebuilt from the fight's own save (the load re-enters the event), and fights that open with a choice (discard any number of cards) mismatch after it; the planner played them in run benchmarks 2–4 (0.35–0.6% of moves). Both are rebuilt through the run clone from run benchmark 5 on.
- FI-7d: reviving Osty (e.g. the card Afterlife) calls scene nodes that are inert in the simulator, so the step fails. It matters for the Necrobinder in co-op.

## Next
- **The act 1 boss at A10.** It is now nearly the whole gap to the Player at the target ascension. Two questions. (1) Do the rollouts bring the wrong deck? The rule planner fights inside the rollouts and rarely beats a boss, so rollout values hardly tell a deck that nearly beats the boss from one that does not, and they cannot see what elites give for the boss fight. Run benchmark 7 added credit for the fraction of the boss's HP removed and found no gain (−0.45 floors, p = 0.70); the act 1 boss was beaten in 3 of 99 fights. The rollout policies also fight no fewer act 1 elites than the Player does at A10 (0.5 against 0.68 before the boss), so that is not the gap either. (2) Is the fight play the limit? Boss replay 1 (queued after run benchmark 9) replays the boss fights reached in whole runs with the planner, `mcw6` and `mcw12`, and shows how many of the losses more search could turn around. The Kin (1 win in 64 fights at A10 across run benchmarks 6 and 7) comes first.
- **More decisions by rollouts:** shops (buy, remove), rest sites (rest or smith, which card), Neow and Ancients, boss relics, events. Each gets its own pre-registered comparison.
- **Cost:** rollouts double the seconds per run (279 against 140 in run benchmark 5). A run-state value network trained on the rollouts (decision 0004 step 5) could prune options or replace short rollouts.
- **Gap to the Player:** our best mean floor is 22.0 at A5 (run benchmark 5) and 16.8 at A10 (run benchmark 6), against the Player's 29.7 at A5–9 (20 finished runs, 5 wins) and 23.8 at A10 (25 runs, 2 wins). No simulated run has won yet.
- **Housekeeping:** make the Release2 build the main host (it passed every check) once no benchmark uses the old one; FI-7d (reviving Osty) needs the Player present; rollout decisions in real runs on profile 2 also need the Player present.
