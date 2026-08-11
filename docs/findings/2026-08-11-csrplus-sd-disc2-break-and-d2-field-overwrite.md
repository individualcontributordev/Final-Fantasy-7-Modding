# Finding: CSR+SD playtest — disc2 break black screen + “CSR trims gone”

**Date:** 2026-08-11  
**Stack:** CSR + CSR+ + Single-disc Disc 1 (no Cheat Engine)  
**Evidence:** `docs/INSTRUCTIONS.md` (DuckStation CD logs + human notes)

## Confirmed OK (this session)

| Build | Result |
|-------|--------|
| Unmodified D1 | OK early path |
| CSR D1 only | OK early path |
| **CSR multi-disc D1 then swap to D2** | **OK — break scene loads as expected** |
| CE off | earlier Midgar freezes likely CE |

So **CSR base disc1 to disc2 break is fine**. Failure is only on the one-disc stack (and/or CSR+ suppressing manip-movies).


## Report on full stack

1. Some **slow loads** (FPS 0 briefly, then recovers ~30).
2. After **Jenova / spiral hut**, CSR-style trims look **missing**.
3. **Disc1→2**: black screen, **disc 2 music**, **no CSR break** (expected cos_btm2 / break, got “regular” D2 start feel).

## Log decode (not a hard softlock)

DuckStation sectors → ISO LBA = sector − 150:

| DS sector | LBA | File |
|-----------|-----|------|
| ~109397 | 109247 | `FIELD/LOSIN2.BSX` |
| 126991 | 126841 | `FIELD/CLOUD.BCX` |
| 126999 | 126849 | `FIELD/BALLET.BCX` |
| 127029 | 126879 | `FIELD/FIELD.TDB` |

Long seek (~340 ms) then party BCX loads = hitch during field/model load. FPS returns. Not the same class as post-Hojo DSKCG hang.

## Why CSR trims “disappear” near Cosmo / disc2 gate

Single-disc **intentionally replaces** several D1 fields with **CSR Disc 2** scripts (prefer/merge). On CSR+SD:

| Field | CSR D1 | CSR+SD |
|-------|--------|--------|
| COS_BTM | CSR D1 | **= CSR D2** |
| COS_BTM2 | CSR D1 | **= CSR D2** |
| WHITE1 | CSR D1 | **= CSR D2** |
| LOST2 | CSR D1 | D2-based + IFUW force (v0.1.6) |
| BLACKBGB | CSR D1 | Ask/DSKCG stripped (still on D1) |

Any **D1-only CSR trim** on those maps is overwritten by the D2 field copy. That is single-disc design (run D2 maps on one disc), not CE.

NVDUN* (Jenova crater tunnels on D1) still match CSR D1 in the hash pass — “spiral hut” feel may be **COS_*** / **LOST*** / **WHITE*** after the crater, not NVDUN.

## Disc1→2 break path (bytes)

1. **BLACKBGB** → MAPJUMP **lost2 (#634)** (DSKCG removed on SD).
2. **LOST2** (SD): IFUW force present; **MAPJUMP cos_btm2 (#526)** in init.
3. **COS_BTM2** on SD **equals CSR D2** (good baseline for break).

So the **script force from v0.1.6 is in the layer**. User still got black + D2 music without clear break → likely **movie / stream / timing**, not missing MAPJUMP byte.

## CSR+ suppresses Single-disc movies

`single-disc-csr-manip-movies-v0.1.2` autoInclude:

```json
"unlessAddonIdPrefix": "csr-plus-scene-"
```

With **CSR+ on**, manip-movies **does not auto-apply**. Endings still do.

Manip-movies is what seeds/aliases D2-related FMVs onto D1 (CANONON, etc.). Break / Cosmo path without that pack + with D2 field scripts can yield **music + black / wrong open** while script still advances.

## Status

| Issue | Likely cause | Next |
|-------|----------------|------|
| Early freeze Midgar | largely CE; CSR-only OK | closed for now |
| Slow BCX loads | long seeks; cosmetic hitch | watch only |
| CSR trims “gone” post-Jenova | SD overwrites with CSR **D2** fields | expected; document |
| No break / black at disc2 | LOST2 force OK; **movies pack off under CSR+** | test CSR+SD **without** CSR+; or allow movies with CSR+ |

## Next human isolation

**Build C:** CSR + Single-disc, **no CSR+** (movies pack should auto-include). Same cold path to disc1→2. Expect CSR D2 break / cos_btm2.
