# FF7 PS1 Encounter Mod

Make field (and eventually world-map) random encounters unpredictable instead of
deterministic — so speedrun-style routing and stutter-step manipulation no longer
apply.

## Status

**Planning / environment setup.** No patches applied yet.

## Project layout

```
ff7-modding/
├── AGENTS.md                 Cursor agent guide
├── README.md                 ← you are here
├── .cursor/
│   ├── rules/                Always-on: capture findings
│   └── skills/record-findings/  Skill: how to document discoveries
├── docs/
│   ├── 00-goals.md           Project goals and success criteria
│   ├── 01-encounter-system.md How FF7 encounter RNG actually works
│   ├── 02-disc-format.md     ISO, FIELD.BIN, Makou Reactor save path
│   ├── 03-environment-setup.md Tool install checklist (start here)
│   ├── 04-workflow.md        Edit → rebuild → test loop
│   ├── 05-ghidra-guide.md    RE workflow for FIELD.BIN
│   └── findings/             Dated lab notebook (index in README.md)
├── scripts/
│   ├── decompress_field_bin.py
│   └── compress_field_bin.py
└── workspace/                Working copies — never commit your ISO here
    ├── iso-extract/          Extracted FIELD.BIN, FIELD.BIN.dec, etc.
    ├── ghidra/               Ghidra projects and exports
    └── patches/              Patch notes, byte diffs, assembled stubs
```

## Research journal

Discoveries are recorded in [docs/findings/](docs/findings/README.md) as we work.
Cursor agents auto-capture via `.cursor/rules/capture-research-findings.mdc` and
the [record-findings](.cursor/skills/record-findings/SKILL.md) skill.

## Where to start

1. Read [docs/03-environment-setup.md](docs/03-environment-setup.md) and work through the checklist.
2. Extract `FIELD.BIN` from a disc you own into `workspace/iso-extract/`.
3. Run `scripts/decompress_field_bin.py` and confirm output size looks sane.
4. Open [docs/05-ghidra-guide.md](docs/05-ghidra-guide.md) when Ghidra is installed.

## Related repos (already cloned)

| Repo | Path | Role |
|------|------|------|
| Makou Reactor | `~/makoureactor` | Field editor, ISO save/rebuild |
| ff7tk | `~/ff7tk` | ISO/FIELD.BIN library used by Makou |

## Key insight

Makou edits per-map `.DAT` data (scripts, encounter tables, rates). The encounter
**timing and formation RNG** lives in `FIELD.BIN` engine code. This project patches
`FIELD.BIN` (and later `WORLD.BIN`), not individual field files.
