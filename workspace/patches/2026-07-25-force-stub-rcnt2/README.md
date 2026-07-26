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

## Shipped rate

```
entropy = *(u32*)0x1F801120        # RCnt2
thresh  = g_enemy_lure / 2         # 50% of raw lure byte
if ((entropy & 0xff) < thresh)
    g_danger = 0xFFFF
else
    g_danger = 0
```

**P(FORCE) ≈ (g_enemy_lure / 2) / 256 = g_enemy_lure / 512** per check.

| At lure | thresh | ≈ P(FORCE) | vs raw `lure/256` |
|---------|--------|------------|-------------------|
| 16 (default) | 8 | **3.13%** | **50%** |
| was `* 3/4` | 12 | 4.69% | 75% |
| was raw | 16 | 6.25% | 100% |

Lure/Away materia still scale `g_enemy_lure`.

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
