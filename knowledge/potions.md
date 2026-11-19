# Potions

Properties and on-use commands from the extracted game data `[GAME-EXTRACT]` (command names, not card text). The Player's counts come from solo runs on v0.107.1 `[PLAYER-DATA]`.

| Potion | Rarity | Usage | Target | On use (game commands) | Taken/offered | Bought | Used | Discarded |
|---|---|---|---|---|---|---|---|---|
| Attack Potion | Common | CombatOnly | Self | CardSelectCmd.FromChooseACardScreen, CardPileCmd.AddGeneratedCardToCombat | 67/130 | 6 | 60 | 7 |
| Block Potion | Common | CombatOnly | AnyPlayer | CreatureCmd.GainBlock | 52/112 | 4 | 43 | 8 |
| Blood Potion | Common | AnyTime | AnyPlayer | CreatureCmd.Heal | 11/22 | 1 | 11 | - |
| Colorless Potion | Common | CombatOnly | Self | CardSelectCmd.FromChooseACardScreen, CardPileCmd.AddGeneratedCardToCombat | 58/122 | 2 | 57 | 1 |
| Dexterity Potion | Common | CombatOnly | AnyPlayer | PowerCmd.Apply<DexterityPower> | 64/129 | 5 | 57 | 6 |
| Energy Potion | Common | CombatOnly | AnyPlayer | PlayerCmd.GainEnergy | 75/141 | 11 | 66 | 5 |
| Explosive Ampoule | Common | CombatOnly | AllEnemies | CreatureCmd.Damage | 69/127 | - | 48 | 15 |
| Fire Potion | Common | CombatOnly | AnyEnemy | CreatureCmd.Damage | 58/117 | 2 | 45 | 8 |
| Flex Potion | Common | CombatOnly | AnyPlayer | PowerCmd.Apply<FlexPotionPower> | 55/121 | 6 | 44 | 8 |
| Focus Potion | Common | CombatOnly | Self | PowerCmd.Apply<FocusPower> | - | - | - | - |
| Poison Potion | Common | CombatOnly | AnyEnemy | PowerCmd.Apply<PoisonPower> | 10/22 | - | 10 | - |
| Potion Of Doom | Common | CombatOnly | AnyEnemy | PowerCmd.Apply<DoomPower> | 15/30 | - | 12 | 2 |
| Power Potion | Common | CombatOnly | Self | CardSelectCmd.FromChooseACardScreen, CardPileCmd.AddGeneratedCardToCombat | 60/119 | 6 | 60 | - |
| Skill Potion | Common | CombatOnly | Self | CardSelectCmd.FromChooseACardScreen, CardPileCmd.AddGeneratedCardToCombat | 51/112 | 7 | 49 | 2 |
| Speed Potion | Common | CombatOnly | AnyPlayer | PowerCmd.Apply<SpeedPotionPower> | 60/117 | - | 40 | 13 |
| Star Potion | Common | CombatOnly | Self | PlayerCmd.GainStars | 12/22 | 2 | 8 | 2 |
| Strength Potion | Common | CombatOnly | AnyPlayer | PowerCmd.Apply<StrengthPower> | 48/106 | 1 | 43 | 3 |
| Swift Potion | Common | CombatOnly | AnyPlayer | CardPileCmd.Draw | 57/115 | 6 | 47 | 9 |
| Vulnerable Potion | Common | CombatOnly | AnyEnemy | PowerCmd.Apply<VulnerablePower> | 57/116 | 2 | 51 | 4 |
| Weak Potion | Common | CombatOnly | AnyEnemy | PowerCmd.Apply<WeakPower> | 62/120 | 4 | 56 | 5 |
| Ashwater | Uncommon | CombatOnly | Self | CardSelectCmd.FromHand, CardCmd.Exhaust | 4/8 | - | 1 | 2 |
| Blessing Of The Forge | Uncommon | CombatOnly | Self | CardCmd.Upgrade | 21/46 | - | 21 | - |
| Bone Brew | Uncommon | CombatOnly | Self | OstyCmd.Summon | 9/15 | - | 9 | - |
| Clarity | Uncommon | CombatOnly | AnyPlayer | CardPileCmd.Draw, PowerCmd.Apply<ClarityPower> | 36/62 | 1 | 35 | - |
| Cunning Potion | Uncommon | CombatOnly | Self | CardCmd.Upgrade | 3/9 | - | 2 | 1 |
| Cure All | Uncommon | CombatOnly | AnyPlayer | PlayerCmd.GainEnergy, CardPileCmd.Draw | 32/49 | 6 | 31 | - |
| Duplicator | Uncommon | CombatOnly | Self | PowerCmd.Apply<DuplicationPower> | 17/37 | 1 | 17 | - |
| Fortifier | Uncommon | CombatOnly | AnyPlayer | CreatureCmd.GainBlock | 21/44 | - | 14 | 5 |
| Fysh Oil | Uncommon | CombatOnly | AnyPlayer | PowerCmd.Apply<StrengthPower>, PowerCmd.Apply<DexterityPower> | 19/49 | - | 17 | 2 |
| Gamblers Brew | Uncommon | CombatOnly | Self | CardSelectCmd.FromHandForDiscard, CardCmd.DiscardAndDraw | 24/42 | - | 18 | 4 |
| Heart Of Iron | Uncommon | CombatOnly | AnyPlayer | PowerCmd.Apply<PlatingPower> | 21/45 | 3 | 21 | - |
| Kings Courage | Uncommon | CombatOnly | AnyPlayer | ForgeCmd.Forge | 6/11 | - | 4 | 1 |
| Liquid Bronze | Uncommon | CombatOnly | AnyPlayer | PowerCmd.Apply<ThornsPower> | 29/63 | 1 | 25 | 3 |
| Potion Of Binding | Uncommon | CombatOnly | AllEnemies | PowerCmd.Apply<WeakPower>, PowerCmd.Apply<VulnerablePower> | 20/44 | 1 | 13 | 5 |
| Potion Of Capacity | Uncommon | CombatOnly | Self | OrbCmd.AddSlots | 1/1 | - | 1 | - |
| Powdered Demise | Uncommon | CombatOnly | AnyEnemy | PowerCmd.Apply<DemisePower> | 24/42 | - | 22 | 1 |
| Radiant Tincture | Uncommon | CombatOnly | AnyPlayer | PlayerCmd.GainEnergy, PowerCmd.Apply<RadiancePower> | 25/48 | 1 | 24 | 1 |
| Regen Potion | Uncommon | CombatOnly | AnyPlayer | PowerCmd.Apply<RegenPower> | 25/54 | 5 | 25 | - |
| Stable Serum | Uncommon | CombatOnly | AnyPlayer | PowerCmd.Apply<RetainHandPower> | 24/48 | - | 13 | 7 |
| Touch Of Insanity | Uncommon | CombatOnly | Self | CardSelectCmd.FromHand | 31/45 | 3 | 29 | - |
| Beetle Juice | Rare | CombatOnly | AnyEnemy | PowerCmd.Apply<ShrinkPower> | 5/17 | - | 4 | 1 |
| Bottled Potential | Rare | CombatOnly | AnyPlayer | CardPileCmd.Add, CardPileCmd.Shuffle, CardPileCmd.Draw | 13/25 | - | 11 | 2 |
| Cosmic Concoction | Rare | CombatOnly | Self | CardCmd.Upgrade, CardPileCmd.AddGeneratedCardToCombat | 1/2 | 1 | 1 | - |
| Distilled Chaos | Rare | CombatOnly | Self | CardPileCmd.AutoPlayFromDrawPile | 6/19 | - | 5 | 1 |
| Droplet Of Precognition | Rare | CombatOnly | Self | CardSelectCmd.FromSimpleGrid, CardPileCmd.Add | 11/18 | - | 9 | - |
| Entropic Brew | Rare | AnyTime | Self | PotionCmd.TryToProcure | 13/21 | - | 13 | - |
| Essence Of Darkness | Rare | CombatOnly | Self | OrbCmd.Channel<DarkOrb> | - | - | - | - |
| Fairy In A Bottle | Rare | Automatic | Self | CreatureCmd.Heal | 14/29 | 3 | 9 | 1 |
| Fruit Juice | Rare | AnyTime | AnyPlayer | CreatureCmd.GainMaxHp | 8/15 | 1 | 8 | - |
| Ghost In A Jar | Rare | CombatOnly | AnyPlayer | PowerCmd.Apply<IntangiblePower> | 3/4 | 1 | 3 | - |
| Gigantification Potion | Rare | CombatOnly | AnyPlayer | PowerCmd.Apply<GigantificationPower> | 8/15 | 1 | 8 | - |
| Liquid Memories | Rare | CombatOnly | Self | CardSelectCmd.FromSimpleGrid, CardPileCmd.Add | 13/19 | 1 | 11 | 2 |
| Lucky Tonic | Rare | CombatOnly | AnyPlayer | PowerCmd.Apply<BufferPower> | 3/13 | - | 1 | 2 |
| Mazaleths Gift | Rare | CombatOnly | AnyPlayer | PowerCmd.Apply<RitualPower> | 7/20 | - | 6 | - |
| Orobic Acid | Rare | CombatOnly | Self | CardPileCmd.AddGeneratedCardsToCombat | 8/18 | - | 7 | - |
| Pot Of Ghouls | Rare | CombatOnly | Self |  | 2/5 | - | 1 | 1 |
| Shackling Potion | Rare | CombatOnly | AllEnemies | PowerCmd.Apply<ShacklingPotionPower> | 7/15 | - | 6 | 1 |
| Ship In A Bottle | Rare | CombatOnly | AnyPlayer | CreatureCmd.GainBlock, PowerCmd.Apply<BlockNextTurnPower> | 8/18 | - | 7 | 1 |
| Snecko Oil | Rare | CombatOnly | AnyPlayer | CardPileCmd.Draw | 13/23 | - | 11 | 2 |
| Soldiers Stew | Rare | CombatOnly | AnyPlayer |  | 4/6 | - | 4 | - |
| Deprecated Potion | None | CombatOnly | AnyEnemy |  | - | - | - | - |
| Foul Potion | Event | AnyTime | TargetedNoCreature | CreatureCmd.Damage, PlayerCmd.GainGold | 17/24 | - | 12 | - |
| Glowwater Potion | Event | CombatOnly | Self | CardCmd.Exhaust, CardPileCmd.Draw | 2/3 | - | - | 2 |
| Potion Shaped Rock | Token | CombatOnly | AnyEnemy | CreatureCmd.Damage | 25/25 | - | 25 | - |
