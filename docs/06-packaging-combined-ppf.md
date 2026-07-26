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
| [scripts/apply_force_stub_rcnt2.py](../scripts/apply_force_stub_rcnt2.py) | Writes stub into a `.dec` |
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

### 3. Apply encounter stub to *that* binary

```bash
cd "$(git rev-parse --show-toplevel)"

python scripts/decompress_field_bin.py workspace/iso-extract/FIELD.BIN.makou

cp workspace/iso-extract/FIELD.BIN.makou.dec \
   workspace/iso-extract/FIELD.BIN.dec.patched

python scripts/apply_force_stub_rcnt2.py \
   workspace/iso-extract/FIELD.BIN.dec.patched

xxd -g1 -s 0xBB7C -l 16 workspace/iso-extract/FIELD.BIN.dec.patched
# must start: 80 1f 01 3c 20 11 22 8c

python scripts/compress_field_bin.py \
  workspace/iso-extract/FIELD.BIN.dec.patched \
  workspace/iso-extract/FIELD.BIN.makou \
  workspace/iso-extract/FIELD.BIN.new
```

`compress_field_bin.py` keeps the 8-byte GZIPPS header from the **Makou** `FIELD.BIN` (second argument). It tries gzip levels and prefers a result **≤ original size** (Python gzip can be a few bytes larger than the game’s compressor — e.g. +4). If still larger, do **not** truncate in CDmage.

### 4. Reimport into the Makou disc

1. Open the **same** Makou-saved `.cue` in CDmage.
2. Import `FIELD.BIN.new` over **`FIELD/FIELD.BIN`**.
3. If “shorter… pad with zeros?” → **Yes**.
4. If “longer… truncated?” → **Cancel** (wrong source; redo step 2–3).
5. Save image (unlock/read-only if “Cannot write”).
6. DuckStation smoke: boot, field, a fight, optionally preempt flag `0x800716D0` (4↔0).

### 5. Make one PPF

| MakePPF role | File |
|--------------|------|
| **Original** | Untouched retail `.bin` (same dump family you always use) |
| **Modified** | Final image after steps 1–4 (Makou **+** stub) |

Output e.g. `yourmod-disc1.ppf`. Do **not** create separate Makou-only and encounter-only PPFs for end users.

### 6. Sanity-check the PPF

Apply `yourmod-disc1.ppf` to a **second** fresh retail `.bin` and boot once.

## End users

```
fresh retail .bin  +  yourmod-disc1.ppf  →  play
```

No Makou, no CDmage, no Python.

## Dev-only: stub on stock FIELD.BIN

For testing the stub **without** Makou (as during RE):

```bash
python scripts/decompress_field_bin.py workspace/iso-extract/FIELD.BIN
cp workspace/iso-extract/FIELD.BIN.dec workspace/iso-extract/FIELD.BIN.dec.patched
python scripts/apply_force_stub_rcnt2.py workspace/iso-extract/FIELD.BIN.dec.patched
python scripts/compress_field_bin.py \
  workspace/iso-extract/FIELD.BIN.dec.patched \
  workspace/iso-extract/FIELD.BIN \
  workspace/iso-extract/FIELD.BIN.new
```

Do **not** use that `.new` on a Makou ISO unless sizes/indexes match.

## Related

- [04-workflow.md](04-workflow.md) — decompress / compress / test loop  
- [02-disc-format.md](02-disc-format.md) — Makou / ff7tk ISO save  
- [findings/2026-07-25-patch-log-force-stub.md](findings/2026-07-25-patch-log-force-stub.md)  
- [findings/2026-07-25-makou-iso-save-path.md](findings/2026-07-25-makou-iso-save-path.md)  
