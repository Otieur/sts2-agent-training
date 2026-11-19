# Phase 2: Knowledge Base

**Goal:** a verified, version-tagged reference for game v0.107.1, covering cards, relics, potions, mechanics, enemies, encounters and bosses. Community strategy is merged into Ironclad playbook v2 with clear provenance.

**Depends on:** Phase 0 for game data exported through the mod; Phase 1 for encounter lists and the Player's habits. Community research (E4) can start at any time.
**Unblocks:** Phases 3 and 4.

---

## 1. What to expect

| | |
|---|---|
| **Duration** | 2–3 Agent sessions |
| **Player time** | Optional. About 15 minutes to review the discrepancy report (community versus Player habits), and possibly a few in-game checks if a mechanic cannot be confirmed from data. |
| **Volume** | Several hundred cards across all pools, a hundred or more relics, dozens of potions, and every encounter seen in the history |
| **Main risk** | The mod's `/data` endpoints may not cover every collection. Fallbacks: the STS2MCP wiki search, the in-game Compendium and Bestiary, and community wikis, labelled until verified. |
| **What changes for play** | The Agent stops guessing what a card or enemy does. Boss fights get a written plan. The playbook gains outside knowledge where the Player's history was thin. |

---

## 2. Folder layout

```
knowledge/
  data/v0.107.1/        raw JSON exports from the mod (cards.json, relics.json, ...)
  cards/                ironclad.md, necrobinder.md, colorless.md, curses-status.md
  relics.md  potions.md  mechanics.md  ascension.md  events.md
  encounters.md         catalogue: every encounter, pool, act, HP, link to its note
  enemies/<ENEMY_ID>.md per-enemy notes (template: templates/enemy-note.md)
  bosses/<BOSS_ID>.md   boss plans (template: templates/boss-plan.md)
  community/            sources.md, ironclad-tiers.md, discrepancies.md
  combat-lessons.md     filled in during Phases 3 and 4
  player-reasoning.md   from the Phase 1 interview
```

Every file starts with a header: game version, date, sources, and the labels used.

---

## 3. Epics and stories

### P2.E1: Game data export

> **P2.E1.S1: Enumerate the data collections** · Size XS · Status: Todo
> *As the Agent, I want the list of collections the mod serves, so that I know what is available first-hand.*
>
> **Acceptance criteria**
> - [ ] The collection names are listed in `docs/api-notes.md`, from the API docs and by probing `GET /data/<name>` for: cards, relics, potions, monsters, encounters, events, powers, keywords, characters, acts.
> - [ ] Unavailable collections are noted with their error codes (`collection_not_found`, `game_data_unavailable`).

> **P2.E1.S2: Export the raw data** · Size S · Status: In progress (extract imported to knowledge/data/extract-2026-09-21/; live /data export on v0.107.1 pending)
> *As the Next Session, I want raw exports saved by version, so that a game patch can be diffed rather than re-researched.*
>
> **Acceptance criteria**
> - [ ] `knowledge/data/v0.107.1/<collection>.json`, each with a sidecar `.meta.json` (export time, mod version, game version, record count).

> **P2.E1.S3: Readable card references** · Size M · Status: Done (from the extract, knowledge/cards/ironclad.md; re-verify numbers against live /data)
> *As the Agent, I want a compact card reference per pool, so that I can read a card's full text and role without calling the API mid-decision.*
>
> **Acceptance criteria**
> - [ ] `knowledge/cards/ironclad.md` and `colorless.md`, plus `curses-status.md`. Each card has: name, ID, cost, type, rarity, base and upgraded text, and role tags (`damage`, `aoe`, `block`, `draw`, `energy`, `scaling`, `exhaust`, `self-damage`, `strength`, `retain`, `X-cost`, `co-op-only`).
> - [ ] Sorted by rarity, then name. The pick rate and implied rank from Phase 1 sit next to each card.

> **P2.E1.S4: Relics and potions** · Size S · Status: Todo
> *As the Agent, I want relic and potion references with role tags, so that rewards and shops can be evaluated quickly.*
>
> **Acceptance criteria**
> - [ ] `knowledge/relics.md` and `potions.md`. Each entry has its effect text, rarity or source, character restriction and role tags. The Player's pick and purchase counts are added where they exist.

> **P2.E1.S5: Fallback sources** · Size S · Status: Done (the decompiled extract served as the fallback source)
> *As the Agent, I want a fallback for missing collections, so that gaps do not block the knowledge base.*
>
> **Acceptance criteria**
> - [ ] Gaps are filled from one of: the STS2MCP `search_wiki` endpoint (if that mod is installed), in-game Compendium or Bestiary screenshots, or community wikis.
> - [ ] Every such entry is labelled `[COMMUNITY]` until confirmed in game.

---

### P2.E2: Mechanics reference

> **P2.E2.S1: Core rules** · Size M · Status: Done (knowledge/mechanics.md; exact multipliers from the extract, order and rounding on the checklist)
> *As the Agent, I want the combat rules written down exactly, so that turn planning uses correct arithmetic.*
>
> **Acceptance criteria:** `knowledge/mechanics.md` covers:
> - [ ] Turn order and energy.
> - [ ] Draw, discard, shuffle and exhaust.
> - [ ] Block expiry, and intents and how to read them.
> - [ ] Every common status and power, with exact numbers: Strength, Dexterity, Vulnerable, Weak, Frail, Artifact, Thorns, Plated Armor, Ritual, Intangible, and any found in the data.
> - [ ] Rounding rules, and the order of operations for damage (additive before multiplicative, and so on).
> - [ ] Each number is labelled `[GAME]` if read from data or verified in a fight. Otherwise it is labelled `[COMMUNITY]` and added to the verification list.

> **P2.E2.S2: Verification list** · Size S · Status: Done (11-item checklist at the end of knowledge/mechanics.md)
> *As the Agent, I want unverified mechanics tested in real fights, so that the damage calculator in Phase 4 is right.*
>
> **Acceptance criteria**
> - [ ] `knowledge/mechanics.md` ends with a checklist of rules to verify: for example "Vulnerable multiplier", "Weak multiplier", "rounding of 1.5× on odd values".
> - [ ] Each item has a test: which card on which enemy, and the expected number. The tests run during the first Phase 4 runs, or the Player runs them.

> **P2.E2.S3: Ascension modifiers** · Size S · Status: Done (knowledge/ascension.md; 5 of 10 levels confirmed in run data)
> *As the Agent, I want every ascension level's effect listed, so that strategy can adjust per level.*
>
> **Acceptance criteria**
> - [ ] `knowledge/ascension.md`: A1–A10, each with its effect and the strategy implication (for example "fewer heals: raise the rest threshold").

> **P2.E2.S4: Map and room types** · Size S · Status: Done (acts, bosses by act variant, boss known at act start; in knowledge/mechanics.md)
> *As the Agent, I want the map structure documented, so that path planning knows what is possible.*
>
> **Acceptance criteria**
> - [ ] The acts seen in the data (for example Underdocks, Hive, Glory) and how acts are chosen.
> - [ ] Room types and their odds where known, the Ancient system, and the boss-relic and Act-transition rules.

---

### P2.E3: Enemies and encounters

> **P2.E3.S1: Encounter catalogue** · Size M · Status: Done (knowledge/encounters.md, 83 encounters)
> *As the Agent, I want every encounter listed with its pool, act, enemies and danger, so that path planning can look ahead.*
>
> **Acceptance criteria**
> - [ ] `knowledge/encounters.md`: encounter ID, act, pool, monster IDs, HP ranges (from `/data/monsters` `min_hp` and `max_hp`), the Player's median and p90 damage (Phase 1 benchmark), and a link to its note.

> **P2.E3.S2: Hallway encounter notes** · Size L · Status: Done (15 most frequent hallway encounters)
> *As the Agent, I want a short note for each common hallway encounter, so that I know the dangerous turn and the right answer before the fight starts.*
>
> **Acceptance criteria:** one note per encounter with n ≥ 5 in the history, using `templates/enemy-note.md`.
> - [ ] Enemies and HP.
> - [ ] Move pattern or intent cycle.
> - [ ] Dangerous turns.
> - [ ] Priorities (which enemy to kill first).
> - [ ] Recommended answers (AoE, block thresholds, debuff timing).
> - [ ] The Player's median damage.
> - [ ] Sources with labels.

> **P2.E3.S3: Elite notes** · Size M · Status: Done (all 12 elites, with ready-to-fight checklists)
> *As the Agent, I want detailed notes for every elite, so that elite pathing decisions account for deck readiness.*
>
> **Acceptance criteria**
> - [ ] Every elite seen in the history gets a hallway note plus:
>   - a "ready to fight" checklist: minimum front-loaded damage, block per turn, AoE needed or not
>   - the deaths it caused in the history (for example Entomancer, Infested Prisms, Byrdonis, Phrog Parasite)

> **P2.E3.S4: Bestiary cross-check** · Size S · Status: Todo
> *As the Agent, I want the notes checked against the in-game Bestiary, so that move patterns come from the game itself.*
>
> **Acceptance criteria**
> - [ ] Where the Bestiary is readable through the mod or from screenshots, each note's move pattern is checked and re-labelled `[GAME]`.

---

### P2.E4: Community strategy

> **P2.E4.S1: Source collection** · Size M · Status: Done
> *As the Agent, I want a list of reputable sources with their version and date, so that outdated advice is easy to spot.*
>
> **Acceptance criteria**
> - [ ] `knowledge/community/sources.md`: title, URL, author type (guide site, high-ascension player, wiki), game version covered, date, and a quality note. Sources older than v0.107.0 are flagged.
> - [ ] Aggregated statistics sites are included with their sample sizes. Example: MetaBot (metabot.gg) lists card pick and win rates from a few hundred tracked runs across all characters (519 as seen on 2026-11-19), which is small, and its pages can disagree with each other.

> **P2.E4.S2: Normalised community tier list** · Size M · Status: Done (three sources, weighted by version match)
> *As the Agent, I want a single community view of Ironclad cards, so that it can be compared with the Player's priorities.*
>
> **Acceptance criteria**
> - [ ] `knowledge/community/ironclad-tiers.md`: each card's tier (S, A, B, C, D) as a consensus across at least 2 sources where possible, with source counts and notes where they disagree.

> **P2.E4.S3: Archetype guides** · Size S · Status: Done (knowledge/community/archetypes-ironclad.md)
> *As the Agent, I want the known Ironclad archetypes summarised, so that the playbook covers builds the Player has not tried.*
>
> **Acceptance criteria**
> - [ ] Each archetype: key cards, key relics, commit signals, weaknesses. These are compared with the Phase 1 archetype clusters.

> **P2.E4.S4: Discrepancy report** · Size S · Status: Done (23 discrepancies; to discuss or test)
> *As the Player, I want to see where my habits differ from community consensus, so that we can discuss which view is right.*
>
> **Acceptance criteria**
> - [ ] `knowledge/community/discrepancies.md`: cards the Player rates much higher or lower than the community (a rank difference of 2 or more tiers), with the Player's pick rate, the community tier and a question for the Player.
> - [ ] The top 5 are discussed with the Player during Phase 3, or in a short chat.

---

### P2.E5: Boss plans

> **P2.E5.S1: One plan per boss** · Size L · Status: Done (12 boss plans in knowledge/bosses/, data blocks auto-generated)
> *As the Agent, I want a written plan for every boss, so that the deck is built toward the fight from Act start, not improvised on arrival.*
>
> **Acceptance criteria:** `knowledge/bosses/<BOSS_ID>.md` exists for every boss in the history (including Vantom, Knowledge Demon, Soul Fysh, Aeonglass, Test Subject, Ceremonial Beast and Waterfall Giant), using `templates/boss-plan.md`:
> - [ ] Mechanics and move cycle.
> - [ ] **Deck checklist:** required damage per turn, block per turn, scaling, and AoE if there are adds, with concrete numbers.
> - [ ] HP target on arrival.
> - [ ] A turn-by-turn plan for the first 3 turns.
> - [ ] Potion plan.
> - [ ] What killed the Player here (from Phase 1 E5.S2) and the counter.

> **P2.E5.S2: Act-level boss preparation** · Size S · Status: Done (bosses by act in knowledge/mechanics.md; boss visible at act start via map state)
> *As the Agent, I want to know which bosses are possible in each act, so that the deck can be prepared for the likely ones.*
>
> **Acceptance criteria**
> - [ ] The playbook's boss preparation section lists the possible bosses per act. It notes whether the boss is visible on the map at the start of the act, and what that changes for the act plan.

---

### P2.E6: Playbook v2

> **P2.E6.S1: Merge the knowledge into the playbook** · Size M · Status: Todo
> *As the Next Session, I want the playbook to combine the Player's practice, game facts and community knowledge with clear labels, so that I know how much to trust each rule.*
>
> **Acceptance criteria**
> - [ ] Card tiers are updated using the conflict precedence in `docs/README.md`. Every conflict is listed under "Open questions" with both views.
> - [ ] The boss preparation section links to every boss plan.
> - [ ] Changelog entry: v2, with a summary of what changed and why.

> **P2.E6.S2: Optional Player review** · Size XS · Status: Todo
> *As the Player, I want to skim the changes from v1 to v2, so that I can object before the Agent starts playing from it.*
>
> **Acceptance criteria**
> - [ ] A diff summary in chat (10 bullet points at most). The Player's objections are recorded.

---

### P2.E7: Knowledge maintenance

> **P2.E7.S1: Patch procedure** · Size S · Status: Todo
> *As the Next Session, I want a procedure for game updates, so that the knowledge base does not silently go stale.*
>
> **Acceptance criteria**
> - [ ] `docs/runbooks/game-patch.md` covers:
>   - detect a new version from `/health` or the logs
>   - export the data to a new version folder
>   - diff it against the previous export
>   - mark affected notes and playbook rules `STALE (vX)`
>   - re-verify the high-impact items first

---

## 4. Exit gate

- [ ] E1.S1–S4 done (or S5 fills the gaps)
- [ ] E2.S1 and E2.S3 done; the E2.S2 verification list exists
- [ ] E3.S1 and E3.S3 done; E3.S2 covers at least the 15 most common hallway encounters
- [ ] E4.S2 and E4.S4 done
- [ ] E5.S1 done for every boss in the history
- [ ] E6.S1 done (playbook v2)

---

## 5. Open questions

| ID | Question | Resolved by |
|---|---|---|
| OQ2.1 | Which collections does `/data` serve on v0.107.1? | P2.E1.S1 |
| OQ2.2 | Can the Bestiary be read through the mod? | P2.E3.S4 |
| OQ2.3 | Is the Act boss visible at the start of the act? | **Resolved (likely yes):** the map state holds the boss (STS2MCP exposes it); confirm live |
| OQ2.4 | How much good v0.107.x-specific community material exists? Early access balance changes often. | P2.E4.S1 |
