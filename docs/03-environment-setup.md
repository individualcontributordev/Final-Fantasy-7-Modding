# Environment Setup

Work through this checklist in order. Check items off as you complete them.

## 1. Project directory

Already created:

```
~/ff7-modding/
```

Clone paths for reference (optional to build now):

| Tool | Path | Needed when |
|------|------|-------------|
| Makou Reactor | `~/makoureactor` | Editing fields / saving ISO |
| ff7tk | `~/ff7tk` | Understanding ISO code; building Makou |

## 2. Game image (you provide)

Place files in `~/ff7-modding/workspace/iso-extract/`:

- [ ] `ff7_disc1.bin` (and `.cue` if you use one)
- Use a **clean, unmodified** rip of a disc you own
- Disc 1 is enough for early testing (Midgar, first reactor)

**Do not** commit or share ISO files.

### Extract FIELD.BIN

Option A — **Makou Reactor** (once built): File → Open ISO → export FIELD.BIN

Option B — **CDmage** (Windows/Wine) or similar: extract `FIELD\FIELD.BIN`

Option C — **Python + ff7tk** (later, if you build ff7tk tools)

For now, any ISO browser that extracts a single file works.

- [ ] `workspace/iso-extract/FIELD.BIN` exists

### Verify decompression

```bash
python3 ~/ff7-modding/scripts/decompress_field_bin.py \
  ~/ff7-modding/workspace/iso-extract/FIELD.BIN
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
- [ ] Can boot your FF7 disc 1 image
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
- [ ] Can create a new project at `~/ff7-modding/workspace/ghidra/`

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
cd ~/ff7-modding
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
