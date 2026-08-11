# Task: Retest CSR+ single-disc after D2/D3 trims on D1

## What changed

CSR+ **Hojo / COTA / endgame** packs now ship **disc1** layers so a Disc 1
single-disc build gets those FIELD trims (before: disc2/disc3 only).

Also shipped: **Single-disc on Highwind** (`single-disc-on-highwind-v0.1.0`).

Hard-refresh the builder first.

## Build A — CSR + CSR+ + Single-disc

- Base: CSR
- Mods: CSR+, Single-disc (encounters/fanfare optional)
- Disc 1

Check APPLIED.txt lists CSR+ packs (hojo/cota/endgame/aerith as applicable).

Play toward crater / late D1 and note if trims feel present vs earlier missing trims.

## Build B — Highwind + Single-disc (smoke)

- Base: Highwind
- Mods: Single-disc
- Confirm endings in APPLIED.txt
- Boot + short play

## Evidence

```
Build A APPLIED packs:
Crater / late game with CSR+: OK / FAIL
notes:

Build B Highwind + SD: boot OK? YES/NO
notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
git add docs/INSTRUCTIONS.md
git commit -m "ops: retest CSR+ SD after disc1 CSR+ layers"
git push
```

Then say **check**.
