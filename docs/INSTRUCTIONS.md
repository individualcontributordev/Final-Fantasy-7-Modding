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
Working image path:
Asks remaining in blackbgb S0-Main (expect 0):
Optional playtest:
Notes / Makou quirks:
```

## Done when

- Four Asks gone; jumps still present
- Evidence filled; this file pushed (no binaries)
- Say **check**

## Out of scope

- blackbg3 / blackbge
- Movie multi-disc branch
- Builder pack / CSR / Highwind
- DISKINFO spoof
