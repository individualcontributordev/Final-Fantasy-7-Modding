# Mislabel: FUN_800c4148 is not WorldRand

**Date:** 2026-07-28  
**Confidence:** confirmed (reject)  
**Related:** [worldseedrand](2026-07-28-worldseedrand.md)

## What happened

Scalar `0x208` hits include scratchpad addresses `0x1F800208` inside a **large** function at **`0x800C4148`** (stack frame `0x98`, params, GPU/scratch setup). That was renamed `WorldRand` — **incorrect**.

True `WorldRand` (wiki) is a **tiny** helper: ++index, if `> 0x208` scramble + clear, return one buffer byte.

## Keep

| Symbol | VA |
|--------|-----|
| `WorldSeedRand` | `0x800ADEA8` |
| index init `ori v0,zero,0x208` | `0x800ADFA4` (inside seed; matches wiki end state) |

## Do next

1. Rename `0x800C4148` back away from `WorldRand` (e.g. restore `FUN_800c4148`).
2. From `WorldSeedRand`, list every `jal` — expect **three** calls to `WorldScrambleRand`.
3. Label scramble; find the small sibling that wraps at `0x208` and returns a byte → real `WorldRand`.
