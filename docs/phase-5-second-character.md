# Phase 5: Second Character (Necrobinder)

**Goal:** take Necrobinder through the same pipeline as Ironclad, reusing everything that is not specific to a character. Measure how much carries over. Decide which character the Agent plays in co-op.

**Depends on:** Phases 1–4. The tools, knowledge base and harness all exist by now.
**Unblocks:** Phase 6, by giving a second trained character and a co-op pairing decision.

---

## 1. What to expect

| | |
|---|---|
| **Duration** | About half the time of Phases 1–4 combined. The extraction, benchmark, harness, enemy notes and boss plans already exist. |
| **Player time** | A short interview (5–8 cases), 2 shadowed runs, and an optional playbook review |
| **Why Necrobinder** | The most recorded card reward decisions of any character (746), 59 runs, 11 wins, and a spread of ascension levels (16 runs at A10) |
| **What is new** | Necrobinder's own mechanics and card pool. Different deck archetypes. Possibly different encounter danger, because the same fight plays differently with a different kit. |
| **What carries over** | Mechanics, enemy notes, boss move cycles, pathing logic, the run harness, the post-mortem pipeline, the calculator (extended for new statuses) |
| **Risk** | Necrobinder's extra mechanics may need new fields in the brief state view and new arithmetic in the calculator. Check that first. |

---

## 2. Epics and stories

### P5.E1: Rerun the history pipeline

> **P5.E1.S1: Run the Phase 1 pipeline with a character parameter** · Size S · Status: Done (2026-11-19, all four characters)
> *As the Agent, I want every Phase 1 script to take a character argument, so that a new character costs one command, not a rewrite.*
>
> **Acceptance criteria**
> - [ ] Each `tools/*.py` analysis accepts `--character NECROBINDER`. Reports go to `reports/phase5/`.
> - [ ] The benchmark is frozen as `data/benchmarks/necrobinder-encounters-v0.107.1.csv`.

> **P5.E1.S2: Compare with Ironclad** · Size S · Status: Done (reports/phase1/cross-character.md)
> *As the Agent, I want to know which encounters are harder or easier for Necrobinder than for Ironclad, so that pathing adjusts per character.*
>
> **Acceptance criteria**
> - [ ] A table of encounters with n ≥ 5 for both characters: median damage for each, and the difference.
> - [ ] Notable differences (more than 25%) are written into both playbooks.

### P5.E2: Necrobinder knowledge

> **P5.E2.S1: Card reference** · Size M · Status: Done (knowledge/cards/necrobinder.md from the extract)
> *As the Agent, I want the Necrobinder pool documented the same way as Ironclad's, so that drafting has full information.*
>
> **Acceptance criteria**
> - [ ] `knowledge/cards/necrobinder.md`, built from the game data with role tags (adding tags for character-specific mechanics) and the Phase 5 pick rates.

> **P5.E2.S2: Mechanics** · Size M · Status: Todo
> *As the Agent, I want Necrobinder's own mechanics specified exactly, so that combat arithmetic and state reading cover them.*
>
> **Acceptance criteria**
> - [ ] The character's unique resources, companion or summon rules, and statuses are documented in `knowledge/mechanics.md` from the game data. They are verified in a test fight.
> - [ ] `tools/sts.py state --brief` shows the relevant fields.
> - [ ] `tools/calc.py` is extended, with tests.

> **P5.E2.S3: Community strategy** · Size S · Status: In progress (tiers and discrepancies done 2026-11-19: knowledge/community/necrobinder-tiers.md, discrepancies-necrobinder.md, playbook v0.1 §3; archetypes still to do)
> *As the Agent, I want community tiers and archetypes for Necrobinder, so that the playbook is not limited to the Player's habits.*
>
> **Acceptance criteria**
> - [ ] The equivalents of P2.E4.S2–S4 for Necrobinder.

### P5.E3: Playbook v1 (Necrobinder)

> **P5.E3.S1: Short interview** · Size S (plus Player time) · Status: Todo
> *As the Player, I want a shorter interview this time, so that it does not repeat what we already covered.*
>
> **Acceptance criteria**
> - [ ] 5–8 cases chosen with the P1.E8.S1 criteria, focused on character-specific choices. Answers are added to `knowledge/player-reasoning.md`.

> **P5.E3.S2: Write the playbook** · Size M · Status: In progress (v0 groundwork draft, 2026-11-19)
> *As the Next Session, I want `playbooks/necrobinder.md` built on the same template, so that switching characters is seamless.*
>
> **Acceptance criteria**
> - [ ] Same sections as Ironclad. Shared content (pathing logic, boss plans) is linked, not copied.
> - [ ] The Player reviews it.

### P5.E4: Light shadowing

> **P5.E4.S1: Two shadowed runs** · Size S (plus Player time) · Status: Todo
> *As the Agent, I want to watch the Player play Necrobinder twice, so that I see the character's combat flow before playing it.*
>
> **Acceptance criteria**
> - [ ] The Phase 3 protocol with the existing tools, for 2 runs. Agreement metrics go to `metrics/shadow.csv`, with a character column. Playbook updated.

### P5.E5: Solo ladder

> **P5.E5.S1: Solo runs to the M3 equivalent** · Size XL · Status: Todo
> *As the Player, I want the Agent to win a Necrobinder run, so that it has two characters it can bring to co-op.*
>
> **Acceptance criteria**
> - [ ] The Phase 4 harness and ladder, unchanged. First win at A0 recorded in `metrics/milestones.md` as "M3 (Necrobinder)".
> - [ ] Exam seeds: 3 Necrobinder seeds from the Player's history.

### P5.E6: Transfer report and co-op pairing

> **P5.E6.S1: Transfer report** · Size S · Status: Todo
> *As the Player, I want to know how much the second character benefited from the first, so that we can decide whether to train Regent and Silent later.*
>
> **Acceptance criteria**
> - [ ] `reports/phase5/transfer.md`: time per phase compared with Ironclad, the knowledge reused, new work needed, runs to first win for each character.

> **P5.E6.S2: Co-op pairing decision** · Size XS · Status: Todo
> *As the Player, I want to choose which character the Agent plays in co-op, so that our characters complement each other.*
>
> **Acceptance criteria**
> - [ ] The Agent presents the options: its trained characters, against the character the Player wants to play. Each comes with strengths, weaknesses and how the pairing covers each other's gaps (front-loaded damage, block, scaling, AoE, support).
> - [ ] The Player decides. The choice is recorded in `docs/decisions/0003-coop-pairing.md`.

---

## 3. Exit gate

- [ ] Necrobinder playbook v1 reviewed, and 2 shadowed runs done
- [ ] First Necrobinder solo win (M3 equivalent)
- [ ] Transfer report written
- [ ] Co-op pairing decided

## 4. Later (optional)

Regent and Silent can go through the same pipeline later. With the tools mature, each should take less time again. They come after the first co-op win, unless the Player wants them sooner.
