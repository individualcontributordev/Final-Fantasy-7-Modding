# TASK: Build single-disc v0.1.40 with complete CSR D1+D2+D3 merge

**Status:** ✅ Automated script ready  
**Agent session:** 2026-08-17  
**Target:** `builder/single-disc-on-csr/layers/disc1.layer.json` v0.1.40  

**⚠️ CRITICAL: CSR layers are NEVER modified - only single-disc layer is rebuilt!**

## Quick Start

```bash
cd ~/Final-Fantasy-7-Modding
git pull --ff-only

# Run the automated build script
python3 mods/single-disc/scripts/build_v0140.py
```

The script will:
1. ✅ Merge CSR D1+D2+D3 fields onto pristine D1 (following prefer policy)
2. ✅ Remove DSKCG operations automatically (19 operations)
3. ✅ Inject SNOVA from pristine D3
4. ✅ Build layer by diffing against pristine
5. ✅ Merge v0.1.39 LOST2 patch (16,726 records)
6. ✅ Update VERSION, pack.json, manifest.json

**Everything is automated!** Just run the script once and it completes the full build.

## After Build Completes

```bash
# Review the layer
cat builder/single-disc-on-csr/layers/disc1.layer.json | head -50

# Commit and push
git add -A
git commit --author="individualcontributordev <contributorindividual@gmail.com>" -m "single-disc v0.1.40: Complete CSR D1+D2+D3 merge + DSKCG + LOST2 + SNOVA

Automated build using build_v0140.py script.

Changes:
- CSR D1 field edits (174 files)
- CSR D2/D3 field merges (77 files, following prefer policy)
- DSKCG removals (19 operations)
- LOST2 IFUW patch (16,726 records from v0.1.39)
- SNOVA inject from pristine D3

Layer size: ~850k+ records (complete CSR story + single-disc patches)"

git push origin main
```

## Test on Builder Site

Wait ~5 min for CDN propagation, then:

1. Go to https://individualcontributor.dev/builder/
2. Clear cache: DevTools Console → `localStorage.clear(); location.reload()`
3. Build: CSR + Single-disc
4. Verify in Makou: Field 103 has no "Ask for disc" operations
5. Playtest in DuckStation: Kalm flashback end should continue without disc swap

## Architecture Notes

See `docs/AGENT_QUESTION.md` for full architecture details.

**Key points:**
- Same field can be edited on D1 AND D2 for different game moments
- 10 fields have conflicts resolved via `csr-field-disc-prefer.txt`
- 77 files merged from D2/D3 via `csr-d2d3-field-merge-on-d1.md`
- CSR layers are never modified - only single-disc layer is rebuilt
