# Hardware & high-confidence verify

Validate patches before calling them hardware-ready. Different tools catch different failures.

## Verification ladder

| Step | Tool | High confidence for | Weak for |
|------|------|---------------------|----------|
| 1 | DuckStation **Safe Mode** | Fast iterate, RAM watches | Can hide CD/timing/EDC issues |
| 2 | **MiSTer PSX** FPGA core | Ghidra / Makou **game logic** on near-real PS1 | Burned CD-R, MechaPwn, optical EDC |
| 3 | Burn + **PS2 Slim 77003 (MechaPwn)** | Disc image + burn + your console | Slow; use after (1)/(2) |

**MiSTer** (not classic MiST) is the FPGA platform with a strong PlayStation **1** core. There is no mature PS2 FPGA stand-in — your MechaPwn PS2 remains the final console gate.

### Why MiSTer is not in this repo

MiSTer is **physical hardware** (typically a Terasic DE10-Nano + extras), plus a PS1 BIOS you must supply yourself. It is not a library or CI dependency. This repo stays disc-mod focused (scripts, layers, findings) — see `keep-repo-succinct`. Setup lives in official MiSTer docs; we only document how it fits **our** verify ladder.

### Set up MiSTer (once)

1. Hardware: DE10-Nano-based MiSTer (kit or DIY) — [MiSTer wiki](https://mister-devel.github.io/MkDocs_MiSTer/)
2. On the device: run **update_all** (or equivalent) so the **PSX** core is installed
3. Place region BIOS files where the PSX core expects them (commonly under `games/PSX/` — follow current core README; US BIOS for NTSC-U FF7)
4. Copy your test `.bin` + `.cue` into a per-game folder under `games/PSX/` (names must match the cue `FILE` line)
5. Menu → PSX core → load the `.cue`

Optional: batch/remote launch helpers exist (`mbc`, REST launchers) to **start** a game from another PC. They do **not** assert “mod works.”

### Headless / automated MiSTer?

**No useful headless verifier for our mods.** You still open the game and play (or watch) through the patched content.

- MiSTer is an interactive FPGA console, not a unit-test runner.
- Remote/CLI tools can load a core/cue; they cannot judge CSR skips, encounter density, or “no softlock in Sector 1.”
- Keep **DuckStation** for RAM watches / fast iterate; use **MiSTer** for a human behavioral gate; use **PS2 burn** for optical proof.

### When to use MiSTer

Use after DuckStation looks good, **before** burning, for:

- Ghidra engine patches (`FIELD.BIN` stubs, encounter logic, crashes/softlocks)
- Makou field/script/data edits
- Timing-sensitive feel DuckStation might paper over (FMV/XA, seek quirks, odd GPU/CD bugs)

**Pass bar:** boots, reaches the patched content, behavior matches intent — treat as **strong evidence** the mod logic will work on real PS1 hardware.

**Does not replace** a burned CD-R on the PS2 for ImgBurn/EDC/media/laser issues (MiSTer loads `.bin/.cue` from storage, not through an optical drive).

### Suggested order for a Ghidra/Makou change

1. Patch → inject → DuckStation Safe Mode + RAM proof  
2. Same `.bin` + `.cue` on **MiSTer PSX**  
3. Builder zip (EDC repair on apply) → burn → **PS2 MechaPwn** when shipping / after disc-format changes  

---

## Console burn (MechaPwn)

- PS2 Slim **77003** + **MechaPwn** (backup PS1 CD-ROMs)
- Burn **CD-R** (not DVD) — FF7 is a PS1 CD image (`MODE2/2352`)

## Build what you burn

1. https://individualcontributor.dev/builder/
2. Clean NTSC-U `.bin` → pick base (+ optional Field density) → **Build zip**
3. Unzip: keep `.bin` + `.cue` together; read `APPLIED.txt`

**First hardware disc (recommended):** Disc **1** only — one variable at a time (e.g. CSR, then later CSR+Light).

## Burn (ImgBurn on Windows — preferred)

1. Insert a quality CD-R (avoid no-name ultra-cheap spindles if the laser is picky)
2. ImgBurn → **Write image file to disc**
3. Source = the **`.cue`** (not the `.bin` alone)
4. Settings that usually matter:
   - Write mode: **DAO** (Disc-at-Once)
   - Speed: **4x** (try 8x only if 4x is clean and you need faster)
   - Do **not** “ISO9660 data disc” the `.bin` as a file
5. Verify (ImgBurn verify pass) before ejecting

Mac: use a tool that burns from `.cue` as raw Mode 2 (e.g. `cdrdao` / Toast “RAW”). Finder “burn folder” will **not** work.

## Boot on PS2

1. MechaPwn path as you normally boot backups
2. Disc should identify as FF7 Disc 1
3. Reach title → New Game or a known save

## Pass / fail checklist (Disc 1)

| Check | Pass |
|-------|------|
| Boot to title | No freeze / read error early |
| New Game → train / Sector 1 | Field loads |
| Walk hostile field | No crash; battles can still occur |
| CSR-only | Cutscene skips match DuckStation / MiSTer |
| + Field Light/Standard/Dense | Density feels like emu; Lure/Away still scale if you have materia |

## EDC/ECC after builder apply

The disc builder regenerates Mode2 Form1 EDC/ECC for every sector changed by layers (`builder/edc.js`). New zips should ImgBurn-verify cleanly. Older zips (before this fix) may still verify-fail at offset 2072 but can boot on MechaPwn.

## Report results

Paste short notes under `docs/windows-last-output.txt` **EVIDENCE** (or a finding `docs/findings/YYYY-MM-DD-ps2-burn-….md` / `…-mister-….md`) and say **check results**. Include: pack list from `APPLIED.txt`, whether MiSTer was run, burn speed/media, pass/fail table.
