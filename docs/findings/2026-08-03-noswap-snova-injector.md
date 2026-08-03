# Finding: D3 SNOVA inject onto D1 (Mode2 grow)

**Date:** 2026-08-03
**Status:** v2 offline OK; v1 in-game FAIL; v2 playtest pending

## Summary

Supernova assets live only on retail D3 under SNOVA/ (17 files, ~1.15 MB).
D1 root has padding for one extra directory record. Image grows +570 sectors.

## Playtest v1 (user-data rewrite)

**FAIL (DuckStation):** Supernova SFX audible, then battle frozen; after SFX ends
music continues but battle stays frozen.

v1 wrote user payloads with cloned headers and zero EDC/ECC. Audio path
could still run; effect/GPU completion likely choked on bad sectors.

## Tool v2 (raw-copy)

mods/no-swap/scripts/inject_snova_d3_to_d1.py

- D3 SNOVA dir LBA 127100 is contiguous for 570 sectors (dir + all files)
- memcpy full Mode2 sectors from D3 (keeps subheader + EDC/ECC)
- Fix MSF (bytes 12-14) for new LBAs only
- Remap LBAs inside SNOVA directory user; zero EDC on dir sector only
- Patch root dir, L/M path tables, PVD size

Offline:

    D3 SNOVA raw block LBA 127100+570 files=17
    grow sectors 317787 -> 318357
    SNOVA0 sector sub+payload+edc match D3: True
    verify: all SNOVA files match D3

## Next

Retest Supernova on v2 image. If still FAIL, look beyond ISO integrity
(battle effect waiter / disc-id checks) — not more file copies (only
SNOVA + huge ending movies are D3-only besides SCUS).
