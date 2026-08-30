# Movie System Reference — PMVIE → MOVIE_ID.BIN → CD-ROM seek

End-to-end reference for how field scripts trigger FMV playback, verified
from raw bytes + Makou Reactor source per `.agents/rules/verified-reference-evidence.mdc`.
Use this to reproduce or extend movie-relocation tooling (`mods/single-disc/scripts/`).

## The chain

```
Field script (FIELD/*.DAT)
  PMVIE opcode (0xF8), 1-byte movie id
        │
        ▼
MINT/MOVIE_ID.BIN  (this disc's table, one 20-byte row per id)
  row[id] = { lba, engine_size, auxA, auxB, auxC }
        │
        ▼
ISO9660 dirent lookup by that LBA (MOVIE/ directory)
        │
        ▼
CD-ROM seek to LBA, stream Form2 (2336-byte) sectors
```

The **id is disc-local and table-driven, not a sorted-directory index and
not an embedded LBA**. Both wrong assumptions have been made in this repo's
own tooling history (see Evidence below) — always resolve via the table.

## PMVIE opcode (evidence: bytes + source)

- `FIELD/LOSLAKE1.DAT` (D2): bytes `f8 2f` → opcode `0xF8`, 1-byte id `0x2f` = 47.
- `FIELD/LAS4_0.DAT` (D3): bytes `f8 19` → id `0x19` = 25.
- Makou Reactor `src/core/field/Opcode.h:1497-1501`:
  ```cpp
  STRUCTPACK(struct OpcodeMovie : public OpcodeBase { quint8 movieID; });
  STRUCTPACK(struct OpcodePMVIE : public OpcodeMovie {});
  ```
  One byte total — cannot hold an LBA. There is no per-opcode disc/LBA field;
  the "Disc" combo in Makou's script editor UI (`ScriptEditorMoviePage.cpp:82-89`)
  is cosmetic label-swapping only (`Data::movie_names_cd1/cd2/cd3`), never
  written into the opcode (confirmed by reading `buildOpcode()`).

## MOVIE_ID.BIN row format (evidence: bytes, `mods/single-disc/scripts/inject_movies_by_disc_id.py`)

Path on every disc: `MINT/MOVIE_ID.BIN`. Fixed 20-byte little-endian rows,
indexed by PMVIE id (row 0 = id 0, etc.), no header:

| Offset in row | Bytes | Field | Notes |
|---|---|---|---|
| 0 | 4 | LBA | Sector number of the movie file's first sector |
| 4 | 4 | engine size | Stream length **in engine units**, usually `nsec * 2336` (Form2 raw), not the ISO9660 byte size |
| 8 | 4 | auxA | Copied verbatim when relocating; meaning not decoded |
| 12 | 4 | auxB | Same |
| 16 | 4 | auxC | Same |

Python (from `inject_movies_by_disc_id.py::_movie_id_meta_by_lba`):
```python
lba, size, a, b, c = struct.unpack_from("<IIIII", blob, row_index * 20)
```

**Engine size gotcha:** copying only the ISO byte size into offset 4 leaves
the player reading a truncated/misaligned stream. Always copy the *source
disc's* row 4-19 (size + aux) verbatim when relocating a movie, or compute
`nsec * 2336` from sector count if no source row exists
(`_form2_size_field()` in the same script).

## Resolving id → filename (evidence: bytes, cross-checked 3 ways)

```python
by_lba = {lba: name for name, lba, size in movie_dirents}   # MOVIE/ dirents
row_lba = struct.unpack_from("<I", movie_id_bin, id * 20)[0]
filename = by_lba[row_lba]
```

**Do not** resolve id via `sorted(MOVIE/ dirents)[id]` — this was a real bug
found and fixed in this repo (`docs/findings/2026-08-24-csr-movie-reachability-scan.md`):
CSR D2 `MOVIE_ID.BIN` row 0 has LBA 129252 → `FSHIP2.BIN`, while the
alphabetically-sorted `MOVIE/` directory's index 0 is `BOOGDOWN.STR` at a
completely different LBA. Every one of 61 D2 rows mismatched between the two
orderings when checked side by side.

## Cross-check: PMVIE id agrees with Makou's own per-disc name list

Makou Reactor's `Data.cpp:607-623` builds `movieList[106]` as
`common[0-19] + disc-specific slice` (`:526-544`). This is a second,
independent verification path (Makou's naming, not the executable's table):

- D2: `movieList[81] = "canonon"`. cd2-list index = `20 + (81-54) = 47`.
  Matches `LOSLAKE1.DAT`'s `f8 2f` (47) and `MOVIE_ID.BIN` row 47 → `CANONON.MOV`.
- D3: `movieList[101] = "ending1"`. cd3-list index = `20 + (101-96) = 25`.
  Matches `LAS4_0.DAT`'s `f8 19` (25).

Three sources agree (field script bytes, `MOVIE_ID.BIN` bytes, Makou source) —
see `docs/findings/2026-08-24-canonon-hardcode-clean-room-reverification.md`
for the full citation trail.

## Absolute-LBA seek exception (CANONON, evidence: bytes + live test on pristine D2)

One confirmed case does **not** go through `MOVIE_ID.BIN`: `LOSLAKE1`'s
PMVIE id 47 (`CANONON`) seeks hardcoded LBA 250450 directly, regardless of
what the table's row 47 says. Confirmed by a clean single-variable live
test on a **pristine, unmodified Disc 2** (not just the single-disc D1
rebuild): patching only row 47 to point at a visually distinct movie
(`BOOGUP.STR`) had no effect — the real CANONON content played anyway. See
`docs/findings/2026-08-24-canonon-hardcode-clean-room-reverification.md`
(live result) and `docs/findings/2026-08-05-loslake1-cdrom-d1-vs-d2.md` +
`alias_d2_seek_lba_on_d1.py` (`D2_CANONON_LBA = 250450`, the working
aliasing tool). This means the file occupying LBA 250450 must literally be
`CANONON.MOV`'s bytes; you cannot redirect this one playback by editing the
table row alone.

**Not yet tested:** whether this is unique to id 47 or a broader engine
behavior. All *other* movies confirmed reachable by the CFG scanner
(`docs/findings/2026-08-24-csr-movie-reachability-scan.md`) are *assumed* to
use the normal table path and relocatable by editing `MOVIE_ID.BIN` + the
dirent (as `inject_movies_by_disc_id.py` does), but only id 47 has actually
been live-tested for table-vs-hardcode behavior.

## Reproducing a movie relocation (worked example)

To move `RCKTOFF.MOV` (D2, PMVIE id 41) onto a single-disc D1 build:

1. Resolve D2 id 41 → LBA via `MOVIE_ID.BIN[41]` → confirm dirent name matches manifest.
2. Pick a D1 target slot (existing id 41's current file) to overwrite.
3. Read D2's raw Form2 sectors at that LBA (`nsec = ceil(size / 2048)`... engine steps in `2336`).
4. Write those sectors into D1 at the target slot's LBA (or a new EOF LBA if larger).
5. Patch D1's dirent (LBA + ISO size) if the target moved/grew.
6. Patch D1's `MOVIE_ID.BIN` row 41: LBA = new location, size/aux copied from D2's row 41.
7. Diff into an `ic-layer-v1` record (`docs/reference/layer-engineering.md`).

`mods/single-disc/scripts/inject_movies_by_disc_id.py` implements exactly
this via a manifest file (`mods/single-disc/patches/csr-manip-movie-seed.txt`).

## Verified vs. unresolved

| Claim | Confidence | Evidence |
|---|---|---|
| PMVIE is 1-byte disc-local table index | confirmed | source + bytes, 3-way cross-check |
| MOVIE_ID.BIN row = 20 bytes LE, offsets above | confirmed | bytes, used successfully by shipped tooling |
| Sorted-dir-order ≠ PMVIE id | confirmed | bytes, 61/61 mismatch on CSR D2 |
| CANONON/LOSLAKE1 needs absolute LBA (not table-only) | confirmed | live test on pristine D2, `2026-08-24-canonon-hardcode-clean-room-reverification.md` + `2026-08-05-loslake1-cdrom-d1-vs-d2.md` |
| Whether *other* engine paths ever bypass the table | open | only PMVIE id 47 (CANONON) has been live-tested |

## Sources

- `workspace/makoureactor/src/core/field/Opcode.h` (1497-1501)
- `workspace/makoureactor/src/widgets/ScriptEditorWidgets/ScriptEditorMoviePage.cpp` (26-99)
- `workspace/makoureactor/src/Data.cpp` (526-544, 607-623)
- `mods/single-disc/scripts/inject_movies_by_disc_id.py`
- `mods/single-disc/scripts/scan_csr_movie_reachability.py`
- `mods/single-disc/scripts/alias_d2_seek_lba_on_d1.py`
- `docs/findings/2026-08-24-canonon-hardcode-clean-room-reverification.md`
- `docs/findings/2026-08-24-csr-movie-reachability-scan.md`
- `docs/findings/2026-08-05-loslake1-cdrom-d1-vs-d2.md`
- `docs/reference/movie-id-mapping.txt`
- https://thelifestream.net/review-the-toshiba-ffvii-dvd/ (Toshiba FFVII DVD ending disc review — not yet cross-checked against build)
- https://wiki.ffrtt.ru/index.php/FF7/Field/Script/Opcodes/F8_PMVIE (Qhimm/ffrtt PMVIE opcode reference)
- https://github.com/cebix/ff7tools/blob/6bf1fbce/fixup (ff7tools `fixup` script, pinned commit)
- https://github.com/cebix/ff7tools/blob/master/fixup (ff7tools `fixup` script, latest)
