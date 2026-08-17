# TASK: Analyze Working v0.1.2 to Build Correct v0.1.40

**Status:** ⏳ BLOCKED - Waiting for v0.1.2 bin path from user  
**Critical Issue:** LOST2 break scene missing (disc 1→2 transition broken)

## Problem Summary

**v0.1.39 and v0.1.40 are both broken:**
- v0.1.39: LOST2 field corrupted (bad LZS compression)
- v0.1.40: Massive corruption from wrong DSKCG opcode (0x13 vs 0x0E)

**Missing:** LOST2 break scene IFUW patch
- IFUW @ position ~1201 checks disc flags
- On single-disc, else-jump 0x0B skips MAPJUMP to cos_btm2 break scene
- **Fix:** Change else-jump 0x0B → 0x00 (always MAPJUMP)
- **Result:** Disc 1→2 transition works with proper break scene

## When User Provides v0.1.2 Bin Path

User is downloading: https://drive.google.com/file/d/1DR7nCRQeANr_qY4jRwR2y_0JNHVEGWnQ

**Agent will run these analyses:**

```bash
# 1. Full field comparison
python3 mods/single-disc/scripts/analyze_working_v012.py \
  --bin USER_PROVIDED_PATH \
  --fields BLACKBGB,BLACKBGE,BLACKBG3,LOST2,DEL1,LOSIN2,CANON_2

# 2. LOST2 break scene check
python3 mods/single-disc/scripts/check_lost2_break_scene.py \
  --bin USER_PROVIDED_PATH

# 3. DSKCG verification
python3 mods/single-disc/scripts/analyze_dskcg.py \
  --from USER_PROVIDED_PATH \
  --fields BLACKBGB,BLACKBGE,BLACKBG3
```

**Expected Results:**
- DSKCG count: 0 (all 19 removed)
- LOST2 IFUW else-jump: 0x00 (break scene enabled)
- Field sources identified: Which CSR disc (D1/D2/D3) each field comes from

## Tools Ready

✅ **analyze_working_v012.py** - Compare v0.1.2 against pristine D1 and CSR D1/D2/D3
✅ **check_lost2_break_scene.py** - Verify LOST2 IFUW patch (0x00 = fixed, 0x0B = broken)
✅ **analyze_dskcg.py** - Count DSKCG operations with full context
✅ **build_v0140.py** - Automated build (needs update after v0.1.2 analysis)

## Next: Build Correct v0.1.40

After analysis, agent will:

1. **Document findings** in `docs/findings/2026-08-17-v012-analysis.md`
2. **Update build_v0140.py** with correct:
   - CSR field source preferences (verified from v0.1.2)
   - LOST2 IFUW patch application
   - DSKCG removal verification
3. **Run build** and verify layer
4. **Commit and publish**

```bash
git add -A
git commit --author="individualcontributordev <contributorindividual@gmail.com>" \
  -m "single-disc v0.1.40: Complete rebuild based on working v0.1.2

Analysis of working v0.1.2 bin identified:
- Correct CSR D1/D2/D3 field merge patterns
- LOST2 break scene IFUW patch (else-jump 0x00)
- All 19 DSKCG operations removed
- SNOVA injection verified

Fixes disc 1→2 transition with proper cos_btm2 break scene."
git push origin main
```

Then test on https://individualcontributor.dev/builder/ after ~5 min CDN.

## Critical Requirement

**Console Hardware Compatibility:** Final mod must burn to disc and run on original PSX/PS2 hardware.
