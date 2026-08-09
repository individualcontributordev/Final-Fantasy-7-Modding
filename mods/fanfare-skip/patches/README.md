# Fanfare-skip battle patches

## What

Skip victory fanfare music and win poses after battles (train-style), without
hiding loot/exp screens.

## Technique (NTSC-U BATTLE.X, decompressed)

1. **Music bit (BTLMD 0x20)**  
   At each load of battle-mode halfword 0x80062D7E / 0x80062D7C that tests bit 0x20,
   replace the delay-slot nop with:
       ori rT, rT, 0x20
   so the official "no victory music" switch always reads on.

2. **Win pose / fanfare queue**  
   At file offset 0x2A08, the win path does:
       andi r2, r2, 0x1
       bne  r2, r0, skip   ; if already flagged, skip
       ... queue victory anim + fanfare id 47 ...
   Replace that bne with always-branch (beq r0,r0,skip) so the queue never runs.
   That stops party win poses (and a second fanfare path).

## What we do NOT force

- Bit 0x100 ("no celebration" in BTMD2 docs) — toggling it touched end-of-battle
  UI flags and caused auto-confirm / context-bar glitches in v0.1.1–0.1.2.
- Reward-screen hide bit (0x80).

## Sites

See force-no-victory-music-sites.txt.

## Apply

    python mods/fanfare-skip/scripts/apply_fanfare_skip.py path/to/BATTLE.X.dec
    python mods/fanfare-skip/scripts/build_battle_x.py path/to/BATTLE.X
