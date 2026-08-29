# CSR single-disc — manip movie whitelist (working)

**Pack (later):** single-disc-csr-manip-movies-v*
**Stack:** CSR base + single-disc-on-csr + this pack (no CSR+ scenes)
**Budget:** keep include total well under ~93 MB raw free after SNOVA (~80 MB target)

Status values: seed | candidate | include | exclude-* | deferred

User MB = ISO file size / 1024^2. Raw on disc is about user x 1.15.

## Seed (from repo analysis)

| Movie file | Disc | User MB | Why seeded | Field / scene (if known) | Status | Notes |
|------------|:----:|--------:|------------|--------------------------|--------|-------|
| LASTFLOR.MOV | D3 | 2.98 | CSR+ endgame removes; CSR LAS0_3 still has Play | LAS0_3 | include | Playtest seed v0.1.0 — D1 id 36 (JAIROFAL.MOV) |
| LAST4_3.BIN | D3 | 0.24 | same endgame diff | LAS0_3 | include | Playtest seed — D1 id 34 (GOLD7_2.MOV) |
| LASTMAP.BIN | D3 | 0.21 | same endgame diff | LAS0_3 | include | Playtest seed — D1 id 37 (JAIROFLY.MOV) |
| ~~CANONHT2.MOV~~ | D2 | 5.00 | ~~CSR+ Hojo removes; CSR CANON_2 still has Play~~ | ~~CANON_2~~ | **exclude-dead** | **2026-08-29 CFG audit: CANON_2 has zero PMVIE opcodes (the `0e 03` bytes there are music, not a movie call — 0.1.20 changelog). ZMIND3's only PMVIE for this id (39) is on `shad3/5`, never called AND unreachable within its own slot (dead code below an unconditional MAPJUMP). `scan_csr_movie_reachability.py` also checked BLACKBG3 (field unreachable) and FSHIP_12 `ad/3` (slot never called) — no live call exists anywhere on CSR D2. Drop from budget.** |
| JUNSEA.STR | D2 | 1.21 | LOSLAKE1 (#637) Costa lake / manip | include | **CORRECTED 2026-08-29: id 47 in LOSLAKE1 resolves to CANONON.MOV, not JUNSEA.STR (this doc's manual id mapping was stale — `scan_csr_movie_reachability.py`'s sorted-dirent resolution is ground truth). See CANONON note below.** |

**Seeded (current pack):** CANONON.MOV via JAIROFAL + LBA 250450 Form2 alias (LOSLAKE1 #637).
**Confirmed live trigger (2026-08-29 CFG audit):** LOSLAKE1 (field 637), entity `cl`, slot 9 — `reachable=True`, `field_reachable=True`, `slot_live=True` (the only live copy of the cl/9-31 dialogue-branch duplicates). PMVIE id 47 → CANONON.MOV per disc-local sorted-dirent resolution. `build_playtest_bin.py` independently confirms the built image's `JAIROFAL.MOV` bytes == D2 `CANONON.MOV` and the raw LBA 250450 Form2 sector matches D2. **To playtest:** reach the LOSLAKE1 field's `cl` dialogue scene (party-choice prompt via `IFPRTYQ`, ends in `MUSIC f003` → `PMVIE 47` → `MOVIE`) and confirm the cannon-firing footage plays cleanly. Video content will legitimately show CANONON (cannon) footage rather than the original JUNSEA (sea) footage — intentional budget repoint, not a bug.
**Also confirmed dead (2026-08-29 CFG audit, FSHIP_12 relocation v0.1.6):** CANONHT1.MOV and CANONH1P.MOV. FSHIP_12's `ad/3` slot carries all three PMVIE calls (ids 59/50/51 → CANONH1P/CANONHT1/CANONHT2) but the slot is never called by anything in the field — confirmed neither `REQ`/`Init`/`Main` autorun reachable nor a walkmesh-line-trigger slot (entity `ad` type-detects as "Default", no `LINE` opcode). The `ship_movie_relocation_fship12_canonht.py` v0.1.6 pack (~16.6 MB total) fixed movie calls that can never fire in-game. **Removed 2026-08-29**: the `single-disc-csr-manip-movies-v0.1.6` layer/pack was deleted and dropped from `build_playtest_bin.py` and `builder/manifest.json` (its never-built `v0.1.7` dangling stub, which depended on it, was removed too — see CHANGELOG). The `v0.1.6` version slot was then reused the same day for an unrelated real bug fix (MD8_5 #731 PMVIE id 53 / OPENINGE.MOV LBA collision, `ship_movie_relocation_v017_mid53.py`), now chained directly on top of v0.1.5's output instead of the deleted CANONHT pack.
**Not in seed:** LASTFLOR.MOV — id-slot clash with CANONON/JAIROFAL.
**Never include:** ENDING2E.MOV (~156 MB), other full endings — will not fit.

## Candidates (fill from CSR multi-disc play + Makou)

| Movie file | Disc | User MB | Field / map | Manip / reason | Status | Notes |
|------------|:----:|--------:|-------------|----------------|--------|-------|
| LOSLAKE1.MOV | D2 | 5.78 | ioslake3 #639 | Bugenhagen lake FMV | candidate | + LSLMV; or trim Set+Play |
| LSLMV.STR | D2 | 1.73 | ioslake3 #639 | lake FMV pair | candidate | with LOSLAKE1.MOV |
| PHOENIX.MOV | D2 | 8.28 | BLIN70_4 | CSR still plays; D2-only | candidate | space ~8 MB |
| DUMCRUSH.MOV | D2 | 8.04 | LOSLAKE1 CSR path | still on CSR after COTA | candidate | may be intentional keep |
| WHITE2.BIN | D3 | 0.24 | CANON_2 / Hojo | CSR+ removes; CSR may play | candidate | tiny |
| LASTFLOR.MOV | D3 | 2.98 | LAS0_3 | endgame; clashes JAIROFAL | deferred | need free D1 slot |

## Decisions — include (ship in movie pack)

| Movie file | Disc | User MB | Field / map | Confirmed by |
|------------|:----:|--------:|-------------|--------------|
| | | | | |

## Decisions — exclude

| Movie file | Status | Reason |
|------------|--------|--------|
| | | |

## Running total

Update after edits:

    python3 mods/single-disc/scripts/list_d2d3_only_movies.py --sum-whitelist

| Metric | Value |
|--------|------:|
| include count | |
| include user MB | |
| include approx raw MB | |
| headroom 80-min after SNOVA | ~93 MB raw |

## Session log

| Date | What checked | Result |
|------|--------------|--------|
| 2026-08-06 | LOSLAKE1 CD logs + Form2 inject | CANONON alias @250450 works; seed injects now raw Form2 |
| | | |


## Playtest pack (v0.1.0)

- Pack: single-disc-csr-manip-movies-v0.1.0
- Stack: csr-v0.14.1 + single-disc-on-csr-v0.1.2 + this pack (no CSR+ scenes)
- Method: overwrite D1 MOVIE id (sorted name index), shrink ISO size to source length
- Work bin: workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin
- Re-inject: python3 mods/single-disc/scripts/inject_movies_by_disc_id.py --d1 WORK.bin --manifest mods/single-disc/patches/csr-manip-movie-seed.txt --in-place

Side effect: D1 ids 7/34/36/37 no longer play original D1 clips (CAR_1209, GOLD7_2, JAIROFAL, JAIROFLY).

After playtest: add more include rows and re-run inject + rebuild layer.

| 2026-08-12 | Dual/flicker audio on manip movies | MOVIE_ID eng_size was ISO bytes + stale aux; CSR D2 uses nsec*2336 Form2 size. Pack v0.1.3 copies source Form2 eng size/aux. Residual zero optional (FF7_ZERO_MOVIE_RESIDUAL=1). |

| 2026-08-12 | Rocket instead of waterfall | v0.1.3 dropped LBA 250450 CANONON Form2 alias; v0.1.4 restores alias + keeps Form2 MOVIE_ID |
