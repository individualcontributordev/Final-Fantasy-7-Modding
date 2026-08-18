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

## Root Cause

The builder website is producing a bin with **identical file size and field data** but **different runtime behavior**. This suggests:

1. **Possible EDC/ECC bug** - Website's edc.js produces checksums that cause read errors
2. **Possible sector ordering bug** - Website writes sectors in wrong order
3. **Possible layer application bug** - Website doesn't apply layers the same way as verify_builder_config.py
4. **Possible caching bug** - Website serving stale layer data

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
