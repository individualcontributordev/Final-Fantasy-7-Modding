# WorldRand single-call xrefs are not encounter check

**Date:** 2026-07-28  
**Confidence:** confirmed (reject trio)  
**Related:** [worldrand](2026-07-28-worldrand.md), [world-4000-scalar-miss](2026-07-28-world-4000-scalar-miss.md)

## Rejected

| Function | Why not encounter |
|----------|-------------------|
| `FUN_800b0250` | Fills 256-word table with `WorldRand()<<2` (init) |
| `FUN_800a21b4` | `WorldRand();` return **discarded** — movement scramble (wiki) |
| `FUN_800abb24` | Script opcode switch; case `0x10` / `16` just **returns** `WorldRand()` |

## Still good candidates (multi-call)

| Function | `# jal WorldRand` |
|----------|-------------------|
| `FUN_800b0810` | 2 |
| `FUN_800b307c` | 3 |
| `FUN_800b5314` | 2 |
| `FUN_800b7c7c` | 8 |

## Next

**DuckStation breakpoint** on `WorldRand` @ `0x800ADFC0` while walking hostile grass → read **RA** (return address) on hits that precede a battle. That RA−8 (ish) is the `jal` in the real encounter check.
