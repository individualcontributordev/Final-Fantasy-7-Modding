# INSTRUCTIONS — Debug Single-Disc × CSR Breakage

## Context

You reported: **"build a .bin from pristine d1 and layer on the csr mod, check this bin, it is working as expected, then add the single-disc mod, adding this and the related manip-movies breaks the csr changes"**

I checked both repos and found:

✅ **CSR layers have content** (Final-Fantasy-7-CSR):
- `builder/csr-v0.14.1/layers/disc1.layer.json` - **12.9MB**, 94,148 records

✅ **Single-disc layers have content** (Final-Fantasy-7-Modding):
- `builder/single-disc-on-csr-v0.1.33/layers/disc1.layer.json` - **84MB**, 834,218 records

The layers are **NOT** empty in the repos!

---

## Diagnosis Steps

We need to determine whether the issue is:
1. **CDN cache** — GitHub Pages serving stale/empty layers
2. **Layer application order** — Single-disc overwrites CSR incorrectly
3. **Baseline mismatch** — Single-disc built against wrong CSR version

### Step 1: Check what the builder site actually loads

Open https://individualcontributor.dev/builder/ in a browser with DevTools Network panel:

1. **Open DevTools** → Network tab
2. **Clear cache** → hard refresh
3. **Select CSR base** + **Single-disc mod**
4. **Filter** Network tab by "layer.json"
5. **Check URLs loaded**:
   - CSR: `https://individualcontributor.dev/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json`
   - Single-disc: `https://individualcontributor.dev/Final-Fantasy-7-Modding/builder/single-disc-on-csr-v0.1.33/layers/disc1.layer.json`

6. **Click each layer.json** in Network tab
7. **Check Response tab size**:
   - CSR disc1: should be ~12.9 MB
   - Single-disc disc1: should be ~84 MB

**Paste back:**
- Are the URLs correct?
- What are the actual sizes in the Response tab?
- If sizes are tiny/empty, **GitHub Pages is serving stale cache** → force CDN refresh

---

### Step 2: If CDN is cached, purge it

If the CDN is serving old/empty layers:

```bash
# Force GitHub Pages to rebuild by pushing a trivial change
cd ~/Final-Fantasy-7-Modding
echo "# CDN refresh $(date)" >> builder/CACHE_BUST.md
git add builder/CACHE_BUST.md
git commit -m "Force Pages CDN refresh for single-disc layers"
git push
```

Wait 2-3 minutes, then hard-refresh the builder site and re-check Network tab sizes.

---

### Step 3: If CDN serves correct sizes, verify layer content

If the CDN is serving 84MB single-disc layer, the issue is **what's inside the layer**.

Run this locally to inspect what single-disc patches:

```bash
cd ~/Final-Fantasy-7-Modding
python3 << 'PYEOF'
import json

with open("builder/single-disc-on-csr-v0.1.33/layers/disc1.layer.json") as f:
    sd_layer = json.load(f)

print(f"Single-disc records: {len(sd_layer['records'])}")
print(f"First 5 offsets:")
for r in sd_layer['records'][:5]:
    print(f"  offset {r['offset']}: {len(r.get('hex', ''))} hex chars")

# Check if any records patch FIELD.BIN (should be removing Ask-for-disc)
field_patches = [r for r in sd_layer['records'] if 'FIELD' in str(r.get('path', ''))]
print(f"\nRecords with 'FIELD' in path: {len(field_patches)}")

# Offsets are raw disc sector addresses - check if they target FIELD.BIN range
# (FIELD.BIN typically starts around LBA 20000-30000)
early_patches = [r for r in sd_layer['records'] if int(r['offset']) < 100_000_000]
print(f"Records with offset < 100MB: {len(early_patches)}")
PYEOF
```

**Paste the output.**

---

### Step 4: Describe the breakage specifically

**What exactly breaks when you apply CSR + Single-disc?**

Examples:
- ❌ "Disc-ask prompts reappear" → single-disc Ask-removal not applying
- ❌ "Field scripts wrong (dialogue/behavior)" → single-disc overwrites CSR fields
- ❌ "Crash at specific location" → single-disc corrupts CSR data
- ❌ "Movies broken" → manip-movies layer issue

**Be specific:**
- When does it break? (boot, specific map, disc transition point like LOST2→COS_BTM2)
- What's wrong? (prompts, crashes, wrong content)
- Does CSR alone work correctly?
- Does single-disc on pristine (not CSR) work?

---

## Why This Matters

If CDN is stale: purge and done.
If layer content is wrong: I'll rebuild from the ship scripts.
If application order is wrong: I'll check the manifest `addon ApplyRank` and `autoIncludeWhen`.

**Paste the Network tab findings + breakage details, and I'll fix it.**
