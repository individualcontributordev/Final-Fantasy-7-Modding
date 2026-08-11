# Task: Retest disc1 to disc2 (LOST2 break) on single-disc-on-csr v0.1.6

## What was wrong

Disc 1 → “disc 2” freeze / no break scene at the start of disc 2.

**Cause:** CSR D2 **LOST2** break jumps to **cos_btm2**, but an IFUW often
skipped that MAPJUMP on single-disc (disc-id / flag context). You landed on
the forest without the D2 open break.

**Fix:** **single-disc-on-csr-v0.1.6** forces that MAPJUMP (IFUW else-jump 0).
Still includes 0.1.5 post-Hojo Ask strips.

## What you do

1. Hard-refresh the builder  
2. Rebuild Disc 1: **CSR + CSR+ + Single-disc**  
3. Confirm APPLIED.txt shows **single-disc-on-csr-v0.1.6**  
4. **Quit DuckStation fully**, then open the new bin (no save-state for this test)  
5. From an **in-game save** before the disc1→2 transition, run the transition  
6. Expect **break / cos_btm2 routing**, then LOST2 area playable  

Also optional: cold-boot retest post-Hojo → field 744 if you have that save.

## Evidence (fill in)

```
APPLIED single-disc id:
Disc1 to disc2 transition: OK / FREEZE / NO BREAK / OTHER
Break scene / cosmo bottom2: SEEN / MISSING
Field after transition playable?: YES / NO
CSR+ on?: YES/NO
Used save-state?: NO (preferred) / YES
Cold DuckStation boot?: YES/NO
notes:
```

## When done

Pull, paste evidence into this file, commit, push, say **check**.

Commit message example: ops: retest disc1-disc2 LOST2 break after single-disc 0.1.6


fresh duckstation restart, after guard scorpion, freezes

[  214.3241] D/CDROM: Read sector 60233 [13:23:08]: mode 2 submode 0x08 into buffer 6
[  214.3243] D/CDROM: Read sector 60234 [13:23:09]: mode 2 submode 0x08 into buffer 7
[  214.3407] D/CDROM: Read sector 60235 [13:23:10]: mode 2 submode 0x08 into buffer 0
[  214.3410] D/CDROM: Read sector 60236 [13:23:11]: mode 2 submode 0x08 into buffer 1
[  214.3412] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  214.4078] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x23, 0x12]
[  214.4079] D/CDROM: CDROM setloc command (13, 23, 12)
[  214.4083] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  214.4083] D/CDROM: Seek time for 13:23:05->13:23:12 (7 LBA): 1580544 (46.667 ms) (forward)
[  214.4581] D/CDROM: Logical seek to [13:23:12] complete, now reading
[  214.4585] D/CDROM: Read sector 60237 [13:23:12]: mode 2 submode 0x08 into buffer 1
[  214.4588] D/CDROM: Read sector 60238 [13:23:13]: mode 2 submode 0x08 into buffer 2
[  214.4750] D/CDROM: Read sector 60239 [13:23:14]: mode 2 submode 0x08 into buffer 3
[  214.4752] D/CDROM: Read sector 60240 [13:23:15]: mode 2 submode 0x08 into buffer 4
[  214.4916] D/CDROM: Read sector 60241 [13:23:16]: mode 2 submode 0x08 into buffer 5
[  214.4918] D/CDROM: Read sector 60242 [13:23:17]: mode 2 submode 0x08 into buffer 6
[  214.4922] D/CDROM: Read sector 60243 [13:23:18]: mode 2 submode 0x08 into buffer 7
[  214.5080] V/PerfMon: FPS: 59.82 VPS: 59.82 CPU: 4.14 GPU: 0.00 Avg: 16.72ms Min: 15.91ms Max: 17.29ms
[  214.5083] D/CDROM: Read sector 60244 [13:23:19]: mode 2 submode 0x08 into buffer 0
[  214.5084] D/CDROM: Read sector 60245 [13:23:20]: mode 2 submode 0x08 into buffer 1
[  214.5085] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  214.5750] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x23, 0x21]
[  214.5751] D/CDROM: CDROM setloc command (13, 23, 21)
[  214.5755] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  214.5756] D/CDROM: Seek time for 13:23:14->13:23:21 (7 LBA): 1580544 (46.667 ms) (forward)
[  214.6252] D/CDROM: Logical seek to [13:23:21] complete, now reading
[  214.6254] D/CDROM: Read sector 60246 [13:23:21]: mode 2 submode 0x08 into buffer 1
[  214.6258] D/CDROM: Read sector 60247 [13:23:22]: mode 2 submode 0x08 into buffer 2
[  214.6422] D/CDROM: Read sector 60248 [13:23:23]: mode 2 submode 0x08 into buffer 3
[  214.6423] D/CDROM: Read sector 60249 [13:23:24]: mode 2 submode 0x08 into buffer 4
[  214.6589] D/CDROM: Read sector 60250 [13:23:25]: mode 2 submode 0x08 into buffer 5
[  214.6592] D/CDROM: Read sector 60251 [13:23:26]: mode 2 submode 0x08 into buffer 6
[  214.6597] D/CDROM: Read sector 60252 [13:23:27]: mode 2 submode 0x08 into buffer 7
[  214.6753] D/CDROM: Read sector 60253 [13:23:28]: mode 2 submode 0x08 into buffer 0
[  214.6755] D/CDROM: Read sector 60254 [13:23:29]: mode 2 submode 0x08 into buffer 1
[  214.6756] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  214.7423] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x23, 0x30]
[  214.7424] D/CDROM: CDROM setloc command (13, 23, 30)
[  214.7429] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  214.7429] D/CDROM: Seek time for 13:23:23->13:23:30 (7 LBA): 1580544 (46.667 ms) (forward)
[  214.7923] D/CDROM: Logical seek to [13:23:30] complete, now reading
[  214.7926] D/CDROM: Read sector 60255 [13:23:30]: mode 2 submode 0x08 into buffer 1
[  214.8092] D/CDROM: Read sector 60256 [13:23:31]: mode 2 submode 0x08 into buffer 2
[  214.8094] D/CDROM: Read sector 60257 [13:23:32]: mode 2 submode 0x08 into buffer 3
[  214.8095] D/CDROM: Read sector 60258 [13:23:33]: mode 2 submode 0x08 into buffer 4
[  214.8256] D/CDROM: Read sector 60259 [13:23:34]: mode 2 submode 0x08 into buffer 5
[  214.8259] D/CDROM: Read sector 60260 [13:23:35]: mode 2 submode 0x08 into buffer 6
[  214.8426] D/CDROM: Read sector 60261 [13:23:36]: mode 2 submode 0x08 into buffer 7
[  214.8428] D/CDROM: Read sector 60262 [13:23:37]: mode 2 submode 0x08 into buffer 0
[  214.8429] D/CDROM: Read sector 60263 [13:23:38]: mode 2 submode 0x08 into buffer 1
[  214.8430] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  214.9093] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x23, 0x39]
[  214.9095] D/CDROM: CDROM setloc command (13, 23, 39)
[  214.9099] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  214.9100] D/CDROM: Seek time for 13:23:32->13:23:39 (7 LBA): 1580544 (46.667 ms) (forward)
[  214.9597] D/CDROM: Logical seek to [13:23:39] complete, now reading
[  214.9599] D/CDROM: Read sector 60264 [13:23:39]: mode 2 submode 0x08 into buffer 1
[  214.9759] D/CDROM: Read sector 60265 [13:23:40]: mode 2 submode 0x08 into buffer 2
[  214.9762] D/CDROM: Read sector 60266 [13:23:41]: mode 2 submode 0x08 into buffer 3
[  214.9763] D/CDROM: Read sector 60267 [13:23:42]: mode 2 submode 0x08 into buffer 4
[  214.9928] D/CDROM: Read sector 60268 [13:23:43]: mode 2 submode 0x08 into buffer 5
[  214.9931] D/CDROM: Read sector 60269 [13:23:44]: mode 2 submode 0x08 into buffer 6
[  215.0095] D/CDROM: Read sector 60270 [13:23:45]: mode 2 submode 0x08 into buffer 7
[  215.0099] D/CDROM: Read sector 60271 [13:23:46]: mode 2 submode 0x08 into buffer 0
[  215.0100] D/CDROM: Read sector 60272 [13:23:47]: mode 2 submode 0x08 into buffer 1
[  215.0101] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  215.0769] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x23, 0x48]
[  215.0770] D/CDROM: CDROM setloc command (13, 23, 48)
[  215.0774] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  215.0775] D/CDROM: Seek time for 13:23:41->13:23:48 (7 LBA): 1580544 (46.667 ms) (forward)
[  215.1271] D/CDROM: Logical seek to [13:23:48] complete, now reading
[  215.1274] D/CDROM: Read sector 60273 [13:23:48]: mode 2 submode 0x08 into buffer 1
[  215.1439] D/CDROM: Read sector 60274 [13:23:49]: mode 2 submode 0x08 into buffer 2
[  215.1443] D/CDROM: Read sector 60275 [13:23:50]: mode 2 submode 0x08 into buffer 3
[  215.1445] D/CDROM: Read sector 60276 [13:23:51]: mode 2 submode 0x08 into buffer 4
[  215.1608] D/CDROM: Read sector 60277 [13:23:52]: mode 2 submode 0x08 into buffer 5
[  215.1610] D/CDROM: Read sector 60278 [13:23:53]: mode 2 submode 0x08 into buffer 6
[  215.1766] D/CDROM: Read sector 60279 [13:23:54]: mode 2 submode 0x08 into buffer 7
[  215.1768] D/CDROM: Read sector 60280 [13:23:55]: mode 2 submode 0x08 into buffer 0
[  215.1769] D/CDROM: Read sector 60281 [13:23:56]: mode 2 submode 0x08 into buffer 1
[  215.1770] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  215.2440] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x23, 0x57]
[  215.2441] D/CDROM: CDROM setloc command (13, 23, 57)
[  215.2445] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  215.2446] D/CDROM: Seek time for 13:23:50->13:23:57 (7 LBA): 1580544 (46.667 ms) (forward)
[  215.2938] D/CDROM: Logical seek to [13:23:57] complete, now reading
[  215.2940] D/CDROM: Read sector 60282 [13:23:57]: mode 2 submode 0x08 into buffer 1
[  215.3108] D/CDROM: Read sector 60283 [13:23:58]: mode 2 submode 0x08 into buffer 2
[  215.3110] D/CDROM: Read sector 60284 [13:23:59]: mode 2 submode 0x08 into buffer 3
[  215.3272] D/CDROM: Read sector 60285 [13:23:60]: mode 2 submode 0x08 into buffer 4
[  215.3275] D/CDROM: Read sector 60286 [13:23:61]: mode 2 submode 0x08 into buffer 5
[  215.3279] D/CDROM: Read sector 60287 [13:23:62]: mode 2 submode 0x08 into buffer 6
[  215.3440] D/CDROM: Read sector 60288 [13:23:63]: mode 2 submode 0x08 into buffer 7
[  215.3443] D/CDROM: Read sector 60289 [13:23:64]: mode 2 submode 0x08 into buffer 0
[  215.3606] D/CDROM: Read sector 60290 [13:23:65]: mode 2 submode 0x08 into buffer 1
[  215.3608] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  215.4109] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x23, 0x66]
[  215.4110] D/CDROM: CDROM setloc command (13, 23, 66)
[  215.4114] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  215.4114] D/CDROM: Seek time for 13:23:59->13:23:66 (7 LBA): 1580544 (46.667 ms) (forward)
[  215.4612] D/CDROM: Logical seek to [13:23:66] complete, now reading
[  215.4616] D/CDROM: Read sector 60291 [13:23:66]: mode 2 submode 0x08 into buffer 1
[  215.4781] D/CDROM: Read sector 60292 [13:23:67]: mode 2 submode 0x08 into buffer 2
[  215.4783] D/CDROM: Read sector 60293 [13:23:68]: mode 2 submode 0x08 into buffer 3
[  215.4946] D/CDROM: Read sector 60294 [13:23:69]: mode 2 submode 0x08 into buffer 4
[  215.4949] D/CDROM: Read sector 60295 [13:23:70]: mode 2 submode 0x08 into buffer 5
[  215.4953] D/CDROM: Read sector 60296 [13:23:71]: mode 2 submode 0x08 into buffer 6
[  215.5111] V/PerfMon: FPS: 27.91 VPS: 59.81 CPU: 4.21 GPU: 0.00 Avg: 16.72ms Min: 15.87ms Max: 17.26ms
[  215.5114] D/CDROM: Read sector 60297 [13:23:72]: mode 2 submode 0x08 into buffer 7
[  215.5115] D/CDROM: Read sector 60298 [13:23:73]: mode 2 submode 0x08 into buffer 0
[  215.5279] D/CDROM: Read sector 60299 [13:23:74]: mode 2 submode 0x08 into buffer 1
[  215.5280] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  215.5782] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x24, 0x00]
[  215.5784] D/CDROM: CDROM setloc command (13, 24, 00)
[  215.5788] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  215.5788] D/CDROM: Seek time for 13:23:68->13:24:00 (7 LBA): 1580544 (46.667 ms) (forward)
[  215.6284] D/CDROM: Logical seek to [13:24:00] complete, now reading
[  215.6286] D/CDROM: Read sector 60300 [13:24:00]: mode 2 submode 0x08 into buffer 1
[  215.6454] D/CDROM: Read sector 60301 [13:24:01]: mode 2 submode 0x08 into buffer 2
[  215.6457] D/CDROM: Read sector 60302 [13:24:02]: mode 2 submode 0x08 into buffer 3
[  215.6617] D/CDROM: Read sector 60303 [13:24:03]: mode 2 submode 0x08 into buffer 4
[  215.6621] D/CDROM: Read sector 60304 [13:24:04]: mode 2 submode 0x08 into buffer 5
[  215.6624] D/CDROM: Read sector 60305 [13:24:05]: mode 2 submode 0x08 into buffer 6
[  215.6783] D/CDROM: Read sector 60306 [13:24:06]: mode 2 submode 0x08 into buffer 7
[  215.6785] D/CDROM: Read sector 60307 [13:24:07]: mode 2 submode 0x08 into buffer 0
[  215.6948] D/CDROM: Read sector 60308 [13:24:08]: mode 2 submode 0x08 into buffer 1
[  215.6950] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  215.7452] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x24, 0x09]
[  215.7453] D/CDROM: CDROM setloc command (13, 24, 09)
[  215.7458] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  215.7459] D/CDROM: Seek time for 13:24:02->13:24:09 (7 LBA): 1580544 (46.667 ms) (forward)
[  215.7955] D/CDROM: Logical seek to [13:24:09] complete, now reading
[  215.8119] D/CDROM: Read sector 60309 [13:24:09]: mode 2 submode 0x08 into buffer 1
[  215.8121] D/CDROM: Read sector 60310 [13:24:10]: mode 2 submode 0x08 into buffer 2
[  215.8123] D/CDROM: Read sector 60311 [13:24:11]: mode 2 submode 0x08 into buffer 3
[  215.8289] D/CDROM: Read sector 60312 [13:24:12]: mode 2 submode 0x08 into buffer 4
[  215.8291] D/CDROM: Read sector 60313 [13:24:13]: mode 2 submode 0x08 into buffer 5
[  215.8454] D/CDROM: Read sector 60314 [13:24:14]: mode 2 submode 0x08 into buffer 6
[  215.8456] D/CDROM: Read sector 60315 [13:24:15]: mode 2 submode 0x08 into buffer 7
[  215.8457] D/CDROM: Read sector 60316 [13:24:16]: mode 2 submode 0x08 into buffer 0
[  215.8625] D/CDROM: Read sector 60317 [13:24:17]: mode 2 submode 0x08 into buffer 1
[  215.8627] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  215.9129] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x24, 0x18]
[  215.9130] D/CDROM: CDROM setloc command (13, 24, 18)
[  215.9135] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  215.9135] D/CDROM: Seek time for 13:24:11->13:24:18 (7 LBA): 1580544 (46.667 ms) (forward)
[  215.9628] D/CDROM: Logical seek to [13:24:18] complete, now reading
[  215.9791] D/CDROM: Read sector 60318 [13:24:18]: mode 2 submode 0x08 into buffer 1
[  215.9793] D/CDROM: Read sector 60319 [13:24:19]: mode 2 submode 0x08 into buffer 2
[  215.9794] D/CDROM: Read sector 60320 [13:24:20]: mode 2 submode 0x08 into buffer 3
[  215.9958] D/CDROM: Read sector 60321 [13:24:21]: mode 2 submode 0x08 into buffer 4
[  215.9961] D/CDROM: Read sector 60322 [13:24:22]: mode 2 submode 0x08 into buffer 5
[  216.0127] D/CDROM: Read sector 60323 [13:24:23]: mode 2 submode 0x08 into buffer 6
[  216.0129] D/CDROM: Read sector 60324 [13:24:24]: mode 2 submode 0x08 into buffer 7
[  216.0131] D/CDROM: Read sector 60325 [13:24:25]: mode 2 submode 0x08 into buffer 0
[  216.0296] D/CDROM: Read sector 60326 [13:24:26]: mode 2 submode 0x08 into buffer 1
[  216.0297] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  216.0797] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x24, 0x27]
[  216.0798] D/CDROM: CDROM setloc command (13, 24, 27)
[  216.0802] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  216.0802] D/CDROM: Seek time for 13:24:20->13:24:27 (7 LBA): 1580544 (46.667 ms) (forward)
[  216.1299] D/CDROM: Logical seek to [13:24:27] complete, now reading
[  216.1466] D/CDROM: Read sector 60327 [13:24:27]: mode 2 submode 0x08 into buffer 1
[  216.1469] D/CDROM: Read sector 60328 [13:24:28]: mode 2 submode 0x08 into buffer 2
[  216.1472] D/CDROM: Read sector 60329 [13:24:29]: mode 2 submode 0x08 into buffer 3
[  216.1637] D/CDROM: Read sector 60330 [13:24:30]: mode 2 submode 0x08 into buffer 4
[  216.1640] D/CDROM: Read sector 60331 [13:24:31]: mode 2 submode 0x08 into buffer 5
[  216.1800] D/CDROM: Read sector 60332 [13:24:32]: mode 2 submode 0x08 into buffer 6
[  216.1803] D/CDROM: Read sector 60333 [13:24:33]: mode 2 submode 0x08 into buffer 7
[  216.1806] D/CDROM: Read sector 60334 [13:24:34]: mode 2 submode 0x08 into buffer 0
[  216.1967] D/CDROM: Read sector 60335 [13:24:35]: mode 2 submode 0x08 into buffer 1
[  216.1968] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  216.2470] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x24, 0x36]
[  216.2471] D/CDROM: CDROM setloc command (13, 24, 36)
[  216.2634] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  216.2635] D/CDROM: Seek time for 13:24:29->13:24:36 (7 LBA): 1580544 (46.667 ms) (forward)
[  216.2969] D/CDROM: Logical seek to [13:24:36] complete, now reading
[  216.3137] D/CDROM: Read sector 60336 [13:24:36]: mode 2 submode 0x08 into buffer 1
[  216.3139] D/CDROM: Read sector 60337 [13:24:37]: mode 2 submode 0x08 into buffer 2
[  216.3302] D/CDROM: Read sector 60338 [13:24:38]: mode 2 submode 0x08 into buffer 3
[  216.3305] D/CDROM: Read sector 60339 [13:24:39]: mode 2 submode 0x08 into buffer 4
[  216.3311] D/CDROM: Read sector 60340 [13:24:40]: mode 2 submode 0x08 into buffer 5
[  216.3472] D/CDROM: Read sector 60341 [13:24:41]: mode 2 submode 0x08 into buffer 6
[  216.3474] D/CDROM: Read sector 60342 [13:24:42]: mode 2 submode 0x08 into buffer 7
[  216.3635] D/CDROM: Read sector 60343 [13:24:43]: mode 2 submode 0x08 into buffer 0
[  216.3637] D/CDROM: Read sector 60344 [13:24:44]: mode 2 submode 0x08 into buffer 1
[  216.3640] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  216.4310] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x24, 0x45]
[  216.4311] D/CDROM: CDROM setloc command (13, 24, 45)
[  216.4314] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  216.4315] D/CDROM: Seek time for 13:24:38->13:24:45 (7 LBA): 1580544 (46.667 ms) (forward)
[  216.4640] D/CDROM: Logical seek to [13:24:45] complete, now reading
[  216.4807] D/CDROM: Read sector 60345 [13:24:45]: mode 2 submode 0x89 into buffer 1
[  216.4809] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  216.5140] V/PerfMon: FPS: 0.00 VPS: 59.83 CPU: 4.12 GPU: 0.00 Avg: 16.71ms Min: 16.25ms Max: 17.13ms
[  216.5313] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x22, 0x67]
[  216.5314] D/CDROM: CDROM setloc command (13, 22, 67)
[  216.5474] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  216.5475] D/CDROM: Seek time for 13:24:39->13:22:67 (122 LBA): 1693440 (50.000 ms) (NT backward)
[  216.5978] D/CDROM: Logical seek to [13:22:67] complete, now reading
[  216.5981] D/CDROM: Read sector 60217 [13:22:67]: mode 2 submode 0x08 into buffer 1
[  216.5986] D/CDROM: Read sector 60218 [13:22:68]: mode 2 submode 0x08 into buffer 2
[  216.6145] D/CDROM: Read sector 60219 [13:22:69]: mode 2 submode 0x08 into buffer 3
[  216.6147] D/CDROM: Read sector 60220 [13:22:70]: mode 2 submode 0x08 into buffer 4
[  216.6310] D/CDROM: Read sector 60221 [13:22:71]: mode 2 submode 0x08 into buffer 5
[  216.6313] D/CDROM: Read sector 60222 [13:22:72]: mode 2 submode 0x08 into buffer 6
[  216.6320] D/CDROM: Read sector 60223 [13:22:73]: mode 2 submode 0x08 into buffer 7
[  216.6479] D/CDROM: Read sector 60224 [13:22:74]: mode 2 submode 0x08 into buffer 0
[  216.6481] D/CDROM: Read sector 60225 [13:23:00]: mode 2 submode 0x08 into buffer 1
[  216.6481] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  216.7146] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x23, 0x01]
[  216.7147] D/CDROM: CDROM setloc command (13, 23, 01)
[  216.7154] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  216.7155] D/CDROM: Seek time for 13:22:69->13:23:01 (7 LBA): 1580544 (46.667 ms) (forward)
[  216.7651] D/CDROM: Logical seek to [13:23:01] complete, now reading
[  216.7654] D/CDROM: Read sector 60226 [13:23:01]: mode 2 submode 0x08 into buffer 1
[  216.7661] D/CDROM: Read sector 60227 [13:23:02]: mode 2 submode 0x89 into buffer 2
[  216.7661] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  216.8325] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x13, 0x24, 0x46]
[  216.8326] D/CDROM: CDROM setloc command (13, 24, 46)
[  216.8332] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  216.8333] D/CDROM: Seek time for 13:22:71->13:24:46 (125 LBA): 1693440 (50.000 ms) (NT forward)
[  216.8820] D/CDROM: Logical seek to [13:24:46] complete, now reading
[  216.8822] D/CDROM: Read sector 60346 [13:24:46]: mode 2 submode 0x08 into buffer 1
[  216.8988] D/CDROM: Read sector 60347 [13:24:47]: mode 2 submode 0x08 into buffer 2
[  216.8991] D/CDROM: Read sector 60348 [13:24:48]: mode 2 submode 0x08 into buffer 3
[  216.9155] D/CDROM: Read sector 60349 [13:24:49]: mode 2 submode 0x08 into buffer 4
[  216.9157] D/CDROM: Read sector 60350 [13:24:50]: mode 2 submode 0x08 into buffer 5
[  216.9163] D/CDROM: Read sector 60351 [13:24:51]: mode 2 submode 0x08 into buffer 6
[  216.9324] D/CDROM: Read sector 60352 [13:24:52]: mode 2 submode 0x89 into buffer 7
[  216.9325] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  216.9326] D/CodeCache: Ignoring fault due to RAM write @ 0x801B0000
[  216.9327] D/CodeCache: Ignoring fault due to RAM write @ 0x801B1000
[  216.9825] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x16]
[  216.9826] D/CDROM: CDROM setloc command (28, 13, 16)
[  216.9990] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  216.9991] D/CDROM: Seek time for 13:24:46->28:13:16 (66645 LBA): 15326652 (452.530 ms) (2N/sled forward)
[  217.4501] D/CDROM: Logical seek to [28:13:16] complete, now reading
[  217.4503] D/CDROM: Read sector 126991 [28:13:16]: mode 2 submode 0x08 into buffer 1
[  217.4514] D/CDROM: Read sector 126992 [28:13:17]: mode 2 submode 0x08 into buffer 2
[  217.4674] D/CDROM: Read sector 126993 [28:13:18]: mode 2 submode 0x08 into buffer 3
[  217.4678] D/CDROM: Read sector 126994 [28:13:19]: mode 2 submode 0x89 into buffer 4
[  217.4679] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  217.5172] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 4.11 GPU: 0.00 Avg: 16.72ms Min: 15.79ms Max: 17.65ms
[  217.5343] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x24]
[  217.5344] D/CDROM: CDROM setloc command (28, 13, 24)
[  217.5344] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  217.5344] D/CDROM: Seek time for 28:13:11->28:13:24 (13 LBA): 1693440 (50.000 ms) (NT forward)
[  217.5844] D/CDROM: Logical seek to [28:13:24] complete, now reading
[  217.5846] D/CDROM: Read sector 126999 [28:13:24]: mode 2 submode 0x08 into buffer 1
[  217.6007] D/CDROM: Read sector 127000 [28:13:25]: mode 2 submode 0x08 into buffer 2
[  217.6010] D/CDROM: Read sector 127001 [28:13:26]: mode 2 submode 0x08 into buffer 3
[  217.6011] D/CDROM: Read sector 127002 [28:13:27]: mode 2 submode 0x89 into buffer 4
[  217.6177] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  217.6680] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x28, 0x13, 0x54]
[  217.6682] D/CDROM: CDROM setloc command (28, 13, 54)
[  217.6691] D/CDROM: CDROM executing command 0x06 (ReadN), stat = 0x02, params = []
[  217.6692] D/CDROM: Seek time for 28:13:19->28:13:54 (35 LBA): 1693440 (50.000 ms) (NT forward)
[  217.7181] D/CDROM: Logical seek to [28:13:54] complete, now reading
[  217.7347] D/CDROM: Read sector 127029 [28:13:54]: mode 2 submode 0x08 into buffer 1
[  217.7350] D/CDROM: Read sector 127030 [28:13:55]: mode 2 submode 0x08 into buffer 2
[  217.7354] D/CDROM: Read sector 127031 [28:13:56]: mode 2 submode 0x08 into buffer 3
[  217.7513] D/CDROM: Read sector 127032 [28:13:57]: mode 2 submode 0x08 into buffer 4
[  217.7517] D/CDROM: Read sector 127033 [28:13:58]: mode 2 submode 0x08 into buffer 5
[  217.7678] D/CDROM: Read sector 127034 [28:13:59]: mode 2 submode 0x08 into buffer 6
[  217.7681] D/CDROM: Read sector 127035 [28:13:60]: mode 2 submode 0x89 into buffer 7
[  217.7683] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[  217.8516] D/CodeCache: Breaking block 0x800A2FD0 at 0x800A3000 due to page crossing
[  218.5204] V/PerfMon: FPS: 19.94 VPS: 59.81 CPU: 4.28 GPU: 0.00 Avg: 16.72ms Min: 16.20ms Max: 17.26ms
[  219.5233] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.75 GPU: 0.00 Avg: 16.72ms Min: 15.71ms Max: 17.59ms
[  220.5264] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 3.73 GPU: 0.00 Avg: 16.72ms Min: 15.49ms Max: 17.96ms
[  221.5296] V/PerfMon: FPS: 26.91 VPS: 59.81 CPU: 3.85 GPU: 0.00 Avg: 16.72ms Min: 15.02ms Max: 17.67ms
[  222.5325] V/PerfMon: FPS: 0.00 VPS: 59.83 CPU: 3.69 GPU: 0.00 Avg: 16.71ms Min: 15.95ms Max: 17.49ms
[  223.5356] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 3.70 GPU: 0.00 Avg: 16.72ms Min: 16.20ms Max: 17.20ms
[  224.5384] V/PerfMon: FPS: 0.00 VPS: 59.83 CPU: 3.57 GPU: 0.00 Avg: 16.71ms Min: 16.01ms Max: 17.87ms
[  225.5418] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 3.58 GPU: 0.00 Avg: 16.72ms Min: 8.65ms Max: 28.63ms
[  226.5448] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 3.60 GPU: 0.00 Avg: 16.72ms Min: 16.19ms Max: 17.16ms
[  227.5476] V/PerfMon: FPS: 0.00 VPS: 59.84 CPU: 3.57 GPU: 0.00 Avg: 16.71ms Min: 16.04ms Max: 17.33ms
[  228.5506] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 3.54 GPU: 0.00 Avg: 16.72ms Min: 16.19ms Max: 17.61ms
[  229.5540] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 3.59 GPU: 0.00 Avg: 16.72ms Min: 15.63ms Max: 17.79ms
[  230.5566] V/PerfMon: FPS: 0.00 VPS: 59.84 CPU: 3.54 GPU: 0.00 Avg: 16.71ms Min: 15.67ms Max: 17.85ms
[  231.5600] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 3.56 GPU: 0.00 Avg: 16.72ms Min: 15.64ms Max: 17.62ms
[  232.5630] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 3.54 GPU: 0.00 Avg: 16.72ms Min: 16.05ms Max: 17.31ms
[  233.5661] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 3.66 GPU: 0.00 Avg: 16.72ms Min: 13.22ms Max: 20.26ms