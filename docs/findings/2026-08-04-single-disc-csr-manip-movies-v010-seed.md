# Finding: CSR manip movies seed pack v0.1.0

**Date:** 2026-08-04
**Status:** playtest pack published

## Pack

builder/single-disc-csr-manip-movies-v0.1.0/

Stack: csr-v0.14.1 + single-disc-on-csr-v0.1.1 + this pack.

## Method

inject_movies_by_disc_id.py: for each source movie on D2/D3, take its sorted MOVIE/
index (id), overwrite D1 file at that same id, shrink ISO size to source length.

| Movie | Disc | Id | D1 slot overwritten |
|-------|:----:|---:|---------------------|
| LASTFLOR.MOV | 3 | 36 | JAIROFAL.MOV |
| LAST4_3.BIN | 3 | 34 | GOLD7_2.MOV |
| LASTMAP.BIN | 3 | 37 | JAIROFLY.MOV |
| CANONHT2.MOV | 2 | 7 | CAR_1209.STR |

## Why not copy by filename

Adding LASTFLOR.MOV as a new D1 name would sort to a different id; PMVIE would still
point at the old D1 file.

## Next

Playtest; extend seed list / whitelist; rebuild pack.

## Update — JUNSEA for LOSLAKE1 (#637)

| Movie | Disc | Id | D1 slot overwritten |
|-------|:----:|---:|---------------------|
| JUNSEA.STR | 2 | 47 | MK8.STR (grew; appended LBA) |

LOSLAKE1 keeps Play (manip). Do **not** paste Clean Set+Play delete for #637.
Injector now appends MODE2 sectors when source is larger than D1 slot.

