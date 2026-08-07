# Task: ending credits test v5

## Why v4 still froze

DuckStation log showed Form2 reads in **ONTRAIN** (MOVIE_ID **id 23**), then:

- `Invalid MDEC command …`
- page fault at `0x00000000`

On Disc 3, **id 23 = LASTMAP.BIN** (Form1 **camera**, not FMV).  
LASTMAP does `PMVIE 23` then later `AD` `MOVIE` while that id is still selected.  
Feeding a Form2 train FMV (or any MDEC stream) at id 23 crashes the same way as v3.

## What v5 does

1. **MOVIE_ID 23** ← real D3 **LASTMAP.BIN** Form1 + D3 aux (camera).  
2. **LASTMAP field patch**: remove early **`MOVIE`** on AD S31  
   (`MVCAM` only). **PMVIE 23/24** kept. Final **AD3 `MOVIE`** still runs  
   after **PMVIE 24** → LASTFLOR.  
3. Form2 D3 streams on **24 / 25 / 26 / 29** (LASTFLOR, ENDING*).  
4. Pristine **LAS4_0** (PMVIE 25 + MOVIE).

Bin ~**1008274176** — DuckStation only.

## What you do

1. Pull  
2. Open ending-test cue (rebuild if needed)  
3. LASTMAP → end credits  
4. Reply: freeze? what played? sound?  

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

Expect ~**1008274176** bytes.

---

## 2. Rebuild if needed

```bash
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

---

## 3. Smoke

- No MDEC crash on LASTMAP  
- LASTFLOR / ENDING* should play for the real FMV path  
- Camera path may load id 23 without full-motion train footage  

---

## 4. Reply

1. Bin size  
2. What played  
3. Freeze yes/no · sound yes/no  

 212.8291] V/System: Preset timing: immediate
[  212.8296] V/System: VSync: Disabled (present throttle allowed)
[  212.8315] V/PerfMon: FPS: 135.97 VPS: 271.93 CPU: 11.92 GPU: 0.00 Avg: 3.68ms Min: 0.82ms Max: 17.41ms
[  213.3781] V/System: Target speed: 100%
[  213.3782] V/System: Preset timing: immediate
[  213.3788] V/System: VSync: Disabled
[  213.8473] V/PerfMon: FPS: 175.24 VPS: 349.49 CPU: 14.41 GPU: 0.00 Avg: 2.86ms Min: 0.30ms Max: 17.05ms
[  213.8752] V/AudioStream: Audio buffer underflow, resampled 414 frames to 441
[  213.9246] V/AudioStream: Underrun compensation done (128 frames buffered)
[  213.9446] V/AudioStream: Audio buffer underflow, resampled 1 frames to 441
[  213.9547] V/AudioStream: Underrun compensation done (128 frames buffered)
[  213.9952] V/AudioStream: Audio buffer underflow, resampled 2 frames to 441
[  214.0046] V/AudioStream: Underrun compensation done (128 frames buffered)
[  214.1148] V/System: Target speed: 1000%
[  214.1149] V/System: Preset timing: immediate
[  214.1155] V/System: VSync: Disabled (present throttle allowed)
[  214.1763] V/AudioStream: ___ Stretcher is being reset.
[  214.1796] V/AudioStream: ___ Stretcher is being reset.
[  214.1815] V/AudioStream: ___ Stretcher is being reset.
[  214.1865] V/AudioStream: ___ Stretcher is being reset.
[  214.1897] V/AudioStream: ___ Stretcher is being reset.
[  214.1916] V/AudioStream: ___ Stretcher is being reset.
[  214.1985] V/AudioStream: ___ Stretcher is being reset.
[  214.1995] V/AudioStream: ___ Stretcher is being reset.
[  214.2027] V/AudioStream: ___ Stretcher is being reset.
[  214.2083] V/AudioStream: ___ Stretcher is being reset.
[  214.2099] V/AudioStream: ___ Stretcher is being reset.
[  214.2131] V/AudioStream: ___ Stretcher is being reset.
[  214.2184] V/AudioStream: ___ Stretcher is being reset.
[  214.2200] V/AudioStream: ___ Stretcher is being reset.
[  214.2233] V/AudioStream: ___ Stretcher is being reset.
[  214.2283] V/AudioStream: ___ Stretcher is being reset.
[  214.2299] V/AudioStream: ___ Stretcher is being reset.
[  214.2330] V/AudioStream: ___ Stretcher is being reset.
[  214.2351] V/AudioStream: ___ Stretcher is being reset.
[  214.2380] V/System: Target speed: 100%
[  214.2381] V/System: Preset timing: immediate
[  214.2381] V/System: VSync: Disabled
[  214.8575] V/PerfMon: FPS: 62.36 VPS: 124.73 CPU: 7.18 GPU: 0.00 Avg: 8.02ms Min: 1.05ms Max: 17.30ms
[  215.1646] V/AudioStream: Audio buffer underflow, resampled 28 frames to 441
[  215.1846] V/AudioStream: Underrun compensation done (128 frames buffered)
[  215.2046] V/AudioStream: Audio buffer underflow, resampled 1 frames to 441
[  215.2090] V/AudioStream: ___ Stretcher is being reset.
[  215.2146] V/AudioStream: Underrun compensation done (128 frames buffered)
[  215.6935] V/AudioStream: === Stretcher is now inactive.
[  215.8601] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.94 GPU: 0.00 Avg: 16.71ms Min: 16.24ms Max: 17.11ms
[  216.8631] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 4.14 GPU: 0.00 Avg: 16.72ms Min: 16.05ms Max: 17.26ms
[  216.9636] D/CodeCache: Discard block 800D3548 with manual protection
[  216.9637] D/CodeCache: Discard block 800D35B8 with manual protection
[  216.9643] D/CodeCache: Discard block 800D35EC with manual protection
[  216.9806] D/CodeCache: Discard block 800D3520 with manual protection
[  217.0806] D/CDROM: CDROM executing command 0x02 (Setloc), stat = 0x02, params = [0x36, 0x23, 0x33]
[  217.0808] D/CDROM: CDROM setloc command (36, 23, 33)
[  217.1808] D/CDROM: CDROM executing command 0x0E (Setmode), stat = 0x02, params = [0xE0]
[  217.1809] D/CDROM: CDROM setmode command 0xE0
[  217.1813] D/CDROM: CDROM executing command 0x1B (ReadS), stat = 0x02, params = []
[  217.1814] D/CDROM: Seek time for 12:01:53->36:23:33 (109630 LBA): 18069980 (533.529 ms) (2N/sled forward)
[  217.7160] W(DoSeekComplete): Logical seek to [36:23:33] failed
[  217.8666] V/PerfMon: FPS: 28.90 VPS: 59.79 CPU: 3.51 GPU: 0.00 Avg: 16.73ms Min: 16.23ms Max: 17.21ms
[  218.8690] V/PerfMon: FPS: 29.93 VPS: 59.85 CPU: 3.40 GPU: 0.00 Avg: 16.71ms Min: 16.20ms Max: 17.21ms
[  219.8726] V/PerfMon: FPS: 29.89 VPS: 59.79 CPU: 3.30 GPU: 0.00 Avg: 16.73ms Min: 16.04ms Max: 17.50ms
[  220.8757] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.27 GPU: 0.00 Avg: 16.72ms Min: 16.10ms Max: 17.58ms
[  221.8784] V/PerfMon: FPS: 29.92 VPS: 59.84 CPU: 3.25 GPU: 0.00 Avg: 16.71ms Min: 16.31ms Max: 17.17ms
[  222.8816] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.37 GPU: 0.00 Avg: 16.72ms Min: 15.77ms Max: 17.25ms
[  223.8846] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.30 GPU: 0.00 Avg: 16.72ms Min: 16.28ms Max: 17.17ms
[  224.8874] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 3.47 GPU: 0.00 Avg: 16.71ms Min: 16.11ms Max: 17.35ms
[  225.8906] V/PerfMon: FPS: 29.90 VPS: 59.81 CPU: 3.36 GPU: 0.00 Avg: 16.72ms Min: 16.22ms Max: 17.25ms
[  226.8936] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.46 GPU: 0.00 Avg: 16.72ms Min: 16.10ms Max: 17.42ms
[  227.8965] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.55 GPU: 0.00 Avg: 16.72ms Min: 16.26ms Max: 17.18ms
[  228.8996] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.39 GPU: 0.00 Avg: 16.72ms Min: 15.95ms Max: 17.25ms
[  229.9029] V/PerfMon: FPS: 29.90 VPS: 59.80 CPU: 3.46 GPU: 0.00 Avg: 16.72ms Min: 16.24ms Max: 17.46ms
[  230.9059] V/PerfMon: FPS: 29.91 VPS: 59.82 CPU: 3.30 GPU: 0.00 Avg: 16.72ms Min: 16.24ms Max: 17.33ms
[  231.9088] V/PerfMon: FPS: 29.92 VPS: 59.83 CPU: 3.32 GPU: 0.00 Avg: 16.71ms Min: 16.23ms Max: 17.27ms