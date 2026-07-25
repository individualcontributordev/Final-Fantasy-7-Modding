# Windows checklist (human)

**Status:** active

**Shell:** Git Bash  
Report in the **Mac Cursor chat**.

```bash
git pull --ff-only
```

---

## Goal

Find encounter RNG **code** via StepID scalar search (table xrefs were 0 — expected).

## Steps (Ghidra)

1. **Search → For Scalars…**
2. Value: `0x9c540` (hex) — this is the low part of StepID `0x8009C540`
3. Search — open hits that look like:
   - `lui …, 0x8009` then `lbu`/`sb` with offset `0xc540`, or similar
4. Go to that instruction → press **F** if needed to make a function
5. In Listing / Decompiler, look for:
   - byte++ (StepID)
   - add `0xd` / `13` (Offset bump on wrap)
   - load from something near `0x80040638` / indexed byte load
6. If you find it, label the function `increment_step_id` (`L` on function name)

If `0x9c540` finds nothing, try scalar `0x9ad2c` (Offset) or `0x7173c` (Danger).

## Tell the Mac chat

- Scalar searched
- Number of hits
- Address of the best hit (and function name if any)
- Whether decompiler shows step/offset/`0xd`
- Or “no hits”
