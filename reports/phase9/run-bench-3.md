# Comparison: card rewards chosen by sampled rollouts (run benchmark 3)

Written before the run (decision 0004 steps 3–4, ML-10), 2026-11-21 at 02:21. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** choosing card rewards by sampled rollouts (`rdraft+shop+rest`) reaches more floors than choosing them by the draft scorer (`draft+shop+rest`) when search plays every fight.

Why: every deck-building rule so far is a hand-made score (`tools/draft.py`), never checked against outcomes; run benchmark 1 found it worse than taking the first card. Since 2026-11-21 a run can be copied at any decision point and played forward with its unseen future re-sampled (checked by `tools/sim.py runclone`; FP-16), so each option can be judged by what tends to follow it rather than by a score.

## 2. Runs
- 60 seeds (`RB003` + index 00000–00059), Ironclad, Ascension 5, whole runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- Combat in both arms: `mcw6` through the save-based fight rebuild, as in run benchmark 2.
- Rollouts (`tools/run_eval.py`): at each card reward, every card and skip is evaluated on the same 6 sampled futures (common random numbers): the run is rebuilt in an evaluation host from its room-entry save plus the actions since, the future re-sampled (`run_from_save` with a sample seed), the option taken, and the run played on to the end of the act or death by `draft+shop+rest` with the rule planner fighting. Rollout value: floors climbed, plus 5 and 5 times the HP fraction left if the act's boss is beaten. The option with the best mean value is taken; exact ties go to the scorer's choice.
- Host: Release build with run clones and the run sampler, rebuilt after run benchmark 2 has finished; checks before the run: clone, clone from saves, run clones and sampler (`sim.py runclone`), fair play, sandbox, fidelity. The run starts only if all pass.
- Stopping rule, fixed in advance and independent of outcomes: 6 workers take seeds in index order (worker w: seeds w, w+6, …; each seed's two policies one after another). At 09:45 unfinished runs stop; the analysis uses the seeds for which both policies finished.
- A smoke test on two other seeds with planner combat (`RB901…`) was run before this was written, to check the plumbing; its outcomes are not used.

## 3. Policies
- `draft+shop+rest`: as in run benchmark 2 (draft scorer, shop removal and scorer's card, rest rules).
- `rdraft+shop+rest`: the same, except that card rewards are chosen by rollouts as above (the scorer only breaks exact ties and decides if every rollout fails).
- Both: non-Ancient events by the Player's most frequent choice, Neow, Ancients, boss relics and potion rewards by the first option, first map move (no route planner), as in run benchmark 2.

## 4. Metrics and test
- Primary: floor reached. Secondary: act 1 and act 2 bosses beaten, wins, where runs die, how often rollouts disagree with the scorer and how often they skip, seconds per run.
- Test: paired by seed, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval (`tools/run_bench.py --report … --baseline draft+shop+rest`).
- What follows: if H1 holds, rollout evaluation becomes the method for strategic decisions (next: map routes, then shops, rest sites and Ancients, then a run-state value network trained on the rollouts, decision 0004 step 5); if it does not, the rollout policy (planner combat in rollouts) and the value are examined before more decision types are moved to rollouts.

## 5. Results
Run 2026-11-21, 03:39–05:20 (`data/learn/runs/run-bench-3/manifest.json`; 6078 s wall, 6 workers, all exited cleanly, code `1cd8c0d`; all 60 seeds finished before the deadline). Report: `python3 -I tools/run_bench.py --report data/learn/runs/run-bench-3 --baseline draft+shop+rest`.

| Policy | Runs | Mean floor | Median floor | Reached the act 1 boss | Beat it | Reached the act 2 boss | Beat it | Reached the act 3 boss | Won | Final deck (mean cards) | Seconds per run |
|---|---|---|---|---|---|---|---|---|---|---|---|
| draft+shop+rest | 60 | 13.12 | 12 | 15 | 7 | 0 | 0 | 0 | 0 | 16.4 | 117 |
| rdraft+shop+rest | 60 | 19.75 | 17 | 41 | 23 | 7 | 4 | 1 | 0 | 20.1 | 326 |

| Pair (B − A), floors | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| rdraft+shop+rest − draft+shop+rest (H1) | 60 | +6.63 | 4.25 to 9.27 | 44 | 7 | 9 | 6.1e-8 |

- **H1** (card rewards by sampled rollouts reach more floors than by the draft scorer): p = 6.1e-8, mean +6.63 floors: **holds**.

Act 1 bosses (fights won / fought): `draft+shop+rest` Ceremonial Beast 5/8, The Kin 1/6, Vantom 1/1; `rdraft+shop+rest` Ceremonial Beast 11/19, The Kin 5/13, Vantom 7/9. Act 2 bosses (`rdraft+shop+rest` only): Knowledge Demon 2/3, Kaiser Crab 1/3, The Insatiable 1/1. One run (`RB00300005`) reached the act 3 boss (Aeonglass, floor 48) and lost.

Where runs die (room type of the fatal fight): `draft+shop+rest` elites 32, hallways 20, bosses 8; `rdraft+shop+rest` elites 25, hallways 13, bosses 22. Last floor reached: floors 7–9 in 20 runs against 8, floors 10–16 in 25 against 11, the act 1 boss floor in 8 against 18, beyond it in 7 against 23. Elites fought per run: 1.28 against 1.97 (same first-map-move rule; the rollout arm lives longer). HP lost per won fight: hallways 4.7 / 3.7, elites 29.5 / 23.8, bosses 36.6 / 44.1.

Rollout decisions: 610 card rewards; the rollouts chose differently from the scorer in 396 (65%) and skipped in 110 (18%); 1 decision fell back to the scorer because every rollout failed. Final decks are larger (20.1 cards against 16.4) and lean on attacks the scorer rates low (Anger 25 copies in 60 decks, Perfected Strike 21, Twin Strike 17, Molten Fist 16, Iron Wave 16; the scorer's decks: Shrug It Off 30, True Grit 25, Pommel Strike 23, Rupture 16). Rollouts cost 2.8 times the seconds per run (326 against 117), most of it in the 6 × options act-length rollouts per reward.

Search in the fights: 18,393 searched moves; fallbacks 12 in `draft+shop+rest` (11 rebuild errors, 1 mismatch) and 94 in `rdraft+shop+rest` (89 and 5), 0.6% overall. Almost all come from two seeds: in `RB00300029` (both arms) the rebuilt fight from floor 6 (Ruby Raiders) on answers a card choice that is not pending in the rebuild ("no choice is pending", 85 decisions), and in `RB00300005` one fight on floor 24 failed to observe after the rebuild and then reported the fight over (15 decisions); the planner played those moves. Both are host faults to examine; neither stopped a run.

**Verdict: H1 holds, by a wide margin.** Choosing card rewards by playing each option forward over six re-sampled futures reaches 6.6 more floors than the hand-made draft scorer (44 seeds better, 7 worse), nearly triples the act 1 boss wins (23 against 7), and gives the first act 2 boss wins (4) and the first run to reach the act 3 boss. The gain is larger than the scorer's loss to the first card in run benchmark 2 (−2.4), so rollouts are not just undoing the scorer's mistakes. Two cautions: the comparison is against the scorer (not against `base`, which is in run benchmark 4's arms through `path`), and the rollout worlds carry the 9% repeated-encounter flaw noted in section 6, equal for every option.

By the rule in section 4: rollout evaluation becomes the method for strategic decisions. Next in order: map routes (run benchmark 4, running), then shops, rest sites and Ancients, then a run-state value network trained on the rollouts (decision 0004 step 5) to cut the 2.8× cost.

## 6. Deviations and notes
- 2026-11-21 04:05, during the run, a note on the rollouts (no change to the run): the run sampler of the Release build used here can put an encounter already met in the act back into a sampled future (9% of future encounters in a check of eight runs; the real game repeats none). Rollout worlds are therefore slightly off, the same for every option and arm. Fixed afterwards in `sim/RunSampler.cs` (0% after the fix), not used by this run.
