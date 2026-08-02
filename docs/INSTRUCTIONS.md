# Task: No-swap prototype — fix gate bits; only skip Ask

Operational handoff. Agent overwrites this file and pushes.
You: git pull --ff-only, fix Makou script, evidence, commit+push. Say **check**.

## Goal

Same working image: neutralize the four `Ask for disc` ops in **blackbgb**
S0-Main **without** skipping the `Bit … OFF` clears (or save setup).

Prior: `docs/findings/2026-08-02-noswap-blackbgb-ask-skip-proto.md`

Working image (keep using this path):
`workspace/iso-extract/ff7_d1_noswap_re.bin`

## Bug in current edit

Each branch does roughly:

```
Goto label 15
Bit N OFF          ← dead (bad)
Label 15
...
Goto label 11
Ask for disc N     ← dead (good)
Label 11
jump ...
```

**Fix:** Bit OFF must run. Only Ask must be skipped/removed.

## Preferred fix (clean)

In `blackbgb` → `init` → S0-Main, **delete** the four `Ask for disc` lines only.
Remove the extra Goto/Label pairs added for skipping if they are no longer needed.
Restore normal flow:

1. bit-5 path: Bit 5 OFF → wait → (no ask) → music → jump **las0_1 #744**
2. bit-6 path: Bit 6 OFF → cloud/save UI unchanged → (no ask) → music → **las0_1 #744**
3. bit-2 path: Bit 2 OFF → wait → (no ask) → flags/music → **lost2 #634**
4. bit-4 path: Bit 4 OFF → cloud/save UI unchanged → (no ask) → flags/music → **lost2 #634**

## Steps

1. git pull --ff-only
2. Open working ISO in Makou → blackbgb → init → S0-Main
3. Apply preferred fix (delete Asks + clean dead Gotos if easy)
4. Save field into the same working ISO
5. Paste the four disc branches (or full disc section) under Evidence
6. Confirm in paste: each gate still has **Bit … OFF** before the jump; **no**
   live Ask on the fall-through path
7. Commit this file only (no .bin)

## Evidence

```
Working image path:
Ask for disc still present as dead code? (yes/no):
Bit OFF runs on all four disc branches? (yes/no):
```

### Disc section paste (after fix)

```
(paste S0-Main from first disc gate through lost2/las0_1 jumps)
```

## Done when

- Asks not executed; Bit OFFs execute; jumps intact
- Evidence pushed; say **check**

## Out of scope

- Builder pack (next turn after fix verifies)
- blackbg3 / blackbge / multi-disc movie
- CSR / Highwind


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
	Label 15
	Bit 5 OFF in Var[3][136]
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
	Label 16
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
	Label 17
	Bit 2 OFF in Var[3][134]
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
	Label 18
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

# latest

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
	Play music #2
	Wait 8 frame
	Jump to map las0_1 (#744) (X=-7, Y=-917, triangle ID=243, direction=228)
	Goto label 8
Label 5
If Var[3][134] bitON 2 (else goto label 6)
	Bit 2 OFF in Var[3][134]
	Wait 4 frame
	Wait 8 frame
	Bit 1 ON in Var[3][137]
	Play music #3
	Wait 8 frame
	Jump to map lost2 (#634) (X=-259, Y=5042, triangle ID=113, direction=0)
	Goto label 8
Label 6
If Var[3][136] bitON 4 (else goto label 8)
	Goto label 18
	Label 18
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
