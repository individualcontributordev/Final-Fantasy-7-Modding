# Victory-skip battle patches

## Idea

Retail battle-mode flags live in RAM halfwords:

- 0x80062D7E
- 0x80062D7C

Relevant bits (BTMD2 / BTLMD wiki):

- 0x20 — do not play victory music
- 0x100 — party does not do victory celebrations (poses)

Also: scene flag byte 0x80109DA0 bit 0x20 skips writing victory anim index 7
into per-action tables (pose timing path).

## Patches (decompressed BATTLE.X)

1. After each:
       lhu  rT, 0x2D7E/0x2D7C(rX)
       nop
       andi r?, rT, 0x20
   replace nop with:
       ori  rT, rT, 0x120
   (music + no-pose bits).

2. After the sole:
       lhu  rT, 0x2D7E(rX)
       nop
       andi r?, rT, 0x100
   replace nop with:
       ori  rT, rT, 0x100

3. At file 0x547C (9da0 gate):
       nop  ->  ori r2, r0, 0x20
   so the check that skips victory anim index 7 always passes.

See force-no-victory-music-sites.txt (24 sites on NTSC-U).

## Apply

    python mods/victory-skip/scripts/apply_victory_skip.py path/to/BATTLE.X.dec
    python mods/victory-skip/scripts/build_battle_x.py path/to/BATTLE.X
