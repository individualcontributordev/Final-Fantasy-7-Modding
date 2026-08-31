# World map random encounters — changelog

RCnt2 FORCE stub in WORLD.BIN. Densities: Off (0%) / Light (25%) / Standard (50%) / Dense (75%).
Index: [CHANGELOGS.md](../../CHANGELOGS.md). **Newest at top.**

Current VERSION file: see `VERSION` in this folder.

## 2026-08-31

- Shipped Light/Standard/Dense (25/50/75%) on-CSR packs for Discs 2 and 3
  (previously Disc 1 only). Off (0%) already covered all 3 discs.

## 2026-08-02

- Retarget Highwind packs to highwind-v0.2.0 (base id bump; engine stubs unchanged).

## v0.2.0

- Off (0%) packs for Unmodified (clean), CSR (csr-v0.14.1), and Highwind
  (highwind-v0.1.1), discs 1–3.
- Pack ids: world-encounter-0-v0.2.0, world-encounter-on-csr-0-v0.2.0,
  world-encounter-on-highwind-0-v0.2.0.
- Builder option Off (0%) in World Random Encounters; preset
  Random Encounters (Off) (field + world).

## v0.1.0

- Light / Standard / Dense packs for Unmodified (`clean`), CSR (`csr-v0.14.1`),
  and Highwind (`highwind-v0.1.1`).
- Pack ids: `world-encounter-25|50|75-v0.1.0`,
  `world-encounter-on-csr-*-v0.1.0`,
  `world-encounter-on-highwind-*-v0.1.0`.
- Builder labels: group **World Random Encounters**, options Light/Standard/Dense.
- Builder preset **Random Encounters (Light)** (`random-encounters-light`) selects
  field + world Light for the current base (see also field changelog).
- Discs 1–3 where layers ship for each base.

## Earlier

- World danger / lure RE and stub path: `docs/findings/` and `patches/`.
