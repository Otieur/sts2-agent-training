# Relics

Effects from the extracted game data `[GAME-EXTRACT]` (hook names kept: `AfterSideTurnStart` = at the start of your turn, `AfterObtained` = when picked up). The Player's offer, pick and purchase counts, Ancient pick rates and final-relic win rates come from solo runs on v0.107.1 `[PLAYER-DATA]`. Win rates are survivorship-biased (relics obtained late appear only in long runs). Baseline win rate of finished runs: 23%.

**Applied by the fight simulator** (`tools/simulate_fight.py` `SIM_RELICS`, plainest reading of the game data, once per fight unless the data says otherwise `[HYPOTHESIS]`): Vajra +1 Strength, Oddly Smooth Stone +1 Dexterity, Anchor 10 Block on turn 1, Bag of Preparation +2 cards on turn 1, Red Mask 1 Weak on the enemy, Gorget 4 Plating, Blood Vial heal 2, Festive Popper 9 damage, Happy Flower +1 energy every third turn, Lizard Tail revives once at half HP, Red Skull +3 Strength at half HP or less. Live play does not need these: the mod's state already shows their effects (Strength, Block, energy).

## Starter (10)

| Relic | Owner | Effect | Picked/offered | Bought | Final-relic win rate |
|---|---|---|---|---|---|
| Black Blood | Event | AfterCombatVictory: Heal 12 HP | 1/1 | - | n=1 |
| Bound Phylactery | Necrobinder | BeforeCombatStart: Summon 1; AfterEnergyResetLate: Summon 1 | - | - | 19% (n=48) |
| Burning Blood | Ironclad | AfterCombatVictory: Heal 6 HP | - | - | 24% (n=51) |
| Cracked Core | Defect | BeforeSideTurnStart: Channel a Lightning orb | - | - | n=5 |
| Divine Destiny | Event | AfterSideTurnStart: Gain 6 Stars | 1/1 | - | n=1 |
| Divine Right | Regent | AfterRoomEntered: Gain 3 Stars | - | - | 23% (n=44) |
| Infused Core | Event | AfterSideTurnStart: Channel a Lightning orb | - | - | - |
| Phylactery Unbound | Event | BeforeCombatStart: Summon 5; AfterSideTurnStart: Summon 2 | 4/4 | - | n=4 |
| Ring Of The Drake | Event | ModifyHandDraw: returns count or count + 2 | 4/4 | - | n=4 |
| Ring Of The Snake | Silent | ModifyHandDraw: returns count or count + 2 | - | - | 18% (n=39) |

## Common (30)

| Relic | Owner | Effect | Picked/offered | Bought | Final-relic win rate |
|---|---|---|---|---|---|
| Amethyst Aubergine | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); TryModifyRewards: returns false or true | 16/16 | - | 27% (n=15) |
| Anchor | Shared | BeforeCombatStart: Gain 10 Block | 21/38 | 4 | 50% (n=20) |
| Bag Of Preparation | Shared | ModifyHandDraw: returns count or count + 2 | 27/38 | 6 | 56% (n=27) |
| Blood Vial | Shared | AfterPlayerTurnStartLate: Heal 2 HP | 21/38 | 1 | 50% (n=20) |
| Bone Flute | Necrobinder | AfterAttack: Gain 2 Block | 6/9 | 1 | n=6 |
| Book Of Five Rings | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); AfterCardChangedPiles: Heal 15 HP | 20/42 | 4 | 40% (n=20) |
| Bronze Scales | Shared | AfterRoomEntered: Gain 3 Thorns | 19/39 | 1 | 50% (n=18) |
| Centennial Puzzle | Shared | AfterDamageReceived: Draw 1 card | 24/42 | 1 | 43% (n=23) |
| Data Disk | Defect | AfterRoomEntered: Gain 1 Focus | - | - | - |
| Fencing Manual | Regent | AfterSideTurnStart: Forge 10 | 3/4 | 2 | n=3 |
| Festive Popper | Shared | AfterPlayerTurnStart: Deal 9 damage to the target | 18/28 | 1 | 39% (n=18) |
| Gorget | Shared | AfterRoomEntered: Gain 4 Plating | 23/43 | 3 | 23% (n=22) |
| Happy Flower | Shared | AfterSideTurnStart: Gain 1 Energy | 27/45 | 7 | 41% (n=27) |
| Juzu Bracelet | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); ModifyUnknownMapPointRoomTypes: returns ha… | 23/39 | 4 | 14% (n=21) |
| Lantern | Shared | AfterSideTurnStart: Gain 1 Energy | 34/48 | 10 | 41% (n=34) |
| Meal Ticket | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); AfterRoomEntered: Heal 15 HP | 24/42 | - | 32% (n=22) |
| Oddly Smooth Stone | Shared | AfterRoomEntered: Gain 1 Dexterity | 25/42 | 4 | 39% (n=23) |
| Pendulum | Shared | AfterShuffle: Draw 1 card | 21/36 | 5 | 52% (n=21) |
| Permafrost | Shared | AfterCardPlayed: Gain 6 Block | 11/26 | 2 | 50% (n=10) |
| Potion Belt | Shared | AfterObtained: gain Max Potion Count | 17/37 | - | 35% (n=17) |
| Red Skull | Ironclad | AfterRoomEntered: Apply -3 Strength to the target; AfterRoomEntered: Apply 3 Strength to the target; AfterCur… | 7/11 | 2 | n=7 |
| Regal Pillow | Shared | ModifyRestSiteHealAmount: returns amount or amount + 15; ModifyExtraRestSiteHealText: returns currentExtraTex… | 18/35 | 3 | 25% (n=16) |
| Snecko Skull | Silent | ModifyPowerAmountGiven: returns amount or amount + 1 | 2/4 | - | n=2 |
| Strawberry | Shared | AfterObtained: Gain 7 Max HP | 12/34 | 1 | 58% (n=12) |
| Strike Dummy | Shared | ModifyDamageAdditive: returns 0 or 3 | 13/34 | 2 | 27% (n=11) |
| Tiny Mailbox | Shared | TryModifyRestSiteHealRewards: returns false or true; ModifyExtraRestSiteHealText: returns currentExtraText or… | 11/22 | - | 40% (n=10) |
| Vajra | Shared | AfterRoomEntered: Gain 1 Strength | 32/47 | 4 | 35% (n=31) |
| Venerable Tea Set | Shared | AfterEnergyReset: Gain 2 Energy | 31/47 | 5 | 29% (n=31) |
| War Paint | Shared | AfterObtained: Upgrade a card | 20/42 | 5 | 30% (n=20) |
| Whetstone | Shared | AfterObtained: Upgrade a card | 14/32 | 1 | 31% (n=13) |

## Uncommon (40)

| Relic | Owner | Effect | Picked/offered | Bought | Final-relic win rate |
|---|---|---|---|---|---|
| Akabeko | Shared | AfterSideTurnStart: Gain 8 Vigor | 11/19 | - | 30% (n=10) |
| Bag Of Marbles | Shared | BeforeSideTurnStart: Apply 1 Vulnerable to the target | 17/40 | 4 | 29% (n=17) |
| Bellows | Shared | AfterPlayerTurnStart: Upgrade a card | 8/12 | - | 25% (n=8) |
| Book Repair Knife | Necrobinder | AfterDiedToDoom: Heal ? HP | 3/8 | - | n=3 |
| Bowler Hat | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); ShouldGainGold: returns true; AfterGoldGai… | 4/4 | - | n=4 |
| Candelabra | Shared | AfterSideTurnStart: Gain 2 Energy | 13/20 | 3 | 54% (n=13) |
| Eternal Feather | Shared | AfterRoomEntered: Heal ? HP | 17/22 | 4 | 59% (n=17) |
| Funerary Mask | Necrobinder | AfterSideTurnStart: Add a generated card to your draw pile | 3/6 | - | n=3 |
| Galactic Dust | Regent | AfterStarsSpent: Gain ? Block | 3/6 | - | n=3 |
| Gold Plated Cables | Defect | ModifyOrbPassiveTriggerCounts: returns triggerCount or triggerCount + 1 | - | - | - |
| Gremlin Horn | Shared | AfterDeath: Gain 1 Energy; AfterDeath: Draw 1 card | 20/28 | 1 | 21% (n=19) |
| Horn Cleat | Shared | AfterBlockCleared: Gain 14 Block | 12/19 | 1 | 42% (n=12) |
| Joss Paper | Shared | no gameplay command in an overridden hook (passive in source) | 4/10 | - | n=4 |
| Kusarigama | Shared | AfterCardPlayed: Deal 6 damage to the target | 11/19 | - | 55% (n=11) |
| Letter Opener | Shared | AfterCardPlayed: Lose 5 HP | 9/23 | - | 22% (n=9) |
| Lucky Fysh | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); AfterCardChangedPiles: Gain 15 Gold | 9/9 | - | n=7 |
| Mercury Hourglass | Shared | AfterPlayerTurnStart: Deal 3 damage to the target | 10/18 | 1 | 44% (n=9) |
| Miniature Cannon | Shared | ModifyDamageAdditive: returns 0 or 3 | 12/20 | 2 | 42% (n=12) |
| Nunchaku | Shared | AfterCardPlayed: Gain 1 Energy | 9/21 | 2 | n=7 |
| Orichalcum | Shared | BeforeTurnEnd: Gain 6 Block | 10/23 | 1 | 30% (n=10) |
| Ornamental Fan | Shared | AfterCardPlayed: Gain 4 Block | 17/23 | 2 | 31% (n=16) |
| Pantograph | Shared | AfterRoomEntered: Heal 25 HP | 15/26 | 5 | 46% (n=13) |
| Paper Phrog | Ironclad | no gameplay command in an overridden hook (passive in source) | 2/5 | - | n=2 |
| Parrying Shield | Shared | AfterTurnEnd: Deal 6 damage to the target | 10/23 | 1 | 12% (n=8) |
| Pear | Shared | AfterObtained: Gain 10 Max HP | 15/26 | 1 | 40% (n=15) |
| Pen Nib | Shared | ModifyDamageMultiplicative: returns 1 or 2 | 12/22 | 1 | 42% (n=12) |
| Petrified Toad | Shared | BeforeCombatStartLate: Obtain a random potion | 8/19 | - | 38% (n=8) |
| Planisphere | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); AfterRoomEntered: Heal 4 HP | 6/14 | - | n=6 |
| Red Mask | Shared | BeforeSideTurnStart: Apply 1 Weak to the target | 15/42 | - | 29% (n=14) |
| Regalite | Regent | AfterCardEnteredCombat: Gain 2 Block | 0/1 | - | - |
| Reptile Trinket | Shared | AfterPotionUsed: Gain 3 Reptile Trinket | 6/26 | - | n=6 |
| Ripple Basin | Shared | BeforeTurnEnd: Gain 4 Block | 9/17 | 1 | 33% (n=9) |
| Self Forming Clay | Ironclad | AfterDamageReceived: Gain 3 Self Forming Clay | - | - | - |
| Sparkling Rouge | Event/Shared | AfterBlockCleared: Gain 1 Strength; AfterBlockCleared: Gain 1 Dexterity | 12/21 | - | 33% (n=12) |
| Stone Cracker | Shared | AfterRoomEntered: Upgrade a card | 8/18 | 1 | 25% (n=8) |
| Symbiotic Virus | Defect | AfterSideTurnStart: Channel a Dark orb | - | - | - |
| Tingsha | Silent | AfterCardDiscarded: Deal 3 damage to the target | 2/2 | 1 | n=2 |
| Tuning Fork | Shared | AfterCardPlayed: Gain 7 Block | 13/24 | - | 38% (n=13) |
| Twisted Funnel | Silent | BeforeSideTurnStart: Apply 4 Poison to the target | 2/3 | 1 | n=2 |
| Vambrace | Shared | ModifyBlockMultiplicative: returns 1 or 2 | 13/27 | - | 58% (n=12) |

## Rare (50)

| Relic | Owner | Effect | Picked/offered | Bought | Final-relic win rate |
|---|---|---|---|---|---|
| Art Of War | Shared | AfterEnergyReset: Gain 1 Energy | 5/8 | - | n=4 |
| Beating Remnant | Shared | ModifyHpLostAfterOsty: returns amount or Math.Min(amount, 20 - DamageReceivedThisTurn) | 3/4 | - | n=3 |
| Big Hat | Necrobinder | AfterSideTurnStart: get Distinct For Combat; AfterSideTurnStart: Add a generated card to your hand | 2/2 | 1 | n=2 |
| Bookmark | Necrobinder | no gameplay command in an overridden hook (passive in source) | 2/2 | - | n=2 |
| Captains Wheel | Shared | AfterBlockCleared: Gain 18 Block | 2/8 | - | n=2 |
| Chandelier | Shared | AfterSideTurnStart: Gain 3 Energy | 3/7 | - | n=3 |
| Charons Ashes | Ironclad | AfterCardExhausted: Lose ? HP | 1/1 | 1 | n=1 |
| Cloak Clasp | Shared | BeforeTurnEnd: Gain ? Block | 4/9 | - | n=4 |
| Demon Tongue | Ironclad | AfterDamageReceived: Heal ? HP | 1/2 | - | n=1 |
| Emotion Chip | Defect | AfterPlayerTurnStart: Trigger an orb passive | - | - | - |
| Frozen Egg | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); TryModifyCardRewardOptionsLate: returns fa… | 7/9 | - | n=7 |
| Gambling Chip | Shared | AfterPlayerTurnStart: Discard 999999999 cards from your hand; AfterPlayerTurnStart: Discard your hand and dra… | 7/14 | 1 | n=7 |
| Game Piece | Shared | AfterCardPlayed: Draw 1 card | 2/7 | - | n=2 |
| Girya | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); AfterRoomEntered: Gain ? Strength; TryModi… | 2/5 | - | n=2 |
| Helical Dart | Silent | AfterCardPlayed: Gain 1 Helical Dart | - | - | - |
| Ice Cream | Shared | ShouldPlayerResetEnergy: returns true or false | 3/6 | 1 | n=3 |
| Intimidating Helmet | Shared | BeforeCardPlayed: Gain 4 Block | 9/12 | - | n=7 |
| Ivory Tile | Necrobinder | AfterCardPlayed: Gain 1 Energy | 0/1 | - | - |
| Kunai | Shared | AfterCardPlayed: Gain 1 Dexterity | 7/11 | - | n=7 |
| Lasting Candy | Event/Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); TryModifyCardRewardOptions: Offer a card r… | 8/19 | 1 | n=7 |
| Lizard Tail | Shared | ShouldDieLate: returns true or false; AfterPreventingDeath: Heal ? HP | 7/10 | - | n=7 |
| Lunar Pastry | Regent | AfterTurnEnd: Gain 1 Stars | 0/1 | - | - |
| Mango | Shared | AfterObtained: Gain 14 Max HP | 4/6 | - | n=4 |
| Meat On The Bone | Shared | BeforeCombatStart: returns creature.CurrentHp <= num; AfterCurrentHpChanged: returns creature.CurrentHp <= nu… | 7/10 | 1 | n=7 |
| Metronome | Defect | AfterOrbChanneled: Lose 30 HP | - | - | - |
| Mini Regent | Regent | AfterStarsSpent: Gain 1 Strength | 0/1 | - | - |
| Molten Egg | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); TryModifyCardRewardOptionsLate: returns fa… | 5/13 | 2 | n=5 |
| Mummified Hand | Shared | no gameplay command in an overridden hook (passive in source) | 5/9 | 1 | n=5 |
| Old Coin | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); AfterObtained: Gain 300 Gold | 2/2 | - | n=2 |
| Orange Dough | Regent | AfterSideTurnStart: get Distinct For Combat; AfterSideTurnStart: Add a generated card to your hand | 1/2 | - | n=1 |
| Paper Krane | Silent | no gameplay command in an overridden hook (passive in source) | 1/1 | 1 | n=1 |
| Pocketwatch | Shared | ModifyHandDraw: returns count or count + 3 | 3/5 | - | n=3 |
| Power Cell | Defect | BeforeSideTurnStart: Put a card into your hand | - | - | - |
| Prayer Wheel | Shared | TryModifyRewards: returns false or true | 4/6 | - | n=4 |
| Rainbow Ring | Shared | AfterCardPlayed: Gain 1 Strength; AfterCardPlayed: Gain 1 Dexterity | 4/4 | - | n=4 |
| Razor Tooth | Event/Shared | AfterCardPlayed: Upgrade a card | 0/3 | - | - |
| Ruined Helmet | Ironclad | TryModifyPowerAmountReceived: returns false or true | 5/5 | 2 | n=5 |
| Shovel | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); TryModifyRestSiteOptions: returns false or… | 5/10 | - | n=5 |
| Shuriken | Shared | AfterCardPlayed: Gain 1 Strength | 4/13 | - | n=4 |
| Stone Calendar | Shared | BeforeTurnEnd: Lose 52 HP | 3/8 | - | n=3 |
| Sturdy Clamp | Shared | ShouldClearBlock: returns true or false; AfterPreventingBlockClear: Lose all Block | 6/8 | - | n=6 |
| The Courier | Shared | ModifyMerchantPrice: returns originalPrice or originalPrice * (1 - 20 / 100); ShouldRefillMerchantEntry: retu… | 5/5 | - | n=4 |
| Tough Bandages | Silent | AfterCardDiscarded: Gain 3 Block | 0/1 | - | - |
| Toxic Egg | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); TryModifyCardRewardOptionsLate: returns fa… | 3/9 | - | n=3 |
| Tungsten Rod | Shared | ModifyHpLostAfterOsty: returns amount or Math.Max(0, amount - 1) | 4/6 | 1 | n=4 |
| Unceasing Top | Shared | AfterHandEmptied: Draw 1 card | 5/12 | 1 | n=5 |
| Unsettling Lamp | Shared | ModifyPowerAmountGiven: returns amount or amount * 2 | 4/8 | 1 | n=4 |
| Vexing Puzzlebox | Shared | AfterPlayerTurnStart: get Distinct For Combat; AfterPlayerTurnStart: Add a generated card to your hand | 4/5 | - | n=4 |
| White Beast Statue | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); ShouldForcePotionReward: returns false or … | 6/10 | 1 | n=6 |
| White Star | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); TryModifyRewards: returns false or true | 12/18 | 3 | 17% (n=12) |

## Shop (30)

| Relic | Owner | Effect | Picked/offered | Bought | Final-relic win rate |
|---|---|---|---|---|---|
| Belt Buckle | Shared | AfterObtained: Gain 2 Dexterity; BeforeCombatStart: Gain 2 Dexterity; AfterPotionProcured: Gain -2 Dexterity;… | 5/20 | 5 | n=5 |
| Bread | Shared | ModifyMaxEnergy: returns amount or amount + 1; AfterSideTurnStart: lose Energy | 4/19 | 4 | n=4 |
| Brimstone | Ironclad | AfterSideTurnStart: Gain 2 Strength; AfterSideTurnStart: Apply 1 Strength to the target | 1/8 | 1 | n=1 |
| Burning Sticks | Shared | AfterCardExhausted: Add a generated card to your hand | 1/21 | 1 | n=1 |
| Cauldron | Shared | AfterObtained: Offer extra rewards | 1/26 | 1 | n=1 |
| Chemical X | Shared | ModifyXValue: returns originalValue or originalValue + 2 | 2/20 | 2 | n=2 |
| Dingy Rug | Shared | ModifyCardRewardCreationOptions: returns options or options.WithCustomPool(list) | 2/14 | 2 | n=2 |
| Dollys Mirror | Shared | AfterObtained: Choose a card in your deck; AfterObtained: Put a card into your deck | 1/15 | 1 | n=1 |
| Dragon Fruit | Shared | IsAllowed: returns RelicModel.IsBeforeAct3TreasureChest(runState); AfterGoldGained: Gain 1 Max HP | 2/16 | 2 | n=2 |
| Ghost Seed | Shared | AfterCardEnteredCombat: Give a card Ethereal; AfterRoomEntered: Give a card Ethereal | 2/18 | 2 | n=2 |
| Gnarled Hammer | Shared | AfterObtained: Enchant a card in your deck; AfterObtained: Enchant a card | 1/13 | 1 | n=1 |
| Kifuda | Shared | AfterObtained: Enchant a card in your deck; AfterObtained: Enchant a card | 1/10 | 1 | n=1 |
| Lava Lamp | Shared | TryModifyCardRewardOptionsLate: Upgrade a card | 0/20 | - | - |
| Lees Waffle | Shared | AfterObtained: Gain 7 Max HP; AfterObtained: Heal ? HP | 7/26 | 7 | n=6 |
| Membership Card | Shared | ModifyMerchantPrice: returns originalPrice or originalPrice * (50 / 100) | 7/26 | 7 | n=7 |
| Miniature Tent | Shared | ShouldDisableRemainingRestSiteOptions: returns true or false | 12/18 | 12 | 45% (n=11) |
| Mystic Lighter | Shared | ModifyDamageAdditive: returns 0 or 9 | 2/18 | 2 | n=2 |
| Ninja Scroll | Silent | BeforeHandDraw: Add 3 Shivs to your hand | 0/4 | - | - |
| Orrery | Shared | AfterObtained: Offer extra rewards | 4/23 | 4 | n=4 |
| Punch Dagger | Shared | AfterObtained: Enchant a card in your deck; AfterObtained: Enchant a card | 1/23 | 1 | n=1 |
| Ringing Triangle | Shared | ShouldFlush: returns true or player.Creature.CombatState.RoundNumber > 1 | 0/17 | - | - |
| Royal Stamp | Shared | AfterObtained: Enchant a card in your deck; AfterObtained: Enchant a card with Royally Approved | 1/17 | 1 | n=1 |
| Runic Capacitor | Defect | AfterSideTurnStart: Add 3 orb slot(s) | - | - | - |
| Screaming Flagon | Shared | BeforeTurnEnd: Lose 20 HP | 0/16 | - | - |
| Sling Of Courage | Shared | AfterRoomEntered: Gain 2 Strength | 2/18 | 2 | n=2 |
| The Abacus | Shared | AfterShuffle: Gain 6 Block | 1/25 | 1 | n=1 |
| Toolbox | Shared | BeforeHandDraw: get Distinct For Combat; BeforeHandDraw: Choose a card from an offered set; BeforeHandDraw: A… | 2/23 | 2 | n=2 |
| Undying Sigil | Necrobinder | ModifyDamageMultiplicative: returns 1 or 0.5 | 0/5 | - | - |
| Vitruvian Minion | Regent | ModifyDamageMultiplicative: returns 1 or 2; ModifyBlockMultiplicative: returns 1 or 2 | 1/4 | 1 | - |
| Wing Charm | Shared | TryModifyCardRewardOptionsLate: Enchant a card with Swift | 2/20 | 2 | n=2 |

## Ancient (92)

| Relic | Owner | Effect | Picked/offered | Bought | Final-relic win rate |
|---|---|---|---|---|---|
| Alchemical Coffer | Event | AfterObtained: gain Max Potion Count; AfterObtained: create Random Potions Out Of Combat; AfterObtained: Obta… | 0/16 | - | - |
| Arcane Scroll | Event | AfterObtained: Offer a card reward; AfterObtained: Put a card into your deck | 20/20 | - | 23% (n=13) |
| Archaic Tooth | Event | AfterObtained: Transform a card | 11/11 | - | 27% (n=11) |
| Astrolabe | Event | AfterObtained: Transform a card in your deck; AfterObtained: create Random Card For Transform; AfterObtained:… | 8/8 | - | 50% (n=8) |
| Beautiful Bracelet | Event | AfterObtained: Enchant a card in your deck; AfterObtained: Enchant a card with Swift | 0/9 | - | - |
| Biiig Hug | Event | AfterObtained: Remove a card from your deck; AfterShuffle: Add a generated card to your draw pile | 0/15 | - | - |
| Black Star | Event | TryModifyRewards: returns false or true | 1/1 | - | n=1 |
| Blessed Antler | Event | ModifyMaxEnergy: returns amount or amount + 1; BeforeHandDraw: Add a generated card to your draw pile | 5/5 | - | n=5 |
| Blood Soaked Rose | Event | AfterObtained: Add the curse Enthralled to your deck; ModifyMaxEnergy: returns amount or amount + 1 | 7/7 | - | n=7 |
| Booming Conch | Event | ModifyHandDraw: returns count or count + 2 | 2/2 | - | n=1 |
| Brilliant Scarf | Event | TryModifyEnergyCostInCombat: returns false or true; TryModifyStarCost: returns false or true | 7/7 | - | n=7 |
| Calling Bell | Event | AfterObtained: Add the curse Curse Of The Bell to your deck; AfterObtained: Offer extra rewards | 4/4 | - | n=4 |
| Choices Paradox | Event | AfterPlayerTurnStart: get Distinct For Combat; AfterPlayerTurnStart: Give a card Retain; AfterPlayerTurnStart… | 0/10 | - | - |
| Claws | Event | AfterObtained: Transform a card in your deck; AfterObtained: Transform a card | 2/2 | - | n=2 |
| Crossbow | Event | AfterSideTurnStart: get Distinct For Combat; AfterSideTurnStart: Add a generated card to your hand | 0/5 | - | - |
| Cursed Pearl | Event | AfterObtained: Add the curse Greed to your deck; AfterObtained: Gain 333 Gold | 17/17 | - | 33% (n=15) |
| Delicate Frond | Event | BeforeCombatStart: create Random Potion Out Of Combat; BeforeCombatStart: Obtain a random potion | 3/3 | - | n=3 |
| Diamond Diadem | Event | BeforeTurnEnd: Gain 1 Diamond Diadem | 0/7 | - | - |
| Distinguished Cape | Event | AfterObtained: Lose 9 Max HP; AfterObtained: Put a card into your deck | 3/3 | - | n=3 |
| Driftwood | Event | TryModifyRewardsLate: returns false or true | 0/16 | - | - |
| Dusty Tome | Event | AfterObtained: Upgrade a card; AfterObtained: Put a card into your deck | 4/4 | - | n=4 |
| Ectoplasm | Event | ShouldGainGold: returns player != base.Owner; ModifyMaxEnergy: returns amount or amount + 1 | 0/2 | - | - |
| Electric Shrymp | Event | AfterObtained: Enchant a card in your deck; AfterObtained: Enchant a card | 2/2 | - | n=2 |
| Empty Cage | Event | AfterObtained: Remove a card from your deck | 3/3 | - | n=3 |
| Fiddle | Event | ModifyHandDrawLate: returns count or count + 2; ShouldDraw: returns true or false | 4/4 | - | n=4 |
| Fur Coat | Event | ModifyGeneratedMapLate: returns AddMarkedRooms(map); BeforeCombatStart: set Current HP | 2/2 | - | n=2 |
| Glass Eye | Event | AfterObtained: Offer extra rewards | 1/1 | - | n=1 |
| Glitter | Event | TryModifyCardRewardOptionsLate: Enchant a card with Glam | 1/1 | - | n=1 |
| Golden Compass | Event | ModifyGeneratedMap: returns map or new GoldenPathActMap(runState); ModifyUnknownMapPointRoomTypes: returns ro… | 3/3 | - | n=3 |
| Golden Pearl | Event | AfterObtained: Gain 150 Gold | 21/21 | - | 35% (n=20) |
| Iron Club | Event | AfterCardPlayed: Draw 1 card | 3/3 | - | n=3 |
| Jeweled Mask | Event | BeforeHandDraw: Put a card into your hand | 1/1 | - | n=1 |
| Jewelry Box | Event | AfterObtained: Put a card into your deck | 3/3 | - | n=3 |
| Large Capsule | Event | AfterObtained: Obtain a random relic; AfterObtained: Obtain a relic; AfterObtained: Put a card into your deck | 7/7 | - | n=6 |
| Lava Rock | Event | TryModifyRewards: returns false or true | 6/6 | - | n=4 |
| Lead Paperweight | Event | AfterObtained: Offer a card reward; AfterObtained: Choose a card from an offered set; AfterObtained: Put a ca… | 13/13 | - | 27% (n=11) |
| Leafy Poultice | Event | AfterObtained: Lose 10 Max HP; AfterObtained: Transform a card | 5/5 | - | n=5 |
| Looming Fruit | Shared | AfterObtained: Gain 31 Max HP | 2/2 | - | n=2 |
| Lords Parasol | Event | no gameplay command in an overridden hook (passive in source) | 0/5 | - | - |
| Lost Coffer | Event | AfterObtained: Offer extra rewards | 6/6 | - | n=4 |
| Massive Scroll | Event | AfterObtained: Offer a card reward; AfterObtained: Choose a card from an offered set; AfterObtained: Put a ca… | - | - | - |
| Meat Cleaver | Event | TryModifyRestSiteOptions: returns false or true | 4/4 | - | n=4 |
| Music Box | Event | AfterCardPlayed: Give a card Ethereal; AfterCardPlayed: Add a generated card to your hand | 0/8 | - | - |
| Neows Torment | Event | AfterObtained: Put a card into your deck | 5/5 | - | n=4 |
| New Leaf | Event | AfterObtained: Transform a card in your deck; AfterObtained: Transform a card into a random card | 1/1 | - | n=1 |
| Nutritious Oyster | Event | AfterObtained: Gain 11 Max HP | 2/2 | - | n=1 |
| Nutritious Soup | Event | AfterObtained: Enchant a card with Tezcataras Ember | 13/13 | - | 23% (n=13) |
| Paels Blood | Event | ModifyHandDraw: returns count or count + 1 | 7/7 | - | n=6 |
| Paels Claw | Event | AfterObtained: Enchant a card with Goopy | 1/1 | - | n=1 |
| Paels Eye | Event | ShouldTakeExtraTurn: returns player == base.Owner or false; BeforeTurnEndEarly: Exhaust a card | 0/11 | - | - |
| Paels Flesh | Event | AfterSideTurnStart: Gain 1 Energy | 9/9 | - | 67% (n=9) |
| Paels Growth | Event | AfterObtained: Enchant a card in your deck; AfterObtained: Enchant a card with Clone; TryModifyRestSiteOption… | 1/1 | - | n=1 |
| Paels Horn | Event | AfterObtained: Put a card into your deck | 3/3 | - | n=3 |
| Paels Legion | Event | AfterObtained: add Pet Mega Crit Sts2 Core Models Monsters Paels Legion; BeforeCombatStart: add Pet Mega Crit… | 0/12 | - | - |
| Paels Tears | Event | AfterSideTurnStart: Gain 2 Energy | 6/6 | - | n=6 |
| Paels Tooth | Event | AfterObtained: Remove a card from your deck; AfterCombatEnd: Upgrade a card; AfterCombatEnd: Put a card into … | 3/3 | - | n=3 |
| Paels Wing | Event | TryModifyCardRewardAlternatives: returns false or true | 6/6 | - | n=5 |
| Pandoras Box | Event | AfterObtained: create Random Card For Transform; AfterObtained: Transform a card | 2/2 | - | n=2 |
| Philosophers Stone | Event | ModifyMaxEnergy: returns amount or amount + 1; AfterCreatureAddedToCombat: Apply 1 Strength to the target; Af… | - | - | - |
| Pomander | Event | AfterObtained: Upgrade a card in your deck; AfterObtained: Upgrade a card | 5/5 | - | n=3 |
| Precarious Shears | Event | AfterObtained: Remove a card from your deck; AfterObtained: Lose 13 HP | 3/3 | - | n=2 |
| Precise Scissors | Event | AfterObtained: Remove a card from your deck | 1/1 | - | n=1 |
| Preserved Fog | Event | AfterObtained: Remove a card from your deck; AfterObtained: Add the curse Folly to your deck | 4/4 | - | n=4 |
| Prismatic Gem | Event | ModifyMaxEnergy: returns amount or amount + 1; ModifyCardRewardCreationOptions: returns options or options.Wi… | 2/2 | - | n=2 |
| Pumpkin Candle | Event | ModifyMaxEnergy: returns amount or amount + 1 | 6/6 | - | n=6 |
| Radiant Pearl | Event | BeforeHandDraw: Add a generated card to your hand | 2/2 | - | n=2 |
| Runic Pyramid | Event | ShouldFlush: returns true or false | 0/6 | - | - |
| Sai | Event | AfterSideTurnStart: Gain 7 Block | 4/4 | - | n=4 |
| Sand Castle | Event | AfterObtained: Upgrade a card | 6/6 | - | n=6 |
| Scroll Boxes | Event | AfterObtained: Lose ? Gold; AfterObtained: from Choose A Bundle Screen; AfterObtained: Put a card into your d… | 18/18 | - | 38% (n=16) |
| Sea Glass | Event | AfterObtained: Offer a card reward; AfterObtained: Choose a card from an offered set; AfterObtained: Put a ca… | 3/3 | - | n=3 |
| Seal Of Gold | Event | AfterSideTurnStart: Gain 1 Energy; AfterSideTurnStart: Lose 5 Gold | 9/9 | - | 33% (n=9) |
| Sere Talon | Event | AfterObtained: Put a card into your deck | 2/2 | - | n=2 |
| Signet Ring | Event | AfterObtained: Gain 999 Gold | 2/2 | - | n=2 |
| Silver Crucible | Event | TryModifyCardRewardOptionsLate: Upgrade a card; ShouldGenerateTreasure: returns true or TreasureRoomsEntered … | 16/16 | - | 13% (n=15) |
| Small Capsule | Event | AfterObtained: Offer extra rewards | 2/2 | - | n=2 |
| Snecko Eye | Event | AfterObtained: Gain 1 Confused; BeforeCombatStart: Gain 1 Confused; ModifyHandDraw: returns count or count + 2 | 0/6 | - | - |
| Sozu | Event | ShouldProcurePotion: returns player != base.Owner; ModifyMaxEnergy: returns amount or amount + 1 | 0/3 | - | - |
| Spiked Gauntlets | Event | ModifyMaxEnergy: returns amount or amount + 1; TryModifyEnergyCostInCombat: returns false or true | 2/2 | - | n=2 |
| Stone Humidifier | Event | AfterRestSiteHeal: Gain 5 Max HP; ModifyExtraRestSiteHealText: returns currentExtraText or new global::_003C_… | 0/14 | - | - |
| Storybook | Event | AfterObtained: Put a card into your deck | 3/3 | - | n=2 |
| Tanxs Whistle | Event | AfterObtained: Put a card into your deck | 0/7 | - | - |
| Throwing Axe | Event | ModifyCardPlayCount: returns playCount or playCount + 1 | 1/1 | - | n=1 |
| Toasty Mittens | Event | BeforeHandDraw: Shuffle your draw pile; BeforeHandDraw: Exhaust a card; BeforeHandDraw: Apply 1 Strength to t… | 0/20 | - | - |
| Touch Of Orobas | Event | AfterObtained: replace | 10/10 | - | 50% (n=10) |
| Toy Box | Event | AfterObtained: Obtain a random relic; AfterObtained: Offer extra rewards; AfterCombatEnd: melt | 2/2 | - | n=2 |
| Tri Boomerang | Event | AfterObtained: Enchant a card in your deck; AfterObtained: Enchant a card with Instinct | 2/2 | - | n=2 |
| Velvet Choker | Event | ModifyMaxEnergy: returns amount or amount + 1; ShouldPlay: returns true or !ShouldPreventCardPlay | 0/2 | - | - |
| Very Hot Cocoa | Shared | AfterSideTurnStart: Gain 4 Energy | 4/4 | - | n=4 |
| War Hammer | Event | AfterCombatVictory: Upgrade a card | 3/3 | - | n=3 |
| Whispering Earring | Event | ModifyMaxEnergy: returns amount or amount + 1; BeforePlayPhaseStart: push Selector; BeforePlayPhaseStart: Aut… | 4/4 | - | n=4 |
| Yummy Cookie | Event | AfterObtained: Upgrade a card in your deck; AfterObtained: Upgrade a card | 5/5 | - | n=5 |

## Event (35)

| Relic | Owner | Effect | Picked/offered | Bought | Final-relic win rate |
|---|---|---|---|---|---|
| Big Mushroom | Event | AfterObtained: Gain 20 Max HP; ModifyHandDraw: returns cardsToDraw or cardsToDraw - 2 | - | - | - |
| Bing Bong | Event | AfterCardChangedPiles: Put a card into your deck | 1/1 | - | n=1 |
| Bone Tea | Event | AfterSideTurnStart: Upgrade a card | 1/1 | - | n=1 |
| Byrdpip | Event | AfterObtained: Transform a card into Byrd Swoop; AfterObtained: add Pet Mega Crit Sts2 Core Models Monsters B… | 7/7 | - | n=7 |
| Chosen Cheese | Event | AfterCombatEnd: Gain 1 Max HP | 5/5 | - | n=5 |
| Darkstone Periapt | Event | AfterCardChangedPiles: Gain 6 Max HP | - | - | - |
| Daughter Of The Wind | Event | AfterCardPlayed: Gain 1 Block | 11/11 | - | 36% (n=11) |
| Dream Catcher | Event | TryModifyRestSiteHealRewards: returns false or true; ModifyExtraRestSiteHealText: returns currentExtraText or… | - | - | - |
| Ember Tea | Event | AfterRoomEntered: Gain 2 Strength | 4/4 | - | n=4 |
| Fake Anchor | Event | BeforeCombatStart: Gain 4 Block | 1/1 | 1 | n=1 |
| Fake Blood Vial | Event | AfterPlayerTurnStartLate: Heal 1 HP | 1/1 | 1 | n=1 |
| Fake Happy Flower | Event | AfterSideTurnStart: Gain 1 Energy | 1/1 | 1 | n=1 |
| Fake Lees Waffle | Event | AfterObtained: Heal ? HP | 4/4 | 4 | n=4 |
| Fake Mango | Event | AfterObtained: Gain 3 Max HP | 2/2 | 2 | n=2 |
| Fake Merchants Rug | Event | no gameplay command in an overridden hook (passive in source) | - | - | - |
| Fake Orichalcum | Event | BeforeTurnEnd: Gain 3 Block | - | - | - |
| Fake Snecko Eye | Event | AfterObtained: Gain 1 Confused; BeforeCombatStart: Gain 1 Confused | - | - | - |
| Fake Strike Dummy | Event | ModifyDamageAdditive: returns 0 or 1 | - | - | - |
| Fake Venerable Tea Set | Event | AfterEnergyReset: Gain 1 Energy | 7/7 | 7 | n=7 |
| Forgotten Soul | Event | AfterCardExhausted: Deal 1 damage to the target | 4/4 | - | n=4 |
| Fragrant Mushroom | Event | AfterObtained: Lose 15 HP; AfterObtained: Upgrade a card | 12/12 | - | 58% (n=12) |
| Fresnel Lens | Shared | TryModifyCardRewardOptionsLate: returns false or true; TryModifyCardBeingAddedToDeck: returns false or true | 13/13 | - | 8% (n=13) |
| Hand Drill | Event | AfterDamageGiven: Apply 2 Vulnerable to the target | - | - | - |
| History Course | Event | AfterPlayerTurnStartEarly: Auto-play a card | 1/1 | - | n=1 |
| Lost Wisp | Event | AfterCardPlayed: Lose 8 HP | 5/5 | - | n=5 |
| Maw Bank | Event | AfterRoomEntered: Gain 12 Gold | 2/2 | - | n=2 |
| Mr Struggles | Event | AfterPlayerTurnStart: Deal ? damage to the target | 3/3 | - | n=3 |
| Pollinous Core | Event | ModifyHandDraw: returns count or count + 2 | - | - | - |
| Royal Poison | Event | AfterPlayerTurnStart: Lose 4 HP | - | - | - |
| Sword Of Jade | Event | AfterRoomEntered: Gain 3 Strength | 3/3 | - | n=3 |
| Sword Of Stone | Event | AfterCombatVictory: replace | 18/18 | - | 0% (n=13) |
| Tea Of Discourtesy | Event | BeforeCombatStart: add To Combat And Preview Dazed | 1/1 | - | n=1 |
| The Boot | Event | ModifyHpLostBeforeOsty: returns amount or 5 | 1/1 | - | n=1 |
| Wongo Customer Appreciation Badge | Event | no gameplay command in an overridden hook (passive in source) | - | - | - |
| Wongos Mystery Ticket | Event | TryModifyRewards: returns false or true | 2/2 | - | n=2 |

## None (2)

| Relic | Owner | Effect | Picked/offered | Bought | Final-relic win rate |
|---|---|---|---|---|---|
| Circlet | Fallback | no gameplay command in an overridden hook (passive in source) | - | - | - |
| Deprecated Relic | Deprecated | no gameplay command in an overridden hook (passive in source) | - | - | - |
