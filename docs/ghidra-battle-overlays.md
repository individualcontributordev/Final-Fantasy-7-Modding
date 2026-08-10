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
4. **Memory Map** → set image base:
   - BATRES → **`0x801B0000`**
   - BATTLE → **`0x800A0000`**
5. **Analysis → Auto Analyze** (defaults OK)
6. Go to **`801B0000`** → **F** create function if needed

PSX/psyq plugin: optional; helpful for `SCUS_941.63`, not required for overlays.

Cross-overlay `jal 800A…` from BATRES: import BATTLE as a **second program** (or second block) if you need both; xrefs won’t always link automatically.

## 4. Sanity checks (BATRES)

| VA | Expect |
|----|--------|
| `801B0000` | function prolog (`addiu sp, sp, -…`) |
| `801B0278` | `jal 0x801B0E20` |
| `801B03A0` | `ori s4, zero, 0x31` |
| `801B03D0` / `801B042C` | `jal 0x80014540` |
| `801B0524` | `jal 0x800A56B0` (rewards) |

If you see `00000278` instead of `801B0278`, image base is still **0**.

## 5. Useful decompile targets (fanfare)

- BATRES: **`801B0000`**, especially **`801B0270`–`801B0540`**, and **`801B0E20`**
- BATTLE: **`800A7254`**, **`800A3354`**, **`800B1060`**, **`800A56B0`**
- SCUS: **`80014540`**, **`80033E34`**, **`80033CB8`** (note: `80033E34` is a global frame pump, not victory-only)

## 6. Existing decompressed copies

May already exist (same bytes, any path works for Ghidra):

- `workspace/iso-extract/BATTLE_X_dec.bin` — BATTLE @ `800A0000`
- `workspace/iso-extract/noswap-re/BATTLE__BATRES.X.dec` — BATRES @ `801B0000`
- `workspace/iso-extract/noswap-re/BATTLE__BATTLE.X.dec`

Do not commit large `.bin` / `.dec` extracts unless the project already tracks them on purpose.
