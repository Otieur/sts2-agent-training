# Ironclad Community Tiers (normalised)

Built by `tools/build_community_tiers.py` on 2026-11-19. Label: `[COMMUNITY]`. Sources and their versions are in `sources.md`.

| Source | Kind | Version | Weight |
|---|---|---|---|
| Spire Codex guide | Win rate when picked, community-submitted runs; partial list | Main branch, mid-July 2026 (v0.107.x era) | 2 |
| MetaBot | Win rate of tracked runs containing the card (survivorship-biased, no sample sizes); converted to quintiles | Not stated | 1 |
| Nat 1 Gaming | Expert opinion | 11/12 beta patch (v0.113.x), **not our version** | 1 |

Consensus = weighted mean of tier scores (S=5 … F=0; MetaBot quintiles 0.5–4.5), mapped back: S ≥ 4.25, A ≥ 3.5, B ≥ 2.75, C ≥ 2.0, D below. **Spread** is the gap in tiers between the most and least favourable source; 2 or more means the sources disagree. The Player column is the quintile of the Player's own head-to-head score (habit, cards with 10+ comparisons).

| Card | Rarity | Consensus | Score | Spire Codex | MetaBot | Nat1 (beta) | Spread | Player habit | Player picked |
|---|---|---|---|---|---|---|---|---|---|
| Offering | Rare | **S** | 4.38 | A | S | S | 1 | S | 4/4 |
| Cascade | Rare | **S** | 4.25 | - | S | A | 1 | C | 2/13 |
| Conflagration | Rare | **S** | 4.25 | - | S | A | 1 | S | 4/7 |
| Corruption | Ancient | **S** | 4.25 | - | S | A | 1 | - | - |
| Demon Form | Rare | **S** | 4.25 | - | S | A | 1 | C | 2/10 |
| Feed | Rare | **S** | 4.25 | - | A | S | 1 | A | 2/7 |
| Stoke | Rare | **S** | 4.25 | - | S | A | 1 | S | 3/7 |
| Unmovable | Rare | **S** | 4.25 | - | S | A | 1 | - | 0/9 |
| Crimson Mantle | Rare | **A** | 4.12 | A | S | A | 1 | A | 4/12 |
| Impervious | Rare | **A** | 4.12 | A | S | A | 1 | S | 4/7 |
| Fiend Fire | Rare | **A** | 3.88 | A | A | A | 0 | S | 4/5 |
| Battle Trance | Uncommon | **A** | 3.75 | - | A | A | 0 | C | 3/16 |
| Brand | Rare | **A** | 3.75 | - | A | A | 0 | S | 4/6 |
| Colossus | Rare | **A** | 3.75 | - | A | A | 0 | A | 10/19 |
| Dominate | Uncommon | **A** | 3.75 | - | A | A | 0 | S | 19/20 |
| Feel No Pain | Uncommon | **A** | 3.75 | - | S | B | 2 | C | 5/15 |
| Hellraiser | Rare | **A** | 3.75 | - | A | A | 0 | A | 2/6 |
| One Two Punch | Rare | **A** | 3.75 | - | S | B | 2 | S | 4/11 |
| Pyre | Rare | **A** | 3.75 | - | S | B | 2 | S | 11/13 |
| Tear Asunder | Rare | **A** | 3.62 | B | S | A | 2 | A | 2/7 |
| Barricade | Rare | **B** | 3.25 | - | S | C | 3 | C | 3/15 |
| Bloodletting | Common | **B** | 3.25 | - | C | A | 2 | C | 22/55 |
| Burning Pact | Uncommon | **B** | 3.25 | - | A | B | 1 | A | 11/18 |
| Cruelty | Rare | **B** | 3.25 | - | A | B | 1 | S | 4/5 |
| Juggernaut | Rare | **B** | 3.25 | - | S | C | 3 | - | 0/6 |
| Shrug It Off | Common | **B** | 3.25 | - | C | A | 2 | C | 21/73 |
| Aggression | Rare | **B** | 3.12 | B | S | C | 3 | S | 4/9 |
| Mangle | Rare | **B** | 3.12 | B | A | B | 1 | A | 3/9 |
| Pacts End | Rare | **B** | 3.12 | B | A | B | 1 | S | 3/5 |
| Thrash | Rare | **B** | 3.12 | B | C | A | 2 | S | 6/7 |
| Demonic Shield | Uncommon | **B** | 3.00 | - | - | B | - | - | - |
| Body Slam | Common | **B** | 2.75 | - | A | C | 2 | D | 4/45 |
| Bully | Uncommon | **B** | 2.75 | - | A | C | 2 | D | 3/13 |
| Dark Embrace | Rare | **B** | 2.75 | - | S | D | 4 | S | 4/5 |
| Expect A Fight | Uncommon | **B** | 2.75 | - | C | B | 1 | D | 0/14 |
| Flame Barrier | Uncommon | **B** | 2.75 | - | C | B | 1 | C | 4/12 |
| Forgotten Ritual | Uncommon | **B** | 2.75 | - | C | B | 1 | C | 7/18 |
| Pommel Strike | Common | **B** | 2.75 | - | D | A | 3 | D | 7/47 |
| Rupture | Uncommon | **B** | 2.75 | - | C | B | 1 | D | 2/12 |
| Second Wind | Uncommon | **B** | 2.75 | - | A | C | 2 | S | 13/19 |
| Stampede | Uncommon | **B** | 2.75 | - | D | A | 3 | A | 9/17 |
| True Grit | Common | **B** | 2.75 | - | C | B | 1 | A | 23/49 |
| Break | Ancient | **C** | 2.38 | D | C | S | 4 | - | - |
| Armaments | Common | **C** | 2.25 | - | D | B | 2 | A | 25/65 |
| Ashen Strike | Uncommon | **C** | 2.25 | - | C | C | 0 | A | 5/10 |
| Drum Of Battle | Uncommon | **C** | 2.25 | - | A | D | 3 | A | 9/21 |
| Evil Eye | Uncommon | **C** | 2.25 | - | C | C | 0 | S | 14/21 |
| Headbutt | Common | **C** | 2.25 | - | D | B | 2 | D | 7/57 |
| Howl From Beyond | Uncommon | **C** | 2.25 | - | D | B | 2 | D | 3/19 |
| Inferno | Uncommon | **C** | 2.25 | - | D | B | 2 | C | 3/12 |
| Juggling | Uncommon | **C** | 2.25 | - | A | D | 3 | D | 0/15 |
| Pillage | Uncommon | **C** | 2.25 | - | C | C | 0 | D | 4/16 |
| Rage | Uncommon | **C** | 2.25 | - | C | C | 0 | D | 4/19 |
| Stomp | Uncommon | **C** | 2.25 | - | D | A | 3 | D | 3/16 |
| Stone Armor | Uncommon | **C** | 2.25 | - | C | C | 0 | D | 1/22 |
| Taunt | Uncommon | **C** | 2.25 | - | D | B | 2 | D | 3/12 |
| Uppercut | Uncommon | **C** | 2.25 | - | D | B | 2 | C | 4/15 |
| Vicious | Uncommon | **C** | 2.25 | - | C | C | 0 | A | 12/25 |
| Anger | Common | **D** | 1.75 | - | D | C | 1 | D | 2/53 |
| Blood Wall | Common | **D** | 1.75 | - | D | C | 1 | D | 1/55 |
| Bludgeon | Uncommon | **D** | 1.75 | - | D | B | 2 | D | 1/21 |
| Dismantle | Uncommon | **D** | 1.75 | - | D | B | 2 | D | 3/14 |
| Fight Me | Uncommon | **D** | 1.75 | - | D | B | 2 | S | 11/14 |
| Inflame | Uncommon | **D** | 1.75 | - | D | C | 1 | D | 2/14 |
| Molten Fist | Common | **D** | 1.75 | - | D | C | 1 | A | 18/43 |
| Primal Force | Rare | **D** | 1.75 | - | D | B | 2 | - | 1/4 |
| Spite | Uncommon | **D** | 1.75 | - | D | C | 1 | D | 2/26 |
| Sword Boomerang | Common | **D** | 1.75 | - | D | C | 1 | D | 10/58 |
| Tremble | Common | **D** | 1.75 | - | C | D | 1 | A | 24/54 |
| Unrelenting | Uncommon | **D** | 1.75 | - | D | C | 1 | C | 5/16 |
| Whirlwind | Uncommon | **D** | 1.75 | - | D | B | 2 | D | 0/13 |
| Breakthrough | Common | **D** | 1.25 | - | D | C | 1 | C | 21/62 |
| Hemokinesis | Uncommon | **D** | 1.25 | - | D | C | 1 | D | 1/25 |
| Infernal Blade | Uncommon | **D** | 1.25 | - | D | C | 1 | C | 4/11 |
| Perfected Strike | Common | **D** | 1.25 | - | D | C | 1 | D | 2/52 |
| Rampage | Uncommon | **D** | 1.25 | - | D | C | 1 | D | 3/26 |
| Setup Strike | Common | **D** | 1.25 | - | D | C | 1 | D | 5/51 |
| Twin Strike | Common | **D** | 1.25 | - | D | C | 1 | D | 9/47 |
| Tank | Rare | **D** | 1.00 | - | - | D | - | - | - |
| Cinder | Common | **D** | 0.88 | D | D | D | 0 | D | 8/54 |
| Havoc | Common | **D** | 0.75 | - | D | F | 1 | D | 6/48 |
| Iron Wave | Common | **D** | 0.75 | - | D | D | 0 | D | 8/66 |
| Thunderclap | Common | **D** | 0.75 | - | D | D | 0 | D | 7/46 |

Spire Codex win rates when picked (main branch, mid-July 2026): Offering 52.5%, Crimson Mantle 52.3%, Impervious 51.6%, Fiend Fire 50.5%.

Names in sources that are not Ironclad cards in the extracted game data (ignored): Not Yet.
