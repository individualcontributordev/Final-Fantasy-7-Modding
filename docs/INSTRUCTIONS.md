# Task: test v7 (LOSLAKE1 + endings, CD-sized)

## What v7 is

Same CD image (~731 MiB) as working endings, plus **CANONON** restored at
LBA **250450** so LOSLAKE1 can play again.

| Check | Expect |
|-------|--------|
| LOSLAKE1 lake FMV | Full CANONON (should work) |
| Endings after final battle | Play; possible glitch mid long credits |
| Bin size | **766340400** |

Mid-ENDING2E (LBA 250450–257808) is CANONON on purpose so the lake works.

## What you do

### 0. Update

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
```

### 1. Rebuild (if bin missing or unsure)

```bash
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

Expect last lines: CANONON OK @ 250450, size 766340400, free80=34175.

### 2. Open

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

Do **not** use `ff7_d1_playtest_csr_sd_movies.cue` for this test.

### 3. Smoke

1. **LOSLAKE1** — lake / Bugenhagen FMV plays with video+audio  
2. **After final battle** — ending sequence / credits play (note any mid-roll hitch)  
3. Optional: bin size still 766340400  

### 4. Reply

1. LOSLAKE1 OK?  
2. Endings OK / mid-credit glitch?  
3. Bin size  

 137.9522] D/CDROM: Read sector 250610 [55:41:35]: mode 2 submode 0x42 into buffer 7
[  137.9524] D/CDROM: Read sector 250611 [55:41:36]: mode 2 submode 0x42 into buffer 0
[  137.9693] D/CDROM: Read sector 250612 [55:41:37]: mode 2 submode 0x42 into buffer 1
[  137.9694] D/CDROM: Read sector 250613 [55:41:38]: mode 2 submode 0x42 into buffer 2
[  137.9695] D/CDROM: Read sector 250614 [55:41:39]: mode 2 submode 0x42 into buffer 3
[  137.9858] D/CDROM: Read sector 250615 [55:41:40]: mode 2 submode 0x64 into buffer 4
[  137.9861] D/CDROM: Read sector 250616 [55:41:41]: mode 2 submode 0x42 into buffer 4
[  138.0025] D/CDROM: Read sector 250617 [55:41:42]: mode 2 submode 0x42 into buffer 5
[  138.0026] D/CDROM: Read sector 250618 [55:41:43]: mode 2 submode 0x42 into buffer 6
[  138.0027] D/CDROM: Read sector 250619 [55:41:44]: mode 2 submode 0x42 into buffer 7
[  138.0193] D/CDROM: Read sector 250620 [55:41:45]: mode 2 submode 0x42 into buffer 0
[  138.0196] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  138.2698] V/PerfMon: FPS: 18.94 VPS: 59.83 CPU: 4.93 GPU: 0.00 Avg: 16.72ms Min: 16.18ms Max: 17.22ms
[  138.8884] D/CodeCache: Breaking block 0x800A0F90 at 0x800A1000 due to page crossing
[  138.8885] D/CodeCache: Breaking block 0x800A0FAC at 0x800A1000 due to page crossing
[  138.9220] D/CodeCache: Page fault on protected RAM @ 0x0003623C (page #54), invalidating code cache.
[  138.9555] D/CodeCache: Page fault on protected RAM @ 0x0003623C (page #54), invalidating code cache.
[  138.9890] D/CodeCache: Page fault on protected RAM @ 0x0003623C (page #54), invalidating code cache.
[  139.0223] D/CodeCache: Page fault on protected RAM @ 0x0003623C (page #54), invalidating code cache.
[  139.0555] D/CodeCache: Page fault on protected RAM @ 0x0003623C (page #54), invalidating code cache.
[  139.0556] D/CodeCache: 5 invalidations in 8 frames to page 54 [0x00036000 -> 0x00037000], switching to manual protection
[  139.2731] V/PerfMon: FPS: 30.90 VPS: 59.80 CPU: 3.40 GPU: 0.00 Avg: 16.72ms Min: 16.16ms Max: 17.16ms
[  140.2760] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 2.88 GPU: 0.00 Avg: 16.71ms Min: 16.01ms Max: 17.48ms
[  141.2794] V/PerfMon: FPS: 29.90 VPS: 59.79 CPU: 2.92 GPU: 0.00 Avg: 16.72ms Min: 16.23ms Max: 17.43ms
[  142.2820] V/PerfMon: FPS: 29.92 VPS: 59.85 CPU: 3.07 GPU: 0.00 Avg: 16.71ms Min: 16.16ms Max: 17.25ms
[  143.2855] V/PerfMon: FPS: 29.90 VPS: 59.79 CPU: 2.92 GPU: 0.00 Avg: 16.72ms Min: 16.04ms Max: 17.65ms
