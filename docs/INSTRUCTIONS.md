# Status: last fields CSR D3 vs ending-v7 scripts

## Short answer

**Not the same** for the ending-related maps. Most Northern Cave (`LAS0_*`) match CSR D3; the crater/ending fields differ.

Detail: `docs/findings/2026-08-07-last-fields-csr-d3-vs-ending-v7.md`

## Same as CSR D3

`LAS4_1`, `LAS0_1` … `LAS0_8` — full decoded match.

## Different (movies)

| Field | CSR D3 | ending_v7 D1 | Meaning |
|-------|--------|--------------|---------|
| LASTMAP | plays id **23** (LASTMAP.BIN) + id **24** (LASTFLOR) | id23 **setup only** (MOVIE NOP’d); id24 path still has MOVIE | Intentional v5 — id23 is Form1 data, not a movie |
| LAS4_0 | ENDING01 (id **25**) + CSR JMPFs | ENDING01 plays; **vanilla** script (no CSR jumps) | Movie restored to default; CSR routing extras dropped |
| LAS4_2 | LAST4_2 (id **20**) plays | **movie skipped** | Still SD-core strip — not restored |
| LAS4_3 | LAST4_3 (id **21**) plays | **movie skipped** | Still SD-core strip — not restored |
| LAS4_4 | id **21** + CSR mapjumps | id21 plays; SD jump layout | Movie on; routing ≠ CSR D3 |

## Your hypothesis

- **CSR base skips end movies?** On Disc 3, **no** — CSR D3 keeps 20/21/23/24/25.
- **D1 ending work restored defaults?** **Partly:**
  - LAS4_0 → pristine (ENDING01 back to vanilla path) ✓  
  - LASTMAP early MOVIE still NOP (needed)  
  - LAS4_2 / LAS4_3 still **skipped** (single-disc core, not CSR)

Single-disc core is more aggressive than CSR D3 (it had stripped LASTMAP movies entirely). Ending work put PMVIE 23/24 back but kept the early MOVIE NOP.

## Optional next

Restore CSR/pris movie ops on **LAS4_2** + **LAS4_3** if you want those short crater FMVs (ids 20/21). LAST4_3 body already in GOLD7_2 for manips.
