# Verify: does the engine honor MOVIE_ID.BIN, or is CANONON's LBA hardcoded?

## Why this test

Static checks (done, both ruled out — no need to repeat):
- `FIELD.BIN`/`BATTLE.X` identical across D1/D2/D3 (MD5) — not there.
- `LOSLAKE1.DAT`'s `PMVIE` opcode is `f8 2f` (id 47, one byte) — the field
  script itself cannot embed a full LBA, so it isn't the source.
- `SCUS_941.63` raw-scanned for `250450` as a 32-bit LE word *and* as a
  BCD MSF triple (`55:41:25`, both byte orders) — zero hits either way.

None of that proves or disproves the engine ignores a patched
`MOVIE_ID.BIN` row at runtime — only a live test can. Prior notes claimed
growing `MOVIE_ID` row 25 to a new LBA didn't change the ending's seek,
but that test also grew the file, moved it to EOF, and changed disc size
all at once — too many variables. This is a single-variable version.

## Test image (already built)

`workspace/iso-extract/d2_verify_canonon_table_test.bin` (+ matching
`.cue`) — pristine Disc 2 with **exactly one byte-level change**:
`MINT/MOVIE_ID.BIN` row 47 (normally LBA 250450, `CANONON.MOV`) rewritten
to row 11's values (LBA 136669, `BOOGUP.STR` — a short, visually distinct
snowboard clip). Nothing else touched: no file moves, no size changes, no
field-script edits.

- If the engine **reads the table**: reaching the LOSLAKE1 cannon scene
  plays `BOOGUP.STR` (snowboarding) instead of the cannon movie.
- If the engine **ignores the table** (hardcoded LBA): the real CANONON
  movie plays anyway, unaffected by the patch.

## Steps

1. Load `d2_verify_canonon_table_test.cue` in DuckStation (or your usual
   emulator/debugger).
2. Get to the point in Disc 2 that triggers the LOSLAKE1 cannon scene
   (fastest known save/route to that field).
3. Report exactly what plays: the cannon movie, the snowboard clip, a
   black screen/freeze, or something else.

That single observation resolves the question — no further steps needed.
