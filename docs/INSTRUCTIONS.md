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

## Test image (you build it — .bin/.cue are never committed to git)

The test disc is **your own pristine Disc 2 rip** with **exactly one
byte-level change**: `MINT/MOVIE_ID.BIN` row 47 (normally LBA 250450,
`CANONON.MOV`) rewritten to row 11's values (LBA 136669, `BOOGUP.STR` — a
short, visually distinct snowboard clip). Nothing else touched: no file
moves, no size changes, no field-script edits.

- If the engine **reads the table**: reaching the LOSLAKE1 cannon scene
  plays `BOOGUP.STR` (snowboarding) instead of the cannon movie.
- If the engine **ignores the table** (hardcoded LBA): the real CANONON
  movie plays anyway, unaffected by the patch.

## Steps (copy-paste — Windows / Git Bash)

### 1. Build the test image from your own Disc 2 rip

You need a pristine Disc 2 `.bin`/`.cue` on this machine already (any path
is fine). From Git Bash, in your clone of this repo:

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

Set this to wherever your pristine Disc 2 image actually is:

```bash
SRC_D2="/c/path/to/your/ff7_disc2.bin"
ls -la "$SRC_D2"
```

Then build the patched test copy (same folder as your source, `.cue` is
copied/renamed alongside if one exists next to `$SRC_D2`):

```bash
python3 - "$SRC_D2" <<'PYEOF'
import sys, shutil
sys.path.insert(0, "scripts")
import psx_mode2_iso as iso

src = sys.argv[1]
dst = src.rsplit(".", 1)[0] + "_verify_canonon_table_test.bin"
shutil.copyfile(src, dst)

with open(dst, "r+b") as f:
    img = bytearray(f.read())
    data = bytearray(iso.extract_file(img, "MINT/MOVIE_ID.BIN"))
    row_size = 20
    row11 = bytes(data[11 * row_size:12 * row_size])
    data[47 * row_size:48 * row_size] = row11
    iso.replace_file_padded(img, "MINT/MOVIE_ID.BIN", bytes(data))
    f.seek(0)
    f.write(img)

print("Wrote:", dst)

src_cue = src.rsplit(".", 1)[0] + ".cue"
dst_cue = dst.rsplit(".", 1)[0] + ".cue"
try:
    with open(src_cue) as cf:
        cue = cf.read()
    import os
    cue = cue.replace(os.path.basename(src), os.path.basename(dst))
    with open(dst_cue, "w") as cf:
        cf.write(cue)
    print("Wrote:", dst_cue)
except FileNotFoundError:
    print("No .cue next to source — point DuckStation at the .bin directly.")
PYEOF
```

This prints the path(s) it created — that's your `$TESTCUE` for the next
step (the `.cue` if one was made, otherwise the `.bin`).

```bash
TESTCUE="${SRC_D2%.*}_verify_canonon_table_test.cue"
[ -f "$TESTCUE" ] || TESTCUE="${SRC_D2%.*}_verify_canonon_table_test.bin"
echo "$TESTCUE"
```

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
