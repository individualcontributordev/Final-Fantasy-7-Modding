# Instructions

Operational handoff. Agent overwrites this file and pushes.

---

## Status: idle (no-swap hub RE done)

### Done (pristine D1 blackbgb)

- Findings: docs/findings/2026-08-02-noswap-*.md
- Working image: workspace/iso-extract/ff7_d1_noswap_re.bin
- S0-Main: four Ask-for-disc removed; gate Bit OFF kept; jumps lost2 / las0_1
- DuckStation: disc prompt skip worked

### Next

Ship a **builder pack** (FIELD add-on) from **Final-Fantasy-7-CSR** — not an engine mod here:

1. git pull --ff-only in **CSR**
2. Open CSR docs/INSTRUCTIONS.md
3. Diff working bin vs pristine -> pack no-swap-blackbgb-hub-v0.1.0 on **clean**
4. Say **check** when the pack is pushed

Keep the working .bin for that path; do not commit bins.
