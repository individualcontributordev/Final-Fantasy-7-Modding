# Task: No-disc-swap — ioslake3 missing FMV (not freeze)

## Report

Map **ioslake3** S0 Main: Bugenhagen idle/animated, FMV should play and does not.
Not a freeze hardlock (per operator).

Script not yet on this clone — push dump when ready.

## Decision for Clean no-disc-swap

Default product policy: **leave Play movie** (wrong/missing FMV OK if story continues).

Trim in Makou **only if**:
- the map never advances after the movie wait, or
- you want polish (skip empty stare) and will rebuild the pack layer

If trimming: delete Play movie (+ optional Set next movie); **keep Jump** and bits.

## Please confirm

    ioslake3 eventually continues after wait: yes / no / unknown
    Want pack trim for polish: yes / no
    Script dump pushed: path or pending

Say check.

- Do not commit .bin images
- Pack is D1-only; D2/D3 layers not required for this add-on
- Leave CSR movie copies out for now (wrong FMV wait finding)

If $GameMoment == 1398 (else goto label 1)
	Execute script #3 in group Untitled (No5) (priority 6/6) - Waiting for end of execution to continue
	Wait 3 frame
	Set next movie: No57 (disc 1), loslake1 (disc 2), No57 (disc 3)
	Execute script #4 in extern group mf (No1) (priority 6/6) - Only if the script is not already running
	Play movie
	Execute script #6 in extern group Untitled (No6) (priority 6/6) - Only if the script is not already running
	Execute script #6 in group Untitled (No5) (priority 6/6) - Waiting for end of execution to continue
	Set next movie: No58 (disc 1), lslmv (disc 2), No58 (disc 3)
	Execute script #3 in extern group mf (No1) (priority 6/6) - Only if the script is not already running
	Play movie
	Wait 10 frame
	Execute script #7 in group Untitled (No5) (priority 6/6) - Waiting for end of execution to continue
	Wait 20 frame
	Jump to map loslake1 (#637) (X=643, Y=-324, triangle ID=19, direction=176)
Label 1
Goto label 1
