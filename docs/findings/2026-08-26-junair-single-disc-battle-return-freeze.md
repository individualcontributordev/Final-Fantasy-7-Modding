# Finding: JUNAIR (field 384) freezes returning from battle on single-disc-on-csr — encounter/SCENE.BIN hypothesis disproven

**Date:** 2026-08-26
**Status:** root cause narrowed, not yet fixed
**Stack:** CSR + Single-disc only (core build, no movie-relocation layer) — reproduces identically with and without movie-relocation, so unrelated to that patch.

## Symptom

At JUNAIR (field id 384, game moment 1016, CSR D2 content), field loads fine.
Triggering a random encounter, finishing the battle, and returning to the
field freezes the game. Confirmed on both `bisect_core_no_relocation.bin`
and `playtest_movie_relocation.bin` (patched). Does **not** freeze on stock
CSR Disc 2 alone.

## Disproven hypothesis (false lead)

Original theory: single-disc merges CSR D2's JUNAIR.DAT wholesale onto a D1
base, but the build only ships D1's `BATTLE/SCENE.BIN`, so JUNAIR's D2
encounter table might reference scene indices invalid on D1.

**Disproved by direct comparison:**
- `FIELD/JUNAIR.DAT` encounter section (48 bytes) is **byte-identical**
  between CSR D1 and CSR D2.
- `BATTLE/SCENE.BIN` is **byte-identical** (270,336 bytes) between CSR D1
  and CSR D2.

So there is no encounter-table/scene-index mismatch for JUNAIR at all — the
D1 and D2 copies of this field have identical battle configuration.

## What actually differs between D1 and D2 JUNAIR.DAT

Full script-slot diff (736 script slots compared): only **one** slot differs,
`('air0', 3)`:

- **D1** (19 bytes): `IFSW(cond=0x0b) → MAPJUMP(60810111f1f6fb410000) → RET`
- **D2** (57 bytes): `IFSW(cond=0x31) → AKAO(f2 00 00 00 c1 78 00 00 00 00 00 00 00 00) → PRTYE(cafefefe) → PRTYE(ca02fefe) → MMBLK(ce02) → BITON(8210e206) → MAPJUMP(609201b0002500010080) → MAPJUMP(60810111f1f6fb410000, same tail as D1) → RET`

`merge_safe_fields.py` classifies JUNAIR as "CSR only edited D2" (D1 copy is
untouched pristine-equivalent for this slot) and takes CSR D2's file
wholesale — this is exactly per its documented behavior, not a bug in the
merge script itself.

Per `docs/findings/2026-08-24-akao-opcode-0xf2-is-canonon-cd-call-site.md`,
opcode `0xF2` (`AKAO`) issues a **raw CD-XA command with parameters
compiled as literal constants in the field's own script bytes** (cmd code,
sector/size fields) — it does **not** go through `MOVIE_ID.BIN`, so the
prior movie-relocation fix cannot affect this at all (consistent with the
freeze being identical with/without that patch).

## `air0`/slot-3 hypothesis: DISPROVEN (2026-08-26 update)

Playtester confirmed this `air0` slot-3 block is gated by a **line trigger**
(walk-into-line script call) that is not being hit in the reproduction —
the freeze happens right after a battle, well before that trigger point in
the field. So this branch cannot be the cause regardless of the `IFSW`
flag state.

This also means **no genuine JUNAIR.DAT content difference explains the
freeze**: a full script-slot diff (736 slots) plus section-by-section diff
confirms `air0`/slot-3 (unreachable here) is the *only* content delta —
`walkmesh`, `background`, `camera`, `inf`, `encounter`, and `model_loader`
sections are all byte-identical D1 vs D2, and all 735 other script slots
match exactly. Text section differs by only 2 bytes total (padding), no
script logic difference.

**Conclusion: the cause is not inside `FIELD/JUNAIR.DAT` at all.** It must
be something else in the battle-return path: engine/global state, a
different shared file (battle module common code, VRAM/module data,
audio/CD-DA track layout affected by the single-disc merge), or something
disc-layout-dependent that isn't visible in this field's own file content.

## Root cause identified (2026-08-26 update): 2MB address-wrap memory corruption

DuckStation debug log (`docs/logs`) captured the exact corruption event, just
before the permanent hang:

```
[86751.8750] D/CodeCache: Page fault handler invoked at PC=... Address=0x2abd3800000 (write), fastmem offset 80200000
[86751.8750] D/CodeCache: Backpatching store at ... (pc 80034E54 addr 80200000) ...
[86751.8750] D/CodeCache: Page fault on protected RAM @ 0x00000000 (page #0), invalidating code cache.
[86751.8750] D/CodeCache: Page fault handler invoked at PC=... Address=0x2abd3800001 (write), fastmem offset 80200001
[86751.8750] D/CodeCache: Backpatching store at ... (pc 80034EFC addr 80200001) ...
[86751.8750] D/CodeCache: Page fault handler invoked at PC=... Address=0x2abd3800016 (read), fastmem offset 80200016
[86751.8750] D/CodeCache: Page fault on protected RAM @ 0x00001000 (page #1), invalidating code cache.
[86751.8750] E(ReadBlockInstructions): Instruction read failed at PC=0x80000084, truncating block.
[86751.8750] W(Compile_Fallback): Compiling instruction fallback at PC=0x80000080, instruction=0x4CF9C255
[86751.9688] V/PerfMon: FPS: 0.00 ...
```

**Mechanism:**
- Something (guest PCs `0x80034E54` / `0x80034EFC` / `0x80034EF4`, inside the
  BIOS SPU/CD low-level driver work area — no application symbol resolves
  here) issues writes to guest address **`0x80200000`+** (2MB above the base
  of PS1 RAM).
- The PS1 only decodes the **low 21 bits** of RAM addresses (2MB physical
  RAM, mirrored every 2MB up to the 8MB KUSEG window). `0x80200000 &
  0x1FFFFF = 0x00000000` — so this write **wraps around and aliases onto
  address `0x00000000`**, which is the **kernel exception-vector / jump
  table** (`0x00000000`–`0x00001FFF`, pages 0–1) that the BIOS installs at
  boot and uses for every hardware interrupt dispatch.
- DuckStation's log confirms this: immediately after the `0x80200000`-range
  writes, it reports `"Page fault on protected RAM @ 0x00000000 (page #0)"`
  and `"@ 0x00001000 (page #1)"` — i.e. **self-modifying code detected in
  the kernel vector table itself**.
- One frame later, `"Instruction read failed at PC=0x80000084"` — the CPU
  tries to execute the now-corrupted exception vector when the next
  hardware interrupt fires (`CAUSE=0x00000400`, matches the earlier-reported
  freeze register dump) and reads garbage (`0x4CF9C255`, previously
  misdecoded as a bogus `cop3` instruction). **The BIOS interrupt handler is
  now permanently broken**, so every subsequent interrupt jumps into
  garbage and the CPU never returns to game logic — this is the observed
  infinite loop at `PC=0x80000080`.

**Conclusion:** this is not a CD-ROM seek/track problem (the background
XA audio stream logged in the same window is a red herring — it's
interrupt-driven and keeps limping along independently of the corrupted
main-thread vector). The actual bug is a **2MB (`0x200000`) address-wrap
memory stomp** onto the exception-vector table, triggered by some
battle-end/field-reinit code path computing a pointer or DMA length that
overruns by exactly one RAM-mirror period. This is disc-layout/build
dependent (present on merged single-disc, absent on stock CSR D2 alone),
consistent with a buffer size, table index, or base pointer that differs
between the two builds (e.g. something sized/offset relative to a battle
module load address, DAT file size, or shared work-buffer length that is
correct on D2 alone but off by 2MB on the single-disc merge).

## Next steps

1. Set a **write breakpoint** in DuckStation at guest address range
   `0x00000000`–`0x00001FFF` (kernel vector table) — this will catch the
   *first* moment battle-return code stomps it, well before the freeze
   becomes visible.
2. Alternatively, breakpoint execution at `0x80034E54` (the guest PC seen
   issuing the bad write) and inspect the register holding the target
   address right before the store — that register should reveal the
   miscalculated pointer/offset and its expected (correct) value.
3. Once the write is caught, trace back to the calling code (call stack at
   that point) to identify which battle-end/field-reinit routine computes
   the bad 2MB-off address — likely a buffer size or module-load-address
   calculation that differs between stock CSR D2 and the merged
   single-disc image.
4. Compare battle/field-common module load addresses and buffer-size
   constants between stock CSR D2 and the single-disc merge to find what's
   sized/offset differently by (or near) `0x200000`.

## False leads (for future readers)

- Encounter table mismatch: **disproved**, tables identical byte-for-byte.
- SCENE.BIN D1 vs D2 mismatch: **disproved**, files identical byte-for-byte.
- Movie-relocation patch (`ship_movie_relocation_v010.py`): **ruled out** —
  freeze reproduces identically on the core build without that layer
  applied at all.
- `air0`/slot-3 `AKAO(0xF2)` script delta: **disproved** — this block is
  gated by a line trigger not hit before the freeze occurs, and no other
  JUNAIR.DAT content differs between D1 and D2. The freeze source is
  outside this file entirely.
