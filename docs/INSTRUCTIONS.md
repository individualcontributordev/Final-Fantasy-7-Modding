# Task: ending credits test v3 (Form2 MOVIE_ID sizes)

## Why LASTMAP froze on v2

Field scripts and D3 movie **bytes** were already on the image, but
`MOVIE_ID.BIN` **size** was set to the ISO file length (2048×sectors).

The movie player needs Disc 3’s lengths: usually **2336×sectors**, plus the
same extra fields Disc 3 stores for that stream. Wrong length → freeze on play.

## What we fixed (local test bin)

1. Pristine `LASTMAP.DAT` / `LAS4_0.DAT` (ending Play movie ops).
2. D3 streams on table ids **23, 24, 25, 26, 29**.
3. **MOVIE_ID** size + aux copied from Disc 3; only the **LBA** is ours (grew).

Still **~1.0 GB** — DuckStation only, not a real CD.

## What you do

1. Pull  
2. Open ending-test cue (rebuild if missing/old)  
3. Run past final battle / LASTMAP into credits  
4. Reply what you saw  

---

## 0. Update

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
```

---

## 1. Open test image

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

Expect bin size **1008274176**.

Do **not** use `ff7_d1_playtest_csr_sd_movies.cue` for this test.

---

## 2. Rebuild if needed

```bash
cd /path/to/Final-Fantasy-7-Modding

python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

---

## 3. Smoke

On LASTMAP and after final battle:

- Should **not** freeze on the first ending movie
- Real ending / credits streams, with sound on the long credit roll if it runs
- Note any freeze, black gap, or wrong short FMV  

---

## 4. Reply

1. Bin size  
2. What played on LASTMAP / after final fight  
3. Sound yes/no / freeze yes-no  


[  117.9776] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.62 GPU: 0.00 Avg: 16.72ms Min: 16.10ms Max: 17.46ms
[  118.9808] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.55 GPU: 0.00 Avg: 16.72ms Min: 16.27ms Max: 17.19ms
[  119.9836] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 3.62 GPU: 0.00 Avg: 16.71ms Min: 16.00ms Max: 17.40ms
[  120.9867] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 3.64 GPU: 0.00 Avg: 16.72ms Min: 16.07ms Max: 17.52ms
[  121.9897] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.71 GPU: 0.00 Avg: 16.72ms Min: 16.26ms Max: 17.30ms
[  122.8255] D/CodeCache: Breaking block 0x800C2FFC at 0x800C3000 due to page crossing
[  122.9262] D/MDEC: Invalid MDEC command 0x17FF03FF
[  122.9263] D/MDEC: Invalid MDEC command 0x1801F76C
[  122.9267] D/MDEC: Invalid MDEC command 0xF7CCFE00
[  122.9268] D/MDEC: Invalid MDEC command 0x1FFF0002
[  122.9270] D/CodeCache: Page fault handler invoked at PC=0x7ff609e346ca Address=0x2295aa39ba3 (read), fastmem offset 80229BA3
[  122.9271] D/CodeCache: Backpatching store at 0x7ff609e346ca[5] (pc 8004269C addr 80229BA3): Bitmask 0BD25D50 Addr 0 Data 0 Size 1 Signed 00
[  122.9272] D/Recompiler: Backpatching 0x7ff609e346ca (guest PC 0x8004269C) to slowmem
[  122.9273] D/CodeCache: Page fault handler invoked at PC=0x7ff609e346dc Address=0x2295aa39ba5 (read), fastmem offset 80229BA5
[  122.9273] D/CodeCache: Backpatching store at 0x7ff609e346dc[5] (pc 800426A0 addr 80229BA5): Bitmask 0BD25D80 Addr 0 Data 0 Size 1 Signed 00
[  122.9275] D/Recompiler: Backpatching 0x7ff609e346dc (guest PC 0x800426A0) to slowmem
[  122.9276] D/CodeCache: Page fault handler invoked at PC=0x7ff609e346ef Address=0x2295aa39ba7 (read), fastmem offset 80229BA7
[  122.9276] D/CodeCache: Backpatching store at 0x7ff609e346ef[5] (pc 800426A4 addr 80229BA7): Bitmask 0BD25DB0 Addr 0 Data 0 Size 1 Signed 00
[  122.9277] D/Recompiler: Backpatching 0x7ff609e346ef (guest PC 0x800426A4) to slowmem
[  122.9278] D/CodeCache: Page fault handler invoked at PC=0x7ff609e346fe Address=0x2295aa39ba9 (read), fastmem offset 80229BA9
[  122.9279] D/CodeCache: Backpatching store at 0x7ff609e346fe[5] (pc 800426A8 addr 80229BA9): Bitmask 0BD25DE0 Addr 0 Data 0 Size 1 Signed 00
[  122.9280] D/Recompiler: Backpatching 0x7ff609e346fe (guest PC 0x800426A8) to slowmem
[  122.9280] D/CodeCache: Page fault handler invoked at PC=0x7ff609e3470d Address=0x2295aa39bab (read), fastmem offset 80229BAB
[  122.9281] D/CodeCache: Backpatching store at 0x7ff609e3470d[5] (pc 800426AC addr 80229BAB): Bitmask 0BD25E10 Addr 0 Data 0 Size 1 Signed 00
[  122.9282] D/Recompiler: Backpatching 0x7ff609e3470d (guest PC 0x800426AC) to slowmem
[  122.9283] D/CodeCache: Page fault handler invoked at PC=0x7ff609e34720 Address=0x2295aa39bad (read), fastmem offset 80229BAD
[  122.9284] D/CodeCache: Backpatching store at 0x7ff609e34720[5] (pc 800426B0 addr 80229BAD): Bitmask 0BD25E40 Addr 0 Data 0 Size 1 Signed 00
[  122.9284] D/Recompiler: Backpatching 0x7ff609e34720 (guest PC 0x800426B0) to slowmem
[  122.9285] D/CodeCache: Page fault handler invoked at PC=0x7ff609e35125 Address=0x2295aa39baf (read), fastmem offset 80229BAF
[  122.9286] D/CodeCache: Backpatching store at 0x7ff609e35125[5] (pc 80042870 addr 80229BAF): Bitmask 0BD26220 Addr 0 Data 0 Size 1 Signed 00
[  122.9287] D/Recompiler: Backpatching 0x7ff609e35125 (guest PC 0x80042870) to slowmem
[  122.9287] D/CodeCache: Page fault handler invoked at PC=0x7ff609e35e5f Address=0x2295aa39bbb (read), fastmem offset 80229BBB
[  122.9288] D/CodeCache: Backpatching store at 0x7ff609e35e5f[5] (pc 8004282C addr 80229BBB): Bitmask 0BD26640 Addr 0 Data 0 Size 1 Signed 00
[  122.9290] D/Recompiler: Backpatching 0x7ff609e35e5f (guest PC 0x8004282C) to slowmem
[  122.9290] D/CodeCache: Page fault handler invoked at PC=0x7ff609e350af Address=0x2295aa39bd1 (read), fastmem offset 80229BD1
[  122.9291] D/CodeCache: Backpatching store at 0x7ff609e350af[5] (pc 800428EC addr 80229BD1): Bitmask 0BD261E0 Addr 0 Data 0 Size 1 Signed 00
[  122.9291] D/Recompiler: Backpatching 0x7ff609e350af (guest PC 0x800428EC) to slowmem
[  122.9596] D/CodeCache: Page fault handler invoked at PC=0x7ff609e35253 Address=0x2295aa10000 (write), fastmem offset 80200000
[  122.9598] D/CodeCache: Backpatching store at 0x7ff609e35253[5] (pc 80042894 addr 80200000): Bitmask 0BD26260 Addr 0 Data 0 Size 1 Signed 00
[  122.9603] D/Recompiler: Backpatching 0x7ff609e35253 (guest PC 0x80042894) to slowmem
[  122.9604] D/CodeCache: Page fault on protected RAM @ 0x00000000 (page #0), invalidating code cache.
[  122.9605] D/CodeCache: Page fault handler invoked at PC=0x7ff609e35406 Address=0x2295aa1001c (write), fastmem offset 8020001C
[  122.9605] D/CodeCache: Backpatching store at 0x7ff609e35406[5] (pc 800428B4 addr 8020001C): Bitmask 0BD26290 Addr 0 Data 0 Size 1 Signed 00
[  122.9606] D/Recompiler: Backpatching 0x7ff609e35406 (guest PC 0x800428B4) to slowmem
[  122.9607] D/CodeCache: Page fault handler invoked at PC=0x7ff609e37e8b Address=0x2295aa1001e (write), fastmem offset 8020001E
[  122.9609] D/CodeCache: Backpatching store at 0x7ff609e37e8b[5] (pc 800427EC addr 8020001E): Bitmask 0BD26F60 Addr 0 Data 0 Size 1 Signed 00
[  122.9609] D/Recompiler: Backpatching 0x7ff609e37e8b (guest PC 0x800427EC) to slowmem
[  122.9609] D/CodeCache: Page fault handler invoked at PC=0x7ff609e37f91 Address=0x2295aa10024 (write), fastmem offset 80200024
[  122.9610] D/CodeCache: Backpatching store at 0x7ff609e37f91[5] (pc 800427EC addr 80200024): Bitmask 0BD26FD0 Addr 0 Data 0 Size 1 Signed 00
[  122.9611] D/Recompiler: Backpatching 0x7ff609e37f91 (guest PC 0x800427EC) to slowmem
[  122.9612] D/CodeCache: Page fault handler invoked at PC=0x7ff609e3581d Address=0x2295aa10042 (write), fastmem offset 80200042
[  122.9613] D/CodeCache: Backpatching store at 0x7ff609e3581d[5] (pc 800428D4 addr 80200042): Bitmask 0BD26390 Addr 0 Data 0 Size 1 Signed 00
[  122.9613] D/Recompiler: Backpatching 0x7ff609e3581d (guest PC 0x800428D4) to slowmem
[  122.9614] D/CodeCache: Page fault handler invoked at PC=0x7ff609e35096 Address=0x2295aa10050 (write), fastmem offset 80200050
[  122.9615] D/CodeCache: Backpatching store at 0x7ff609e35096[5] (pc 800428E4 addr 80200050): Bitmask 0BD261A0 Addr 0 Data 0 Size 1 Signed 00
[  122.9616] D/Recompiler: Backpatching 0x7ff609e35096 (guest PC 0x800428E4) to slowmem
[  122.9617] W(ReadBlockInstructions): Direct branch in delay slot at 80000084, skipping block
[  122.9617] E(CompileOrRevalidateBlock): Failed to read block at 0x80000080, falling back to uncached interpreter
[  123.0112] V/AudioStream: Audio buffer underflow, resampled 334 frames to 441
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create a timer (The current process has used all of its system allowance of handles for Window Manager objects.)
QEventDispatcherWin32::registerTimer: Failed to create