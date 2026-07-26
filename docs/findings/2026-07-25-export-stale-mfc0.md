# Export still had mfc0 stub (stale)

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [rcnt2-stub-patched-ghidra](2026-07-25-rcnt2-stub-patched-ghidra.md)

## Evidence

```
xxd @ 0xBB7C: 00 48 02 40 06 80 01 3c …   # old mfc0 Count stub
expected:     80 1f 01 3c 20 11 22 8c …   # RCnt2 stub
```

Ghidra Listing was updated earlier; **Raw Bytes export** on disk did not get the RCnt2 bytes (unsaved program, wrong file, or export of original).

## Fix

Patch `FIELD.BIN.dec.patched` at file offset `0xBB7C` with the RCnt2 blob; confirm `xxd` before compress.
