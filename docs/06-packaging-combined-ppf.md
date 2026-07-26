# Packaging: Makou + encounter stub → one PPF

How to ship **Makou Reactor field edits** and the **FIELD.BIN encounter FORCE stub** as a **single PPF** that others apply to a fresh retail `.bin`.

PPF does **not** stack. Always: pristine dump → final combined image → one `.ppf`.

## What each piece changes

| Piece | Touches | Does not touch |
|-------|---------|----------------|
| Makou | `FIELD/*.DAT` (etc.), and may update **`FIELD.BIN` index** | Encounter engine code (unless it recompresses `FIELD.BIN`) |
| Encounter stub | Decompressed `FIELD.BIN` code @ file `0xBB7C` | Per-map `.DAT` files |

**Never** import a stock-based `FIELD.BIN.new` onto a Makou ISO if Makou’s `FIELD.BIN` is a different size — you can wipe the index or hit CDmage truncate. Always patch **the `FIELD.BIN` extracted from the Makou-saved disc**.

## Patch package

| Path | Role |
|------|------|
| [workspace/patches/2026-07-25-force-stub-rcnt2/](../workspace/patches/2026-07-25-force-stub-rcnt2/) | Stub bytes + log |
| [scripts/build_field_encounter_patch.py](../scripts/build_field_encounter_patch.py) | **One-shot:** decompress → stub → compress |
| [scripts/make_ppf.py](../scripts/make_ppf.py) | Create RomPatcher.js-compatible **PPF 3.0** from two `.bin`s |
| [scripts/apply_ppf.py](../scripts/apply_ppf.py) | Apply a **.ppf** to a pristine `.bin` |
| [scripts/apply_force_stub_rcnt2.py](../scripts/apply_force_stub_rcnt2.py) | Stub only (into a `.dec`) |
| [scripts/decompress_field_bin.py](../scripts/decompress_field_bin.py) | GZIPPS → `.dec` |
| [scripts/compress_field_bin.py](../scripts/compress_field_bin.py) | `.dec` → GZIPPS `.new` |

## Build final disc (author)

### 1. Makou first

1. Copy a fresh retail disc → working image (e.g. `ff7_disc1_work.bin` + `.cue`).
2. Open in Makou → apply all field edits → **Save ISO**.
3. Close Makou.

### 2. Extract Makou’s `FIELD.BIN`

In CDmage (or your ISO tool), from the **Makou-saved** image:

- Extract `FIELD/FIELD.BIN` → e.g. `workspace/iso-extract/FIELD.BIN.makou`

### 3. Apply encounter stub (one command)

```bash
cd "$(git rev-parse --show-toplevel)"

python scripts/build_field_encounter_patch.py workspace/iso-extract/FIELD.BIN.makou
# writes workspace/iso-extract/FIELD.BIN.new
# optional: -o path/to/out.new   --keep-dec
```

If compress reports growth and you have zopfli:

```bash
pip install zopfli
python scripts/build_field_encounter_patch.py workspace/iso-extract/FIELD.BIN.makou
```

Do **not** accept CDmage truncate if still larger.

### 4. Reimport into the Makou disc

1. Open the **same** Makou-saved `.cue` in CDmage.
2. Import `FIELD.BIN.new` over **`FIELD/FIELD.BIN`**.
3. If “shorter… pad with zeros?” → **Yes**.
4. If “longer… truncated?” → **Cancel** (wrong source; redo step 2–3).
5. Save image (unlock/read-only if “Cannot write”).
6. DuckStation smoke: boot, field, a fight, optionally preempt flag `0x800716D0` (4↔0).

### 5. Make one PPF

| Role | File |
|------|------|
| **Original** | Untouched retail `.bin` |
| **Modified** | Final image after steps 1–4 |

```bash
python scripts/make_ppf.py \
  workspace/iso-extract/ff7_disc1_pristine.bin \
  workspace/iso-extract/ff7_disc1_final.bin \
  -o workspace/iso-extract/yourmod-disc1.ppf \
  -d "Your mod name here" \
  --verify
```

Same PPF format as [RomPatcher.js](https://github.com/marcrobledo/RomPatcher.js) creator mode. Full disc images take a few minutes to diff.

Do **not** create separate Makou-only and encounter-only PPFs for end users.

### 6. Sanity-check the PPF

Apply `yourmod-disc1.ppf` to a **second** fresh retail `.bin` and boot once.

## End users

```bash
python scripts/apply_ppf.py path/to/fresh_retail.bin path/to/yourmod-disc1.ppf \
  -o path/to/ff7_disc1_patched.bin
```

Or use [RomPatcher.js](https://www.marcrobledo.com/RomPatcher.js/) / PPF-O-Matic in a browser — same `.ppf`.

No Makou, no CDmage required for players.

### Dev-only: stub on stock FIELD.BIN

For testing the stub **without** Makou (as during RE):

```bash
python scripts/build_field_encounter_patch.py workspace/iso-extract/FIELD.BIN
```

Do **not** use that `.new` on a Makou ISO unless sizes/indexes match.

## Related

- [04-workflow.md](04-workflow.md) — decompress / compress / test loop  
- [02-disc-format.md](02-disc-format.md) — Makou / ff7tk ISO save  
- [findings/2026-07-25-patch-log-force-stub.md](findings/2026-07-25-patch-log-force-stub.md)  
- [findings/2026-07-25-makou-iso-save-path.md](findings/2026-07-25-makou-iso-save-path.md)  
