# Comparison: shops without the option limit, and events by rollouts, at Ascension 0 (run benchmark 15, two factors)

Written before the run (decision 0005 items 2 and 3, ML-10), 2026-11-21 at 14:46, after the results of run benchmarks 2–9 and 11 and before any result of run benchmark 12. It replaces run benchmark 13, withdrawn before its start: that benchmark's question is one of the two factors here. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Hypotheses
- **H1 (shops, floors):** at Ascension 0, judging every affordable item of a shop by rollouts (`rshop2`) reaches more floors than the stack's shop behaviour so far.
- **H2 (events, floors):** choosing events (Neow and the Ancients included) and card choices outside fights by rollouts (`ropt`) reaches more floors than choosing them by rules.
- **H3, H4 (wins):** each of the two wins more runs.

Why shops: run benchmark 11's arm with `rshop` buys about one card per run and ends with 503 gold. Its recorded decisions show why. `rshop` leaves a shop to the rules when more than 12 options are open, and the rule leaves. A shop sells up to 14 items, so every shop entered with more than about 180 gold was left without a purchase: of 28 shop visits with a decision in 30 runs, 26 are in act 1, none has more than 176 gold, and no relic was ever among the options, while the routes chose a shop at 10 forks in act 2 with 429 gold on average. The richer the agent, the less it bought. `rshop2` removes the limit for shops. The agent still holds 3.4 relics at the act 1 boss against the Player's 5.3.

Why events: as registered for run benchmark 13. Run benchmark 9 found +1.9 floors for `ropt` at A10, short of the registered test (p = 0.084). At A0 runs spread over three acts and Neow and the Ancients each get a decision that lasts.

## 2. Runs
- 30 new seeds (`RB015` + index 00000–00029), Ironclad, **Ascension 0**, whole new runs in the simulator (`tools/run_bench.py`). Four policies play every seed.
- `S`, the stack supported by run benchmarks 11 and 12, by the rule fixed in run benchmark 13's registration before their results: start from `rcard+rpath`; add each of `pot`, `smith`, `rshop` for which run benchmark 11's treatment arm (all three on) reaches more floors on average than run benchmark 12's arm without that component, on the seeds both finished.
- `S2`: `S` with `rshop2` in place of `rshop` (added if `S` has no `rshop`).
- Arms: `S`, `S+ropt`, `S2`, `S2+ropt`. Computed by the queue script (`data/learn/queue/stack2.py`) before any result of this run.
- `rshop2` (`tools/run_opts.py`): as `rshop`, one purchase at a time (leaving, or one affordable card, relic, potion or card removal), each option on the same 6 sampled futures played to the end of the act by the stack's rules with the rule planner fighting, the shop judged again after each purchase until leaving wins; ties and failures to the rule. Changes against `rshop`: up to 24 options instead of 12, which covers every shop; when every option has the same value (the rollouts cannot tell them apart), it buys the cheapest affordable relic, else the card removal, and leaves only when neither is for sale; the card to remove follows the removal order (curses, then Strikes, then Defends) unless `ropt` judges it.
- `ropt` as in run benchmark 9: every event page with two or more options and every card choice outside fights except card rewards; more than 12 options left to the rule. If `smith` is in `S`, rest sites and upgrade choices stay with that rule.
- Combat in all arms: `mcw6` in every fight, `--fight-rebuild save+run`. Host: the Release2 build, unchanged. 7 workers claim seeds in index order (`--dynamic`). Stopping rule: unfinished runs stop 7 hours after the start; time the machine is asleep does not count (the rule of run benchmark 12, section 6). The analysis uses the seeds for which all four policies finished.
- Fights and rollout decisions are recorded as in run benchmark 11.

## 3. Policies
- `S`: as fixed above; Neow, Ancients, boss relics and potion rewards by the first option, other events by the Player's most frequent choice, card choices outside fights by the rules; shops as in run benchmarks 11 and 12.
- `S+ropt`: the same with events and card choices outside fights by rollouts.
- `S2`, `S2+ropt`: the same two with every affordable shop item judged.

## 4. Metrics and tests
- A factor's effect on a seed: the mean floor of the two arms with it minus the mean floor of the two arms without it. H1 and H2: one-sided sign test at 0.05 across seeds, with the mean effect and a bootstrap 95% interval. H3 and H4: per seed, wins with the factor minus wins without (−2 to 2), one-sided exact sign test at 0.05 on the seeds where it is not zero; wins per arm with Wilson intervals. `tools/run_details.py --factor`. The interaction (the shop effect with `ropt` minus without) is reported, not tested. The two factors are separate questions; no correction is applied across them.
- Secondary: purchases per run by type and gold left; relics, upgrades and potions at each boss fight's start; shop decisions by gold held; `ropt` decisions by screen and how often they differ from the rules; act bosses beaten; where runs die; seconds per run per arm.
- What follows, the stack that runs next: a factor's treatment enters the stack if its mean effect in floors is positive and its two arms together do not win fewer runs than the two arms without it. That is a rule for choosing what to run next, as in run benchmark 12. A claim that the component helps needs its test.
- Gate G1 (run benchmark 14, deferred) is measured once a 30-seed benchmark shows at least 12 wins for a stack.

## 5. Results
Run 2026-11-21 16:50–18:35 and 21:55 to 2026-11-22 01:02 (`data/learn/runs/run-bench-15/manifest.json`; 7 workers; 105 and 187 minutes of running time, inside the 7 hours). All 30 seeds were finished by all four policies: 120 runs, no host error, no rollout error. Seeds 00000–00008 ran on the code of `31bb9aa`, seeds 00009–00029 on that of `db6a04e` (section 6). Reports: `python3 -I tools/run_details.py data/learn/runs/run-bench-15`, the same with `--factor --on … --off …` for each factor, and with `--decisions`. `S` = `rcard+rpath+pot+smith+rshop`, `S2` = `rcard+rpath+pot+smith+rshop2`.

| Policy | Mean floor | Median | Wins (Wilson 95%) | Act 1 boss beaten | Act 2 boss | Act 3 boss | Seconds per run |
|---|---|---|---|---|---|---|---|
| `S` | 30.03 | 33 | 0 of 30 (0–11%) | 23 of 30 | 4 of 17 | 0 of 2 | 572 |
| `S+ropt` | 34.57 | 33 | 2 of 30 (2–21%) | 25 of 28 | 11 of 22 | 2 of 8 | 944 |
| `S2` | 31.90 | 32 | 2 of 30 (2–21%) | 23 of 30 | 9 of 15 | 2 of 6 | 813 |
| `S2+ropt` | 33.13 | 33 | 0 of 30 (0–11%) | 24 of 30 | 9 of 20 | 0 of 6 | 1070 |

| Factor (the two arms with it minus the two without) | Seeds | Mean effect, floors | Bootstrap 95% | Better | Worse | Equal | Sign test p (one-sided) | Wins with / without (of 60) | Seeds with more wins with / without | Sign test p, wins |
|---|---|---|---|---|---|---|---|---|---|---|
| Shops: `rshop2` against `rshop` (H1, H3) | 30 | +0.22 | −3.37 to 3.65 | 14 | 13 | 3 | 0.50 | 2 / 2 | 1 / 1 | 0.75 |
| Events: `ropt` against the rules (H2, H4) | 30 | +2.88 | −0.20 to 6.12 | 17 | 7 | 6 | 0.032 | 2 / 2 | 1 / 1 | 0.75 |

- **H1** (every affordable shop item judged by rollouts reaches more floors): p = 0.50, mean +0.22: **does not hold**.
- **H2** (events and card choices outside fights by rollouts reach more floors): p = 0.032 by the registered sign test, 17 seeds better against 7: **holds**. The mean effect is +2.88 floors; its bootstrap interval reaches just below zero (−0.20).
- **H3, H4** (wins): 2 wins against 2 for each factor: **do not hold**. The run has 4 wins in 120 runs (3.3%).
- Interaction, reported and not tested: the shop effect is +1.87 floors without `ropt` and −1.44 with it (difference −3.3).
- The two groups of seeds (section 6): seeds 00000–00008, shops −1.50 (3 better, 5 worse, 1 equal) and events +1.17 (5, 3, 1); seeds 00009–00029, shops +0.95 (11, 8, 2) and events +3.62 (12, 4, 5). The events effect has the same sign in both; the shop effect does not.

**The stack that runs next** (section 4): both treatments enter, each with a positive mean effect and as many wins with it as without: `rcard+rpath+pot+smith+rshop2+ropt`. For `rshop2` that is the rule for what runs next and nothing more: +0.22 floors is no evidence that it helps, and the arm that is now the stack (`S2+ropt`) reached fewer floors than `S+ropt` (33.13 against 34.57) and won no run. Run benchmark 18 started on this stack at 01:02.

**Shops.** The mechanism of H1 happened and the floors did not follow. With `rshop` a run has 0.8 shop visits with a decision, buys 0.8 cards and no relic and ends with about 455 gold. With `rshop2` it has 2.5, buys 2.3 cards, 0.6 relics, 0.9 potions and 0.9 card removals and ends with about 210 gold. `rshop2` decisions by gold held (both arms): under 100 gold 113 decisions (no relic, 51 cards, 23 potions, 5 removals, 34 left); 100–199 gold 127 (7 relics, 59 cards, 19 potions, 36 removals, 6 left); 200–399 gold 68 (20 relics, 24 cards, 8 potions, 11 removals, 5 left); 400 and more 23 (10 relics, 6 cards, 2 potions, 3 removals, 2 left). All options had the same value in 32 of 331 shop decisions; 19 of those became a purchase by the tie rule. Relics at the act 2 boss: 5.2 and 5.6 in the `rshop` arms, 6.8 and 6.1 in the `rshop2` arms.

**Events.** `ropt` decided 8.8 times a run and differed from the rule in 261 of 529 decisions (49%; Neow in 44 of 67); all options had the same value in 54 (10%). It costs about two thirds more time per run with `rshop` (944 seconds against 572) and a third more with `rshop2` (1,070 against 813).

**Where the runs end** (120 runs): act 2 boss 41, act 1 boss 23, act 3 boss 18, act 2 hallway 12, act 2 elite 9, act 3 hallway 7, act 3 elite 4, act 1 hallway 1, act 1 elite 1, won 4. Bosses end 82 of the 116 lost runs. Boss fights won of those reached: act 1 95 of 118 (Ceremonial Beast 34 of 36, The Kin 34 of 42, Vantom 27 of 40); act 2 33 of 74 (Kaiser Crab 13 of 35, Knowledge Demon 6 of 19, The Insatiable 14 of 20); act 3 4 of 22 (Aeonglass 2 of 8, Queen 0 of 4, Test Subject 2 of 10).

**What the Agent brings to a boss, beside the Player** `[OBS]` for the Agent (this run, four arms together), `[PLAYER-DATA]` for the Player (`data/runs.db`, finished solo Ironclad runs on v0.107.1; relics counted from the final relic list by the floor they were added). The Player's runs are on another game version and mostly at higher ascensions, and the A0–4 group has 8 runs, so this is a description, not a test.

| Boss of | Who | Fights | Won | HP at the start | Deck | Upgraded cards | Relics | Elites fought in the act |
|---|---|---|---|---|---|---|---|---|
| Act 1 | Agent, A0 | 118 | 81% | 77% | 18.3 | 3.2 | 3.4 | 0.76 |
| | Player, all ascensions | 44 | 68% | 60% | 19.8 | 4.4 | 5.1 | 1.00 |
| | Player, A0–4 | 8 | 75% | 56% | 19.9 | 5.1 | 5.2 | 1.62 |
| Act 2 | Agent, A0 | 74 | 45% | 65% | 24.8 | 7.4 | 5.9 | 0.53 |
| | Player, all ascensions | 24 | 67% | 68% | 26.6 | 10.1 | 9.9 | 1.08 |
| | Player, A0–4 | 6 | 83% | 75% | 26.8 | 11.7 | 10.7 | 1.17 |
| Act 3 | Agent, A0 | 22 | 18% | 62% | 31.5 | 13.1 | 8.8 | 0.27 |
| | Player, all ascensions | 14 | 93% | 75% | 31.4 | 18.7 | 14.9 | 0.64 |
| | Player, A0–4 | 5 | 100% | 82% | 28.2 | 17.6 | 15.0 | 0.40 |

The Agent reaches the act 1 boss with more HP than the Player (77% against 60%) and less of everything else, and the gap grows: at the act 2 boss it holds 5.9 relics against the Player's 9.9 and 7.4 upgraded cards against 10.1, at the act 3 boss 8.8 against 14.9 and 13.1 against 18.7. It fights fewer elites (0.76 against 1.00 in act 1, 0.53 against 1.08 in act 2; the route rollouts took an elite at 32 of the 194 forks that offered one) and keeps the HP it would have paid for them. The Player's shops buy 0.6 to 1.4 relics an act in acts 2 and 3; `rshop2` buys 0.6 a run. This agrees with boss replay 1 (the decks, not the fight search, limit the boss fights) and names what is missing: relics and upgrades. It is the pattern run benchmark 18 tests a cause of: inside rollouts the rule planner fights, elites and bosses look worse than they are for search, and the routes keep away from them.

**Checks.** Every decision recorded on seeds 00009–00029 names `path+pot+smith` as the policy that played its rollouts, with no boss credit, in all four arms (decisions on the first nine seeds were recorded before that field existed). Search: no mismatch; four search errors, each followed by the planner's action for that decision, in two runs of `S+ropt` (seeds 00004 and 00022, both reached floor 48 and lost); none in the other arms. Workers' exit codes all 0.

## 6. Deviations and notes
- 2026-11-21 15:17, before the start: the definition of `rshop2` in section 2 gained two rules after its smoke test on two seeds outside every benchmark (`RB097`). There the agent stood in a shop two floors before the act 2 boss with 783 gold and three relics for sale, every option had the same rollout value (each sampled future ended at that boss with the rule planner fighting), and the tie went to the rule, which leaves. So when all options tie, `rshop2` buys the cheapest relic, else the card removal. In run benchmark 11 all options tie in 13% of card decisions and 4% of route decisions. The removal order is added because a purchased removal otherwise removes the first card offered. No result of run benchmark 12 or of this run was known.
- 2026-11-21 17:55, during the run: a defect found today in the benchmark tool (a worker's rollout evaluators kept the rollout policy and boss credit of the first arm that used them; run benchmarks 7, 11 and 12, their section 6) does not touch this run: its four arms have the same rule policy (`path+pot+smith`) and no boss credit, so every arm's rollouts are played as section 2 says. The run uses the code of `31bb9aa`; fixes made since apply from run benchmark 16 on.
- 2026-11-21 18:35, interruption: the run was stopped after 105 minutes because the machine was being shut down (the Player). Recorded: seeds 00000–00008, all four arms each. Seeds 00009–00015 were under way and are not recorded; they are played again from their start. The run continues with `--resume` (`data/learn/queue/queue10.sh`) and stops 315 minutes after its restart, the rest of its 7 hours of running time. This replaces the last sentence of the 17:55 note: the first nine seeds ran on the code of `31bb9aa`, the others run on the code of the restart (`398cba6` or later). For this run's arms the two differ only where a rollout or a search playout used to fail (cards the host cannot simulate are no longer played; a decision whose first three rollouts fail goes to the rule at once; a refused card choice inside a search playout gets a legal answer) and in what is recorded per decision; the four arms of a seed always run on the same code, and every comparison is within seeds. Section 5 will give the factor effects for the two groups of seeds separately as well.
- 2026-11-21 23:55, during the run: an interim count was read at the Player's request, over the 21 seeds recorded by then (00000–00019 and 00021): floors and wins per arm, the two factor effects, and where the runs ended. Nothing depends on that reading. The run stops by its time rule, its arms are fixed, and the arms of run benchmarks 18, 16 and 17 are computed by the queue script from the finished run by the rules registered before it. The interim figures are not reported here; section 5 uses the finished run only.
