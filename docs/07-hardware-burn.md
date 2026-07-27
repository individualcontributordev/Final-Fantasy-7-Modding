# Hardware burn / PS2 test (MechaPwn)

Validate builder zips on real hardware. Emulators often ignore bad sector checksums; consoles may not.

## Console

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
| CSR-only | Cutscene skips match DuckStation |
| + Field Light/Standard/Dense | Density feels like emu; Lure/Away still scale if you have materia |

## If ImgBurn verify fails early (EDC)

Example seen with CSR+ Disc 1: miscompare at LBA ~614, **offset 2072**, image `0x00` vs device `0xCC`, path `\INIT\YAMADA.BIN`.

Offset 2072 is the **EDC footer**, not file payload. User data may still be intact.

1. Try the disc on the PS2 anyway.
2. If the console fails: reburn **4x DAO**, better media; then consider EDC/ECC rebuild on the `.bin` before another burn.
3. Log result in a finding / `notes/` screenshot + short md.

## Report results

Paste short notes under `docs/windows-last-output.txt` **EVIDENCE** (or a finding `docs/findings/YYYY-MM-DD-ps2-burn-….md`) and say **check results**. Include: pack list from `APPLIED.txt`, burn speed/media, pass/fail table.
