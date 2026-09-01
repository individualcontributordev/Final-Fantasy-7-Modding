# Agent rules

Workflows: [README.md](README.md). Historical files: [ARCHIVED.md](ARCHIVED.md).

## Paths

- `~/Final-Fantasy-7-Modding` — this repo (addons + collapsed-base builders)
- `~/Final-Fantasy-7-CSR` — CSR / CSR+ / Highwind published **bases**
- `~/individualcontributordev.github.io` — builder UI
- `~/makoureactor`, `~/ff7tk` — opcode/maplist ground truth when needed

Missing paths are unavailable, not assumed.

## Ground truth

Hex offsets, MIPS stubs, and bytecode must be checked against `makoureactor` /
`ff7tk` or a file still in this repo. Unchecked claims are labeled
**UNVERIFIED ENGINE SPECULATION**.

## Binary edits

Map every offset before writing. Copy `FILE` → `FILE.bak` once per session.
Validate (re-parse, EDC, or an existing test) before calling the edit done.

## Scope

Allowed: Python under `scripts/` and `mods/*/scripts/`, edits to docs the user
is discussing, the README/ARCHIVED pair.

Ask first: new dependencies, extra Markdown beyond README/ARCHIVED, destructive
writes to original game assets without a `.bak`.
