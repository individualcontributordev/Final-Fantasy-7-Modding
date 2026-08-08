# Battle victory fanfare — mod feasibility

**Date:** 2026-08-08  
**Ask:** Remove or shorten the end-of-battle fanfare to speed battles.  
**Status:** feasible as optional engine/sound mod; not implemented yet

## What the fanfare is

- Asset: `ENEMY6/FAN2.SND` on Disc 1 (~2420 bytes).
- Format: AKAO sequence, **song id 47** in the file header.
- Sister file: `ENEMY6/OVER2.SND` (game over sting) — leave alone.
- Docs already list this under open ideas: `docs/SUGGESTIONS.md` (battle pacing).

Victory is not only music: battle also runs win pose / brief end wait. Cutting
**only** the fanfare track shortens audio; full “instant exit” needs battle-code
timing as well.

## Why a separate mod makes sense

- Optional (some players like the fanfare).
- Engine/sound layer in **this** repo, not a cutscene/Makou field pack.
- Same class as encounter-rate mods (builder add-on on CSR / Highwind / clean).

## Likely approaches (light → heavy)

| Approach | Idea | Risk | Speed gain |
|----------|------|------|------------|
| A. Silence / stub `FAN2.SND` | Replace with tiny silent or near-empty AKAO still id 47 | Low if header/id kept; test all win paths | Stops music; may still wait “fanfare length” |
| B. Shorten AKAO sequence | Keep id 47, truncate notes so it ends in &lt;1s | Low–med | Good if engine waits on song end |
| C. Battle binary skip | Patch decompressed `BATTLE/BATTLE.X` win state: don’t play fanfare and/or skip wait | Med–high (gzip + 8-byte header reinsert) | Best time-save |
| D. Global battle-mode flag | Field “battle mode” bits (qhimm: skip battle BGM style flags) — may not cover fanfare | Unknown without RE | Maybe |

**Recommended first spike:** B or A on a work bin, DuckStation full win (normal + boss + escape-fail), then C if wait remains.

## Shipping shape (if it works)

- Pack id sketch: `battle-fanfare-off-v0.1.0` (name TBD).
- `compatibleBases`: clean, csr-v0.14.1, highwind-v0.2.0.
- Exclusive group if multiple intensities later (mute vs skip-wait).
- Not tied to single-disc.

## Out of scope for v1

- Battle intro flash shorten  
- Death / game-over sting (`OVER2.SND`)  
- Super Nova / long in-battle cinematics  

## Next concrete steps

1. Work copy of pristine D1; back up `ENEMY6/FAN2.SND`.  
2. Spike silent/short AKAO; document wait behavior.  
3. If still slow: Ghidra win-state in decompressed `BATTLE.X` (song 47 / fanfare call).  
4. Layer + builder entry only after console-ish playtest.
