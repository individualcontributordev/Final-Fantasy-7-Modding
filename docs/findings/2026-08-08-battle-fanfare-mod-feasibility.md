# Battle victory sequence skip — mod feasibility

**Date:** 2026-08-08 (updated same day)  
**Ask:** After the last enemy falls, skip victory **song and win animations**. End the fight
**before** those start (straight back to field / next step).  
**Status:** feasible as optional battle-engine mod; mute-only is **not** enough; not implemented

## Goal (player-facing)

Normal win today: last hit → party victory poses + fanfare → then leave battle.

Wanted: last hit → **leave battle immediately** (no poses, no fanfare wait).

Silencing `ENEMY6/FAN2.SND` alone is **out of scope as the product** — music can stop
while poses/wait still burn time.

## What the game does today (rough)

1. Battle decides “all enemies dead / win.”
2. Enters a **victory state**: play win animations on party; start fanfare AKAO.
3. Fanfare asset: `ENEMY6/FAN2.SND` (~2420 bytes), AKAO **song id 47**.
4. After that sequence finishes (or is dismissed), tear down battle and return to field.

Product fix must interrupt or never enter step 2 — jump to teardown.

## Why not file-mute only

| Approach | Music | Poses / wait | Matches ask? |
|----------|-------|--------------|--------------|
| Silent / short `FAN2.SND` | Gone/short | **Still there** | **No** |
| Patch battle win state in `BATTLE/BATTLE.X` | Skipped if never started | Skipped if state jumped | **Yes** |

## Recommended approach

**Primary:** RE + patch **decompressed** `BATTLE/BATTLE.X` (8-byte header + gzip body on disc):

1. Find win-state entry (fanfare play + victory anim setup).
2. Branch straight to battle-exit / return-to-field path used after a normal win.
3. Must still run reward grants (exp/AP/gil/items) on the success path — only skip
   the **presentation** (poses + song + wait).
4. Preserve lose / game-over; test bosses and scripted wins after v1 hook.

Repack: strip/restore BATTLE.X header, gzip `-n` (known qhimm procedure).

## Risks

| Risk | Notes |
|------|--------|
| Softlock if exit skips cleanup | Rewards must still apply |
| Boss / scripted battles | May assume win length; test carefully |
| Escape / lose | Must not touch lose path (`OVER2.SND`) |
| Level-up UI | Confirm when it queues vs after fanfare |

## Shipping shape (if spike works)

- Optional builder mod on clean / CSR / Highwind.
- Name sketch: “Skip battle victory” / `battle-victory-skip-v0.1.0`.
- Independent of single-disc.

## Spike plan

1. DuckStation + Ghidra on decompressed `BATTLE.X`: win state / song 47 / victory anim.
2. Force jump from “start victory sequence” → “finish battle success” (after rewards).
3. Verify exp/AP/items; field return; normal + boss fights.
4. Layer + ship only after that.

## Related

- `docs/SUGGESTIONS.md` — battle pacing  
- Asset only (not full fix): `ENEMY6/FAN2.SND` id 47  
