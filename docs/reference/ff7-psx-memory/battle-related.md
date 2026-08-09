# PSX memory — battle-related (excerpt)

Auto-filtered from psx-address-list.json for battle / battle-end / nearby input / audio / rewards.
Full list: same folder JSON/CSV.
Query: python3 docs/reference/ff7-psx-memory/query_memory.py TEXT_OR_ADDR

| Offset | DuckStation VA | Len | Description | Notes |
|--------|----------------|-----|-------------|-------|
| 9010 | 0x80009010 | 4 | PSX RNG (BIOS value) | the main PSX RNG value, used for chocobo racing |
| 4A630 | 0x8004A630 | 1 | Field RNG Increment (Stone) |  |
| 51568 | 0x80051568 | 4 | Global frame counter | increases by 1 every 60fps frame, used to seed chocorace rng |
| 62D4C | 0x80062D4C | 4 | Battle: "Joker" value | +1 on every RNG16 call. When = 0 (mod 8), do not increment index. |
| 62D78 | 0x80062D78 | 2 | Battle Controller Inputs |  |
| 62D7A | 0x80062D7A | 2 | Battle Controller Inputs Copy |  |
| 62D88 | 0x80062D88 | 2 | Battle Controller Inputs (Battle Frame) | Is copied at 15fps, does not update while the game is paused |
| 62D8A | 0x80062D8A | 2 | Battle Controller Inputs (Battle Frame) (Copy) |  |
| 62E10 | 0x80062E10 | 8 | Battle RNG | 8 1-byte indexes into the Battle RNG table |
| 62E18 | 0x80062E18 | 1 | Battle RNG Index | Value from 0-7, specifies which value in ^ to use. Increments on RNG16 (see 62D4C) |
| 62F19 | 0x80062F19 | 1 | Enemy Away / Lure Modifier |  |
| 62F1A | 0x80062F1A | 1 | Chocobo Lure Modifier | 2a0 |
| 62F1B | 0x80062F1B | 1 | Preemptive Rate Modifier | Based on number of preemptive materia you have, 16 by default |
| 62F54 | 0x80062F54 | 4 | Battle: Active Enemy Formation ID | Usually the same as 707BC except this one changes when a mid-battle battle change happens (Hundred/Heli gunner, Hojo,... |
| 707BC | 0x800707BC | 2 | Battle: Starting Enemy Formation ID | Freeze this value to set the next battle |
| 716D0 | 0x800716D0 | 1 | Preemptive Step ID Flag | 4 = Preemptive, lock it to 4 and you only get preempts when possible |
| 71C20 | 0x80071C20 | 1 | Field Formation Accumulator | often called "formation", determines the next battle formation in field encounters |
| 7E774 | 0x8007E774 | 2 | Last Battle Formation |  |
| 7EBC8 | 0x8007EBC8 | 1 | Entering Random Encounter | Duplicating boss glitch happens when this is set to 1 |
| 95DC8 | 0x80095DC8 | 1 | Field RNG (List) |  |
| 9AC60 | 0x8009AC60 | 2 | (Field) Controller Inputs |  |
| 9AC70 | 0x8009AC70 | 2 | (Field) Controller Inputs Copy |  |
| 9C747 | 0x8009C747 | 1 | Cloud's Current Limit Bar |  |
| 9C774 | 0x8009C774 | 4 | Cloud's Current EXP |  |
| 9C7B8 | 0x8009C7B8 | 4 | Cloud's EXP to Next Level |  |
| 9C7CB | 0x8009C7CB | 1 | Barret's Current Limit Bar |  |
| 9C7F8 | 0x8009C7F8 | 4 | Barret's Current EXP |  |
| 9C83C | 0x8009C83C | 4 | Barret's EXP to Next Level |  |
| 9C84F | 0x8009C84F | 1 | Tifa's Current Limit Bar |  |
| 9C87C | 0x8009C87C | 4 | Tifa's Current EXP |  |
| 9C8C0 | 0x8009C8C0 | 4 | Tifa's EXP to Next Level |  |
| 9C8D3 | 0x8009C8D3 | 1 | Aeris's Current Limit Bar |  |
| 9C900 | 0x8009C900 | 4 | Aeris's Current EXP |  |
| 9C944 | 0x8009C944 | 4 | Aeris's EXP to Next Level |  |
| 9C957 | 0x8009C957 | 1 | Red XIII's Current Limit Bar |  |
| 9C984 | 0x8009C984 | 4 | Red XIII's Current EXP |  |
| 9C9C8 | 0x8009C9C8 | 4 | Red XIII's EXP to Next Level |  |
| 9C9DB | 0x8009C9DB | 1 | Yuffie's Current Limit Bar |  |
| 9CA08 | 0x8009CA08 | 4 | Yuffie's Current EXP |  |
| 9CA4C | 0x8009CA4C | 4 | Yuffie's EXP to Next Level |  |
| 9CA5F | 0x8009CA5F | 1 | CaitSith's Current Limit Bar |  |
| 9CA8C | 0x8009CA8C | 4 | CaitSith's Current EXP |  |
| 9CAD0 | 0x8009CAD0 | 4 | CaitSith's EXP to Next Level |  |
| 9CAE3 | 0x8009CAE3 | 1 | Vincent's Current Limit Bar |  |
| 9CB10 | 0x8009CB10 | 4 | Vincent's Current EXP |  |
| 9CB54 | 0x8009CB54 | 4 | Vincent's EXP to Next Level |  |
| 9CB67 | 0x8009CB67 | 1 | Cid's Current Limit Bar |  |
| 9CB94 | 0x8009CB94 | 4 | Cid's Current EXP |  |
| 9CBD8 | 0x8009CBD8 | 4 | Cid's EXP to Next Level |  |
| 9D260 | 0x8009D260 | 4 | Gil |  |
| 9D2A0 | 0x8009D2A0 | 2 | Battle Count | $BattleCount |
| 9D2A2 | 0x8009D2A2 | 2 | Battle Escapes | $BattleEscaped |
| 9D2D8 | 0x8009D2D8 | 1 | Aeris's Battle Affection Rating (dummied out) | $AerisBattleLovePoints |
| 9D2D9 | 0x8009D2D9 | 1 | Tifas Battle Affection Rating (dummied out) | $TifaBattleLovePoints |
| 9D2DA | 0x8009D2DA | 1 | Yuffies Battle Affection Rating (dummied out) | $YuffieBattleLovePoints |
| 9D2DB | 0x8009D2DB | 1 | Barrets Battle Affection Rating (dummied out) | $BarretBattleLovePoints |
| 9D2F8 | 0x8009D2F8 | 4 | Current Battle Square Game BP |  |
| 9D324 | 0x8009D324 | 1 | $VictoryFortCondor | $VictoryFortCondor |
| 9D3E5 | 0x8009D3E5 | 2 | Stable 1 - Battle Count Difference |  |
| 9D3EC | 0x8009D3EC | 2 | Stable 2 - Battle Count Difference |  |
| 9D3EE | 0x8009D3EE | 2 | Stable 3 - Battle Count Difference |  |
| 9D3F0 | 0x8009D3F0 | 2 | Stable 4 - Battle Count Difference |  |
| 9D3F2 | 0x8009D3F2 | 2 | Stable 5 - Battle Count Difference |  |
| 9D3F4 | 0x8009D3F4 | 2 | Stable 6 - Battle Count Difference |  |
| 9D63C | 0x8009D63C | 2 | World Map Last Encounter Formation |  |
| 9D6DF | 0x8009D6DF | 1 | Kalm Traveller Rewards |  |
| C84C8 | 0x800C84C8 | 2 | World Map Controller Inputs |  |
| E0638 | 0x800E0638 | 256 | Field RNG Table |  |
| F39E4 | 0x800F39E4 | 4 | Battle: Forced-Wait Timer |  |
| F5BBC | 0x800F5BBC | 2 | Player 1 ATB |  |
| F5BE4 | 0x800F5BE4 | 4 | Player 1 Cued Damage |  |
| F5C00 | 0x800F5C00 | 2 | Player 2 ATB |  |
| F5C28 | 0x800F5C28 | 4 | Player 2 Cued Damage |  |
| F5C44 | 0x800F5C44 | 2 | Player 3 ATB |  |
| F5C6C | 0x800F5C6C | 4 | Player 3 Cued Damage |  |
| F5CCA | 0x800F5CCA | 2 | Enemy 1 ATB Increase Per Frame |  |
| F5CCC | 0x800F5CCC | 2 | Enemy 1 ATB |  |
| F5CF4 | 0x800F5CF4 | 1 | Enemy 1 Cued Damage |  |
| F5D10 | 0x800F5D10 | 2 | Enemy 2 ATB |  |
| F5D38 | 0x800F5D38 | 4 | Enemy 2 Cued Damage |  |
| F5D54 | 0x800F5D54 | 2 | Enemy 3 ATB |  |
| F5D7C | 0x800F5D7C | 4 | Enemy 3 Cued Damage |  |
| F5D98 | 0x800F5D98 | 2 | Enemy 4 ATB |  |
| F5DC0 | 0x800F5DC0 | 4 | Enemy 4 Cued Damage |  |
| F5DDC | 0x800F5DDC | 2 | Enemy 5 ATB |  |
| F5E04 | 0x800F5E04 | 4 | Enemy 5 Cued Damage |  |
| F5E20 | 0x800F5E20 | 2 | Enemy 6 ATB |  |
| F5E48 | 0x800F5E48 | 4 | Enemy 6 Cued Damage |  |
| F8368 | 0x800F8368 | 4 | Battle Frame Update | Don't mess with this unless you want the battle scene to break. |
| F8370 | 0x800F8370 | 4 | ? | FFFF usually, is set to 0x118 on Flying Sickle? gotta figure this out |
| F83AE | 0x800F83AE | 1 | ? | is usually F7. Changing to _0 causes a Game Over, 0_ causes a Victory, _8 causes all enemies to constantly spend thei... |
| F83C6 | 0x800F83C6 | 1 | Exit Battle Status + Battle Party Lock? | 1 = Victory, 3 = Game Over, 4-5 = Run Away, 8-F = Fade Out Exit. 0x10, 0x40, 0x80 disable party members, and switchin... |
| F8408 | 0x800F8408 | 2 | Player 1 Current MP |  |
| F840A | 0x800F840A | 2 | Player 1 Max MP |  |
| F840C | 0x800F840C | 2 | Player 1 Current HP |  |
| F8410 | 0x800F8410 | 2 | Player 1 Max HP |  |
| F8474 | 0x800F8474 | 2 | Player 2 Current HP |  |
| F84DC | 0x800F84DC | 2 | Player 3 Current HP |  |
| F859A | 0x800F859A | 2 | Enemy 1 Last Attacked By |  |
| F859C | 0x800F859C | 2 | Enemy 1 Last Damaged By |  |
| F859E | 0x800F859E | 2 | Enemy 1 Last Magic'd By |  |
| F85A4 | 0x800F85A4 | 2 | Enemy 1 ID |  |
| F85AC | 0x800F85AC | 2 | Enemy 1 Current HP | Live actor HP in battle (confirmed). Slot stride 0x68 from Enemy 1. Enemy N = F85AC + (N-1)*0x68. Distinct from stats... |
| F85B0 | 0x800F85B0 | 2 | Enemy 1 Max HP | Live actor HP in battle (confirmed). Slot stride 0x68 from Enemy 1. Enemy N = F85AC + (N-1)*0x68. Distinct from stats... |
| F860C | 0x800F860C | 2 | Enemy 2 ID |  |
| F8614 | 0x800F8614 | 2 | Enemy 2 Current HP | Live actor HP in battle (confirmed). Slot stride 0x68 from Enemy 1. Enemy N = F85AC + (N-1)*0x68. Distinct from stats... |
| F8618 | 0x800F8618 | 2 | Enemy 2 Max HP | Live actor HP in battle (confirmed). Slot stride 0x68 from Enemy 1. Enemy N = F85AC + (N-1)*0x68. Distinct from stats... |
| F8674 | 0x800F8674 | 2 | Enemy 3 ID |  |
| F867C | 0x800F867C | 2 | Enemy 3 Current HP | Live actor HP in battle (confirmed). Slot stride 0x68 from Enemy 1. Enemy N = F85AC + (N-1)*0x68. Distinct from stats... |
| F8680 | 0x800F8680 | 2 | Enemy 3 Max HP | Live actor HP in battle (confirmed). Slot stride 0x68 from Enemy 1. Enemy N = F85AC + (N-1)*0x68. Distinct from stats... |
| F86D1 | 0x800F86D1 | 1 | Enemy 1 Level |  |
| F86D5 | 0x800F86D5 | 1 | Enemy 1 Strength |  |
| F86D6 | 0x800F86D6 | 1 | Enemy 1 Magic |  |
| F86D7 | 0x800F86D7 | 1 | Enemy 1 Evade |  |
| F86D8 | 0x800F86D8 | 1 | Enemy 1 IdleAnim ID |  |
| F86D9 | 0x800F86D9 | 1 | Enemy 1 DamageAnim ID |  |
| F86DB | 0x800F86DB | 1 | Enemy 1 Size |  |
| F86DC | 0x800F86DC | 1 | Enemy 1 Dexterity |  |
| F86DD | 0x800F86DD | 1 | Enemy 1 Luck |  |
| F86E4 | 0x800F86E4 | 2 | Enemy 4 Current HP | Live actor HP in battle (confirmed). Slot stride 0x68 from Enemy 1. Enemy N = F85AC + (N-1)*0x68. Distinct from stats... |
| F86E8 | 0x800F86E8 | 2 | Enemy 1 Defence |  |
| F86EA | 0x800F86EA | 2 | Enemy 1 MDefence |  |
| F86EC | 0x800F86EC | 1 | Enemy 1 Index ID |  |
| F86F0 | 0x800F86F0 | 2 | Enemy 1 Current MP |  |
| F86F2 | 0x800F86F2 | 2 | Enemy 1 Max MP |  |
| F86F4 | 0x800F86F4 | 2 | Enemy 1 Current HP (stats block) | Stats-block / secondary HP copy (spreadsheet). Not the live actor HP used for on-screen enemy health; use F85AC + (N-... |
| F86F8 | 0x800F86F8 | 2 | Enemy 1 Max HP (stats block) | Stats-block / secondary HP copy (spreadsheet). Not the live actor HP used for on-screen enemy health; use F85AC + (N-... |
| F871E | 0x800F871E | 1 | Enemy 1 Evade ID |  |
| F8720 | 0x800F8720 | 4 | Enemy 1 Gil |  |
| F8724 | 0x800F8724 | 4 | Enemy 1 EXP |  |
| F8739 | 0x800F8739 | 1 | Enemy 2 Level |  |
| F873D | 0x800F873D | 1 | Enemy 2 Strength |  |
| F873E | 0x800F873E | 1 | Enemy 2 Magic |  |
| F873F | 0x800F873F | 1 | Enemy 2 Evade |  |
| F8740 | 0x800F8740 | 1 | Enemy 2 IdleAnim ID |  |
| F8741 | 0x800F8741 | 1 | Enemy 2 DamageAnim ID |  |
| F8743 | 0x800F8743 | 1 | Enemy 2 Size |  |
| F8744 | 0x800F8744 | 1 | Enemy 2 Dexterity |  |
| F8745 | 0x800F8745 | 1 | Enemy 2 Luck |  |
| F874C | 0x800F874C | 2 | Enemy 5 Current HP | Live actor HP in battle (confirmed). Slot stride 0x68 from Enemy 1. Enemy N = F85AC + (N-1)*0x68. Distinct from stats... |
| F8750 | 0x800F8750 | 2 | Enemy 2 Defence |  |
| F8752 | 0x800F8752 | 2 | Enemy 2 MDefence |  |
| F8754 | 0x800F8754 | 1 | Enemy 2 Index ID |  |
| F8758 | 0x800F8758 | 2 | Enemy 2 Current MP |  |
| F875A | 0x800F875A | 2 | Enemy 2 Max MP |  |
| F875C | 0x800F875C | 2 | Enemy 2 Current HP (stats block) | Stats-block / secondary HP copy (spreadsheet). Not the live actor HP used for on-screen enemy health; use F85AC + (N-... |
| F8760 | 0x800F8760 | 2 | Enemy 2 Max HP (stats block) | Stats-block / secondary HP copy (spreadsheet). Not the live actor HP used for on-screen enemy health; use F85AC + (N-... |
| F8786 | 0x800F8786 | 1 | Enemy 2 Evade ID |  |
| F8788 | 0x800F8788 | 4 | Enemy 2 Gil |  |
| F878C | 0x800F878C | 4 | Enemy 2 EXP |  |
| F87A1 | 0x800F87A1 | 1 | Enemy 3 Level |  |
| F87A5 | 0x800F87A5 | 1 | Enemy 3 Strength |  |
| F87A6 | 0x800F87A6 | 1 | Enemy 3 Magic |  |
| F87A7 | 0x800F87A7 | 1 | Enemy 3 Evade |  |
| F87A8 | 0x800F87A8 | 1 | Enemy 3 IdleAnim ID |  |
| F87A9 | 0x800F87A9 | 1 | Enemy 3 DamageAnim ID |  |
| F87AB | 0x800F87AB | 1 | Enemy 3 Size |  |
| F87AC | 0x800F87AC | 1 | Enemy 3 Dexterity |  |
| F87AD | 0x800F87AD | 1 | Enemy 3 Luck |  |
| F87B4 | 0x800F87B4 | 2 | Enemy 6 Current HP | Live actor HP in battle (confirmed). Slot stride 0x68 from Enemy 1. Enemy N = F85AC + (N-1)*0x68. Distinct from stats... |
| F87B8 | 0x800F87B8 | 2 | Enemy 3 Defence |  |
| F87BA | 0x800F87BA | 2 | Enemy 3 MDefence |  |
| F87BC | 0x800F87BC | 1 | Enemy 3 Index ID |  |
| F87C0 | 0x800F87C0 | 2 | Enemy 3 Current MP |  |
| F87C2 | 0x800F87C2 | 2 | Enemy 3 Max MP |  |
| F87C4 | 0x800F87C4 | 2 | Enemy 3 Current HP (stats block) | Stats-block / secondary HP copy (spreadsheet). Not the live actor HP used for on-screen enemy health; use F85AC + (N-... |
| F87C8 | 0x800F87C8 | 2 | Enemy 3 Max HP (stats block) | Stats-block / secondary HP copy (spreadsheet). Not the live actor HP used for on-screen enemy health; use F85AC + (N-... |
| F87EE | 0x800F87EE | 1 | Enemy 3 Evade ID |  |
| F87F0 | 0x800F87F0 | 4 | Enemy 3 Gil |  |
| F87F4 | 0x800F87F4 | 4 | Enemy 3 EXP |  |
| F8809 | 0x800F8809 | 1 | Enemy 4 Level |  |
| F880D | 0x800F880D | 1 | Enemy 4 Strength |  |
| F880E | 0x800F880E | 1 | Enemy 4 Magic |  |
| F880F | 0x800F880F | 1 | Enemy 4 Evade |  |
| F8810 | 0x800F8810 | 1 | Enemy 4 IdleAnim ID |  |
| F8811 | 0x800F8811 | 1 | Enemy 4 DamageAnim ID |  |
| F8813 | 0x800F8813 | 1 | Enemy 4 Size |  |
| F8814 | 0x800F8814 | 1 | Enemy 4 Dexterity |  |
| F8815 | 0x800F8815 | 1 | Enemy 4 Luck |  |
| F8820 | 0x800F8820 | 2 | Enemy 4 Defence |  |
| F8822 | 0x800F8822 | 2 | Enemy 4 MDefence |  |
| F8824 | 0x800F8824 | 1 | Enemy 4 Index ID |  |
| F8828 | 0x800F8828 | 2 | Enemy 4 Current MP |  |
| F882A | 0x800F882A | 2 | Enemy 4 Max MP |  |
| F882C | 0x800F882C | 2 | Enemy 4 Current HP (stats block) | Stats-block / secondary HP copy (spreadsheet). Not the live actor HP used for on-screen enemy health; use F85AC + (N-... |
| F8830 | 0x800F8830 | 2 | Enemy 4 Max HP (stats block) | Stats-block / secondary HP copy (spreadsheet). Not the live actor HP used for on-screen enemy health; use F85AC + (N-... |
| F8856 | 0x800F8856 | 1 | Enemy 4 Evade ID |  |
| F8858 | 0x800F8858 | 4 | Enemy 4 Gil |  |
| F885C | 0x800F885C | 4 | Enemy 4 EXP |  |
| F8871 | 0x800F8871 | 1 | Enemy 5 Level |  |
| F8875 | 0x800F8875 | 1 | Enemy 5 Strength |  |
| F8876 | 0x800F8876 | 1 | Enemy 5 Magic |  |
| F8877 | 0x800F8877 | 1 | Enemy 5 Evade |  |
| F8878 | 0x800F8878 | 1 | Enemy 5 IdleAnim ID |  |
| F8879 | 0x800F8879 | 1 | Enemy 5 DamageAnim ID |  |
| F887B | 0x800F887B | 1 | Enemy 5 Size |  |
| F887C | 0x800F887C | 1 | Enemy 5 Dexterity |  |
| F887D | 0x800F887D | 1 | Enemy 5 Luck |  |
| F8888 | 0x800F8888 | 2 | Enemy 5 Defence |  |
| F888A | 0x800F888A | 2 | Enemy 5 MDefence |  |
| F888C | 0x800F888C | 1 | Enemy 5 Index ID |  |
| F8890 | 0x800F8890 | 2 | Enemy 5 Current MP |  |
| F8892 | 0x800F8892 | 2 | Enemy 5 Max MP |  |
| F8894 | 0x800F8894 | 2 | Enemy 5 Current HP (stats block) | Stats-block / secondary HP copy (spreadsheet). Not the live actor HP used for on-screen enemy health; use F85AC + (N-... |
| F8898 | 0x800F8898 | 2 | Enemy 5 Max HP (stats block) | Stats-block / secondary HP copy (spreadsheet). Not the live actor HP used for on-screen enemy health; use F85AC + (N-... |
| F88BE | 0x800F88BE | 1 | Enemy 5 Evade ID |  |
| F88C0 | 0x800F88C0 | 4 | Enemy 5 Gil |  |
| F88C4 | 0x800F88C4 | 4 | Enemy 5 EXP |  |
| F88D9 | 0x800F88D9 | 1 | Enemy 6 Level |  |
| F88DD | 0x800F88DD | 1 | Enemy 6 Strength |  |
| F88DE | 0x800F88DE | 1 | Enemy 6 Magic |  |
| F88DF | 0x800F88DF | 1 | Enemy 6 Evade |  |
| F88E0 | 0x800F88E0 | 1 | Enemy 6 IdleAnim ID |  |
| F88E1 | 0x800F88E1 | 1 | Enemy 6 DamageAnim ID |  |
| F88E3 | 0x800F88E3 | 1 | Enemy 6 Size |  |
| F88E4 | 0x800F88E4 | 1 | Enemy 6 Dexterity |  |
| F88E5 | 0x800F88E5 | 1 | Enemy 6 Luck |  |
| F88F0 | 0x800F88F0 | 2 | Enemy 6 Defence |  |
| F88F2 | 0x800F88F2 | 2 | Enemy 6 MDefence |  |
| F88F4 | 0x800F88F4 | 1 | Enemy 6 Index ID |  |
| F88F8 | 0x800F88F8 | 2 | Enemy 6 Current MP |  |
| F88FA | 0x800F88FA | 2 | Enemy 6 Max MP |  |
| F88FC | 0x800F88FC | 2 | Enemy 6 Current HP (stats block) | Stats-block / secondary HP copy (spreadsheet). Not the live actor HP used for on-screen enemy health; use F85AC + (N-... |
| F8900 | 0x800F8900 | 2 | Enemy 6 Max HP (stats block) | Stats-block / secondary HP copy (spreadsheet). Not the live actor HP used for on-screen enemy health; use F85AC + (N-... |
| F8926 | 0x800F8926 | 1 | Enemy 6 Evade ID |  |
| F8928 | 0x800F8928 | 4 | Enemy 6 Gil |  |
| F892C | 0x800F892C | 4 | Enemy 6 EXP |  |
| F8B38 | 0x800F8B38 | 1 | Enemy 1 LocalVar:0000 |  |
| F8B3C | 0x800F8B3C | 1 | Enemy 1 LocalVar:0020 |  |
| F8BB8 | 0x800F8BB8 | 1 | Enemy 2 LocalVar:0000 |  |
| F8BBC | 0x800F8BBC | 1 | Enemy 2 LocalVar:0020 |  |
| F8C38 | 0x800F8C38 | 1 | Enemy 3 LocalVar:0000 |  |
| F8C3C | 0x800F8C3C | 1 | Enemy 3 LocalVar:0020 |  |
| F8CB8 | 0x800F8CB8 | 1 | Enemy 4 LocalVar:0000 |  |
| F8CBC | 0x800F8CBC | 1 | Enemy 4 LocalVar:0020 |  |
| F8D38 | 0x800F8D38 | 1 | Enemy 5 LocalVar:0000 |  |
| F8D3C | 0x800F8D3C | 1 | Enemy 5 LocalVar:0020 |  |
| F8DB8 | 0x800F8DB8 | 1 | Enemy 6 LocalVar:0000 |  |
| F8DBC | 0x800F8DBC | 1 | Enemy 6 LocalVar:0020 |  |
| 10AE58 | 0x8010AE58 | 4 | World Map RNG Index |  |
| 10AE5C | 0x8010AE5C | 521 | World Map RNG Buffer |  |
| 163780 | 0x80163780 | 1 | Battle: Runnable due to pincer | 2 or greater = not runnable. there's also a lot of nice stuff back here in battle, look into it |

