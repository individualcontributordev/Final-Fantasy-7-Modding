# Changelog

## 0.1.1 — 2026-08-08

- Also force no-victory-pose bit (0x100) and skip the victory anim index write
  (9da0 gate). v0.1.0 removed music only; poses could still play.

## 0.1.0 — 2026-08-08

- Initial ship: force train-style no-victory-music bit in BATTLE.X at battle-mode
  checks for 0x80062D7E / 0x80062D7C bit 0x20.
- Optional packs for clean, CSR, and Highwind (discs 1-3).
