# CDmage: pad shorter FIELD.BIN.new import

**Date:** 2026-07-25  
**Confidence:** likely  
**Related:** [cdmage-field-bin-path](2026-07-25-cdmage-field-bin-path.md), [force-stub-compressed](2026-07-25-force-stub-compressed.md)

## Summary

After restoring pristine test ISO, `FIELD/FIELD.BIN` shows size **85435** (correct). Importing `FIELD.BIN.new` (85355) yields:

> Import file is shorter than file in the image. Should it be padded with zeros to match the size?

This is expected (−80 gzip size). **Yes** = pad trailing zeros to keep ISO directory size; gzip payload should still decompress (trailer ignored).

## Do not

- Choose options that truncate
- Import `FIELD.BIN.dec.patched`

## Next

Pad Yes → save image → DuckStation smoke test.
