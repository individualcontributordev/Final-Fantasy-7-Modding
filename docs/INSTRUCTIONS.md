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

[  134.9936] D/CDROM: Read sector 250167 [55:35:42]: mode 2 submode 0x64 into buffer 4
[  134.9944] D/CDROM: Read sector 250168 [55:35:43]: mode 2 submode 0x48 into buffer 4
[  135.0102] D/CDROM: Read sector 250169 [55:35:44]: mode 2 submode 0x48 into buffer 5
[  135.0106] D/CDROM: Read sector 250170 [55:35:45]: mode 2 submode 0x48 into buffer 6
[  135.0271] D/CDROM: Read sector 250171 [55:35:46]: mode 2 submode 0x48 into buffer 7
[  135.0275] D/CDROM: Read sector 250172 [55:35:47]: mode 2 submode 0x48 into buffer 0
[  135.0278] D/CDROM: Read sector 250173 [55:35:48]: mode 2 submode 0x48 into buffer 1
[  135.0437] D/CDROM: Read sector 250174 [55:35:49]: mode 2 submode 0x48 into buffer 2
[  135.0440] D/CDROM: Read sector 250175 [55:35:50]: mode 2 submode 0x64 into buffer 3
[  135.0607] D/CDROM: Read sector 250176 [55:35:51]: mode 2 submode 0x48 into buffer 3
[  135.0610] D/CDROM: Read sector 250177 [55:35:52]: mode 2 submode 0x48 into buffer 4
[  135.0613] D/CDROM: Read sector 250178 [55:35:53]: mode 2 submode 0x48 into buffer 5
[  135.0770] D/CDROM: Read sector 250179 [55:35:54]: mode 2 submode 0x48 into buffer 6
[  135.0773] D/CDROM: Read sector 250180 [55:35:55]: mode 2 submode 0x48 into buffer 7
[  135.0938] D/CDROM: Read sector 250181 [55:35:56]: mode 2 submode 0x48 into buffer 0
[  135.0940] D/CDROM: Read sector 250182 [55:35:57]: mode 2 submode 0x48 into buffer 1
[  135.0944] D/CDROM: Read sector 250183 [55:35:58]: mode 2 submode 0x64 into buffer 2
[  135.1108] D/CDROM: Read sector 250184 [55:35:59]: mode 2 submode 0x48 into buffer 2
[  135.1111] D/CDROM: Read sector 250185 [55:35:60]: mode 2 submode 0x48 into buffer 3
[  135.1272] D/CDROM: Read sector 250186 [55:35:61]: mode 2 submode 0x48 into buffer 4
[  135.1276] D/CDROM: Read sector 250187 [55:35:62]: mode 2 submode 0x48 into buffer 5
[  135.1280] D/CDROM: Read sector 250188 [55:35:63]: mode 2 submode 0x48 into buffer 6
[  135.1438] D/CDROM: Read sector 250189 [55:35:64]: mode 2 submode 0x48 into buffer 7
[  135.1442] D/CDROM: Read sector 250190 [55:35:65]: mode 2 submode 0x48 into buffer 0
[  135.1603] D/CDROM: Read sector 250191 [55:35:66]: mode 2 submode 0x64 into buffer 1
[  135.1606] D/CDROM: Read sector 250192 [55:35:67]: mode 2 submode 0x48 into buffer 1
[  135.1609] D/CDROM: Read sector 250193 [55:35:68]: mode 2 submode 0x48 into buffer 2
[  135.1776] D/CDROM: Read sector 250194 [55:35:69]: mode 2 submode 0x48 into buffer 3
[  135.1780] D/CDROM: Read sector 250195 [55:35:70]: mode 2 submode 0x48 into buffer 4
[  135.1941] D/CDROM: Read sector 250196 [55:35:71]: mode 2 submode 0x48 into buffer 5
[  135.1945] D/CDROM: Read sector 250197 [55:35:72]: mode 2 submode 0x48 into buffer 6
[  135.1948] D/CDROM: Read sector 250198 [55:35:73]: mode 2 submode 0x48 into buffer 7
[  135.2109] D/CDROM: Read sector 250199 [55:35:74]: mode 2 submode 0x64 into buffer 0
[  135.2113] D/CDROM: Read sector 250200 [55:36:00]: mode 2 submode 0x48 into buffer 0
[  135.2273] D/CDROM: Read sector 250201 [55:36:01]: mode 2 submode 0x48 into buffer 1
[  135.2275] D/CDROM: Read sector 250202 [55:36:02]: mode 2 submode 0x48 into buffer 2
[  135.2277] D/CDROM: Read sector 250203 [55:36:03]: mode 2 submode 0x48 into buffer 3
[  135.2444] D/CDROM: Read sector 250204 [55:36:04]: mode 2 submode 0x48 into buffer 4
[  135.2449] D/CDROM: Read sector 250205 [55:36:05]: mode 2 submode 0x48 into buffer 5
[  135.2612] V/PerfMon: FPS: 15.94 VPS: 59.78 CPU: 5.86 GPU: 0.00 Avg: 16.73ms Min: 16.15ms Max: 17.41ms
[  135.2615] D/CDROM: Read sector 250206 [55:36:06]: mode 2 submode 0x48 into buffer 6
[  135.2617] D/CDROM: Read sector 250207 [55:36:07]: mode 2 submode 0x64 into buffer 7
[  135.2621] D/CDROM: Read sector 250208 [55:36:08]: mode 2 submode 0x48 into buffer 7
[  135.2777] D/CDROM: Read sector 250209 [55:36:09]: mode 2 submode 0x48 into buffer 0
[  135.2780] D/CDROM: Read sector 250210 [55:36:10]: mode 2 submode 0x48 into buffer 1
[  135.2944] D/CDROM: Read sector 250211 [55:36:11]: mode 2 submode 0x48 into buffer 2
[  135.2946] D/CDROM: Read sector 250212 [55:36:12]: mode 2 submode 0x48 into buffer 3
[  135.2949] D/CDROM: Read sector 250213 [55:36:13]: mode 2 submode 0x48 into buffer 4
[  135.3109] D/CDROM: Read sector 250214 [55:36:14]: mode 2 submode 0x48 into buffer 5
[  135.3112] D/CDROM: Read sector 250215 [55:36:15]: mode 2 submode 0x64 into buffer 6
[  135.3275] D/CDROM: Read sector 250216 [55:36:16]: mode 2 submode 0x48 into buffer 6
[  135.3279] D/CDROM: Read sector 250217 [55:36:17]: mode 2 submode 0x48 into buffer 7
[  135.3284] D/CDROM: Read sector 250218 [55:36:18]: mode 2 submode 0x48 into buffer 0
[  135.3448] D/CDROM: Read sector 250219 [55:36:19]: mode 2 submode 0x48 into buffer 1
[  135.3451] D/CDROM: Read sector 250220 [55:36:20]: mode 2 submode 0x48 into buffer 2
[  135.3614] D/CDROM: Read sector 250221 [55:36:21]: mode 2 submode 0x48 into buffer 3
[  135.3616] D/CDROM: Read sector 250222 [55:36:22]: mode 2 submode 0x48 into buffer 4
[  135.3620] D/CDROM: Read sector 250223 [55:36:23]: mode 2 submode 0x64 into buffer 5
[  135.3778] D/CDROM: Read sector 250224 [55:36:24]: mode 2 submode 0x48 into buffer 5
[  135.3782] D/CDROM: Read sector 250225 [55:36:25]: mode 2 submode 0x48 into buffer 6
[  135.3945] D/CDROM: Read sector 250226 [55:36:26]: mode 2 submode 0x48 into buffer 7
[  135.3949] D/CDROM: Read sector 250227 [55:36:27]: mode 2 submode 0x48 into buffer 0
[  135.3953] D/CDROM: Read sector 250228 [55:36:28]: mode 2 submode 0x48 into buffer 1
[  135.4117] D/CDROM: Read sector 250229 [55:36:29]: mode 2 submode 0x48 into buffer 2
[  135.4120] D/CDROM: Read sector 250230 [55:36:30]: mode 2 submode 0x48 into buffer 3
[  135.4281] D/CDROM: Read sector 250231 [55:36:31]: mode 2 submode 0x64 into buffer 4
[  135.4284] D/CDROM: Read sector 250232 [55:36:32]: mode 2 submode 0x48 into buffer 4
[  135.4286] D/CDROM: Read sector 250233 [55:36:33]: mode 2 submode 0x48 into buffer 5
[  135.4451] D/CDROM: Read sector 250234 [55:36:34]: mode 2 submode 0x48 into buffer 6
[  135.4454] D/CDROM: Read sector 250235 [55:36:35]: mode 2 submode 0x48 into buffer 7
[  135.4620] D/CDROM: Read sector 250236 [55:36:36]: mode 2 submode 0x48 into buffer 0
[  135.4625] D/CDROM: Read sector 250237 [55:36:37]: mode 2 submode 0x48 into buffer 1
[  135.4630] D/CDROM: Read sector 250238 [55:36:38]: mode 2 submode 0x48 into buffer 2
[  135.4783] D/CDROM: Read sector 250239 [55:36:39]: mode 2 submode 0x64 into buffer 3
[  135.4788] D/CDROM: Read sector 250240 [55:36:40]: mode 2 submode 0x48 into buffer 3
[  135.4951] D/CDROM: Read sector 250241 [55:36:41]: mode 2 submode 0x48 into buffer 4
[  135.4954] D/CDROM: Read sector 250242 [55:36:42]: mode 2 submode 0x48 into buffer 5
[  135.4957] D/CDROM: Read sector 250243 [55:36:43]: mode 2 submode 0x48 into buffer 6
[  135.5119] D/CDROM: Read sector 250244 [55:36:44]: mode 2 submode 0x48 into buffer 7
[  135.5122] D/CDROM: Read sector 250245 [55:36:45]: mode 2 submode 0x48 into buffer 0
[  135.5284] D/CDROM: Read sector 250246 [55:36:46]: mode 2 submode 0x48 into buffer 1
[  135.5294] D/CDROM: Read sector 250247 [55:36:47]: mode 2 submode 0x64 into buffer 2
[  135.5299] D/CDROM: Read sector 250248 [55:36:48]: mode 2 submode 0x48 into buffer 2
[  135.5455] D/CDROM: Read sector 250249 [55:36:49]: mode 2 submode 0x48 into buffer 3
[  135.5458] D/CDROM: Read sector 250250 [55:36:50]: mode 2 submode 0x48 into buffer 4
[  135.5620] D/CDROM: Read sector 250251 [55:36:51]: mode 2 submode 0x48 into buffer 5
[  135.5622] D/CDROM: Read sector 250252 [55:36:52]: mode 2 submode 0x48 into buffer 6
[  135.5625] D/CDROM: Read sector 250253 [55:36:53]: mode 2 submode 0x48 into buffer 7
[  135.5785] D/CDROM: Read sector 250254 [55:36:54]: mode 2 submode 0x48 into buffer 0
[  135.5788] D/CDROM: Read sector 250255 [55:36:55]: mode 2 submode 0x64 into buffer 1
[  135.5953] D/CDROM: Read sector 250256 [55:36:56]: mode 2 submode 0x48 into buffer 1
[  135.5957] D/CDROM: Read sector 250257 [55:36:57]: mode 2 submode 0x48 into buffer 2
[  135.5961] D/CDROM: Read sector 250258 [55:36:58]: mode 2 submode 0x48 into buffer 3
[  135.6120] D/CDROM: Read sector 250259 [55:36:59]: mode 2 submode 0x48 into buffer 4
[  135.6124] D/CDROM: Read sector 250260 [55:36:60]: mode 2 submode 0x48 into buffer 5
[  135.6288] D/CDROM: Read sector 250261 [55:36:61]: mode 2 submode 0x48 into buffer 6
[  135.6291] D/CDROM: Read sector 250262 [55:36:62]: mode 2 submode 0x48 into buffer 7
[  135.6294] D/CDROM: Read sector 250263 [55:36:63]: mode 2 submode 0x64 into buffer 0
[  135.6458] D/CDROM: Read sector 250264 [55:36:64]: mode 2 submode 0x48 into buffer 0
[  135.6461] D/CDROM: Read sector 250265 [55:36:65]: mode 2 submode 0x48 into buffer 1
[  135.6623] D/CDROM: Read sector 250266 [55:36:66]: mode 2 submode 0x48 into buffer 2
[  135.6627] D/CDROM: Read sector 250267 [55:36:67]: mode 2 submode 0x48 into buffer 3
[  135.6630] D/CDROM: Read sector 250268 [55:36:68]: mode 2 submode 0x48 into buffer 4
[  135.6790] D/CDROM: Read sector 250269 [55:36:69]: mode 2 submode 0x48 into buffer 5
[  135.6795] D/CDROM: Read sector 250270 [55:36:70]: mode 2 submode 0x48 into buffer 6
[  135.6952] D/CDROM: Read sector 250271 [55:36:71]: mode 2 submode 0x64 into buffer 7
[  135.6955] D/CDROM: Read sector 250272 [55:36:72]: mode 2 submode 0x48 into buffer 7
[  135.6959] D/CDROM: Read sector 250273 [55:36:73]: mode 2 submode 0x48 into buffer 0
[  135.7124] D/CDROM: Read sector 250274 [55:36:74]: mode 2 submode 0x48 into buffer 1
[  135.7127] D/CDROM: Read sector 250275 [55:37:00]: mode 2 submode 0x48 into buffer 2
[  135.7290] D/CDROM: Read sector 250276 [55:37:01]: mode 2 submode 0x48 into buffer 3
[  135.7293] D/CDROM: Read sector 250277 [55:37:02]: mode 2 submode 0x48 into buffer 4
[  135.7297] D/CDROM: Read sector 250278 [55:37:03]: mode 2 submode 0x48 into buffer 5
[  135.7458] D/CDROM: Read sector 250279 [55:37:04]: mode 2 submode 0x64 into buffer 6
[  135.7463] D/CDROM: Read sector 250280 [55:37:05]: mode 2 submode 0x48 into buffer 6
[  135.7625] D/CDROM: Read sector 250281 [55:37:06]: mode 2 submode 0x48 into buffer 7
[  135.7627] D/CDROM: Read sector 250282 [55:37:07]: mode 2 submode 0x48 into buffer 0
[  135.7631] D/CDROM: Read sector 250283 [55:37:08]: mode 2 submode 0x48 into buffer 1
[  135.7794] D/CDROM: Read sector 250284 [55:37:09]: mode 2 submode 0x48 into buffer 2
[  135.7797] D/CDROM: Read sector 250285 [55:37:10]: mode 2 submode 0x48 into buffer 3
[  135.7958] D/CDROM: Read sector 250286 [55:37:11]: mode 2 submode 0x48 into buffer 4
[  135.7961] D/CDROM: Read sector 250287 [55:37:12]: mode 2 submode 0x64 into buffer 5
[  135.7967] D/CDROM: Read sector 250288 [55:37:13]: mode 2 submode 0x48 into buffer 5
[  135.8130] D/CDROM: Read sector 250289 [55:37:14]: mode 2 submode 0x48 into buffer 6
[  135.8133] D/CDROM: Read sector 250290 [55:37:15]: mode 2 submode 0x48 into buffer 7
[  135.8291] D/CDROM: Read sector 250291 [55:37:16]: mode 2 submode 0x48 into buffer 0
[  135.8294] D/CDROM: Read sector 250292 [55:37:17]: mode 2 submode 0x48 into buffer 1
[  135.8297] D/CDROM: Read sector 250293 [55:37:18]: mode 2 submode 0x48 into buffer 2
[  135.8461] D/CDROM: Read sector 250294 [55:37:19]: mode 2 submode 0x48 into buffer 3
[  135.8465] D/CDROM: Read sector 250295 [55:37:20]: mode 2 submode 0x64 into buffer 4
[  135.8629] D/CDROM: Read sector 250296 [55:37:21]: mode 2 submode 0x48 into buffer 4
[  135.8633] D/CDROM: Read sector 250297 [55:37:22]: mode 2 submode 0x48 into buffer 5
[  135.8637] D/CDROM: Read sector 250298 [55:37:23]: mode 2 submode 0x48 into buffer 6
[  135.8794] D/CDROM: Read sector 250299 [55:37:24]: mode 2 submode 0x48 into buffer 7
[  135.8797] D/CDROM: Read sector 250300 [55:37:25]: mode 2 submode 0x48 into buffer 0
[  135.8800] D/CDROM: Read sector 250301 [55:37:26]: mode 2 submode 0x48 into buffer 1
[  135.8963] D/CDROM: Read sector 250302 [55:37:27]: mode 2 submode 0x48 into buffer 2
[  135.8967] D/CDROM: Read sector 250303 [55:37:28]: mode 2 submode 0x64 into buffer 3
[  135.9132] D/CDROM: Read sector 250304 [55:37:29]: mode 2 submode 0x48 into buffer 3
[  135.9136] D/CDROM: Read sector 250305 [55:37:30]: mode 2 submode 0x48 into buffer 4
[  135.9139] D/CDROM: Read sector 250306 [55:37:31]: mode 2 submode 0x48 into buffer 5
[  135.9299] D/CDROM: Read sector 250307 [55:37:32]: mode 2 submode 0x48 into buffer 6
[  135.9302] D/CDROM: Read sector 250308 [55:37:33]: mode 2 submode 0x48 into buffer 7
[  135.9464] D/CDROM: Read sector 250309 [55:37:34]: mode 2 submode 0x48 into buffer 0
[  135.9467] D/CDROM: Read sector 250310 [55:37:35]: mode 2 submode 0x48 into buffer 1
[  135.9469] D/CDROM: Read sector 250311 [55:37:36]: mode 2 submode 0x64 into buffer 2
[  135.9634] D/CDROM: Read sector 250312 [55:37:37]: mode 2 submode 0x48 into buffer 2
[  135.9636] D/CDROM: Read sector 250313 [55:37:38]: mode 2 submode 0x48 into buffer 3
[  135.9797] D/CDROM: Read sector 250314 [55:37:39]: mode 2 submode 0x48 into buffer 4
[  135.9800] D/CDROM: Read sector 250315 [55:37:40]: mode 2 submode 0x48 into buffer 5
[  135.9802] D/CDROM: Read sector 250316 [55:37:41]: mode 2 submode 0x48 into buffer 6
[  135.9964] D/CDROM: Read sector 250317 [55:37:42]: mode 2 submode 0x48 into buffer 7
[  135.9968] D/CDROM: Read sector 250318 [55:37:43]: mode 2 submode 0x48 into buffer 0
[  136.0135] D/CDROM: Read sector 250319 [55:37:44]: mode 2 submode 0x64 into buffer 1
[  136.0139] D/CDROM: Read sector 250320 [55:37:45]: mode 2 submode 0x48 into buffer 1
[  136.0140] D/CDROM: Read sector 250321 [55:37:46]: mode 2 submode 0x48 into buffer 2
[  136.0302] D/CDROM: Read sector 250322 [55:37:47]: mode 2 submode 0x48 into buffer 3
[  136.0304] D/CDROM: Read sector 250323 [55:37:48]: mode 2 submode 0x48 into buffer 4
[  136.0464] D/CDROM: Read sector 250324 [55:37:49]: mode 2 submode 0x48 into buffer 5
[  136.0467] D/CDROM: Read sector 250325 [55:37:50]: mode 2 submode 0x48 into buffer 6
[  136.0470] D/CDROM: Read sector 250326 [55:37:51]: mode 2 submode 0x48 into buffer 7
[  136.0634] D/CDROM: Read sector 250327 [55:37:52]: mode 2 submode 0x64 into buffer 0
[  136.0638] D/CDROM: Read sector 250328 [55:37:53]: mode 2 submode 0x48 into buffer 0
[  136.0800] D/CDROM: Read sector 250329 [55:37:54]: mode 2 submode 0x48 into buffer 1
[  136.0803] D/CDROM: Read sector 250330 [55:37:55]: mode 2 submode 0x48 into buffer 2
[  136.0808] D/CDROM: Read sector 250331 [55:37:56]: mode 2 submode 0x48 into buffer 3
[  136.0967] D/CDROM: Read sector 250332 [55:37:57]: mode 2 submode 0x48 into buffer 4
[  136.0969] D/CDROM: Read sector 250333 [55:37:58]: mode 2 submode 0x48 into buffer 5
[  136.1138] D/CDROM: Read sector 250334 [55:37:59]: mode 2 submode 0x48 into buffer 6
[  136.1141] D/CDROM: Read sector 250335 [55:37:60]: mode 2 submode 0x64 into buffer 7
[  136.1147] D/CDROM: Read sector 250336 [55:37:61]: mode 2 submode 0x48 into buffer 7
[  136.1303] D/CDROM: Read sector 250337 [55:37:62]: mode 2 submode 0x48 into buffer 0
[  136.1307] D/CDROM: Read sector 250338 [55:37:63]: mode 2 submode 0x48 into buffer 1
[  136.1471] D/CDROM: Read sector 250339 [55:37:64]: mode 2 submode 0x48 into buffer 2
[  136.1474] D/CDROM: Read sector 250340 [55:37:65]: mode 2 submode 0x48 into buffer 3
[  136.1478] D/CDROM: Read sector 250341 [55:37:66]: mode 2 submode 0x48 into buffer 4
[  136.1638] D/CDROM: Read sector 250342 [55:37:67]: mode 2 submode 0x48 into buffer 5
[  136.1640] D/CDROM: Read sector 250343 [55:37:68]: mode 2 submode 0x64 into buffer 6
[  136.1803] D/CDROM: Read sector 250344 [55:37:69]: mode 2 submode 0x48 into buffer 6
[  136.1806] D/CDROM: Read sector 250345 [55:37:70]: mode 2 submode 0x48 into buffer 7
[  136.1810] D/CDROM: Read sector 250346 [55:37:71]: mode 2 submode 0x48 into buffer 0
[  136.1975] D/CDROM: Read sector 250347 [55:37:72]: mode 2 submode 0x48 into buffer 1
[  136.1978] D/CDROM: Read sector 250348 [55:37:73]: mode 2 submode 0x48 into buffer 2
[  136.2138] D/CDROM: Read sector 250349 [55:37:74]: mode 2 submode 0x48 into buffer 3
[  136.2142] D/CDROM: Read sector 250350 [55:38:00]: mode 2 submode 0x48 into buffer 4
[  136.2148] D/CDROM: Read sector 250351 [55:38:01]: mode 2 submode 0x64 into buffer 5
[  136.2305] D/CDROM: Read sector 250352 [55:38:02]: mode 2 submode 0x48 into buffer 5
[  136.2307] D/CDROM: Read sector 250353 [55:38:03]: mode 2 submode 0x48 into buffer 6
[  136.2473] D/CDROM: Read sector 250354 [55:38:04]: mode 2 submode 0x48 into buffer 7
[  136.2477] D/CDROM: Read sector 250355 [55:38:05]: mode 2 submode 0x48 into buffer 0
[  136.2480] D/CDROM: Read sector 250356 [55:38:06]: mode 2 submode 0x48 into buffer 1
[  136.2639] V/PerfMon: FPS: 14.96 VPS: 59.84 CPU: 5.73 GPU: 0.00 Avg: 16.71ms Min: 16.14ms Max: 17.19ms
[  136.2643] D/CDROM: Read sector 250357 [55:38:07]: mode 2 submode 0x48 into buffer 2
[  136.2646] D/CDROM: Read sector 250358 [55:38:08]: mode 2 submode 0x48 into buffer 3
[  136.2809] D/CDROM: Read sector 250359 [55:38:09]: mode 2 submode 0x64 into buffer 4
[  136.2814] D/CDROM: Read sector 250360 [55:38:10]: mode 2 submode 0x48 into buffer 4
[  136.2816] D/CDROM: Read sector 250361 [55:38:11]: mode 2 submode 0x48 into buffer 5
[  136.2975] D/CDROM: Read sector 250362 [55:38:12]: mode 2 submode 0x48 into buffer 6
[  136.2977] D/CDROM: Read sector 250363 [55:38:13]: mode 2 submode 0x48 into buffer 7
[  136.3144] D/CDROM: Read sector 250364 [55:38:14]: mode 2 submode 0x48 into buffer 0
[  136.3147] D/CDROM: Read sector 250365 [55:38:15]: mode 2 submode 0x48 into buffer 1
[  136.3151] D/CDROM: Read sector 250366 [55:38:16]: mode 2 submode 0x48 into buffer 2
[  136.3312] D/CDROM: Read sector 250367 [55:38:17]: mode 2 submode 0x64 into buffer 3
[  136.3316] D/CDROM: Read sector 250368 [55:38:18]: mode 2 submode 0x48 into buffer 3
[  136.3475] D/CDROM: Read sector 250369 [55:38:19]: mode 2 submode 0x48 into buffer 4
[  136.3479] D/CDROM: Read sector 250370 [55:38:20]: mode 2 submode 0x48 into buffer 5
[  136.3483] D/CDROM: Read sector 250371 [55:38:21]: mode 2 submode 0x48 into buffer 6
[  136.3642] D/CDROM: Read sector 250372 [55:38:22]: mode 2 submode 0x48 into buffer 7
[  136.3644] D/CDROM: Read sector 250373 [55:38:23]: mode 2 submode 0x48 into buffer 0
[  136.3807] D/CDROM: Read sector 250374 [55:38:24]: mode 2 submode 0x48 into buffer 1
[  136.3811] D/CDROM: Read sector 250375 [55:38:25]: mode 2 submode 0x64 into buffer 2
[  136.3816] D/CDROM: Read sector 250376 [55:38:26]: mode 2 submode 0x48 into buffer 2
[  136.3980] D/CDROM: Read sector 250377 [55:38:27]: mode 2 submode 0x48 into buffer 3
[  136.3985] D/CDROM: Read sector 250378 [55:38:28]: mode 2 submode 0x48 into buffer 4
[  136.4144] D/CDROM: Read sector 250379 [55:38:29]: mode 2 submode 0x48 into buffer 5
[  136.4147] D/CDROM: Read sector 250380 [55:38:30]: mode 2 submode 0x48 into buffer 6
[  136.4150] D/CDROM: Read sector 250381 [55:38:31]: mode 2 submode 0x48 into buffer 7
[  136.4312] D/CDROM: Read sector 250382 [55:38:32]: mode 2 submode 0x48 into buffer 0
[  136.4314] D/CDROM: Read sector 250383 [55:38:33]: mode 2 submode 0x64 into buffer 1
[  136.4481] D/CDROM: Read sector 250384 [55:38:34]: mode 2 submode 0x48 into buffer 1
[  136.4484] D/CDROM: Read sector 250385 [55:38:35]: mode 2 submode 0x48 into buffer 2
[  136.4487] D/CDROM: Read sector 250386 [55:38:36]: mode 2 submode 0x48 into buffer 3
[  136.4647] D/CDROM: Read sector 250387 [55:38:37]: mode 2 submode 0x48 into buffer 4
[  136.4651] D/CDROM: Read sector 250388 [55:38:38]: mode 2 submode 0x48 into buffer 5
[  136.4814] D/CDROM: Read sector 250389 [55:38:39]: mode 2 submode 0x48 into buffer 6
[  136.4817] D/CDROM: Read sector 250390 [55:38:40]: mode 2 submode 0x48 into buffer 7
[  136.4820] D/CDROM: Read sector 250391 [55:38:41]: mode 2 submode 0x64 into buffer 0
[  136.4985] D/CDROM: Read sector 250392 [55:38:42]: mode 2 submode 0x48 into buffer 0
[  136.4988] D/CDROM: Read sector 250393 [55:38:43]: mode 2 submode 0x48 into buffer 1
[  136.5146] D/CDROM: Read sector 250394 [55:38:44]: mode 2 submode 0x48 into buffer 2
[  136.5149] D/CDROM: Read sector 250395 [55:38:45]: mode 2 submode 0x48 into buffer 3
[  136.5153] D/CDROM: Read sector 250396 [55:38:46]: mode 2 submode 0x48 into buffer 4
[  136.5318] D/CDROM: Read sector 250397 [55:38:47]: mode 2 submode 0x48 into buffer 5
[  136.5322] D/CDROM: Read sector 250398 [55:38:48]: mode 2 submode 0x48 into buffer 6
[  136.5482] D/CDROM: Read sector 250399 [55:38:49]: mode 2 submode 0x64 into buffer 7
[  136.5486] D/CDROM: Read sector 250400 [55:38:50]: mode 2 submode 0x48 into buffer 7
[  136.5488] D/CDROM: Read sector 250401 [55:38:51]: mode 2 submode 0x48 into buffer 0
[  136.5648] D/CDROM: Read sector 250402 [55:38:52]: mode 2 submode 0x48 into buffer 1
[  136.5651] D/CDROM: Read sector 250403 [55:38:53]: mode 2 submode 0x48 into buffer 2
[  136.5818] D/CDROM: Read sector 250404 [55:38:54]: mode 2 submode 0x48 into buffer 3
[  136.5820] D/CDROM: Read sector 250405 [55:38:55]: mode 2 submode 0x48 into buffer 4
[  136.5820] D/CDROM: Read sector 250406 [55:38:56]: mode 2 submode 0x48 into buffer 5
[  136.5984] D/CDROM: Read sector 250407 [55:38:57]: mode 2 submode 0x64 into buffer 6
[  136.5990] D/CDROM: Read sector 250408 [55:38:58]: mode 2 submode 0x48 into buffer 6
[  136.6151] D/CDROM: Read sector 250409 [55:38:59]: mode 2 submode 0x48 into buffer 7
[  136.6154] D/CDROM: Read sector 250410 [55:38:60]: mode 2 submode 0x48 into buffer 0
[  136.6157] D/CDROM: Read sector 250411 [55:38:61]: mode 2 submode 0x48 into buffer 1
[  136.6321] D/CDROM: Read sector 250412 [55:38:62]: mode 2 submode 0x48 into buffer 2
[  136.6326] D/CDROM: Read sector 250413 [55:38:63]: mode 2 submode 0x48 into buffer 3
[  136.6481] D/CDROM: Read sector 250414 [55:38:64]: mode 2 submode 0x48 into buffer 4
[  136.6485] D/CDROM: Read sector 250415 [55:38:65]: mode 2 submode 0x64 into buffer 5
[  136.6489] D/CDROM: Read sector 250416 [55:38:66]: mode 2 submode 0x48 into buffer 5
[  136.6652] D/CDROM: Read sector 250417 [55:38:67]: mode 2 submode 0x48 into buffer 6
[  136.6655] D/CDROM: Read sector 250418 [55:38:68]: mode 2 submode 0x48 into buffer 7
[  136.6820] D/CDROM: Read sector 250419 [55:38:69]: mode 2 submode 0x48 into buffer 0
[  136.6823] D/CDROM: Read sector 250420 [55:38:70]: mode 2 submode 0x48 into buffer 1
[  136.6826] D/CDROM: Read sector 250421 [55:38:71]: mode 2 submode 0x48 into buffer 2
[  136.6987] D/CDROM: Read sector 250422 [55:38:72]: mode 2 submode 0x48 into buffer 3
[  136.6991] D/CDROM: Read sector 250423 [55:38:73]: mode 2 submode 0x64 into buffer 4
[  136.7153] D/CDROM: Read sector 250424 [55:38:74]: mode 2 submode 0x48 into buffer 4
[  136.7156] D/CDROM: Read sector 250425 [55:39:00]: mode 2 submode 0x48 into buffer 5
[  136.7160] D/CDROM: Read sector 250426 [55:39:01]: mode 2 submode 0x48 into buffer 6
[  136.7322] D/CDROM: Read sector 250427 [55:39:02]: mode 2 submode 0x48 into buffer 7
[  136.7326] D/CDROM: Read sector 250428 [55:39:03]: mode 2 submode 0x48 into buffer 0
[  136.7484] D/CDROM: Read sector 250429 [55:39:04]: mode 2 submode 0x48 into buffer 1
[  136.7487] D/CDROM: Read sector 250430 [55:39:05]: mode 2 submode 0x48 into buffer 2
[  136.7490] D/CDROM: Read sector 250431 [55:39:06]: mode 2 submode 0x64 into buffer 3
[  136.7654] D/CDROM: Read sector 250432 [55:39:07]: mode 2 submode 0x48 into buffer 3
[  136.7656] D/CDROM: Read sector 250433 [55:39:08]: mode 2 submode 0x48 into buffer 4
[  136.7820] D/CDROM: Read sector 250434 [55:39:09]: mode 2 submode 0x48 into buffer 5
[  136.7822] D/CDROM: Read sector 250435 [55:39:10]: mode 2 submode 0x48 into buffer 6
[  136.7823] D/CDROM: Read sector 250436 [55:39:11]: mode 2 submode 0x48 into buffer 7
[  136.7991] D/CDROM: Read sector 250437 [55:39:12]: mode 2 submode 0x48 into buffer 0
[  136.7995] D/CDROM: Read sector 250438 [55:39:13]: mode 2 submode 0x48 into buffer 1
[  136.8157] D/CDROM: Read sector 250439 [55:39:14]: mode 2 submode 0x64 into buffer 2
[  136.8161] D/CDROM: Read sector 250440 [55:39:15]: mode 2 submode 0x48 into buffer 2
[  136.8164] D/CDROM: Read sector 250441 [55:39:16]: mode 2 submode 0x48 into buffer 3
[  136.8323] D/CDROM: Read sector 250442 [55:39:17]: mode 2 submode 0x48 into buffer 4
[  136.8327] D/CDROM: Read sector 250443 [55:39:18]: mode 2 submode 0x48 into buffer 5
[  136.8489] D/CDROM: Read sector 250444 [55:39:19]: mode 2 submode 0x48 into buffer 6
[  136.8491] D/CDROM: Read sector 250445 [55:39:20]: mode 2 submode 0x48 into buffer 7
[  136.8492] D/CDROM: Read sector 250446 [55:39:21]: mode 2 submode 0x48 into buffer 0
[  136.8661] D/CDROM: Read sector 250447 [55:39:22]: mode 2 submode 0x64 into buffer 1
[  136.8666] D/CDROM: Read sector 250448 [55:39:23]: mode 2 submode 0x48 into buffer 1
[  136.8825] D/CDROM: Read sector 250449 [55:39:24]: mode 2 submode 0x48 into buffer 2
[  136.8831] D/CDROM: Read sector 250450 [55:39:25]: mode 2 submode 0x48 into buffer 3
[  136.8835] D/CDROM: Read sector 250451 [55:39:26]: mode 2 submode 0x48 into buffer 4
[  136.8999] D/CDROM: Read sector 250452 [55:39:27]: mode 2 submode 0x48 into buffer 5
[  136.9004] D/CDROM: Read sector 250453 [55:39:28]: mode 2 submode 0x48 into buffer 6
[  136.9160] D/CDROM: Read sector 250454 [55:39:29]: mode 2 submode 0x48 into buffer 7
[  136.9163] D/CDROM: Read sector 250455 [55:39:30]: mode 2 submode 0x64 into buffer 0
[  136.9169] D/CDROM: Read sector 250456 [55:39:31]: mode 2 submode 0x48 into buffer 0
[  136.9327] D/CDROM: Read sector 250457 [55:39:32]: mode 2 submode 0x48 into buffer 1
[  136.9330] D/CDROM: Read sector 250458 [55:39:33]: mode 2 submode 0x48 into buffer 2
[  136.9495] D/CDROM: Read sector 250459 [55:39:34]: mode 2 submode 0x48 into buffer 3
[  136.9498] D/CDROM: Read sector 250460 [55:39:35]: mode 2 submode 0x48 into buffer 4
[  136.9501] D/CDROM: Read sector 250461 [55:39:36]: mode 2 submode 0x48 into buffer 5
[  136.9660] D/CDROM: Read sector 250462 [55:39:37]: mode 2 submode 0x48 into buffer 6
[  136.9662] D/CDROM: Read sector 250463 [55:39:38]: mode 2 submode 0x64 into buffer 7
[  136.9831] D/CDROM: Read sector 250464 [55:39:39]: mode 2 submode 0x48 into buffer 7
[  136.9834] D/CDROM: Read sector 250465 [55:39:40]: mode 2 submode 0x48 into buffer 0
[  136.9838] D/CDROM: Read sector 250466 [55:39:41]: mode 2 submode 0x48 into buffer 1
[  136.9998] D/CDROM: Read sector 250467 [55:39:42]: mode 2 submode 0x48 into buffer 2
[  137.0001] D/CDROM: Read sector 250468 [55:39:43]: mode 2 submode 0x48 into buffer 3
[  137.0003] D/CDROM: Read sector 250469 [55:39:44]: mode 2 submode 0x48 into buffer 4
[  137.0162] D/CDROM: Read sector 250470 [55:39:45]: mode 2 submode 0x48 into buffer 5
[  137.0165] D/CDROM: Read sector 250471 [55:39:46]: mode 2 submode 0x64 into buffer 6
[  137.0328] D/CDROM: Read sector 250472 [55:39:47]: mode 2 submode 0x48 into buffer 6
[  137.0330] D/CDROM: Read sector 250473 [55:39:48]: mode 2 submode 0x48 into buffer 7
[  137.0332] D/CDROM: Read sector 250474 [55:39:49]: mode 2 submode 0x48 into buffer 0
[  137.0500] D/CDROM: Read sector 250475 [55:39:50]: mode 2 submode 0x48 into buffer 1
[  137.0502] D/CDROM: Read sector 250476 [55:39:51]: mode 2 submode 0x48 into buffer 2
[  137.0662] D/CDROM: Read sector 250477 [55:39:52]: mode 2 submode 0x48 into buffer 3
[  137.0665] D/CDROM: Read sector 250478 [55:39:53]: mode 2 submode 0x48 into buffer 4
[  137.0668] D/CDROM: Read sector 250479 [55:39:54]: mode 2 submode 0x64 into buffer 5
[  137.0835] D/CDROM: Read sector 250480 [55:39:55]: mode 2 submode 0x48 into buffer 5
[  137.0838] D/CDROM: Read sector 250481 [55:39:56]: mode 2 submode 0x48 into buffer 6
[  137.1001] D/CDROM: Read sector 250482 [55:39:57]: mode 2 submode 0x48 into buffer 7
[  137.1005] D/CDROM: Read sector 250483 [55:39:58]: mode 2 submode 0x48 into buffer 0
[  137.1007] D/CDROM: Read sector 250484 [55:39:59]: mode 2 submode 0x48 into buffer 1
[  137.1166] D/CDROM: Read sector 250485 [55:39:60]: mode 2 submode 0x48 into buffer 2
[  137.1167] D/CDROM: Read sector 250486 [55:39:61]: mode 2 submode 0x48 into buffer 3
[  137.1334] D/CDROM: Read sector 250487 [55:39:62]: mode 2 submode 0x64 into buffer 4
[  137.1338] D/CDROM: Read sector 250488 [55:39:63]: mode 2 submode 0x48 into buffer 4
[  137.1341] D/CDROM: Read sector 250489 [55:39:64]: mode 2 submode 0x48 into buffer 5
[  137.1504] D/CDROM: Read sector 250490 [55:39:65]: mode 2 submode 0x48 into buffer 6
[  137.1508] D/CDROM: Read sector 250491 [55:39:66]: mode 2 submode 0x48 into buffer 7
[  137.1665] D/CDROM: Read sector 250492 [55:39:67]: mode 2 submode 0x48 into buffer 0
[  137.1670] D/CDROM: Read sector 250493 [55:39:68]: mode 2 submode 0x48 into buffer 1
[  137.1673] D/CDROM: Read sector 250494 [55:39:69]: mode 2 submode 0x48 into buffer 2
[  137.1836] D/CDROM: Read sector 250495 [55:39:70]: mode 2 submode 0x64 into buffer 3
[  137.1841] D/CDROM: Read sector 250496 [55:39:71]: mode 2 submode 0x48 into buffer 3
[  137.2003] D/CDROM: Read sector 250497 [55:39:72]: mode 2 submode 0x48 into buffer 4
[  137.2007] D/CDROM: Read sector 250498 [55:39:73]: mode 2 submode 0x48 into buffer 5
[  137.2009] D/CDROM: Read sector 250499 [55:39:74]: mode 2 submode 0x48 into buffer 6
[  137.2172] D/CDROM: Read sector 250500 [55:40:00]: mode 2 submode 0x48 into buffer 7
[  137.2176] D/CDROM: Read sector 250501 [55:40:01]: mode 2 submode 0x48 into buffer 0
[  137.2334] D/CDROM: Read sector 250502 [55:40:02]: mode 2 submode 0x48 into buffer 1
[  137.2336] D/CDROM: Read sector 250503 [55:40:03]: mode 2 submode 0x64 into buffer 2
[  137.2340] D/CDROM: Read sector 250504 [55:40:04]: mode 2 submode 0x48 into buffer 2
[  137.2505] D/CDROM: Read sector 250505 [55:40:05]: mode 2 submode 0x48 into buffer 3
[  137.2509] D/CDROM: Read sector 250506 [55:40:06]: mode 2 submode 0x48 into buffer 4
[  137.2669] V/PerfMon: FPS: 14.96 VPS: 59.83 CPU: 5.65 GPU: 0.00 Avg: 16.72ms Min: 16.12ms Max: 17.19ms
[  137.2671] D/CDROM: Read sector 250507 [55:40:07]: mode 2 submode 0x48 into buffer 5
[  137.2674] D/CDROM: Read sector 250508 [55:40:08]: mode 2 submode 0x48 into buffer 6
[  137.2676] D/CDROM: Read sector 250509 [55:40:09]: mode 2 submode 0x48 into buffer 7
[  137.2840] D/CDROM: Read sector 250510 [55:40:10]: mode 2 submode 0x48 into buffer 0
[  137.2843] D/CDROM: Read sector 250511 [55:40:11]: mode 2 submode 0x64 into buffer 1
[  137.3006] D/CDROM: Read sector 250512 [55:40:12]: mode 2 submode 0x48 into buffer 1
[  137.3008] D/CDROM: Read sector 250513 [55:40:13]: mode 2 submode 0x48 into buffer 2
[  137.3010] D/CDROM: Read sector 250514 [55:40:14]: mode 2 submode 0x48 into buffer 3
[  137.3174] D/CDROM: Read sector 250515 [55:40:15]: mode 2 submode 0x48 into buffer 4
[  137.3179] D/CDROM: Read sector 250516 [55:40:16]: mode 2 submode 0x48 into buffer 5
[  137.3338] D/CDROM: Read sector 250517 [55:40:17]: mode 2 submode 0x48 into buffer 6
[  137.3342] D/CDROM: Read sector 250518 [55:40:18]: mode 2 submode 0x48 into buffer 7
[  137.3344] D/CDROM: Read sector 250519 [55:40:19]: mode 2 submode 0x64 into buffer 0
[  137.3505] D/CDROM: Read sector 250520 [55:40:20]: mode 2 submode 0x48 into buffer 0
[  137.3509] D/CDROM: Read sector 250521 [55:40:21]: mode 2 submode 0x48 into buffer 1
[  137.3669] D/CDROM: Read sector 250522 [55:40:22]: mode 2 submode 0x48 into buffer 2
[  137.3672] D/CDROM: Read sector 250523 [55:40:23]: mode 2 submode 0x48 into buffer 3
[  137.3673] D/CDROM: Read sector 250524 [55:40:24]: mode 2 submode 0x48 into buffer 4
[  137.3840] D/CDROM: Read sector 250525 [55:40:25]: mode 2 submode 0x48 into buffer 5
[  137.3844] D/CDROM: Read sector 250526 [55:40:26]: mode 2 submode 0x48 into buffer 6
[  137.4008] D/CDROM: Read sector 250527 [55:40:27]: mode 2 submode 0x64 into buffer 7
[  137.4013] D/CDROM: Read sector 250528 [55:40:28]: mode 2 submode 0x48 into buffer 7
[  137.4015] D/CDROM: Read sector 250529 [55:40:29]: mode 2 submode 0x48 into buffer 0
[  137.4175] D/CDROM: Read sector 250530 [55:40:30]: mode 2 submode 0x48 into buffer 1
[  137.4179] D/CDROM: Read sector 250531 [55:40:31]: mode 2 submode 0x48 into buffer 2
[  137.4342] D/CDROM: Read sector 250532 [55:40:32]: mode 2 submode 0x48 into buffer 3
[  137.4344] D/CDROM: Read sector 250533 [55:40:33]: mode 2 submode 0x48 into buffer 4
[  137.4345] D/CDROM: Read sector 250534 [55:40:34]: mode 2 submode 0x48 into buffer 5
[  137.4512] D/CDROM: Read sector 250535 [55:40:35]: mode 2 submode 0x64 into buffer 6
[  137.4517] D/CDROM: Read sector 250536 [55:40:36]: mode 2 submode 0x48 into buffer 6
[  137.4678] D/CDROM: Read sector 250537 [55:40:37]: mode 2 submode 0x48 into buffer 7
[  137.4681] D/CDROM: Read sector 250538 [55:40:38]: mode 2 submode 0x48 into buffer 0
[  137.4684] D/CDROM: Read sector 250539 [55:40:39]: mode 2 submode 0x48 into buffer 1
[  137.4843] D/CDROM: Read sector 250540 [55:40:40]: mode 2 submode 0x48 into buffer 2
[  137.4846] D/CDROM: Read sector 250541 [55:40:41]: mode 2 submode 0x48 into buffer 3
[  137.5009] D/CDROM: Read sector 250542 [55:40:42]: mode 2 submode 0x48 into buffer 4
[  137.5011] D/CDROM: Read sector 250543 [55:40:43]: mode 2 submode 0x64 into buffer 5
[  137.5014] D/CDROM: Read sector 250544 [55:40:44]: mode 2 submode 0x48 into buffer 5
[  137.5178] D/CDROM: Read sector 250545 [55:40:45]: mode 2 submode 0x48 into buffer 6
[  137.5183] D/CDROM: Read sector 250546 [55:40:46]: mode 2 submode 0x48 into buffer 7
[  137.5343] D/CDROM: Read sector 250547 [55:40:47]: mode 2 submode 0x48 into buffer 0
[  137.5346] D/CDROM: Read sector 250548 [55:40:48]: mode 2 submode 0x48 into buffer 1
[  137.5351] D/CDROM: Read sector 250549 [55:40:49]: mode 2 submode 0x48 into buffer 2
[  137.5512] D/CDROM: Read sector 250550 [55:40:50]: mode 2 submode 0x48 into buffer 3
[  137.5516] D/CDROM: Read sector 250551 [55:40:51]: mode 2 submode 0x64 into buffer 4
[  137.5678] D/CDROM: Read sector 250552 [55:40:52]: mode 2 submode 0x48 into buffer 4
[  137.5680] D/CDROM: Read sector 250553 [55:40:53]: mode 2 submode 0x48 into buffer 5
[  137.5682] D/CDROM: Read sector 250554 [55:40:54]: mode 2 submode 0x48 into buffer 6
[  137.5850] D/CDROM: Read sector 250555 [55:40:55]: mode 2 submode 0x48 into buffer 7
[  137.5854] D/CDROM: Read sector 250556 [55:40:56]: mode 2 submode 0x48 into buffer 0
[  137.6012] D/CDROM: Read sector 250557 [55:40:57]: mode 2 submode 0x48 into buffer 1
[  137.6015] D/CDROM: Read sector 250558 [55:40:58]: mode 2 submode 0x48 into buffer 2
[  137.6018] D/CDROM: Read sector 250559 [55:40:59]: mode 2 submode 0x64 into buffer 3
[  137.6183] D/CDROM: Read sector 250560 [55:40:60]: mode 2 submode 0x48 into buffer 3
[  137.6187] D/CDROM: Read sector 250561 [55:40:61]: mode 2 submode 0x48 into buffer 4
[  137.6349] D/CDROM: Read sector 250562 [55:40:62]: mode 2 submode 0x48 into buffer 5
[  137.6351] D/CDROM: Read sector 250563 [55:40:63]: mode 2 submode 0x48 into buffer 6
[  137.6353] D/CDROM: Read sector 250564 [55:40:64]: mode 2 submode 0x48 into buffer 7
[  137.6515] D/CDROM: Read sector 250565 [55:40:65]: mode 2 submode 0x48 into buffer 0
[  137.6519] D/CDROM: Read sector 250566 [55:40:66]: mode 2 submode 0x48 into buffer 1
[  137.6684] D/CDROM: Read sector 250567 [55:40:67]: mode 2 submode 0x64 into buffer 2
[  137.6688] D/CDROM: Read sector 250568 [55:40:68]: mode 2 submode 0x48 into buffer 2
[  137.6691] D/CDROM: Read sector 250569 [55:40:69]: mode 2 submode 0x48 into buffer 3
[  137.6850] D/CDROM: Read sector 250570 [55:40:70]: mode 2 submode 0x48 into buffer 4
[  137.6853] D/CDROM: Read sector 250571 [55:40:71]: mode 2 submode 0x48 into buffer 5
[  137.7014] D/CDROM: Read sector 250572 [55:40:72]: mode 2 submode 0x48 into buffer 6
[  137.7016] D/CDROM: Read sector 250573 [55:40:73]: mode 2 submode 0x48 into buffer 7
[  137.7017] D/CDROM: Read sector 250574 [55:40:74]: mode 2 submode 0x48 into buffer 0
[  137.7185] D/CDROM: Read sector 250575 [55:41:00]: mode 2 submode 0x64 into buffer 1
[  137.7191] D/CDROM: Read sector 250576 [55:41:01]: mode 2 submode 0x48 into buffer 1
[  137.7353] D/CDROM: Read sector 250577 [55:41:02]: mode 2 submode 0x48 into buffer 2
[  137.7356] D/CDROM: Read sector 250578 [55:41:03]: mode 2 submode 0x48 into buffer 3
[  137.7359] D/CDROM: Read sector 250579 [55:41:04]: mode 2 submode 0x48 into buffer 4
[  137.7522] D/CDROM: Read sector 250580 [55:41:05]: mode 2 submode 0x48 into buffer 5
[  137.7526] D/CDROM: Read sector 250581 [55:41:06]: mode 2 submode 0x48 into buffer 6
[  137.7686] D/CDROM: Read sector 250582 [55:41:07]: mode 2 submode 0x48 into buffer 7
[  137.7688] D/CDROM: Read sector 250583 [55:41:08]: mode 2 submode 0x64 into buffer 0
[  137.7690] D/CDROM: Read sector 250584 [55:41:09]: mode 2 submode 0x48 into buffer 0
[  137.7856] D/CDROM: Read sector 250585 [55:41:10]: mode 2 submode 0x48 into buffer 1
[  137.7859] D/CDROM: Read sector 250586 [55:41:11]: mode 2 submode 0x48 into buffer 2
[  137.8020] D/CDROM: Read sector 250587 [55:41:12]: mode 2 submode 0x48 into buffer 3
[  137.8024] D/CDROM: Read sector 250588 [55:41:13]: mode 2 submode 0x48 into buffer 4
[  137.8026] D/CDROM: Read sector 250589 [55:41:14]: mode 2 submode 0x48 into buffer 5
[  137.8189] D/CDROM: Read sector 250590 [55:41:15]: mode 2 submode 0x48 into buffer 6
[  137.8193] D/CDROM: Read sector 250591 [55:41:16]: mode 2 submode 0x64 into buffer 7
[  137.8360] D/CDROM: Read sector 250592 [55:41:17]: mode 2 submode 0x48 into buffer 7
[  137.8363] D/CDROM: Read sector 250593 [55:41:18]: mode 2 submode 0x48 into buffer 0
[  137.8364] D/CDROM: Read sector 250594 [55:41:19]: mode 2 submode 0x48 into buffer 1
[  137.8523] D/CDROM: Read sector 250595 [55:41:20]: mode 2 submode 0x48 into buffer 2
[  137.8526] D/CDROM: Read sector 250596 [55:41:21]: mode 2 submode 0x48 into buffer 3
[  137.8686] D/CDROM: Read sector 250597 [55:41:22]: mode 2 submode 0x48 into buffer 4
[  137.8690] D/CDROM: Read sector 250598 [55:41:23]: mode 2 submode 0x48 into buffer 5
[  137.8692] D/CDROM: Read sector 250599 [55:41:24]: mode 2 submode 0x64 into buffer 6
[  137.8856] D/CDROM: Read sector 250600 [55:41:25]: mode 2 submode 0x42 into buffer 6
[  137.8862] D/CDROM: Read sector 250601 [55:41:26]: mode 2 submode 0x42 into buffer 7
[  137.9020] D/CDROM: Read sector 250602 [55:41:27]: mode 2 submode 0x42 into buffer 0
[  137.9021] D/CDROM: Read sector 250603 [55:41:28]: mode 2 submode 0x42 into buffer 1
[  137.9023] D/CDROM: Read sector 250604 [55:41:29]: mode 2 submode 0x42 into buffer 2
[  137.9190] D/CDROM: Read sector 250605 [55:41:30]: mode 2 submode 0x42 into buffer 3
[  137.9192] D/CDROM: Read sector 250606 [55:41:31]: mode 2 submode 0x42 into buffer 4
[  137.9355] D/CDROM: Read sector 250607 [55:41:32]: mode 2 submode 0x64 into buffer 5
[  137.9357] D/CDROM: Read sector 250608 [55:41:33]: mode 2 submode 0x42 into buffer 5
[  137.9358] D/CDROM: Read sector 250609 [55:41:34]: mode 2 submode 0x42 into buffer 6
[  137.9522] D/CDROM: Read sector 250610 [55:41:35]: mode 2 submode 0x42 into buffer 7
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
[  144.2885] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 2.92 GPU: 0.00 Avg: 16.72ms Min: 16.12ms Max: 17.28ms
[  147.1408] V/AudioStream: Audio buffer underflow, resampled 279 frames to 441
[  147.1526] V/PerfMon: FPS: 0.00 VPS: 0.35 CPU: 0.16 GPU: 0.00 Avg: 2864.07ms Min: 2864.07ms Max: 2864.07ms
[  147.1531] V/AudioStream: ~~~ Stretcher is now active @ tempo 0.8314514.
[  147.1604] V/AudioStream: Underrun compensation done (128 frames buffered)
[  147.5986] V/AudioStream: === Stretcher is now inactive.
[  148.1666] V/PerfMon: FPS: 30.57 VPS: 61.14 CPU: 3.01 GPU: 0.00 Avg: 16.36ms Min: 0.72ms Max: 17.37ms
[  149.1696] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 2.97 GPU: 0.00 Avg: 16.72ms Min: 15.97ms Max: 17.46ms
[  150.1726] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.08 GPU: 0.00 Avg: 16.72ms Min: 16.25ms Max: 17.36ms
[  151.1763] V/PerfMon: FPS: 29.89 VPS: 59.78 CPU: 3.15 GPU: 0.00 Avg: 16.73ms Min: 16.18ms Max: 17.36ms
[  152.1791] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 3.34 GPU: 0.00 Avg: 16.71ms Min: 16.11ms Max: 17.50ms
[  153.1818] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.41 GPU: 0.00 Avg: 16.71ms Min: 16.07ms Max: 17.79ms
[  154.1848] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.26 GPU: 0.00 Avg: 16.72ms Min: 15.88ms Max: 17.31ms
[  155.1881] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.25 GPU: 0.00 Avg: 16.72ms Min: 15.95ms Max: 17.39ms
[  156.1910] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.34 GPU: 0.00 Avg: 16.71ms Min: 15.97ms Max: 17.39ms
[  157.1940] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.71 GPU: 0.00 Avg: 16.72ms Min: 10.45ms Max: 22.92ms
[  158.1971] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.40 GPU: 0.00 Avg: 16.72ms Min: 15.94ms Max: 17.54ms
[  159.2001] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.34 GPU: 0.00 Avg: 16.72ms Min: 16.03ms Max: 17.28ms
[  160.2037] V/PerfMon: FPS: 29.89 VPS: 59.78 CPU: 3.33 GPU: 0.00 Avg: 16.73ms Min: 16.13ms Max: 17.36ms
[  161.2063] V/PerfMon: FPS: 29.92 VPS: 59.85 CPU: 3.29 GPU: 0.00 Avg: 16.71ms Min: 16.09ms Max: 17.20ms
[  161.6413] D/CodeCache: Breaking block 0x80031FF0 at 0x80032000 due to page crossing
[  162.2099] V/PerfMon: FPS: 29.89 VPS: 59.78 CPU: 3.35 GPU: 0.00 Avg: 16.73ms Min: 16.19ms Max: 17.49ms
[  163.2126] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.45 GPU: 0.00 Avg: 16.71ms Min: 16.07ms Max: 17.17ms
[  164.2207] V/PerfMon: FPS: 29.76 VPS: 59.52 CPU: 3.71 GPU: 0.00 Avg: 16.80ms Min: 11.41ms Max: 22.61ms
[  165.2350] V/PerfMon: FPS: 30.56 VPS: 60.14 CPU: 3.65 GPU: 0.00 Avg: 16.63ms Min: 12.02ms Max: 17.39ms
[  166.2381] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.46 GPU: 0.00 Avg: 16.72ms Min: 13.47ms Max: 19.95ms
[  167.2415] V/PerfMon: FPS: 29.90 VPS: 59.79 CPU: 3.30 GPU: 0.00 Avg: 16.72ms Min: 16.07ms Max: 17.39ms
[  168.2442] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.34 GPU: 0.00 Avg: 16.71ms Min: 15.73ms Max: 17.86ms
[  169.2476] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.46 GPU: 0.00 Avg: 16.72ms Min: 16.14ms Max: 17.23ms
[  170.2507] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 3.34 GPU: 0.00 Avg: 16.72ms Min: 16.08ms Max: 17.31ms
[  171.2534] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.36 GPU: 0.00 Avg: 16.71ms Min: 16.00ms Max: 17.22ms
[  172.2564] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.53 GPU: 0.00 Avg: 16.72ms Min: 16.08ms Max: 17.34ms
[  173.2600] V/PerfMon: FPS: 29.89 VPS: 59.79 CPU: 3.46 GPU: 0.00 Avg: 16.73ms Min: 16.02ms Max: 17.38ms
[  174.2628] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.47 GPU: 0.00 Avg: 16.71ms Min: 16.06ms Max: 17.34ms
[  175.2657] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.44 GPU: 0.00 Avg: 16.72ms Min: 16.20ms Max: 17.76ms
[  176.2690] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.34 GPU: 0.00 Avg: 16.72ms Min: 16.12ms Max: 17.29ms
[  177.2722] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.33 GPU: 0.00 Avg: 16.72ms Min: 16.19ms Max: 17.22ms
[  178.2747] V/PerfMon: FPS: 29.93 VPS: 59.85 CPU: 3.25 GPU: 0.00 Avg: 16.71ms Min: 16.25ms Max: 17.39ms
[  179.2779] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.45 GPU: 0.00 Avg: 16.72ms Min: 16.03ms Max: 17.95ms
[  180.2808] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.99 GPU: 0.00 Avg: 16.72ms Min: 15.97ms Max: 17.46ms
[  181.2844] V/PerfMon: FPS: 29.89 VPS: 59.79 CPU: 3.51 GPU: 0.00 Avg: 16.73ms Min: 16.31ms Max: 17.32ms
[  182.2873] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 2.98 GPU: 0.00 Avg: 16.71ms Min: 16.00ms Max: 17.41ms
[  183.2905] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 2.96 GPU: 0.00 Avg: 16.72ms Min: 16.38ms Max: 17.27ms
[  184.2930] V/PerfMon: FPS: 29.92 VPS: 59.85 CPU: 3.27 GPU: 0.00 Avg: 16.71ms Min: 15.96ms Max: 17.43ms
[  185.2966] V/PerfMon: FPS: 29.89 VPS: 59.78 CPU: 3.28 GPU: 0.00 Avg: 16.73ms Min: 15.99ms Max: 17.49ms
[  186.2993] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.14 GPU: 0.00 Avg: 16.71ms Min: 16.23ms Max: 17.26ms
[  187.3025] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.14 GPU: 0.00 Avg: 16.72ms Min: 16.31ms Max: 17.16ms
[  188.3055] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.06 GPU: 0.00 Avg: 16.72ms Min: 16.01ms Max: 17.32ms
[  189.3083] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 3.03 GPU: 0.00 Avg: 16.71ms Min: 16.13ms Max: 17.32ms
[  190.3114] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.04 GPU: 0.00 Avg: 16.72ms Min: 16.20ms Max: 17.26ms
[  191.3148] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.00 GPU: 0.00 Avg: 16.72ms Min: 16.13ms Max: 17.31ms
[  192.3174] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.04 GPU: 0.00 Avg: 16.71ms Min: 16.02ms Max: 17.51ms
[  193.3207] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.06 GPU: 0.00 Avg: 16.72ms Min: 16.20ms Max: 17.36ms
[  194.3241] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.06 GPU: 0.00 Avg: 16.72ms Min: 15.99ms Max: 17.45ms
[  195.3269] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 3.20 GPU: 0.00 Avg: 16.71ms Min: 16.20ms Max: 17.11ms
[  196.3301] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.06 GPU: 0.00 Avg: 16.72ms Min: 16.07ms Max: 17.35ms
[  197.3328] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 2.99 GPU: 0.00 Avg: 16.71ms Min: 16.03ms Max: 17.72ms
[  198.3359] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 3.00 GPU: 0.00 Avg: 16.72ms Min: 16.04ms Max: 17.30ms
[  199.3388] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.12 GPU: 0.00 Avg: 16.71ms Min: 16.22ms Max: 17.18ms
[  200.3421] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.02 GPU: 0.00 Avg: 16.72ms Min: 16.18ms Max: 17.19ms
[  201.3450] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.02 GPU: 0.00 Avg: 16.72ms Min: 16.20ms Max: 17.17ms
[  202.3481] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 3.17 GPU: 0.00 Avg: 16.72ms Min: 16.21ms Max: 17.20ms
[  203.3513] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 3.03 GPU: 0.00 Avg: 16.72ms Min: 16.17ms Max: 17.23ms
[  204.3541] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.02 GPU: 0.00 Avg: 16.71ms Min: 15.86ms Max: 17.63ms
[  205.3573] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 2.99 GPU: 0.00 Avg: 16.72ms Min: 16.16ms Max: 17.22ms
[  206.3607] V/PerfMon: FPS: 29.90 VPS: 59.79 CPU: 3.04 GPU: 0.00 Avg: 16.72ms Min: 16.00ms Max: 17.70ms
[  207.3632] V/PerfMon: FPS: 29.92 VPS: 59.85 CPU: 3.01 GPU: 0.00 Avg: 16.71ms Min: 15.75ms Max: 17.58ms
[  208.3664] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 3.05 GPU: 0.00 Avg: 16.72ms Min: 15.99ms Max: 17.39ms
[  209.3693] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.01 GPU: 0.00 Avg: 16.72ms Min: 16.34ms Max: 17.13ms
[  210.3724] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.13 GPU: 0.00 Avg: 16.72ms Min: 16.15ms Max: 17.21ms
[  211.3754] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.06 GPU: 0.00 Avg: 16.72ms Min: 15.99ms Max: 17.53ms
[  212.3784] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.07 GPU: 0.00 Avg: 16.72ms Min: 16.11ms Max: 17.25ms
[  213.3815] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 3.11 GPU: 0.00 Avg: 16.72ms Min: 15.91ms Max: 17.47ms
[  214.3850] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.20 GPU: 0.00 Avg: 16.72ms Min: 16.16ms Max: 17.53ms
[  215.3878] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 3.22 GPU: 0.00 Avg: 16.71ms Min: 16.29ms Max: 17.18ms
[  216.3910] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.21 GPU: 0.00 Avg: 16.72ms Min: 16.29ms Max: 17.09ms
[  217.3942] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.19 GPU: 0.00 Avg: 16.72ms Min: 15.92ms Max: 17.47ms
[  218.3972] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.08 GPU: 0.00 Avg: 16.72ms Min: 16.18ms Max: 17.12ms
[  219.3998] V/PerfMon: FPS: 29.92 VPS: 59.85 CPU: 3.04 GPU: 0.00 Avg: 16.71ms Min: 16.11ms Max: 17.39ms
[  220.4033] V/PerfMon: FPS: 29.89 VPS: 59.79 CPU: 3.13 GPU: 0.00 Avg: 16.73ms Min: 16.09ms Max: 17.42ms
[  221.4063] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.20 GPU: 0.00 Avg: 16.72ms Min: 16.27ms Max: 17.35ms
[  222.4093] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.21 GPU: 0.00 Avg: 16.72ms Min: 16.19ms Max: 17.31ms
[  223.4124] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.06 GPU: 0.00 Avg: 16.72ms Min: 16.16ms Max: 17.16ms
[  224.4154] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.01 GPU: 0.00 Avg: 16.72ms Min: 16.28ms Max: 17.18ms
[  225.4183] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.13 GPU: 0.00 Avg: 16.71ms Min: 16.23ms Max: 17.24ms
[  226.4213] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.12 GPU: 0.00 Avg: 16.72ms Min: 16.12ms Max: 17.62ms
[  227.4244] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 3.14 GPU: 0.00 Avg: 16.72ms Min: 15.93ms Max: 17.96ms
[  228.4275] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 3.00 GPU: 0.00 Avg: 16.72ms Min: 15.99ms Max: 17.34ms
[  229.4307] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.02 GPU: 0.00 Avg: 16.72ms Min: 16.19ms Max: 17.18ms
[  230.4337] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 2.98 GPU: 0.00 Avg: 16.72ms Min: 16.22ms Max: 17.33ms
[  231.4365] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 2.97 GPU: 0.00 Avg: 16.71ms Min: 16.26ms Max: 17.07ms
[  232.4396] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 3.22 GPU: 0.00 Avg: 16.72ms Min: 16.15ms Max: 17.48ms
[  233.4428] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.13 GPU: 0.00 Avg: 16.72ms Min: 16.08ms Max: 17.20ms
[  234.4456] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 3.04 GPU: 0.00 Avg: 16.71ms Min: 16.12ms Max: 17.30ms
[  235.4490] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.15 GPU: 0.00 Avg: 16.72ms Min: 15.87ms Max: 17.53ms
[  236.4522] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.09 GPU: 0.00 Avg: 16.72ms Min: 16.06ms Max: 17.29ms
[  237.4552] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.07 GPU: 0.00 Avg: 16.72ms Min: 16.04ms Max: 17.23ms
[  238.4581] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.12 GPU: 0.00 Avg: 16.72ms Min: 16.10ms Max: 17.30ms
[  239.4613] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.19 GPU: 0.00 Avg: 16.72ms Min: 16.12ms Max: 17.20ms
[  240.4640] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.46 GPU: 0.00 Avg: 16.71ms Min: 15.77ms Max: 17.72ms
[  241.4672] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.25 GPU: 0.00 Avg: 16.72ms Min: 15.53ms Max: 17.74ms
[  243.6823] V/AudioStream: Audio buffer underflow, resampled 302 frames to 441
[  243.6836] V/AudioStream: ___ Stretcher is being reset.
[  243.6837] V/AudioStream: Underrun compensation done (128 frames buffered)
[  243.6862] V/PerfMon: FPS: 0.00 VPS: 0.45 CPU: 0.11 GPU: 0.00 Avg: 2219.03ms Min: 2219.03ms Max: 2219.03ms
[  244.1924] V/AudioStream: === Stretcher is now inactive.
[  244.6936] V/PerfMon: FPS: 30.77 VPS: 60.55 CPU: 3.16 GPU: 0.00 Avg: 16.52ms Min: 4.30ms Max: 17.25ms
[  245.6969] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.16 GPU: 0.00 Avg: 16.72ms Min: 15.96ms Max: 17.44ms
[  246.6999] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.15 GPU: 0.00 Avg: 16.72ms Min: 16.15ms Max: 17.18ms
[  247.7024] V/PerfMon: FPS: 29.92 VPS: 59.85 CPU: 3.24 GPU: 0.00 Avg: 16.71ms Min: 15.84ms Max: 17.61ms
[  248.7059] V/PerfMon: FPS: 29.89 VPS: 59.79 CPU: 3.27 GPU: 0.00 Avg: 16.73ms Min: 16.08ms Max: 17.55ms
[  249.7088] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.06 GPU: 0.00 Avg: 16.72ms Min: 16.12ms Max: 17.48ms
[  250.7124] V/PerfMon: FPS: 29.89 VPS: 59.79 CPU: 3.14 GPU: 0.00 Avg: 16.73ms Min: 15.29ms Max: 18.42ms
[  251.7152] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 3.16 GPU: 0.00 Avg: 16.71ms Min: 15.91ms Max: 17.32ms
[  258.1869] V/AudioStream: Audio buffer underflow, resampled 316 frames to 441
[  258.1903] V/AudioStream: Underrun compensation done (128 frames buffered)
[  258.1930] V/PerfMon: FPS: 0.00 VPS: 0.15 CPU: 0.08 GPU: 0.00 Avg: 6477.79ms Min: 6477.79ms Max: 6477.79ms
[  258.1933] V/AudioStream: ~~~ Stretcher is now active @ tempo 0.8270008.
[  258.7698] V/AudioStream: === Stretcher is now inactive.
[  259.2047] V/PerfMon: FPS: 30.64 VPS: 60.30 CPU: 3.23 GPU: 0.00 Avg: 16.58ms Min: 8.28ms Max: 17.18ms
[  260.2075] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 3.15 GPU: 0.00 Avg: 16.71ms Min: 15.90ms Max: 17.54ms
[  261.2104] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.11 GPU: 0.00 Avg: 16.72ms Min: 16.00ms Max: 17.52ms
[  262.2134] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.20 GPU: 0.00 Avg: 16.72ms Min: 16.06ms Max: 17.19ms
[  263.2163] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.40 GPU: 0.00 Avg: 16.72ms Min: 15.82ms Max: 17.58ms
[  264.2195] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.19 GPU: 0.00 Avg: 16.72ms Min: 15.88ms Max: 17.25ms
[  265.2227] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.18 GPU: 0.00 Avg: 16.72ms Min: 16.28ms Max: 17.25ms
[  266.2256] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.24 GPU: 0.00 Avg: 16.71ms Min: 16.04ms Max: 17.38ms
[  267.2291] V/PerfMon: FPS: 29.90 VPS: 59.79 CPU: 3.32 GPU: 0.00 Avg: 16.73ms Min: 16.18ms Max: 17.21ms
[  268.2315] V/PerfMon: FPS: 29.93 VPS: 59.85 CPU: 3.22 GPU: 0.00 Avg: 16.71ms Min: 16.21ms Max: 17.15ms
[  269.2346] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.19 GPU: 0.00 Avg: 16.72ms Min: 16.15ms Max: 17.23ms
[  270.2377] V/PerfMon: FPS: 29.91 VPS: 59.81 CPU: 3.36 GPU: 0.00 Avg: 16.72ms Min: 15.68ms Max: 17.74ms
[  271.2408] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.55 GPU: 0.00 Avg: 16.72ms Min: 15.70ms Max: 17.69ms
[  272.2441] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.27 GPU: 0.00 Avg: 16.72ms Min: 16.10ms Max: 17.40ms
[  273.2474] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.28 GPU: 0.00 Avg: 16.72ms Min: 16.18ms Max: 17.16ms
[  273.7840] V/AudioStream: Audio buffer underflow, resampled 313 frames to 441
[  273.7849] V/AudioStream: Underrun compensation done (128 frames buffered)
[  273.7991] V/AudioStream: ~~~ Stretcher is now active @ tempo 0.8277345.
[  274.2503] V/PerfMon: FPS: 13.96 VPS: 28.92 CPU: 1.67 GPU: 0.00 Avg: 34.58ms Min: 13.10ms Max: 538.46ms
[  274.3172] V/AudioStream: === Stretcher is now inactive.
[  275.2533] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.28 GPU: 0.00 Avg: 16.72ms Min: 16.14ms Max: 17.26ms
[  276.2561] V/PerfMon: FPS: 29.91 VPS: 59.83 CPU: 3.24 GPU: 0.00 Avg: 16.71ms Min: 16.27ms Max: 17.15ms
