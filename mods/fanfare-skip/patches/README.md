# Fanfare-skip patches

## v0.1.4 approach (current)

Earlier builds forced battle-mode bit 0x20 globally. That killed fanfare music
but also pushed every fight onto a special end-of-battle path that:
- still showed win poses, and
- left the confirm action auto-firing (held-confirm feel).

**0.1.4 does not force any battle-mode bits.**

Instead:

1. **BATTLE.X** — replace the victory queue function at decompressed file
   offset 0x2974 with an immediate return (6 words). Stock already calls this
   for the win ceremony path; train-like early exit does not need it.
2. **ENEMY6/FAN2.SND** — keep AKAO header / song id, zero the sequence body so
   if anything still requests the fanfare track it is effectively silent.

## Files

- force-no-victory-music-sites.txt — BATTLE.X word patches
- FAN2.SND.quiet — silent-ish fanfare asset (same max size as stock FAN2)

## Apply

    python mods/fanfare-skip/scripts/apply_fanfare_skip.py path/to/BATTLE.X.dec
    python mods/fanfare-skip/scripts/build_on_base.py --against clean --discs 1
