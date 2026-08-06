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
