# Task: CSR single-disc — music after Ask removal + Disc 2 break scene on Disc 1

## Context

You playtested:

    CSR + Single-disc core + movie seed

You removed **Ask for disc** on **blackbgb**. After that, **music stopped working** on that path.

You also want CSR’s **5-minute break scene** (start of Disc 2: take a break or continue) to run in the **same place on Disc 1** for single-disc.

---

## 1. Music broken after removing Ask for disc

This is almost always the **script order** on blackbgb, not a separate music pack.

On the disc-2 / disc-3 branches, the usual order is something like:

    flags / bits
    Ask for disc     ← you removed this
    Play music
    Wait
    Jump to next map

### What goes wrong

| Mistake | Result |
|---------|--------|
| Delete Ask **and** the Play music line | Silence |
| Jump **over** Play music when bypassing Ask | Silence |
| Leave a Goto that skips the music block | Silence |
| Skip bit/flag lines that the music/jump path needs | Odd mute or wrong branch (CSR break scene had a known mute bug if music option 3 + timer) |

### What to do in Makou (blackbgb)

1. Open the **same** Disc 1 .bin you are editing (your playtest image is fine).
2. Map **blackbgb**, main/init script — every branch that used to **Ask for disc**.
3. For each branch, you want:

       … setup / bits …
       (no Ask for disc)
       Play music   ← must still run
       waits …
       Jump to map (lost2 / las0_1 / etc.)

4. If you used “Goto over the Ask” earlier: make sure the Goto lands **before** Play music, not after it.
5. Do not delete Play music unless you replace it with another Play music.
6. Save into the same .bin.

Re-test that path. Fix music **before** chasing the break scene if both are broken on the same hub jump.

---

## 2. Why only blackbgb needed Ask removal (reminder)

Other maps already had Ask removed in the published core pack.  
**blackbgb** was left alone because **CSR already changed that map** — we could not paste Clean’s file over it.

---

## 3. Break scene = Disc 2 start in CSR (LOST2)

CSR changelog: break scene was **moved to the start of Disc 2**.

In the field data that shows up as **CSR’s Disc 2 version of map lost2**:

| Disc | File | About |
|------|------|--------|
| CSR Disc 2 | FIELD/LOST2.DAT | Larger — includes break (take a break / continue, timer, music options) |
| CSR Disc 1 | FIELD/LOST2.DAT | Smaller — **not** the same script as Disc 2 |

After Jenova Life / disc change, blackbgb jumps to **lost2**. On multi-disc CSR you get Disc 2’s lost2 (with break). On single-disc D1 you still have Disc 1’s lost2 (no break).

### Goal

Put **CSR Disc 2’s LOST2.DAT** into **Disc 1’s LOST2** slot so the same jump hits the break scene.

Sizes (csr-v0.14.1):

- D2 LOST2 ≈ 17090 bytes  
- D1 LOST2 slot ≈ 17007 bytes  
- Same number of disc sectors → can grow the D1 file size by ~83 bytes (no full ISO rebuild)

---

## 4. Break scene — two ways

### Option A — you do it in Makou (fine)

1. On **CSR Disc 2** (or a builder zip of CSR disc 2 only), open **lost2** and note/export how the break works (or keep that .bin open as reference).
2. On your **Disc 1** single-disc playtest .bin, open **lost2**.
3. Make lost2 on Disc 1 match Disc 2’s break behavior (or paste/replace field data if Makou allows replacing the whole map file from D2 CSR).
4. Save Disc 1 .bin.

If pasting whole map is awkward, use Option B.

### Option B — copy CSR D2 LOST2 file onto D1 (agent can run this later)

Needs:

- Your updated Disc 1 .bin (after music fix), path = WORK  
- CSR disc2 layer applied to pristine D2 to extract LOST2, **or** extract from a CSR D2 builder output

Concept:

1. Read FIELD/LOST2.DAT from CSR Disc 2 image  
2. On Disc 1 WORK image, grow FIELD/LOST2.DAT size to 17090 if needed  
3. Write D2 bytes into that slot  
4. Rebuild packs from WORK (same as after blackbgb)

Say **copy lost2** if you want the agent to do Option B on a path you give.

---

## 5. After music + break scene are good on your .bin

Your WORK .bin is the source of truth until packs are updated.

1. Rebuild **core** pack = WORK minus CSR base (if WORK is core+movies, see below)  
2. Rebuild **movie** pack if WORK still has the four videos  
3. Verify, push, **new** builder zip, playtest again  

If WORK is **full playtest** (core + movies + your edits):

    # CSR base
    python3 scripts/apply_layer.py workspace/pristine/FINALFANTASY7_D1.bin \
      /Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json \
      -o workspace/iso-extract/ff7_d1_csr_base.bin

    # Core pack from WORK vs CSR base — only OK if WORK has no movie-seed byte changes
    # you want in the CORE pack. Prefer: rebuild core from a core-only edit bin;
    # or if WORK is full stack, movie pack = WORK minus (CSR+new core without movies).

**Simpler path if you only use one full playtest bin (core+movies+edits):**

    A. Tell agent path to WORK after music + lost2 are fixed
    B. Agent rebuilds core + movie packs and verifies
    C. You pull, new builder zip, playtest

Or run the rebuild commands yourself from the previous instructions (WORK = your bin).

---

## 6. What you should do right now (order)

1. **Makou blackbgb** — fix music (Play music still runs on every old Ask branch). Save. Quick test.
2. **Break scene** — copy/match CSR Disc 2 **lost2** onto Disc 1 (Option A or ask agent Option B). Save.
3. **Playtest** that same .bin (DuckStation is fine) — break appears; music OK; no Ask.
4. **Say check** with path to WORK (or rebuild packs yourself then check).

Do not create a second zip just to edit — keep using your current playtest Disc 1 .bin.

---

## Notes for check

    Music fixed on blackbgb: yes/no
    Break scene on D1 lost2: yes/no / need agent copy
    WORK bin path:
    Still asks for disc:
    Ready to rebuild packs: yes/no
