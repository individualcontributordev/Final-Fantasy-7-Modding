## RETRACTED 2026-08-28

The "id 53 LBA collision" diagnosis below and the v0.1.7 fix it produced
were **wrong** and have been reverted (never shipped to the user for
playtest). Re-verified: `MOVIE_ID.BIN` row 53's LBA (295563) and size
field (11957984) both check out exactly against `/MOVIE/OPENINGE.MOV`'s
real dirent (10483712 bytes; `11957984 == 10483712 * 2336/2048`, the
correct ISO-logical-to-Form2-payload size conversion). Per the user:
field 731's intended movie is **PARASHOT** (CSR D2), and D1's equivalent
slot for that content is `OPENINGE.MOV` (see
`mods/single-disc/patches/csr-manip-movie-seed.txt`: `PARASHOT.MOV
->OPENINGE.MOV`). So id 53 -> OPENINGE was already correct; there was no
collision to fix. v0.1.7 (which repointed id 53 to a fresh NRCRLB.MOV
copy, based on the now-superseded 2026-08-12 finding) has been removed
from `build_playtest_bin.py` and deleted from `builder/`.

**Actual open question:** if id 53/OPENINGE is structurally correct, why
did the user observe no movie playing at the 67->731 transition? Next
lead: `MD8_5` `dir`/slot0's very first opcode is `IFSW` (bank 0x20, addr
0x00, value 0x3f00, cmp 0x06, jump +0x24) gating the entire
fade/PMVIE/MOVIE/SETWORD block — if that switch is already true on
arrival, the whole sequence (including the movie) is skipped. Not yet
confirmed whether that's the actual failure mode; needs a playtest/debug
session (e.g. watch switch bank 0x20 addr 0 in an emulator's memory
viewer when arriving at field 731) rather than further static analysis.

---

# Finding: FSHIP_12 (#67) -> MD8_5 (#731) still broken — id 53 LBA collision, not a movie-id mismatch

**Stack:** csr-v0.14.2 + single-disc-on-csr + manip-movies v0.1.4/v0.1.5/v0.1.6
**Report:** field 67 jumps straight to 731 without playing any movies; also
confirmed broken in the known-working reference bin
(`ff7-d1-csr-sd-mov-end.bin`) — not a single-disc-merge regression.

## Wrong turn first: v0.1.6 fixed a different transition

Initial report guessed `pcid`/Script 3. Actual decode of `FIELD/FSHIP_12.DAT`
shows the `ad` entity (index 2) has two separate, switch-gated exits, not
one:
- `ad` slot 3: `PMVIE` 59/50/51 (CANONHT triplet) -> `MAPJUMP` to field
  **269** (`blin70_4`). These 3 ids were genuinely broken (59 OOB, 50/51
  wrong content) — fixed for real in `single-disc-csr-manip-movies-v0.1.6`.
  This is a legitimate, separate fix; keep it.
- `ad` slot 4: ASK menu -> `MAPJUMP` straight to field **731** (`MD8_5`).
  **No PMVIE/MOVIE opcodes in FSHIP_12 for this path at all.**

So v0.1.6 could never have fixed the reported symptom — it targeted the
269 branch, not the 731 branch.

## Real location of the 731 movie

`FIELD/MD8_5.DAT`, entity `dir` (index 0), script slot 1 (Main):
`PMVIE id=53` -> `MOVIE` -> `SETWORD` (GameMoment progress). This exact
site was already documented and "fixed" once:
`docs/findings/2026-08-12-fship12-md8-5-mid53-nrcrlb.md` (id 53 should
resolve to CSR D2 `NRCRLB.MOV`, injected into D1's `NIVLSFS.MOV` slot).

## Root cause (this session): id 53's LBA points at the wrong appended block

`MINT/MOVIE_ID.BIN` row 53 has LBA **295563** in both the current build
and the reference bin (identical — confirms this has been broken the whole
time, in both). Walking the ISO9660 tree shows LBA 295563 belongs to
`/MOVIE/OPENINGE.MOV` (the PARASHOT inject target from the same v0.1.4/
v0.1.5 batch), **not** `/MOVIE/NIVLSFS.MOV` (whose actual dirent LBA is
198348). So id 53 currently streams PARASHOT/OPENINGE content (or hits a
Form2 size mismatch) instead of NRCRLB — matching the observed symptom
(transition happens, no movie, MD8_5's post-movie `SETWORD`/game-logic
setup never completes correctly).

This is the same class of bug flagged in
`docs/findings/2026-08-21-md8-52-nrcrl-inject-dropped-from-movies-pack.md`
("many full-bin-diff layer rebuilds... lost track of injects") — id 53's
target LBA was silently repointed to the wrong appended location at some
point after the original v0.1.21 fix, likely during the v0.1.4/v0.1.5
restore of 5 injects.

## Not changed

`FIELD/MD8_5.DAT` bytes — byte-identical between reference bin and current
build. `FIELD/FSHIP_12.DAT` `ad`/slot4 (the 731 ASK+MAPJUMP path) —
unaffected by v0.1.6 (only slot3's movie ids were touched).

## Fix (not yet shipped)

Give id 53 its own freshly EOF-appended copy of CSR D2 `NRCRLB.MOV`,
independent of whatever landed at LBA 295563 for OPENINGE/PARASHOT.
Template: `mods/single-disc/scripts/ship_movie_relocation_fship12_canonht.py`
(same `_append_raw_grow` + `MOVIE_ID.BIN` row repoint + raw-sector verify
pattern). Ship as `single-disc-csr-manip-movies-v0.1.7`, delta on v0.1.6.
Also worth auditing the other 4 sibling injects from the same batch
(`MTNVL2.STR`->NRCRL, `MTCRL.STR`->METEOFIX, `MTNVL.STR`->METEOSKY, and
OPENINGE->PARASHOT itself) for the same kind of LBA collision.

Full runbook (build commands, diagnostic one-liners, exact fix steps)
written to the user's own instructions file for manual RE — see chat
session, not duplicated here.

## Verify

Re-run: `MINT/MOVIE_ID.BIN` row 53 LBA should point at a dirent-less,
freshly-appended block whose raw sectors byte-match CSR D2 `NRCRLB.MOV`,
not `/MOVIE/OPENINGE.MOV`.
