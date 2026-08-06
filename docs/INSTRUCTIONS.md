# Task: movies pack is one cumulative latest (v0.1.2)

## What changed

Before: builder auto-applied two movie packs (v0.1.0 seed + v0.1.1 LBA alias).

Now:

- Latest only: single-disc-csr-manip-movies-v0.1.2 = seed + LBA alias in one layer
- Only 0.1.2 is enabled and auto-included with Single-disc on CSR
- v0.1.0 and v0.1.1 stay in repo/manifest but disabled (same exclusive group)
- Byte-identical to the old two-pack stack (verified)

Main single-disc pack is still single-disc-on-csr-v0.1.2.

## What you do

1. Pull
2. Rebuild playtest (one movies layer)
3. Optional verify
4. Reply with sizes / PASS

---

## 0. Update

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
```

---

## 1. Rebuild playtest

```bash
cd /path/to/Final-Fantasy-7-Modding
python3 mods/single-disc/scripts/build_playtest_bin.py
```

Open only:

```text
workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.cue
```

Expect bin about 766340400 bytes.

---

## 2. Optional stack check

```bash
python3 scripts/verify_builder_config.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 \
  --base csr-v0.14.1 \
  --addon single-disc-on-csr-v0.1.2 \
  --addon single-disc-csr-manip-movies-v0.1.2
```

Expect PASS. Only one movies addon (not 0.1.0 + 0.1.1).

---

## 3. Reply

Paste playtest last lines + verify PASS if run.

## Policy

Each new manip-movies version includes all previous movie work. Ship the new
id as the only enabled/auto pack; leave older ids disabled for history.

 cd /path/to/Final-Fantasy-7-Modding
python3 mods/single-disc/scripts/build_playtest_bin.py
cd: no such file or directory: /path/to/Final-Fantasy-7-Modding
1/3 CSR base...
    747435024 bytes
2/3 single-disc main pack...
    748775664 bytes
   JAIROFAL after main size 4700160 (still D1-family until movies)
3/3 manip-movies v0.1.2 cumulative (seed + LBA 250450)...
    766340400 bytes
JAIROFAL ISO IsoFile(path='MOVIE/JAIROFAL.MOV', lba=318357, size=15071232)
size 15071232 CANONON 15071232 vanilla_d1 4700160
==CANONON True
==vanilla_jairofal False
sha a8ce3563d7943439 canon a8ce3563d7943439
LBA250450 raw Form2 sector0 == D2 CANONON OK
WROTE D:\projects\Final-Fantasy-7-Modding\workspace\iso-extract\ff7_d1_playtest_csr_sd_movies.bin
WROTE D:\projects\Final-Fantasy-7-Modding\workspace\iso-extract\ff7_d1_playtest_csr_sd_movies.cue
Open the .cue in DuckStation.
Do NOT open other ff7_d1_*_work.bin files in iso-extract (many are core-only ~714MB).
This playtest bin must be ~731MB (766084032 bytes if current packs).
actual 766340400
➜  Final-Fantasy-7-Modding git:(main) python3 scripts/verify_builder_config.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 \
  --base csr-v0.14.1 \
  --addon single-disc-on-csr-v0.1.2 \
  --addon single-disc-csr-manip-movies-v0.1.2
Config: base=csr-v0.14.1 addons=['single-disc-on-csr-v0.1.2', 'single-disc-csr-manip-movies-v0.1.2'] disc=1
Pristine: D:\projects\Final-Fantasy-7-Modding\workspace\pristine\FINALFANTASY7_D1.BIN
  cache hit: D:\projects\Final-Fantasy-7-CSR\cache\csr\FINALFANTASY7_D1.bin
  OK base csr-v0.14.1 ← csr-v0.14.1\layers\disc1.layer.json (94148 records, src=D:\projects\Final-Fantasy-7-CSR\cache\csr\FINALFANTASY7_D1.bin)
  OK addon single-disc-on-csr-v0.1.2 ← single-disc-on-csr-v0.1.2\layers\disc1.layer.json (93571 records)
  OK addon single-disc-csr-manip-movies-v0.1.2 ← single-disc-csr-manip-movies-v0.1.2\layers\disc1.layer.json (841839 records)
Stack:
  - base:csr-v0.14.1 (94148 records via cache/layer)
  - addon:single-disc-on-csr-v0.1.2 (disc1.layer.json, 93571 records)
  - addon:single-disc-csr-manip-movies-v0.1.2 (disc1.layer.json, 841839 records)
PASS — builder config applies cleanly (1029558 total records)
➜  Final-Fantasy-7-Modding git:(main)


smoketest of the csr + single-disc mod is good
