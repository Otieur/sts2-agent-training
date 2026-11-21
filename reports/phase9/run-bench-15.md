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
Pending.

## 6. Deviations and notes
- 2026-11-21 15:17, before the start: the definition of `rshop2` in section 2 gained two rules after its smoke test on two seeds outside every benchmark (`RB097`). There the agent stood in a shop two floors before the act 2 boss with 783 gold and three relics for sale, every option had the same rollout value (each sampled future ended at that boss with the rule planner fighting), and the tie went to the rule, which leaves. So when all options tie, `rshop2` buys the cheapest relic, else the card removal. In run benchmark 11 all options tie in 13% of card decisions and 4% of route decisions. The removal order is added because a purchased removal otherwise removes the first card offered. No result of run benchmark 12 or of this run was known.
- 2026-11-21 17:55, during the run: a defect found today in the benchmark tool (a worker's rollout evaluators kept the rollout policy and boss credit of the first arm that used them; run benchmarks 7, 11 and 12, their section 6) does not touch this run: its four arms have the same rule policy (`path+pot+smith`) and no boss credit, so every arm's rollouts are played as section 2 says. The run uses the code of `31bb9aa`; fixes made since apply from run benchmark 16 on.
