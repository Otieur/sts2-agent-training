# Comparison: rollout decisions at Ascension 10 (run benchmark 6)

Written before the run (decision 0004 steps 3–4, ML-10), 2026-11-21 at 06:34, after the results of run benchmarks 3 and 4 and before any result of run benchmark 5. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** at Ascension 10, choosing card rewards and map moves by sampled rollouts (`rcard+rpath`) reaches more floors than the best rule policy so far (`path`: first card, route planner) when search plays every fight.

Why: the milestone that matters is Ascension 10 (M8: the Player won 8% of finished Ironclad runs there). Tonight's rollout results are all at A5 (cards +6.6 floors over the draft scorer in run benchmark 3, routes +1.1 over the route planner in run benchmark 4). This tests whether rollout decisions, both together, carry to the target ascension, where enemies hit harder and the act 3 boss is doubled.

## 2. Runs
- 60 seeds (`RB006` + index 00000–00059), Ironclad, **Ascension 10**, whole runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- Combat in both arms: `mcw6` through the save-based fight rebuild, and the run-clone rebuild for fights the save cannot rebuild (`--fight-rebuild save+run`); mismatches and failures fall back to the planner (counted).
- Rollouts (`tools/run_eval.py`), at each card reward (every card and skip) and at each map choice with two or more next points (the boss excepted): every option is evaluated on the same 6 sampled futures; the run is rebuilt in an evaluation host from its room-entry save plus the actions since with the future re-sampled, the option taken, and the run played on to the end of the act or death by `path` (rollouts never start rollouts of their own) with the rule planner fighting. Rollout value: floors climbed, plus 5 and 5 times the HP fraction left if the act's boss is beaten. The best mean value is taken; exact ties go to the first card and to the route planner's move.
- Host: the Release2 build used by run benchmark 5 (`sim/bin/Release2`, all checks passed at 05:37), unchanged.
- Starts when run benchmark 5 has finished, and not after 09:15. Stopping rule, fixed in advance and independent of outcomes: 6 workers take seeds in index order (worker w: seeds w, w+6, …; each seed's two policies one after another). At 10:30 unfinished runs stop; the analysis uses the seeds for which both policies finished.
- A smoke test on one other seed with planner combat (`RB903…`, A10) checked the plumbing; its outcome is not used.

## 3. Policies
- `path`: first card of each card reward, leave shops, rest below 60% HP else smith the first card, every map move before the boss by the route planner.
- `rcard+rpath`: the same, except that card rewards and map moves are chosen by rollouts as above.
- Both: non-Ancient events by the Player's most frequent choice; Neow, Ancients, boss relics and potion rewards by the first option.

## 4. Metrics and test
- Primary: floor reached. Secondary: act bosses beaten, wins, where runs die, elites fought, how often rollouts differ from the rules, seconds per run, search fallbacks.
- Test: paired by seed, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval (`tools/run_bench.py --report … --baseline path`).
- Reference, not a test (different seeds and game version): the Player's finished Ironclad runs at A10 on v0.107.1 (`data/runs.db`): 25 runs, mean floor 23.8, median 17, 2 wins.
- What follows: if H1 holds, `rcard+rpath` becomes the default run policy for Ascension work and simulated-run fight specs at A10, and the next steps aim at boss fights and the rollout value. If it does not, the A5 gains do not carry to A10 as they are, and where the rollout policy's runs die at A10 decides what is examined first.

## 5. Results
Run 2026-11-21, 08:07–09:11 (`data/learn/runs/run-bench-6/manifest.json`; 3840 s wall, 6 workers, all exited cleanly; all 60 seeds finished before the deadline). Host: `sim/bin/Release2`, as registered. Code: the run started from `bcd4372` (the manifest now records the start; the edits made during the run and the check that they change nothing are in section 6). Report: `python3 -I tools/run_bench.py --report data/learn/runs/run-bench-6 --baseline path`.

| Policy | Runs | Mean floor | Median floor | Reached the act 1 boss | Beat it | Reached the act 2 boss | Beat it | Won | Elites fought per run | Final deck (mean cards) | Seconds per run |
|---|---|---|---|---|---|---|---|---|---|---|---|
| path | 60 | 13.97 | 14 | 24 | 4 | 2 | 0 | 0 | 1.42 | 17.6 | 111 |
| rcard+rpath | 60 | 16.78 | 17 | 48 | 5 | 0 | 0 | 0 | 0.85 | 18.5 | 219 |
| *Reference: the Player, A10, v0.107.1* | 25 | 23.8 | 17 | 19 | 12 | 9 | 4 | 2 | | | |

| Pair (B − A), floors | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| rcard+rpath − path (H1) | 60 | +2.82 | 1.03 to 4.55 | 32 | 7 | 21 | 3.5e-5 |

- **H1** (at A10, card rewards and map moves by sampled rollouts reach more floors than the route planner with the first card): p = 3.5e-5, mean +2.82 floors: **holds**.

Act 1 bosses (fights won / fought): `path` Ceremonial Beast 1/4, The Kin 1/8, Vantom 2/12; `rcard+rpath` Ceremonial Beast 4/14, The Kin 0/19, Vantom 1/15. Act 2 bosses: `path` 0/2 (Kaiser Crab, The Insatiable); `rcard+rpath` none reached.

Where runs die (room type of the fatal fight): `path` elites 33, bosses 22, hallways 5; `rcard+rpath` elites 14, bosses 43, hallways 3. Last floor reached: floors 7–16 in 36 runs against 12, the act 1 boss floor in 20 against 43, beyond it in 4 against 5. HP lost per won fight: hallways 5.0 / 5.9, elites 34.7 / 29.6, bosses 57.8 / 40.2. The Player's 25 finished A10 runs (different seeds and game version, not a test): 6 ended before the act 1 boss, 7 at it, 12 beat it.

Rollout decisions: 441 card rewards, the rollouts chose differently from the first card in 259 (59%) and skipped in 47 (11%); 348 map choices, different from the route planner in 113 (32%). Most common added cards: `rcard+rpath` Anger 24, Thunderclap 21, Twin Strike 21, Perfected Strike 18; `path` Blood Wall 18, Taunt 16, True Grit 15, Twin Strike 15. Rollouts cost 2.0 times the seconds per run (219 against 111).

Search in the fights: 14,682 searched moves, 0 fallbacks, 0 mismatches, 0 rebuild errors (no fight needed the run-clone rebuild).

**Verdict: H1 holds, but at A10 the whole gain is in reaching the act 1 boss.** The rollout policy gets twice as many runs to the act 1 boss (48 against 24): it fights fewer elites (0.85 per run against 1.42) and dies in them far less often (14 against 33). It then beats the boss in 5 of 48 fights against 4 of 24, and no run reaches the act 2 boss (2 for `path`). Next to the Player's A10 runs, the rollout policy reaches the act 1 boss about as often (80% of runs against 76%) but beats it in 10% of fights against 63%. The Kin is not beaten once in 19 fights. At the target ascension the gap to the Player is now almost entirely the act 1 boss fight: the deck brought to it and the play in it.

By the rule in section 4, `rcard+rpath` becomes the default run policy for Ascension work and for simulated-run fight specs at A10 (`tools/run_specs.py --policy rcard+rpath --no-test-hp`), and the next steps aim at boss fights and the rollout value. Run benchmark 7 (pre-registered at 08:17, before these results; started 09:12) tests credit for boss progress in the rollout value. A separate question it does not answer is whether the act 1 boss losses come from the decks or from the fight play: replaying the boss fights reached here with a larger search budget would separate the two.

## 6. Deviations and notes
- 2026-11-21 08:20, during the run, a note on the code (no change to the run's behaviour): the run started at 08:07 from `bcd4372`. Between 08:12 and 08:17 `tools/run_eval.py` and `tools/run_bench.py` gained an optional boss credit for run benchmark 7 (component `bc`, off unless named; commit `e33474f`). The rollouts import both files from disk at a worker's first rollout decision, and every worker plays `path` before `rcard+rpath` on its first seed, so some workers may have loaded the new files. With `bc` off the rollout values are meant to be identical. Checked: on seed `RB905…` at A10, 4 decisions (2 card rewards, 2 map choices, 16 options, 3 sampled futures each, `path` rollouts) gave the same values to four decimals from the code of `bcd4372` and from `e33474f`.
