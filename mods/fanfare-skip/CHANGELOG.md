# Changelog

## 0.1.3 — 2026-08-09

- Fix poses still playing: skip the victory anim/fanfare queue in BATTLE.X.
- Remove bit 0x100 force (was flipping end-battle UI: auto-confirm / context bar).
- Keep only no-music bit 0x20 for the fanfare song.


## 0.1.2 — 2026-08-09

- Rename to Fanfare Skip (clearer name).
- Builder checkbox shows short help text (hint) plus longer tooltip (blurb).


## 0.1.1 — 2026-08-08

- Also force no-victory-pose bit (0x100) and skip the victory anim index write
  (9da0 gate). v0.1.0 removed music only; poses could still play.

## 0.1.0 — 2026-08-08

- Initial ship: force train-style no-victory-music bit in BATTLE.X at battle-mode
  checks for 0x80062D7E / 0x80062D7C bit 0x20.
- Optional packs for clean, CSR, and Highwind (discs 1-3).
