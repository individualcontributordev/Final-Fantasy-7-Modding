# Finding: D1→D2 disc-swap hang — NRCRL FMV inject dropped from manip-movies pack

**Date:** 2026-08-21
**Status:** fixed, `single-disc-csr-manip-movies-v0.1.5`
**Stack:** CSR + single-disc-on-csr + manip-movies (CSR+ off)

## Symptom

Game hangs on black screen at the D1→D2 transition. No "Insert Disc 2"
prompt ever appears — DuckStation log shows normal forward reads climbing
through ~28:13:xx, then a hard backward seek to LBA 68314 and FPS 0.00
forever.

## Investigation

Ruled out `BLACKBGB` DSKCG-removal jump corruption (fixed separately in
v0.1.3.2) — the symptom (no prompt at all, hang far earlier) doesn't match
a broken disc-swap-prompt script.

Compared `FIELD/MD8_52.DAT` (field #779) across CSR baseline, current
single-disc work bin, and a known-working reference. Current build's script
was byte-identical to raw CSR (still has `PMVIE 34` / `MOVIE` opcodes intact
— not corrupted). This ruled out the field script as broken.

Checked whether `MOVIE/MTNVL2.STR` (the D1 movie slot MD8_52's `PMVIE 34`
resolves to) actually contains the injected D2 `NRCRL.MOV` FMV. It did not —
it was still stock pristine D1 content (`MTNVL2.STR` original, len 3543040,
vs D2 `NRCRL.MOV` len 5801984).

## Root cause

`docs/findings/2026-08-13-md8-52-nrcrl-cloud-position.md` documents that this
exact inject (`NRCRL.MOV` → `MTNVL2.STR`) was implemented in
`single-disc-on-csr-v0.1.22`, then folded into the cumulative
`single-disc-csr-manip-movies-v0.1.4` pack (which also carries 4 sibling
injects: `NRCRLB.MOV`→`NIVLSFS.MOV`, `PARASHOT.MOV`→`OPENINGE.MOV`,
`METEOFIX.MOV`→`MTCRL.STR`, `METEOSKY.MOV`→`MTNVL.STR`, from v0.1.21/23).

Diffing the shipped `builder/single-disc-csr-manip-movies-v0.1.4/layers/disc1.layer.json`
against a fresh CSR+core baseline confirmed all 5 of these injects are
**absent** from the pack as currently shipped — it only carries the
JAIROFAL/CANONON, CANONHT2, LAST4_3, LASTMAP, and LBA-250450-alias content.
The 5 PMVIE-target injects were lost at some point after v0.1.23 and never
restored; no single commit could be found that removed them (likely dropped
during one of several full-bin-diff layer rebuilds in this period).

Since the field script still calls `PMVIE 34`/`MOVIE` and `MINT/MOVIE_ID.BIN`
still points at the (unpatched) stock `MTNVL2.STR` LBA/size, the engine tries
to stream the movie from where the *stock* file lives — but the field script
expects D2-length data, so the CD-ROM seek pattern goes wrong and the drive
stalls indefinitely. No "Insert Disc 2" prompt shows because the hang occurs
during MD8_52's FMV before the disc-swap fields are ever reached.

## Fix (v0.1.5)

New `single-disc-csr-manip-movies-v0.1.5` layer — a **delta pack** diffed
against (CSR + single-disc-on-csr + manip-movies v0.1.4) as its baseline,
containing only the 5 restored injects (via
`inject_movies_by_disc_id.inject_one`). Built as a delta rather than a
from-scratch cumulative layer because a full cumulative layer.json exceeded
GitHub's 100MB file-size limit. `v0.1.4` stays enabled in
`builder/manifest.json`; `v0.1.5`'s `autoIncludeWhen.addonSelected` targets
`single-disc-csr-manip-movies-v0.1.4` so it always applies right after it.

## Verify

`verify_builder_config.py` full 10-addon stack (base + single-disc-on-csr +
manip-movies v0.1.4 + v0.1.5 + 7 endings parts) applies cleanly (4,978,843
records). `MOVIE/MTNVL2.STR` byte-matches pristine D2 `NRCRL.MOV` after the
full stack is applied.

## Not changed

`single-disc-on-csr` core field-merge pipeline (`build_work_bin.py`) — its
`MD8_52.DAT` output was already correct (matches raw CSR, PMVIE/MOVIE
intact). Only the movie-file injection was missing, in the movies pack.
