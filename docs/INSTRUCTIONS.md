# Task: No-swap prototype — remove Ask for disc in blackbgb (pristine)

Operational handoff. Agent overwrites this file and pushes.
You: git pull --ff-only, edit, evidence, commit+push. Say **check**.

## Goal

On **Unmodified Disc 1** only, make `blackbgb` (#103) stop prompting for disc 2/3
but still jump to the destination maps. Smallest possible script edit.

Prior: `docs/findings/2026-08-02-noswap-blackbgb-hub-branches.md`

## Edit plan (four sites only)

In `blackbgb` → `init` → **S0 - Main**, **delete** (or skip) each:

1. Gate `Var[3][136]` bit 5 → ~~Ask for disc 3~~ → keep music/wait → jump **las0_1 #744**
2. Gate `Var[13][82]` bit 6 → save UI optional → ~~Ask for disc 3~~ → keep → jump **las0_1 #744**
3. Gate `Var[3][134]` bit 2 → ~~Ask for disc 2~~ → keep bit/music → jump **lost2 #634**
4. Gate `Var[3][136]` bit 4 → save UI optional → ~~Ask for disc 2~~ → keep → jump **lost2 #634**

Do **not** change jump targets, save prompts, or the multi-disc movie branch yet.

## Steps

1. git pull --ff-only
2. Copy pristine D1 → working image (e.g. workspace/iso-extract/ff7_d1_noswap_proto.bin)
3. Open working image in Makou → map **blackbgb** → init → S0 - Main
4. Apply the four Ask removals; save the field back into the working ISO
5. Re-open script and confirm no `Ask for disc` remains in S0-Main
6. Optional DS: if you can force a gate flag / use a late save, confirm no disc dialog and map jump still runs
7. Evidence: short note + optional before/after snippet. **Do not commit .bin**
8. Leave working path in Evidence so we can diff FIELD/blackbgb next turn

## Evidence

```
Working image path: D:\projects\Final-Fantasy-7-Modding\workspace\iso-extract\ff7_d1_noswap_re.bin
Asks remaining in blackbgb S0-Main (expect 0):
Optional playtest:
Notes / Makou quirks:
```

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
	Goto label 15
	Bit 5 OFF in Var[3][136]
	Label 15
	Wait 4 frame
	Goto label 11
	Ask for disc 3
	Label 11
	Play music #2
	Wait 8 frame
	Jump to map las0_1 (#744) (X=-7, Y=-917, triangle ID=243, direction=228)
	Goto label 8
Label 3
If Var[13][82] bitON 6 (else goto label 5)
	Goto label 16
	Bit 6 OFF in Var[13][82]
	Label 16
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
	Goto label 12
	Ask for disc 3
	Label 12
	Play music #2
	Wait 8 frame
	Jump to map las0_1 (#744) (X=-7, Y=-917, triangle ID=243, direction=228)
	Goto label 8
Label 5
If Var[3][134] bitON 2 (else goto label 6)
	Goto label 17
	Bit 2 OFF in Var[3][134]
	Label 17
	Wait 4 frame
	Goto label 13
	Ask for disc 2
	Label 13
	Wait 8 frame
	Bit 1 ON in Var[3][137]
	Play music #3
	Wait 8 frame
	Jump to map lost2 (#634) (X=-259, Y=5042, triangle ID=113, direction=0)
	Goto label 8
Label 6
If Var[3][136] bitON 4 (else goto label 8)
	Goto label 18
	Bit 4 OFF in Var[3][136]
	Label 18
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
	Goto label 14
	Ask for disc 2
	Label 14
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


## Done when

- Four Asks gone; jumps still present
- Evidence filled; this file pushed (no binaries)
- Say **check**

## Out of scope

- blackbg3 / blackbge
- Movie multi-disc branch
- Builder pack / CSR / Highwind
- DISKINFO spoof
