# Task: No-disc-swap — console smoke continued

## Done (console burn)

- ImgBurn verify: PASS
- **Boot to title: PASS**
- **New game to first field: PASS**
- Disc-ask hub: not reported yet
- Supernova: not reported yet

Finding: docs/findings/2026-08-03-noswap-console-boot-pass.md

## Still useful if easy

| Check | Why |
|-------|-----|
| Former disc-ask path | Confirms Makou Ask removal on optical |
| Supernova (late save) | Confirms SNOVA+BATTLE.X on optical / high LBA |

Not blocking for "disc boots and plays early game."

## Evidence (optional more smoke)

    Disc-ask: PASS/FAIL/not tested
    Supernova: PASS/FAIL/not tested
    Notes:

Say check. Or stop here and call early-game console gate PASS.

## Notes

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
