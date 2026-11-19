# Phase 1: Learning from the Run History

**Goal:** turn the Player's 233 recorded runs into a clean dataset. From it, produce analyses of how the Player plays Ironclad, a per-encounter combat benchmark, and Ironclad playbook v1, which the Player reviews.

**Depends on:** nothing. Needs neither the game running nor the mod.
**Unblocks:** Phase 2 (discrepancy analysis), Phase 3 (shadowing starts from playbook v1), and Phase 4 (the benchmark).

---

## 1. What to expect

| | |
|---|---|
| **Duration** | 2–3 Agent sessions. Extraction about 1 session, analyses about 1 session, playbook and report about 1 session. |
| **Player time** | Interview, 30–45 minutes, can be split over several evenings. Playbook review, about 15 minutes. Browsing the visual report is optional. |
| **What the results will tell us** | How the Player drafts, paths, rests and spends. Which encounters cost the most HP. Where runs end. Which deck archetypes the Player builds. |
| **What they will not tell us** | Which cards *cause* wins: only 12 Ironclad wins, so outcome statistics are weak evidence. Anything about combat play turn by turn, which is not recorded. |
| **Likely surprises** | Habits the Player is unaware of, such as a consistent rest threshold, a card always skipped, or an act where HP is usually lost. These are the best interview material. |
| **Deliverables** | The dataset with its dictionary, 5 analysis reports, a frozen benchmark, a visual report, interview notes, and `playbooks/ironclad.md` v1 |

---

## 2. Data scope

| Decision | Choice | Reason |
|---|---|---|
| Source folders | `steam/<id>/profile1`, `steam/<id>/modded/profile1`, `steam/back_prof1` | All three hold history. They overlap almost completely, so runs are deduplicated. |
| Deduplication key | `(seed, start_time)` | Unique per run; produces 233 unique runs |
| Primary analysis set | Solo runs, `build_id = v0.107.1`, character Ironclad (57 runs) | Matches the target game version |
| Excluded from Ironclad analysis | The 6 runs on v0.113.1 (Fool and beta balance) | Different version |
| Cross-character tables | All 227 v0.107.1 solo runs | Encounter danger and pathing are mostly shared across characters, and more data helps |
| Abandoned runs | Kept for decision statistics up to the point of abandonment; excluded from outcome statistics | An abandonment is not a loss to the game |
| Ascension bands | A0–4, A5–9, A10 | Enough runs per band for comparisons |

**Fields available per floor** (`map_point_history[act][i].player_stats[]`): `card_choices` (card, was_picked), `cards_gained`, `cards_removed`, `cards_transformed`, `cards_enchanted`, `upgraded_cards`, `downgraded_cards`, `relic_choices`, `relics_removed`, `bought_relics`, `bought_potions`, `bought_colorless`, `potion_choices`, `potion_used`, `potion_discarded`, `rest_site_choices` (`SMITH`, `HEAL`, `DIG`, `COOK`, `KINDLE`, `HATCH`, `LIFT`, `CLONE`), `event_choices`, `ancient_choice`, `completed_quests`, `current_hp`, `max_hp`, `damage_taken`, `hp_healed`, `max_hp_gained`, `max_hp_lost`, and the gold fields. Per room: `model_id` (encounter or event ID), `monster_ids`, `room_type`, `turns_taken`.

---

## 3. Epics and stories

### P1.E1: Dataset extraction

> **P1.E1.S1: Locate, copy and deduplicate runs** · Size S · Status: Done
> *As the Agent, I want a read-only copy of every unique run, so that analysis never touches the live save folder.*
>
> **Acceptance criteria**
> - [ ] `tools/extract_runs.py` scans every `**/saves/history/*.run` under the game's save directory.
> - [ ] Unique runs are copied to `data/raw/<run_id>.run`, where `run_id = <start_time>-<seed>`.
> - [ ] The count is 233 unique runs (as of 2026-11-18). A `source_folders` column lists where each run was found.
> - [ ] The script runs with `python3 -I`, and the live folder is only ever read.

> **P1.E1.S2: Flatten into tables** · Size M · Status: Done
> *As the Agent, I want flat tables and a SQLite database, so that any question can be answered with one query.*
>
> **Acceptance criteria:** `data/runs.db` (SQLite) and CSV copies in `data/tables/` contain these tables.
> - [ ] `runs`: run_id, seed, start_time, build_id, character, ascension, win, abandoned, killed_by_encounter, killed_by_event, floors_reached, acts, run_time, n_players, game_mode, is_custom.
> - [ ] `floors`: run_id, act, floor (1-based within the run), map_point_type, room_type, model_id, monster_ids, turns_taken, hp_before, hp_after, max_hp, damage_taken, hp_healed, gold_before, gold_after, gold_gained, gold_spent.
> - [ ] `card_offers`: run_id, floor, offer_group (one per screen), source (`reward`, `shop`, `event`, `ancient`), card_id, upgraded, picked, act, deck_size_before.
> - [ ] `deck_changes`: run_id, floor, change (`gained`, `removed`, `transformed_from`, `transformed_to`, `upgraded`, `downgraded`, `enchanted`), card_id.
> - [ ] `relic_events`, `potion_events` (offered, picked, used, discarded, bought), `rest_choices`, `shop_visits`, `event_choices`, `ancient_choices`.
>
> **Notes:** `hp_before` is derived as `current_hp + damage_taken - hp_healed` (adjusted for max HP changes). Check it on sample floors against the neighbouring floors' values.

> **P1.E1.S3: Reconstruct the deck at every floor** · Size M · Status: Done
> *As the Agent, I want the deck as it was at each decision, so that card picks can be judged in context.*
>
> **Acceptance criteria**
> - [ ] `deck_snapshots` (run_id, floor, card_id, count, upgraded) is built by replaying `deck_changes` from the starting deck.
> - [ ] The reconstructed final deck matches `players[0].deck` in at least 95% of runs. Mismatches are listed with the likely cause (for example card effects that add cards mid-combat and are not logged).

> **P1.E1.S4: Data dictionary** · Size S · Status: Done
> *As the Next Session, I want every column documented, so that I can query the data without reading the extractor.*
>
> **Acceptance criteria**
> - [ ] `data/README.md` describes every table and column: units, derivation, known caveats.

> **P1.E1.S5: Validation checks** · Size S · Status: Done
> *As the Agent, I want automatic sanity checks, so that a parsing bug does not quietly corrupt every analysis.*
>
> **Acceptance criteria**
> - [ ] `tools/validate_data.py` checks:
>   - per-character run counts (Ironclad 57, Necrobinder 59, Regent 53, Silent 52, Defect 7, Fool 6 including the co-op run)
>   - non-negative damage
>   - HP never above max HP
>   - each floor's `hp_after` equals the next floor's `hp_before` within 1
>   - every winning run ends on a boss floor
> - [ ] All checks pass, or each failure is explained in `data/README.md`.

---

### P1.E2: Card evaluation (Ironclad)

> **P1.E2.S1: Offer and pick table** · Size S · Status: Done
> *As the Agent, I want to know how often the Player takes each card when offered, so that playbook v1 reflects the Player's real priorities.*
>
> **Acceptance criteria**
> - [ ] `reports/phase1/card-picks.csv`: card_id, rarity, times offered, times picked, pick rate, Wilson 95% interval, pick rate by act.
> - [ ] Only reward screens (`source = reward`) are included. Shop and event offers get separate tables.

> **P1.E2.S2: Implied priority ranking** · Size M · Status: Done
> *As the Agent, I want a ranking of cards from head-to-head choices, so that the Player's preferences are separated from how often each card happens to appear.*
>
> **Acceptance criteria**
> - [ ] Every reward screen is converted into pairwise comparisons: the picked card beats each card not picked, and "Skip" counts as a pseudo-card.
> - [ ] A Bradley–Terry model is fitted (iterative MM algorithm; pure Python if scipy is unavailable).
> - [ ] `reports/phase1/card-ranking.md` lists cards by strength, with comparison counts. Cards with fewer than 5 comparisons are listed separately as "insufficient data".

> **P1.E2.S3: Context effects** · Size M · Status: Done (rules by card type deferred to Phase 2: card types are not in the run files)
> *As the Agent, I want to know how the deck's state changes the Player's picks, so that the playbook can say "take X when Y".*
>
> **Acceptance criteria**
> - [ ] Pick rate against deck size, act, and the number of attacks, skills and powers already in the deck.
> - [ ] Skip rate against act and deck size.
> - [ ] At least 3 context rules are drafted with evidence (for example "after 4 attacks, the Player takes skills over attacks 70% of the time").

> **P1.E2.S4: Outcome association** · Size S · Status: Done
> *As the Agent, I want weak signals about which cards appear in winning decks, so that they become hypotheses to test, not rules.*
>
> **Acceptance criteria**
> - [ ] Win rate of runs with versus without each card in the final deck, for cards in at least 10 runs, stratified by ascension band.
> - [ ] Every row shows n and is labelled `[PLAYER-DATA]`, weak. Results go to the playbook's hypothesis list only.

> **P1.E2.S5: Upgrade and removal priorities** · Size S · Status: Done
> *As the Agent, I want to know what the Player upgrades and removes first, so that rest-site and shop policies start from the Player's practice.*
>
> **Acceptance criteria**
> - [ ] The first, second and third upgrade targets, by frequency.
> - [ ] Removal targets (Strike or Defend or curse) and the floor of the first removal.

---

### P1.E3: Encounter danger and the combat benchmark

> **P1.E3.S1: Per-encounter statistics** · Size S · Status: Done
> *As the Agent, I want to know how much each encounter costs, so that pathing and HP budgeting are grounded in data.*
>
> **Acceptance criteria**
> - [ ] `reports/phase1/encounters.csv`: encounter_id, pool (taken from the suffix: `_WEAK`, `_NORMAL`, `_ELITE`, `_BOSS`), act, n, median, mean and p90 damage taken, damage as % of max HP, median turns, deaths, death rate given reached.
> - [ ] One version for Ironclad only and one for all characters. Ironclad is also split by ascension band.

> **P1.E3.S2: Danger ranking report** · Size S · Status: Done
> *As the Player, I want a readable list of the encounters that hurt the most, so that I can sanity-check the numbers against experience.*
>
> **Acceptance criteria**
> - [ ] `reports/phase1/danger.md` has the top 10 hallway fights, the elites and the bosses per act, with median and p90 damage and n.

> **P1.E3.S3: Freeze the benchmark** · Size S · Status: Done
> *As the Agent, I want a frozen per-encounter damage benchmark, so that solo runs in Phase 4 can be compared against the Player's real performance.*
>
> **Acceptance criteria**
> - [ ] `data/benchmarks/ironclad-encounters-v0.107.1.csv`: encounter_id, n, median_dmg, p75_dmg, p90_dmg, median_turns, benchmark_grade (yes if n ≥ 5).
> - [ ] The file header records its creation date and source run count. It is never edited afterwards; a new benchmark gets a new file.

---

### P1.E4: Pathing, rest, shops, events, Ancients, potions

> **P1.E4.S1: Pathing profile** · Size S · Status: Done
> *As the Agent, I want the Player's room mix per act, compared between wins and losses, so that path planning has a baseline.*
>
> **Acceptance criteria**
> - [ ] Per act: mean count of monsters, elites, unknowns, shops, rest sites and treasure, for wins and losses separately.
> - [ ] Elites per act against reaching the next act.

> **P1.E4.S2: Rest-site policy** · Size S · Status: Done
> *As the Agent, I want the HP level at which the Player rests rather than upgrades, so that rest decisions have a starting rule.*
>
> **Acceptance criteria**
> - [ ] A table of HP% buckets (0–30, 30–50, 50–70, 70–100) against choice (`HEAL`, `SMITH`, other), plus whether the next floor is a boss.
> - [ ] A threshold estimate: the HP% where HEAL and SMITH are equally likely.
> - [ ] Uses of the less common options (`DIG`, `COOK`, `KINDLE`, `HATCH`, `LIFT`, `CLONE`) are listed with their context.

> **P1.E4.S3: Shop behaviour** · Size S · Status: Done
> *As the Agent, I want to know how the Player spends gold, so that the shop policy reflects practice.*
>
> **Acceptance criteria**
> - [ ] Gold on arrival and gold spent. The split between card, relic, potion and removal purchases. The most bought relics.

> **P1.E4.S4: Event and Ancient choices** · Size S · Status: Done
> *As the Agent, I want the Player's choices per event and Ancient, so that each one has a default.*
>
> **Acceptance criteria**
> - [ ] Per event ID: the options chosen with counts.
> - [ ] Per Ancient: the options offered and the pick rate.
> - [ ] Outcomes recorded where visible (HP change, cards and relics gained).

> **P1.E4.S5: Potion use** · Size S · Status: Done
> *As the Agent, I want to know where potions get used and wasted, so that the potion policy is calibrated.*
>
> **Acceptance criteria**
> - [ ] Potions used by room type (hallway, elite, boss). Potions still held at death. Potions discarded.

---

### P1.E5: Death analysis

> **P1.E5.S1: Death table** · Size S · Status: Done
> *As the Agent, I want every death described in one row, so that common failure patterns stand out.*
>
> **Acceptance criteria**
> - [ ] Each row: floor, act, encounter, HP entering as an absolute and a %, deck size, upgrades, relic count, potions held.

> **P1.E5.S2: Deep dives on the top killers** · Size M · Status: Done
> *As the Agent, I want to know why the Player loses to specific bosses, so that boss plans in Phase 2 address real failure modes.*
>
> **Acceptance criteria**
> - [ ] For Vantom (6 Ironclad deaths), Knowledge Demon (4), Soul Fysh (3) and the Entomancer elite (3): arrival HP distribution, turns survived, and deck features in fights won compared with fights lost against the same enemy.
> - [ ] Written up in `reports/phase1/deaths.md`.

> **P1.E5.S3: HP trajectories** · Size S · Status: Done
> *As the Player, I want to see how HP moves through a run, so that the act where runs start to fail is visible.*
>
> **Acceptance criteria**
> - [ ] A chart of median HP% by floor for wins and losses, overall and by ascension band. A cumulative death distribution by floor.

---

### P1.E6: Deck archetypes

> **P1.E6.S1: Cluster final decks** · Size M · Status: Done
> *As the Agent, I want the Player's recurring deck shapes identified, so that the playbook can describe archetypes and when to commit to them.*
>
> **Acceptance criteria**
> - [ ] Final decks as card-count vectors, excluding starter cards.
> - [ ] Jaccard distance with agglomerative clustering. k (3–6) is chosen by inspection.
> - [ ] Each cluster gets a name, its defining cards, its run count and its win rate with n.

> **P1.E6.S2: Commit signals** · Size S · Status: Done
> *As the Agent, I want to know when each archetype's key cards arrive, so that the playbook can say when to commit.*
>
> **Acceptance criteria**
> - [ ] For each archetype: the median floor at which its first and second key cards were taken.

---

### P1.E7: Visual report

> **P1.E7.S1: Interactive report for the Player** · Size M · Status: Done ((private link) data built by tools/build_report_data.py)
> *As the Player, I want to browse the findings visually, so that I can react to them before the interview.*
>
> **Acceptance criteria**
> - [ ] One HTML report, published as a private artifact. It has:
>   - card pick rates and the implied ranking
>   - the danger table
>   - HP trajectories
>   - the rest threshold chart
>   - the death breakdown
>   - archetypes
> - [ ] A "Top 10 findings" summary in plain language at the top.

---

### P1.E8: Player interview

> **P1.E8.S1: Select interview cases** · Size S · Status: Done
> *As the Agent, I want 10–15 decisions worth asking about, so that the interview targets the most informative moments.*
>
> **Acceptance criteria:** the cases come from these sources.
> - [ ] Picks that contradict the Player's own implied ranking.
> - [ ] Decisions in the 2–3 floors before a death.
> - [ ] Unusual rest or shop choices compared with the Player's thresholds.
> - [ ] Skips of cards the Player usually takes.
> - [ ] Each case is shown as a card: floor, HP, deck summary, options, choice. The case list is saved in `reports/phase1/interview-cases.md`.

> **P1.E8.S2: Conduct the interview** · Size S (plus Player time) · Status: Done
> *As the Player, I want the interview in short batches, so that it feels like talking about the game, not filling in a form.*
>
> **Acceptance criteria**
> - [ ] Batches of 3–5 cases in chat. Answers are recorded close to verbatim in `knowledge/player-reasoning.md`.

> **P1.E8.S3: Record answers as context and hypotheses** · Size S · Status: Done
> *As the Agent, I want each answer recorded with a data check, so that the Player's reasoning informs play only as far as the evidence supports it.*
>
> **Acceptance criteria**
> - [x] Each answer is recorded with a data check and linked back to its case.
> - [x] An answer becomes a playbook rule only when outcome evidence supports it. Otherwise it is recorded as a habit (baseline) or a `[HYPOTHESIS]` for Phase 4.
>
> **Notes:** the interview closed after two batches (2026-11-18). The Player clarified that the goal is strong play, not imitation, so the remaining cases (5, 8–14) were dropped.

---

### P1.E9: Playbook v1

> **P1.E9.S1: Write `playbooks/ironclad.md` v1** · Size M · Status: Done
> *As the Next Session, I want one playbook file that contains everything I need to draft and path as Ironclad, so that I can play from it without re-reading reports.*
>
> **Acceptance criteria:** it follows `templates/playbook.md`, with these sections.
> 1. Win conditions and the Ironclad overview
> 2. Card tiers by act (S, A, B, C, avoid), with context rules
> 3. Archetypes and commit signals
> 4. Path planning and HP budget per act
> 5. Rest-site policy
> 6. Shop policy, including removal
> 7. Events and Ancients
> 8. Potion policy
> 9. Boss preparation (filled in during Phase 2)
> 10. Player baseline: habits to beat or test, not targets
> 11. Hypotheses to test
> 12. Changelog
>
> - [ ] Every rule has a provenance label and an evidence pointer (a report file, row or n).

> **P1.E9.S2: Player review** · Size S · Status: Optional (the Player may flag factual errors at any time; not a gate)
> *As the Player, I want to review the playbook, so that factual errors are caught before the Agent builds on it. The playbook aims at strong play, not at representing my style.*
>
> **Acceptance criteria**
> - [ ] The Player's edits and comments are applied. Changelog entry: "v1, reviewed by the Player".

---

## 4. Statistical cautions

These go at the top of every report.

1. **Selection bias:** which cards get offered depends on earlier picks and relics. Pick rates are conditional on what was offered.
2. **Survivorship:** late-floor statistics come only from runs that got there. Act 3 numbers describe the Player's better runs.
3. **Confounding by ascension:** higher ascension means more damage everywhere. Compare within bands.
4. **Small samples:** 12 Ironclad wins. Show n next to every rate. Treat win correlations as hypotheses.
5. **Multiple comparisons:** with about 100 cards, some will look significant by chance. Do not promote a single-test result to a rule.

---

## 5. Exit gate

- [ ] E1 done, with validation passing
- [ ] E2.S1–S2, E3, E4.S2 and E5 done
- [ ] E8 done (interview complete)
- [x] E9.S1 done (playbook v1 written). The Player's review is optional (2026-11-19): the Player's statistics are a rough guide, and the target is to play better than the Player.
- [ ] E6 and E7 done, or explicitly deferred in STATUS.md

---

## 6. Open questions

| ID | Question | Resolved by |
|---|---|---|
| OQ1.1 | Do `cards_gained` and the other change fields capture every deck change, or do some card effects add cards without logging them? | **Resolved:** 232/232 decks match by card, 230/232 including upgrades |
| OQ1.2 | Is `turns_taken` reliable for every room type? | **Resolved:** every fight has turns_taken > 0 |
| OQ1.3 | Can encounter IDs be mapped to acts from the floor position alone, or do some appear in several acts? | **Resolved:** each encounter appears in exactly one act |
