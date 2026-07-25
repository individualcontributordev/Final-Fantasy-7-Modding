# Dual jal path intact after FORCE stub

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [force-stub-complete-ghidra](2026-07-25-force-stub-complete-ghidra.md)

## Summary

Delay slot disassembled; second `jal increment_step_id` and Danger threshold path unchanged.

## Listing

```
800abbd8  nop
800abbdc  lui / lbu DAT_80062f1b / andi / sltu   preempt flag path
800abc10  jal increment_step_id                 threshold roll — intact
800abc14  nop
800abc1c  lhu g_danger                          threshold uses Danger
```

## Next

Export Ghidra program → `FIELD.BIN.dec.patched` → compress → ISO → DuckStation.
