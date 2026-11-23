# Comparison: the last boss with more HP at arrival (boss replay 7)

Written before the run (ML-10, decision 0006 item 3), 2026-11-23 at 12:36, after boss replay 5 was read (`reports/phase9/boss-replay-5.md` section 5) and before any fight of this comparison is played. Sections 1–4 are not edited after the run starts; corrections go in section 6 with the reason.

## 1. Question and hypotheses
Boss replay 5 replayed the 47 last-boss situations of run benchmark 20 five times each. Looked at by what the situations bring to the fight (a look after the fact at 47 situations, 13 counts and some 150 cards and relics, so a lead and nothing more), one thing stands apart from the rest: **the HP the run arrives with.** The 30 situations that win no replay arrive with 60% of their max HP on average (53 HP), the 17 that win at least one with 77%, the six that win more than half with 92% (81 HP). The share of replays won goes with the HP fraction at arrival (correlation +0.59 over the 47 situations; with the HP itself +0.56, and by boss +0.78 at Aeonglass, +0.62 at the Test Subject, +0.01 at the Queen), more than with anything counted in the deck (deck size −0.38, relics +0.31, curses −0.26, the numbers of attacks, skills, powers and upgrades between −0.23 and −0.03). The runs arrive between 37% and 100% of max HP, at 66% on average.

That can be read two ways. HP at arrival may be what wins the fight: the last bosses are long fights and the Agent's fights there are races. Or it may only mark a deck that took less damage on the way and would have won anyway. The two readings ask for different work (the rest sites and potions before the boss, or the deck), and they can be told apart cheaply: play the same situations again with the same decks, relics, potions and sample seeds, and more HP.

- **H1 (full HP):** with HP set to max HP the situations win a larger share of their replays than with the HP the runs arrived with.
- **H2 (one rest):** with HP raised by one rest (30% of max HP, rounded down, capped at max HP; `knowledge/mechanics.md`) they win a larger share than with the HP the runs arrived with.
- Described and not tested: the size of both, by boss and by thirds of the HP fraction at arrival; the share won at full HP, which is the most that HP at arrival alone can give these decks.

What this is not: a policy. No run arrives with more HP for free: a rest in place of an upgrade costs the upgrade, and here the deck keeps it. The comparison says what the HP is worth in the fight, which is one side of that trade.

## 2. Runs
- **The base:** boss replay 5's fights (`data/learn/bench/boss-replay-5`: `data/sim/boss-replay-5.json`, sample indexes 0 to 4, arm `mcw6paf`, 233 fights counted). Not played again.
- **Set R (one rest):** `data/sim/boss-replay-7-rest.json`, the same 47 situations in the same order with HP raised by one rest: 44 situations change (22.8 HP more on average; 17 of them reach max HP), 3 were at max HP already. Mean HP fraction 0.90.
- **Set F (full HP):** `data/sim/boss-replay-7-full.json`, the same with HP set to max HP: the same 44 situations change (32.5 HP more on average).
- Sample indexes 0 to 4 in both (fight seed 7000000 + 10 × situation + index, the base's seeds): 235 fights a set. Arm `mcw6paf`, the fight search as the runs play boss rooms. Folders `data/learn/bench/boss-replay-7-rest` and `-full`.
- Each fight is started fresh from its spec. Host: the Release5 build. Order: F, R. After boss replay 6 and before run benchmark 19's third sitting; nine workers at the lowest priority with nothing beside them. No deadline: every fight is played.
- The fight search's code changed between the base and these sets only by the option of boss replay 6 (`tools/sim.py SEARCH_CHOICES = "curse"`), which `mcw6paf` does not switch on. The three situations at max HP already are the same fights in all three sets and serve as the check that a replay reproduces the base (section 4).

## 3. Policies
None is played. The situations come from run benchmark 20's three arms (16 of `C*`, 16 of `C*+ctb`, 15 of `C*+cth`); the fights are played by `mcw6paf`.

## 4. Metrics and tests
- A situation's value is the share of its five fights won. **H1, H2:** the set against the base, one-sided sign test at 0.05 over the situations whose two values differ (`tools/variant_compare.py`). A fight with a host error in either is left out of both and reported.
- Reported with them: fights won per set, in all, by boss and by thirds of the HP fraction at arrival; the same over the 44 situations the sets change; HP left in the fights won in both; for the three situations the sets do not change, in how many of their fights the outcome and the HP left are the base's (if not all, the sets are compared as two samples of the same situations and the sign test stands as it is).
- **What follows.**
  - If H1 holds and Set F wins at least twice the base's share of fights: HP at arrival is taken as a lever of its own for the last boss. Run benchmark 19's `br` component (heal at the rest site before a boss below 80% HP in place of 50%) is its first reading in whole runs and is read by its own rule; the registration after it is about arriving with more HP (the rest sites of the act's last floors, the potions kept for the boss), sized from what Set R gives for one rest.
  - If H1 holds with less than that: HP at arrival helps and is not the main thing; the deck stays the line of work, and nothing is registered for the route from this.
  - If H1 does not hold: HP at arrival is read as a mark of the deck and not as a cause.
  - Nothing enters the stack from this comparison.

## 5. Results
Pending.

## 6. Deviations and notes
- 2026-11-23 12:36, before the run. The look that led here (`reports/phase9/boss-replay-5.md`, its data; not kept as a tool): per situation, the share of replays won against HP, max HP, deck size, card types, upgrades, relics and potions, and against each card and relic held in at least six situations. Cards and relics that go with a larger share (Breakthrough, in 17 situations: 0.29 with and 0.05 without; Blood Vial, in 10: 0.39 and 0.07) or a smaller one (Twin Strike, in 16: 0.04 and 0.19) are named here so that they are not found a second time as news; with some 150 cards and relics looked at and 47 situations none of them is a result, and none is tested here.
- 2026-11-23 12:36, before the run. The reader's arithmetic is checked on made-up records (`tools/tests/test_variant_compare.py`). No fight of Sets R and F has been played.
