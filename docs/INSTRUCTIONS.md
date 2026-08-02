# Task: No-swap — dump blackbgb S0-Main disc branches

Operational handoff. Agent overwrites this file and pushes.
You: git pull --ff-only, fill Evidence, commit+push. Say **check**.

## Goal

Document the **four** `Ask for disc` sites in pristine **blackbgb (#103)**
`init` / **S0 - Main**, including the condition bits and the map jump after each.
That script is the live disc-change hub on D1.

Prior: `docs/findings/2026-08-02-noswap-ask-for-disc-inventory.md`

## Preconditions

- Pristine D1 in Makou; open map **blackbgb** (field 103)
- Read-only — do not save script edits yet

## Steps

1. git pull --ff-only
2. Makou → blackbgb → group **init** → script **S0 - Main**
3. For each Ask line (**43, 64, 73, 95**), copy the surrounding branch:
   - gating `If` / Var bits / GameMoment
   - save prompt if any
   - `Ask for disc N`
   - waits / music
   - **Jump to map** (name + id + coords if shown)
   - any `Var[13][0] = disc` style writes
4. Paste under Evidence (four blocks or one annotated dump of the whole S0-Main
   disc-related section). Commit **this file only** (no bins; no screenshot files
   under docs/ — paste text).

## Evidence

### blackbgb / init / S0 - Main

If Var[3][136] bitON 7 (else goto label 1)
	Play music #0
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=1, param2=127, param3=0, param4=0, param5=0)
	Play a sound effect on channel #1 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Play a sound effect on channel #2 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Play a sound effect on channel #3 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Play a sound effect on channel #4 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Volume control (channel #1) [param1: volume] (param1 (8-bit)=127, param2=0, param3=0, param4=0, param5=0)
	Volume control (channel #2) [param1: volume] (param1 (8-bit)=127, param2=0, param3=0, param4=0, param5=0)
	Volume control (channel #3) [param1: volume] (param1 (8-bit)=127, param2=0, param3=0, param4=0, param5=0)
	Volume control (channel #4) [param1: volume] (param1 (8-bit)=127, param2=0, param3=0, param4=0, param5=0)
	Tempo control (channel #1) (param1 (8-bit)=0, param2=0, param3=0, param4=0, param5=0)
	Tempo control (channel #2) (param1 (8-bit)=0, param2=0, param3=0, param4=0, param5=0)
	Tempo control (channel #3) (param1 (8-bit)=0, param2=0, param3=0, param4=0, param5=0)
	Tempo control (channel #4) (param1 (8-bit)=0, param2=0, param3=0, param4=0, param5=0)
	Set the music #1 for next battle
	Bit 7 OFF in Var[3][136]
	Show menu HP to 1 (parameter Var[3][0])
	Start battle #468
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=255, param2=0, param3=0, param4=0, param5=0)
	Wait 80 frame
	Play music #0
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=0, param2=127, param3=0, param4=0, param5=0)
	Jump to map roadend (#226) (X=-1243, Y=-34, triangle ID=50, direction=0)
Label 1
If Var[13][91] bitON 2 (else goto label 2)
	Bit 7 ON in Var[3][136]
	Bit 2 OFF in Var[13][91]
	Restores full HP and MP of every available character and removing status effects
	Set the window #0 mode: No Background/Border (prevent the closing of the window by the player)
	Set the window #1 mode: Normal (prevent the closing of the window by the player)
	Set the window #2 mode: Normal (prevent the closing of the window by the player)
	Set the window #3 mode: Transparent Background (prevent the closing of the window by the player)
	Wait 1 frame
	Execute script #3 in extern group byke (No6) (priority 6/6) - Only if the script is not already running
	Execute script #3 in extern group bcloud (No7) (priority 6/6) - Only if the script is not already running
	Create window #0 (X=16, Y=8, Width=287, Height=57)
	Displays the dialog "Control the bike with the ¶[Directi...uck from the Shinra Pursuit Troops." in the window #0
Label 2
If Var[3][136] bitON 5 (else goto label 3)
	Bit 5 OFF in Var[3][136]
	Wait 4 frame
	Ask for disc 3
	Play music #2
	Wait 8 frame
	Jump to map las0_1 (#744) (X=-7, Y=-917, triangle ID=243, direction=228)
	Goto label 8
Label 3
If Var[13][82] bitON 6 (else goto label 5)
	Bit 6 OFF in Var[13][82]
	Execute script #4 in extern group cloud (No5) (priority 6/6) - Only if the script is not already running
	Wait 16 frame
	Create window #1 (X=70, Y=125, Width=180, Height=73)
	Ask Question "Save the game to this point on the memory card? Yes No" in the window #1 (and put selected answer in Var[5][0]) first line=2, last line=3
	Restores full HP and MP of every available character and removing status effects
	If Var[5][0] == 2 (else goto label 4)
		Wait 4 frame
		Bit 5 ON in Var[3][136]
		Var[13][0] = 3 (8 bit)
		Show menu Save (parameter 0)
	Label 4
	Bit 5 OFF in Var[3][136]
	Wait 4 frame
	Ask for disc 3
	Play music #2
	Wait 8 frame
	Jump to map las0_1 (#744) (X=-7, Y=-917, triangle ID=243, direction=228)
	Goto label 8
Label 5
If Var[3][134] bitON 2 (else goto label 6)
	Bit 2 OFF in Var[3][134]
	Wait 4 frame
	Ask for disc 2
	Wait 8 frame
	Bit 1 ON in Var[3][137]
	Play music #3
	Wait 8 frame
	Jump to map lost2 (#634) (X=-259, Y=5042, triangle ID=113, direction=0)
	Goto label 8
Label 6
If Var[3][136] bitON 4 (else goto label 8)
	Bit 4 OFF in Var[3][136]
	Execute script #3 in extern group cloud (No5) (priority 6/6) - Only if the script is not already running
	Wait 16 frame
	Create window #1 (X=70, Y=125, Width=180, Height=73)
	Ask Question "Save the game to this point on the memory card? Yes No" in the window #1 (and put selected answer in Var[5][0]) first line=2, last line=3
	If Var[5][0] == 2 (else goto label 7)
		Wait 4 frame
		Bit 2 ON in Var[3][134]
		Var[13][0] = 2 (8 bit)
		Show menu Save (parameter 0)
	Label 7
	Bit 2 OFF in Var[3][134]
	Wait 4 frame
	Ask for disc 2
	Wait 8 frame
	Bit 1 ON in Var[3][137]
	Play music #3
	Wait 8 frame
	Jump to map lost2 (#634) (X=-259, Y=5042, triangle ID=113, direction=0)
Label 8
If Var[3][131] bitON 2 (else goto label 9)
	Deactivate the movability of the playable character
	Disables access to the main menu
	Fades the screen to the colour RGB(0, 0, 0) (speed=0, type=0)
	Volume transitions (channel #1) [param1: transition time, param2: target volume] (param1 (8-bit)=16, param2=0, param3=0, param4=0, param5=0)
	Volume transitions (channel #2) [param1: transition time, param2: target volume] (param1 (8-bit)=16, param2=0, param3=0, param4=0, param5=0)
	Volume control (channel #4) [param1: volume] (param1 (8-bit)=16, param2=0, param3=0, param4=0, param5=0)
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=16, param2=0, param3=0, param4=0, param5=0)
	Wait 6 frame
	Play a sound effect on channel #1 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Play a sound effect on channel #2 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Play a sound effect on channel #3 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Volume transitions (channel #1) [param1: transition time, param2: target volume] (param1 (8-bit)=1, param2=127, param3=0, param4=0, param5=0)
	Volume transitions (channel #2) [param1: transition time, param2: target volume] (param1 (8-bit)=1, param2=127, param3=0, param4=0, param5=0)
	Volume control (channel #4) [param1: volume] (param1 (8-bit)=1, param2=127, param3=0, param4=0, param5=0)
	Play music #0
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=1, param2=127, param3=0, param4=0, param5=0)
	Set next movie: rcktfail (disc 1), rckethit1 (disc 2), No45 (disc 3)
	Play movie
	Wait 3 frame
	Lock music
	Jump to map rktsid (#558) (X=-41, Y=409, triangle ID=85, direction=240)
	Goto label 10
Label 9
If $GameMoment == 638 (else goto label 10)
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=96, param2=0, param3=0, param4=0, param5=0)
	Wait 48 frame
	Play music #0
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=1, param2=0, param3=0, param4=0, param5=0)
	Wait 4 frame
	Aerith not available
	Show menu Remove Aerith's Materia
	Jump to map gninn (#522) (X=-119, Y=240, triangle ID=34, direction=255)
Label 10
Return


#### Branch A (Ask line 43) — disc ?

```
(paste)
```

#### Branch B (Ask line 64) — disc ?

```
(paste)
```

#### Branch C (Ask line 73) — disc ?

```
(paste)
```

#### Branch D (Ask line 95) — disc ?

```
(paste)
```

### Quick table

| Line | Ask disc | Jump map (id) | Notes |
|------|----------|---------------|-------|
| 43 | | | |
| 64 | | | |
| 73 | | | |
| 95 | | | |

## Done when

- All four branches pasted with jump targets
- Pushed; say **check**

## Out of scope

- Editing opcodes / shipping packs
- blackbg3 / blackbge deep dump (after hub is locked)
- CSR / Highwind
