# Kernel EXE (all 3 discs) ruled out for CANONON movie-id-47 hardcode

## Evidence

Decompiled kernel EXEs for all three discs, base `0x80010000`:
- `workspace/ghidra/SCUS_941.63_disc1.c` (36,672 lines)
- `workspace/ghidra/SCUS_941.64_D2.body.c` (27,843 lines)
- `workspace/ghidra/SCUS_941.65_D3.body.c` (27,843 lines)

Extraction reproducible via `python3 scripts/extract_kernel_exe.py D2 D3`.

### CD-command dispatcher is identical across discs

`FUN_8002da7c` (the `DAT_8009a000`-keyed CD-command dispatcher) sits at the
same address in all three kernels. Diffed the full function bodies
(disc1 line 14105 vs disc2 line 16079): byte-for-byte identical logic —
only cosmetic Ghidra decompile differences (`DAT_` vs `_DAT_` naming,
explicit vs implicit `param_2`/`param_3` register args). No disc-specific
branch exists in the dispatcher.

### No literal `0x2f` (47) / `47` movie-id constant

`grep -n "== 0x2f\|== 47\|!= 0x2f\|!= 47"` across all three kernel exports
only matches an unrelated sentinel `0x2fffffff` (list-terminator pattern
in an unrelated table-walk function), in all three discs identically.

### Movie-streaming primitives have no in-file caller (any disc)

CD-streaming-queue helpers, all at the same addresses on every disc:

- `FUN_80033dac` (mode `1`)
- `FUN_80033e34` (mode `3`)
- `FUN_80033e74` (mode `0xb`, movie streaming)
- Blocking wrappers: `FUN_80033edc`, `FUN_80033f40`, `FUN_80033fc4`
  (one per mode above, retry-loop around the non-blocking version)

`FUN_80033f40` (mode-3 blocking wrapper) **is** called locally, several
times, always as generic overlay loading against `SUB_800a0000` (matches
the known `FIELD.BIN`/battle-overlay load address, already ruled out for
movie logic separately).

`FUN_80033dac`, `FUN_80033e34`, `FUN_80033e74`, and their blocking
wrappers `FUN_80033edc`/`FUN_80033fc4` have **zero call sites** inside any
of the three kernel EXE bodies. `FUN_80033fc4` (blocking wrapper around
the movie-mode `0xb` primitive) is present in the disc-2/3 kernels but
absent entirely from disc 1 — this looked like a promising divergence at
first, but since it has no caller in disc-2/3 either, it's dead code left
by the linker, not a functional difference.

## Conclusion

The kernel EXE, on **all three discs**, only exposes the movie-streaming
primitive (`FUN_80033e74`/mode `0xb`) — it never calls it. Whatever
resolves a movie ID to an LBA and invokes that primitive lives in a
**third module**, not the kernel EXE and not `FIELD.BIN` (already ruled
out in `2026-08-24-field-bin-pmvie-movie-mvief-handlers-located.md`).

## Next step

Identify what other loadable module (likely a dedicated movie-player
overlay, distinct from `FIELD.BIN` and the kernel EXE) calls
`FUN_80033dac`/`FUN_80033e34`/`FUN_80033e74`. That module is where the
CANONON/movie-id-47 disc-repoint-ignoring behavior must be implemented.
