# Task: No-disc-swap — load save asks for disc 2

## Report

0.1.0 burned pack: loading a save asks for disc 2.

## Analysis (this machine)

Applied 0.1.0 has Ask removed on BLACKBGB / BLACKBG3 / BLACKBGE.
DISKINFO still DISK0001. SAVEMENU unchanged.

So this is almost certainly **save file disc ID = 2**, not missing field Ask edits.

Finding: docs/findings/2026-08-04-noswap-load-save-asks-disc2.md

## Please confirm

    Ask appears: at save list / after load confirm / after field enters
    Save was made on: retail D2 / D2 image / this D1 pack / unknown
    Approximate story point:

## Workarounds now

1. New game on the no-swap D1 disc (or load a pure D1 save)
2. Edit memcard save disc number to 1
3. Continue playtest from a D1-origin save

## If we need pack fix

Next RE: SAVEMENU / load path ignore save disc field so any progress save loads on D1-only.

## Evidence

    Where ask shows:
    Save origin:
    Notes:

Say check.
