# What You'll See in the Builder UI for v0.1.2

## Builder URL
https://individualcontributor.dev/builder/

## Step-by-Step UI Flow

### 1. Select Base
**You'll see:**
- Clean (Unmodified)
- **CSR v0.14.1** ← SELECT THIS
- Highwind v0.2.0

**Select:** CSR v0.14.1

### 2. Select Mods
**You'll see in the mod list:**

**Single-disc (v0.1.2)** [BETA]
- Description: "Play the whole game from one Disc 1 image on CSR. v0.1.2: Rollback to working version with verified field changes."
- Hint: "CSR. Movies + endings auto-apply."
- Beta note: "Single-disc v0.1.2 rollback. Known issue: movie audio flickering (ending + loslake1). Field changes verified exact match to working bin."

**Check this box:** ✅ Single-disc

### 3. What Happens Automatically

When you select "Single-disc", the builder UI will **automatically apply** these hidden layers:

1. **CSR manip movies (v0.1.4)** [AUTO-INCLUDED, HIDDEN]
   - Description: "D2/D3 manip FMVs on D1"
   - 841,849 records
   - Moves Disc 2/3 movies to Disc 1

2. **Single-disc ending credits (parts 1-7)** [AUTO-INCLUDED, HIDDEN]
   - Part 1/7: 541,474 records
   - Part 2/7: 602,679 records
   - Part 3/7: 469,145 records
   - Part 4/7: 415,496 records
   - Part 5/7: 326,769 records
   - Part 6/7: 503,283 records
   - Part 7/7: 412,829 records

**You won't see these in the UI** - they auto-apply when you select Single-disc on CSR.

### 4. Build Configuration

**What gets applied (in order):**

1. **CSR v0.14.1 base** (from your pristine Disc 1)
2. **Single-disc v0.1.2 layer** (96,497 records)
   - Field changes: CSR D1 + D2 overlays + DSKCG stripped
3. **CSR manip movies v0.1.4** (841,849 records) [AUTO]
   - Disc 2/3 movies on Disc 1
4. **Ending credits parts 1-7** (3,271,675 records) [AUTO]
   - Ending movies on Disc 1

**Total: 4,210,021 records applied to Disc 1**

### 5. Download

**Builder will provide:**
- Disc 1: 766,340,400 bytes (325,825 sectors)
- Discs 2 & 3: Not needed (all content on Disc 1)

## What You Should See in the UI

```
┌─────────────────────────────────────────┐
│ SELECT BASE                             │
├─────────────────────────────────────────┤
│ ○ Clean (Unmodified)                    │
│ ● CSR v0.14.1                           │
│ ○ Highwind v0.2.0                       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ MODS                                    │
├─────────────────────────────────────────┤
│ ☐ Field Random Encounters               │
│ ☐ World Random Encounters               │
│ ☐ Fanfare Skip                          │
│ ✅ Single-disc (v0.1.2) [BETA]          │
│   "CSR. Movies + endings auto-apply."   │
│   Known: movie audio flickering         │
└─────────────────────────────────────────┘

[BUILD DISC 1]
```

## Verification

After downloading, the Disc 1 bin should be:
- ✅ 766,340,400 bytes
- ✅ All FIELD files match working bin exactly
- ✅ Movies included (may have audio flickering)
- ✅ Endings included

## Testing Checklist

Load Disc 1 in DuckStation:
- [ ] Game boots
- [ ] Disc 1 content plays normally
- [ ] Disc 1→2 transition (no "Insert Disc 2" prompt)
- [ ] Break scene plays at COS_BTM2
- [ ] Can continue after break scene
- [ ] Ending plays (note audio flickering)
- [ ] LOSLAKE1 movie plays (note audio flickering)

## Known Issues

**Expected (from working v0.1.2):**
- Movie audio flickering on ending credits
- Movie audio flickering on LOSLAKE1 (field 637, movie 0x2F)

**These are expected** - your working bin has the same issues.

## Next Steps

After testing:
1. Confirm disc 1→2 transition works
2. Confirm break scene works
3. Report movie flickering details
4. Agent investigates movie flickering for v0.1.41
