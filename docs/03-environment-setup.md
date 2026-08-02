# Environment Setup

Tooling checklist for **Final Fantasy VII PSX disc modding** (any topic — field, engine binaries, ISO workflow).

Work through this list in order.

## 1. Project directory

Already created:

```
~/Final-Fantasy-7-Modding/
```

Clone paths for reference (optional to build now):

| Tool | Path | Needed when |
|------|------|-------------|
| Makou Reactor | `~/makoureactor` | Editing fields / saving ISO |
| ff7tk | `~/ff7tk` | Understanding ISO code; building Makou |

## 2. Game image (you provide)

Place files in `~/Final-Fantasy-7-Modding/workspace/iso-extract/`:

- [ ] `ff7_disc1.bin` (and `.cue` if you use one)
- Use a **clean, unmodified** rip of a disc you own
- Disc 1 is enough for early testing (Midgar, first reactor)

**Do not** commit or share ISO files.

### Extract FIELD.BIN (engine binary)

`FIELD.BIN` on the disc is the **field engine** (gzipped MIPS code), not a field map.
Makou Reactor does **not** export it — Makou only rewrites it when you save ISO field edits.

**Use CDmage (desktop ISO tool)** — classic ISO browser for Final Fantasy VII PSX:

1. Install [CDmage](https://www.romhacking.net/utilities/1435/) (or any PSX ISO tool that extracts files)
2. File → Open → your `ff7_disc1.bin` / `.cue`
3. Browse to folder `FIELD`
4. Right-click `FIELD.BIN` → Extract (or Extract As…)
5. Save as `workspace/iso-extract/FIELD.BIN` in the Final-Fantasy-7-Modding clone

Option B — other ISO tools that can extract a single file from Mode 2 / 2352 images.

- [ ] `workspace/iso-extract/FIELD.BIN` exists

Makou is for later: editing `.DAT` fields and reinserting into the ISO after engine patches.

### Verify decompression

```bash
python3 ~/Final-Fantasy-7-Modding/scripts/decompress_gzipps.py \
  ~/Final-Fantasy-7-Modding/workspace/iso-extract/FIELD.BIN
```

Expected: creates `FIELD.BIN.dec` (~500KB–1MB+ depending on version). Script prints size.

- [ ] `FIELD.BIN.dec` created without errors

## 3. Emulator (pick one)

For **testing patches** and **RAM debugging**:

| Emulator | Platform | Debugger | Notes |
|----------|----------|----------|-------|
| [DuckStation](https://github.com/stenzek/duckstation) | macOS | Good | Recommended |
| [PCSX-Redux](https://github.com/grumpycoders/pcsx-redux) | macOS | Excellent | Heavier, great for breakpoints |
| RetroArch + beetle_psx | macOS | Basic | Fine for smoke tests only |

Install:

```bash
# DuckStation via Homebrew (if you use brew)
brew install --cask duckstation
```

- [ ] Emulator installed
- [ ] Can boot your Final Fantasy VII disc 1 image
- [ ] Know how to open memory viewer (for Danger at `0x8007173C`)

### Emulator settings for modding

**Use Safe Mode** for hardware-accurate testing:

- **Settings → Main → Safe Mode** (disables PGXP, upscaling, CPU overclock, CD speedup, fast boot, runahead)

Also:

- Disable cheats / patches from other mods
- Use a **copy** of your ISO for testing (`ff7_disc1_test.bin`)
- Match disc region (US/EU/JP)
- Memory watch: Danger `0x8007173C`, StepID `0x8009C540`, Offset `0x8009AD2C`

Full detail: [findings/2026-07-25-duckstation-accurate-settings.md](findings/2026-07-25-duckstation-accurate-settings.md)

### MiSTer PSX (high-confidence behavioral gate)

[MiSTer](https://mister-devel.github.io/MkDocs_MiSTer/) **PSX** FPGA core — near-real PlayStation **1** (not PS2). **Not shipped in this repo** (separate hardware + BIOS).

- Buy/setup DE10-Nano MiSTer → update_all → PSX core + BIOS → load `.cue` (details: [07-hardware-burn.md](07-hardware-burn.md))
- Use **after** DuckStation Safe Mode, **before** burning, for Ghidra/Makou logic
- **Interactive playtest** — no headless “pass/fail” CLI for mod correctness
- Does **not** replace PS2 MechaPwn + CD-R for optical/EDC/burn issues

## 4. Ghidra

Download: https://github.com/NationalSecurityAgency/ghidra/releases

macOS install:

1. Download `ghidra_*_PUBLIC_*.zip`
2. Unzip to `~/Applications/Ghidra` or `~/tools/ghidra`
3. Run `ghidraRun` (needs Java 21+)

```bash
# Java (if needed)
brew install openjdk@21
```

- [ ] Ghidra launches
- [ ] Can create a new project at `~/Final-Fantasy-7-Modding/workspace/ghidra/`

Optional plugins (later):

- PSX loaders / MIPS helpers from the Ghidra community repo

## 5. Makou Reactor (optional for phase 1)

Needed when you reinsert a patched ISO. Not required for Ghidra-only exploration.

Build deps: Qt 6.2+, CMake, ff7tk. See `~/makoureactor/README.md`.

- [ ] Makou builds and opens (defer if painful — CDmage + scripts work too)

## 6. Hex editor (sanity checks)

Any of: `xxd` (CLI), Hex Fiend (macOS), ImHex.

- [ ] Can search `FIELD.BIN.dec` for bytes `B1 CA EE 6C`

## 7. Version control (recommended)

```bash
cd ~/Final-Fantasy-7-Modding
git init
echo 'workspace/iso-extract/*.bin' >> .gitignore
echo 'workspace/iso-extract/*.cue' >> .gitignore
echo 'workspace/iso-extract/FIELD.BIN' >> .gitignore
echo 'workspace/iso-extract/*.dec' >> .gitignore
git add docs scripts README.md .gitignore
git commit -m "Initial project docs and scripts"
```

- [ ] Git repo initialized (docs/scripts only; ISO stays ignored)

## Phase 1 complete when

All checked:

- [ ] FIELD.BIN extracted and decompressed
- [ ] Emulator boots disc 1
- [ ] Ghidra project created
- [ ] RNG table found in `FIELD.BIN.dec` (see `05-ghidra-guide.md`)

Then proceed to Ghidra analysis — not patching yet.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Decompress fails | Confirm file is PS1 `FIELD.BIN` (8-byte GZIPPS header, not raw gzip) |
| Ghidra won't start | Install JDK 21+, set `JAVA_HOME` |
| Emulator black screen | Check `.cue` points to correct `.bin` track |
| Wrong RAM addresses | Confirm PS1 region (US/EU/JP); addresses above are US-focused |
