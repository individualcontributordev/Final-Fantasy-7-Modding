# Task: Bisect crater freeze (single-disc + CSR+)

## Context

Freeze **entering the crater before Hojo** on Disc 1:

CSR + **CSR+** + Single-disc + Fanfare off + Field encounters Light 25%.

Main playtests so far: **single-disc + CSR without CSR+**. CSR+ Hojo/COTA packs are **Disc 2 layers only** — they never patch a Disc 1 single-disc image. Crater/Hojo maps on that image are CSR **D2 fields merged onto D1**.

Finding: [findings/2026-08-10-single-disc-csrplus-crater-hojo-freeze.md](findings/2026-08-10-single-disc-csrplus-crater-hojo-freeze.md)

## What you do

### 0. Confirm the bad zip

Open **APPLIED.txt**. Note packs. Paste into Evidence.

### 1. Three builds (hard-refresh builder)

Same save approaching the crater when possible.

**A — CSR + Single-disc only** (no CSR+, default encounters, fanfare off)

**B — CSR + Single-disc + CSR+** (default encounters, fanfare off)

**C — your stack** (CSR+ + Single-disc + Field Light 25% + fanfare off)

### 2. At the freeze

- Last map name if known
- Softlock (menu works) vs hard freeze
- Repro every time?

## Evidence

```
APPLIED.txt packs (bad zip):

Build A (CSR + SD only): crater OK? YES/NO
Build B (CSR + SD + CSR+): crater OK? YES/NO
Build C (full): crater OK? YES/NO

Map at freeze:
Softlock or hard freeze:
Repro every time? YES/NO
notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
git add docs/INSTRUCTIONS.md
git commit -m "ops: bisect single-disc CSR+ crater freeze"
git push
```

Then say **check**. Do not commit .bin images.
