# Player Reasoning

The Player's own explanations of their decisions, from interviews and retros, each with a data check.

**How this file is used.** The goal is strong play, not imitation of the Player (clarified by the Player, 2026-11-18). Entries here are context and hypotheses. An entry turns into a playbook rule only when outcome evidence supports it. Habits with no outcome support are kept as a **baseline**: something to beat or test, not a target.

Each entry records:
- **Habit:** what the Player does and why, in the Player's words.
- **Evidence:** what the history shows about outcomes.
- **Use:** how it enters the playbook: rule (with its evidence label), baseline, or hypothesis to test.

---

## Principle: the need triangle

- Asked: 2026-11-18 (volunteered)
- Habit: "There's a need triangle: attack, defend, and operations (draw cards and gain energy). It's impossible to have a perfect three, just need to balance." Which corner is short is judged "based on feelings". Card counts are not used.
- Evidence: none either way yet; the run files carry no card types. Phase 2 game data makes it measurable.
- Use: **framework, adopted.** The card reward procedure (P4.E3.S2) assesses the deck against attack, defence and operations, plus two additions: scaling for long boss fights (6–10 turns) and attack shape (multi-hit or cheap against big single hits; single-target against multi-target). Unlike the Player, the Agent judges "short" by measured quantities, such as expected damage and block per turn and cards drawn per turn, with thresholds to be set in Phase 2.

## Ironclad cases 1–4: smithing at low HP before a boss or a hard fight

- Asked: 2026-11-18
- Habit: "Considering it's A9, high ascension, my thought process is either get strong to face Act 2 and 3 or die."
- Evidence (v0.107.1, rest site directly before a boss):
  - Ironclad, HP 35–50%: died at the boss after HEAL 1/6 (17%), after SMITH 3/12 (25%).
  - Ironclad, HP under 35%: HEAL 6/16 (38%), SMITH 2/4 (50%).
  - All characters, HP 35–50%: HEAL 7/33 (21%), SMITH 15/48 (31%).
  - All characters, HP under 35%: HEAL 24/68 (35%), SMITH 3/14 (21%). Likely selection: smithing that low happens only when the deck already looks strong.
  - A HEAL restores a median 29% of max HP (n=297), about 23 HP on 80.
  - The Vantom benchmark is a median of 48 damage and a p90 of 63.
  - Mixed, small samples.
- Use: **hypothesis to test** (Phase 4). Before a boss, rest if HP is below that boss's median benchmark damage plus a margin; otherwise smith. The Player's "always get strong" stays as the baseline to compare against.

## Ironclad cases 6–7: Anger taken early in Act 1

- Asked: 2026-11-18
- Habit: "I think I was really low on attack that run? Couldn't remember. Need more attacks." (The answer was pasted under the rest-site heading; it is recorded here as the Anger answer.)
- Evidence: at floors 3 and 5, both decks held only starter attacks plus one or two other cards. No outcome data on the rule itself.
- Use: **consistent with the triangle framework.** Front-loaded damage in early Act 1 is also standard community advice, to be confirmed in Phase 2. Anger costs 0 energy, which is what Vantom's Slippery rewards.

## Ironclad case 11: elites at moderate or low HP

- Asked: 2026-11-18
- Question: On 2026-10-03 (A9, floor 30, 52/80 HP), three floors before the Act 2 boss, the Player took Decimillipede, lost 43 HP and died to Kaiser Crab. How is the decision to take an elite made?
- Habit: "Same thought process as being strong enough for later Act 3, because it's high ascension."
- Evidence (elite fights in Acts 1–2, v0.107.1, by HP on arrival):

  | HP on arrival | Ironclad: died in the elite | Ironclad: survived the act | All characters: died in the elite | All characters: survived the act |
  |---|---|---|---|---|
  | under 50% | 4/16 (25%) | 8/16 (50%) | 16/66 (24%) | 38/66 (58%) |
  | 50–70% | 3/32 (9%) | 18/32 (56%) | 10/121 (8%) | 75/121 (62%) |
  | 70%+ | 2/31 (6%) | 26/31 (84%) | 4/121 (3%) | 99/121 (82%) |

  The death rate inside the elite fight itself is direct evidence: about 3–8× higher under 50% HP.
- Use: **rule** `[PLAYER-DATA]` (outcome evidence, n=308 elite fights): avoid elites under 50% HP unless the alternative path is worse or the deck clearly handles that elite. Between 50% and 70%, decide by the elite's benchmark damage. The Player's "always take it for scaling" is the baseline.

## Ironclad: knowing the boss in advance

- Asked: 2026-11-18
- Question: When the act boss is visible at the start of the act, does it change drafting or pathing?
- Habit: "Yes." No detail given.
- Use: **rule in principle** (standard practice; the specifics are Phase 2 boss plans). At each act start, read the boss and load its plan (`knowledge/bosses/`). Draft and path toward its checklist, for example cheap and multi-hit attacks for Vantom.

## Ironclad: Vantom

- Asked: 2026-11-18
- Habit: "I honestly have no idea."
- Evidence: Vantom fights by character on v0.107.1:
  - Ironclad: 11 fights, 6 deaths, mean 48 damage
  - Necrobinder: 5 fights, 3 deaths, 33 damage
  - Silent: 6 fights, 2 deaths, 24 damage
  - Regent: 4 fights, 1 death, 20 damage
  - Defect: 2 fights, 0 deaths, 17 damage
- Use: research priority 1 for Phase 2. Early notes and the Slippery hypothesis are in `knowledge/bosses/VANTOM_BOSS.md`.

## Ironclad: card removal

- Asked: 2026-11-18
- Habit: "I just think removals aren't that strong. If I have enough cards with draw effects, or if my deck is big enough, having one less card doesn't matter."
- Evidence:
  - Arithmetic: one basic removed from a 15-card deck with 9 basics raises non-basic draws from 40% to 43%. From a 25-card deck with 8 basics, from 68% to 71%. Small per card, which supports the Player's view.
  - Outcome (confounded): Ironclad runs that removed a Strike or Defend in Act 1 survived Act 1 in 11/14 (79%), against 19/38 (50%).
  - Ascender's Bane (present from A5) was never removed.
- Use: **hypothesis to test** (Phase 4): remove a Strike at the first Act 1 shop when affordable, against the Player's baseline of relics first.
