# Decompress BATTLE overlays + import in Ghidra

FF7 PSX `BATTLE/*.X` files (and `FIELD.BIN` / `WORLD.BIN`) are **GZIPPS**:

```
[0:4]  decompressed size (u32 little-endian)
[4:8]  GZIPPS marker
[8:]   gzip payload (bytes start with 1f 8b)
```

Tool: `scripts/decompress_gzipps.py`  
**Not** for FIELD map `.DAT` (use `scripts/lzs.py`).

## Load addresses (image base in Ghidra)

| Disc file | Decompressed size (typical) | Ghidra image base |
|-----------|-----------------------------|-------------------|
| `BATTLE/BATRES.X` | 6460 (`0x193C`) | **`0x801B0000`** |
| `BATTLE/BATTLE.X` | 342188 (`0x538AC`) | **`0x800A0000`** |
| `BATTLE/BATINI.X` | 10164 (`0x27B4`) | init overlay (separate) |
| `SCUS_941.63` body | — | **`0x80010000`** (after 0x800 EXE hdr) |

Fanfare / victory RE: start with **BATRES** @ `801B0000`.

## 1. Extract compressed files

### Option A — from pristine ISO (repo)

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p workspace/iso-extract/battle-raw workspace/iso-extract/battle-dec

python3 << 'PY'
from pathlib import Path
from scripts.psx_mode2_iso import extract_file

img = bytearray(Path("workspace/pristine/FINALFANTASY7_D1.bin").read_bytes())
out = Path("workspace/iso-extract/battle-raw")
for name in ("BATTLE/BATTLE.X", "BATTLE/BATRES.X", "BATTLE/BATINI.X"):
    data = extract_file(img, name)
    dest = out / name.replace("/", "_")
    dest.write_bytes(data)
    print(f"wrote {dest} ({len(data)} bytes) head={data[:12].hex()}")
PY
```

Head should contain `1f8b` after the first 8 bytes.

### Option B — CDMage

Open Disc 1 → extract `BATTLE/BATTLE.X`, `BATRES.X`, `BATINI.X` into e.g.
`workspace/iso-extract/battle-raw/`.

## 2. Decompress

```bash
cd "$(git rev-parse --show-toplevel)"

python3 scripts/decompress_gzipps.py \
  workspace/iso-extract/battle-raw/BATTLE_BATRES.X \
  workspace/iso-extract/battle-dec/BATRES.X.dec

python3 scripts/decompress_gzipps.py \
  workspace/iso-extract/battle-raw/BATTLE_BATTLE.X \
  workspace/iso-extract/battle-dec/BATTLE.X.dec

python3 scripts/decompress_gzipps.py \
  workspace/iso-extract/battle-raw/BATTLE_BATINI.X \
  workspace/iso-extract/battle-dec/BATINI.X.dec
```

Sanity (BATRES should start with MIPS `addiu sp,…`):

```bash
xxd -l 16 workspace/iso-extract/battle-dec/BATRES.X.dec
# expect: 78 ff bd 27 ...
```

| Failure | Cause |
|---------|--------|
| Not a gzipped file | Already `.dec`, or bad/truncated extract |
| Size ≠ header | Corrupt extract; re-extract |

### One-liner (BATRES only)

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p workspace/iso-extract/battle-raw workspace/iso-extract/battle-dec
python3 << 'PY'
from pathlib import Path
from scripts.psx_mode2_iso import extract_file
img = bytearray(Path("workspace/pristine/FINALFANTASY7_D1.bin").read_bytes())
raw = Path("workspace/iso-extract/battle-raw/BATTLE_BATRES.X")
raw.write_bytes(extract_file(img, "BATTLE/BATRES.X"))
print("raw", raw.stat().st_size)
PY
python3 scripts/decompress_gzipps.py \
  workspace/iso-extract/battle-raw/BATTLE_BATRES.X \
  workspace/iso-extract/battle-dec/BATRES.X.dec
xxd -l 16 workspace/iso-extract/battle-dec/BATRES.X.dec
```

## 3. Import in Ghidra

1. **File → Import File…** → `workspace/iso-extract/battle-dec/BATRES.X.dec`
2. **Format:** Raw Binary (not PS-X EXE unless it really is `SCUS`)
3. **Language:** MIPS · default **32-bit little-endian** (PSX)
4. After import, open the file. If **Auto Analyze** pops up, you can run it now **or**
   fix the image base first (recommended), then analyze.
5. **Window → Memory Map** → select the block → pencil / **Set Image Base** (or
   right‑click block → **Set Image Base**):
   - BATRES → **`0x801B0000`**
   - BATTLE → **`0x800A0000`**
6. **Analysis → Auto Analyze…** → Analyze (defaults OK).

### Make code + a function (do **not** rely on `F`)

On many Ghidra installs / tool configs, **`F` = define float data**, not “function”.
That matches “press F → s float”. Use the menu instead.

1. **G** (or **Navigation → Go To…**) → type `801B0000` → Enter.
   Listing should show address **`801b0000`**, not `00000000`.
2. Click the **first byte** of that line in the Listing (left/code window).
3. If you only see `??` or undefined bytes:
   - Press **`D`** (**Disassemble**), **or**
   - Right‑click → **Disassemble**.
4. You should see MIPS, e.g. `addiu sp,sp,-0x88` (or similar). Then:
   - Right‑click the instruction → **Function → Create Function**
   - Menu path alternate: **Edit → Create Function** (wording varies slightly by version)
5. Decompiler (right) should fill in `undefined FUN_801b0000(...)` or similar.
6. Optional rename: click the function name in the Decompiler or Listing → **`L`**
   (or right‑click → **Rename Function**).

| Key | Usually means |
|-----|----------------|
| **`D`** | Disassemble (bytes → instructions) — use this first |
| **`C`** | Clear code/data (undo bad disassembly) |
| **`G`** | Go to address |
| **`L`** | Label / rename |
| **`F`** | Often **float** data type — **not** reliable for “create function” |

If **Create Function** is greyed out: bytes are still data, or a function already
exists there, or the cursor is not on an instruction (click the mnemonic column).

PSX/psyq plugin: optional; helpful for `SCUS_941.63`, not required for overlays.

## 4. Cross-overlay calls (BATRES → BATTLE / SCUS)

In-game, BATRES sits at `801B0000` while **BATTLE.X** is already loaded at
`800A0000` and **SCUS** at `80010000`. So BATRES contains real calls like:

```text
jal 0x800A7254    ; code lives in BATTLE.X, not in the BATRES file
jal 0x80014540    ; code lives in SCUS
```

Ghidra only knows about bytes you imported. In a **BATRES-only** program those
targets are **outside memory** — double-click / decompiler will not open them.

You do **not** need one magic “link overlays” button. Pick a workflow:

### Recommended: two (or three) separate programs in one project

Simplest. No merged memory. You jump by address yourself.

1. Same Ghidra **project** (e.g. `FF7-battle`).
2. Import and open **BATRES.X.dec** @ `801B0000` (you may already have this) →
   name the program something like `BATRES`.
3. **File → Import File…** again → `BATTLE.X.dec` → Raw Binary → MIPS 32 LE →
   open it → Memory Map image base **`0x800A0000`** → Auto Analyze →
   program name e.g. `BATTLE`.
4. Optional third import: `SCUS_941.63` (see §7) @ **`0x80010000`**.
5. How to “follow” a `jal 800A7254` from BATRES:
   - In the BATRES Listing, read the target: `800A7254`.
   - **Window → BATRES** vs tool tabs: open the **BATTLE** CodeBrowser
     (double-click `BATTLE` in the Project window — second tool window is fine).
   - In **BATTLE**, press **G** → type `800A7254` → Enter.
   - **D** if needed, then **Function → Create Function**, decompile there.
6. Paste / compare decompiles side by side. Xrefs in BATRES will still show
   `jal 0x800A7254` as an external-looking address; that is normal.

You never merge the files. Victory flow RE is mostly reading BATRES and only
opening BATTLE when you care what `800A7254` / `800A3354` / `800A56B0` do.

### Optional advanced: both overlays in **one** program (shared Memory Map)

Use this only if you want clickable `jal` inside a single Listing. Easy to get
wrong; **two programs is enough for fanfare work.**

1. Open **BATRES** (base `801B0000`) as the main program.
2. **Window → Memory Map**.
3. Toolbar in Memory Map: **Add Block** (“+” / green plus — label varies).
4. Add Block dialog (typical fields):
   - **Block Name:** `BATTLE`
   - **Start Address:** `800A0000`
   - **Length:** size of decompressed BATTLE (e.g. `0x538AC` / 342188)
     or set End so length matches file size.
   - **Read / Write / Execute:** enable at least **Read** + **Execute**.
   - **Type:** Initialized
   - **File offset / bytes:** map from `BATTLE.X.dec`
     (file offset `0`, length = full file). Use **Import from file** /
     **File Bytes** if your Ghidra build offers it when adding the block.
5. OK → confirm Memory Map shows:
   - block around `801B0000` (BATRES, short)
   - block `800A0000`–… (BATTLE, long)
   - **no overlap** (they must not occupy the same addresses).
6. **G** → `800A7254` should land in the BATTLE block. **D** + Create Function.
7. Re-run **Auto Analyze** if `jal` targets still look unresolved.
8. Optional: add another block for SCUS body at `80010000` the same way.

If **Add Block** has no “from file” option: **File → Add To Program…** (some
Ghidra versions) and choose `BATTLE.X.dec` with load address `800A0000`, or
stick to **two programs** above.

### What you should *not* expect

| Expectation | Reality |
|-------------|---------|
| Auto-analyze on BATRES alone follows `jal 800A…` | **No** — those bytes are not in the file |
| One “link PSX overlays” checkbox | **No** (unless a custom plugin adds it) |
| Project tree alone merges RAM | **No** — each program has its own memory |

### Practical fanfare workflow

1. Stay in **BATRES** / `batres_victory` for control flow (`801B0278`–`0540`).
2. Note external targets: `800A7254`, `800A3354`, `800B1060`, `800A56B0`, `80014540`.
3. Switch to **BATTLE** or **SCUS** program → **G** → that address → decompile.
4. Send both decompiles when asking for patch help.

## 5. Sanity checks (BATRES)

| VA | Expect |
|----|--------|
| `801B0000` | function prolog (`addiu sp, sp, -…`) |
| `801B0278` | `jal 0x801B0E20` |
| `801B03A0` | `ori s4, zero, 0x31` |
| `801B03D0` / `801B042C` | `jal 0x80014540` |
| `801B0524` | `jal 0x800A56B0` (rewards) |

If you see `00000278` instead of `801B0278`, image base is still **0**.

## 6. Useful decompile targets (fanfare)

- BATRES: **`801B0000`**, especially **`801B0270`–`801B0540`**, and **`801B0E20`**
- BATTLE: **`800A7254`**, **`800A3354`**, **`800B1060`**, **`800A56B0`**
- SCUS: **`80014540`**, **`80033E34`**, **`80033CB8`** (note: `80033E34` is a global frame pump, not victory-only)

## 7. SCUS (kernel) for `80014540` etc.

```bash
# extract
python3 << 'PY'
from pathlib import Path
from scripts.psx_mode2_iso import extract_file
img = bytearray(Path("workspace/pristine/FINALFANTASY7_D1.bin").read_bytes())
Path("workspace/iso-extract/battle-raw").mkdir(parents=True, exist_ok=True)
data = extract_file(img, "SCUS_941.63")
Path("workspace/iso-extract/battle-raw/SCUS_941.63").write_bytes(data)
print(len(data), data[:8])  # b'PS-X EXE'
PY
```

Import options:

- **PS-X EXE** loader if Ghidra/PSX plugin offers it (sets base for you), or
- Raw: skip first **`0x800`** bytes of the file, load remainder at **`0x80010000`**.

SCUS is **not** GZIPPS — do not run `decompress_gzipps.py` on it.

## 8. Existing decompressed copies

May already exist (same bytes, any path works for Ghidra):

- `workspace/iso-extract/BATTLE_X_dec.bin` — BATTLE @ `800A0000`
- `workspace/iso-extract/noswap-re/BATTLE__BATRES.X.dec` — BATRES @ `801B0000`
- `workspace/iso-extract/noswap-re/BATTLE__BATTLE.X.dec`

Do not commit large `.bin` / `.dec` extracts unless the project already tracks them on purpose.
