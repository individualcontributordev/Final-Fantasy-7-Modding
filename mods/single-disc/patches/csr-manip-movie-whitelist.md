# CSR single-disc — manip movie whitelist (working)

**Pack (later):** single-disc-csr-manip-movies-v*
**Stack:** CSR base + single-disc-on-csr + this pack (no CSR+ scenes)
**Budget:** keep include total well under ~93 MB raw free after SNOVA (~80 MB target)

Status values: seed | candidate | include | exclude-* | deferred

User MB = ISO file size / 1024^2. Raw on disc is about user x 1.15.

## Seed (from repo analysis)

| Movie file | Disc | User MB | Why seeded | Field / scene (if known) | Status | Notes |
|------------|:----:|--------:|------------|--------------------------|--------|-------|
| LASTFLOR.MOV | D3 | 2.98 | CSR+ endgame removes; CSR LAS0_3 still has Play | LAS0_3 | seed | Confirm manip needs correct stream |
| LAST4_3.BIN | D3 | 0.24 | same endgame diff | LAS0_3 | seed | Tiny; include if LASTFLOR in |
| LASTMAP.BIN | D3 | 0.21 | same endgame diff | LAS0_3 | seed | Tiny stub |
| CANONHT2.MOV | D2 | 5.00 | CSR+ Hojo removes; CSR CANON_2 still has Play | CANON_2 | seed | Only if Hojo-path FMV needed on CSR-alone |

**Not seeded:** CANONON.MOV — CSR base already removed from LOSLAKE1 (COTA FMV).
**Never include:** ENDING2E.MOV (~156 MB), other full endings — will not fit.

## Candidates (fill from CSR multi-disc play + Makou)

| Movie file | Disc | User MB | Field / map | Manip / reason | Status | Notes |
|------------|:----:|--------:|-------------|----------------|--------|-------|
| | | | | | | |

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
| | | |
