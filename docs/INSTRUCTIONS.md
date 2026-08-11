# Task: Disc1 to disc2 break — CSR + Single-disc only (no CSR+)

## Locked in

| Build | Disc1 to disc2 break |
|-------|----------------------|
| CSR multi-disc (swap D2) | **OK** — break scene as expected |
| Unmodified / CSR early Midgar | OK |
| CSR + CSR+ + Single-disc | black + D2 music, no break (prior report) |

CSR base is not the bug. Next isolate **Single-disc** with movies pack on.

## Why Build C

On CSR + CSR+ + SD, auto pack `single-disc-csr-manip-movies` is **off**
(because `unlessAddonIdPrefix: csr-plus-scene-`). That pack seeds D2 FMVs on D1.
LOST2 force MAPJUMP to cos_btm2 is already in single-disc v0.1.6.

Build C = CSR + Single-disc, **CSR+ off** so movies auto-includes.

## What you do

1. Hard-refresh builder
2. Base: **CSR**
3. Mods: **Single-disc only** (CSR+ off, Fanfare off)
4. Build Disc 1
5. APPLIED.txt must show:
   - single-disc-on-csr-v0.1.6 (or current)
   - **single-disc-csr-manip-movies-...** (auto)
   - endings parts OK
   - **no** csr-plus-scene-*
6. Quit DuckStation fully; **no CE**; prefer in-game save before transition (no savestate)
7. Run disc1 to disc2 / break path

**Expect:** break / cos_btm2 like multi-disc CSR, not black + music only.

## Evidence (paste)

```
APPLIED (confirm movies pack YES, CSR+ NO):
Disc1 to disc2: OK BREAK / BLACK+MUSIC / FREEZE / OTHER
Break / cos_btm2: YES / NO
Playable after: YES / NO
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say **check**.

If C is OK: fix is allow manip-movies with CSR+ (or equivalent FMV on full stack).
If C still fails: bug is Single-disc core / LOST2 routing, not CSR+ gate.
