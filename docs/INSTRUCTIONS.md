# Task: Catch the real win-pose code address (DuckStation)

## Why the last breaks failed

Execute breaks at 800A54A0 / 800A5484 / 800A2974 / 800ABE4C were wrong for this job.

- FIELD, WORLD, and BATTLE all take turns in the **same code slot** around 800A0000.
- On the **world map**, 800A… is **world** code — so those breaks fire every frame while you idle.
- In **battle**, different bytes sit there. Our guessed pose spots often **never run**, so nothing hits until you leave battle and world code loads again (after rewards).

Do **not** keep those 800A execute breaks on.

## Goal this pass

When the party starts the win pose on a **normal** fight, read the yellow **PC** (code address). That is the real hook.

## Method A — pause by eye (simplest)

1. Turn **off** all old execute breaks on 800A…
2. Normal battle, Fanfare Skip 0.1.4 OK.
3. Save state before last kill.
4. Kill last enemy.
5. The moment win poses **start**, pause the emulator (Emulation pause), open CPU Debugger.
6. Screenshot or write down:
   - **pc** (yellow arrow / register pc)
   - **ra** (return address register), if shown
   - top few **Stack** return addresses if easy

If pause is a frame late, still useful — note pc anyway.

## Method B — break when battle exit status becomes Victory

RAM (not execute on 800A):

| Watch | Address | Size | Why |
|-------|---------|------|-----|
| Exit battle status | 800F83C6 | 1 byte | Notes: 1 = Victory |
| Enemy 1 current HP | 800F85AC | 2 bytes | Confirmed live HP |

1. Clear 800A execute breaks.
2. Add a **CPU/memory write** break on **800F83C6** (byte).
3. Optional: write break on **800F85AC** to see last-hit timing (may fire often — disable after last enemy is low).
4. Kill last enemy; when it breaks, check pc + whether value at 800F83C6 is 1.
5. Screenshot debugger.

If 800F83C6 never breaks during win/rewards, say so.

## Method C — only if A/B need backup

With debugger open mid-battle (before win), confirm you sometimes see **pc** in 800B…/800C…/800D… (battle overlay). Your earlier mid-battle shot had pc 800D3074 — that is normal for battle.

Do not set a thick grid of execute breaks across all of 800A–800E (too noisy).

## Write down

```
pc when poses start: ........
ra: ........
800F83C6 value at break/pause: ..
did write break on 800F83C6 hit: yes/no (count)
poses still played: yes
```

## Do not

- Do not leave execute breaks on 800A54A0 / 800A5484 / 800A2974 / 800ABE4C
- Do not use old Fanfare Skip before 0.1.4
- Do not poke memory by hand

## When done

Push a screenshot under docs/ or paste the pc/ra lines in chat.
