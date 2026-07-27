# WORLD.BIN load base = 0x800A0000

**Date:** 2026-07-28  
**Confidence:** confirmed  
**Related:** [world-bin-extract](2026-07-28-world-bin-extract.md), [align-ghidra-duckstation-base](2026-07-25-align-ghidra-duckstation-base.md)

## DuckStation (on world map)

Needle = start of `WORLD.BIN.dec`:

```
4e 45 57 20 20 00 00 00 4f 4c 44 20 20 00 00 00  # "NEW  " / "OLD  "
4a 55 4d 50 20 00 00 00 46 52 4f 4d 20 00 00 00  # "JUMP " / "FROM "
```

| Hit (DuckStation) | PS1 VA | Notes |
|-------------------|--------|--------|
| `000A0000` | **`0x800A0000`** | module base |
| `000A0010` | `0x800A0010` | same image; second string at file +0x10 |

Same overlay window as `FIELD.BIN` — Field and World are not resident together.

## Ghidra

Import `WORLD.BIN.dec` as Raw Binary, MIPS R3000 LE, base **`0x800A0000`**.
