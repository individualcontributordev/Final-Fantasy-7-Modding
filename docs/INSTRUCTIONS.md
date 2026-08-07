# Task: ending credits test v4 (no LASTMAP.BIN)

## Why v3 froze (MDEC crash)

DuckStation log (pasted earlier into this file) showed:

- `Invalid MDEC command …`
- then page fault at `0x00000000`

Cause: we injected Disc 3 **`LASTMAP.BIN`** into **MOVIE_ID row 23**.

That file is **Form1 data** (submode `0x08`), not a Form2 FMV.  
LASTMAP’s first play path does `PMVIE 23` then `MOVIE` → MDEC fed garbage → freeze.

PMVIE indexes **`MINT/MOVIE_ID.BIN` row numbers**, same on Disc 1 and Disc 3 for the
ending range. The mistake was **bytes**, not “wrong disc’s id table.”

## What v4 does

1. Restore pristine **LASTMAP.DAT** / **LAS4_0.DAT** (ending Play ops).  
2. Inject **only Form2** Disc 3 streams (engine size = D3, usually ×2336):

| MOVIE_ID id | Disc 3 file | Role |
|------------:|-------------|------|
| 24 | LASTFLOR.MOV | LASTMAP final FMV |
| 25 | ENDING01.MOV | LAS4_0 |
| 26 | ENDING3E.MOV | ending |
| 29 | ENDING2E.MOV | long credits |

3. **Do not** put LASTMAP.BIN on id 23. Id 23 stays Disc 1’s **ONTRAIN** FMV  
   (harmless short clip if the first `PMVIE 23` path runs).

Still **~1.0 GB** — DuckStation only.

## What you do

1. Pull  
2. Open ending-test cue (rebuild if missing)  
3. LASTMAP → after final battle / credits  
4. Reply: freeze? what FMV? sound?  

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

Bin size **1008274176**.

Not the normal playtest cue.

---

## 2. Rebuild if needed

```bash
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

---

## 3. Smoke

- Should **not** MDEC-crash / hard freeze on LASTMAP entry movies  
- Expect LASTFLOR + ENDING* (not random Midgar junk forever)  
- Note any short ONTRAIN blip from id 23  

---

## 4. Reply

1. Bin size  
2. What played  
3. Freeze yes/no · sound yes/no  

 1939.9937] D/CDROM: Read sector 162225 [36:03:00]: mode 2 submode 0x64 into buffer 0
[ 1939.9945] D/CDROM: Read sector 162226 [36:03:01]: mode 2 submode 0x42 into buffer 1
[ 1939.9946] D/CDROM: Read sector 162227 [36:03:02]: mode 2 submode 0x42 into buffer 2
[ 1939.9950] D/CDROM: Read sector 162228 [36:03:03]: mode 2 submode 0x42 into buffer 3
[ 1939.9963] D/CDROM: Read sector 162229 [36:03:04]: mode 2 submode 0x42 into buffer 4
[ 1939.9973] D/CDROM: Read sector 162230 [36:03:05]: mode 2 submode 0x42 into buffer 5
[ 1939.9974] D/CDROM: CDROM executing command 0x09 (Pause), stat = 0x22, params = []
[ 1940.0353] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0406] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0437] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0452] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0505] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0540] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0566] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0618] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0636] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0668] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0720] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0739] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0767] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0815] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0840] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0868] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0918] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0940] V/AudioStream: ___ Stretcher is being reset.
[ 1940.0985] V/AudioStream: ___ Stretcher is being reset.
[ 1940.1021] V/AudioStream: ___ Stretcher is being reset.
[ 1940.1039] V/AudioStream: ___ Stretcher is being reset.
[ 1940.1050] V/System: Target speed: 100%
[ 1940.1051] V/System: Preset timing: immediate
[ 1940.1052] V/System: VSync: Disabled
[ 1940.2227] V/System: Target speed: 1000%
[ 1940.2228] V/System: Preset timing: immediate
[ 1940.2234] V/System: VSync: Disabled (present throttle allowed)
[ 1940.6418] V/System: Target speed: 100%
[ 1940.6420] V/System: Preset timing: immediate
[ 1940.6426] V/System: VSync: Disabled
[ 1940.7430] V/PerfMon: FPS: 176.91 VPS: 354.82 CPU: 13.70 GPU: 0.00 Avg: 2.82ms Min: 0.82ms Max: 17.44ms
[ 1941.1571] V/AudioStream: Audio buffer underflow, resampled 374 frames to 441
[ 1941.2170] V/AudioStream: Underrun compensation done (128 frames buffered)
[ 1941.2571] V/AudioStream: Audio buffer underflow, resampled 2 frames to 441
[ 1941.2617] V/System: Target speed: 1000%
[ 1941.2618] V/System: Preset timing: immediate
[ 1941.2620] V/System: VSync: Disabled (present throttle allowed)
[ 1941.2673] V/AudioStream: Underrun compensation done (128 frames buffered)
[ 1941.3228] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3250] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3313] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3325] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3362] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3416] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3427] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3462] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3514] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3530] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3568] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3613] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3630] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3666] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3715] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3730] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3765] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3817] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3832] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3870] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3915] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3931] V/AudioStream: ___ Stretcher is being reset.
[ 1941.3964] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4016] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4028] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4070] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4116] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4150] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4165] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4219] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4250] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4264] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4318] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4351] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4365] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4419] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4451] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4467] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4514] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4551] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4565] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4617] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4651] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4666] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4722] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4752] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4766] V/AudioStream: ___ Stretcher is being reset.
[ 1941.4777] V/System: Target speed: 100%
[ 1941.4778] V/System: Preset timing: immediate
[ 1941.4779] V/System: VSync: Disabled
[ 1941.7456] V/PerfMon: FPS: 87.78 VPS: 175.56 CPU: 8.18 GPU: 0.00 Avg: 5.70ms Min: 0.31ms Max: 17.38ms
[ 1941.8629] V/System: Target speed: 1000%
[ 1941.8629] V/System: Preset timing: immediate
[ 1941.8636] V/System: VSync: Disabled (present throttle allowed)
[ 1942.0062] V/System: Target speed: 100%
[ 1942.0063] V/System: Preset timing: immediate
[ 1942.0071] V/System: VSync: Disabled
[ 1942.1917] V/System: Target speed: 1000%
[ 1942.1918] V/System: Preset timing: immediate
[ 1942.1923] V/System: VSync: Disabled (present throttle allowed)
[ 1942.3467] V/System: Target speed: 100%
[ 1942.3469] V/System: Preset timing: immediate
[ 1942.3475] V/System: VSync: Disabled
[ 1942.5153] V/System: Target speed: 1000%
[ 1942.5154] V/System: Preset timing: immediate
[ 1942.5159] V/System: VSync: Disabled (present throttle allowed)
[ 1942.6383] V/System: Target speed: 100%
[ 1942.6384] V/System: Preset timing: immediate
[ 1942.6388] V/System: VSync: Disabled
[ 1942.7561] V/PerfMon: FPS: 141.52 VPS: 282.06 CPU: 10.77 GPU: 0.00 Avg: 3.55ms Min: 0.84ms Max: 17.74ms
[ 1943.2172] V/AudioStream: Audio buffer underflow, resampled 93 frames to 441
[ 1943.2272] V/AudioStream: Underrun compensation done (128 frames buffered)
[ 1943.2478] V/AudioStream: Audio buffer underflow, resampled 1 frames to 441
[ 1943.2672] V/AudioStream: Underrun compensation done (128 frames buffered)
[ 1943.6093] V/AudioStream: === Stretcher is now inactive.
[ 1943.7593] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.39 GPU: 0.00 Avg: 16.72ms Min: 16.20ms Max: 17.19ms
[ 1944.7626] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.63 GPU: 0.00 Avg: 16.72ms Min: 16.25ms Max: 17.29ms
[ 1945.7653] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.60 GPU: 0.00 Avg: 16.71ms Min: 16.32ms Max: 17.11ms
[ 1946.7689] V/PerfMon: FPS: 29.89 VPS: 59.78 CPU: 3.63 GPU: 0.00 Avg: 16.73ms Min: 15.93ms Max: 17.26ms
[ 1947.7715] V/PerfMon: FPS: 29.92 VPS: 59.85 CPU: 3.59 GPU: 0.00 Avg: 16.71ms Min: 16.14ms Max: 17.27ms
[ 1948.3234] D/CodeCache: Breaking block 0x800C2FFC at 0x800C3000 due to page crossing
[ 1948.4237] D/MDEC: Invalid MDEC command 0x17FF03FF
[ 1948.4238] D/MDEC: Invalid MDEC command 0x1801F76C
[ 1948.4243] D/MDEC: Invalid MDEC command 0xF7CCFE00
[ 1948.4244] D/MDEC: Invalid MDEC command 0x1FFF0002
[ 1948.4246] D/CodeCache: Page fault handler invoked at PC=0x7ff609e33aa1 Address=0x28435529ba3 (read), fastmem offset 80229BA3
[ 1948.4247] D/CodeCache: Backpatching store at 0x7ff609e33aa1[5] (pc 8004269C addr 80229BA3): Bitmask 0BD259B0 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4249] D/Recompiler: Backpatching 0x7ff609e33aa1 (guest PC 0x8004269C) to slowmem
[ 1948.4249] D/CodeCache: Page fault handler invoked at PC=0x7ff609e33ab3 Address=0x28435529ba5 (read), fastmem offset 80229BA5
[ 1948.4250] D/CodeCache: Backpatching store at 0x7ff609e33ab3[5] (pc 800426A0 addr 80229BA5): Bitmask 0BD259E0 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4250] D/Recompiler: Backpatching 0x7ff609e33ab3 (guest PC 0x800426A0) to slowmem
[ 1948.4252] D/CodeCache: Page fault handler invoked at PC=0x7ff609e33ac6 Address=0x28435529ba7 (read), fastmem offset 80229BA7
[ 1948.4253] D/CodeCache: Backpatching store at 0x7ff609e33ac6[5] (pc 800426A4 addr 80229BA7): Bitmask 0BD25A10 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4253] D/Recompiler: Backpatching 0x7ff609e33ac6 (guest PC 0x800426A4) to slowmem
[ 1948.4253] D/CodeCache: Page fault handler invoked at PC=0x7ff609e33ad5 Address=0x28435529ba9 (read), fastmem offset 80229BA9
[ 1948.4253] D/CodeCache: Backpatching store at 0x7ff609e33ad5[5] (pc 800426A8 addr 80229BA9): Bitmask 0BD25A40 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4255] D/Recompiler: Backpatching 0x7ff609e33ad5 (guest PC 0x800426A8) to slowmem
[ 1948.4257] D/CodeCache: Page fault handler invoked at PC=0x7ff609e33ae4 Address=0x28435529bab (read), fastmem offset 80229BAB
[ 1948.4257] D/CodeCache: Backpatching store at 0x7ff609e33ae4[5] (pc 800426AC addr 80229BAB): Bitmask 0BD25A70 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4257] D/Recompiler: Backpatching 0x7ff609e33ae4 (guest PC 0x800426AC) to slowmem
[ 1948.4258] D/CodeCache: Page fault handler invoked at PC=0x7ff609e33af7 Address=0x28435529bad (read), fastmem offset 80229BAD
[ 1948.4259] D/CodeCache: Backpatching store at 0x7ff609e33af7[5] (pc 800426B0 addr 80229BAD): Bitmask 0BD25AA0 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4260] D/Recompiler: Backpatching 0x7ff609e33af7 (guest PC 0x800426B0) to slowmem
[ 1948.4261] D/CodeCache: Page fault handler invoked at PC=0x7ff609e344fc Address=0x28435529baf (read), fastmem offset 80229BAF
[ 1948.4263] D/CodeCache: Backpatching store at 0x7ff609e344fc[5] (pc 80042870 addr 80229BAF): Bitmask 0BD25E80 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4264] D/Recompiler: Backpatching 0x7ff609e344fc (guest PC 0x80042870) to slowmem
[ 1948.4265] D/CodeCache: Page fault handler invoked at PC=0x7ff609e35236 Address=0x28435529bbb (read), fastmem offset 80229BBB
[ 1948.4265] D/CodeCache: Backpatching store at 0x7ff609e35236[5] (pc 8004282C addr 80229BBB): Bitmask 0BD262A0 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4266] D/Recompiler: Backpatching 0x7ff609e35236 (guest PC 0x8004282C) to slowmem
[ 1948.4266] D/CodeCache: Page fault handler invoked at PC=0x7ff609e34486 Address=0x28435529bd1 (read), fastmem offset 80229BD1
[ 1948.4268] D/CodeCache: Backpatching store at 0x7ff609e34486[5] (pc 800428EC addr 80229BD1): Bitmask 0BD25E40 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4269] D/Recompiler: Backpatching 0x7ff609e34486 (guest PC 0x800428EC) to slowmem
[ 1948.4570] D/CodeCache: Page fault handler invoked at PC=0x7ff609e3462a Address=0x28435500000 (write), fastmem offset 80200000
[ 1948.4572] D/CodeCache: Backpatching store at 0x7ff609e3462a[5] (pc 80042894 addr 80200000): Bitmask 0BD25EC0 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4575] D/Recompiler: Backpatching 0x7ff609e3462a (guest PC 0x80042894) to slowmem
[ 1948.4578] D/CodeCache: Page fault on protected RAM @ 0x00000000 (page #0), invalidating code cache.
[ 1948.4579] D/CodeCache: Page fault handler invoked at PC=0x7ff609e347dd Address=0x2843550001c (write), fastmem offset 8020001C
[ 1948.4579] D/CodeCache: Backpatching store at 0x7ff609e347dd[5] (pc 800428B4 addr 8020001C): Bitmask 0BD25EF0 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4580] D/Recompiler: Backpatching 0x7ff609e347dd (guest PC 0x800428B4) to slowmem
[ 1948.4580] D/CodeCache: Page fault handler invoked at PC=0x7ff609e37262 Address=0x2843550001e (write), fastmem offset 8020001E
[ 1948.4581] D/CodeCache: Backpatching store at 0x7ff609e37262[5] (pc 800427EC addr 8020001E): Bitmask 0BD26BC0 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4583] D/Recompiler: Backpatching 0x7ff609e37262 (guest PC 0x800427EC) to slowmem
[ 1948.4584] D/CodeCache: Page fault handler invoked at PC=0x7ff609e37368 Address=0x28435500024 (write), fastmem offset 80200024
[ 1948.4584] D/CodeCache: Backpatching store at 0x7ff609e37368[5] (pc 800427EC addr 80200024): Bitmask 0BD26C30 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4584] D/Recompiler: Backpatching 0x7ff609e37368 (guest PC 0x800427EC) to slowmem
[ 1948.4585] D/CodeCache: Page fault handler invoked at PC=0x7ff609e34bf4 Address=0x28435500042 (write), fastmem offset 80200042
[ 1948.4587] D/CodeCache: Backpatching store at 0x7ff609e34bf4[5] (pc 800428D4 addr 80200042): Bitmask 0BD25FF0 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4590] D/Recompiler: Backpatching 0x7ff609e34bf4 (guest PC 0x800428D4) to slowmem
[ 1948.4591] D/CodeCache: Page fault handler invoked at PC=0x7ff609e3446d Address=0x28435500050 (write), fastmem offset 80200050
[ 1948.4594] D/CodeCache: Backpatching store at 0x7ff609e3446d[5] (pc 800428E4 addr 80200050): Bitmask 0BD25E00 Addr 0 Data 0 Size 1 Signed 00
[ 1948.4595] D/Recompiler: Backpatching 0x7ff609e3446d (guest PC 0x800428E4) to slowmem
[ 1948.4596] W(ReadBlockInstructions): Direct branch in delay slot at 80000084, skipping block
[ 1948.4597] E(CompileOrRevalidateBlock): Failed to read block at 0x80000080, falling back to uncached interpreter
[ 1948.5071] V/AudioStream: Audio buffer underflow, resampled 262 frames to 441

