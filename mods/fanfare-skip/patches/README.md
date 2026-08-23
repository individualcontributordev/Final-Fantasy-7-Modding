# Fanfare-skip patches

## v0.1.5 approach (current)

**Ship: BATTLE.X victory-queue stub only. Leave stock FAN2.SND.**

| Piece | Ship? | Role |
|-------|-------|------|
| BATTLE.X @ file+0x2974 early return | **yes** | Skips victory queue (poses / ceremony path) |
| ENEMY6/FAN2.SND quiet (zero body) | **no** | Causes held frozen tone until field |

### Why quiet FAN2 was removed

FAN2.SND.quiet keeps a 16-byte AKAO header from stock FAN2 and zeros the rest.
As the fanfare track it does not silence cleanly — SPU hangs on a tone until
field/world reloads audio. Stock ISO and stub-only images do not freeze.

### History

- 0.1.4 shipped stub + quiet FAN2 = freeze regression.
- 0.1.3 and earlier used battle-mode bit forces (auto-confirm / pose issues).

## Files

- force-no-victory-music-sites.txt — BATTLE.X word patches (shipped)
- FAN2.SND.quiet.layer.json — ic-layer-v1 diff vs stock FAN2.SND, research only (reproduces freeze; not default)
- fan2-quiet-source.txt — how quiet asset was produced

## Apply

```bash
python mods/fanfare-skip/scripts/apply_fanfare_skip.py path/to/BATTLE.X.dec
python mods/fanfare-skip/scripts/build_on_base.py --against clean --discs 1
# research freeze only: add --quiet-fan2 or --fan2-only
```
