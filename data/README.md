# Run History Dataset

Built by `tools/extract_runs.py` from the game's run history files (`.run`, RunHistory schema v11). Rebuild at any time:

```
python3 -I tools/extract_runs.py      # read saves, write data/raw, data/runs.db, data/tables/*.csv
python3 -I tools/validate_data.py     # sanity checks; exit code 1 on failure
```

The extractor only reads the save folder. `data/raw/` holds one copy of each unique run, named `<start_time>-<seed>.run`.

## Snapshot (2026-11-18)

- 689 files scanned across `profile1`, `modded/profile1` and `back_prof1`. 233 unique runs after deduplicating on `(seed, start_time)`.
- Since 2026-11-20 `tools/extract_runs.py` skips `modded/profile2`, the Agent's practice profile, so the dataset stays the Player's history (`--include-agent` reads it too). The Agent's runs are in `runs/` and `metrics/scoreboard.csv`. Rebuilt 2026-11-20: 690 files, 234 unique runs.
- 227 runs on v0.107.1 (main branch) and 6 on v0.113.1 (beta). 232 solo runs and 1 co-op run.
- Deck reconstruction matches the recorded final deck in 232/232 solo runs by card, and 230/232 including upgrade levels. The two misses are Silent runs where an upgrade was not logged.

## Conventions

- `run_id` = `<start_time>-<seed>`.
- `floor` is 1-based and counts every map point in the run, including the Ancient on floor 1. It matches the game's `floor_added_to_deck`.
- `act` is 1-based. `act_floor` is the 1-based position within the act.
- IDs keep the game's prefixes (`CARD.`, `RELIC.`, `POTION.`, `ENCOUNTER.`, `EVENT.`).
- Upgrade level: 0 means not upgraded.
- **Co-op runs** (`n_players > 1`) appear only in `runs`, `final_deck` and `final_relics`. Per-player floor data is not extracted, because which player is the local one is ambiguous.

## Tables

### runs
| Column | Meaning |
|---|---|
| run_id, seed, start_time | Identity. `start_time` is a Unix timestamp. |
| build_id | Game version, for example `v0.107.1` |
| character | `IRONCLAD`, `SILENT`, `NECROBINDER`, `REGENT`, `DEFECT`, `FOOL` |
| ascension | 0–10 |
| win, abandoned | 0/1 |
| killed_by_encounter, killed_by_event | NULL when not applicable (the game's `NONE.NONE`) |
| floors_reached | Number of map points visited |
| acts | JSON list of act IDs, for example `["ACT.UNDERDOCKS","ACT.HIVE","ACT.GLORY"]` |
| run_time | Seconds |
| n_players, game_mode, is_custom | |
| source_folders | Which save folders held this run: `main`, `modded`, `backup` |
| has_ascenders_bane | 1 if the run started with Ascender's Bane. This happens from A5 upwards: 100% of A5+ runs, 0% below. |
| deck_match_ids, deck_match_levels | Whether the reconstructed final deck matches the recorded one |
| deck_diff | JSON of any differences (NULL when they match) |

### floors (one row per map point, solo runs)
| Column | Meaning |
|---|---|
| map_point_type | `ancient`, `monster`, `elite`, `boss`, `unknown` (a ? room), `shop`, `rest_site`, `treasure` |
| room_type | Type of the primary room. For a ? room that turned into a fight, this is `monster`. |
| room_types | All rooms at this map point, comma-separated. 27 floors have two (`event,monster`). |
| model_id | Encounter or event ID of the primary room (the fight room if there is one) |
| monster_ids | JSON list of monster IDs (fights only) |
| turns_taken | Combat turns (fights only) |
| hp_before | The previous floor's `hp_after`. Floor 1 uses max HP. |
| hp_after, max_hp, damage_taken, hp_healed, max_hp_gained, max_hp_lost | From the game. `damage_taken` is per map point: on a two-room floor it includes both rooms. |
| gold_before, gold_after, gold_gained, gold_spent, gold_lost, gold_stolen | Gold. Floor 1's `gold_before` is derived. |
| deck_size_before | Deck size at the start of the floor, from the reconstruction |
| is_last_floor | 1 for the run's final map point |

`hp_after = hp_before - damage_taken + hp_healed` holds on 99.5% of floors without a max HP change.

### card_offers
One row per card shown.

| Column | Meaning |
|---|---|
| source | `reward` (after a fight, including fights in ? rooms), `shop`, `event`, `ancient`. For `shop`: the game's list usually holds only the stock left **unsold**, so the extractor adds each card gained at the shop as a picked row. A shop row with picked = 1 means bought; the rows still do not capture the full original stock. |
| offer_group | One per choice. Reward screens with 6 or 9 cards are split into groups of 3; 8 cards into groups of 4. Other sizes are one group. |
| position | Index in the game's list |
| upgrade_level | Level of the offered card. Upgraded offers are common in rewards. |
| picked | 0/1. A reward group with no pick is a skip. |
| deck_size_before | Deck size when offered |

### deck_changes
| change | Meaning |
|---|---|
| gained | Card added (rewards, shops, events, Ancients, curses) |
| removed | Card removed (shop removal, events) |
| transformed_from / transformed_to | Transform pairs. `detail` holds the other side. |
| upgraded / downgraded | `upgrade_level` is NULL; the card ID is in `card_id` |
| enchanted | `detail` holds the enchantment ID |

Within a floor, changes replay in this order: gains, transforms, upgrades, downgrades, removals.

### deck_snapshots
The deck **after** each floor's changes: `(run_id, floor, card_id, upgrade_level, count)`. For the deck at the start of floor *f*, use floor *f − 1*. Floor 0 is the starting deck, which is not stored. It is the character's starter deck, plus Ascender's Bane at A5 and above.

### relic_events
`kind`:
- `offered`: a choice was shown (treasure, elite, boss, event or shop stock); `picked` 0/1
- `bought`
- `removed`

`source` is the map point type.

### potion_events
`kind`:
- `offered`: with `picked`
- `used` and `discarded`: `source` is the room type, for example `elite`
- `bought`

### rest_choices
`choice`: `SMITH`, `HEAL`, `DIG`, `COOK`, `KINDLE`, `HATCH`, `LIFT`, `CLONE`. `hp_before` and `max_hp` are taken at arrival. `next_is_boss` is 1 when the next map point is the boss. `upgraded` lists the cards upgraded on that floor.

### shop_visits
Gold on arrival, gold spent, the counts of cards, colorless cards, relics and potions bought, the number of removals and the removed card IDs.

### event_choices
`event_id` is the `EVENT.` room ID. `choice_key` is the localisation key of the chosen option, for example `THIS_OR_THAT.pages.INITIAL.options.ORNATE.title`. `hp_change`, `gold_change` and `max_hp_change` are the net change over the floor.

### ancient_choices
`ancient_id` is the Ancient's event ID. `option` is its TextKey (usually a relic ID without prefix). `chosen` is 0/1.

### final_deck, final_relics
The recorded end-of-run deck (with upgrade level, enchantment and floor added) and relics.

## Known caveats

1. On a floor with two rooms (event then fight), `damage_taken` covers both rooms.
2. Shop `card_choices` in the raw files list unsold stock; purchases come from `cards_gained` (see `card_offers`). `shop_visits.cards_bought` counts the class cards gained at the shop (gained minus colorless purchases).
3. `choice_key` for events is a localisation key, not a stable option ID across game versions.
4. Two Silent runs have one unlogged upgrade each. See `runs.deck_diff`.
