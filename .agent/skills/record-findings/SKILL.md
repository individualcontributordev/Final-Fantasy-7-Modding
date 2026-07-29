---
name: record-findings
description: >-
  Records RE discoveries, Ghidra addresses, emulator settings, patch notes, and
  test results for FF7 PSX disc modding. Use when working in Final-Fantasy-7-Modding, after
  Ghidra/emulator sessions, when the user learns something useful, or when asked
  to document findings.
---

# Record Findings (FF7 PSX Modding)

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
- Disc/ISO/file format behavior clarified
- Emulator RAM or hardware test result
- Patch attempted (success or failure)
- Tool setting that affects accuracy or testing
- Contradiction with prior docs (note both sides)
- User says "remember this" or "document this"
- After **check results**: useful content appeared in `docs/windows-last-output.txt` (pasted listing/decompiler)

User-facing next steps always go **in chat** as **one atomic task** (full GUI/commands, addresses, expected observations). File has COPY-PASTE values + EVIDENCE paste only — **never** yes/no answer blanks. See `.cursor/rules/mac-human-workflow.mdc`.

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
| New topic | New `docs/0N-topic.md` + row in `docs/00-goals.md` |

Add a "Sources" link back to the finding file. Do not delete the journal entry.

## Patch log

Hardware-impacting changes also get a finding under `docs/findings/` and, when
shipping, stub notes under `mods/<mod>/patches/` (see `docs/04-workflow.md`).

## Quality bar

Each finding must include:

- **What** was discovered (one sentence)
- **How** it was found (tool, steps)
- **Why it matters** for PSX disc modding
- **Confidence**: confirmed / likely / unverified
- **Follow-ups** if any

Avoid duplicating entire reference docs inside findings — link instead.

## Related project paths

```
~/Final-Fantasy-7-Modding/
├── docs/findings/
├── mods/<mod>/patches/
├── workspace/iso-extract/
├── workspace/ghidra/
├── scripts/
~/makoureactor/
~/ff7tk/
```

## Key facts (quick reference)

Update when confirmed; see reference docs for detail:

- PSX FF7 uses custom indexes in `FIELD.BIN` (not ISO dir alone)
- Makou/ff7tk `pack()` updates gzip indexes on ISO save
- GZIPPS: 8-byte header then gzip (`scripts/decompress_gzipps.py` / `compress_gzipps.py`)
- DuckStation **Safe Mode** for hardware-like testing
- Encounter FORCE stubs: Light/Standard/Dense presets only (`mods/.../scripts/density.py`)
- Players apply packs via https://individualcontributor.dev/builder/ (this repo is CDN + research)
