# Engineer Curriculum — FF7 PSX Disc Modding

A sequenced path through this repo's existing docs for someone who has never
touched the project, ending with the ability to independently RE a new
engine behavior and ship it as a builder pack. Every module below is an
**existing doc** unless marked **(new)** — this page is the index/order, not
a duplicate of their content, per `.agents/rules/keep-repo-succinct.mdc`.

## Prerequisites

- Own a legal rip of FF7 PSX discs 1-3 (never commit them — `03-environment-setup.md`)
- Comfortable with Python and basic binary/hex concepts (bytes, endianness, offsets)
- macOS or Windows+Git Bash; DuckStation; Ghidra 11+; Java 21

## Module 1 — Environment and mental model

| Read | Why |
|---|---|
| `docs/00-goals.md` | What this project ships and why (context for every later decision) |
| `docs/03-environment-setup.md` | Install everything: emulator, Ghidra, Makou Reactor, hex tool |
| `docs/02-disc-format.md` | PSX disc layout, `FIELD.BIN`'s GZIPPS compression, workspace file conventions |

**Exercise:** extract and decompress `FIELD.BIN` from your own disc 1 rip;
confirm `FIELD.BIN.dec` is created (`03-environment-setup.md` §2 checklist).

## Module 2 — The field engine and RE workflow

| Read | Why |
|---|---|
| `docs/01-encounter-system.md` | Worked example of a fully-RE'd engine system (RNG table, StepID, Danger) — the template for how deep this project's RE goes |
| `docs/05-ghidra-guide.md` | Ghidra import settings, VA alignment (`0x800A0000`), the "4 wins" method for finding code from a known data pattern |
| `docs/04-workflow.md` | Patch → recompress → reinsert → test loop for any engine-binary edit |

**Exercise:** in Ghidra, find `g_field_rng_table` by its known byte
signature (`05-ghidra-guide.md` "First win"), then find the code that reads
it without relying on xrefs (they're often empty on MIPS `lui`/`addiu` pairs).

## Module 3 — Evidence discipline and verifying claims (new)

| Read | Why |
|---|---|
| `.agents/rules/verified-reference-evidence.mdc` | The standard every claim in this repo must meet: bytes, source, or live test |
| `docs/reference/verifying-makou-with-ghidra.md` **(new)** | Worked example of applying that standard — how a real "hardcoded LBA" hallucination was caught and overturned using Makou Reactor source + raw bytes, and why even that wasn't enough without a single-variable live test |

**Exercise:** pick any claim in `docs/reference/INDEX.md` and independently
re-derive it from raw bytes or Makou source, without reading the finding
that first established it.

## Module 4 — Field scripts and Makou Reactor internals

| Read | Why |
|---|---|
| `docs/reference/INDEX.md` + `field-id-mapping.txt` / `movie-id-mapping.txt` / `music-id-mapping.txt` | Canonical ID tables, extracted and cited from Makou Reactor source |
| `docs/05-ghidra-guide.md` "Exporting Field Script Data" section | Using Ghidra (not just Python) to read/patch bytecode scripts |
| `docs/reference/movie-system.md` **(new)** | Full worked system: `PMVIE` opcode → `MOVIE_ID.BIN` table format → CD-ROM seek, with the byte layout, a documented bug (sorted-dir-order ≠ table id), and the one known hardware-seek exception |

**Exercise:** using `scripts/decode_field_script.py`, decode a `PMVIE`
opcode from any `FIELD/*.DAT` file, then resolve its filename via
`MINT/MOVIE_ID.BIN` by hand (not the query tool) following
`docs/reference/movie-system.md`'s row format.

## Module 5 — From patch to shippable pack

| Read | Why |
|---|---|
| `docs/reference/layer-engineering.md` **(new)** | The `ic-layer-v1` JSON format itself: schema, growth handling, manifest wiring, and a byte-level worked diff — not just the CLI commands |
| `docs/08-engineer-build-guide.md` | The CLI commands: work-bin vs layered-bin, `bin_diff_to_layer.py`, `verify_builder_config.py`, publish gotchas |
| `docs/06-new-mod-research.md` | The full idea → RE → patch → playtest → ship loop, plus the mod scaffold convention |

**Exercise:** take any single-byte engine patch, diff it into a layer with
`bin_diff_to_layer.py`, then round-trip verify with
`scripts/apply_layer.py --expect` (`layer-engineering.md`'s worked example).

## Module 6 — Hardware and release gates

| Read | Why |
|---|---|
| `docs/07-hardware-burn.md` | MiSTer PSX as a pre-burn behavioral gate; PS2 MechaPwn burn checklist |
| `docs/findings/2026-07-30-verify-built-disc-stacking.md` | Why a built zip must be smoke-tested against `APPLIED.txt`, not re-derived config |

**Exercise:** run `scripts/verify_built_disc.py` against any recent
downloaded builder-site output and confirm it passes.

## Module 7 — Recording new discoveries

| Read | Why |
|---|---|
| `.agents/skills/record-findings/SKILL.md` | When/how to write a `docs/findings/*.md` entry |
| `docs/findings/README.md` | Index format and how findings supersede each other |
| `docs/06-new-mod-research.md` "Capabilities unlocked" table | How a repeatable new capability gets promoted from a one-off finding into living process docs |

**Exercise:** pick an open follow-up from any recent finding (e.g.
`docs/findings/2026-08-24-csr-movie-reachability-scan.md`'s follow-ups list)
and write the finding entry for your own investigation of it, meeting the
evidence-class standard from Module 3.

## Capstone project

Pick one unclaimed row from `docs/06-new-mod-research.md`'s "Next likely
targets" table (e.g. world map encounter density), and independently run
the full loop: RE the system (Modules 1-4), patch and verify (Module 5),
hardware-gate it (Module 6), and document it (Module 7). This mirrors
exactly how `mods/field-random-encounters/` was originally built.

## Where topics not covered here live

| Topic | Doc |
|---|---|
| Single-disc-specific field/movie conflict resolution | `mods/single-disc/`, rule `single-disc-fields.mdc`, skill `ship-single-disc` |
| PSX RAM address lookup | `docs/reference/ff7-psx-memory/` |
| Ghidra metadata automation (headless CLI) | `docs/06-ghidra-automation.md` |
| Disc-transition-specific debugging session log | `docs/reference/disc-transition-knowledge-base.md` |
