# Victory-skip battle patches

Retail stores field BTLMD/BTMD2 flags in RAM halfwords:

- 0x80062D7E
- 0x80062D7C

Bit 0x20 = do not run normal victory music/celebration (wiki BTLMD; train fights set this).

In decompressed BATTLE.X, each pattern:

    lhu  rT, 0x2D7E/0x2D7C(rX)
    nop
    andi r?, rT, 0x20
    beq  ...

has the nop replaced with: ori rT, rT, 0x20

22 sites — see force-no-victory-music-sites.txt.
