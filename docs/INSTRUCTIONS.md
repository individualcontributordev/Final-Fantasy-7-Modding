# Task: Playtest CSR + CSR+ + Single-disc (no Cheat Engine)

## Already confirmed (chat / this session)

| Build | Field 122 stairs / early path | Notes |
|-------|-------------------------------|--------|
| Unmodified D1 | OK | Pristine baseline |
| CSR D1 only | OK | CSR base not the early freeze |
| Cheat Engine | off | Earlier freezes may have been CE attaching to DuckStation |

## What you are testing now

**CSR + CSR+ + Single-disc** Disc 1, cold DuckStation, **no Cheat Engine**.

## Setup

1. Hard-refresh the builder (recent fixes: disc-filtered APPLIED, no bogus size pad on CSR+)
2. Base: **CSR**
3. Mods: **CSR+** + **Single-disc** (no Fanfare unless noted)
4. Build Disc 1
5. Check **APPLIED.txt**:
   - Single-disc listed
   - CSR+ lines only packs that apply to **this disc** (not every disc2/3-only id)
   - Apply order intent: Single-disc before CSR+ in the stack
6. Quit DuckStation fully; open new `.bin` + `.cue`
7. **Do not** attach Cheat Engine

## Smoke path

1. New game → bomb mission → elevator → **field 122 stairs**
2. Continue → Guard Scorpion → **after battle** (back to field)
3. Optional later: Cosmo / disc1→2 if early path is clean

## Evidence (paste below)

```
APPLIED.txt (full or key lines):
Cheat Engine attached?: NO
Cold DuckStation quit/reopen?: YES/NO

field 122 stairs: OK / FREEZE
Guard Scorpion fight: OK / FREEZE
After Scorpion (field return): OK / FREEZE
notes (music continues? FPS 0? where exactly?):
```

## When done

Pull, paste evidence into this file, commit, push, say **check**.

Commit message example: ops: retest disc1-disc2 LOST2 break after single-disc 0.1.6

some slow loading and this is the duckstation output around that time

[  647.8022] D/CDROM: Read sector 109397 [24:18:47]: mode 2 submode 0x08 into buffer 3
[  647.8025] D/CDROM: Read sector 109398 [24:18:48]: mode 2 submode 0x08 into buffer 4
[  647.8187] D/CDROM: Read sector 109399 [24:18:49]: mode 2 submode 0x08 into buffer 5
[  647.8188] D/CDROM: Read sector 109400 [24:18:50]: mode 2 submode 0x08 into buffer 6
[  647.8195] D/CDROM: Read sector 109401 [24:18:51]: mode 2 submode 0x08 into buffer 7
[  647.8354] D/CDROM: Read sector 109402 [24:18:52]: mode 2 submode 0x89 into buffer 0
[  647.8355] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  647.8864] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x16]
[  647.8865] D/CDROM: CDROM setloc command (28, 13, 16)
[  647.9022] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  647.9022] D/CDROM: Seek time for 24:18:44->28:13:16 (17597 LBA): 11503270 (339.642 ms) (2N/sled forward)
[  648.0861] V/PerfMon: FPS: 0.00 VPS: 59.85 CPU: 4.22 GPU: 0.00 Avg: 16.71ms Min: 16.17ms Max: 17.37ms
[  648.2368] D/CDROM: Logical seek to [28:13:16] complete, now reading
[  648.2371] D/CDROM: Read sector 126991 [28:13:16]: mode 2 submode 0x08 into buffer 1
[  648.2533] D/CDROM: Read sector 126992 [28:13:17]: mode 2 submode 0x08 into buffer 2
[  648.2537] D/CDROM: Read sector 126993 [28:13:18]: mode 2 submode 0x08 into buffer 3
[  648.2538] D/CDROM: Read sector 126994 [28:13:19]: mode 2 submode 0x89 into buffer 4
[  648.2701] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  648.3204] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x24]
[  648.3206] D/CDROM: CDROM setloc command (28, 13, 24)
[  648.3210] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  648.3210] D/CDROM: Seek time for 28:13:11->28:13:24 (13 LBA): 1693440 (50.000 ms) (NT forward)
[  648.3707] D/CDROM: Logical seek to [28:13:24] complete, now reading
[  648.3900] D/CDROM: Read sector 126999 [28:13:24]: mode 2 submode 0x08 into buffer 1
[  648.3904] D/CDROM: Read sector 127000 [28:13:25]: mode 2 submode 0x08 into buffer 2
[  648.3912] D/CDROM: Read sector 127001 [28:13:26]: mode 2 submode 0x08 into buffer 3
[  648.4036] D/CDROM: Read sector 127002 [28:13:27]: mode 2 submode 0x89 into buffer 4
[  648.4037] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  648.4543] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x28]
[  648.4545] D/CDROM: CDROM setloc command (28, 13, 28)
[  648.4549] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  648.4550] D/CDROM: Seek time for 28:13:19->28:13:28 (9 LBA): 1806336 (53.333 ms) (forward)
[  648.5209] D/CDROM: Logical seek to [28:13:28] complete, now reading
[  648.5212] D/CDROM: Read sector 127003 [28:13:28]: mode 2 submode 0x08 into buffer 1
[  648.5217] D/CDROM: Read sector 127004 [28:13:29]: mode 2 submode 0x08 into buffer 2
[  648.5378] D/CDROM: Read sector 127005 [28:13:30]: mode 2 submode 0x08 into buffer 3
[  648.5380] D/CDROM: Read sector 127006 [28:13:31]: mode 2 submode 0x08 into buffer 4
[  648.5542] D/CDROM: Read sector 127007 [28:13:32]: mode 2 submode 0x89 into buffer 5
[  648.5543] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  648.6046] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x33]
[  648.6048] D/CDROM: CDROM setloc command (28, 13, 33)
[  648.6052] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  648.6052] D/CDROM: Seek time for 28:13:24->28:13:33 (9 LBA): 1806336 (53.333 ms) (forward)
[  648.6548] D/CDROM: Logical seek to [28:13:33] complete, now reading
[  648.6714] D/CDROM: Read sector 127008 [28:13:33]: mode 2 submode 0x08 into buffer 1
[  648.6716] D/CDROM: Read sector 127009 [28:13:34]: mode 2 submode 0x08 into buffer 2
[  648.6879] D/CDROM: Read sector 127010 [28:13:35]: mode 2 submode 0x08 into buffer 3
[  648.6882] D/CDROM: Read sector 127011 [28:13:36]: mode 2 submode 0x08 into buffer 4
[  648.6886] D/CDROM: Read sector 127012 [28:13:37]: mode 2 submode 0x89 into buffer 5
[  648.7046] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  648.7553] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x38]
[  648.7554] D/CDROM: CDROM setloc command (28, 13, 38)
[  648.7558] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  648.7559] D/CDROM: Seek time for 28:13:29->28:13:38 (9 LBA): 1806336 (53.333 ms) (forward)
[  648.8051] D/CDROM: Logical seek to [28:13:38] complete, now reading
[  648.8223] D/CDROM: Read sector 127013 [28:13:38]: mode 2 submode 0x08 into buffer 1
[  648.8225] D/CDROM: Read sector 127014 [28:13:39]: mode 2 submode 0x08 into buffer 2
[  648.8387] D/CDROM: Read sector 127015 [28:13:40]: mode 2 submode 0x08 into buffer 3
[  648.8390] D/CDROM: Read sector 127016 [28:13:41]: mode 2 submode 0x89 into buffer 4
[  648.8393] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  648.9052] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x42]
[  648.9053] D/CDROM: CDROM setloc command (28, 13, 42)
[  648.9057] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  648.9058] D/CDROM: Seek time for 28:13:33->28:13:42 (9 LBA): 1806336 (53.333 ms) (forward)
[  648.9557] D/CDROM: Logical seek to [28:13:42] complete, now reading
[  648.9562] D/CDROM: Read sector 127017 [28:13:42]: mode 2 submode 0x08 into buffer 1
[  648.9722] D/CDROM: Read sector 127018 [28:13:43]: mode 2 submode 0x08 into buffer 2
[  648.9724] D/CDROM: Read sector 127019 [28:13:44]: mode 2 submode 0x08 into buffer 3
[  648.9728] D/CDROM: Read sector 127020 [28:13:45]: mode 2 submode 0x89 into buffer 4
[  648.9728] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  649.0394] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x46]
[  649.0395] D/CDROM: CDROM setloc command (28, 13, 46)
[  649.0399] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  649.0400] D/CDROM: Seek time for 28:13:37->28:13:46 (9 LBA): 1806336 (53.333 ms) (forward)
[  649.0894] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 4.18 GPU: 0.00 Avg: 16.72ms Min: 13.68ms Max: 19.33ms
[  649.0900] D/CDROM: Logical seek to [28:13:46] complete, now reading
[  649.1064] D/CDROM: Read sector 127021 [28:13:46]: mode 2 submode 0x08 into buffer 1
[  649.1067] D/CDROM: Read sector 127022 [28:13:47]: mode 2 submode 0x08 into buffer 2
[  649.1069] D/CDROM: Read sector 127023 [28:13:48]: mode 2 submode 0x08 into buffer 3
[  649.1230] D/CDROM: Read sector 127024 [28:13:49]: mode 2 submode 0x89 into buffer 4
[  649.1232] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  649.1894] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x50]
[  649.1895] D/CDROM: CDROM setloc command (28, 13, 50)
[  649.1900] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  649.1901] D/CDROM: Seek time for 28:13:41->28:13:50 (9 LBA): 1806336 (53.333 ms) (forward)
[  649.2401] D/CDROM: Logical seek to [28:13:50] complete, now reading
[  649.2406] D/CDROM: Read sector 127025 [28:13:50]: mode 2 submode 0x08 into buffer 1
[  649.2563] D/CDROM: Read sector 127026 [28:13:51]: mode 2 submode 0x08 into buffer 2
[  649.2567] D/CDROM: Read sector 127027 [28:13:52]: mode 2 submode 0x08 into buffer 3
[  649.2568] D/CDROM: Read sector 127028 [28:13:53]: mode 2 submode 0x89 into buffer 4
[  649.2568] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  649.3236] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x54]
[  649.3238] D/CDROM: CDROM setloc command (28, 13, 54)
[  649.3247] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  649.3247] D/CDROM: Seek time for 28:13:45->28:13:54 (9 LBA): 1806336 (53.333 ms) (forward)
[  649.3738] D/CDROM: Logical seek to [28:13:54] complete, now reading
[  649.3902] D/CDROM: Read sector 127029 [28:13:54]: mode 2 submode 0x08 into buffer 1
[  649.3904] D/CDROM: Read sector 127030 [28:13:55]: mode 2 submode 0x08 into buffer 2
[  649.3906] D/CDROM: Read sector 127031 [28:13:56]: mode 2 submode 0x08 into buffer 3
[  649.4068] D/CDROM: Read sector 127032 [28:13:57]: mode 2 submode 0x08 into buffer 4
[  649.4071] D/CDROM: Read sector 127033 [28:13:58]: mode 2 submode 0x08 into buffer 5
[  649.4235] D/CDROM: Read sector 127034 [28:13:59]: mode 2 submode 0x08 into buffer 6
[  649.4238] D/CDROM: Read sector 127035 [28:13:60]: mode 2 submode 0x89 into buffer 7
[  649.4238] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  649.5747] D/CodeCache: Breaking block 0x800B9F7C at 0x800BA000 due to page crossing
[  649.5754] D/CodeCache: Page fault handler invoked at PC=0x7ff609e1278f Address=0x2189f680020 (read), fastmem offset 1F800020
[  649.5756] D/CodeCache: Backpatching store at 0x7ff609e1278f[5] (pc 8003BF3C addr 1F800020): Bitmask 0BD19120 Addr 0 Data 0 Size 1 Signed 00
[  649.5757] D/Recompiler: Backpatching 0x7ff609e1278f (guest PC 0x8003BF3C) to slowmem
[  649.5757] D/CodeCache: Page fault handler invoked at PC=0x7ff609e127d1 Address=0x2189f680000 (write), fastmem offset 1F800000
[  649.5757] D/CodeCache: Backpatching store at 0x7ff609e127d1[5] (pc 8003BF44 addr 1F800000): Bitmask 0BD19140 Addr 0 Data 0 Size 1 Signed 00
[  649.5758] D/Recompiler: Backpatching 0x7ff609e127d1 (guest PC 0x8003BF44) to slowmem
[  649.5758] D/CodeCache: Page fault handler invoked at PC=0x7ff609e127e1 Address=0x2189f680026 (read), fastmem offset 1F800026
[  649.5759] D/CodeCache: Backpatching store at 0x7ff609e127e1[5] (pc 8003BF48 addr 1F800026): Bitmask 0BD19160 Addr 0 Data 0 Size 1 Signed 00
[  649.5759] D/Recompiler: Backpatching 0x7ff609e127e1 (guest PC 0x8003BF48) to slowmem
[  649.5760] D/CodeCache: Page fault handler invoked at PC=0x7ff609e127f1 Address=0x2189f68002c (read), fastmem offset 1F80002C
[  649.5760] D/CodeCache: Backpatching store at 0x7ff609e127f1[5] (pc 8003BF4C addr 1F80002C): Bitmask 0BD19180 Addr 0 Data 0 Size 1 Signed 00
[  649.5761] D/Recompiler: Backpatching 0x7ff609e127f1 (guest PC 0x8003BF4C) to slowmem
[  649.5762] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12801 Address=0x2189f680002 (write), fastmem offset 1F800002
[  649.5763] D/CodeCache: Backpatching store at 0x7ff609e12801[5] (pc 8003BF50 addr 1F800002): Bitmask 0BD191A0 Addr 0 Data 0 Size 1 Signed 00
[  649.5764] D/Recompiler: Backpatching 0x7ff609e12801 (guest PC 0x8003BF50) to slowmem
[  649.5764] D/CodeCache: Page fault handler invoked at PC=0x7ff609e1280d Address=0x2189f680022 (read), fastmem offset 1F800022
[  649.5764] D/CodeCache: Backpatching store at 0x7ff609e1280d[5] (pc 8003BF54 addr 1F800022): Bitmask 0BD191D0 Addr 0 Data 0 Size 1 Signed 00
[  649.5765] D/Recompiler: Backpatching 0x7ff609e1280d (guest PC 0x8003BF54) to slowmem
[  649.5765] D/CodeCache: Page fault handler invoked at PC=0x7ff609e1281d Address=0x2189f680004 (write), fastmem offset 1F800004
[  649.5765] D/CodeCache: Backpatching store at 0x7ff609e1281d[5] (pc 8003BF58 addr 1F800004): Bitmask 0BD19200 Addr 0 Data 0 Size 1 Signed 00
[  649.5766] D/Recompiler: Backpatching 0x7ff609e1281d (guest PC 0x8003BF58) to slowmem
[  649.5767] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12829 Address=0x2189f680028 (read), fastmem offset 1F800028
[  649.5767] D/CodeCache: Backpatching store at 0x7ff609e12829[5] (pc 8003BF5C addr 1F800028): Bitmask 0BD19230 Addr 0 Data 0 Size 1 Signed 00
[  649.5767] D/Recompiler: Backpatching 0x7ff609e12829 (guest PC 0x8003BF5C) to slowmem
[  649.5767] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12839 Address=0x2189f680006 (write), fastmem offset 1F800006
[  649.5768] D/CodeCache: Backpatching store at 0x7ff609e12839[5] (pc 8003BF60 addr 1F800006): Bitmask 0BD19260 Addr 0 Data 0 Size 1 Signed 00
[  649.5768] D/Recompiler: Backpatching 0x7ff609e12839 (guest PC 0x8003BF60) to slowmem
[  649.5768] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12845 Address=0x2189f68002e (read), fastmem offset 1F80002E
[  649.5769] D/CodeCache: Backpatching store at 0x7ff609e12845[5] (pc 8003BF64 addr 1F80002E): Bitmask 0BD19290 Addr 0 Data 0 Size 1 Signed 00
[  649.5769] D/Recompiler: Backpatching 0x7ff609e12845 (guest PC 0x8003BF64) to slowmem
[  649.5770] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12855 Address=0x2189f680008 (write), fastmem offset 1F800008
[  649.5770] D/CodeCache: Backpatching store at 0x7ff609e12855[5] (pc 8003BF68 addr 1F800008): Bitmask 0BD192C0 Addr 0 Data 0 Size 1 Signed 00
[  649.5770] D/Recompiler: Backpatching 0x7ff609e12855 (guest PC 0x8003BF68) to slowmem
[  649.5771] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12861 Address=0x2189f680024 (read), fastmem offset 1F800024
[  649.5771] D/CodeCache: Backpatching store at 0x7ff609e12861[5] (pc 8003BF6C addr 1F800024): Bitmask 0BD192F0 Addr 0 Data 0 Size 1 Signed 00
[  649.5772] D/Recompiler: Backpatching 0x7ff609e12861 (guest PC 0x8003BF6C) to slowmem
[  649.5772] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12871 Address=0x2189f68000a (write), fastmem offset 1F80000A
[  649.5773] D/CodeCache: Backpatching store at 0x7ff609e12871[5] (pc 8003BF70 addr 1F80000A): Bitmask 0BD19320 Addr 0 Data 0 Size 1 Signed 00
[  649.5773] D/Recompiler: Backpatching 0x7ff609e12871 (guest PC 0x8003BF70) to slowmem
[  649.5773] D/CodeCache: Page fault handler invoked at PC=0x7ff609e1287d Address=0x2189f68002a (read), fastmem offset 1F80002A
[  649.5774] D/CodeCache: Backpatching store at 0x7ff609e1287d[5] (pc 8003BF74 addr 1F80002A): Bitmask 0BD19350 Addr 0 Data 0 Size 1 Signed 00
[  649.5774] D/Recompiler: Backpatching 0x7ff609e1287d (guest PC 0x8003BF74) to slowmem
[  649.5775] D/CodeCache: Page fault handler invoked at PC=0x7ff609e1288d Address=0x2189f68000c (write), fastmem offset 1F80000C
[  649.5775] D/CodeCache: Backpatching store at 0x7ff609e1288d[5] (pc 8003BF78 addr 1F80000C): Bitmask 0BD19380 Addr 0 Data 0 Size 1 Signed 00
[  649.5775] D/Recompiler: Backpatching 0x7ff609e1288d (guest PC 0x8003BF78) to slowmem
[  649.5775] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12899 Address=0x2189f680030 (read), fastmem offset 1F800030
[  649.5776] D/CodeCache: Backpatching store at 0x7ff609e12899[5] (pc 8003BF7C addr 1F800030): Bitmask 0BD193B0 Addr 0 Data 0 Size 1 Signed 00
[  649.5776] D/Recompiler: Backpatching 0x7ff609e12899 (guest PC 0x8003BF7C) to slowmem
[  649.5776] D/CodeCache: Page fault handler invoked at PC=0x7ff609e128a9 Address=0x2189f68000e (write), fastmem offset 1F80000E
[  649.5777] D/CodeCache: Backpatching store at 0x7ff609e128a9[5] (pc 8003BF80 addr 1F80000E): Bitmask 0BD193E0 Addr 0 Data 0 Size 1 Signed 00
[  649.5777] D/Recompiler: Backpatching 0x7ff609e128a9 (guest PC 0x8003BF80) to slowmem
[  649.5778] D/CodeCache: Page fault handler invoked at PC=0x7ff609e128c3 Address=0x2189f680010 (write), fastmem offset 1F800010
[  649.5778] D/CodeCache: Backpatching store at 0x7ff609e128c3[5] (pc 8003BF88 addr 1F800010): Bitmask 0BD19410 Addr 0 Data 0 Size 1 Signed 00
[  649.5778] D/Recompiler: Backpatching 0x7ff609e128c3 (guest PC 0x8003BF88) to slowmem
[  650.0923] V/PerfMon: FPS: 15.95 VPS: 59.83 CPU: 4.31 GPU: 0.00 Avg: 16.72ms Min: 16.13ms Max: 17.08ms
[  651.0952] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 4.06 GPU: 0.00 Avg: 16.71ms Min: 15.95ms Max: 17.70ms
[  652.0984] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.97 GPU: 0.00 Avg: 16.72ms Min: 16.08ms Max: 17.48ms
[  653.1013] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 4.07 GPU: 0.00 Avg: 16.71ms Min: 15.56ms Max: 17.87ms
[  654.1043] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.03 GPU: 0.00 Avg: 16.72ms Min: 16.22ms Max: 17.25ms
[  655.1072] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 4.07 GPU: 0.00 Avg: 16.72ms Min: 15.45ms Max: 17.58ms
[  656.1108] V/PerfMon: FPS: 29.89 VPS: 59.78 CPU: 3.98 GPU: 0.00 Avg: 16.73ms Min: 16.17ms Max: 17.54ms


this is csr with csr+ and single-disc, and the trims made in csr have been removed after the jenova fight in the spiral hut just before the disc 2 swap, these are the duckstation logs whlie running the trimmed scenes


 649.3238] D/CDROM: CDROM setloc command (28, 13, 54)
[  649.3247] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  649.3247] D/CDROM: Seek time for 28:13:45->28:13:54 (9 LBA): 1806336 (53.333 ms) (forward)
[  649.3738] D/CDROM: Logical seek to [28:13:54] complete, now reading
[  649.3902] D/CDROM: Read sector 127029 [28:13:54]: mode 2 submode 0x08 into buffer 1
[  649.3904] D/CDROM: Read sector 127030 [28:13:55]: mode 2 submode 0x08 into buffer 2
[  649.3906] D/CDROM: Read sector 127031 [28:13:56]: mode 2 submode 0x08 into buffer 3
[  649.4068] D/CDROM: Read sector 127032 [28:13:57]: mode 2 submode 0x08 into buffer 4
[  649.4071] D/CDROM: Read sector 127033 [28:13:58]: mode 2 submode 0x08 into buffer 5
[  649.4235] D/CDROM: Read sector 127034 [28:13:59]: mode 2 submode 0x08 into buffer 6
[  649.4238] D/CDROM: Read sector 127035 [28:13:60]: mode 2 submode 0x89 into buffer 7
[  649.4238] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  649.5747] D/CodeCache: Breaking block 0x800B9F7C at 0x800BA000 due to page crossing
[  649.5754] D/CodeCache: Page fault handler invoked at PC=0x7ff609e1278f Address=0x2189f680020 (read), fastmem offset 1F800020
[  649.5756] D/CodeCache: Backpatching store at 0x7ff609e1278f[5] (pc 8003BF3C addr 1F800020): Bitmask 0BD19120 Addr 0 Data 0 Size 1 Signed 00
[  649.5757] D/Recompiler: Backpatching 0x7ff609e1278f (guest PC 0x8003BF3C) to slowmem
[  649.5757] D/CodeCache: Page fault handler invoked at PC=0x7ff609e127d1 Address=0x2189f680000 (write), fastmem offset 1F800000
[  649.5757] D/CodeCache: Backpatching store at 0x7ff609e127d1[5] (pc 8003BF44 addr 1F800000): Bitmask 0BD19140 Addr 0 Data 0 Size 1 Signed 00
[  649.5758] D/Recompiler: Backpatching 0x7ff609e127d1 (guest PC 0x8003BF44) to slowmem
[  649.5758] D/CodeCache: Page fault handler invoked at PC=0x7ff609e127e1 Address=0x2189f680026 (read), fastmem offset 1F800026
[  649.5759] D/CodeCache: Backpatching store at 0x7ff609e127e1[5] (pc 8003BF48 addr 1F800026): Bitmask 0BD19160 Addr 0 Data 0 Size 1 Signed 00
[  649.5759] D/Recompiler: Backpatching 0x7ff609e127e1 (guest PC 0x8003BF48) to slowmem
[  649.5760] D/CodeCache: Page fault handler invoked at PC=0x7ff609e127f1 Address=0x2189f68002c (read), fastmem offset 1F80002C
[  649.5760] D/CodeCache: Backpatching store at 0x7ff609e127f1[5] (pc 8003BF4C addr 1F80002C): Bitmask 0BD19180 Addr 0 Data 0 Size 1 Signed 00
[  649.5761] D/Recompiler: Backpatching 0x7ff609e127f1 (guest PC 0x8003BF4C) to slowmem
[  649.5762] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12801 Address=0x2189f680002 (write), fastmem offset 1F800002
[  649.5763] D/CodeCache: Backpatching store at 0x7ff609e12801[5] (pc 8003BF50 addr 1F800002): Bitmask 0BD191A0 Addr 0 Data 0 Size 1 Signed 00
[  649.5764] D/Recompiler: Backpatching 0x7ff609e12801 (guest PC 0x8003BF50) to slowmem
[  649.5764] D/CodeCache: Page fault handler invoked at PC=0x7ff609e1280d Address=0x2189f680022 (read), fastmem offset 1F800022
[  649.5764] D/CodeCache: Backpatching store at 0x7ff609e1280d[5] (pc 8003BF54 addr 1F800022): Bitmask 0BD191D0 Addr 0 Data 0 Size 1 Signed 00
[  649.5765] D/Recompiler: Backpatching 0x7ff609e1280d (guest PC 0x8003BF54) to slowmem
[  649.5765] D/CodeCache: Page fault handler invoked at PC=0x7ff609e1281d Address=0x2189f680004 (write), fastmem offset 1F800004
[  649.5765] D/CodeCache: Backpatching store at 0x7ff609e1281d[5] (pc 8003BF58 addr 1F800004): Bitmask 0BD19200 Addr 0 Data 0 Size 1 Signed 00
[  649.5766] D/Recompiler: Backpatching 0x7ff609e1281d (guest PC 0x8003BF58) to slowmem
[  649.5767] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12829 Address=0x2189f680028 (read), fastmem offset 1F800028
[  649.5767] D/CodeCache: Backpatching store at 0x7ff609e12829[5] (pc 8003BF5C addr 1F800028): Bitmask 0BD19230 Addr 0 Data 0 Size 1 Signed 00
[  649.5767] D/Recompiler: Backpatching 0x7ff609e12829 (guest PC 0x8003BF5C) to slowmem
[  649.5767] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12839 Address=0x2189f680006 (write), fastmem offset 1F800006
[  649.5768] D/CodeCache: Backpatching store at 0x7ff609e12839[5] (pc 8003BF60 addr 1F800006): Bitmask 0BD19260 Addr 0 Data 0 Size 1 Signed 00
[  649.5768] D/Recompiler: Backpatching 0x7ff609e12839 (guest PC 0x8003BF60) to slowmem
[  649.5768] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12845 Address=0x2189f68002e (read), fastmem offset 1F80002E
[  649.5769] D/CodeCache: Backpatching store at 0x7ff609e12845[5] (pc 8003BF64 addr 1F80002E): Bitmask 0BD19290 Addr 0 Data 0 Size 1 Signed 00
[  649.5769] D/Recompiler: Backpatching 0x7ff609e12845 (guest PC 0x8003BF64) to slowmem
[  649.5770] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12855 Address=0x2189f680008 (write), fastmem offset 1F800008
[  649.5770] D/CodeCache: Backpatching store at 0x7ff609e12855[5] (pc 8003BF68 addr 1F800008): Bitmask 0BD192C0 Addr 0 Data 0 Size 1 Signed 00
[  649.5770] D/Recompiler: Backpatching 0x7ff609e12855 (guest PC 0x8003BF68) to slowmem
[  649.5771] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12861 Address=0x2189f680024 (read), fastmem offset 1F800024
[  649.5771] D/CodeCache: Backpatching store at 0x7ff609e12861[5] (pc 8003BF6C addr 1F800024): Bitmask 0BD192F0 Addr 0 Data 0 Size 1 Signed 00
[  649.5772] D/Recompiler: Backpatching 0x7ff609e12861 (guest PC 0x8003BF6C) to slowmem
[  649.5772] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12871 Address=0x2189f68000a (write), fastmem offset 1F80000A
[  649.5773] D/CodeCache: Backpatching store at 0x7ff609e12871[5] (pc 8003BF70 addr 1F80000A): Bitmask 0BD19320 Addr 0 Data 0 Size 1 Signed 00
[  649.5773] D/Recompiler: Backpatching 0x7ff609e12871 (guest PC 0x8003BF70) to slowmem
[  649.5773] D/CodeCache: Page fault handler invoked at PC=0x7ff609e1287d Address=0x2189f68002a (read), fastmem offset 1F80002A
[  649.5774] D/CodeCache: Backpatching store at 0x7ff609e1287d[5] (pc 8003BF74 addr 1F80002A): Bitmask 0BD19350 Addr 0 Data 0 Size 1 Signed 00
[  649.5774] D/Recompiler: Backpatching 0x7ff609e1287d (guest PC 0x8003BF74) to slowmem
[  649.5775] D/CodeCache: Page fault handler invoked at PC=0x7ff609e1288d Address=0x2189f68000c (write), fastmem offset 1F80000C
[  649.5775] D/CodeCache: Backpatching store at 0x7ff609e1288d[5] (pc 8003BF78 addr 1F80000C): Bitmask 0BD19380 Addr 0 Data 0 Size 1 Signed 00
[  649.5775] D/Recompiler: Backpatching 0x7ff609e1288d (guest PC 0x8003BF78) to slowmem
[  649.5775] D/CodeCache: Page fault handler invoked at PC=0x7ff609e12899 Address=0x2189f680030 (read), fastmem offset 1F800030
[  649.5776] D/CodeCache: Backpatching store at 0x7ff609e12899[5] (pc 8003BF7C addr 1F800030): Bitmask 0BD193B0 Addr 0 Data 0 Size 1 Signed 00
[  649.5776] D/Recompiler: Backpatching 0x7ff609e12899 (guest PC 0x8003BF7C) to slowmem
[  649.5776] D/CodeCache: Page fault handler invoked at PC=0x7ff609e128a9 Address=0x2189f68000e (write), fastmem offset 1F80000E
[  649.5777] D/CodeCache: Backpatching store at 0x7ff609e128a9[5] (pc 8003BF80 addr 1F80000E): Bitmask 0BD193E0 Addr 0 Data 0 Size 1 Signed 00
[  649.5777] D/Recompiler: Backpatching 0x7ff609e128a9 (guest PC 0x8003BF80) to slowmem
[  649.5778] D/CodeCache: Page fault handler invoked at PC=0x7ff609e128c3 Address=0x2189f680010 (write), fastmem offset 1F800010
[  649.5778] D/CodeCache: Backpatching store at 0x7ff609e128c3[5] (pc 8003BF88 addr 1F800010): Bitmask 0BD19410 Addr 0 Data 0 Size 1 Signed 00
[  649.5778] D/Recompiler: Backpatching 0x7ff609e128c3 (guest PC 0x8003BF88) to slowmem
[  650.0923] V/PerfMon: FPS: 15.95 VPS: 59.83 CPU: 4.31 GPU: 0.00 Avg: 16.72ms Min: 16.13ms Max: 17.08ms
[  651.0952] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 4.06 GPU: 0.00 Avg: 16.71ms Min: 15.95ms Max: 17.70ms
[  652.0984] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.97 GPU: 0.00 Avg: 16.72ms Min: 16.08ms Max: 17.48ms
[  653.1013] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 4.07 GPU: 0.00 Avg: 16.71ms Min: 15.56ms Max: 17.87ms
[  654.1043] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.03 GPU: 0.00 Avg: 16.72ms Min: 16.22ms Max: 17.25ms
[  655.1072] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 4.07 GPU: 0.00 Avg: 16.72ms Min: 15.45ms Max: 17.58ms
[  656.1108] V/PerfMon: FPS: 29.89 VPS: 59.78 CPU: 3.98 GPU: 0.00 Avg: 16.73ms Min: 16.17ms Max: 17.54ms
[  657.1138] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.03 GPU: 0.00 Avg: 16.72ms Min: 15.78ms Max: 17.62ms
[  658.1166] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 4.11 GPU: 0.00 Avg: 16.71ms Min: 14.93ms Max: 18.79ms
[  665.4549] V/AudioStream: Audio buffer underflow, resampled 128 frames to 441
[  665.4573] V/AudioStream: Underrun compensation done (128 frames buffered)
[  665.4590] V/AudioStream: Audio buffer underflow, resampled 354 frames to 441
[  665.4874] V/PerfMon: FPS: 0.00 VPS: 0.14 CPU: 0.18 GPU: 0.00 Avg: 7370.74ms Min: 7370.74ms Max: 7370.74ms
[  665.4880] V/AudioStream: ~~~ Stretcher is now active @ tempo 0.83010614.
[  665.4890] V/AudioStream: Underrun compensation done (128 frames buffered)
[  666.0074] V/AudioStream: === Stretcher is now inactive.
[  666.4919] V/PerfMon: FPS: 30.86 VPS: 61.72 CPU: 4.27 GPU: 0.00 Avg: 16.20ms Min: 0.63ms Max: 17.44ms
[  667.4954] V/PerfMon: FPS: 29.90 VPS: 59.79 CPU: 4.02 GPU: 0.00 Avg: 16.72ms Min: 16.06ms Max: 17.29ms
[  668.4982] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 4.01 GPU: 0.00 Avg: 16.71ms Min: 15.94ms Max: 17.96ms
[  669.5016] V/PerfMon: FPS: 29.90 VPS: 59.79 CPU: 4.15 GPU: 0.00 Avg: 16.72ms Min: 15.75ms Max: 17.51ms
[  670.5042] V/PerfMon: FPS: 29.93 VPS: 59.85 CPU: 4.20 GPU: 0.00 Avg: 16.71ms Min: 16.11ms Max: 17.31ms
[  671.5073] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 4.38 GPU: 0.00 Avg: 16.72ms Min: 15.62ms Max: 17.76ms
[  672.5105] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 4.47 GPU: 0.00 Avg: 16.72ms Min: 15.85ms Max: 17.66ms
[  673.5137] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 4.54 GPU: 0.00 Avg: 16.72ms Min: 15.97ms Max: 17.32ms
[  674.5168] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.24 GPU: 0.00 Avg: 16.72ms Min: 15.35ms Max: 17.90ms
[  675.5193] V/PerfMon: FPS: 29.92 VPS: 59.85 CPU: 4.22 GPU: 0.00 Avg: 16.71ms Min: 16.31ms Max: 17.12ms
[  676.5228] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 4.15 GPU: 0.00 Avg: 16.72ms Min: 16.05ms Max: 17.51ms
[  677.5259] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 4.15 GPU: 0.00 Avg: 16.72ms Min: 16.06ms Max: 17.60ms
[  678.5286] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 4.54 GPU: 0.00 Avg: 16.71ms Min: 15.93ms Max: 17.77ms
[  679.5317] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.16 GPU: 0.00 Avg: 16.72ms Min: 16.25ms Max: 17.37ms
[  680.5350] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 4.59 GPU: 0.00 Avg: 16.72ms Min: 16.20ms Max: 17.41ms
[  681.5381] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.25 GPU: 0.00 Avg: 16.72ms Min: 15.82ms Max: 17.43ms
[  682.5407] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 4.36 GPU: 0.00 Avg: 16.71ms Min: 16.04ms Max: 17.46ms
[  683.5439] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 4.27 GPU: 0.00 Avg: 16.72ms Min: 16.26ms Max: 17.18ms
[  684.5474] V/PerfMon: FPS: 29.90 VPS: 59.79 CPU: 3.95 GPU: 0.00 Avg: 16.72ms Min: 15.92ms Max: 17.39ms
[  685.5501] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 4.00 GPU: 0.00 Avg: 16.71ms Min: 16.11ms Max: 17.49ms
[  686.5533] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 4.01 GPU: 0.00 Avg: 16.72ms Min: 16.03ms Max: 17.47ms
[  687.5560] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 4.11 GPU: 0.00 Avg: 16.71ms Min: 15.49ms Max: 17.80ms
[  688.5591] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.35 GPU: 0.00 Avg: 16.72ms Min: 16.10ms Max: 17.38ms
[  689.5623] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 4.12 GPU: 0.00 Avg: 16.72ms Min: 16.00ms Max: 17.86ms
[  690.5654] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 4.07 GPU: 0.00 Avg: 16.72ms Min: 15.56ms Max: 17.80ms
[  691.5685] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 4.06 GPU: 0.00 Avg: 16.72ms Min: 16.05ms Max: 17.22ms
[  692.5719] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 4.08 GPU: 0.00 Avg: 16.72ms Min: 16.26ms Max: 17.32ms
[  693.5745] V/PerfMon: FPS: 29.92 VPS: 59.85 CPU: 4.20 GPU: 0.00 Avg: 16.71ms Min: 16.03ms Max: 17.74ms
[  694.5775] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 4.34 GPU: 0.00 Avg: 16.72ms Min: 16.01ms Max: 17.38ms
[  695.5806] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.63 GPU: 0.00 Avg: 16.72ms Min: 16.30ms Max: 17.41ms
[  696.5838] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 4.32 GPU: 0.00 Avg: 16.72ms Min: 15.89ms Max: 17.78ms
[  697.5866] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 4.32 GPU: 0.00 Avg: 16.71ms Min: 15.95ms Max: 17.32ms
[  698.5897] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 4.46 GPU: 0.00 Avg: 16.72ms Min: 16.19ms Max: 17.34ms
[  699.5932] V/PerfMon: FPS: 29.90 VPS: 59.79 CPU: 4.38 GPU: 0.00 Avg: 16.72ms Min: 15.64ms Max: 17.52ms
[  700.5957] V/PerfMon: FPS: 29.93 VPS: 59.85 CPU: 4.03 GPU: 0.00 Avg: 16.71ms Min: 16.12ms Max: 17.22ms
[  701.5990] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 4.00 GPU: 0.00 Avg: 16.72ms Min: 15.98ms Max: 17.51ms
[  702.6017] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.98 GPU: 0.00 Avg: 16.71ms Min: 15.97ms Max: 17.49ms
[  703.6050] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 4.20 GPU: 0.00 Avg: 16.72ms Min: 16.19ms Max: 17.26ms
[  704.6078] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.99 GPU: 0.00 Avg: 16.71ms Min: 15.88ms Max: 17.29ms
[  705.6111] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.96 GPU: 0.00 Avg: 16.72ms Min: 16.23ms Max: 17.40ms
[  706.6141] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.07 GPU: 0.00 Avg: 16.72ms Min: 15.33ms Max: 17.57ms
[  706.7647] V/System: Target speed: 1000%
[  706.7649] V/System: Preset timing: immediate
[  706.7653] V/System: VSync: Disabled (present throttle allowed)
[  706.7692] V/AudioStream: ~~~ Stretcher is now active @ tempo 0.8272371.
[  706.8286] V/AudioStream: ___ Stretcher is being reset.
[  706.8331] V/AudioStream: ___ Stretcher is being reset.
[  706.8362] V/AudioStream: ___ Stretcher is being reset.
[  706.8382] V/AudioStream: ___ Stretcher is being reset.
[  706.8427] V/AudioStream: ___ Stretcher is being reset.
[  706.8464] V/AudioStream: ___ Stretcher is being reset.
[  706.8484] V/AudioStream: ___ Stretcher is being reset.
[  706.8529] V/AudioStream: ___ Stretcher is being reset.
[  706.8564] V/AudioStream: ___ Stretcher is being reset.
[  706.8583] V/AudioStream: ___ Stretcher is being reset.
[  706.8628] V/AudioStream: ___ Stretcher is being reset.
[  706.8665] V/AudioStream: ___ Stretcher is being reset.
[  706.8684] V/AudioStream: ___ Stretcher is being reset.
[  706.8741] V/System: Target speed: 100%
[  706.8742] V/System: Preset timing: immediate
[  706.8743] V/System: VSync: Disabled
[  706.8748] V/AudioStream: ___ Stretcher is being reset.
[  706.9918] V/System: Target speed: 1000%
[  706.9919] V/System: Preset timing: immediate
[  706.9922] V/System: VSync: Disabled (present throttle allowed)
[  707.1317] D/CodeCache: Breaking block 0x800D6FD0 at 0x800D7000 due to page crossing
[  707.2788] V/System: Target speed: 100%
[  707.2789] V/System: Preset timing: immediate
[  707.2792] V/System: VSync: Disabled
[  707.3630] V/System: Target speed: 1000%
[  707.3632] V/System: Preset timing: immediate
[  707.3632] V/System: VSync: Disabled (present throttle allowed)
[  707.5140] V/System: Target speed: 100%
[  707.5141] V/System: Preset timing: immediate
[  707.5145] V/System: VSync: Disabled
[  707.6149] V/PerfMon: FPS: 176.86 VPS: 352.72 CPU: 15.46 GPU: 0.00 Avg: 2.84ms Min: 0.33ms Max: 17.30ms
[  707.6320] V/System: Target speed: 1000%
[  707.6321] V/System: Preset timing: immediate
[  707.6324] V/System: VSync: Disabled (present throttle allowed)
[  707.8152] V/System: Target speed: 100%
[  707.8154] V/System: Preset timing: immediate
[  707.8157] V/System: VSync: Disabled
[  708.2173] V/System: Target speed: 1000%
[  708.2175] V/System: Preset timing: immediate
[  708.2179] V/System: VSync: Disabled (present throttle allowed)
[  708.3301] V/System: Target speed: 100%
[  708.3302] V/System: Preset timing: immediate
[  708.3306] V/System: VSync: Disabled
[  708.5147] V/System: Target speed: 1000%
[  708.5148] V/System: Preset timing: immediate
[  708.5151] V/System: VSync: Disabled (present throttle allowed)
[  708.6159] V/PerfMon: FPS: 133.87 VPS: 267.73 CPU: 12.82 GPU: 0.00 Avg: 3.74ms Min: 0.32ms Max: 17.82ms
[  708.6224] V/System: Target speed: 100%
[  708.6225] V/System: Preset timing: immediate
[  708.6225] V/System: VSync: Disabled
[  708.7235] V/System: Target speed: 1000%
[  708.7236] V/System: Preset timing: immediate
[  708.7239] V/System: VSync: Disabled (present throttle allowed)
[  708.8581] V/System: Target speed: 100%
[  708.8583] V/System: Preset timing: immediate
[  708.8583] V/System: VSync: Disabled
[  708.9593] V/System: Target speed: 1000%
[  708.9594] V/System: Preset timing: immediate
[  708.9597] V/System: VSync: Disabled (present throttle allowed)
[  709.0270] V/System: Target speed: 100%
[  709.0272] V/System: Preset timing: immediate
[  709.0275] V/System: VSync: Disabled
[  709.5192] V/AudioStream: Audio buffer underflow, resampled 42 frames to 441
[  709.5391] V/AudioStream: Underrun compensation done (128 frames buffered)
[  709.6297] V/PerfMon: FPS: 84.83 VPS: 169.66 CPU: 8.17 GPU: 0.00 Avg: 5.89ms Min: 0.36ms Max: 17.73ms
[  709.9307] V/AudioStream: === Stretcher is now inactive.
[  710.6326] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 4.13 GPU: 0.00 Avg: 16.71ms Min: 16.19ms Max: 17.46ms
[  711.6361] V/PerfMon: FPS: 29.89 VPS: 59.79 CPU: 4.06 GPU: 0.00 Avg: 16.73ms Min: 15.96ms Max: 17.47ms
[  712.6387] V/PerfMon: FPS: 29.92 VPS: 59.85 CPU: 4.06 GPU: 0.00 Avg: 16.71ms Min: 15.76ms Max: 17.59ms
[  713.6417] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 4.09 GPU: 0.00 Avg: 16.72ms Min: 15.85ms Max: 17.89ms
[  714.6452] V/PerfMon: FPS: 29.90 VPS: 59.79 CPU: 3.93 GPU: 0.00 Avg: 16.72ms Min: 16.10ms Max: 17.25ms
[  715.6478] V/PerfMon: FPS: 29.92 VPS: 59.85 CPU: 4.15 GPU: 0.00 Avg: 16.71ms Min: 15.25ms Max: 17.99ms
[  716.6510] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.97 GPU: 0.00 Avg: 16.72ms Min: 16.06ms Max: 17.54ms

the transition to disc 2 is not loading, just getting a black screen and I can hear music from start of disc 2 but I was expecting the break scene at the start of csr disc 2 not the regular staart of disc 2
