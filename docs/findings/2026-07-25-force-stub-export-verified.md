# FIELD.BIN.dec.patched export verified

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [patch-log-force-stub](2026-07-25-patch-log-force-stub.md)

## Summary

Raw export contains FORCE stub at file offset `0xBB7C`.

## xxd

```
0000bb7c: 00 48 02 40 06 80 01 3c 19 2f 23 90 ff 00 42 30
0000bb8c: 2b 10 43 00 23 10 02 00 07 80 01 3c 3c 17 22 a4
```

Matches assembled stub through `sh g_danger`.

## Next

Compress → `FIELD.BIN.new` → reinsert ISO → DuckStation.
