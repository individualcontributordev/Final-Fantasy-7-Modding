# Task: Compare a normal win vs a train-style win (DuckStation)

## Why

Fanfare Skip **v0.1.4** already:

- keeps **confirm** normal (no stuck “button held”)
- keeps **music** off most of the time

Still wrong:

- **win poses** still play on a normal fight
- **sound can stick** until you close the rewards screen

We need a live side-by-side in DuckStation so the next patch only cuts the win show — not by forcing the old global switches that broke confirm.

## What you need

- DuckStation with the **debug** view (breakpoints / memory)
- One disc image with **Fanfare Skip v0.1.4** on (same pack you just tested)
- Optional: a second run on **clean** stock if you want, but modded is enough if you can reach a train fight and a normal fight

## Setup (once)

1. Open the disc in DuckStation.
2. Turn on the debugger (or “Show debug” / CPU debugger — whatever your build calls it).
3. Make a **save state right before the last enemy dies** for each fight type when you can.

## Fight A — normal random

1. Get into any normal random battle.
2. Save state just before the finishing blow.
3. Kill the last enemy.
4. Watch until win poses start (or until rewards).

**Write down:**

- Does the win pose still play? (yes/no)
- Does music glitch or stick until rewards close? (yes/no)
- In the debugger, as soon as the last enemy dies, open memory and note the value at:

  `80062D7C`

  (two-byte value; paste the hex you see right after the kill and again when poses start)

- If you can: the **code address** (PC) when the first party member starts the win pose. One address is enough; a short call stack is better if easy.

## Fight B — train (or any fight that already skips the show)

Same steps as Fight A on a train battle (or any fight that already cuts out with no poses).

**Write down the same list**, especially the value at `80062D7C` right after the kill.

## What “good notes” look like

Paste something like this in chat (or commit under `docs/playtest/` if you prefer):

```
normal:
  poses: yes
  stuck sound: yes/no
  80062D7C after kill: ????
  80062D7C when pose starts: ????
  PC when pose starts: ????????

train:
  poses: no
  stuck sound: n/a or no
  80062D7C after kill: ????
  PC after kill (first stop): ????????
```

## Do not

- Do not turn old Fanfare Skip packs (0.1.3 and earlier) back on for this test
- Do not change code yourself for this task — notes only
- Do not force memory bits by hand unless we ask later (that’s how confirm broke before)

## When you’re done

Paste the notes here. Next patch will target only the win-show path from those addresses.
