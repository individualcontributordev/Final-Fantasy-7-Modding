# Task: Retest D1→D2 disc-swap hang fix (v0.1.3.3 / manip-movies v0.1.5)

## Why

Your last playtest hung at the D1→D2 transition: black screen, no "Insert
Disc 2" prompt, DuckStation log showed normal reads then a hard backward
seek to LBA 68314 (`13:02:57`) and FPS 0.00 forever.

Root cause: field #779 (`MD8_52`) plays a `PMVIE`/`MOVIE` FMV (Cloud-position
cutscene, `NRCRL.MOV` on CSR Disc 2) right before jumping into the D1→D2
break. That FMV has to be copied onto the Disc 1 image's `MTNVL2.STR` movie
slot for a single-disc build to find it. This inject (and 4 siblings for
`MD8_5`/`FSHIP_12`) was implemented back in single-disc v0.1.21–23 and
folded into the `single-disc-csr-manip-movies-v0.1.4` pack, but somewhere
after that it silently dropped out of the pack — `MOVIE/MTNVL2.STR` was
still stock D1 content, so the engine tried to stream data that didn't
match what the field script expected, and the CD-ROM stalled. No prompt
appears because the hang is *before* the disc-swap fields are ever reached.

**Fix:** new `single-disc-csr-manip-movies-v0.1.5` pack — a delta pack that
applies right after v0.1.4 and restores the 5 missing injects: `NRCRLB`→
`NIVLSFS.MOV` (MD8_5), `NRCRL`→`MTNVL2.STR` (MD8_52 — the hang fix),
`PARASHOT`→`OPENINGE.MOV`, `METEOFIX`→`MTCRL.STR`, `METEOSKY`→`MTNVL.STR`
(FSHIP_12). v0.1.4 stays enabled/auto-included as before; v0.1.5 chains on
top of it automatically.

`verify_builder_config.py` confirms the full 10-addon stack (base +
single-disc-on-csr + manip-movies v0.1.4 + v0.1.5 + 7 endings parts) applies
cleanly: 4,978,843 total records. Confirmed programmatically that
`MOVIE/MTNVL2.STR` byte-matches pristine D2 `NRCRL.MOV` after the full stack
is applied.

## What you do

1. Open a **private/incognito browser window** (avoid stale cache).
2. Go to https://individualcontributor.dev/builder/.
3. Base: CSR. Mods: Single-disc only (CSR+ off). Build Disc 1.
4. Check the builder's "applied" list — confirm you see **both**
   `single-disc-csr-manip-movies-v0.1.4` AND `single-disc-csr-manip-movies-v0.1.5`.
5. Quit DuckStation fully if it was already open, start fresh (no cheat
   engine / speedhack).
6. Play through to the point just before the D1→D2 transition (the scene
   right after Diamond Weapon/Cloud approaches the Highwind, field #779
   MD8_52 / "Cloud position" cutscene).
7. Confirm the Cloud-position FMV plays (not a freeze), then confirm you
   get the "Insert Disc 2" prompt (should just continue seamlessly on
   single-disc — no actual disc swap needed, just no hang).
8. Continue into field 634 (LOST2, forest near Cosmo Canyon) — confirm it
   loads with music and the break-scene cutscene plays.
9. If you'd previously seen the FSHIP_12/PARASHOT (Cloud Highwind meteor
   scene) or MD8_5/NRCRLB (Diamond Weapon approach) sequences, check those
   FMVs still play correctly too (they use the same inject mechanism).

## Evidence (paste)

```
Used incognito window: YES
APPLIED manip-movies versions shown: (should be BOTH 0.1.4 and 0.1.5)
MD8_52 Cloud-position FMV: PLAYED / FROZE / OTHER (describe)
D1->D2 transition: NO HANG / STILL HANGS (describe)
Field 634 (LOST2 forest) load: OK / FROZE / OTHER
FSHIP_12/PARASHOT scene: OK / MISSING / OTHER
MD8_5/NRCRLB scene: OK / MISSING / OTHER
Load method:
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.

## Prior playtest logs (for reference, now fixed)

duckstation logs

 2890.6624] D/CDROM: Read sector 127013 [28:13:38]: mode 2 submode 0x08 into buffer 1
[ 2890.6785] D/CDROM: Read sector 127014 [28:13:39]: mode 2 submode 0x08 into buffer 2
[ 2890.6787] D/CDROM: Read sector 127015 [28:13:40]: mode 2 submode 0x08 into buffer 3
[ 2890.6790] D/CDROM: Read sector 127016 [28:13:41]: mode 2 submode 0x89 into buffer 4
[ 2890.6790] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2890.7454] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x42]
[ 2890.7456] D/CDROM: CDROM setloc command (28, 13, 42)
[ 2890.7458] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2890.7461] D/CDROM: Seek time for 28:13:33->28:13:42 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2890.7957] D/CDROM: Logical seek to [28:13:42] complete, now reading
[ 2890.8120] D/CDROM: Read sector 127017 [28:13:42]: mode 2 submode 0x08 into buffer 1
[ 2890.8123] D/CDROM: Read sector 127018 [28:13:43]: mode 2 submode 0x08 into buffer 2
[ 2890.8291] D/CDROM: Read sector 127019 [28:13:44]: mode 2 submode 0x08 into buffer 3
[ 2890.8293] D/CDROM: Read sector 127020 [28:13:45]: mode 2 submode 0x89 into buffer 4
[ 2890.8293] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2890.8958] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x46]
[ 2890.8960] D/CDROM: CDROM setloc command (28, 13, 46)
[ 2890.8962] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2890.8962] D/CDROM: Seek time for 28:13:37->28:13:46 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2890.9475] D/CDROM: Logical seek to [28:13:46] complete, now reading
[ 2890.9480] D/CDROM: Read sector 127021 [28:13:46]: mode 2 submode 0x08 into buffer 1
[ 2890.9629] D/CDROM: Read sector 127022 [28:13:47]: mode 2 submode 0x08 into buffer 2
[ 2890.9629] D/CDROM: Read sector 127023 [28:13:48]: mode 2 submode 0x08 into buffer 3
[ 2890.9631] D/CDROM: Read sector 127024 [28:13:49]: mode 2 submode 0x89 into buffer 4
[ 2890.9631] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2891.0298] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x50]
[ 2891.0298] D/CDROM: CDROM setloc command (28, 13, 50)
[ 2891.0300] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2891.0300] D/CDROM: Seek time for 28:13:41->28:13:50 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2891.1133] D/CDROM: Logical seek to [28:13:50] complete, now reading
[ 2891.1174] V/PerfMon: FPS: 0.00 VPS: 59.93 CPU: 4.41 GPU: 0.00 Avg: 16.69ms Min: 1.57ms Max: 63.73ms
[ 2891.1179] D/CDROM: Read sector 127025 [28:13:50]: mode 2 submode 0x08 into buffer 1
[ 2891.1182] D/CDROM: Read sector 127026 [28:13:51]: mode 2 submode 0x08 into buffer 2
[ 2891.1184] D/CDROM: Read sector 127027 [28:13:52]: mode 2 submode 0x08 into buffer 3
[ 2891.1309] V/AudioStream: ~~~ Stretcher is now active @ tempo 0.8296927.
[ 2891.1309] D/CDROM: Read sector 127028 [28:13:53]: mode 2 submode 0x89 into buffer 4
[ 2891.1311] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2891.1973] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x54]
[ 2891.1973] D/CDROM: CDROM setloc command (28, 13, 54)
[ 2891.1980] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2891.1980] D/CDROM: Seek time for 28:13:45->28:13:54 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2891.2468] D/CDROM: Logical seek to [28:13:54] complete, now reading
[ 2891.2471] D/CDROM: Read sector 127029 [28:13:54]: mode 2 submode 0x08 into buffer 1
[ 2891.2637] D/CDROM: Read sector 127030 [28:13:55]: mode 2 submode 0x08 into buffer 2
[ 2891.2639] D/CDROM: Read sector 127031 [28:13:56]: mode 2 submode 0x08 into buffer 3
[ 2891.2642] D/CDROM: Read sector 127032 [28:13:57]: mode 2 submode 0x08 into buffer 4
[ 2891.2803] D/CDROM: Read sector 127033 [28:13:58]: mode 2 submode 0x08 into buffer 5
[ 2891.2805] D/CDROM: Read sector 127034 [28:13:59]: mode 2 submode 0x08 into buffer 6
[ 2891.2971] D/CDROM: Read sector 127035 [28:13:60]: mode 2 submode 0x89 into buffer 7
[ 2891.2974] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2891.3977] V/AudioStream: === Stretcher is now inactive.
[ 2891.4314] D/CodeCache: Breaking block 0x800B9F7C at 0x800BA000 due to page crossing
[ 2891.4319] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abb90 Address=0x2c614100020 (read), fastmem offset 1F800020
[ 2891.4321] D/CodeCache: Backpatching store at 0x7ff6e59abb90[5] (pc 8003BF3C addr 1F800020): Bitmask E78B5980 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4324] D/Recompiler: Backpatching 0x7ff6e59abb90 (guest PC 0x8003BF3C) to slowmem
[ 2891.4326] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abbd2 Address=0x2c614100000 (write), fastmem offset 1F800000
[ 2891.4329] D/CodeCache: Backpatching store at 0x7ff6e59abbd2[5] (pc 8003BF44 addr 1F800000): Bitmask E78B59A0 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4331] D/Recompiler: Backpatching 0x7ff6e59abbd2 (guest PC 0x8003BF44) to slowmem
[ 2891.4331] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abbe2 Address=0x2c614100026 (read), fastmem offset 1F800026
[ 2891.4331] D/CodeCache: Backpatching store at 0x7ff6e59abbe2[5] (pc 8003BF48 addr 1F800026): Bitmask E78B59C0 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4331] D/Recompiler: Backpatching 0x7ff6e59abbe2 (guest PC 0x8003BF48) to slowmem
[ 2891.4331] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abbf2 Address=0x2c61410002c (read), fastmem offset 1F80002C
[ 2891.4331] D/CodeCache: Backpatching store at 0x7ff6e59abbf2[5] (pc 8003BF4C addr 1F80002C): Bitmask E78B59E0 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4333] D/Recompiler: Backpatching 0x7ff6e59abbf2 (guest PC 0x8003BF4C) to slowmem
[ 2891.4333] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abc02 Address=0x2c614100002 (write), fastmem offset 1F800002
[ 2891.4333] D/CodeCache: Backpatching store at 0x7ff6e59abc02[5] (pc 8003BF50 addr 1F800002): Bitmask E78B5A00 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4333] D/Recompiler: Backpatching 0x7ff6e59abc02 (guest PC 0x8003BF50) to slowmem
[ 2891.4333] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abc0e Address=0x2c614100022 (read), fastmem offset 1F800022
[ 2891.4333] D/CodeCache: Backpatching store at 0x7ff6e59abc0e[5] (pc 8003BF54 addr 1F800022): Bitmask E78B5A30 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4333] D/Recompiler: Backpatching 0x7ff6e59abc0e (guest PC 0x8003BF54) to slowmem
[ 2891.4336] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abc1e Address=0x2c614100004 (write), fastmem offset 1F800004
[ 2891.4336] D/CodeCache: Backpatching store at 0x7ff6e59abc1e[5] (pc 8003BF58 addr 1F800004): Bitmask E78B5A60 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4336] D/Recompiler: Backpatching 0x7ff6e59abc1e (guest PC 0x8003BF58) to slowmem
[ 2891.4336] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abc2a Address=0x2c614100028 (read), fastmem offset 1F800028
[ 2891.4336] D/CodeCache: Backpatching store at 0x7ff6e59abc2a[5] (pc 8003BF5C addr 1F800028): Bitmask E78B5A90 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4336] D/Recompiler: Backpatching 0x7ff6e59abc2a (guest PC 0x8003BF5C) to slowmem
[ 2891.4336] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abc3a Address=0x2c614100006 (write), fastmem offset 1F800006
[ 2891.4338] D/CodeCache: Backpatching store at 0x7ff6e59abc3a[5] (pc 8003BF60 addr 1F800006): Bitmask E78B5AC0 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4338] D/Recompiler: Backpatching 0x7ff6e59abc3a (guest PC 0x8003BF60) to slowmem
[ 2891.4338] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abc46 Address=0x2c61410002e (read), fastmem offset 1F80002E
[ 2891.4338] D/CodeCache: Backpatching store at 0x7ff6e59abc46[5] (pc 8003BF64 addr 1F80002E): Bitmask E78B5AF0 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4338] D/Recompiler: Backpatching 0x7ff6e59abc46 (guest PC 0x8003BF64) to slowmem
[ 2891.4338] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abc56 Address=0x2c614100008 (write), fastmem offset 1F800008
[ 2891.4341] D/CodeCache: Backpatching store at 0x7ff6e59abc56[5] (pc 8003BF68 addr 1F800008): Bitmask E78B5B20 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4341] D/Recompiler: Backpatching 0x7ff6e59abc56 (guest PC 0x8003BF68) to slowmem
[ 2891.4341] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abc62 Address=0x2c614100024 (read), fastmem offset 1F800024
[ 2891.4341] D/CodeCache: Backpatching store at 0x7ff6e59abc62[5] (pc 8003BF6C addr 1F800024): Bitmask E78B5B50 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4341] D/Recompiler: Backpatching 0x7ff6e59abc62 (guest PC 0x8003BF6C) to slowmem
[ 2891.4343] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abc72 Address=0x2c61410000a (write), fastmem offset 1F80000A
[ 2891.4343] D/CodeCache: Backpatching store at 0x7ff6e59abc72[5] (pc 8003BF70 addr 1F80000A): Bitmask E78B5B80 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4343] D/Recompiler: Backpatching 0x7ff6e59abc72 (guest PC 0x8003BF70) to slowmem
[ 2891.4343] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abc7e Address=0x2c61410002a (read), fastmem offset 1F80002A
[ 2891.4343] D/CodeCache: Backpatching store at 0x7ff6e59abc7e[5] (pc 8003BF74 addr 1F80002A): Bitmask E78B5BB0 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4346] D/Recompiler: Backpatching 0x7ff6e59abc7e (guest PC 0x8003BF74) to slowmem
[ 2891.4346] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abc8e Address=0x2c61410000c (write), fastmem offset 1F80000C
[ 2891.4346] D/CodeCache: Backpatching store at 0x7ff6e59abc8e[5] (pc 8003BF78 addr 1F80000C): Bitmask E78B5BE0 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4346] D/Recompiler: Backpatching 0x7ff6e59abc8e (guest PC 0x8003BF78) to slowmem
[ 2891.4346] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abc9a Address=0x2c614100030 (read), fastmem offset 1F800030
[ 2891.4348] D/CodeCache: Backpatching store at 0x7ff6e59abc9a[5] (pc 8003BF7C addr 1F800030): Bitmask E78B5C10 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4348] D/Recompiler: Backpatching 0x7ff6e59abc9a (guest PC 0x8003BF7C) to slowmem
[ 2891.4348] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abcaa Address=0x2c61410000e (write), fastmem offset 1F80000E
[ 2891.4348] D/CodeCache: Backpatching store at 0x7ff6e59abcaa[5] (pc 8003BF80 addr 1F80000E): Bitmask E78B5C40 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4348] D/Recompiler: Backpatching 0x7ff6e59abcaa (guest PC 0x8003BF80) to slowmem
[ 2891.4348] D/CodeCache: Page fault handler invoked at PC=0x7ff6e59abcc4 Address=0x2c614100010 (write), fastmem offset 1F800010
[ 2891.4348] D/CodeCache: Backpatching store at 0x7ff6e59abcc4[5] (pc 8003BF88 addr 1F800010): Bitmask E78B5C70 Addr 0 Data 0 Size 1 Signed 00
[ 2891.4351] D/Recompiler: Backpatching 0x7ff6e59abcc4 (guest PC 0x8003BF88) to slowmem
[ 2892.1338] V/PerfMon: FPS: 20.66 VPS: 60.03 CPU: 4.34 GPU: 0.00 Avg: 16.66ms Min: 12.98ms Max: 17.87ms
[ 2893.1362] V/PerfMon: FPS: 29.92 VPS: 59.85 CPU: 4.17 GPU: 0.00 Avg: 16.71ms Min: 15.73ms Max: 17.31ms
[ 2894.1392] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 4.18 GPU: 0.00 Avg: 16.71ms Min: 15.93ms Max: 17.62ms
[ 2895.1421] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.18 GPU: 0.00 Avg: 16.72ms Min: 15.53ms Max: 17.71ms
[ 2896.1453] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 4.18 GPU: 0.00 Avg: 16.72ms Min: 15.29ms Max: 18.21ms
[ 2896.1863] V/AudioStream: Audio buffer underflow, resampled 303 frames to 441
[ 2896.1890] V/AudioStream: Underrun compensation done (128 frames buffered)
[ 2896.2129] V/AudioStream: ~~~ Stretcher is now active @ tempo 0.8285168.
[ 2896.4126] V/AudioStream: === Stretcher is now inactive.
[ 2897.1479] V/PerfMon: FPS: 29.92 VPS: 58.84 CPU: 4.17 GPU: 0.00 Avg: 17.00ms Min: 7.78ms Max: 42.42ms
[ 2898.1511] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.20 GPU: 0.00 Avg: 16.72ms Min: 14.91ms Max: 18.67ms
[ 2899.1550] V/PerfMon: FPS: 29.88 VPS: 59.76 CPU: 4.14 GPU: 0.00 Avg: 16.73ms Min: 14.33ms Max: 19.20ms
[ 2900.1577] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 4.13 GPU: 0.00 Avg: 16.71ms Min: 15.10ms Max: 17.90ms
[ 2901.1602] V/PerfMon: FPS: 29.93 VPS: 59.85 CPU: 4.18 GPU: 0.00 Avg: 16.71ms Min: 15.16ms Max: 17.85ms
[ 2901.5286] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x02, 0x57]
[ 2901.5288] D/CDROM: CDROM setloc command (13, 02, 57)
[ 2901.5291] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2901.5293] D/CDROM: Seek time for 28:13:46->13:02:57 (68314 LBA): 15438077 (455.820 ms) (2N/sled backward)
[ 2901.9961] D/CDROM: Logical seek to [13:02:57] complete, now reading
[ 2901.9963] D/CDROM: Read sector 58707 [13:02:57]: mode 2 submode 0x08 into buffer 1
[ 2901.9968] D/CDROM: Read sector 58708 [13:02:58]: mode 2 submode 0x08 into buffer 2
[ 2902.0132] D/CDROM: Read sector 58709 [13:02:59]: mode 2 submode 0x08 into buffer 3
[ 2902.0134] D/CDROM: Read sector 58710 [13:02:60]: mode 2 submode 0x08 into buffer 4
[ 2902.0300] D/CDROM: Read sector 58711 [13:02:61]: mode 2 submode 0x08 into buffer 5
[ 2902.0300] D/CDROM: Read sector 58712 [13:02:62]: mode 2 submode 0x08 into buffer 6
[ 2902.0305] D/CDROM: Read sector 58713 [13:02:63]: mode 2 submode 0x08 into buffer 7
[ 2902.0464] D/CDROM: Read sector 58714 [13:02:64]: mode 2 submode 0x08 into buffer 0
[ 2902.0466] D/CDROM: Read sector 58715 [13:02:65]: mode 2 submode 0x08 into buffer 1
[ 2902.0466] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2902.1301] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x02, 0x66]
[ 2902.1301] D/CDROM: CDROM setloc command (13, 02, 66)
[ 2902.1306] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2902.1309] D/CDROM: Seek time for 13:02:62->13:02:66 (4 LBA): 903168 (26.667 ms) (forward)
[ 2902.1631] V/PerfMon: FPS: 11.96 VPS: 59.82 CPU: 3.99 GPU: 0.00 Avg: 16.72ms Min: 15.53ms Max: 17.99ms
[ 2902.1633] D/CDROM: Logical seek to [13:02:66] complete, now reading
[ 2902.1638] D/CDROM: Read sector 58716 [13:02:66]: mode 2 submode 0x08 into buffer 1
[ 2902.1797] D/CDROM: Read sector 58717 [13:02:67]: mode 2 submode 0x08 into buffer 2
[ 2902.1799] D/CDROM: Read sector 58718 [13:02:68]: mode 2 submode 0x08 into buffer 3
[ 2902.1802] D/CDROM: Read sector 58719 [13:02:69]: mode 2 submode 0x08 into buffer 4
[ 2902.1968] D/CDROM: Read sector 58720 [13:02:70]: mode 2 submode 0x08 into buffer 5
[ 2902.1968] D/CDROM: Read sector 58721 [13:02:71]: mode 2 submode 0x08 into buffer 6
[ 2902.2144] D/CDROM: Read sector 58722 [13:02:72]: mode 2 submode 0x89 into buffer 7
[ 2902.2146] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2902.2637] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x02, 0x50]
[ 2902.2639] D/CDROM: CDROM setloc command (13, 02, 50)
[ 2902.2651] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2902.2654] D/CDROM: Seek time for 13:02:66->13:02:50 (16 LBA): 1693440 (50.000 ms) (NT backward)
[ 2902.3142] D/CDROM: Logical seek to [13:02:50] complete, now reading
[ 2902.3303] D/CDROM: Read sector 58700 [13:02:50]: mode 2 submode 0x08 into buffer 1
[ 2902.3306] D/CDROM: Read sector 58701 [13:02:51]: mode 2 submode 0x08 into buffer 2
[ 2902.3311] D/CDROM: Read sector 58702 [13:02:52]: mode 2 submode 0x08 into buffer 3
[ 2902.3474] D/CDROM: Read sector 58703 [13:02:53]: mode 2 submode 0x08 into buffer 4
[ 2902.3477] D/CDROM: Read sector 58704 [13:02:54]: mode 2 submode 0x08 into buffer 5
[ 2902.3640] D/CDROM: Read sector 58705 [13:02:55]: mode 2 submode 0x08 into buffer 6
[ 2902.3643] D/CDROM: Read sector 58706 [13:02:56]: mode 2 submode 0x89 into buffer 7
[ 2902.3645] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2903.1665] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 3.06 GPU: 0.00 Avg: 16.72ms Min: 15.21ms Max: 18.04ms
[ 2904.1692] V/PerfMon: FPS: 0.00 VPS: 59.83 CPU: 2.66 GPU: 0.00 Avg: 16.71ms Min: 14.59ms Max: 18.55ms
[ 2905.1726] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 2.63 GPU: 0.00 Avg: 16.72ms Min: 15.32ms Max: 17.68ms
[ 2906.1755] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 2.61 GPU: 0.00 Avg: 16.72ms Min: 15.82ms Max: 17.29ms
[ 2907.1787] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 2.55 GPU: 0.00 Avg: 16.72ms Min: 15.66ms Max: 18.51ms
[ 2908.1819] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 2.59 GPU: 0.00 Avg: 16.72ms Min: 15.75ms Max: 17.59ms
[ 2909.1848] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 2.58 GPU: 0.00 Avg: 16.72ms Min: 15.41ms Max: 17.88ms
[ 2910.1877] V/PerfMon: FPS: 0.00 VPS: 59.83 CPU: 2.60 GPU: 0.00 Avg: 16.72ms Min: 14.63ms Max: 19.05ms
[ 2911.1907] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 2.59 GPU: 0.00 Avg: 16.72ms Min: 14.93ms Max: 18.48ms
[ 2912.1938] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 2.54 GPU: 0.00 Avg: 16.72ms Min: 15.58ms Max: 18.02ms