# Patch: FORCE encounter stub (RCnt2)

**Date:** 2026-07-25  
**Target:** `FIELD.BIN` (GZIPPS) → decompressed `.dec`  
**VA base:** `0x800A0000`

## Goal

Replace vanilla Danger `+=` with lure-scaled independent FORCE using PSX **RCnt2**, so normal encounters feel random while StepID/Offset preempt routing stays intact.

## Apply (preferred)

```bash
# One-shot per builder base (downloads CSR layer if needed):
python scripts/build_encounter_on_base.py --against csr-plus --discs 1 --version 0.1.1

# Or stub-only into an existing .dec:
python scripts/apply_force_stub_rcnt2.py path/to/FIELD.BIN.dec.patched
```

For **Makou + this stub → one PPF**, follow [docs/06-packaging-combined-ppf.md](../../../docs/06-packaging-combined-ppf.md).

## File offsets

| Dec offset | VA | Bytes | Meaning |
|------------|-----|-------|---------|
| `0xBB7C` | `0x800ABB7C` | 88 | stub (`stub-bb7c.hex`) |
| `0xBBD4` | `0x800ABBD4` | 4 | must stay `jal increment_step_id` (`jal-bbd4.hex`) |

## Path logic

```
step fraction wraps
  → stub sets g_danger to 0xFFFF or 0 from RCnt2 vs (lure/2)
  → jal increment_step_id   (preempt — unchanged)
  → jal increment_step_id   (threshold — unchanged)
  → vanilla Danger vs Lure/Away compare
  → battle if threshold passes (FORCE almost always does)
```

## Shipped rates

```
entropy = *(u32*)0x1F801120        # RCnt2
thresh  = g_enemy_lure scaled by rate (see table)
if ((entropy & 0xff) < thresh)
    g_danger = 0xFFFF
else
    g_danger = 0
```

| Rate pack | Formula | At lure 16 | Hex file |
|-----------|---------|------------|----------|
| **25%** | `lure / 4` | ~1.56% | `stub-bb7c-rate25.hex` |
| **50%** | `lure / 2` | ~3.13% | `stub-bb7c-rate50.hex` (also `stub-bb7c.hex`) |
| **75%** | `lure × 3/4` | ~4.69% | `stub-bb7c-rate75.hex` |

Lure/Away materia still scale `g_enemy_lure`. Builder add-ons share `exclusiveGroup: encounter-rate`.

```bash
python scripts/build_all_encounter_rates.py
# or: python scripts/build_encounter_on_base.py --against clean --rate 25 --discs 1
```

## Playtest

- Sparse encounters (not every StepID+2)  
- Lure poke 1 / 16 / 64 → none / normal / a lot  
- Preempt flag `0x800716D0` still 4↔0  
- Revs: dense raw → `* 3/4` → still dense → **`/ 2` (shipped)**  

## Files in this folder

| File | Contents |
|------|----------|
| `stub-bb7c.hex` | 88-byte LE stub |
| `jal-bbd4.hex` | `72 ae 02 0c` |
| `README.md` | this log |

## Finding links

- [docs/findings/2026-07-25-patch-log-force-stub.md](../../../docs/findings/2026-07-25-patch-log-force-stub.md)  
- [docs/findings/2026-07-25-playtest-rcnt2-sparse.md](../../../docs/findings/2026-07-25-playtest-rcnt2-sparse.md)  
- Public write-up: [articles/remaking-field-encounters.md](../../../articles/remaking-field-encounters.md)  
