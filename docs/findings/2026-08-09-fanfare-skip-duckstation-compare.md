# Fanfare Skip — live DuckStation compare (normal vs train win)

**Date:** 2026-08-09  
**Status:** waiting on human notes (`docs/INSTRUCTIONS.md`)  
**Mod under test:** Fanfare Skip v0.1.4 (`0110cf4`)

## Playtest report (v0.1.4)

| Item | Result |
|------|--------|
| Auto-confirm / stuck confirm | **Fixed** (mode-bit force removed) |
| Victory music | **Off** (good) |
| Win poses | **Still play** |
| Stuck / glitched audio until rewards close | **Still happens sometimes** |

## What v0.1.4 did

- No global force of battle-mode `0x20` / `0x100`
- Stub victory-queue function at file off `0x2974` (only direct `jal` was `@0xbe4c`)
- Quiet `ENEMY6/FAN2.SND`

Stub alone is **not** enough for poses. Music request paths still exist outside that function (e.g. stores of AKAO id `0x2F` / 47 at `0x1ce0`, `0x2adc` inside the stubbed range, `0x8658`).

## Static candidates (for after live compare)

| Region | Role |
|--------|------|
| `0x5250` | Party action / anim setup; case table around `0x5404` |
| `0x5494–0x54a4` | When mode byte bit `0x20` clear, writes anim index `7` (win pose) |
| `0x80062D7C` | Battle mode halfword (train sets skip bits from field) |
| AKAO id `0x2F` | Fanfare request — engine may still “start” track even if FAN2 is silent → stuck driver until rewards UI |

**Do not** re-force mode bits globally without checking confirm/UI. Prefer NOP/skip of pose write + never request track 47 on win.

## Human task

See root `docs/INSTRUCTIONS.md` — normal win vs train win memory/PC notes.
