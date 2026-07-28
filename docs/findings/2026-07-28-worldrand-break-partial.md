# DuckStation WorldRand breakpoint hits; RA not captured yet

**Date:** 2026-07-28  
**Confidence:** partial  
**Related:** [worldrand-xrefs-reject](2026-07-28-worldrand-xrefs-reject.md)

## Evidence

Screenshots `docs/image1.png` / `docs/image2.png`:

- Execute breakpoint @ **`0x800ADFC0`** (`WorldRand` entry `lui v0,0x8011`) — **Hit Count 6**
- On world map (Midgar-area grass visible in one shot)
- `windows-last-output.txt` evidence fields still empty — **no RA values**

## Gap

Need register **`ra`** (r31) at each break — that is the return address after `jal WorldRand`. Without it we cannot jump to the caller in Ghidra.

## Tip

Enable the breakpoint only while **walking** on hostile grass (disable during load/menus) so hits aren’t drowned by init / script / scramble.
