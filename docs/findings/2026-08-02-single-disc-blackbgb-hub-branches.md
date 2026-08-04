# Single-disc — blackbgb S0-Main disc branches (pristine)

**Date:** 2026-08-02
**Confidence:** confirmed (full Makou script paste)
**Map:** `blackbgb` (#103) · group `init` · script `S0 - Main`

## Hub behaviour

On enter, S0-Main walks a priority chain of flag checks. Disc-change is only
four branches; other labels handle bike mini-game setup, rocket movie, Aerith
removal, etc.

## Disc-change branches (the four Asks)

| Order | Gate | Ask | After | Dest map |
|------:|------|-----|-------|----------|
| 1 | `Var[3][136]` bit **5** ON | disc **3** | music #2, wait | **las0_1 (#744)** (−7, −917, tri 243, dir 228) |
| 2 | `Var[13][82]` bit **6** ON | disc **3** | optional save (`Var[13][0]=3`, sets bit 5 then clears), music #2 | **las0_1 (#744)** same |
| 3 | `Var[3][134]` bit **2** ON | disc **2** | sets `Var[3][137]` bit 1, music #3 | **lost2 (#634)** (−259, 5042, tri 113, dir 0) |
| 4 | `Var[3][136]` bit **4** ON | disc **2** | optional save (`Var[13][0]=2`, sets bit 2 on [134] then clears), music #3, bit 1 on [137] | **lost2 (#634)** same |

### Patterns

- **Direct resume after save:** save branches set a sticky bit (5 or 2) +
  `Var[13][0] = target disc`, show save menu; on next load the *other* branch
  (bit 5 / bit 2 direct) can fire Ask without another prompt.
- **Post-ask always jumps** to a map that exists on all retail discs (shared FIELD set).
- Single-disc minimal edit: **remove or no-op each `Ask for disc N`**, keep waits/music/jumps/flags.

### Line numbers (inventory screenshot)

Earlier Find All lines 43/64 = disc 3 branches; 73/95 = disc 2. Exact line
numbers may shift in paste; use gates + jumps as identity.

## Related (same script, not Ask)

| Gate | Action |
|------|--------|
| `Var[3][136]` bit 7 | battle #468 → `roadend` (#226) |
| `Var[13][91]` bit 2 | bike mini-game intro UI |
| `Var[3][131]` bit 2 | **multi-disc movie** `rcktfail` / `rckethit1` / `No45` then `rktsid` (#558) |
| `$GameMoment == 638` | Aerith materia strip → `gninn` (#522) |

Movie branch is a second single-disc surface (pick D1 file or skip) — not required for Ask-no-op prototype.

## Minimal prototype (next)

1. Pristine D1 copy in Makou.
2. `blackbgb` / `init` / S0-Main: delete or skip all four `Ask for disc` ops only.
3. Save map; keep jumps to `lost2` / `las0_1`.
4. Optional: DS smoke if a save can set the gate bits; else script-only OK for now.

## Any-base note

Diff will be `FIELD/blackbgb.DAT` (and whatever Makou touches beside it). Verify
byte identity on CSR/Highwind later or ship per-base packs if those bases already
edited this map.
