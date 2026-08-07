# Task: ending credits test v6 (D3 absolute LBAs)

## What worked / what failed last time

- **v5 fixed LASTMAP freeze** (id23 = camera BIN; early MOVIE removed).
- After final battle: text boxes, then **black + no sound** (not a hard freeze).

Log:

```text
setloc (36, 23, 33)   → ISO LBA 163608
ReadS … Seek … failed
```

**163608 is Disc 3’s ENDING01 start.**  
Our inject had put ENDING01 at grown LBA **325825** and updated MOVIE_ID —  
the game still sought the **Disc 3 absolute address**. Seek failed → black silence.

Same idea as CANONON @ LBA **250450**.

## What v6 does

1. LASTMAP v5 field patch + pristine LAS4_0.  
2. Copy D3 raw sectors for endings to **exact D3 LBAs**:

| id | D3 file | D3 LBA |
|---:|---------|-------:|
| 23 | LASTMAP.BIN | 161972 |
| 24 | LASTFLOR.MOV | 162081 |
| 25 | ENDING01.MOV | **163608** |
| 26 | ENDING3E.MOV | 172631 |
| 29 | ENDING2E.MOV | 197242 |

3. Dirents + MOVIE_ID rows match those LBAs and D3 size/aux.

Bin stays ~**766340400** if endings fit in existing image span (overwrites other D1 movie ranges at those addresses). DuckStation test only.

## What you do

1. Pull  
2. Open ending-test cue (rebuild if needed)  
3. Past final battle → text → should get **ENDING01** (not black)  
4. Reply  

---

## 0. Update

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
```

---

## 1. Open

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

---

## 2. Rebuild if needed

```bash
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

---

## 3. Smoke

- LASTMAP still OK (no MDEC crash)  
- After final battle / dialogue: real ending FMV + audio  
- Note black screen or seek errors  

---

## 4. Reply

1. Bin size  
2. What played after text  
3. Freeze / black / sound  

 2331.4934] V/System: VSync: Disabled (present throttle allowed)
[ 2331.5149] D/CodeCache: Breaking block 0x800D5FC0 at 0x800D6000 due to page crossing
[ 2331.5339] D/CodeCache: Breaking block 0x800CAFE4 at 0x800CB000 due to page crossing
[ 2331.7480] V/PerfMon: FPS: 144.82 VPS: 290.65 CPU: 12.95 GPU: 0.00 Avg: 3.44ms Min: 0.50ms Max: 17.71ms
[ 2331.9387] D/CodeCache: Breaking block 0x800D6FD0 at 0x800D7000 due to page crossing
[ 2332.0862] V/System: Target speed: 100%
[ 2332.0864] V/System: Preset timing: immediate
[ 2332.0872] V/System: VSync: Disabled
[ 2332.5442] V/AudioStream: Audio buffer underflow, resampled 417 frames to 441
[ 2332.5740] V/AudioStream: Underrun compensation done (128 frames buffered)
[ 2332.5940] V/AudioStream: Audio buffer underflow, resampled 1 frames to 441
[ 2332.6140] V/AudioStream: Underrun compensation done (128 frames buffered)
[ 2332.7561] V/PerfMon: FPS: 120.01 VPS: 240.03 CPU: 10.12 GPU: 0.00 Avg: 4.17ms Min: 0.98ms Max: 17.10ms
[ 2332.9402] V/AudioStream: === Stretcher is now inactive.
[ 2333.7590] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.86 GPU: 0.00 Avg: 16.72ms Min: 16.11ms Max: 17.23ms
[ 2334.7625] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.80 GPU: 0.00 Avg: 16.72ms Min: 16.27ms Max: 17.21ms
[ 2335.7651] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.85 GPU: 0.00 Avg: 16.71ms Min: 15.82ms Max: 17.74ms
[ 2336.0496] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x55, 0x41, 0x25]
[ 2336.0498] D/CDROM: CDROM setloc command (55, 41, 25)
[ 2336.1497] D/CDROM: CDROM executing command 0x0E (Setmode), stat = 0x02, params = [0xE0]
[ 2336.1499] D/CDROM: CDROM setmode command 0xE0
[ 2336.1509] D/CDROM: CDROM executing command 0x1B (ReadS), stat = 0x02, params = []
[ 2336.1509] D/CDROM: Seek time for 24:34:67->55:41:25 (139983 LBA): 19909974 (587.856 ms) (2N/sled forward)
[ 2336.7351] D/CDROM: Logical seek to [55:41:25] complete, now reading
[ 2336.7351] D/CDROM: Read sector 250600 [55:41:25]: mode 2 submode 0x48 into buffer 1
[ 2336.7517] D/CDROM: Read sector 250601 [55:41:26]: mode 2 submode 0x48 into buffer 2
[ 2336.7522] D/CDROM: Read sector 250602 [55:41:27]: mode 2 submode 0x48 into buffer 3
[ 2336.7522] D/CDROM: Read sector 250603 [55:41:28]: mode 2 submode 0x48 into buffer 4
[ 2336.7683] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.17 GPU: 0.00 Avg: 16.72ms Min: 16.19ms Max: 17.16ms
[ 2336.7683] D/CDROM: Read sector 250604 [55:41:29]: mode 2 submode 0x48 into buffer 5
[ 2336.7688] D/CDROM: Read sector 250605 [55:41:30]: mode 2 submode 0x48 into buffer 6
[ 2336.7854] D/CDROM: Read sector 250606 [55:41:31]: mode 2 submode 0x48 into buffer 7
[ 2336.7856] D/CDROM: Read sector 250607 [55:41:32]: mode 2 submode 0x64 into buffer 0
[ 2336.7859] D/CDROM: Read sector 250608 [55:41:33]: mode 2 submode 0x48 into buffer 0
[ 2336.8020] D/CDROM: Read sector 250609 [55:41:34]: mode 2 submode 0x48 into buffer 1
[ 2336.8022] D/CDROM: Read sector 250610 [55:41:35]: mode 2 submode 0x48 into buffer 2
[ 2336.8186] D/CDROM: Read sector 250611 [55:41:36]: mode 2 submode 0x48 into buffer 3
[ 2336.8191] D/CDROM: Read sector 250612 [55:41:37]: mode 2 submode 0x48 into buffer 4
[ 2336.8193] D/CDROM: Read sector 250613 [55:41:38]: mode 2 submode 0x48 into buffer 5
[ 2336.8354] D/CDROM: Read sector 250614 [55:41:39]: mode 2 submode 0x48 into buffer 6
[ 2336.8354] D/CDROM: Read sector 250615 [55:41:40]: mode 2 submode 0x64 into buffer 7
[ 2336.8525] D/CDROM: Read sector 250616 [55:41:41]: mode 2 submode 0x48 into buffer 7
[ 2336.8528] D/CDROM: Read sector 250617 [55:41:42]: mode 2 submode 0x48 into buffer 0
[ 2336.8530] D/CDROM: Read sector 250618 [55:41:43]: mode 2 submode 0x48 into buffer 1
[ 2336.8689] D/CDROM: Read sector 250619 [55:41:44]: mode 2 submode 0x48 into buffer 2
[ 2336.8691] D/CDROM: Read sector 250620 [55:41:45]: mode 2 submode 0x48 into buffer 3
[ 2336.8862] D/CDROM: Read sector 250621 [55:41:46]: mode 2 submode 0x48 into buffer 4
[ 2336.8865] D/CDROM: Read sector 250622 [55:41:47]: mode 2 submode 0x48 into buffer 5
[ 2336.8870] D/CDROM: Read sector 250623 [55:41:48]: mode 2 submode 0x64 into buffer 6
[ 2336.9026] D/CDROM: Read sector 250624 [55:41:49]: mode 2 submode 0x48 into buffer 6
[ 2336.9028] D/CDROM: Read sector 250625 [55:41:50]: mode 2 submode 0x48 into buffer 7
[ 2336.9192] D/CDROM: Read sector 250626 [55:41:51]: mode 2 submode 0x48 into buffer 0
[ 2336.9194] D/CDROM: Read sector 250627 [55:41:52]: mode 2 submode 0x48 into buffer 1
[ 2336.9197] D/CDROM: Read sector 250628 [55:41:53]: mode 2 submode 0x48 into buffer 2
[ 2336.9360] D/CodeCache: Breaking block 0x80035FDC at 0x80036000 due to page crossing
[ 2336.9365] D/CDROM: Read sector 250629 [55:41:54]: mode 2 submode 0x48 into buffer 3
[ 2336.9370] D/CDROM: Read sector 250630 [55:41:55]: mode 2 submode 0x48 into buffer 4
[ 2336.9524] D/CDROM: Read sector 250631 [55:41:56]: mode 2 submode 0x64 into buffer 5
[ 2336.9529] D/CDROM: Read sector 250632 [55:41:57]: mode 2 submode 0x48 into buffer 5
[ 2336.9531] D/CDROM: Read sector 250633 [55:41:58]: mode 2 submode 0x48 into buffer 6
[ 2336.9692] D/CDROM: Read sector 250634 [55:41:59]: mode 2 submode 0x48 into buffer 7
[ 2336.9695] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2337.0364] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x02, params = []
[ 2337.0364] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x16, 0x24, 0x08]
[ 2337.0366] D/CDROM: CDROM setloc command (16, 24, 08)
[ 2337.0369] D/CDROM: CDROM executing command 0x0E (Setmode), stat = 0x02, params = [0xA0]
[ 2337.0371] D/CDROM: CDROM setmode command 0xA0
[ 2337.0371] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2337.0371] D/CDROM: Seek time for 55:41:50->16:24:08 (176817 LBA): 22085666 (652.095 ms) (2N/sled backward)
[ 2337.6880] D/CDROM: Logical seek to [16:24:08] complete, now reading
[ 2337.6880] D/CDROM: Read sector 73808 [16:24:08]: mode 2 submode 0x08 into buffer 1
[ 2337.7046] D/CDROM: Read sector 73809 [16:24:09]: mode 2 submode 0x08 into buffer 2
[ 2337.7048] D/CDROM: Read sector 73810 [16:24:10]: mode 2 submode 0x08 into buffer 3
[ 2337.7217] D/CDROM: Read sector 73811 [16:24:11]: mode 2 submode 0x08 into buffer 4
[ 2337.7217] D/CDROM: Read sector 73812 [16:24:12]: mode 2 submode 0x08 into buffer 5
[ 2337.7224] D/CDROM: Read sector 73813 [16:24:13]: mode 2 submode 0x08 into buffer 6
[ 2337.7380] D/CDROM: Read sector 73814 [16:24:14]: mode 2 submode 0x08 into buffer 7
[ 2337.7385] D/CDROM: Read sector 73815 [16:24:15]: mode 2 submode 0x08 into buffer 0
[ 2337.7544] D/CDROM: Read sector 73816 [16:24:16]: mode 2 submode 0x08 into buffer 1
[ 2337.7546] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2337.7712] V/PerfMon: FPS: 39.88 VPS: 59.82 CPU: 4.53 GPU: 0.00 Avg: 16.72ms Min: 16.01ms Max: 17.25ms
[ 2337.8052] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x16, 0x24, 0x17]
[ 2337.8054] D/CDROM: CDROM setloc command (16, 24, 17)
[ 2337.8057] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2337.8057] D/CDROM: Seek time for 16:24:09->16:24:17 (8 LBA): 1806336 (53.333 ms) (forward)
[ 2337.8555] D/CDROM: Logical seek to [16:24:17] complete, now reading
[ 2337.8716] D/CDROM: Read sector 73817 [16:24:17]: mode 2 submode 0x08 into buffer 1
[ 2337.8718] D/CDROM: Read sector 73818 [16:24:18]: mode 2 submode 0x08 into buffer 2
[ 2337.8884] D/CDROM: Read sector 73819 [16:24:19]: mode 2 submode 0x08 into buffer 3
[ 2337.8884] D/CDROM: Read sector 73820 [16:24:20]: mode 2 submode 0x08 into buffer 4
[ 2337.8887] D/CDROM: Read sector 73821 [16:24:21]: mode 2 submode 0x08 into buffer 5
[ 2337.9050] D/CDROM: Read sector 73822 [16:24:22]: mode 2 submode 0x08 into buffer 6
[ 2337.9053] D/CDROM: Read sector 73823 [16:24:23]: mode 2 submode 0x08 into buffer 7
[ 2337.9221] D/CDROM: Read sector 73824 [16:24:24]: mode 2 submode 0x08 into buffer 0
[ 2337.9224] D/CDROM: Read sector 73825 [16:24:25]: mode 2 submode 0x08 into buffer 1
[ 2337.9224] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2337.9888] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x16, 0x24, 0x26]
[ 2337.9890] D/CDROM: CDROM setloc command (16, 24, 26)
[ 2337.9890] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2337.9895] D/CDROM: Seek time for 16:24:18->16:24:26 (8 LBA): 1806336 (53.333 ms) (forward)
[ 2338.0391] D/CDROM: Logical seek to [16:24:26] complete, now reading
[ 2338.0393] D/CDROM: Read sector 73826 [16:24:26]: mode 2 submode 0x08 into buffer 1
[ 2338.0554] D/CDROM: Read sector 73827 [16:24:27]: mode 2 submode 0x08 into buffer 2
[ 2338.0557] D/CDROM: Read sector 73828 [16:24:28]: mode 2 submode 0x08 into buffer 3
[ 2338.0725] D/CDROM: Read sector 73829 [16:24:29]: mode 2 submode 0x08 into buffer 4
[ 2338.0728] D/CDROM: Read sector 73830 [16:24:30]: mode 2 submode 0x08 into buffer 5
[ 2338.0728] D/CDROM: Read sector 73831 [16:24:31]: mode 2 submode 0x08 into buffer 6
[ 2338.0891] D/CDROM: Read sector 73832 [16:24:32]: mode 2 submode 0x08 into buffer 7
[ 2338.0894] D/CDROM: Read sector 73833 [16:24:33]: mode 2 submode 0x89 into buffer 0
[ 2338.0894] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2338.1562] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x16, 0x24, 0x03]
[ 2338.1565] D/CDROM: CDROM setloc command (16, 24, 03)
[ 2338.1567] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2338.1567] D/CDROM: Seek time for 16:24:26->16:24:03 (23 LBA): 1693440 (50.000 ms) (NT backward)
[ 2338.2065] D/CDROM: Logical seek to [16:24:03] complete, now reading
[ 2338.2065] D/CDROM: Read sector 73803 [16:24:03]: mode 2 submode 0x08 into buffer 1
[ 2338.2229] D/CDROM: Read sector 73804 [16:24:04]: mode 2 submode 0x08 into buffer 2
[ 2338.2231] D/CDROM: Read sector 73805 [16:24:05]: mode 2 submode 0x08 into buffer 3
[ 2338.2231] D/CDROM: Read sector 73806 [16:24:06]: mode 2 submode 0x08 into buffer 4
[ 2338.2395] D/CDROM: Read sector 73807 [16:24:07]: mode 2 submode 0x89 into buffer 5
[ 2338.2397] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2338.2898] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x16, 0x24, 0x34]
[ 2338.2898] D/CDROM: CDROM setloc command (16, 24, 34)
[ 2338.2900] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2338.2900] D/CDROM: Seek time for 16:24:00->16:24:34 (34 LBA): 1693440 (50.000 ms) (NT forward)
[ 2338.3406] D/CDROM: Logical seek to [16:24:34] complete, now reading
[ 2338.3569] D/CDROM: Read sector 73834 [16:24:34]: mode 2 submode 0x08 into buffer 1
[ 2338.3572] D/CDROM: Read sector 73835 [16:24:35]: mode 2 submode 0x08 into buffer 2
[ 2338.3733] D/CDROM: Read sector 73836 [16:24:36]: mode 2 submode 0x08 into buffer 3
[ 2338.3733] D/CDROM: Read sector 73837 [16:24:37]: mode 2 submode 0x08 into buffer 4
[ 2338.3738] D/CDROM: Read sector 73838 [16:24:38]: mode 2 submode 0x08 into buffer 5
[ 2338.3901] D/CDROM: Read sector 73839 [16:24:39]: mode 2 submode 0x08 into buffer 6
[ 2338.3904] D/CDROM: Read sector 73840 [16:24:40]: mode 2 submode 0x08 into buffer 7
[ 2338.4065] D/CDROM: Read sector 73841 [16:24:41]: mode 2 submode 0x08 into buffer 0
[ 2338.4067] D/CDROM: Read sector 73842 [16:24:42]: mode 2 submode 0x08 into buffer 1
[ 2338.4067] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2338.4741] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x16, 0x24, 0x43]
[ 2338.4741] D/CDROM: CDROM setloc command (16, 24, 43)
[ 2338.4746] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2338.4746] D/CDROM: Seek time for 16:24:35->16:24:43 (8 LBA): 1806336 (53.333 ms) (forward)
[ 2338.5237] D/CDROM: Logical seek to [16:24:43] complete, now reading
[ 2338.5239] D/CDROM: Read sector 73843 [16:24:43]: mode 2 submode 0x08 into buffer 1
[ 2338.5403] D/CDROM: Read sector 73844 [16:24:44]: mode 2 submode 0x08 into buffer 2
[ 2338.5405] D/CDROM: Read sector 73845 [16:24:45]: mode 2 submode 0x08 into buffer 3
[ 2338.5408] D/CDROM: Read sector 73846 [16:24:46]: mode 2 submode 0x08 into buffer 4
[ 2338.5574] D/CDROM: Read sector 73847 [16:24:47]: mode 2 submode 0x08 into buffer 5
[ 2338.5576] D/CDROM: Read sector 73848 [16:24:48]: mode 2 submode 0x08 into buffer 6
[ 2338.5740] D/CDROM: Read sector 73849 [16:24:49]: mode 2 submode 0x08 into buffer 7
[ 2338.5742] D/CDROM: Read sector 73850 [16:24:50]: mode 2 submode 0x08 into buffer 0
[ 2338.5745] D/CDROM: Read sector 73851 [16:24:51]: mode 2 submode 0x08 into buffer 1
[ 2338.5908] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2338.6406] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x16, 0x24, 0x52]
[ 2338.6409] D/CDROM: CDROM setloc command (16, 24, 52)
[ 2338.6409] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2338.6409] D/CDROM: Seek time for 16:24:44->16:24:52 (8 LBA): 1806336 (53.333 ms) (forward)
[ 2338.6909] D/CDROM: Logical seek to [16:24:52] complete, now reading
[ 2338.7080] D/CDROM: Read sector 73852 [16:24:52]: mode 2 submode 0x08 into buffer 1
[ 2338.7083] D/CDROM: Read sector 73853 [16:24:53]: mode 2 submode 0x08 into buffer 2
[ 2338.7244] D/CDROM: Read sector 73854 [16:24:54]: mode 2 submode 0x89 into buffer 3
[ 2338.7244] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2338.7744] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 4.18 GPU: 0.00 Avg: 16.72ms Min: 16.25ms Max: 17.30ms
[ 2338.7749] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x16]
[ 2338.7749] D/CDROM: CDROM setloc command (28, 13, 16)
[ 2338.7751] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2338.7751] D/CDROM: Seek time for 16:24:47->28:13:16 (53144 LBA): 14401440 (425.213 ms) (2N/sled forward)
[ 2339.2092] D/CDROM: Logical seek to [28:13:16] complete, now reading
[ 2339.2095] D/CDROM: Read sector 126991 [28:13:16]: mode 2 submode 0x08 into buffer 1
[ 2339.2102] D/CDROM: Read sector 126992 [28:13:17]: mode 2 submode 0x08 into buffer 2
[ 2339.2261] D/CDROM: Read sector 126993 [28:13:18]: mode 2 submode 0x08 into buffer 3
[ 2339.2263] D/CDROM: Read sector 126994 [28:13:19]: mode 2 submode 0x89 into buffer 4
[ 2339.2263] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2339.2930] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x54]
[ 2339.2932] D/CDROM: CDROM setloc command (28, 13, 54)
[ 2339.2932] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2339.2935] D/CDROM: Seek time for 28:13:11->28:13:54 (43 LBA): 1693440 (50.000 ms) (NT forward)
[ 2339.3428] D/CDROM: Logical seek to [28:13:54] complete, now reading
[ 2339.3430] D/CDROM: Read sector 127029 [28:13:54]: mode 2 submode 0x08 into buffer 1
[ 2339.3599] D/CDROM: Read sector 127030 [28:13:55]: mode 2 submode 0x08 into buffer 2
[ 2339.3604] D/CDROM: Read sector 127031 [28:13:56]: mode 2 submode 0x08 into buffer 3
[ 2339.3762] D/CDROM: Read sector 127032 [28:13:57]: mode 2 submode 0x08 into buffer 4
[ 2339.3765] D/CDROM: Read sector 127033 [28:13:58]: mode 2 submode 0x08 into buffer 5
[ 2339.3770] D/CDROM: Read sector 127034 [28:13:59]: mode 2 submode 0x08 into buffer 6
[ 2339.3933] D/CDROM: Read sector 127035 [28:13:60]: mode 2 submode 0x89 into buffer 7
[ 2339.3936] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2339.7776] V/PerfMon: FPS: 7.97 VPS: 59.81 CPU: 3.93 GPU: 0.00 Avg: 16.72ms Min: 16.09ms Max: 17.13ms
[ 2340.7805] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.24 GPU: 0.00 Avg: 16.72ms Min: 16.01ms Max: 17.29ms
[ 2341.7839] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 4.13 GPU: 0.00 Avg: 16.72ms Min: 16.25ms Max: 17.33ms
[ 2342.6204] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x26, 0x04]
[ 2342.6206] D/CDROM: CDROM setloc command (24, 26, 04)
[ 2342.6365] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2342.6365] D/CDROM: Seek time for 28:13:53->24:26:04 (17074 LBA): 11448005 (338.010 ms) (2N/sled backward)
[ 2342.7869] V/PerfMon: FPS: 35.90 VPS: 59.83 CPU: 4.30 GPU: 0.00 Avg: 16.72ms Min: 15.92ms Max: 17.41ms
[ 2342.9707] D/CDROM: Logical seek to [24:26:04] complete, now reading
[ 2342.9709] D/CDROM: Read sector 109954 [24:26:04]: mode 2 submode 0x08 into buffer 1
[ 2342.9873] D/CDROM: Read sector 109955 [24:26:05]: mode 2 submode 0x08 into buffer 2
[ 2342.9878] D/CDROM: Read sector 109956 [24:26:06]: mode 2 submode 0x08 into buffer 3
[ 2342.9880] D/CDROM: Read sector 109957 [24:26:07]: mode 2 submode 0x08 into buffer 4
[ 2343.0046] D/CDROM: Read sector 109958 [24:26:08]: mode 2 submode 0x08 into buffer 5
[ 2343.0049] D/CDROM: Read sector 109959 [24:26:09]: mode 2 submode 0x08 into buffer 6
[ 2343.0210] D/CDROM: Read sector 109960 [24:26:10]: mode 2 submode 0x08 into buffer 7
[ 2343.0212] D/CDROM: Read sector 109961 [24:26:11]: mode 2 submode 0x08 into buffer 0
[ 2343.0217] D/CDROM: Read sector 109962 [24:26:12]: mode 2 submode 0x08 into buffer 1
[ 2343.0217] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2343.0881] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x26, 0x13]
[ 2343.0881] D/CDROM: CDROM setloc command (24, 26, 13)
[ 2343.0889] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2343.0891] D/CDROM: Seek time for 24:26:04->24:26:13 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2343.1382] D/CDROM: Logical seek to [24:26:13] complete, now reading
[ 2343.1545] D/CDROM: Read sector 109963 [24:26:13]: mode 2 submode 0x08 into buffer 1
[ 2343.1548] D/CDROM: Read sector 109964 [24:26:14]: mode 2 submode 0x08 into buffer 2
[ 2343.1714] D/CDROM: Read sector 109965 [24:26:15]: mode 2 submode 0x08 into buffer 3
[ 2343.1716] D/CDROM: Read sector 109966 [24:26:16]: mode 2 submode 0x08 into buffer 4
[ 2343.1719] D/CDROM: Read sector 109967 [24:26:17]: mode 2 submode 0x08 into buffer 5
[ 2343.1885] D/CDROM: Read sector 109968 [24:26:18]: mode 2 submode 0x08 into buffer 6
[ 2343.1887] D/CDROM: Read sector 109969 [24:26:19]: mode 2 submode 0x08 into buffer 7
[ 2343.2048] D/CDROM: Read sector 109970 [24:26:20]: mode 2 submode 0x08 into buffer 0
[ 2343.2056] D/CDROM: Read sector 109971 [24:26:21]: mode 2 submode 0x08 into buffer 1
[ 2343.2056] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2343.2720] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x26, 0x22]
[ 2343.2720] D/CDROM: CDROM setloc command (24, 26, 22)
[ 2343.2727] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2343.2727] D/CDROM: Seek time for 24:26:13->24:26:22 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2343.3218] D/CDROM: Logical seek to [24:26:22] complete, now reading
[ 2343.3220] D/CDROM: Read sector 109972 [24:26:22]: mode 2 submode 0x08 into buffer 1
[ 2343.3384] D/CDROM: Read sector 109973 [24:26:23]: mode 2 submode 0x08 into buffer 2
[ 2343.3386] D/CDROM: Read sector 109974 [24:26:24]: mode 2 submode 0x08 into buffer 3
[ 2343.3389] D/CDROM: Read sector 109975 [24:26:25]: mode 2 submode 0x08 into buffer 4
[ 2343.3555] D/CDROM: Read sector 109976 [24:26:26]: mode 2 submode 0x08 into buffer 5
[ 2343.3557] D/CDROM: Read sector 109977 [24:26:27]: mode 2 submode 0x08 into buffer 6
[ 2343.3718] D/CDROM: Read sector 109978 [24:26:28]: mode 2 submode 0x08 into buffer 7
[ 2343.3721] D/CDROM: Read sector 109979 [24:26:29]: mode 2 submode 0x08 into buffer 0
[ 2343.3726] D/CDROM: Read sector 109980 [24:26:30]: mode 2 submode 0x08 into buffer 1
[ 2343.3726] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2343.4390] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x26, 0x31]
[ 2343.4392] D/CDROM: CDROM setloc command (24, 26, 31)
[ 2343.4392] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2343.4395] D/CDROM: Seek time for 24:26:22->24:26:31 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2343.4890] D/CDROM: Logical seek to [24:26:31] complete, now reading
[ 2343.5054] D/CDROM: Read sector 109981 [24:26:31]: mode 2 submode 0x08 into buffer 1
[ 2343.5059] D/CDROM: Read sector 109982 [24:26:32]: mode 2 submode 0x08 into buffer 2
[ 2343.5061] D/CDROM: Read sector 109983 [24:26:33]: mode 2 submode 0x08 into buffer 3
[ 2343.5227] D/CDROM: Read sector 109984 [24:26:34]: mode 2 submode 0x08 into buffer 4
[ 2343.5232] D/CDROM: Read sector 109985 [24:26:35]: mode 2 submode 0x08 into buffer 5
[ 2343.5391] D/CDROM: Read sector 109986 [24:26:36]: mode 2 submode 0x08 into buffer 6
[ 2343.5393] D/CDROM: Read sector 109987 [24:26:37]: mode 2 submode 0x08 into buffer 7
[ 2343.5398] D/CDROM: Read sector 109988 [24:26:38]: mode 2 submode 0x08 into buffer 0
[ 2343.5559] D/CDROM: Read sector 109989 [24:26:39]: mode 2 submode 0x08 into buffer 1
[ 2343.5559] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2343.6062] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x26, 0x40]
[ 2343.6062] D/CDROM: CDROM setloc command (24, 26, 40)
[ 2343.6226] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2343.6226] D/CDROM: Seek time for 24:26:31->24:26:40 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2343.6733] D/CDROM: Logical seek to [24:26:40] complete, now reading
[ 2343.6736] D/CDROM: Read sector 109990 [24:26:40]: mode 2 submode 0x08 into buffer 1
[ 2343.6897] D/CDROM: Read sector 109991 [24:26:41]: mode 2 submode 0x08 into buffer 2
[ 2343.6899] D/CDROM: Read sector 109992 [24:26:42]: mode 2 submode 0x08 into buffer 3
[ 2343.6902] D/CDROM: Read sector 109993 [24:26:43]: mode 2 submode 0x08 into buffer 4
[ 2343.7061] D/CDROM: Read sector 109994 [24:26:44]: mode 2 submode 0x08 into buffer 5
[ 2343.7063] D/CDROM: Read sector 109995 [24:26:45]: mode 2 submode 0x08 into buffer 6
[ 2343.7065] D/CDROM: Read sector 109996 [24:26:46]: mode 2 submode 0x08 into buffer 7
[ 2343.7231] D/CDROM: Read sector 109997 [24:26:47]: mode 2 submode 0x08 into buffer 0
[ 2343.7236] D/CDROM: Read sector 109998 [24:26:48]: mode 2 submode 0x08 into buffer 1
[ 2343.7239] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2343.7905] V/PerfMon: FPS: 24.91 VPS: 59.78 CPU: 4.41 GPU: 0.00 Avg: 16.73ms Min: 16.26ms Max: 17.46ms
[ 2343.7908] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x26, 0x49]
[ 2343.7915] D/CDROM: CDROM setloc command (24, 26, 49)
[ 2343.7915] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2343.7915] D/CDROM: Seek time for 24:26:40->24:26:49 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2343.8406] D/CDROM: Logical seek to [24:26:49] complete, now reading
[ 2343.8567] D/CDROM: Read sector 109999 [24:26:49]: mode 2 submode 0x08 into buffer 1
[ 2343.8569] D/CDROM: Read sector 110000 [24:26:50]: mode 2 submode 0x08 into buffer 2
[ 2343.8574] D/CDROM: Read sector 110001 [24:26:51]: mode 2 submode 0x08 into buffer 3
[ 2343.8733] D/CDROM: Read sector 110002 [24:26:52]: mode 2 submode 0x08 into buffer 4
[ 2343.8735] D/CDROM: Read sector 110003 [24:26:53]: mode 2 submode 0x08 into buffer 5
[ 2343.8901] D/CDROM: Read sector 110004 [24:26:54]: mode 2 submode 0x08 into buffer 6
[ 2343.8904] D/CDROM: Read sector 110005 [24:26:55]: mode 2 submode 0x08 into buffer 7
[ 2343.8909] D/CDROM: Read sector 110006 [24:26:56]: mode 2 submode 0x08 into buffer 0
[ 2343.9067] D/CDROM: Read sector 110007 [24:26:57]: mode 2 submode 0x08 into buffer 1
[ 2343.9070] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2343.9575] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x26, 0x58]
[ 2343.9575] D/CDROM: CDROM setloc command (24, 26, 58)
[ 2343.9575] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2343.9575] D/CDROM: Seek time for 24:26:49->24:26:58 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2344.0237] D/CDROM: Logical seek to [24:26:58] complete, now reading
[ 2344.0242] D/CDROM: Read sector 110008 [24:26:58]: mode 2 submode 0x08 into buffer 1
[ 2344.0244] D/CDROM: Read sector 110009 [24:26:59]: mode 2 submode 0x08 into buffer 2
[ 2344.0408] D/CDROM: Read sector 110010 [24:26:60]: mode 2 submode 0x08 into buffer 3
[ 2344.0413] D/CDROM: Read sector 110011 [24:26:61]: mode 2 submode 0x08 into buffer 4
[ 2344.0574] D/CDROM: Read sector 110012 [24:26:62]: mode 2 submode 0x08 into buffer 5
[ 2344.0576] D/CDROM: Read sector 110013 [24:26:63]: mode 2 submode 0x08 into buffer 6
[ 2344.0579] D/CDROM: Read sector 110014 [24:26:64]: mode 2 submode 0x08 into buffer 7
[ 2344.0740] D/CDROM: Read sector 110015 [24:26:65]: mode 2 submode 0x08 into buffer 0
[ 2344.0742] D/CDROM: Read sector 110016 [24:26:66]: mode 2 submode 0x08 into buffer 1
[ 2344.0742] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2344.1411] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x26, 0x67]
[ 2344.1414] D/CDROM: CDROM setloc command (24, 26, 67)
[ 2344.1414] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2344.1416] D/CDROM: Seek time for 24:26:58->24:26:67 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2344.1914] D/CDROM: Logical seek to [24:26:67] complete, now reading
[ 2344.1917] D/CDROM: Read sector 110017 [24:26:67]: mode 2 submode 0x08 into buffer 1
[ 2344.2083] D/CDROM: Read sector 110018 [24:26:68]: mode 2 submode 0x08 into buffer 2
[ 2344.2085] D/CDROM: Read sector 110019 [24:26:69]: mode 2 submode 0x08 into buffer 3
[ 2344.2249] D/CDROM: Read sector 110020 [24:26:70]: mode 2 submode 0x08 into buffer 4
[ 2344.2253] D/CDROM: Read sector 110021 [24:26:71]: mode 2 submode 0x08 into buffer 5
[ 2344.2253] D/CDROM: Read sector 110022 [24:26:72]: mode 2 submode 0x08 into buffer 6
[ 2344.2417] D/CDROM: Read sector 110023 [24:26:73]: mode 2 submode 0x08 into buffer 7
[ 2344.2419] D/CDROM: Read sector 110024 [24:26:74]: mode 2 submode 0x08 into buffer 0
[ 2344.2578] D/CDROM: Read sector 110025 [24:27:00]: mode 2 submode 0x08 into buffer 1
[ 2344.2581] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2344.3083] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x27, 0x01]
[ 2344.3083] D/CDROM: CDROM setloc command (24, 27, 01)
[ 2344.3086] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2344.3088] D/CDROM: Seek time for 24:26:67->24:27:01 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2344.3748] D/CDROM: Logical seek to [24:27:01] complete, now reading
[ 2344.3750] D/CDROM: Read sector 110026 [24:27:01]: mode 2 submode 0x08 into buffer 1
[ 2344.3752] D/CDROM: Read sector 110027 [24:27:02]: mode 2 submode 0x08 into buffer 2
[ 2344.3918] D/CDROM: Read sector 110028 [24:27:03]: mode 2 submode 0x08 into buffer 3
[ 2344.3921] D/CDROM: Read sector 110029 [24:27:04]: mode 2 submode 0x08 into buffer 4
[ 2344.4082] D/CDROM: Read sector 110030 [24:27:05]: mode 2 submode 0x08 into buffer 5
[ 2344.4087] D/CDROM: Read sector 110031 [24:27:06]: mode 2 submode 0x08 into buffer 6
[ 2344.4089] D/CDROM: Read sector 110032 [24:27:07]: mode 2 submode 0x08 into buffer 7
[ 2344.4253] D/CDROM: Read sector 110033 [24:27:08]: mode 2 submode 0x08 into buffer 0
[ 2344.4258] D/CDROM: Read sector 110034 [24:27:09]: mode 2 submode 0x08 into buffer 1
[ 2344.4258] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2344.4922] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x27, 0x10]
[ 2344.4922] D/CDROM: CDROM setloc command (24, 27, 10)
[ 2344.4927] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2344.4927] D/CDROM: Seek time for 24:27:01->24:27:10 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2344.5420] D/CDROM: Logical seek to [24:27:10] complete, now reading
[ 2344.5425] D/CDROM: Read sector 110035 [24:27:10]: mode 2 submode 0x08 into buffer 1
[ 2344.5588] D/CDROM: Read sector 110036 [24:27:11]: mode 2 submode 0x08 into buffer 2
[ 2344.5588] D/CDROM: Read sector 110037 [24:27:12]: mode 2 submode 0x08 into buffer 3
[ 2344.5757] D/CDROM: Read sector 110038 [24:27:13]: mode 2 submode 0x08 into buffer 4
[ 2344.5759] D/CDROM: Read sector 110039 [24:27:14]: mode 2 submode 0x08 into buffer 5
[ 2344.5762] D/CDROM: Read sector 110040 [24:27:15]: mode 2 submode 0x08 into buffer 6
[ 2344.5925] D/CDROM: Read sector 110041 [24:27:16]: mode 2 submode 0x08 into buffer 7
[ 2344.5925] D/CDROM: Read sector 110042 [24:27:17]: mode 2 submode 0x08 into buffer 0
[ 2344.6089] D/CDROM: Read sector 110043 [24:27:18]: mode 2 submode 0x08 into buffer 1
[ 2344.6091] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2344.6594] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x27, 0x19]
[ 2344.6597] D/CDROM: CDROM setloc command (24, 27, 19)
[ 2344.6599] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2344.6599] D/CDROM: Seek time for 24:27:10->24:27:19 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2344.7097] D/CDROM: Logical seek to [24:27:19] complete, now reading
[ 2344.7261] D/CDROM: Read sector 110044 [24:27:19]: mode 2 submode 0x08 into buffer 1
[ 2344.7263] D/CDROM: Read sector 110045 [24:27:20]: mode 2 submode 0x08 into buffer 2
[ 2344.7429] D/CDROM: Read sector 110046 [24:27:21]: mode 2 submode 0x08 into buffer 3
[ 2344.7432] D/CDROM: Read sector 110047 [24:27:22]: mode 2 submode 0x08 into buffer 4
[ 2344.7437] D/CDROM: Read sector 110048 [24:27:23]: mode 2 submode 0x08 into buffer 5
[ 2344.7595] D/CDROM: Read sector 110049 [24:27:24]: mode 2 submode 0x08 into buffer 6
[ 2344.7598] D/CDROM: Read sector 110050 [24:27:25]: mode 2 submode 0x08 into buffer 7
[ 2344.7764] D/CDROM: Read sector 110051 [24:27:26]: mode 2 submode 0x08 into buffer 0
[ 2344.7766] D/CDROM: Read sector 110052 [24:27:27]: mode 2 submode 0x08 into buffer 1
[ 2344.7769] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2344.7930] V/PerfMon: FPS: 0.00 VPS: 59.85 CPU: 4.22 GPU: 0.00 Avg: 16.71ms Min: 16.14ms Max: 17.18ms
[ 2344.8433] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x27, 0x28]
[ 2344.8433] D/CDROM: CDROM setloc command (24, 27, 28)
[ 2344.8435] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2344.8438] D/CDROM: Seek time for 24:27:19->24:27:28 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2344.8933] D/CDROM: Logical seek to [24:27:28] complete, now reading
[ 2344.8936] D/CDROM: Read sector 110053 [24:27:28]: mode 2 submode 0x08 into buffer 1
[ 2344.9102] D/CDROM: Read sector 110054 [24:27:29]: mode 2 submode 0x08 into buffer 2
[ 2344.9104] D/CDROM: Read sector 110055 [24:27:30]: mode 2 submode 0x08 into buffer 3
[ 2344.9268] D/CDROM: Read sector 110056 [24:27:31]: mode 2 submode 0x08 into buffer 4
[ 2344.9272] D/CDROM: Read sector 110057 [24:27:32]: mode 2 submode 0x08 into buffer 5
[ 2344.9275] D/CDROM: Read sector 110058 [24:27:33]: mode 2 submode 0x08 into buffer 6
[ 2344.9434] D/CDROM: Read sector 110059 [24:27:34]: mode 2 submode 0x08 into buffer 7
[ 2344.9436] D/CDROM: Read sector 110060 [24:27:35]: mode 2 submode 0x08 into buffer 0
[ 2344.9597] D/CDROM: Read sector 110061 [24:27:36]: mode 2 submode 0x08 into buffer 1
[ 2344.9600] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2345.0103] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x27, 0x37]
[ 2345.0105] D/CDROM: CDROM setloc command (24, 27, 37)
[ 2345.0107] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2345.0107] D/CDROM: Seek time for 24:27:28->24:27:37 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2345.0605] D/CDROM: Logical seek to [24:27:37] complete, now reading
[ 2345.0771] D/CDROM: Read sector 110062 [24:27:37]: mode 2 submode 0x08 into buffer 1
[ 2345.0771] D/CDROM: Read sector 110063 [24:27:38]: mode 2 submode 0x08 into buffer 2
[ 2345.0940] D/CDROM: Read sector 110064 [24:27:39]: mode 2 submode 0x08 into buffer 3
[ 2345.0942] D/CDROM: Read sector 110065 [24:27:40]: mode 2 submode 0x08 into buffer 4
[ 2345.0945] D/CDROM: Read sector 110066 [24:27:41]: mode 2 submode 0x08 into buffer 5
[ 2345.1106] D/CDROM: Read sector 110067 [24:27:42]: mode 2 submode 0x08 into buffer 6
[ 2345.1106] D/CDROM: Read sector 110068 [24:27:43]: mode 2 submode 0x08 into buffer 7
[ 2345.1274] D/CDROM: Read sector 110069 [24:27:44]: mode 2 submode 0x08 into buffer 0
[ 2345.1274] D/CDROM: Read sector 110070 [24:27:45]: mode 2 submode 0x08 into buffer 1
[ 2345.1277] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2345.1938] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x27, 0x46]
[ 2345.1941] D/CDROM: CDROM setloc command (24, 27, 46)
[ 2345.1941] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2345.1943] D/CDROM: Seek time for 24:27:37->24:27:46 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2345.2441] D/CDROM: Logical seek to [24:27:46] complete, now reading
[ 2345.2444] D/CDROM: Read sector 110071 [24:27:46]: mode 2 submode 0x08 into buffer 1
[ 2345.2612] D/CDROM: Read sector 110072 [24:27:47]: mode 2 submode 0x08 into buffer 2
[ 2345.2612] D/CDROM: Read sector 110073 [24:27:48]: mode 2 submode 0x08 into buffer 3
[ 2345.2615] D/CDROM: Read sector 110074 [24:27:49]: mode 2 submode 0x08 into buffer 4
[ 2345.2781] D/CDROM: Read sector 110075 [24:27:50]: mode 2 submode 0x08 into buffer 5
[ 2345.2783] D/CDROM: Read sector 110076 [24:27:51]: mode 2 submode 0x08 into buffer 6
[ 2345.2944] D/CDROM: Read sector 110077 [24:27:52]: mode 2 submode 0x08 into buffer 7
[ 2345.2947] D/CDROM: Read sector 110078 [24:27:53]: mode 2 submode 0x08 into buffer 0
[ 2345.2947] D/CDROM: Read sector 110079 [24:27:54]: mode 2 submode 0x08 into buffer 1
[ 2345.3113] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2345.3616] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x27, 0x55]
[ 2345.3616] D/CDROM: CDROM setloc command (24, 27, 55)
[ 2345.3618] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2345.3621] D/CDROM: Seek time for 24:27:46->24:27:55 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2345.4116] D/CDROM: Logical seek to [24:27:55] complete, now reading
[ 2345.4282] D/CDROM: Read sector 110080 [24:27:55]: mode 2 submode 0x08 into buffer 1
[ 2345.4285] D/CDROM: Read sector 110081 [24:27:56]: mode 2 submode 0x08 into buffer 2
[ 2345.4448] D/CDROM: Read sector 110082 [24:27:57]: mode 2 submode 0x08 into buffer 3
[ 2345.4448] D/CDROM: Read sector 110083 [24:27:58]: mode 2 submode 0x08 into buffer 4
[ 2345.4451] D/CDROM: Read sector 110084 [24:27:59]: mode 2 submode 0x08 into buffer 5
[ 2345.4617] D/CDROM: Read sector 110085 [24:27:60]: mode 2 submode 0x08 into buffer 6
[ 2345.4619] D/CDROM: Read sector 110086 [24:27:61]: mode 2 submode 0x08 into buffer 7
[ 2345.4785] D/CDROM: Read sector 110087 [24:27:62]: mode 2 submode 0x08 into buffer 0
[ 2345.4788] D/CDROM: Read sector 110088 [24:27:63]: mode 2 submode 0x08 into buffer 1
[ 2345.4788] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2345.5454] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x27, 0x64]
[ 2345.5454] D/CDROM: CDROM setloc command (24, 27, 64)
[ 2345.5454] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2345.5454] D/CDROM: Seek time for 24:27:55->24:27:64 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2345.5955] D/CDROM: Logical seek to [24:27:64] complete, now reading
[ 2345.5957] D/CDROM: Read sector 110089 [24:27:64]: mode 2 submode 0x08 into buffer 1
[ 2345.6118] D/CDROM: Read sector 110090 [24:27:65]: mode 2 submode 0x08 into buffer 2
[ 2345.6121] D/CDROM: Read sector 110091 [24:27:66]: mode 2 submode 0x08 into buffer 3
[ 2345.6123] D/CDROM: Read sector 110092 [24:27:67]: mode 2 submode 0x08 into buffer 4
[ 2345.6287] D/CDROM: Read sector 110093 [24:27:68]: mode 2 submode 0x08 into buffer 5
[ 2345.6289] D/CDROM: Read sector 110094 [24:27:69]: mode 2 submode 0x08 into buffer 6
[ 2345.6453] D/CDROM: Read sector 110095 [24:27:70]: mode 2 submode 0x08 into buffer 7
[ 2345.6455] D/CDROM: Read sector 110096 [24:27:71]: mode 2 submode 0x08 into buffer 0
[ 2345.6458] D/CDROM: Read sector 110097 [24:27:72]: mode 2 submode 0x08 into buffer 1
[ 2345.6458] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2345.7126] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x27, 0x73]
[ 2345.7126] D/CDROM: CDROM setloc command (24, 27, 73)
[ 2345.7134] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2345.7134] D/CDROM: Seek time for 24:27:64->24:27:73 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2345.7629] D/CDROM: Logical seek to [24:27:73] complete, now reading
[ 2345.7793] D/CDROM: Read sector 110098 [24:27:73]: mode 2 submode 0x08 into buffer 1
[ 2345.7793] D/CDROM: Read sector 110099 [24:27:74]: mode 2 submode 0x08 into buffer 2
[ 2345.7795] D/CDROM: Read sector 110100 [24:28:00]: mode 2 submode 0x08 into buffer 3
[ 2345.7959] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 4.14 GPU: 0.00 Avg: 16.72ms Min: 15.96ms Max: 17.39ms
[ 2345.7961] D/CDROM: Read sector 110101 [24:28:01]: mode 2 submode 0x08 into buffer 4
[ 2345.7964] D/CDROM: Read sector 110102 [24:28:02]: mode 2 submode 0x08 into buffer 5
[ 2345.8127] D/CDROM: Read sector 110103 [24:28:03]: mode 2 submode 0x08 into buffer 6
[ 2345.8130] D/CDROM: Read sector 110104 [24:28:04]: mode 2 submode 0x08 into buffer 7
[ 2345.8132] D/CDROM: Read sector 110105 [24:28:05]: mode 2 submode 0x08 into buffer 0
[ 2345.8296] D/CDROM: Read sector 110106 [24:28:06]: mode 2 submode 0x08 into buffer 1
[ 2345.8296] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2345.8962] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x28, 0x07]
[ 2345.8962] D/CDROM: CDROM setloc command (24, 28, 07)
[ 2345.8965] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2345.8967] D/CDROM: Seek time for 24:27:73->24:28:07 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2345.9465] D/CDROM: Logical seek to [24:28:07] complete, now reading
[ 2345.9465] D/CDROM: Read sector 110107 [24:28:07]: mode 2 submode 0x08 into buffer 1
[ 2345.9629] D/CDROM: Read sector 110108 [24:28:08]: mode 2 submode 0x08 into buffer 2
[ 2345.9631] D/CDROM: Read sector 110109 [24:28:09]: mode 2 submode 0x08 into buffer 3
[ 2345.9634] D/CDROM: Read sector 110110 [24:28:10]: mode 2 submode 0x08 into buffer 4
[ 2345.9807] D/CDROM: Read sector 110111 [24:28:11]: mode 2 submode 0x08 into buffer 5
[ 2345.9810] D/CDROM: Read sector 110112 [24:28:12]: mode 2 submode 0x08 into buffer 6
[ 2345.9963] D/CDROM: Read sector 110113 [24:28:13]: mode 2 submode 0x08 into buffer 7
[ 2345.9966] D/CDROM: Read sector 110114 [24:28:14]: mode 2 submode 0x08 into buffer 0
[ 2345.9966] D/CDROM: Read sector 110115 [24:28:15]: mode 2 submode 0x08 into buffer 1
[ 2345.9966] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2346.0635] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x28, 0x16]
[ 2346.0635] D/CDROM: CDROM setloc command (24, 28, 16)
[ 2346.0635] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2346.0640] D/CDROM: Seek time for 24:28:07->24:28:16 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2346.1135] D/CDROM: Logical seek to [24:28:16] complete, now reading
[ 2346.1304] D/CDROM: Read sector 110116 [24:28:16]: mode 2 submode 0x08 into buffer 1
[ 2346.1306] D/CDROM: Read sector 110117 [24:28:17]: mode 2 submode 0x08 into buffer 2
[ 2346.1306] D/CDROM: Read sector 110118 [24:28:18]: mode 2 submode 0x08 into buffer 3
[ 2346.1472] D/CDROM: Read sector 110119 [24:28:19]: mode 2 submode 0x08 into buffer 4
[ 2346.1475] D/CDROM: Read sector 110120 [24:28:20]: mode 2 submode 0x08 into buffer 5
[ 2346.1636] D/CDROM: Read sector 110121 [24:28:21]: mode 2 submode 0x89 into buffer 6
[ 2346.1636] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2346.2141] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x25, 0x68]
[ 2346.2141] D/CDROM: CDROM setloc command (24, 25, 68)
[ 2346.2144] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2346.2146] D/CDROM: Seek time for 24:28:13->24:25:68 (170 LBA): 3386880 (100.000 ms) (NT backward)
[ 2346.3145] D/CDROM: Logical seek to [24:25:68] complete, now reading
[ 2346.3311] D/CDROM: Read sector 109943 [24:25:68]: mode 2 submode 0x08 into buffer 1
[ 2346.3313] D/CDROM: Read sector 109944 [24:25:69]: mode 2 submode 0x08 into buffer 2
[ 2346.3315] D/CDROM: Read sector 109945 [24:25:70]: mode 2 submode 0x08 into buffer 3
[ 2346.3474] D/CDROM: Read sector 109946 [24:25:71]: mode 2 submode 0x08 into buffer 4
[ 2346.3477] D/CDROM: Read sector 109947 [24:25:72]: mode 2 submode 0x08 into buffer 5
[ 2346.3643] D/CDROM: Read sector 109948 [24:25:73]: mode 2 submode 0x08 into buffer 6
[ 2346.3645] D/CDROM: Read sector 109949 [24:25:74]: mode 2 submode 0x08 into buffer 7
[ 2346.3650] D/CDROM: Read sector 109950 [24:26:00]: mode 2 submode 0x08 into buffer 0
[ 2346.3811] D/CDROM: Read sector 109951 [24:26:01]: mode 2 submode 0x08 into buffer 1
[ 2346.3811] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2346.4478] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x26, 0x02]
[ 2346.4478] D/CDROM: CDROM setloc command (24, 26, 02)
[ 2346.4480] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2346.4482] D/CDROM: Seek time for 24:25:68->24:26:02 (9 LBA): 1806336 (53.333 ms) (forward)
[ 2346.4983] D/CDROM: Logical seek to [24:26:02] complete, now reading
[ 2346.4983] D/CDROM: Read sector 109952 [24:26:02]: mode 2 submode 0x08 into buffer 1
[ 2346.5146] D/CDROM: Read sector 109953 [24:26:03]: mode 2 submode 0x89 into buffer 2
[ 2346.5149] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2346.5652] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x28, 0x22]
[ 2346.5652] D/CDROM: CDROM setloc command (24, 28, 22)
[ 2346.5657] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2346.5657] D/CDROM: Seek time for 24:25:70->24:28:22 (177 LBA): 3386880 (100.000 ms) (NT forward)
[ 2346.6655] D/CDROM: Logical seek to [24:28:22] complete, now reading
[ 2346.6821] D/CDROM: Read sector 110122 [24:28:22]: mode 2 submode 0x08 into buffer 1
[ 2346.6824] D/CDROM: Read sector 110123 [24:28:23]: mode 2 submode 0x08 into buffer 2
[ 2346.6826] D/CDROM: Read sector 110124 [24:28:24]: mode 2 submode 0x08 into buffer 3
[ 2346.6990] D/CDROM: Read sector 110125 [24:28:25]: mode 2 submode 0x08 into buffer 4
[ 2346.6990] D/CDROM: Read sector 110126 [24:28:26]: mode 2 submode 0x08 into buffer 5
[ 2346.7153] D/CDROM: Read sector 110127 [24:28:27]: mode 2 submode 0x08 into buffer 6
[ 2346.7156] D/CDROM: Read sector 110128 [24:28:28]: mode 2 submode 0x08 into buffer 7
[ 2346.7158] D/CDROM: Read sector 110129 [24:28:29]: mode 2 submode 0x08 into buffer 0
[ 2346.7322] D/CDROM: Read sector 110130 [24:28:30]: mode 2 submode 0x89 into buffer 1
[ 2346.7324] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2346.7825] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x16]
[ 2346.7825] D/CDROM: CDROM setloc command (28, 13, 16)
[ 2346.7988] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 3.99 GPU: 0.00 Avg: 16.72ms Min: 15.78ms Max: 17.54ms
[ 2346.7991] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2346.7991] D/CDROM: Seek time for 24:28:22->28:13:16 (16869 LBA): 11426114 (337.364 ms) (2N/sled forward)
[ 2347.1331] D/CDROM: Logical seek to [28:13:16] complete, now reading
[ 2347.1333] D/CDROM: Read sector 126991 [28:13:16]: mode 2 submode 0x08 into buffer 1
[ 2347.1335] D/CDROM: Read sector 126992 [28:13:17]: mode 2 submode 0x08 into buffer 2
[ 2347.1506] D/CDROM: Read sector 126993 [28:13:18]: mode 2 submode 0x08 into buffer 3
[ 2347.1509] D/CDROM: Read sector 126994 [28:13:19]: mode 2 submode 0x89 into buffer 4
[ 2347.1511] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2347.2170] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x28]
[ 2347.2173] D/CDROM: CDROM setloc command (28, 13, 28)
[ 2347.2175] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2347.2178] D/CDROM: Seek time for 28:13:11->28:13:28 (17 LBA): 1693440 (50.000 ms) (NT forward)
[ 2347.2671] D/CDROM: Logical seek to [28:13:28] complete, now reading
[ 2347.2673] D/CDROM: Read sector 127003 [28:13:28]: mode 2 submode 0x08 into buffer 1
[ 2347.2837] D/CDROM: Read sector 127004 [28:13:29]: mode 2 submode 0x08 into buffer 2
[ 2347.2839] D/CDROM: Read sector 127005 [28:13:30]: mode 2 submode 0x08 into buffer 3
[ 2347.3008] D/CDROM: Read sector 127006 [28:13:31]: mode 2 submode 0x08 into buffer 4
[ 2347.3010] D/CDROM: Read sector 127007 [28:13:32]: mode 2 submode 0x89 into buffer 5
[ 2347.3013] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2347.3672] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x38]
[ 2347.3672] D/CDROM: CDROM setloc command (28, 13, 38)
[ 2347.3677] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2347.3677] D/CDROM: Seek time for 28:13:24->28:13:38 (14 LBA): 1693440 (50.000 ms) (NT forward)
[ 2347.4172] D/CDROM: Logical seek to [28:13:38] complete, now reading
[ 2347.4175] D/CDROM: Read sector 127013 [28:13:38]: mode 2 submode 0x08 into buffer 1
[ 2347.4177] D/CDROM: Read sector 127014 [28:13:39]: mode 2 submode 0x08 into buffer 2
[ 2347.4346] D/CDROM: Read sector 127015 [28:13:40]: mode 2 submode 0x08 into buffer 3
[ 2347.4348] D/CDROM: Read sector 127016 [28:13:41]: mode 2 submode 0x89 into buffer 4
[ 2347.4348] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2347.5012] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x54]
[ 2347.5012] D/CDROM: CDROM setloc command (28, 13, 54)
[ 2347.5015] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2347.5017] D/CDROM: Seek time for 28:13:33->28:13:54 (21 LBA): 1693440 (50.000 ms) (NT forward)
[ 2347.5513] D/CDROM: Logical seek to [28:13:54] complete, now reading
[ 2347.5513] D/CDROM: Read sector 127029 [28:13:54]: mode 2 submode 0x08 into buffer 1
[ 2347.5676] D/CDROM: Read sector 127030 [28:13:55]: mode 2 submode 0x08 into buffer 2
[ 2347.5679] D/CDROM: Read sector 127031 [28:13:56]: mode 2 submode 0x08 into buffer 3
[ 2347.5681] D/CDROM: Read sector 127032 [28:13:57]: mode 2 submode 0x08 into buffer 4
[ 2347.5852] D/CDROM: Read sector 127033 [28:13:58]: mode 2 submode 0x08 into buffer 5
[ 2347.5852] D/CDROM: Read sector 127034 [28:13:59]: mode 2 submode 0x08 into buffer 6
[ 2347.6013] D/CDROM: Read sector 127035 [28:13:60]: mode 2 submode 0x89 into buffer 7
[ 2347.6016] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2347.7185] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x24, 0x33, 0x60]
[ 2347.7188] D/CDROM: CDROM setloc command (24, 33, 60)
[ 2347.7852] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[ 2347.7852] D/CDROM: Seek time for 28:13:53->24:33:60 (16493 LBA): 11385610 (336.168 ms) (2N/sled backward)
[ 2347.8022] V/PerfMon: FPS: 2.99 VPS: 59.80 CPU: 3.98 GPU: 0.00 Avg: 16.72ms Min: 16.15ms Max: 17.64ms
[ 2348.1199] D/CDROM: Logical seek to [24:33:60] complete, now reading
[ 2348.1201] D/CDROM: Read sector 110535 [24:33:60]: mode 2 submode 0x08 into buffer 1
[ 2348.1362] D/CDROM: Read sector 110536 [24:33:61]: mode 2 submode 0x08 into buffer 2
[ 2348.1365] D/CDROM: Read sector 110537 [24:33:62]: mode 2 submode 0x08 into buffer 3
[ 2348.1367] D/CDROM: Read sector 110538 [24:33:63]: mode 2 submode 0x08 into buffer 4
[ 2348.1531] D/CDROM: Read sector 110539 [24:33:64]: mode 2 submode 0x08 into buffer 5
[ 2348.1533] D/CDROM: Read sector 110540 [24:33:65]: mode 2 submode 0x08 into buffer 6
[ 2348.1697] D/CDROM: Read sector 110541 [24:33:66]: mode 2 submode 0x08 into buffer 7
[ 2348.1699] D/CDROM: Read sector 110542 [24:33:67]: mode 2 submode 0x08 into buffer 0
[ 2348.1702] D/CDROM: Read sector 110543 [24:33:68]: mode 2 submode 0x08 into buffer 1
[ 2348.1865] D/CDROM: Read sector 110544 [24:33:69]: mode 2 submode 0x08 into buffer 2
[ 2348.1868] D/CDROM: Read sector 110545 [24:33:70]: mode 2 submode 0x08 into buffer 3
[ 2348.2031] D/CDROM: Read sector 110546 [24:33:71]: mode 2 submode 0x08 into buffer 4
[ 2348.2034] D/CDROM: Read sector 110547 [24:33:72]: mode 2 submode 0x08 into buffer 5
[ 2348.2039] D/CDROM: Read sector 110548 [24:33:73]: mode 2 submode 0x08 into buffer 6
[ 2348.2200] D/CDROM: Read sector 110549 [24:33:74]: mode 2 submode 0x08 into buffer 7
[ 2348.2202] D/CDROM: Read sector 110550 [24:34:00]: mode 2 submode 0x08 into buffer 0
[ 2348.2363] D/CDROM: Read sector 110551 [24:34:01]: mode 2 submode 0x08 into buffer 1
[ 2348.2366] D/CDROM: Read sector 110552 [24:34:02]: mode 2 submode 0x08 into buffer 2
[ 2348.2368] D/CDROM: Read sector 110553 [24:34:03]: mode 2 submode 0x08 into buffer 3
[ 2348.2537] D/CDROM: Read sector 110554 [24:34:04]: mode 2 submode 0x08 into buffer 4
[ 2348.2539] D/CDROM: Read sector 110555 [24:34:05]: mode 2 submode 0x08 into buffer 5
[ 2348.2703] D/CDROM: Read sector 110556 [24:34:06]: mode 2 submode 0x08 into buffer 6
[ 2348.2705] D/CDROM: Read sector 110557 [24:34:07]: mode 2 submode 0x08 into buffer 7
[ 2348.2710] D/CDROM: Read sector 110558 [24:34:08]: mode 2 submode 0x08 into buffer 0
[ 2348.2866] D/CDROM: Read sector 110559 [24:34:09]: mode 2 submode 0x08 into buffer 1
[ 2348.2871] D/CDROM: Read sector 110560 [24:34:10]: mode 2 submode 0x08 into buffer 2
[ 2348.2871] D/CDROM: Read sector 110561 [24:34:11]: mode 2 submode 0x08 into buffer 3
[ 2348.3040] D/CDROM: Read sector 110562 [24:34:12]: mode 2 submode 0x08 into buffer 4
[ 2348.3044] D/CDROM: Read sector 110563 [24:34:13]: mode 2 submode 0x08 into buffer 5
[ 2348.3201] D/CDROM: Read sector 110564 [24:34:14]: mode 2 submode 0x08 into buffer 6
[ 2348.3206] D/CDROM: Read sector 110565 [24:34:15]: mode 2 submode 0x08 into buffer 7
[ 2348.3206] D/CDROM: Read sector 110566 [24:34:16]: mode 2 submode 0x08 into buffer 0
[ 2348.3369] D/CDROM: Read sector 110567 [24:34:17]: mode 2 submode 0x08 into buffer 1
[ 2348.3372] D/CDROM: Read sector 110568 [24:34:18]: mode 2 submode 0x08 into buffer 2
[ 2348.3535] D/CDROM: Read sector 110569 [24:34:19]: mode 2 submode 0x08 into buffer 3
[ 2348.3538] D/CDROM: Read sector 110570 [24:34:20]: mode 2 submode 0x08 into buffer 4
[ 2348.3540] D/CDROM: Read sector 110571 [24:34:21]: mode 2 submode 0x08 into buffer 5
[ 2348.3708] D/CDROM: Read sector 110572 [24:34:22]: mode 2 submode 0x08 into buffer 6
[ 2348.3708] D/CDROM: Read sector 110573 [24:34:23]: mode 2 submode 0x08 into buffer 7
[ 2348.3875] D/CDROM: Read sector 110574 [24:34:24]: mode 2 submode 0x08 into buffer 0
[ 2348.3877] D/CDROM: Read sector 110575 [24:34:25]: mode 2 submode 0x08 into buffer 1
[ 2348.3877] D/CDROM: Read sector 110576 [24:34:26]: mode 2 submode 0x08 into buffer 2
[ 2348.4036] D/CDROM: Read sector 110577 [24:34:27]: mode 2 submode 0x08 into buffer 3
[ 2348.4038] D/CDROM: Read sector 110578 [24:34:28]: mode 2 submode 0x08 into buffer 4
[ 2348.4207] D/CDROM: Read sector 110579 [24:34:29]: mode 2 submode 0x08 into buffer 5
[ 2348.4211] D/CDROM: Read sector 110580 [24:34:30]: mode 2 submode 0x08 into buffer 6
[ 2348.4211] D/CDROM: Read sector 110581 [24:34:31]: mode 2 submode 0x08 into buffer 7
[ 2348.4375] D/CDROM: Read sector 110582 [24:34:32]: mode 2 submode 0x08 into buffer 0
[ 2348.4375] D/CDROM: Read sector 110583 [24:34:33]: mode 2 submode 0x08 into buffer 1
[ 2348.4543] D/CDROM: Read sector 110584 [24:34:34]: mode 2 submode 0x08 into buffer 2
[ 2348.4548] D/CDROM: Read sector 110585 [24:34:35]: mode 2 submode 0x08 into buffer 3
[ 2348.4548] D/CDROM: Read sector 110586 [24:34:36]: mode 2 submode 0x08 into buffer 4
[ 2348.4707] D/CDROM: Read sector 110587 [24:34:37]: mode 2 submode 0x08 into buffer 5
[ 2348.4709] D/CDROM: Read sector 110588 [24:34:38]: mode 2 submode 0x08 into buffer 6
[ 2348.4873] D/CDROM: Read sector 110589 [24:34:39]: mode 2 submode 0x08 into buffer 7
[ 2348.4878] D/CDROM: Read sector 110590 [24:34:40]: mode 2 submode 0x08 into buffer 0
[ 2348.4878] D/CDROM: Read sector 110591 [24:34:41]: mode 2 submode 0x08 into buffer 1
[ 2348.5042] D/CDROM: Read sector 110592 [24:34:42]: mode 2 submode 0x08 into buffer 2
[ 2348.5044] D/CDROM: Read sector 110593 [24:34:43]: mode 2 submode 0x08 into buffer 3
[ 2348.5210] D/CDROM: Read sector 110594 [24:34:44]: mode 2 submode 0x08 into buffer 4
[ 2348.5212] D/CDROM: Read sector 110595 [24:34:45]: mode 2 submode 0x08 into buffer 5
[ 2348.5215] D/CDROM: Read sector 110596 [24:34:46]: mode 2 submode 0x08 into buffer 6
[ 2348.5376] D/CDROM: Read sector 110597 [24:34:47]: mode 2 submode 0x08 into buffer 7
[ 2348.5378] D/CDROM: Read sector 110598 [24:34:48]: mode 2 submode 0x08 into buffer 0
[ 2348.5544] D/CDROM: Read sector 110599 [24:34:49]: mode 2 submode 0x08 into buffer 1
[ 2348.5547] D/CDROM: Read sector 110600 [24:34:50]: mode 2 submode 0x08 into buffer 2
[ 2348.5549] D/CDROM: Read sector 110601 [24:34:51]: mode 2 submode 0x08 into buffer 3
[ 2348.5710] D/CDROM: Read sector 110602 [24:34:52]: mode 2 submode 0x08 into buffer 4
[ 2348.5713] D/CDROM: Read sector 110603 [24:34:53]: mode 2 submode 0x08 into buffer 5
[ 2348.5879] D/CDROM: Read sector 110604 [24:34:54]: mode 2 submode 0x08 into buffer 6
[ 2348.5881] D/CDROM: Read sector 110605 [24:34:55]: mode 2 submode 0x08 into buffer 7
[ 2348.5886] D/CDROM: Read sector 110606 [24:34:56]: mode 2 submode 0x08 into buffer 0
[ 2348.6047] D/CDROM: Read sector 110607 [24:34:57]: mode 2 submode 0x08 into buffer 1
[ 2348.6050] D/CDROM: Read sector 110608 [24:34:58]: mode 2 submode 0x08 into buffer 2
[ 2348.6213] D/CDROM: Read sector 110609 [24:34:59]: mode 2 submode 0x08 into buffer 3
[ 2348.6218] D/CDROM: Read sector 110610 [24:34:60]: mode 2 submode 0x08 into buffer 4
[ 2348.6221] D/CDROM: Read sector 110611 [24:34:61]: mode 2 submode 0x08 into buffer 5
[ 2348.6377] D/CDROM: Read sector 110612 [24:34:62]: mode 2 submode 0x08 into buffer 6
[ 2348.6379] D/CDROM: Read sector 110613 [24:34:63]: mode 2 submode 0x08 into buffer 7
[ 2348.6548] D/CDROM: Read sector 110614 [24:34:64]: mode 2 submode 0x08 into buffer 0
[ 2348.6550] D/CDROM: Read sector 110615 [24:34:65]: mode 2 submode 0x08 into buffer 1
[ 2348.6550] D/CDROM: Read sector 110616 [24:34:66]: mode 2 submode 0x08 into buffer 2
[ 2348.6714] D/CDROM: Read sector 110617 [24:34:67]: mode 2 submode 0x08 into buffer 3
[ 2348.6716] D/CDROM: Read sector 110618 [24:34:68]: mode 2 submode 0x89 into buffer 4
[ 2348.6719] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 2348.8049] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.94 GPU: 0.00 Avg: 16.71ms Min: 16.05ms Max: 17.48ms
