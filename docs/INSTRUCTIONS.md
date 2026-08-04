# Task: Inventory CSR single-disc manip movies (whitelist)

## Goal

List the exact D2/D3 MOVIE files that must live on Disc 1 when:

    Base: CSR (csr-v0.14.1)
    single-disc core: on
    CSR+ scenes: none

Those files become pack single-disc-csr-manip-movies later.
CSR + CSR+ single-disc does not use this pack.

Budget after SNOVA on an 80-min CD: about 93 MB raw free. Prefer a tight list.

## Do not (this task)

- Do not inject movies into a layer yet
- Do not rebuild single-disc-on-csr for this task
- Do not copy all D2/D3 movies
- Do not touch Unmodified / Highwind packs

## Background (already in repo)

| Doc | Use |
|-----|-----|
| docs/findings/2026-08-04-single-disc-csr-manip-movies-pack-split.md | Why core vs movie pack is split |
| docs/findings/2026-08-04-single-disc-csrplus-fmv-deduce-manip-movies.md | CSR+ COTA/endgame diffs |
| mods/single-disc/patches/csr-manip-movie-whitelist.md | Working list (edit this) |
| mods/single-disc/patches/field-movie-d2d3-missing-on-d1.md | All D2/D3-only refs (too big to copy) |

Automated CSR+ endgame seed: LASTFLOR.MOV (~3 MB) + small BIN stubs.
COTA pack did not add a CSR-only movie (CANONON already cut on CSR base).
Hojo CSR+ may imply CANONHT2.MOV (~5 MB) if that FMV still matters for CSR manips.

## Step 0 — setup

    cd /path/to/Final-Fantasy-7-Modding
    git pull --ff-only

Optional size dump:

    python3 mods/single-disc/scripts/list_d2d3_only_movies.py

## Step 1 — seed the working list

Open mods/single-disc/patches/csr-manip-movie-whitelist.md.

Start from Seed (from repo) rows. Keep columns filled as you go.

## Step 2 — CSR multi-disc reference (what still plays)

Need CSR without CSR+ and without single-disc, normal D1/D2/D3:

- Builder: base csr-v0.14.1, no single-disc, no CSR+ scenes
- Or known-good CSR multi-disc set

Play manip-critical scenes only (not full story), especially:

1. Final Descent / List-related FMVs still on CSR
2. Hojo FD path (if you care about that FMV timing)
3. Any other CSR-kept FMV runners rely on (note map + movie filename)

For each FMV that must look/time correctly on single-disc:

1. Note map / field (Makou name or DAT)
2. On the correct retail disc for that map (D2 or D3), Makou: Find Set next movie / Play movie
3. Read the movie name Makou shows for that disc
4. Confirm file is missing from pristine D1 MOVIE/:

       python3 mods/single-disc/scripts/list_d2d3_only_movies.py --check NAME.MOV

5. Add/update a row in the whitelist with status candidate and size from the script

If CSR already removed the FMV (no Play), skip — no copy needed.

## Step 3 — optional: CSR+ cross-check

If a scene is trimmed by a CSR+ pack you use for manips on multi-disc CSR without that pack,
the movie may still be required for CSR-alone.

Diff method is only a hint (see csrplus-fmv finding). Trust play + Makou over auto scan.

## Step 4 — budget gate

    python3 mods/single-disc/scripts/list_d2d3_only_movies.py --sum-whitelist

Keep raw total of include rows under ~80 MB if possible (leave headroom under ~93 MB).

If over: drop largest non-essential, or accept wrong FMV / duration-only for that site (document why).

## Step 5 — mark decisions

For each row set status to one of:

- include — copy onto D1 in movie pack; keep Play on CSR single-disc
- exclude-csr-already-cut — CSR base has no Play
- exclude-wrong-fmv-ok — crawls not an issue / wrong stream OK
- exclude-csr-plus-only — only matters when CSR+ off and you do not need it
- deferred — need another session

## Step 6 — commit evidence

    git add mods/single-disc/patches/csr-manip-movie-whitelist.md
    git commit -m "single-disc: CSR manip movie whitelist progress"
    git push

## Done when

- Every known CSR manip FMV has a whitelist row with status
- Sum of include sizes fits budget (script --sum-whitelist)
- No plan to ship endings (ENDING2E etc.) on D1
- Notes list which manips were checked

## After this task (not now)

Build single-disc-csr-manip-movies-v* ISO inject from include rows only;
stack with single-disc-on-csr for CSR-alone single-disc. Finish BLACKBGB on core pack separately.

## Evidence

    Whitelist path: mods/single-disc/patches/csr-manip-movie-whitelist.md
    include count / MB:
    Manips checked:
    Not checked yet:
    Budget OK:
    Push:

Say check when the whitelist has real include decisions.
