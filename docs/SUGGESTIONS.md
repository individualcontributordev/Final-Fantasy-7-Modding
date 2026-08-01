# Modding suggestions (community)

Source: FF7 speedrun Discord CSR channel export (2024-11 → 2026-07).
This repo = **engine RE + cross-base mods** (encounters today). Cutscene
products live in **Final-Fantasy-7-CSR** — see that repo’s `docs/SUGGESTIONS.md`.

Demand = frequency / multi-person interest. Not a commitment.

## Product lines (current)

| Product | Role |
|---------|------|
| Field random encounters | Light / Standard / Dense on clean, CSR, Highwind |
| World random encounters | Same densities × bases |
| Builder mods UI | All-base mods section + Light/Standard/Dense presets |

---

## Done

| Item | Status | Notes |
|------|--------|--------|
| Field encounter density packs (25/50/75) | **Done** | Per-base layers (clean / CSR / Highwind) |
| World encounter density packs | **Done** | Same |
| Builder: mods on all bases | **Done** | Packs vs Mods split on site |
| Presets Light / Standard / Dense | **Done** | Field+World together |
| Console burn smoke (RE + base) | **Partial** | IC reported PS2 slim OK on early stack |
| Shared tools (layer apply, verify, HAR extract) | **Done** | Root `scripts/` |

---

## To do — prioritised

### P1 — encounter / battle mods (high runner interest)

| ID | Suggestion | Demand | Notes |
|----|------------|--------|--------|
| M-01 | **0% / off** field + world encounters (true no-enc) | High (Luzbel WM noenc for ocean-skip IGT; longstanding) | Distinct from Light 25%. Need safe engine patch + per-base variants. |
| M-02 | **Battle open / win / death / fanfare shorten** | High (Cornfed FF9 CSR; Phek priority after CSR+; Okami FF9 length context) | Engine binary work (not Makou FIELD). Highest “mod” upside after densities. |
| M-03 | World-map no-enc **segment** option (e.g. post-Zolom) if full 0% is hard | Med–High (Luzbel ocean-skip) | Prefer full M-01; segment is fallback. |

### P2 — gameplay quality-of-life mods

| ID | Suggestion | Demand | Notes |
|----|------------|--------|--------|
| M-04 | Faster **Diamond Weapon** (or other long forced battles) | Med (IC mentioned with battle anim work) | After M-02 infrastructure. |
| M-05 | Optional **pre-empt / formation** practice helpers | Low–Med | Careful: must not silently break step routes unless labeled. |
| M-06 | “Random encounters feel like routed Light” tuning docs / preset blurb | Med | Soft: Light already aimed at this; publish expected variance. |

### P2 — tooling

| ID | Suggestion | Demand | Notes |
|----|------------|--------|--------|
| T-01 | Builder: clearer battle-mod vs encounter-mod grouping when M-02 lands | — | UX when catalog grows. |
| T-02 | Verify stacks: CSR + many packs + RE in one command matrix | Med | Partially have `verify_builder_config` / built-disc. |
| T-03 | Document FPGA / console known-good stacks | Med (Okami FPGA notes) | Findings + README pointer. |

### P3

| ID | Suggestion | Notes |
|----|------------|--------|
| M-07 | Pincer-chance / exotic formation chaos mod | Fun; niche; after M-01/M-02. |
| M-08 | Auto “Chuck Norris” joke items NPC | IC joke; invalidates runs — novelty only. |

---

## Deprioritised / reject (here)

| Suggestion | Why |
|------------|-----|
| Putting encounter 0% **into CSR base** | Must stay a **mod** so Unmodified/CSR/Highwind choose. |
| Scene/cutscene requests | CSR repo packs/base — not this repo. |
| Changing CSR skill-check scenes for battle IGT | Cutscene product decision. |
| Full game “randomizer” | Out of scope vs density + battle timing mods. |
| Self-bot Discord scrapers as product | N/A; HAR/export is human workflow only. |

---

## Suggested next ships (short)

1. **M-01** Field+World **Off (0%)** mod family (all bases), builder group + preset.  
2. Spike **M-02** battle intro/outro/fanfare (Ghidra / existing encounter RE).  
3. Wire M-02 as builder **mods** with base-specific layers if needed.  
4. Keep encounter presets in sync when CSR/Highwind base IDs bump.

## Related docs

- Encounter system: `docs/01-encounter-system.md`  
- New mod pipeline: `docs/06-new-mod-research.md`  
- CSR cutscene backlog: CSR repo `docs/SUGGESTIONS.md`
