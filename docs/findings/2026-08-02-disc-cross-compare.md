# Disc 1 vs 2 vs 3 — ISO tree + code identity

**Date:** 2026-08-02  
**Confidence:** confirmed (hashes on pristine NTSC-U bins)  
**Sources:** `Final-Fantasy-7-CSR/pristine/FINALFANTASY7_D{1,2,3}.bin` via `scripts/psx_mode2_iso.py`

## Summary

Retail discs share essentially the **same game code and field/world data**. They differ mainly in **which FMV files are present**, a few disc-ID metadata files, and a D3-only `SNOVA/` set. Boot EXEs are **byte-identical** (different filenames only).

## Image sizes

| Disc | Image bytes | ISO files | Sum of file sizes |
|------|-------------|-----------|-------------------|
| 1 | 747,435,024 | 3377 | 643,280,813 |
| 2 | 732,657,408 | 3384 | 630,401,435 |
| 3 | 659,561,952 | 3370 | 567,909,827 |

Unique paths across all three: **3451**. On all three with same size: **3335**. Exclusive: D1=35, D2=46, D3=27 (almost all under `MOVIE/`).

## Code / engine (identical across discs)

| Path | Size | Result |
|------|------|--------|
| `FIELD/FIELD.BIN` | 85435 | identical SHA-256 |
| `WORLD/WORLD.BIN` | 66715 | identical |
| `INIT/KERNEL.BIN` | 22376 | identical |
| `INIT/WINDOW.BIN`, `INIT/YAMADA.BIN` | — | identical |
| `BATTLE/*` (7 files) | — | identical |
| `MENU/*` (26) | — | identical |
| `MAGIC/*` (318) | — | identical |
| `SOUND/*`, `STARTUP/*` | — | identical |
| `ENEMY1`–`ENEMY6`, `STAGE1`/`2`, `MINI` | — | identical |
| Boot EXE body | 397312 | **identical** on all discs |

Boot **filenames** differ; contents do not:

- D1 `SYSTEM.CNF` → `SCUS_941.63`
- D2 → `SCUS_941.64`
- D3 → `SCUS_941.65`

## FIELD maps

- Each disc: **787** `.DAT` / `.MIM` / `.BSX`
- Full `FIELD/*` hash pass: **2373/2374 identical**
- Only difference found: `FIELD/TUNNEL_6.MIM` (same size 86147; D1 hash ≠ D2/D3). Likely a one-file retail variance, not a second engine.

## What actually differs

1. **`MOVIE/` FMV set** — dominant exclusive bytes (opening/mid/end movies split by disc). D3 ending cluster alone is large (`ENDING2E.MOV` ~164 MB).
2. **`MINT/DISKINFO.CNF`** — `DISK0001` / `DISK0002` / `DISK0003` (+ short JP text).
3. **`MINT/MOVIE_ID.BIN`** — different size/hash per disc (movie index for that disc’s set).
4. **D3-only `SNOVA/`** (~1.1 MB) — Super Nova related assets.
5. A few movies shared by two discs only (e.g. Gold Saucer set on D1+D3, not D2).

## Capacity sketch (union of unique files)

| | Bytes |
|--|------:|
| Union all files | ~1,230,571,707 (~1.15 GiB) |
| Union movie-ish | ~973,700,145 |
| Union non-movie | ~256,871,562 |

Non-movie payload (~257 MB) fits easily on one CD image; **full FMV union does not**. A single-disc build without FMVs (or with heavily trimmed/replaced video) is plausible from a storage standpoint; shipping **all** retail movies on one disc is not.

## Implications for a “no disc-swap” pack

**Feasible in principle** for gameplay code: one disc can carry the shared FIELD/WORLD/BATTLE/INIT/MENU stack plus one boot EXE.

**Still required for a real pack (not done here):**

1. Disc-change field scripts / world events that prompt “insert disc N”.
2. Whatever reads `MINT/DISKINFO.CNF` / disc id (and save disc marking).
3. Missing-movie handling when a cutscene id isn’t on the disc (`MOVIE_ID` + players).
4. ISO rebuild (current tools are in-place layer patchers, not multi-disc mergers).
5. Hardware/emulator edge cases (PS1 multi-disc save compatibility).

## Method

ISO9660 walk + per-file SHA-256 of user data (Mode 2/2352) for trees and code paths. No sector EDC compared.
