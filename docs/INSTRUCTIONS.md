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

66.0699] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0699] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0700] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0700] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0700] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0701] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0702] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0703] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0703] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0704] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0704] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0704] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0705] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0706] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0707] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0707] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0707] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0708] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0708] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0709] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0710] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0711] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0711] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0711] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0712] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0713] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0713] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0714] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0714] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0715] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0715] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0716] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0716] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0717] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.0718] W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
[   66.3679] V/PerfMon: FPS: 1.00 VPS: 59.81 CPU: 4.37 GPU: 0.00 Avg: 16.72ms Min: 11.69ms Max: 19.41ms
[   67.2706] D/MDEC: Invalid MDEC command 0x8A010160
[   67.2707] D/MDEC: Invalid MDEC command 0x0FFF1000
[   67.2715] D/MDEC: Invalid MDEC command 0x100107FF
[   67.2717] D/MDEC: Invalid MDEC command 0x1C01101C
[   67.2718] D/MDEC: Invalid MDEC command 0x0003526F
[   67.2719] D/MDEC: Invalid MDEC command 0x000107FF
[   67.2720] D/MDEC: Invalid MDEC command 0x03FF3BFF
[   67.2720] D/MDEC: Invalid MDEC command 0x00011401
[   67.2721] D/MDEC: Invalid MDEC command 0x1348FE00
[   67.2721] D/MDEC: Invalid MDEC command 0x00010002
[   67.3710] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 3.22 GPU: 0.00 Avg: 16.72ms Min: 15.98ms Max: 17.82ms
[   68.3739] V/PerfMon: FPS: 0.00 VPS: 59.83 CPU: 3.14 GPU: 0.00 Avg: 16.71ms Min: 15.67ms Max: 17.63ms
[   69.3770] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 3.19 GPU: 0.00 Avg: 16.72ms Min: 16.11ms Max: 17.29ms
[   70.3801] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 3.25 GPU: 0.00 Avg: 16.72ms Min: 9.88ms Max: 23.84ms
[   71.3831] V/PerfMon: FPS: 1.00 VPS: 59.82 CPU: 3.59 GPU: 0.00 Avg: 16.72ms Min: 3.76ms Max: 29.01ms
[   71.9183] D/MDEC: Invalid MDEC command 0x8A010160
[   71.9184] D/MDEC: Invalid MDEC command 0x0FFF1000
[   71.9189] D/MDEC: Invalid MDEC command 0x100107FF
[   71.9191] D/MDEC: Invalid MDEC command 0x1C01101C
[   71.9192] D/MDEC: Invalid MDEC command 0x0003526F
[   71.9192] D/MDEC: Invalid MDEC command 0x000107FF
[   71.9193] D/MDEC: Invalid MDEC command 0x03FF3BFF
[   71.9193] D/MDEC: Invalid MDEC command 0x00011401
[   71.9193] D/MDEC: Invalid MDEC command 0x1348FE00
[   71.9194] D/MDEC: Invalid MDEC command 0x00010002
[   72.3864] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 3.22 GPU: 0.00 Avg: 16.72ms Min: 14.78ms Max: 17.76ms
[   73.3896] V/PerfMon: FPS: 0.00 VPS: 59.81 CPU: 3.24 GPU: 0.00 Avg: 16.72ms Min: 15.59ms Max: 18.13ms
[   74.3922] V/PerfMon: FPS: 0.00 VPS: 59.84 CPU: 3.20 GPU: 0.00 Avg: 16.71ms Min: 16.19ms Max: 17.37ms
[   75.3952] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 3.33 GPU: 0.00 Avg: 16.72ms Min: 16.03ms Max: 17.48ms
[   76.3988] V/PerfMon: FPS: 1.00 VPS: 59.79 CPU: 3.21 GPU: 0.00 Avg: 16.73ms Min: 16.28ms Max: 17.32ms
[   76.5829] D/MDEC: Invalid MDEC command 0x8A010160
[   76.5830] D/MDEC: Invalid MDEC command 0x0FFF1000
[   76.5838] D/MDEC: Invalid MDEC command 0x100107FF
[   76.5841] D/MDEC: Invalid MDEC command 0x1C01101C
[   76.5842] D/MDEC: Invalid MDEC command 0x0003526F
[   76.5843] D/MDEC: Invalid MDEC command 0x000107FF
[   76.5845] D/MDEC: Invalid MDEC command 0x03FF3BFF
[   76.5846] D/MDEC: Invalid MDEC command 0x00011401
[   76.5848] D/MDEC: Invalid MDEC command 0x1348FE00
[   76.5849] D/MDEC: Invalid MDEC command 0x00010002
[   76.5851] E(UnknownReadHandler): Invalid halfword read at address 0xD9B625E6, pc 0x80042684
[   76.5852] E(UnknownReadHandler): Invalid halfword read at address 0xD9B625E8, pc 0x80042684
[   76.5852] E(UnknownReadHandler): Invalid halfword read at address 0xD9B625EA, pc 0x80042684
[   76.5853] E(UnknownReadHandler): Invalid halfword read at address 0xD9B625EC, pc 0x80042684
[   76.5853] E(UnknownReadHandler): Invalid halfword read at address 0xD9B625EE, pc 0x80042684
[   76.5854] E(UnknownReadHandler): Invalid halfword read at address 0xD9B625F0, pc 0x80042684
[   77.4135] V/PerfMon: FPS: 0.00 VPS: 59.13 CPU: 3.30 GPU: 0.00 Avg: 16.91ms Min: 8.45ms Max: 29.05ms
[   78.4212] V/PerfMon: FPS: 0.00 VPS: 60.54 CPU: 3.51 GPU: 0.00 Avg: 16.52ms Min: 4.66ms Max: 17.57ms
[   79.4242] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 3.25 GPU: 0.00 Avg: 16.72ms Min: 8.61ms Max: 24.70ms
[   80.4275] V/PerfMon: FPS: 1.00 VPS: 59.80 CPU: 3.35 GPU: 0.00 Avg: 16.72ms Min: 15.55ms Max: 17.73ms
[   81.2298] D/MDEC: Invalid MDEC command 0xFFFFFFFF
[   81.2299] D/MDEC: Invalid MDEC command 0xFE00FE00
[   81.2320] D/MDEC: Invalid MDEC command 0x1001FE00
[   81.2321] D/MDEC: Invalid MDEC command 0x1C01101C
[   81.2322] D/MDEC: Invalid MDEC command 0x0003526F
[   81.2322] D/MDEC: Invalid MDEC command 0x000107FF
[   81.2323] D/MDEC: Invalid MDEC command 0x03FF3BFF
[   81.2323] D/MDEC: Invalid MDEC command 0x00011401
[   81.2323] D/MDEC: Invalid MDEC command 0x1348FE00
[   81.2325] D/MDEC: Invalid MDEC command 0x00010002
[   81.2325] E(UnknownReadHandler): Invalid halfword read at address 0x3CC4F184, pc 0x80042684
[   81.2326] E(UnknownReadHandler): Invalid halfword read at address 0x3CC4F186, pc 0x80042684
[   81.2327] E(UnknownReadHandler): Invalid halfword read at address 0x3CC4F188, pc 0x80042684
[   81.2327] E(UnknownReadHandler): Invalid halfword read at address 0x3CC4F18A, pc 0x80042684
[   81.2329] E(UnknownReadHandler): Invalid halfword read at address 0x3CC4F18C, pc 0x80042684
[   81.2330] E(UnknownReadHandler): Invalid halfword read at address 0x3CC4F18E, pc 0x80042684
[   81.4302] V/PerfMon: FPS: 0.00 VPS: 59.84 CPU: 3.25 GPU: 0.00 Avg: 16.71ms Min: 15.39ms Max: 17.89ms
[   82.4336] V/PerfMon: FPS: 0.00 VPS: 59.80 CPU: 3.31 GPU: 0.00 Avg: 16.72ms Min: 15.62ms Max: 17.72ms
[   83.4366] V/PerfMon: FPS: 0.00 VPS: 59.82 CPU: 3.31 GPU: 0.00 Avg: 16.72ms Min: 15.98ms Max: 17.34ms
[   96.2019] V/AudioStream: Audio buffer underflow, resampled 402 frames to 441
[   96.2052] V/AudioStream: Underrun compensation done (128 frames buffered)
[   96.2079] V/AudioStream: Audio buffer underflow, resampled 354 frames to 441
[   96.2400] V/PerfMon: FPS: 0.00 VPS: 0.08 CPU: 0.14 GPU: 0.00 Avg: 12803.34ms Min: 12803.34ms Max: 12803.34ms
[   96.2410] V/AudioStream: ~~~ Stretcher is now active @ tempo 0.8240761.
[   96.2479] V/AudioStream: Underrun compensation done (128 frames buffered)
[   96.6275] V/AudioStream: === Stretcher is now inactive.