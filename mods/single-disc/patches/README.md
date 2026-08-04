# Single-disc patches / RE notes

## Playable path (use this)

1. FIELD *.DAT (Makou): remove Ask-for-disc (DSKCG) opcodes; keep control flow.
2. ISO + BATTLE.X: scripts/inject_snova_d3_to_d1.py v3
   - Raw-copy D3 SNOVA/ (570 sectors)
   - Remap 17 hardcoded LBAs in decompressed BATTLE/BATTLE.X, recompress gzipps

## Abandoned (do not ship)

| Approach | Result |
|----------|--------|
| FIELD.BIN MOVIE (0xF9) entry stub | Softlock new game intro |
| FIELD.BIN DSKCG (0x0E) entry stub | No Ask UI; disc-change black/silent |
| SNOVA files only (no BATTLE.X LBA patch) | Supernova SFX then battle freeze |

scripts/stub_field_movie_dskcg.py kept for RE only.

## BATTLE.X LBA table (NTSC-U decompressed)

- 0x48D78 + 8*n: SNOVA0..SNOVA15 (lba, padded_size)
- 0x4F5A8: LASBOSS3 (lba, padded_size)
- Retail D3 LBAs start SNOVA0=127254, LASBOSS3=127101

## Findings index

- Ask inventory: docs/findings/2026-08-02-single-disc-ask-for-disc-inventory.md
- SNOVA/BATTLE: docs/findings/2026-08-03-single-disc-snova-injector.md
- Combined DS: docs/findings/2026-08-03-single-disc-combined-ds-pass.md
- FMV wait: docs/findings/2026-08-03-single-disc-fmv-wait-vs-stream.md

- csr-manip-movie-whitelist.md — CSR-alone single-disc D2/D3 movie copy list (working)
