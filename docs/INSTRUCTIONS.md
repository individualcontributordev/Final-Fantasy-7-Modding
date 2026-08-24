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

## Steps (copy-paste — Windows / Git Bash)

### 1. Get the test disc path

From Git Bash, in your clone of this repo:

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
TESTCUE="$(pwd)/workspace/iso-extract/d2_verify_canonon_table_test.cue"
echo "$TESTCUE"
```

Confirm that path prints and the file exists (`ls -la "$TESTCUE"`).

### 2. Launch DuckStation on the test disc

If DuckStation is already installed, try launching it directly with the
disc from Git Bash:

```bash
"/c/Program Files/DuckStation/duckstation-qt-x64-ReleaseLTCG.exe" "$TESTCUE" &
```

If that path doesn't exist (install location varies — winget, portable
zip, etc.), find your actual `duckstation-qt-x64-*.exe` and substitute it
above, e.g.:

```bash
find "/c/Program Files" "/c/Program Files (x86)" -iname "duckstation*.exe" 2>/dev/null
```

If you can't get the command-line launch working, that's fine — just open
DuckStation normally (double-click / Start Menu), then use
**File → Start File...** and browse to the path Step 1 printed.

### 3. Set Safe Mode (once, if not already set)

**Settings → Emulation → Safe Mode** — this is the accurate/hardware-like
baseline from `docs/03-environment-setup.md`. Not required for this test's
result to be valid, but keep it consistent with every other test in this
repo.

### 4. Reach the LOSLAKE1 cannon scene

This test disc is a **pristine Disc 2** rip with only one byte-range
changed (`MOVIE_ID.BIN` row 47) — there is no save state or memory card in
this repo for it, so you need your own Disc 2 mid-game save (or a fresh
Disc 2 boot) and play forward to the mandatory story scene where the party
aims the Junon cannon at Diamond Weapon (this is the scene that plays
`CANONON.MOV` / triggers field `LOSLAKE1`). If you have a memory card save
already sitting right before this scene, load that; otherwise this is the
first major forced story beat after Disc 2 begins, so a fresh boot will
reach it without any sidequest detours.

### 5. Report the result

Reply with exactly what plays when the cannon scene triggers:
- **Snowboard clip plays** (`BOOGUP.STR`, party snowboarding) → the engine
  followed the patched table row → **table is honored**.
- **Cannon movie plays anyway** (real CANONON.MOV content, unaffected by
  the patch) → engine ignored the table and sought a hardcoded LBA →
  **matches CANONON's known hardcoded-LBA behavior**.
- Anything else (black screen, freeze, crash) → report exactly what you
  see/hear and any DuckStation console/log output.

That single observation resolves the question — no further steps needed.
