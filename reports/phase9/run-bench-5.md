# Comparison: card rewards by sampled rollouts against the first card (run benchmark 5)

Written before the run (decision 0004 steps 3–4, ML-10), 2026-11-21 at 05:26, after run benchmark 3's results and before any result of run benchmark 4. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypothesis
- **H1:** choosing card rewards by sampled rollouts (`rcard+path`) reaches more floors than taking the first card of every reward (`path`) when search plays every fight.

Why: in run benchmark 3 rollouts beat the hand-made draft scorer by 6.6 floors (44 seeds better, 7 worse). But in run benchmark 2 the scorer was itself 2.4 floors worse than taking the first card, so run benchmark 3 does not show that rollouts beat the strongest card rule known. This comparison sets rollouts against the first card, with the route planner (the one rule that helped in run benchmark 2) in both arms, and with rollouts that play the first card rather than the scorer.

## 2. Runs
- 60 seeds (`RB005` + index 00000–00059), Ironclad, Ascension 5, whole runs in the simulator (`tools/run_bench.py`). Both policies play every seed.
- Combat in both arms: `mcw6` through the save-based fight rebuild, and, for fights the save cannot rebuild (fights started by events), the rebuild through the run clone (`--fight-rebuild save+run`). Mismatches and failures fall back to the planner (counted).
- Rollouts (`tools/run_eval.py`): at each card reward, every card and skip is evaluated on the same 6 sampled futures (common random numbers): the run is rebuilt in an evaluation host from its room-entry save plus the actions since with the future re-sampled (`run_from_save` with a sample seed), the option taken, and the run played on to the end of the act or death by the `path` policy (first card, route planner, simple shop and rest rules) with the rule planner fighting. Rollout value: floors climbed, plus 5 and 5 times the HP fraction left if the act's boss is beaten. The best mean value is taken; exact ties go to the first card.
- Host: a Release build of the current host code, which adds to the build used in run benchmarks 3 and 4 the run sampler fix (no encounter already met in the act comes back in a sampled future) and the fight rebuild through the run clone. Built into `sim/bin/Release2` so that run benchmark 4's host is not touched. Checks before the run: clone, clone from saves, clone from run clones, run clones and sampler (`sim.py runclone`), fair play, sandbox, fidelity. The run starts only if all pass.
- Starts when run benchmark 4 has finished, and not after 09:15. Stopping rule, fixed in advance and independent of outcomes: 6 workers take seeds in index order (worker w: seeds w, w+6, …; each seed's two policies one after another). At 10:00 unfinished runs stop; the analysis uses the seeds for which both policies finished.
- A smoke test on one other seed with planner combat (`RB902…`) checks the plumbing; its outcome is not used.

## 3. Policies
- `path`: first card of each card reward, leave shops, rest below 60% HP else smith the first card, every map move before the boss by the route planner (as in run benchmark 4).
- `rcard+path`: the same, except that card rewards are chosen by rollouts as above (the first card only breaks exact ties and decides if a rollout fails).
- Both: non-Ancient events by the Player's most frequent choice; Neow, Ancients, boss relics and potion rewards by the first option.

## 4. Metrics and test
- Primary: floor reached. Secondary: act 1 and act 2 bosses beaten, wins, where runs die, how often rollouts differ from the first card and how often they skip, final deck size, seconds per run, search fallbacks.
- Test: paired by seed, one-sided sign test at 0.05, mean paired difference with a bootstrap 95% interval (`tools/run_bench.py --report … --baseline path`).
- What follows: if H1 holds, card rewards move to rollouts in the run policy for later benchmarks and simulated-run fight specs, and rollouts are extended to shops, rest sites and Ancients. If it does not, the run benchmark 3 gain is read as mostly undoing the scorer's mistakes, and the next step is to examine the rollout policy and value (planner fighting in rollouts, act-end horizon) before moving more decisions to rollouts.

## 5. Results
Run 2026-11-21, 06:27–08:07 (`data/learn/runs/run-bench-5/manifest.json`; 6006 s wall, 6 workers, all exited cleanly; all 60 seeds finished before the deadline). Host: `sim/bin/Release2`, as registered. Code: the run started from `b10dc5c`; the manifest records `bcd4372`, the commit when it ended (the start-commit fix came later). The changes in between are in `tools/run_bench.py` only: manifest fields, and a refactor of the rollout policy (`Policy.rule_policy`) that gives this arm the same rollout policy (`path`) as before. Report: `python3 -I tools/run_bench.py --report data/learn/runs/run-bench-5 --baseline path`.

| Policy | Runs | Mean floor | Median floor | Reached the act 1 boss | Beat it | Reached the act 2 boss | Beat it | Reached the act 3 boss | Won | Elites fought per run | Final deck (mean cards) | Seconds per run |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| path | 60 | 16.53 | 17 | 40 | 10 | 1 | 1 | 0 | 0 | 1.60 | 19.6 | 140 |
| rcard+path | 60 | 22.03 | 17 | 52 | 23 | 12 | 5 | 2 | 0 | 2.00 | 20.6 | 279 |

| Pair (B − A), floors | Pairs | Mean difference | Bootstrap 95% | B better | B worse | Equal | Sign test p (one-sided) |
|---|---|---|---|---|---|---|---|
| rcard+path − path (H1) | 60 | +5.50 | 3.12 to 8.13 | 32 | 8 | 20 | 9.1e-5 |

- **H1** (card rewards by sampled rollouts reach more floors than taking the first card): p = 9.1e-5, mean +5.50 floors: **holds**.

Act 1 bosses (fights won / fought): `path` Ceremonial Beast 1/11, The Kin 4/14, Vantom 5/15; `rcard+path` Ceremonial Beast 8/18, The Kin 4/15, Vantom 11/19. Act 2 bosses: `path` The Insatiable 1/1; `rcard+path` The Insatiable 3/6, Kaiser Crab 1/4, Knowledge Demon 1/2. Two `rcard+path` runs reached the act 3 boss on floor 48 (Aeonglass, Queen) and lost.

Where runs die (room type of the fatal fight): `path` bosses 30, elites 23, hallways 7; `rcard+path` bosses 38, elites 14, hallways 8. Last floor reached: floors 7–16 in 20 runs against 8, the act 1 boss floor in 30 against 29, beyond it in 10 against 23. Elites fought per run: 1.60 against 2.00 (same route planner in both arms; the rollout arm lives longer). HP lost per won fight: hallways 3.4 / 3.5, elites 32.6 / 24.3, bosses 44.8 / 44.4.

Rollout decisions: 596 card rewards; the rollouts chose differently from the first card in 354 (59%) and skipped in 89 (15%); 1 decision fell back to the first card because a rollout failed. Final decks are slightly larger (20.6 cards against 19.6) and differ in make-up: the rollout arm's most common added cards are Anger (30 copies in 60 decks), Setup Strike 23, Twin Strike 20, Iron Wave 20, Thunderclap 19, Shrug It Off 17; the first-card arm's are Havoc 26, Thunderclap 18, Tremble 17, Setup Strike 16, Headbutt 16. Rollouts cost 2.0 times the seconds per run (279 against 140).

Search in the fights: 19,750 searched moves, **0 fallbacks, 0 mismatches, 0 rebuild errors**; 50 fights (19 and 31) were rebuilt through the run clone because their own save could not rebuild them. This is the first run benchmark in which search played every move of every fight.

**Verdict: H1 holds, by a wide margin.** Against the strongest card rule known (the first card), choosing card rewards by playing each option forward over six re-sampled futures reaches 5.5 more floors (32 seeds better, 8 worse). It more than doubles the act 1 boss wins (23 against 10), takes 12 runs to the act 2 boss against 1, and gets 2 runs to the act 3 boss. The rollout decks also lose about a quarter less HP per won elite. So run benchmark 3's gain was not mainly a matter of undoing the scorer's mistakes. Cautions: The Kin is not helped (4 wins in 15 fights against 4 in 14), and bosses are now where most rollout runs die (38 of 60). The route results of run benchmark 4 point the same way: the planner that fights inside the rollouts sees boss fights poorly.

By the rule in section 4, card rewards move to rollouts in the run policy, and rollouts are next extended to shops, rest sites and Ancients. Before that, the rollout value or fighter for boss fights is the most promising target (see run benchmark 4's verdict).

## 6. Deviations and notes
