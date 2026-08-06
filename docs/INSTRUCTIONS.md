# Task: single-disc v0.1.2 published — rebuild playtest and smoke

## What shipped

Builder main pack: **single-disc-on-csr-v0.1.2** (v0.1.1 main pack disabled).

Movies auto-stack still:

- single-disc-csr-manip-movies-v0.1.0
- single-disc-csr-manip-movies-v0.1.1

Locked in this release:

- DEL1 = CSR Disc 1 (no jump to field 442)
- BLACKBGB = asks removed (zero disc-change ops)
- LOST2 = CSR Disc 2
- LOSLAKE1 movie LBA alias (movies pack)

## What you do

1. Pull
2. Rebuild playtest
3. Open the new cue in DuckStation
4. Reply: build size + any smoke notes

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

Expect bin size about **766340400** bytes.

Optional stack check:

```bash
python3 scripts/verify_builder_config.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 \
  --base csr-v0.14.1 \
  --addon single-disc-on-csr-v0.1.2 \
  --addon single-disc-csr-manip-movies-v0.1.0 \
  --addon single-disc-csr-manip-movies-v0.1.1
```

Expect: PASS — builder config applies cleanly

---

## 2. Smoke (as far as you can)

- Boots to title / new game or load
- Costa / DEL1 path does not jump into DEL2 (#442)
- If you reach blackbg hub: no insert-disc prompts on those four routes
- LOSLAKE1 FMV matches Disc 2 cannon scene if you get there

---

## 3. Reply

Paste:

1. Playtest build last lines (size OK or fail)
2. verify PASS if you ran it
3. Short smoke notes

---

## After this release

Seven multi-disc field maps still marked review in
mods/single-disc/patches/csr-field-disc-prefer.txt
(BUGIN1A, COS_BTM, COS_BTM2, JUNAIR2, NIVGATE, RCKTIN2, RCKTIN7).

Those are the next merge train (new version after 0.1.2).
