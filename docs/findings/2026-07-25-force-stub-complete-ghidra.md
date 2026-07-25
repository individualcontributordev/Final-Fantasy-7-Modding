# FORCE stub + jal restore complete (Ghidra)

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [force-stub-patched-jal-clobber](2026-07-25-force-stub-patched-jal-clobber.md)

## Summary

Ghidra FIELD image now has the full in-place FORCE stub and restored first `jal increment_step_id`.

## Listing (verified)

```
800abb7c–800abb98  mfc0…sh g_danger     FORCE stub
800abb9c–800abbd0  nop ×14
800abbd4  jal increment_step_id         restored (72 ae 02 0c)
800abbd8  00 00 00 00                   delay (shown as ?? until Disassemble)
800abbdc  lui / lbu DAT_80062f1b        preempt path continues
```

## Follow-ups

- [ ] Disassemble `0x800ABBD8` as `nop`
- [ ] Confirm second `jal` @ `0x800ABC10` intact
- [ ] Export patched `FIELD.BIN.dec` → rebuild ISO → DuckStation
