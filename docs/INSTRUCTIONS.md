# INSTRUCTIONS — rebuild Disc 1 (Single-disc v0.1.25)

## Why

One Single-disc checkbox. The path-engine fix (MOVIE_ID / fields 71+255) is
hidden and always auto-applied with it (GitHub layer size split).

## Build

1. Hard-refresh https://individualcontributor.dev/builder/
2. Base: CSR
3. Mods: **Single-disc** only — badge **v0.1.25**. Do not look for a second row.
4. CSR+ off for this check
5. APPLIED should list (order):
   - single-disc-csr-manip-movies-v0.1.4
   - single-disc-on-csr-v0.1.24
   - single-disc-on-csr-v0.1.25  (auto, not in checklist)
6. Build Disc 1

## Test

| Spot | Expect |
|------|--------|
| FSHIP_12 then MD8_5 (#731) | Full PARASHOT; field not glitched |
| FSHIP_24 (#71) | CSR D2 trim |
| BLIN66_6 (#255) | CSR D2 trim |

## Evidence

- APPLIED.txt
- Pass/fail for #731 / #71 / #255

duckstation output 

 29.5663] D/CDROM: Seek time for 80:52:34->80:52:34 (0 LBA): 1806336 (53.333 ms) (1T back+forward)
[   29.6155] W(DoSeekComplete): Logical seek to [80:52:34] failed
[   29.6156] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x02, params = []
[   29.6161] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x80, 0x52, 0x34]
[   29.6161] D/CDROM: CDROM setloc command (80, 52, 34)
[   29.6162] D/CDROM: CDROM executing command 0x0E (Setmode), stat = 0x02, params = [0xA0]
[   29.6163] D/CDROM: CDROM setmode command 0xA0
[   29.6164] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[   29.6165] D/CDROM: Seek time for 80:52:34->80:52:34 (0 LBA): 1806336 (53.333 ms) (1T back+forward)
[   29.6664] W(DoSeekComplete): Logical seek to [80:52:34] failed
[   29.6820] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x02, params = []
[   29.6822] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x80, 0x52, 0x34]
[   29.6824] D/CDROM: CDROM setloc command (80, 52, 34)
[   29.6825] D/CDROM: CDROM executing command 0x0E (Setmode), stat = 0x02, params = [0xA0]
[   29.6825] D/CDROM: CDROM setmode command 0xA0
[   29.6826] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[   29.6827] D/CDROM: Seek time for 80:52:34->80:52:34 (0 LBA): 1806336 (53.333 ms) (1T back+forward)
[   29.7325] W(DoSeekComplete): Logical seek to [80:52:34] failed
[   29.7326] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x02, params = []
[   29.7330] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x80, 0x52, 0x34]
[   29.7331] D/CDROM: CDROM setloc command (80, 52, 34)
[   29.7332] D/CDROM: CDROM executing command 0x0E (Setmode), stat = 0x02, params = [0xA0]
[   29.7332] D/CDROM: CDROM setmode command 0xA0
[   29.7332] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[   29.7333] D/CDROM: Seek time for 80:52:34->80:52:34 (0 LBA): 1806336 (53.333 ms) (1T back+forward)