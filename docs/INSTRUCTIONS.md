# Fanfare-skip v0.1.6 — confirmed

## Operator result

Image / pack: **fanfare-skip-v0.1.6** (BATRES ceremony skip-setup)

- Fanfare music: **none**
- Win poses: **none**
- Battle end / rewards / return to field: **OK**
- Freeze: **no**

Status: **working fine** — ship accepted.

## What shipped

- `builder/fanfare-skip-v0.1.6` (clean)
- `builder/fanfare-skip-on-csr-v0.1.6`
- `builder/fanfare-skip-on-highwind-v0.1.6`
- Manifest: 0.1.6 enabled, 0.1.5 disabled

Patch: BATRES.X only — force skip of ceremony setup at 801B02E0 (plus s4=0 / nop 7254).
Does not quiet FAN2.SND.

Finding: [findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md](findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md)

## Next

No operator task. Idle until a new goal.
