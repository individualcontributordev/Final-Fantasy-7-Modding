# Task: Retest Cosmo / Bugenhagen on single-disc-on-csr v0.1.3

## What was wrong

Field **642 = WHITE1** (Cosmo). WATERFALL = loslake*.  

v0.1.2 left **hybrid** scripts (`WHITE2`, `LOSLAKE3`, …) that were not pure CSR D1 or D2 → glitches in that area even when early Midgar was fine.

## Fix shipped

**single-disc-on-csr-v0.1.3** — Cosmo corridor maps restored from pure CSR Disc 2.  
Hard-refresh builder. 0.1.2 is disabled.

Also keep apply order: Single-disc before CSR+ (previous fix).

## What you do

1. Hard-refresh builder  
2. Rebuild Disc 1: CSR + Single-disc (+ CSR+ if you want same stack)  
3. Confirm APPLIED.txt shows **single-disc-on-csr-v0.1.3** (not 0.1.2)  
4. Fresh DuckStation; go to Cosmo / Bugenhagen waterfall + field 642 (WHITE1)

## Evidence

```
APPLIED single-disc id:
Cosmo waterfall: OK / GLITCH / FREEZE
Field 642 WHITE1: OK / GLITCH / FREEZE
CSR+ on?: YES/NO
notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
git add docs/INSTRUCTIONS.md
git commit -m "ops: retest Cosmo after single-disc 0.1.3"
git push
```

Then say **check**.

duckstation logs

[  161.9227] D/CDROM: Read sector 59929 [13:19:04]: mode 2 submode 0x08 into buffer 6
[  161.9390] D/CDROM: Read sector 59930 [13:19:05]: mode 2 submode 0x08 into buffer 7
[  161.9396] D/CDROM: Read sector 59931 [13:19:06]: mode 2 submode 0x08 into buffer 0
[  161.9400] D/CDROM: Read sector 59932 [13:19:07]: mode 2 submode 0x08 into buffer 1
[  161.9555] D/CDROM: Read sector 59933 [13:19:08]: mode 2 submode 0x08 into buffer 2
[  161.9557] D/CDROM: Read sector 59934 [13:19:09]: mode 2 submode 0x08 into buffer 3
[  161.9720] D/CDROM: Read sector 59935 [13:19:10]: mode 2 submode 0x08 into buffer 4
[  161.9725] D/CDROM: Read sector 59936 [13:19:11]: mode 2 submode 0x08 into buffer 5
[  161.9727] D/CDROM: Read sector 59937 [13:19:12]: mode 2 submode 0x08 into buffer 6
[  161.9891] V/PerfMon: FPS: 29.89 VPS: 59.79 CPU: 4.16 GPU: 0.00 Avg: 16.73ms Min: 15.97ms Max: 17.34ms
[  161.9893] D/CDROM: Read sector 59938 [13:19:13]: mode 2 submode 0x08 into buffer 7
[  161.9895] D/CDROM: Read sector 59939 [13:19:14]: mode 2 submode 0x08 into buffer 0
[  162.0055] D/CDROM: Read sector 59940 [13:19:15]: mode 2 submode 0x08 into buffer 1
[  162.0061] D/CDROM: Read sector 59941 [13:19:16]: mode 2 submode 0x08 into buffer 2
[  162.0063] D/CDROM: Read sector 59942 [13:19:17]: mode 2 submode 0x08 into buffer 3
[  162.0230] D/CDROM: Read sector 59943 [13:19:18]: mode 2 submode 0x08 into buffer 4
[  162.0233] D/CDROM: Read sector 59944 [13:19:19]: mode 2 submode 0x08 into buffer 5
[  162.0390] D/CDROM: Read sector 59945 [13:19:20]: mode 2 submode 0x08 into buffer 6
[  162.0395] D/CDROM: Read sector 59946 [13:19:21]: mode 2 submode 0x08 into buffer 7
[  162.0397] D/CDROM: Read sector 59947 [13:19:22]: mode 2 submode 0x08 into buffer 0
[  162.0558] D/CDROM: Read sector 59948 [13:19:23]: mode 2 submode 0x08 into buffer 1
[  162.0560] D/CDROM: Read sector 59949 [13:19:24]: mode 2 submode 0x08 into buffer 2
[  162.0729] D/CDROM: Read sector 59950 [13:19:25]: mode 2 submode 0x08 into buffer 3
[  162.0733] D/CDROM: Read sector 59951 [13:19:26]: mode 2 submode 0x08 into buffer 4
[  162.0738] D/CDROM: Read sector 59952 [13:19:27]: mode 2 submode 0x08 into buffer 5
[  162.0893] D/CDROM: Read sector 59953 [13:19:28]: mode 2 submode 0x08 into buffer 6
[  162.0895] D/CDROM: Read sector 59954 [13:19:29]: mode 2 submode 0x08 into buffer 7
[  162.1060] D/CDROM: Read sector 59955 [13:19:30]: mode 2 submode 0x08 into buffer 0
[  162.1064] D/CDROM: Read sector 59956 [13:19:31]: mode 2 submode 0x08 into buffer 1
[  162.1070] D/CDROM: Read sector 59957 [13:19:32]: mode 2 submode 0x08 into buffer 2
[  162.1228] D/CDROM: Read sector 59958 [13:19:33]: mode 2 submode 0x08 into buffer 3
[  162.1232] D/CDROM: Read sector 59959 [13:19:34]: mode 2 submode 0x08 into buffer 4
[  162.1395] D/CDROM: Read sector 59960 [13:19:35]: mode 2 submode 0x08 into buffer 5
[  162.1400] D/CDROM: Read sector 59961 [13:19:36]: mode 2 submode 0x08 into buffer 6
[  162.1405] D/CDROM: Read sector 59962 [13:19:37]: mode 2 submode 0x08 into buffer 7
[  162.1560] D/CDROM: Read sector 59963 [13:19:38]: mode 2 submode 0x08 into buffer 0
[  162.1562] D/CDROM: Read sector 59964 [13:19:39]: mode 2 submode 0x08 into buffer 1
[  162.1726] D/CDROM: Read sector 59965 [13:19:40]: mode 2 submode 0x08 into buffer 2
[  162.1730] D/CDROM: Read sector 59966 [13:19:41]: mode 2 submode 0x08 into buffer 3
[  162.1734] D/CDROM: Read sector 59967 [13:19:42]: mode 2 submode 0x08 into buffer 4
[  162.1895] D/CDROM: Read sector 59968 [13:19:43]: mode 2 submode 0x08 into buffer 5
[  162.1897] D/CDROM: Read sector 59969 [13:19:44]: mode 2 submode 0x08 into buffer 6
[  162.2062] D/CDROM: Read sector 59970 [13:19:45]: mode 2 submode 0x08 into buffer 7
[  162.2066] D/CDROM: Read sector 59971 [13:19:46]: mode 2 submode 0x08 into buffer 0
[  162.2072] D/CDROM: Read sector 59972 [13:19:47]: mode 2 submode 0x08 into buffer 1
[  162.2228] D/CDROM: Read sector 59973 [13:19:48]: mode 2 submode 0x08 into buffer 2
[  162.2232] D/CDROM: Read sector 59974 [13:19:49]: mode 2 submode 0x08 into buffer 3
[  162.2396] D/CDROM: Read sector 59975 [13:19:50]: mode 2 submode 0x08 into buffer 4
[  162.2401] D/CDROM: Read sector 59976 [13:19:51]: mode 2 submode 0x08 into buffer 5
[  162.2403] D/CDROM: Read sector 59977 [13:19:52]: mode 2 submode 0x08 into buffer 6
[  162.2563] D/CDROM: Read sector 59978 [13:19:53]: mode 2 submode 0x08 into buffer 7
[  162.2565] D/CDROM: Read sector 59979 [13:19:54]: mode 2 submode 0x08 into buffer 0
[  162.2728] D/CDROM: Read sector 59980 [13:19:55]: mode 2 submode 0x08 into buffer 1
[  162.2733] D/CDROM: Read sector 59981 [13:19:56]: mode 2 submode 0x08 into buffer 2
[  162.2736] D/CDROM: Read sector 59982 [13:19:57]: mode 2 submode 0x08 into buffer 3
[  162.2898] D/CDROM: Read sector 59983 [13:19:58]: mode 2 submode 0x08 into buffer 4
[  162.2900] D/CDROM: Read sector 59984 [13:19:59]: mode 2 submode 0x08 into buffer 5
[  162.3065] D/CDROM: Read sector 59985 [13:19:60]: mode 2 submode 0x08 into buffer 6
[  162.3071] D/CDROM: Read sector 59986 [13:19:61]: mode 2 submode 0x08 into buffer 7
[  162.3073] D/CDROM: Read sector 59987 [13:19:62]: mode 2 submode 0x08 into buffer 0
[  162.3233] D/CDROM: Read sector 59988 [13:19:63]: mode 2 submode 0x08 into buffer 1
[  162.3236] D/CDROM: Read sector 59989 [13:19:64]: mode 2 submode 0x08 into buffer 2
[  162.3402] D/CDROM: Read sector 59990 [13:19:65]: mode 2 submode 0x08 into buffer 3
[  162.3406] D/CDROM: Read sector 59991 [13:19:66]: mode 2 submode 0x08 into buffer 4
[  162.3409] D/CDROM: Read sector 59992 [13:19:67]: mode 2 submode 0x08 into buffer 5
[  162.3568] D/CDROM: Read sector 59993 [13:19:68]: mode 2 submode 0x08 into buffer 6
[  162.3569] D/CDROM: Read sector 59994 [13:19:69]: mode 2 submode 0x08 into buffer 7
[  162.3736] D/CDROM: Read sector 59995 [13:19:70]: mode 2 submode 0x08 into buffer 0
[  162.3740] D/CDROM: Read sector 59996 [13:19:71]: mode 2 submode 0x08 into buffer 1
[  162.3743] D/CDROM: Read sector 59997 [13:19:72]: mode 2 submode 0x08 into buffer 2
[  162.3899] D/CDROM: Read sector 59998 [13:19:73]: mode 2 submode 0x08 into buffer 3
[  162.3900] D/CDROM: Read sector 59999 [13:19:74]: mode 2 submode 0x08 into buffer 4
[  162.4069] D/CDROM: Read sector 60000 [13:20:00]: mode 2 submode 0x08 into buffer 5
[  162.4072] D/CDROM: Read sector 60001 [13:20:01]: mode 2 submode 0x08 into buffer 6
[  162.4078] D/CDROM: Read sector 60002 [13:20:02]: mode 2 submode 0x08 into buffer 7
[  162.4235] D/CDROM: Read sector 60003 [13:20:03]: mode 2 submode 0x08 into buffer 0
[  162.4236] D/CDROM: Read sector 60004 [13:20:04]: mode 2 submode 0x08 into buffer 1
[  162.4241] D/CDROM: Read sector 60005 [13:20:05]: mode 2 submode 0x08 into buffer 2
[  162.4406] D/CDROM: Read sector 60006 [13:20:06]: mode 2 submode 0x08 into buffer 3
[  162.4411] D/CDROM: Read sector 60007 [13:20:07]: mode 2 submode 0x08 into buffer 4
[  162.4569] D/CDROM: Read sector 60008 [13:20:08]: mode 2 submode 0x08 into buffer 5
[  162.4570] D/CDROM: Read sector 60009 [13:20:09]: mode 2 submode 0x08 into buffer 6
[  162.4573] D/CDROM: Read sector 60010 [13:20:10]: mode 2 submode 0x08 into buffer 7
[  162.4740] D/CDROM: Read sector 60011 [13:20:11]: mode 2 submode 0x08 into buffer 0
[  162.4743] D/CDROM: Read sector 60012 [13:20:12]: mode 2 submode 0x08 into buffer 1
[  162.4903] D/CDROM: Read sector 60013 [13:20:13]: mode 2 submode 0x08 into buffer 2
[  162.4905] D/CDROM: Read sector 60014 [13:20:14]: mode 2 submode 0x08 into buffer 3
[  162.4907] D/CDROM: Read sector 60015 [13:20:15]: mode 2 submode 0x08 into buffer 4
[  162.5074] D/CDROM: Read sector 60016 [13:20:16]: mode 2 submode 0x08 into buffer 5
[  162.5077] D/CDROM: Read sector 60017 [13:20:17]: mode 2 submode 0x08 into buffer 6
[  162.5237] D/CDROM: Read sector 60018 [13:20:18]: mode 2 submode 0x08 into buffer 7
[  162.5240] D/CDROM: Read sector 60019 [13:20:19]: mode 2 submode 0x08 into buffer 0
[  162.5241] D/CDROM: Read sector 60020 [13:20:20]: mode 2 submode 0x08 into buffer 1
[  162.5409] D/CDROM: Read sector 60021 [13:20:21]: mode 2 submode 0x08 into buffer 2
[  162.5414] D/CDROM: Read sector 60022 [13:20:22]: mode 2 submode 0x08 into buffer 3
[  162.5571] D/CDROM: Read sector 60023 [13:20:23]: mode 2 submode 0x08 into buffer 4
[  162.5573] D/CDROM: Read sector 60024 [13:20:24]: mode 2 submode 0x08 into buffer 5
[  162.5574] D/CDROM: Read sector 60025 [13:20:25]: mode 2 submode 0x08 into buffer 6
[  162.5740] D/CDROM: Read sector 60026 [13:20:26]: mode 2 submode 0x08 into buffer 7
[  162.5743] D/CDROM: Read sector 60027 [13:20:27]: mode 2 submode 0x08 into buffer 0
[  162.5910] D/CDROM: Read sector 60028 [13:20:28]: mode 2 submode 0x08 into buffer 1
[  162.5912] D/CDROM: Read sector 60029 [13:20:29]: mode 2 submode 0x08 into buffer 2
[  162.5913] D/CDROM: Read sector 60030 [13:20:30]: mode 2 submode 0x08 into buffer 3
[  162.6078] D/CDROM: Read sector 60031 [13:20:31]: mode 2 submode 0x08 into buffer 4
[  162.6084] D/CDROM: Read sector 60032 [13:20:32]: mode 2 submode 0x08 into buffer 5
[  162.6244] D/CDROM: Read sector 60033 [13:20:33]: mode 2 submode 0x08 into buffer 6
[  162.6250] D/CDROM: Read sector 60034 [13:20:34]: mode 2 submode 0x08 into buffer 7
[  162.6251] D/CDROM: Read sector 60035 [13:20:35]: mode 2 submode 0x08 into buffer 0
[  162.6410] D/CDROM: Read sector 60036 [13:20:36]: mode 2 submode 0x08 into buffer 1
[  162.6415] D/CDROM: Read sector 60037 [13:20:37]: mode 2 submode 0x08 into buffer 2
[  162.6575] D/CDROM: Read sector 60038 [13:20:38]: mode 2 submode 0x08 into buffer 3
[  162.6577] D/CDROM: Read sector 60039 [13:20:39]: mode 2 submode 0x08 into buffer 4
[  162.6578] D/CDROM: Read sector 60040 [13:20:40]: mode 2 submode 0x08 into buffer 5
[  162.6748] D/CDROM: Read sector 60041 [13:20:41]: mode 2 submode 0x08 into buffer 6
[  162.6750] D/CDROM: Read sector 60042 [13:20:42]: mode 2 submode 0x08 into buffer 7
[  162.6909] D/CDROM: Read sector 60043 [13:20:43]: mode 2 submode 0x08 into buffer 0
[  162.6911] D/CDROM: Read sector 60044 [13:20:44]: mode 2 submode 0x08 into buffer 1
[  162.6914] D/CDROM: Read sector 60045 [13:20:45]: mode 2 submode 0x08 into buffer 2
[  162.7079] D/CDROM: Read sector 60046 [13:20:46]: mode 2 submode 0x08 into buffer 3
[  162.7082] D/CDROM: Read sector 60047 [13:20:47]: mode 2 submode 0x08 into buffer 4
[  162.7245] D/CDROM: Read sector 60048 [13:20:48]: mode 2 submode 0x08 into buffer 5
[  162.7246] D/CDROM: Read sector 60049 [13:20:49]: mode 2 submode 0x89 into buffer 6
[  162.7246] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  162.9921] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.44 GPU: 0.00 Avg: 16.72ms Min: 16.10ms Max: 17.41ms
[  163.9950] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.85 GPU: 0.00 Avg: 16.72ms Min: 16.20ms Max: 17.26ms
[  164.9978] V/PerfMon: FPS: 1.00 VPS: 59.83 CPU: 3.70 GPU: 0.00 Avg: 16.71ms Min: 15.64ms Max: 17.35ms
[  166.0007] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 3.71 GPU: 0.00 Avg: 16.72ms Min: 15.64ms Max: 17.64ms
[  167.0040] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 3.87 GPU: 0.00 Avg: 16.72ms Min: 16.04ms Max: 17.43ms
[  168.0070] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 3.75 GPU: 0.00 Avg: 16.72ms Min: 15.83ms Max: 17.69ms
[  169.0104] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 3.85 GPU: 0.00 Avg: 16.72ms Min: 8.61ms Max: 26.33ms
[  170.0131] V/PerfMon: FPS: 0.00 VPS: 59.84 CPU: 3.69 GPU: 0.00 Avg: 16.71ms Min: 15.94ms Max: 17.53ms
[  171.0163] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 3.81 GPU: 0.00 Avg: 16.72ms Min: 15.50ms Max: 18.01ms
[  172.0195] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 3.90 GPU: 0.00 Avg: 16.72ms Min: 15.98ms Max: 17.38ms
[  173.0227] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 3.87 GPU: 0.00 Avg: 16.72ms Min: 8.12ms Max: 25.02ms
[  174.0253] V/PerfMon: FPS: 0.00 VPS: 59.85 CPU: 4.03 GPU: 0.00 Avg: 16.71ms Min: 10.61ms Max: 23.15ms
[  175.0288] V/PerfMon: FPS: 0.00 VPS: 59.79 CPU: 4.18 GPU: 0.00 Avg: 16.72ms Min: 16.03ms Max: 17.41ms
[  176.0321] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 3.81 GPU: 0.00 Avg: 16.72ms Min: 14.06ms Max: 19.57ms
[  177.0348] V/PerfMon: FPS: 0.00 VPS: 59.84 CPU: 3.58 GPU: 0.00 Avg: 16.71ms Min: 16.20ms Max: 17.23ms
[  178.0376] V/PerfMon: FPS: 0.00 VPS: 59.83 CPU: 3.69 GPU: 0.00 Avg: 16.71ms Min: 15.88ms Max: 17.57ms
[  179.0406] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 3.76 GPU: 0.00 Avg: 16.72ms Min: 7.81ms Max: 25.88ms
[  180.0440] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 3.94 GPU: 0.00 Avg: 16.72ms Min: 15.77ms Max: 17.52ms
[  181.0468] V/PerfMon: FPS: 0.00 VPS: 59.83 CPU: 3.88 GPU: 0.00 Avg: 16.71ms Min: 15.62ms Max: 17.85ms
[  182.0498] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 4.24 GPU: 0.00 Avg: 16.72ms Min: 15.85ms Max: 17.85ms
[  183.0530] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 3.71 GPU: 0.00 Avg: 16.72ms Min: 15.60ms Max: 17.32ms
[  184.0557] V/PerfMon: FPS: 0.00 VPS: 59.84 CPU: 3.82 GPU: 0.00 Avg: 16.71ms Min: 15.51ms Max: 17.75ms
[  185.0591] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 3.82 GPU: 0.00 Avg: 16.72ms Min: 15.41ms Max: 17.71ms
[  186.0619] V/PerfMon: FPS: 0.00 VPS: 59.83 CPU: 3.79 GPU: 0.00 Avg: 16.71ms Min: 16.14ms Max: 17.43ms
[  187.0652] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 3.98 GPU: 0.00 Avg: 16.72ms Min: 16.22ms Max: 17.19ms
[  188.0685] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 3.90 GPU: 0.00 Avg: 16.72ms Min: 15.89ms Max: 17.33ms
[  189.0712] V/PerfMon: FPS: 0.00 VPS: 59.83 CPU: 3.71 GPU: 0.00 Avg: 16.71ms Min: 16.20ms Max: 17.53ms
[  190.0746] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 4.24 GPU: 0.00 Avg: 16.72ms Min: 15.83ms Max: 17.91ms
[  191.0774] V/PerfMon: FPS: 0.00 VPS: 59.83 CPU: 3.95 GPU: 0.00 Avg: 16.71ms Min: 15.82ms Max: 17.44ms