# Draft Backtest (Ironclad)

`tools/draft.py` replayed on 640 of the Player's card reward screens (v0.107.1, solo, finished runs). Built by `tools/backtest_draft.py`. Caveats: v0.111.1 card values and the current tier file applied to v0.107.1 screens; the decision-point signal is switched off (it was fitted on these screens). `[PLAYER-DATA, observational]`

**Agreement:** 43% of screens (203 same card, 75 both skip).

| Case | Screens | Survived the act |
|---|---|---|
| same card | 203 | 71% (144/203) |
| different cards | 174 | 60% (105/174) |
| tool skips, Player picks | 122 | 60% (73/122) |
| both skip | 75 | 69% (52/75) |
| Player skips, tool picks | 66 | 71% (47/66) |

**Act survival when the Player matched the tool:** 71% (196/278); when not: 62% (225/362); Fisher p = 0.03.

Reading: a higher survival rate when the Player happened to choose what the tool recommends is weak support for the tool (confounded: easy screens may produce both agreement and survival). The disagreement table shows where the tool and the Player differ most.

## Sample disagreements (both picked a card)

| Seed | Floor | Player picked | Tool picks | Tool's main reasons |
|---|---|---|---|---|
| 9WHJYMRG9F | 2 | Breakthrough | Anger | tier D; Vantom: cheap or multi-hit attacks clear Slippery (+1) |
| 9WHJYMRG9F | 3 | Dismantle | Iron Wave | tier D; Vantom: cheap or multi-hit attacks clear Slippery (+1) |
| 9WHJYMRG9F | 4 | Armaments | Shrug It Off | tier B (sources disagree); block 7.7 below the act 1 target 10 (+0.5) |
| 9WHJYMRG9F | 6 | True Grit | Battle Trance | tier A; block 8.6 below the act 1 target 10 (+0.5) |
| Y7M0Z35FZZ | 3 | Fight Me | Flame Barrier | tier B |
| Y7M0Z35FZZ | 9 | Breakthrough | Shrug It Off | tier B (sources disagree); block 8.4 below the act 1 target 10 (+0.5) |
| Y7M0Z35FZZ | 14 | Primal Force | Pommel Strike | tier B (sources disagree); raw damage already enough; block is the gap (-0.5) |
| Y7M0Z35FZZ | 31 | Tremble | Forgotten Ritual | tier B; v0.111.1: no exhaust needed (+0.5) |
| ZDS61QSYXM | 3 | Breakthrough | Spite | tier D; Vantom: cheap or multi-hit attacks clear Slippery (+1) |
| ZDS61QSYXM | 13 | Sword Boomerang | Body Slam | tier C; Vantom: cheap or multi-hit attacks clear Slippery (+1) |
| ZDS61QSYXM | 17 | One Two Punch | Cascade | tier S |
| ZDS61QSYXM | 19 | Burning Pact | Stone Armor | tier C; Knowledge Demon: needs scaling and energy (H7) (+0.5) |
| ZDS61QSYXM | 22 | Uppercut | Feel No Pain | tier B; Knowledge Demon: needs scaling and energy (H7) (+0.5) |
| ZDS61QSYXM | 30 | Evil Eye | Dominate | tier A; Knowledge Demon: needs scaling and energy (H7) (+0.5) |
| 94EVN1PK7X | 3 | Armaments | Pommel Strike | tier B (sources disagree) |
