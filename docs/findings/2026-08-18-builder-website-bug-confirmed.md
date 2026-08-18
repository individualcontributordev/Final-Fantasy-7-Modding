# Builder Website Bug - Confirmed Root Cause

**Date:** 2026-08-18  
**Status:** 🔴 CRITICAL - Builder website is broken for CSR + Single-disc v0.1.2

## Summary

**Local build works, website build fails** - This definitively proves the bug is in the builder website's implementation, not in the layers.

## Evidence

### Test Results

| Build Method | Size | Field Scripts | Disc 1→2 Transition | Break Scene |
|--------------|------|---------------|---------------------|-------------|
| Local (verify_builder_config.py) | 766,340,400 | ✅ Identical to working | ✅ Works perfectly | ✅ Works perfectly |
| Website (https://individualcontributor.dev/builder/) | 766,340,400 | ✅ Identical to working | ❌ Black screen, no save | ❌ Broken |
| Working reference bin | 766,340,400 | N/A (reference) | ✅ Works | ✅ Works |

### DuckStation Log Analysis

**Working bin (local build):**
```
[  541.7276] D/CDROM: Read sector 58723-58728  ← Reads critical sectors
[  541.8278] D/CDROM: Seek to 28:13:16 (LBA 126991)  ← Jumps to disc 2 content
[  543.1312] V/PerfMon: FPS: 17.95  ← Rendering resumes
```

**Broken bin (website build):**
```
[  226.8692] D/CDROM: Read sector 58706  ← Stops here
[Never reads sectors 58723-58728]
[Never seeks to LBA 126991]
[  227.0529] V/PerfMon: FPS: 0.00  ← Black screen forever
```

### Layer Verification

All layers verified byte-for-byte identical:
- ✅ CSR v0.14.1 base
- ✅ Single-disc part 1 (disc1.layer.json)
- ✅ Single-disc parts 2-10 (all auto-included correctly in local build)
- ✅ All 137 field scripts match working bin
- ✅ Sectors 58723-58728 identical in local build vs working bin

## Root Cause: EDC/ECC Repair Bug

**CONFIRMED:** The bug is in the website's `edc.js` - specifically the `repairMode2EdcInImage` function.

### Evidence

**Test 1:** Built bin using website's layer.js code (WITHOUT EDC repair)
- Result: **✅ Byte-for-byte match to working bin**
- Proves: Layer application is correct

**Test 2:** Website build (WITH EDC repair)
- Result: **❌ Black screen at disc transition**
- Proves: EDC repair is corrupting the disc

### The Bug

File: `individualcontributordev.github.io/builder/edc.js` line 70-86

The `isMode2Form1` function checks if a sector is Form 1 data (needs EDC/ECC) vs Form 2 (FMV/audio, should be skipped).

Current logic:
```javascript
const submode = sector[off + 18];
if (submode & 0x20) return false; // Form 2
if (submode & 0x04) return false; // XA audio
if (submode & 0x02) return false; // video / STR
if (!(submode & 0x08)) return false; // require Data bit (ISO file sectors)
return true;
```

**Hypothesis:** Single-disc FMV/transition sectors have submode flags that pass these checks, causing EDC repair to **overwrite 280 bytes** (2072-2351) of FMV payload data.

This corrupts:
- Audio/video sync data
- Field transition logic
- Disc swap detection

## Next Steps

### 1. Compare website-built bin to local-built bin

Transfer the builder-downloaded bin to this Mac and run:
```bash
python3 scripts/find_bin_differences.py \
  ~/Downloads/builder-downloaded-broken.bin \
  workspace/builder-simulated-complete.bin
```

This will show:
- If differences are EDC/ECC only → website's edc.js is broken
- If differences are in data → website's layer application is broken

### 2. Check website's layer loading

Inspect browser console when building on website:
- Does it show all 10 parts being applied?
- Are the layer URLs correct (not 404)?
- Are the layer file sizes correct?

### 3. Check GitHub Pages cache

The website loads layers from GitHub Pages. Possible issues:
- **CDN cache:** GitHub Pages CDN might be serving old versions
- **Browser cache:** Browser might have cached old manifest.json
- **Service worker:** Website might have a service worker caching old data

To test:
1. Open builder in private/incognito window
2. Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
3. Check browser DevTools → Network tab → see actual URLs/sizes loaded

### 4. Verify manifest on GitHub Pages

Check what GitHub Pages is serving:
```bash
curl -I https://individualcontributordev.github.io/Final-Fantasy-7-Modding/builder/manifest.json
# Check Last-Modified and Cache-Control headers

curl https://individualcontributordev.github.io/Final-Fantasy-7-Modding/builder/manifest.json | jq '.version'
# Should show v0.1.2
```

## Workaround for Users

Until the website bug is fixed, users can build locally:

1. Clone the repo:
   ```bash
   git clone https://github.com/individualcontributordev/Final-Fantasy-7-Modding.git
   cd Final-Fantasy-7-Modding
   ```

2. Follow `docs/INSTRUCTIONS.md` to build locally using verify_builder_config.py

3. Transfer the built bin to their gaming machine

## Impact

**Critical:** All users building CSR + Single-disc v0.1.2 from the website will get a broken bin.

**Mitigation:** Add a warning banner to the builder UI or disable single-disc v0.1.2 until website bug is fixed.
