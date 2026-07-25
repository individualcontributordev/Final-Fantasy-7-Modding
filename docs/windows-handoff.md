# Windows checklist (human)

**Status:** active

Report output in the **Mac Cursor chat**.

```bash
git pull --ff-only
```

---

## Goal

Find how StepID / RNG addresses appear in `FIELD.BIN.dec` (Ghidra scalar search found nothing).

## A. Byte search (Git Bash) — do this first

```bash
cd "$(git rev-parse --show-toplevel)"
python scripts/search_encounter_addrs.py workspace/iso-extract/FIELD.BIN.dec
# or: python3 scripts/search_encounter_addrs.py workspace/iso-extract/FIELD.BIN.dec
```

Copy the full script output into the Mac chat.

## B. Optional — Ghidra Memory search (not Scalars)

1. **Search → Memory…**
2. Hex: `40 C5 09 80`  (StepID pointer `0x8009C540` little-endian)
3. Search All
4. If no hits, try `B1 CA EE 6C` (confirm table only)

Do **not** spend time on Search → For Scalars for now.

## Tell the Mac chat

Paste the Python script output (or say it failed + error text).
