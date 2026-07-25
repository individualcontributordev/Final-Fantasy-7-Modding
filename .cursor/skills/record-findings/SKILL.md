---
name: record-findings
description: >-
  Records RE discoveries, Ghidra addresses, emulator settings, patch notes, and
  test results for the FF7 PS1 encounter RNG mod. Use when working in
  ff7-modding, after Ghidra/emulator sessions, when the user learns
  something useful, or when asked to document findings.
---

# Record Findings (FF7 PS1 Encounter Mod)

Capture durable knowledge in this repo so future sessions don't re-discover the same facts.

## Two layers of documentation

| Layer | Location | What goes here |
|-------|----------|----------------|
| **Findings journal** | `docs/findings/YYYY-MM-DD-slug.md` | Dated discoveries, session notes, raw RE output |
| **Reference docs** | `docs/0N-*.md` | Curated, stable guides (update when a finding is confirmed) |

**Journal first, merge later.** Write a finding immediately; promote to reference docs once verified.

## When to record

Record a finding when any of these are true:

- Ghidra address, function name, or byte offset identified
- Emulator RAM behavior confirmed or corrected
- Patch attempted (success or failure)
- Tool setting that affects accuracy or testing
- Contradiction with prior docs (note both sides)
- User says "remember this" or "document this"

## Create a finding file

1. Copy `docs/findings/_template.md`
2. Save as `docs/findings/YYYY-MM-DD-short-slug.md` (today's date, kebab-case slug)
3. Fill every section; skip only if truly N/A
4. Add a row to the index table in `docs/findings/README.md`

## Promote to reference docs

After a finding is **verified** (reproduced twice or confirmed in source):

| Topic | Update |
|-------|--------|
| Encounter RNG / RAM | `docs/01-encounter-system.md` |
| ISO / FIELD.BIN / Makou | `docs/02-disc-format.md` |
| Tools / emulator | `docs/03-environment-setup.md` |
| Patch workflow | `docs/04-workflow.md` |
| Ghidra procedure | `docs/05-ghidra-guide.md` |

Add a "Sources" link back to the finding file. Do not delete the journal entry.

## Patch log

Hardware-impacting changes also get `workspace/patches/YYYY-MM-DD-slug.md`
(see `docs/04-workflow.md`). Link the finding and the patch log to each other.

## Quality bar

Each finding must include:

- **What** was discovered (one sentence)
- **How** it was found (tool, steps)
- **Why it matters** for this project
- **Confidence**: confirmed / likely / unverified
- **Follow-ups** if any

Avoid duplicating entire reference docs inside findings — link instead.

## Related project paths

```
~/ff7-modding/
├── docs/findings/          ← journal (this skill)
├── workspace/iso-extract/  ← binaries (gitignored)
├── workspace/ghidra/       ← Ghidra projects
├── workspace/patches/      ← patch attempt logs
├── scripts/                ← decompress/recompress
~/makoureactor/             ← field editor source
~/ff7tk/                    ← ISO/FIELD.BIN library source
```

## Key facts (quick reference)

Do not duplicate long explanations here — see reference docs. Update these one-liners when confirmed:

- Encounter RNG lives in **FIELD.BIN** engine, not per-map `.DAT` files
- RNG table starts: `B1 CA EE 6C 5A 71 2E 55…`
- Target patch: reseed StepID/Offset/Formation on **field load**
- Makou/ff7tk: `IsoArchiveFF7::updateFieldBin()` rewrites gzip index on ISO save
- DuckStation: **Safe Mode** for hardware-accurate testing
