# Builder vs Working Bin - CDROM Read Difference Analysis

**Date:** 2026-08-18  
**Issue:** Builder-downloaded bin shows black screen at disc 1→2 transition  
**Status:** 🔴 ROOT CAUSE IDENTIFIED

## TL;DR

**Both bins read the exact same sectors up to LBA 58723.**  
**After that, they diverge completely:**

- **Working bin:** Continues reading more sectors (58723-58728), then **jumps to LBA 126991** (28:13:16) and rendering resumes (FPS 17.95)
- **Broken bin:** **Stops at LBA 58722**, never reads sectors 58723-58728, **never seeks to LBA 126991**, rendering never resumes (FPS: 0.00 forever)

## Detailed Comparison

### Phase 1: Identical behavior (LBA 58700-58722)

Both bins read:
```
[13:02:57] LBA 58707-58715 (9 sectors)
[13:02:66] LBA 58716-58722 (7 sectors)  
[13:02:50] LBA 58700-58706 (7 sectors) - backward seek
```

### Phase 2: DIVERGENCE at LBA 58723

**Working bin (line 134-144):**
```
[  541.6771] D/CDROM: CDROM setloc command (13, 02, 73)
[  541.7276] D/CDROM: Read sector 58723 [13:02:73]: mode 2 submode 0x08
[  541.7281] D/CDROM: Read sector 58724 [13:02:74]: mode 2 submode 0x08
[  541.7439] D/CDROM: Read sector 58725 [13:03:00]: mode 2 submode 0x08
[  541.7441] D/CDROM: Read sector 58726 [13:03:01]: mode 2 submode 0x08
[  541.7606] D/CDROM: Read sector 58727 [13:03:02]: mode 2 submode 0x08
[  541.7608] D/CDROM: Read sector 58728 [13:03:03]: mode 2 submode 0x89
```

**Broken bin:**
- **MISSING** - Never seeks to 13:02:73
- **MISSING** - Never reads LBA 58723-58728
- Stops after reading LBA 58706

### Phase 3: Critical jump to disc 2 content

**Working bin (line 146-152):**
```
[  541.8278] D/CDROM: CDROM setloc command (28, 13, 16)  ← JUMP TO DISC 2 AREA
[  541.8298] D/CDROM: Seek time: 13:02:72->28:13:16 (68269 LBA, 455ms)
[  542.2790] D/CDROM: Read sector 126991 [28:13:16]: mode 2 submode 0x08
[  542.2957] D/CDROM: Read sector 126992 [28:13:17]: mode 2 submode 0x08
[  542.2958] D/CDROM: Read sector 126993 [28:13:18]: mode 2 submode 0x08
[  542.3121] D/CDROM: Read sector 126994 [28:13:19]: mode 2 submode 0x89

[  542.1286] V/PerfMon: FPS: 0.00 ← Black screen during seek
[  543.1312] V/PerfMon: FPS: 17.95 ← RENDERING RESUMES after reading LBA 126991-126994
```

**Broken bin:**
- **MISSING** - Never seeks to 28:13:16
- **MISSING** - Never reads LBA 126991-126994 (disc 2 content)
- **RESULT:** FPS stays 0.00 forever (lines 55-62)

## LBA Location Analysis

**LBA 58723-58728:**
- Byte offset: ~120 MB into disc
- Location: FIELD directory area
- **Hypothesis:** Contains field index or directory that tells the game where disc 2 fields are located

**LBA 126991 (28:13:16):**
- Byte offset: ~260 MB into disc  
- **This is the single-disc "disc 2" content area**
- Contains the next field to load after the transition

## Root Cause

The field script is executing (VPS ~60fps), but it's **not loading the next field** because:

1. **Either:** Sectors 58723-58728 are corrupted/missing in the builder bin, OR
2. **Or:** The field script itself has wrong opcodes that skip the CDROM read

Since we already verified **all 137 field scripts are identical** between working and broken bins, the field script opcodes are correct.

**Therefore:** The data at **LBA 58723-58728** must be different between the two bins.

## Next Steps

1. **Extract and compare sectors 58723-58728** from both bins
2. **Check if these sectors are in the single-disc layers** (parts 1-10)
3. **If different:** Find which layer modifies them and why the builder produces different bytes

## Commands to Verify

```bash
# Extract sector 58723 from both bins
dd if=~/Downloads/ff7-d1-csr-sd-mov-end.bin bs=2352 skip=58723 count=1 | xxd > working-58723.hex
dd if=workspace/builder-simulated-complete.bin bs=2352 skip=58723 count=1 | xxd > broken-58723.hex
diff working-58723.hex broken-58723.hex
```
