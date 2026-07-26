# Patch: FORCE encounter stub (RCnt2)

**Date:** 2026-07-25  
**Target:** `FIELD.BIN` (GZIPPS) → decompressed `.dec`  
**VA base:** `0x800A0000`

## Goal

Replace vanilla Danger `+=` with lure-scaled independent FORCE using PSX **RCnt2**, so normal encounters feel random while StepID/Offset preempt routing stays intact.

## Apply (preferred)

```bash
python scripts/apply_force_stub_rcnt2.py path/to/FIELD.BIN.dec.patched
```

For **Makou + this stub → one PPF**, follow [docs/06-packaging-combined-ppf.md](../../../docs/06-packaging-combined-ppf.md) (patch Makou’s extracted `FIELD.BIN`, not stock).

## File offsets

| Dec offset | VA | Bytes | Meaning |
|------------|-----|-------|---------|
| `0xBB7C` | `0x800ABB7C` | 88 | stub (`stub-bb7c.hex`) |
| `0xBBD4` | `0x800ABBD4` | 4 | must stay `jal increment_step_id` (`jal-bbd4.hex`) |

## Behavior

```
entropy = *(u32*)0x1F801120   # RCnt2
if ((entropy & 0xff) < g_enemy_lure)  # 0x80062F19
    g_danger = 0xFFFF
else
    g_danger = 0
```

Then vanilla dual `increment_step_id` + threshold.

## Playtest

- Sparse encounters (not every StepID+2)  
- Lure poke 1 / 16 / 64 → none / normal / a lot  
- Preempt flag `0x800716D0` still 4↔0  

## Files in this folder

| File | Contents |
|------|----------|
| `stub-bb7c.hex` | 88-byte LE stub |
| `jal-bbd4.hex` | `72 ae 02 0c` |
| `README.md` | this log |

## Finding links

- [docs/findings/2026-07-25-patch-log-force-stub.md](../../../docs/findings/2026-07-25-patch-log-force-stub.md)  
- [docs/findings/2026-07-25-playtest-rcnt2-sparse.md](../../../docs/findings/2026-07-25-playtest-rcnt2-sparse.md)  
