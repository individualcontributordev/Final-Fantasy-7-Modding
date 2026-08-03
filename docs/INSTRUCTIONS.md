# Task: No-swap — next after combined D1 work bin PASS

## Done (DuckStation)

- Makou Ask-for-disc removal: PASS
- Supernova v3 (SNOVA raw-copy + BATTLE.X 17 LBA remap): PASS
- **Combined** Ask-fixed work bin + SNOVA v3: PASS
  - Work image (local only): workspace/iso-extract/ff7_d1_noswap_work.bin
  - Backup before inject: workspace/iso-extract/ff7_d1_noswap_work.pre_snova.bak
- Findings:
  - docs/findings/2026-08-03-noswap-makou-ask-ds-pass.md
  - docs/findings/2026-08-03-noswap-snova-injector.md
  - docs/findings/2026-08-03-noswap-supernova-ds-pass.md
  - docs/findings/2026-08-03-noswap-combined-ds-pass.md

Engine MOVIE/DSKCG stubs stay abandoned.

## Goal this turn (pick one; say check with choice if unsure)

Preferred order unless you want pack ship now:

1. **Document repro recipe** for Clean Unmodified no-swap D1 (Makou list + inject command)
   so it is rebuildable without chat memory.
2. **CSR-base path:** whitelist manip-critical D2/D3 movies for CSR no-swap
   (see docs/findings/2026-08-03-noswap-full-run-scope.md).
3. **Console smoke** on combined bin (optional; not blocking docs).
4. **Pack wiring** toward builder only after recipe is solid.

## If continuing on 1 (default)

No playtest required this turn. Agent should turn combined PASS into a short
mods/no-swap README + field list pointer when you say check without new FAIL.

## Evidence (if you ran more smoke)

    Combined still OK: yes/no
    Extra maps/battles:
    Console: untested / notes
    Want next: recipe / CSR movies / pack / other

Say check.

## Notes

- Do not commit .bin images
- Inject refuses double SNOVA; restore bak or pristine+Makou then inject once
