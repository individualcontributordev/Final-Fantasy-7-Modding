# Task: blackbgb (#103) - DELETE Ask-for-disc (no JMPF / forward)

## Bug

Field **103 / BLACKBGB** (post-Hojo disc hub) used a bad single-disc edit:

- **Wrong:** replace Ask-for-disc with **JMPF+0** (Makou shows this as **forward 1 byte(s)**)
- That is not a real NOP. Script flow breaks - disc 3 field (las0_1 #744) fails to load after Hojo.

## Correct edit (Makou)

Open the CSR single-disc work image (or CSR D1 base + rebuild pack after):

1. Field map **blackbgb** (#103)
2. Group **init** - script **S0 - Main**
3. Find All: **Ask for disc**
4. There should be **four** asks (2x disc 2, 2x disc 3)
5. For **each** of the four:
   - Select the **Ask for disc N** instruction only
   - **Delete** it (do **not** insert JMPF / forward N bytes)
6. **Keep** everything else in those branches:
   - Bit ON/OFF gates
   - Wait
   - **Play music**
   - Jump to map (**lost2 #634** or **las0_1 #744**)
   - Optional save-menu setup on the save branches

### Good shape (each disc branch)

    ... gate / Bit OFF ...
    Wait ...
    # Ask for disc  - DELETED (gone, not replaced)
    Play music ...
    ...
    Jump to map las0_1 or lost2 ...

### Bad shape (what we shipped by mistake)

    ... gate ...
    forward 1 byte(s)     # JMPF+0 - REMOVE THIS
    Play music ...          # may never run correctly

7. Save the map in Makou.
8. Rebuild / refresh the single-disc-on-csr pack layer for FIELD/BLACKBGB.DAT (same process as other field ships).
9. Playtest: after Hojo -> hub -> should land **las0_1** (Northern Cave) with music, no insert-disc, no freeze.

## Do not

- Do **not** leave forward 1 byte(s) / JMPF+0 anywhere in this script.
- Do **not** delete Bit OFF / Play music / Jump.
- Do **not** use FIELD.BIN DSKCG engine stubs (abandoned).

## Reference

- Hub branches: docs/findings/2026-08-02-single-disc-blackbgb-hub-branches.md
- Correct prototype: docs/findings/2026-08-02-single-disc-blackbgb-ask-skip-proto.md (prefer **delete** Ask)
- Past DS pass: docs/findings/2026-08-03-single-disc-makou-ask-ds-pass.md

## Notes for check

    After Hojo hub:
    las0_1 loads:
    Music:
    Ask for disc:
    Other maps:
