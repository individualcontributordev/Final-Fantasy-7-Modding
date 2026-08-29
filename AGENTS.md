# AGENTS.md — FF7 Modding/RE Workspace Rules

Operating rules for AI agents working in this repository. Note: these are
followed *when the agent is actively invoked on a task* — an agent has no
persistent background process, so anything described as "automatic" below
means "the agent will do this as part of the current tool-driven task,"
not an always-on daemon.

## Reference paths
Consulted when relevant to the task at hand:
- `~/Final-Fantasy-7-CSR` — workspace notes/logs, `field_maplist.py`
- `~/Final-Fantasy-7-Modding` — this repo (active modding codebase)
- `~/Final-Fantasy-7-RE-Archive` — historical/superseded findings, old Ghidra
  CLI logs, script pastes (moved out of this repo to keep default context
  lean). Each entry has a `STATUS: CONFIRMED|UNCONFIRMED|DEAD-END` header and
  is indexed in that repo's `INDEX.md`. Only consult on request or when doing
  deep RE history digging — never treat archive content as live ground
  truth; use `scripts/field_pattern_finder.py` /
  `scripts/duckstation_addr_advisor.py` and `docs/05-ghidra-guide.md` for that.
- `~/individualcontributordev.github.io` — mod site frontend
- `~/makoureactor` — Makou Reactor engine source (opcode/maplist ground truth)
- `~/ff7tk` — FF7TK library source
- `~/Downloads/ghidra_12.1.2_PUBLIC` — Ghidra, for MIPS/decompiler work if needed

Paths that don't exist on disk when checked are treated as unavailable, not
assumed.

## 1. Reverse-engineering ground-truth rule
- Any hex offset, MIPS stub, or bytecode parse must be cross-checked against
  a local source of truth (`makoureactor`/`ff7tk` source, or files already in
  this repo like `scripts/ff7_opcodes.py`) before being asserted as fact.
- Qhimm Wiki lookups happen only when the `web-search`/`web-fetch` tools are
  actually invoked in-session — a rule can't force a search that doesn't
  happen; if no verification source was checked, the claim is flagged.
- Unverified values are explicitly labeled **"UNVERIFIED ENGINE SPECULATION"**
  in output rather than presented as fact.
- Before hand-deriving a field-script opcode offset or a DuckStation RAM
  address, run `scripts/field_pattern_finder.py` / `scripts/duckstation_addr_advisor.py`
  and use their `[CONFIRMED]`/`[UNCONFIRMED: <reason>]` tags (see
  `scripts/README.md` "Verification contract" and
  `docs/10-patch-workflow-cheatsheet.md`) instead of guessing by eye.

## 2. Local playtesting & binary-edit workflow
Before writing bytes to any binary (ISO, FIELD.BIN, MOVIE_ID.BIN, etc.):
1. Map out every affected offset/address and state the expected before/after
   values.
2. Create a `.bak` copy of the target file before the first write
   (e.g. `FIELD.BIN` → `FIELD.BIN.bak`), never overwrite a `.bak` that already
   exists for the same session.
3. After editing, run a validation pass (checksum/EDC check, struct re-parse,
   or an existing test/script) and report pass/fail before declaring the edit
   done.

## 3. Verified-insight logging (manual, on request)
- Location: `.workspace/verified_insights/organic_growth.jsonl` (created on
  first use).
- When a user confirms a fix passed a live playtest and asks for it to be
  logged, the agent appends one JSONL row in the same
  `{"instruction", "input", "output"}` (with `<thinking>` + self-contained
  code) format as `data/ff7_re_dataset.jsonl`, respecting the Self-Contained
  Code Rule.
- This is done per explicit request or explicit confirmation of a verified
  result — not silently inferred from conversation.

## 4. Scope & file safeguards
Allowed without asking:
- Python automation/patch scripts under `scripts/`, `data/`, or workspace
  temp locations (temp scripts deleted after use unless the user asks to
  keep them).
- Edits to existing docs/config the user is actively discussing.

Requires explicit ask first:
- Adding new dependencies or changing dependency versions.
- New Markdown/doc files beyond what's explicitly requested.
- Bulk unstructured text dumps (large prose dumps, changelog rewrites, etc.).
- Any destructive operation on original game assets without a `.bak` in place
  first.
