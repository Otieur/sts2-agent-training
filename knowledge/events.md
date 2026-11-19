# Events

Options, effects, costs and risk tags from the extracted game data `[GAME-EXTRACT]` (base values; `?` = computed in game). The Player's choices are from solo runs on v0.107.1 `[PLAYER-DATA]`, with the mean net HP, gold and max-HP change over the event floor. The Player's choices are a baseline, not advice.

Risk tags: `lethal-possible` (an option can kill at low HP), `costly`, `none-detected` (no cost found; not a guarantee).

## This Or That (`THIS_OR_THAT`)

Player visits: 50 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| PLAIN | Gain 0 Gold | Lose 6 HP; event is marked lethal at 6 current HP | lethal-possible | 9 | -6.0 | 53 |
| ORNATE | Obtain a random relic; Obtain a relic | Add the curse Clumsy to your deck | harmful | 41 | 0.6 | 0 |

## Self Help Book (`SELF_HELP_BOOK`)

Player visits: 40 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| READ_THE_BACK | none detected | none detected | none-detected | 24 | 0.2 | 0 |
| READ_THE_BACK_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| READ_PASSAGE | none detected | none detected | none-detected | 9 | 0.0 | 0 |
| READ_PASSAGE_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| READ_ENTIRE_BOOK | none detected | none detected | none-detected | 7 | 0.0 | 0 |
| READ_ENTIRE_BOOK_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| NO_OPTIONS | none detected | none detected | none-detected | 0 | - | - |

## Slippery Bridge (`SLIPPERY_BRIDGE`)

Player visits: 38 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| OVERCOME | none detected | Remove a card from your deck | costly | 38 | -3.6 | 0 |
| HOLD_ON_0 | none detected | Lose ? HP; event is marked lethal at ? current HP | lethal-possible | 28 | -4.9 | 0 |
| unknown | none detected | Lose ? HP; event is marked lethal at ? current HP | lethal-possible | 0 | - | - |
| HOLD_ON_1 | (not in the extract) | - | - | 11 | -8.4 | 0 |
| HOLD_ON_2 | (not in the extract) | - | - | 3 | -12.0 | 0 |

## The Legends Were True (`THE_LEGENDS_WERE_TRUE`)

Player visits: 38 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| NAB_THE_MAP | Put a card into your deck | none detected | none-detected | 38 | 0.0 | 0 |
| SLOWLY_FIND_AN_EXIT | Offer extra rewards | Lose 8 HP; event is marked lethal at 8 current HP | lethal-possible | 0 | - | - |

## Brain Leech (`BRAIN_LEECH`)

Player visits: 34 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| SHARE_KNOWLEDGE | Offer a card reward; Choose a card from an offered set; Put a card in… | none detected | none-detected | 21 | 0.2 | 1 |
| RIP | Offer extra rewards | Lose ? HP; event is marked lethal at 5 current HP | lethal-possible | 13 | -5.0 | 0 |

## Room Full Of Cheese (`ROOM_FULL_OF_CHEESE`)

Player visits: 34 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| GORGE | Offer a card reward; Choose a card from an offered set; Put a card in… | none detected | none-detected | 29 | 0.0 | 1 |
| SEARCH | Obtain the relic Chosen Cheese | Lose 14 HP; event is marked lethal at 14 current HP | lethal-possible | 5 | -12.8 | 0 |

## Symbiote (`SYMBIOTE`)

Player visits: 30 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| APPROACH_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| APPROACH | Enchant a card in your deck; Enchant a card with Corrupted | none detected | none-detected | 9 | 0.0 | 0 |
| KILL_WITH_FIRE | Transform a card in your deck; Transform a card into a random card | none detected | none-detected | 21 | 0.2 | 1 |

## Sunken Statue (`SUNKEN_STATUE`)

Player visits: 29 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| GRAB_SWORD | Obtain the relic Sword Of Stone | none detected | none-detected | 18 | 0.0 | 0 |
| DIVE_INTO_WATER | Gain 111 Gold | Lose 7 HP; event is marked lethal at 7 current HP | lethal-possible | 11 | -7.0 | 110 |

## Potion Courier (`POTION_COURIER`)

Player visits: 26 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| GRAB_POTIONS | Offer extra rewards | none detected | none-detected | 8 | 0.0 | 0 |
| RANSACK | Offer extra rewards | none detected | none-detected | 18 | 0.6 | 0 |

## Sunken Treasury (`SUNKEN_TREASURY`)

Player visits: 23 · highest risk: harmful · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| FIRST_CHEST | Gain 60 Gold | none detected | none-detected | 0 | - | - |
| SECOND_CHEST | Gain 333 Gold | Add the curse Greed to your deck | harmful | 23 | 0.0 | 337 |

## Byrdonis Nest (`BYRDONIS_NEST`)

Player visits: 20 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| EAT | Gain 7 Max HP | none detected | none-detected | 12 | 7.0 | 0 |
| TAKE | Put a card into your deck | none detected | none-detected | 8 | 0.0 | 2 |

## The Future Of Potions (`THE_FUTURE_OF_POTIONS`)

Player visits: 20 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| unknown | none detected | none detected | none-detected | 0 | - | - |
| POTION | (not in the extract) | - | - | 20 | 0.0 | 1 |

## Abyssal Baths (`ABYSSAL_BATHS`)

Player visits: 19 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| IMMERSE | Gain 2 Max HP | Lose 3 HP; event is marked lethal at ? current HP | lethal-possible | 7 | -6.9 | 0 |
| ABSTAIN | Heal 10 HP | none detected | none-detected | 12 | 9.6 | 0 |
| LINGER | Gain 2 Max HP | Lose 3 HP; event is marked lethal at ? current HP | lethal-possible | 14 | -10.7 | 0 |
| EXIT_BATHS | none detected | none detected | none-detected | 7 | -6.9 | 0 |

## Aroma Of Chaos (`AROMA_OF_CHAOS`)

Player visits: 18 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| LET_GO | Transform a card in your deck; Transform a card into a random card | none detected | none-detected | 4 | 0.0 | 0 |
| MAINTAIN_CONTROL | Upgrade a card in your deck; Upgrade a card | none detected | none-detected | 14 | 0.0 | 0 |

## Battleworn Dummy (`BATTLEWORN_DUMMY`)

Player visits: 17 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| SETTING_1 | none detected | none detected | none-detected | 6 | 0.8 | 0 |
| SETTING_2 | none detected | none detected | none-detected | 8 | 2.9 | -2 |
| SETTING_3 | none detected | none detected | none-detected | 3 | 1.7 | 0 |

## Bugslayer (`BUGSLAYER`)

Player visits: 17 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| EXTERMINATION | none detected | none detected | none-detected | 8 | 0.0 | 0 |
| SQUASH | none detected | none detected | none-detected | 9 | 0.0 | 0 |

## Spiraling Whirlpool (`SPIRALING_WHIRLPOOL`)

Player visits: 17 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| OBSERVE | Enchant a card in your deck; Enchant a card with Spiral | none detected | none-detected | 12 | 0.4 | 0 |
| DRINK | Heal 0 HP | none detected | none-detected | 5 | 22.4 | 0 |

## Drowning Beacon (`DROWNING_BEACON`)

Player visits: 16 · highest risk: harmful · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| BOTTLE | Offer extra rewards | none detected | none-detected | 3 | 0.0 | 0 |
| CLIMB | Obtain the relic Fresnel Lens | Lose 13 Max HP | harmful | 13 | 0.0 | 0 |

## Infested Automaton (`INFESTED_AUTOMATON`)

Player visits: 16 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| STUDY | Offer a card reward; Put a card into your deck | none detected | none-detected | 10 | 0.0 | 0 |
| TOUCH_CORE | Offer a card reward; Put a card into your deck | none detected | none-detected | 6 | 0.0 | 2 |

## Ranwid The Elder (`RANWID_THE_ELDER`)

Player visits: 16 · highest risk: costly · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| unknown | none detected | none detected | none-detected | 0 | - | - |
| POTION_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| GOLD | Obtain a random relic; Obtain a relic | Lose 100 Gold | costly | 7 | 0.7 | -57 |
| RELIC_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| RELIC | (not in the extract) | - | - | 5 | 0.0 | 0 |
| POTION | (not in the extract) | - | - | 4 | 1.2 | 0 |

## Relic Trader (`RELIC_TRADER`)

Player visits: 16 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| TOP | none detected | none detected | none-detected | 6 | 0.0 | 0 |
| MIDDLE | none detected | none detected | none-detected | 7 | 0.7 | 0 |
| BOTTOM | none detected | none detected | none-detected | 3 | 0.0 | 0 |
| PROCEED | none detected | none detected | none-detected | 0 | - | - |

## Sapphire Seed (`SAPPHIRE_SEED`)

Player visits: 16 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| EAT | Heal 9 HP; Upgrade a card in your deck; Upgrade a card | none detected | none-detected | 16 | 8.6 | 0 |
| PLANT | Enchant a card in your deck; Enchant a card with Sown | none detected | none-detected | 0 | - | - |

## Doll Room (`DOLL_ROOM`)

Player visits: 15 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| RANDOM | none detected | none detected | none-detected | 12 | 0.0 | 0 |
| TAKE_SOME_TIME | none detected | Lose ? HP; event is marked lethal at 5 current HP | lethal-possible | 3 | -3.3 | 0 |
| EXAMINE | none detected | Lose ? HP; event is marked lethal at 15 current HP | lethal-possible | 0 | - | - |
| unknown | none detected | none detected | none-detected | 0 | - | - |
| DAUGHTER_OF_THE_WIND | (not in the extract) | - | - | 3 | -3.3 | 0 |

## Spirit Grafter (`SPIRIT_GRAFTER`)

Player visits: 15 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| LET_IT_IN | Heal 25 HP; Put a card into your deck | none detected | none-detected | 15 | 19.1 | 0 |
| REJECTION | none detected | Remove a card from your deck; Lose 9 HP; event is marked le… | lethal-possible | 0 | - | - |

## Wellspring (`WELLSPRING`)

Player visits: 15 · highest risk: costly · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| BOTTLE | Offer extra rewards | none detected | none-detected | 4 | 0.0 | 0 |
| BATHE | none detected | Remove a card from your deck | costly | 11 | 0.0 | 0 |

## Doors Of Light And Dark (`DOORS_OF_LIGHT_AND_DARK`)

Player visits: 14 · highest risk: costly · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| LIGHT | Upgrade a card | none detected | none-detected | 11 | 0.0 | 0 |
| DARK | none detected | Remove a card from your deck | costly | 3 | 0.0 | 0 |

## Field Of Man Sized Holes (`FIELD_OF_MAN_SIZED_HOLES`)

Player visits: 14 · highest risk: harmful · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| RESIST | none detected | Remove a card from your deck; Add curses to your deck | harmful | 2 | 0.0 | 0 |
| ENTER_YOUR_HOLE | Enchant a card in your deck; Enchant a card with Perfect Fit | none detected | none-detected | 12 | 0.0 | 0 |

## Crystal Sphere (`CRYSTAL_SPHERE`)

Player visits: 13 · highest risk: harmful · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| UNCOVER_FUTURE | none detected | Lose 50 Gold | costly | 4 | 0.0 | -57 |
| PAYMENT_PLAN | none detected | Add the curse Debt to your deck | harmful | 9 | 1.2 | 50 |

## Wood Carvings (`WOOD_CARVINGS`)

Player visits: 13 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| SNAKE_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| SNAKE | Enchant a card in your deck; Enchant a card with Slither | none detected | none-detected | 6 | 0.0 | 0 |
| BIRD | Choose a card in your deck; Transform a card into Peck | none detected | none-detected | 7 | 0.0 | 0 |
| TORUS | Choose a card in your deck; Transform a card into Toric Toughness | none detected | none-detected | 0 | - | - |

## Endless Conveyor (`ENDLESS_CONVEYOR`)

Player visits: 12 · highest risk: costly · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| OBSERVE_CHEF | Upgrade a card | none detected | none-detected | 5 | 0.0 | 0 |
| LEAVE | none detected | none detected | none-detected | 7 | 14.3 | -213 |
| unknown | none detected | Lose 35 Gold | costly | 0 | - | - |
| LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| CAVIAR | (not in the extract) | - | - | 10 | 15.4 | -230 |
| SUSPICIOUS_CONDIMENT | (not in the extract) | - | - | 4 | 13.5 | -261 |
| JELLY_LIVER | (not in the extract) | - | - | 3 | 18.0 | -268 |
| SEAPUNK_SALAD | (not in the extract) | - | - | 6 | 17.7 | -276 |
| SPICY_SNAPPY | (not in the extract) | - | - | 6 | 21.0 | -303 |
| CLAM_ROLL | (not in the extract) | - | - | 6 | 22.7 | -263 |
| GOLDEN_FYSH | (not in the extract) | - | - | 2 | 26.0 | -305 |
| FRIED_EEL | (not in the extract) | - | - | 6 | 15.3 | -262 |

## Hungry For Mushrooms (`HUNGRY_FOR_MUSHROOMS`)

Player visits: 12 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| BIG_MUSHROOM | Obtain the relic Big Mushroom; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| FRAGRANT_MUSHROOM | Obtain the relic Fragrant Mushroom; the source finishes the event aft… | none detected | none-detected | 12 | -14.4 | 0 |

## Lost Wisp (`LOST_WISP`)

Player visits: 12 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| CLAIM | none detected | none detected | none-detected | 5 | 4.0 | 0 |
| SEARCH | Gain 60 Gold | none detected | none-detected | 7 | 0.0 | 58 |

## Morphic Grove (`MORPHIC_GROVE`)

Player visits: 12 · highest risk: costly · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| GROUP | Transform a card in your deck; Transform a card into a random card | Lose 100 Gold | costly | 3 | 0.0 | -130 |
| LONER | Gain 5 Max HP | none detected | none-detected | 9 | 5.0 | 0 |

## Jungle Maze Adventure (`JUNGLE_MAZE_ADVENTURE`)

Player visits: 11 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| SOLO_QUEST | Gain 150 Gold | Lose 18 HP; event is marked lethal at 18 current HP | lethal-possible | 5 | -18.0 | 154 |
| JOIN_FORCES | Gain 50 Gold | none detected | none-detected | 6 | 0.0 | 41 |

## Tinker Time (`TINKER_TIME`)

Player visits: 11 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| CHOOSE_CARD_TYPE | none detected | none detected | none-detected | 11 | 0.0 | 0 |
| ATTACK | none detected | none detected | none-detected | 0 | - | - |
| SKILL | none detected | none detected | none-detected | 7 | 0.0 | 0 |
| POWER | none detected | none detected | none-detected | 4 | 0.0 | 0 |
| unknown | Put a card into your deck | none detected | none-detected | 0 | - | - |
| CURIOUS | (not in the extract) | - | - | 3 | 0.0 | 0 |
| ENERGIZED | (not in the extract) | - | - | 5 | 0.0 | 0 |
| WISDOM | (not in the extract) | - | - | 1 | 0.0 | 0 |
| IMPROVEMENT | (not in the extract) | - | - | 1 | 0.0 | 0 |
| CHAOS | (not in the extract) | - | - | 1 | 0.0 | 0 |

## Whispering Hollow (`WHISPERING_HOLLOW`)

Player visits: 11 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| GOLD | Offer extra rewards | Lose 50 Gold | costly | 5 | 0.0 | -35 |
| HUG | Transform a card in your deck; Transform a card into a random card | Lose 9 HP; event is marked lethal at 9 current HP | lethal-possible | 6 | -9.0 | 0 |

## Amalgamator (`AMALGAMATOR`)

Player visits: 10 · highest risk: costly · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| COMBINE_STRIKES | Put a card into your deck | Remove a card from your deck | costly | 6 | 0.8 | 0 |
| COMBINE_DEFENDS | Put a card into your deck | Remove a card from your deck | costly | 4 | 0.0 | 0 |

## Dense Vegetation (`DENSE_VEGETATION`)

Player visits: 10 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| TRUDGE_ON | none detected | Remove a card from your deck; Lose 11 HP; event is marked l… | lethal-possible | 7 | -7.9 | 83 |
| REST | Heal as if you had rested | none detected | none-detected | 3 | 15.0 | 9 |
| FIGHT | none detected | none detected | none-detected | 3 | 15.0 | 9 |

## Reflections (`REFLECTIONS`)

Player visits: 10 · highest risk: harmful · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| TOUCH_A_MIRROR | Upgrade a card | Downgrade a card | costly | 7 | 0.0 | 0 |
| SHATTER | Put a card into your deck | Add the curse Bad Luck to your deck | harmful | 3 | 14.7 | 0 |

## Stone Of All Time (`STONE_OF_ALL_TIME`)

Player visits: 10 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| LIFT | Gain 10 Max HP | Discard a potion | harmful | 3 | 10.0 | 0 |
| LIFT_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| PUSH_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| PUSH | Enchant a card in your deck; Enchant a card | Lose 6 HP; event is marked lethal at 6 current HP | lethal-possible | 7 | -6.0 | 0 |

## Trial (`TRIAL`)

Player visits: 10 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| ACCEPT | none detected | none detected | none-detected | 8 | 3.1 | 38 |
| REJECT | none detected | none detected | none-detected | 2 | 8.0 | 150 |
| GUILTY | Obtain a relic | Add the curse Regret to your deck | harmful | 1 | 0.0 | 0 |
| INNOCENT | Upgrade a card in your deck; Upgrade a card | Add the curse Shame to your deck | harmful | 3 | 0.0 | 0 |
| GUILTY | Heal 10 HP | none detected | none-detected | 2 | 12.5 | 0 |
| INNOCENT | Gain 300 Gold | Add the curse Regret to your deck | harmful | 2 | 8.0 | 300 |
| GUILTY | Offer extra rewards | Add the curse Doubt to your deck | harmful | 0 | - | - |
| INNOCENT | Transform a card in your deck; Transform a card into a random card | Add the curse Doubt to your deck | harmful | 2 | 0.0 | 0 |
| ACCEPT | none detected | none detected | none-detected | 2 | 8.0 | 150 |
| DOUBLE_DOWN | none detected | event is marked lethal at 9999 current HP | lethal-possible | 0 | - | - |

## Round Tea Party (`ROUND_TEA_PARTY`)

Player visits: 9 · highest risk: harmful · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| ENJOY_TEA | Obtain the relic Royal Poison; Heal ? HP | none detected | none-detected | 0 | - | - |
| PICK_FIGHT | none detected | none detected | none-detected | 9 | -10.4 | 0 |
| CONTINUE_FIGHT | Obtain a relic | Lose 11 HP | harmful | 0 | - | - |

## Waterlogged Scriptorium (`WATERLOGGED_SCRIPTORIUM`)

Player visits: 9 · highest risk: costly · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| BLOODY_INK | Gain 6 Max HP | none detected | none-detected | 5 | 6.0 | 0 |
| TENTACLE_QUILL | Enchant a card in your deck; Enchant a card with Steady | Lose 65 Gold | costly | 0 | - | - |
| TENTACLE_QUILL_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| PRICKLY_SPONGE | Enchant a card in your deck; Enchant a card with Steady | Lose 155 Gold | costly | 4 | 0.0 | -99 |
| PRICKLY_SPONGE_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |

## Colossal Flower (`COLOSSAL_FLOWER`)

Player visits: 8 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| EXTRACT_CURRENT_PRIZE_* | Gain ? Gold | none detected | none-detected | 0 | - | - |
| REACH_DEEPER_* | none detected | Lose ? HP; event is marked lethal at ? current HP | lethal-possible | 0 | - | - |
| EXTRACT_CURRENT_PRIZE_* | Gain ? Gold | none detected | none-detected | 0 | - | - |
| REACH_DEEPER_* | none detected | Lose ? HP; event is marked lethal at ? current HP | lethal-possible | 0 | - | - |
| EXTRACT_INSTEAD | Gain ? Gold | none detected | none-detected | 0 | - | - |
| POLLINOUS_CORE | Obtain the relic Pollinous Core | Lose ? HP; event is marked lethal at ? current HP | lethal-possible | 0 | - | - |
| EXTRACT_CURRENT_PRIZE_1 | (not in the extract) | - | - | 7 | 0.7 | 35 |
| REACH_DEEPER_1 | (not in the extract) | - | - | 1 | -5.0 | 75 |
| EXTRACT_CURRENT_PRIZE_2 | (not in the extract) | - | - | 1 | -5.0 | 75 |

## Tablet Of Truth (`TABLET_OF_TRUTH`)

Player visits: 8 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| DECIPHER_1 | none detected | none detected | lethal-possible | 1 | 0.0 | 0 |
| SMASH | Heal 20 HP | none detected | none-detected | 7 | 16.6 | 0 |
| DECIPHER | none detected | none detected | lethal-possible | 0 | - | - |
| GIVE_UP | none detected | none detected | none-detected | 1 | 0.0 | 0 |
| DECIPHER | (not in the extract) | - | - | 1 | 0.0 | 0 |

## Trash Heap (`TRASH_HEAP`)

Player visits: 8 · highest risk: lethal-possible · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| DIVE_IN | Obtain a relic | Lose 8 HP; event is marked lethal at 8 current HP | lethal-possible | 3 | -8.0 | 0 |
| GRAB | Gain 100 Gold; Put a card into your deck | none detected | none-detected | 5 | 0.0 | 100 |

## Zen Weaver (`ZEN_WEAVER`)

Player visits: 8 · highest risk: costly · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| BREATHING_TECHNIQUES | Put a card into your deck | Lose 50 Gold | costly | 4 | 0.0 | -50 |
| EMOTIONAL_AWARENESS | none detected | none detected | none-detected | 4 | 0.0 | -125 |
| ARACHNID_ACUPUNCTURE | none detected | none detected | none-detected | 0 | - | - |
| LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |

## Colorful Philosophers (`COLORFUL_PHILOSOPHERS`)

Player visits: 7 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| unknown | Offer extra rewards | none detected | none-detected | 0 | - | - |
| DEFECT | (not in the extract) | - | - | 4 | 0.0 | 0 |
| SILENT | (not in the extract) | - | - | 1 | 14.0 | 0 |
| REGENT | (not in the extract) | - | - | 1 | 0.0 | 0 |
| IRONCLAD | (not in the extract) | - | - | 1 | 0.0 | 0 |

## Grave Of The Forgotten (`GRAVE_OF_THE_FORGOTTEN`)

Player visits: 7 · highest risk: harmful · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| CONFRONT_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| CONFRONT | Enchant a card in your deck; Enchant a card with Souls Power | Add the curse Decay to your deck | harmful | 3 | 0.0 | 0 |
| ACCEPT | Obtain the relic Forgotten Soul | none detected | none-detected | 4 | 0.0 | 0 |

## The Lantern Key (`THE_LANTERN_KEY`)

Player visits: 7 · highest risk: none-detected · combat event: MysteriousKnightEventEncounter

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| RETURN_THE_KEY | Gain 100 Gold | none detected | none-detected | 3 | 0.0 | 100 |
| KEEP_THE_KEY | none detected | none detected | none-detected | 4 | -12.5 | 15 |
| FIGHT | none detected | none detected | none-detected | 4 | -12.5 | 15 |

## Tea Master (`TEA_MASTER`)

Player visits: 6 · highest risk: costly · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| BONE_TEA | Obtain the relic Bone Tea | Lose 50 Gold | costly | 1 | 0.0 | -50 |
| BONE_TEA_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| EMBER_TEA | Obtain the relic Ember Tea | Lose 150 Gold | costly | 4 | 0.0 | -150 |
| EMBER_TEA_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| TEA_OF_DISCOURTESY | Obtain the relic Tea Of Discourtesy | none detected | none-detected | 1 | 0.0 | 0 |

## Welcome To Wongos (`WELCOME_TO_WONGOS`)

Player visits: 6 · highest risk: costly · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| BARGAIN_BIN | Obtain a random relic; Obtain a relic | Lose 100 Gold | costly | 2 | 0.0 | -100 |
| BARGAIN_BIN_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| FEATURED_ITEM | Obtain a relic | Lose 200 Gold | costly | 1 | 0.0 | -188 |
| FEATURED_ITEM_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| MYSTERY_BOX | Obtain the relic Wongos Mystery Ticket | Lose 300 Gold | costly | 2 | 0.0 | -300 |
| MYSTERY_BOX_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| LEAVE | none detected | Downgrade a card | costly | 1 | 0.0 | 0 |

## Luminous Choir (`LUMINOUS_CHOIR`)

Player visits: 5 · highest risk: harmful · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| REACH_INTO_THE_FLESH | none detected | Remove a card from your deck; Add the curse Spore Mind to y… | harmful | 3 | 0.0 | 0 |
| OFFER_TRIBUTE | Obtain a random relic; Obtain a relic | Lose 149 Gold | costly | 2 | 0.0 | -137 |
| OFFER_TRIBUTE_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |

## Punch Off (`PUNCH_OFF`)

Player visits: 5 · highest risk: harmful · combat event: PunchOffEventEncounter

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| NAB | Offer extra rewards | Add the curse Injury to your deck | harmful | 3 | 1.7 | 0 |
| I_CAN_TAKE_THEM | none detected | none detected | none-detected | 2 | -32.0 | 13 |
| FIGHT | none detected | none detected | none-detected | 2 | -32.0 | 13 |

## Unrest Site (`UNREST_SITE`)

Player visits: 3 · highest risk: harmful · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| REST | Heal 0 HP | Add curses to your deck | harmful | 0 | - | - |
| KILL | Obtain a random relic; Obtain a relic | Lose 8 Max HP | harmful | 3 | 0.0 | 0 |

## War Historian Repy (`WAR_HISTORIAN_REPY`)

Player visits: 2 · highest risk: costly · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| UNLOCK_CAGE | Obtain the relic History Course; complete Quest | Remove a card from your deck | costly | 1 | 0.0 | 0 |
| UNLOCK_CHEST | Offer extra rewards; complete Quest | Remove a card from your deck | costly | 1 | 0.0 | 0 |

## Darv (`DARV`)

Player visits: 0 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| DUSTY_TOME | Obtain the relic Dusty Tome; the source finishes the event after it | none detected | none-detected | 0 | - | - |

## Deprecated Ancient Event (`DEPRECATED_ANCIENT_EVENT`)

Player visits: 0 · highest risk: unknown · no combat

No option data.

## Deprecated Event (`DEPRECATED_EVENT`)

Player visits: 0 · highest risk: unknown · no combat

No option data.

## Fake Merchant (`FAKE_MERCHANT`)

Player visits: 0 · highest risk: unknown · no combat

No option data.

## Neow (`NEOW`)

Player visits: 0 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| unknown | none detected | none detected | none-detected | 0 | - | - |
| ARCANE_SCROLL | Obtain the relic Arcane Scroll; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| BOOMING_CONCH | Obtain the relic Booming Conch; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| POMANDER | Obtain the relic Pomander; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| GOLDEN_PEARL | Obtain the relic Golden Pearl; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| LEAD_PAPERWEIGHT | Obtain the relic Lead Paperweight; the source finishes the event afte… | none detected | none-detected | 0 | - | - |
| NEW_LEAF | Obtain the relic New Leaf; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| NEOWS_TORMENT | Obtain the relic Neows Torment; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| PRECISE_SCISSORS | Obtain the relic Precise Scissors; the source finishes the event afte… | none detected | none-detected | 0 | - | - |
| LOST_COFFER | Obtain the relic Lost Coffer; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| NUTRITIOUS_OYSTER | Obtain the relic Nutritious Oyster; the source finishes the event aft… | none detected | none-detected | 0 | - | - |
| STONE_HUMIDIFIER | Obtain the relic Stone Humidifier; the source finishes the event afte… | none detected | none-detected | 0 | - | - |
| MASSIVE_SCROLL | Obtain the relic Massive Scroll; the source finishes the event after … | none detected | none-detected | 0 | - | - |
| LAVA_ROCK | Obtain the relic Lava Rock; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| SMALL_CAPSULE | Obtain the relic Small Capsule; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| SILVER_CRUCIBLE | Obtain the relic Silver Crucible; the source finishes the event after… | none detected | none-detected | 0 | - | - |
| CURSED_PEARL | Obtain the relic Cursed Pearl; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| LARGE_CAPSULE | Obtain the relic Large Capsule; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| LEAFY_POULTICE | Obtain the relic Leafy Poultice; the source finishes the event after … | none detected | none-detected | 0 | - | - |
| PRECARIOUS_SHEARS | Obtain the relic Precarious Shears; the source finishes the event aft… | none detected | none-detected | 0 | - | - |
| SCROLL_BOXES | Obtain the relic Scroll Boxes; the source finishes the event after it | none detected | none-detected | 0 | - | - |

## Nonupeipe (`NONUPEIPE`)

Player visits: 0 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| BLESSED_ANTLER | Obtain the relic Blessed Antler; the source finishes the event after … | none detected | none-detected | 0 | - | - |
| BRILLIANT_SCARF | Obtain the relic Brilliant Scarf; the source finishes the event after… | none detected | none-detected | 0 | - | - |
| DELICATE_FROND | Obtain the relic Delicate Frond; the source finishes the event after … | none detected | none-detected | 0 | - | - |
| DIAMOND_DIADEM | Obtain the relic Diamond Diadem; the source finishes the event after … | none detected | none-detected | 0 | - | - |
| FUR_COAT | Obtain the relic Fur Coat; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| GLITTER | Obtain the relic Glitter; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| JEWELRY_BOX | Obtain the relic Jewelry Box; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| LOOMING_FRUIT | Obtain the relic Looming Fruit; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| SIGNET_RING | Obtain the relic Signet Ring; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| BEAUTIFUL_BRACELET | Obtain the relic Beautiful Bracelet; the source finishes the event af… | none detected | none-detected | 0 | - | - |

## Orobas (`OROBAS`)

Player visits: 0 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| OPTION_POOL_3_LOCKED | option is locked (no handler) | n/a | locked | 0 | - | - |
| ELECTRIC_SHRYMP | Obtain the relic Electric Shrymp; the source finishes the event after… | none detected | none-detected | 0 | - | - |
| GLASS_EYE | Obtain the relic Glass Eye; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| SAND_CASTLE | Obtain the relic Sand Castle; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| ALCHEMICAL_COFFER | Obtain the relic Alchemical Coffer; the source finishes the event aft… | none detected | none-detected | 0 | - | - |
| DRIFTWOOD | Obtain the relic Driftwood; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| RADIANT_PEARL | Obtain the relic Radiant Pearl; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| PRISMATIC_GEM | Obtain the relic Prismatic Gem; the source finishes the event after it | none detected | none-detected | 0 | - | - |

## Pael (`PAEL`)

Player visits: 0 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| PAELS_CLAW | Obtain the relic Paels Claw; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| PAELS_TOOTH | Obtain the relic Paels Tooth; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| PAELS_GROWTH | Obtain the relic Paels Growth; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| PAELS_LEGION | Obtain the relic Paels Legion; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| PAELS_FLESH | Obtain the relic Paels Flesh; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| PAELS_HORN | Obtain the relic Paels Horn; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| PAELS_TEARS | Obtain the relic Paels Tears; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| PAELS_WING | Obtain the relic Paels Wing; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| PAELS_EYE | Obtain the relic Paels Eye; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| PAELS_BLOOD | Obtain the relic Paels Blood; the source finishes the event after it | none detected | none-detected | 0 | - | - |

## Tanx (`TANX`)

Player visits: 0 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| CLAWS | Obtain the relic Claws; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| CROSSBOW | Obtain the relic Crossbow; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| IRON_CLUB | Obtain the relic Iron Club; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| MEAT_CLEAVER | Obtain the relic Meat Cleaver; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| SAI | Obtain the relic Sai; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| SPIKED_GAUNTLETS | Obtain the relic Spiked Gauntlets; the source finishes the event afte… | none detected | none-detected | 0 | - | - |
| TANXS_WHISTLE | Obtain the relic Tanxs Whistle; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| THROWING_AXE | Obtain the relic Throwing Axe; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| WAR_HAMMER | Obtain the relic War Hammer; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| TRI_BOOMERANG | Obtain the relic Tri Boomerang; the source finishes the event after it | none detected | none-detected | 0 | - | - |

## Tezcatara (`TEZCATARA`)

Player visits: 0 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| NUTRITIOUS_SOUP | Obtain the relic Nutritious Soup; the source finishes the event after… | none detected | none-detected | 0 | - | - |
| VERY_HOT_COCOA | Obtain the relic Very Hot Cocoa; the source finishes the event after … | none detected | none-detected | 0 | - | - |
| YUMMY_COOKIE | Obtain the relic Yummy Cookie; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| BIIIG_HUG | Obtain the relic Biiig Hug; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| STORYBOOK | Obtain the relic Storybook; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| SEAL_OF_GOLD | Obtain the relic Seal Of Gold; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| TOASTY_MITTENS | Obtain the relic Toasty Mittens; the source finishes the event after … | none detected | none-detected | 0 | - | - |
| GOLDEN_COMPASS | Obtain the relic Golden Compass; the source finishes the event after … | none detected | none-detected | 0 | - | - |
| PUMPKIN_CANDLE | Obtain the relic Pumpkin Candle; the source finishes the event after … | none detected | none-detected | 0 | - | - |
| TOY_BOX | Obtain the relic Toy Box; the source finishes the event after it | none detected | none-detected | 0 | - | - |

## The Architect (`THE_ARCHITECT`)

Player visits: 0 · highest risk: none-detected · combat event: TheArchitectEventEncounter

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| unknown | none detected | none detected | none-detected | 0 | - | - |
| PROCEED | none detected | none detected | none-detected | 0 | - | - |

## Vakuu (`VAKUU`)

Player visits: 0 · highest risk: none-detected · no combat

| Option | Effect | Cost | Risk | Player picks | Mean HP change | Mean gold change |
|---|---|---|---|---|---|---|
| BLOOD_SOAKED_ROSE | Obtain the relic Blood Soaked Rose; the source finishes the event aft… | none detected | none-detected | 0 | - | - |
| WHISPERING_EARRING | Obtain the relic Whispering Earring; the source finishes the event af… | none detected | none-detected | 0 | - | - |
| FIDDLE | Obtain the relic Fiddle; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| PRESERVED_FOG | Obtain the relic Preserved Fog; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| SERE_TALON | Obtain the relic Sere Talon; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| DISTINGUISHED_CAPE | Obtain the relic Distinguished Cape; the source finishes the event af… | none detected | none-detected | 0 | - | - |
| CHOICES_PARADOX | Obtain the relic Choices Paradox; the source finishes the event after… | none detected | none-detected | 0 | - | - |
| MUSIC_BOX | Obtain the relic Music Box; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| LORDS_PARASOL | Obtain the relic Lords Parasol; the source finishes the event after it | none detected | none-detected | 0 | - | - |
| JEWELED_MASK | Obtain the relic Jeweled Mask; the source finishes the event after it | none detected | none-detected | 0 | - | - |
