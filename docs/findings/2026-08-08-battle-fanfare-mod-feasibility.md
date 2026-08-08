# Battle victory sequence skip — mod feasibility

**Date:** 2026-08-08 (updated)  
**Ask:** End every battle before victory song + win poses (like train fights).  
**Status:** game already has this mode; best path is force those flags globally


## Implementation (v0.1.0)

Shipped as optional builder mod **Victory Skip**:

- mods/victory-skip/ — apply + pack build scripts
- Packs: victory-skip-v0.1.0, victory-skip-on-csr-v0.1.0, victory-skip-on-highwind-v0.1.0
- Technique: in decompressed BATTLE.X, 22 sites load RAM halfwords 0x80062D7E / 0x80062D7C and test bit 0x20 (no victory music). Each delay-slot nop after the load is replaced with ori rT, rT, 0x20 so the bit always reads set.
- Not field patches. Rewards screens unchanged (bit 0x80 not forced).
- Playtest needed: randoms, bosses, train (should stay fine), arena, level-up still shows.

## What you noticed (train battles)

Train fights skip the celebration on purpose. Square set **battle mode** bits from
field scripts, not a one-off train hack.

### Official flags (field opcodes)

**BTLMD (0x72)** — one-byte bitfield (wiki):

| Bit | Effect when set |
|-----|-----------------|
| 0x20 | Do not play battle victory music |
| 0x80 | Do not show AP/EXP/Gil/item receive screens |

**BTMD2 (0x22)** — extended bitfield (wiki), includes e.g.:

| Bit | Effect when set |
|-----|-----------------|
| 0x20 | Do not play victory music (same idea) |
| 0x01 | Party does **not** perform victory celebrations |

Combine **no music + no victory poses** for “leave like the train.”

### Example on Disc 1 fields (pristine scan)

| Field | What we saw |
|-------|-------------|
| `SMKIN_4.DAT` | `BTLMD` with raw `722200` (includes **0x20** — no victory music) |
| `TRNAD_4.DAT` | `BTLMD` `720800` (no-escape style; other train maps mostly set battle music) |

Not every train map sets the same bits; the **engine support** for skip-music /
skip-poses is what matters. Train sequence uses that machinery.

## Product goal

Last enemy dies → **no fanfare, no win poses** → exit battle (rewards still apply).

Mute-only `ENEMY6/FAN2.SND` is **not** enough.

## Best implementation paths

| Path | Idea | Pros | Cons |
|------|------|------|------|
| **A. Force battle-mode bits in engine** | When any battle starts (or when win is decided), OR in 0x20 + pose-skip bits as if field set BTMD2/BTLMD | One hook; matches retail train behavior | Need RAM address of battle mode + where field copies it into battle |
| **B. Jump win-state in `BATTLE.X`** | Skip victory state → teardown after rewards | Full control | Heavier RE; same as earlier plan |
| **C. Patch every field** | Inject BTLMD/BTMD2 before every BATTLE | No battle binary | Huge, miss world-map / randoms |

**Prefer A**, then B if the mode bits only kill music/poses but still wait.

## Rewards / UI

Flag 0x80 skips **reward screens** — that may speed more but changes UX (no loot
popup). Product default should probably:

- skip music + poses  
- **keep** exp/AP/gil/item grants and screens unless we offer a second “turbo” option  

Confirm train fights: do they still give rewards quietly? (usually yes, with 0x80).

## Fanfare asset (secondary)

`ENEMY6/FAN2.SND` AKAO id **47** — only needed if something still starts the song.

## Shipping

Optional builder mod: “Skip battle victory (train-style)” on clean/CSR/Highwind.  
Independent of single-disc.

## Spike

1. Document battle-mode RAM / load from field → battle (Ghidra).  
2. Force pose-skip + no-victory-music bits for all battles on a work bin.  
3. DuckStation: randoms, bosses, train (idempotent), arena.  
4. If wait remains, add BATTLE.X exit jump.

## Related

- Wiki: BTLMD 0x72, BTMD2 0x22  
- `docs/SUGGESTIONS.md` battle pacing  
