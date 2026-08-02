# Instructions

Operational handoff. Agent overwrites this file and pushes.

---

## Status: idle (no-swap RE complete for hub)

### Done (pristine D1 blackbgb hub)

- Ask inventory + hub branches documented under `docs/findings/2026-08-02-noswap-*.md`
- Working edit: `workspace/iso-extract/ff7_d1_noswap_re.bin`
- S0-Main: four `Ask for disc` removed; gate Bit OFF kept; jumps to lost2 / las0_1
- DuckStation: disc prompt skip observed working

### Next (other machine)

Ship FIELD pack from **Final-Fantasy-7-CSR** (Makou add-ons live there):

1. `git pull --ff-only` in **CSR**
2. Open **CSR** `docs/INSTRUCTIONS.md`
3. Diff working bin vs pristine → `no-swap-blackbgb-hub-v0.1.0` on **clean**
4. Say **check** in chat when pushed

Keep the working `.bin` available for that path (do not commit bins here).
