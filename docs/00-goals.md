# Goals

## Project scope

**FF7 PSX disc modding** — understand, change, and rebuild PlayStation disc images so
mods remain playable on console hardware (and test accurately in emulators).

This includes:

- ISO / sector layout and Square’s custom indexes (`FIELD.BIN`, `WORLD.BIN`, etc.)
- Per-map field data (`.DAT` and related files) via tools like Makou Reactor
- Engine binaries in gzip blobs on the disc (RE in Ghidra, MIPS patches)
- Workflow: extract → edit → recompress → reinsert → verify

**Platform:** PS1 (PSX) disc images only for now — not PC / 7th Heaven.

**Out of scope (unless we explicitly add them):** PPF distribution, piracy, sharing disc images.

## Topic areas

Work is organized by topic. Each gets reference docs and findings as we learn.

| Topic | Docs | Notes |
|-------|------|-------|
| Disc & ISO | `02-disc-format.md`, `04-workflow.md` | Makou/ff7tk save path, GZIPPS |
| Tooling | `03-environment-setup.md`, `git-setup.md` | DuckStation, Ghidra, scripts |
| Field encounter RNG | `01-encounter-system.md` | **First research thread** — not the whole project |
| *(future)* | TBD | Kernel, battle, world map, scripts, etc. |

New topics: add `docs/0N-topic.md` + findings; update this table and the README.

### Encounter RNG (current research thread)

One candidate mod: make field encounters less deterministic (speedrun routing today
relies on predictable StepID/Offset/Danger). See
[findings/2026-07-25-patch-target-field-load-reseed.md](findings/2026-07-25-patch-target-field-load-reseed.md).

That idea requires patching `FIELD.BIN` (and eventually `WORLD.BIN`), not just Makou
field edits.

## Success criteria — “environment ready”

Applies to any mod work in this repo:

- [ ] Clean FF7 PS1 disc image (`.bin` + `.cue`) in `workspace/iso-extract/`
- [ ] Can extract key files (`FIELD.BIN`, etc.) from the image
- [ ] `scripts/decompress_field_bin.py` runs successfully
- [ ] Emulator boots the image (DuckStation Safe Mode — see findings)
- [ ] Ghidra project created under `workspace/ghidra/`
- [ ] Can recompress, reinsert into ISO, and boot again

Topic-specific milestones (e.g. find RNG table in Ghidra) live in findings and topic docs.

## Principles

1. **Console-first** — if it doesn’t work on hardware, it’s not done (emulator is for dev).
2. **Document as we go** — findings journal + reference docs, not chat-only knowledge.
3. **Pristine backups** — never edit the only copy of a source ISO.
4. **Minimal patches** — smallest change that achieves the goal; avoid unrelated edits.
