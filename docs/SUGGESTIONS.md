# Suggestions (engine / gameplay mods)

Ideas that apply across bases (Unmodified, CSR, Highwind) - encounters, battle
pacing, engine bits. Not a release promise. **Open items first**; shipped work
is marked **Done** below.

Cutscenes / CSR+ / Highwind:
https://github.com/individualcontributordev/Final-Fantasy-7-CSR/blob/main/docs/SUGGESTIONS.md

History / chat archives:
https://individualcontributor.dev/history/

---

## What ships today

| Mod | Builder |
|-----|---------|
| Field random encounters | Light / Standard / Dense on Unmodified, CSR, Highwind |
| World map random encounters | Same densities / bases |
| Preset | e.g. Random Encounters (Light) = field + world Light |

---

## Open


### Battle pacing (entry / win-death / fanfare)

**Partial ship (2026-08-08):** optional Fanfare Skip mod
(mods/fanfare-skip/, builder packs) forces the official no-victory-music
battle-mode bit in BATTLE.X so fights exit without fanfare/win poses
(train-style). Playtest still open.

Still open: battle entry length, death anims, broader win/death pacing if
Fanfare Skip is not enough on hardware.

### Super Nova / long forced-battle stretches

Request: shorten or skip Super Nova presentation (awesomewaves 2024-11).
Related: other long forced-battle or in-battle cinematic waits if RE finds a
safe hook.

High risk / high specificity; keep optional and well labeled if shipped.

### Clearer mod grouping in the builder

As more engine mods appear (0%, battle speed, etc.), group and preset labels
should stay obvious next to encounter densities (builder already splits Packs
vs Mods; extend that pattern rather than dumping checkboxes).

### Console / FPGA notes for engine mods

Encounter density packs already need hardware confidence; any new battle
binary mod should record PS2 burn / MiSTer / RetroArch notes the same way
field stubs did (docs/07-hardware-burn.md, findings).

### Diamond Weapon / world-map movement speedups (research)

Discussed as interesting (PC CSR / landscaper ideas, 2026-07) but uncertain on
PSX burned discs. Track as research - not promised - until a binary path is
proven on hardware.

### Random-encounter routing consequences (document, maybe tools)

With random density mods, step-id / pre-empt routing from vanilla is not 1:1.
Open need: short player-facing notes on what still works (pre-empts tied to
step offset vs pure danger), and what people should not expect (stable
formations for routing). Optional later: helpers or presets aimed at practice
with light random vs tool-assist no enc.

---

## Done

**Done - Encounter off (0%)**  
Field and world Off packs + builder preset Random Encounters (Off) for Unmodified / CSR / Highwind (v0.2.0).


**Done - Field random encounter density packs**  
RCnt2 FORCE-style field stub; Light (25%) / Standard (50%) / Dense (75%) on
Unmodified, CSR, and Highwind; discs where layers ship. Builder group Field
Random Encounters.

**Done - World map random encounter density packs**  
Same density set and bases for WORLD.BIN path; builder group World Random
Encounters.

**Done - Builder mods UI + density presets**  
Mods section separate from CSR+ packs; presets such as Random Encounters
(Light) selecting field + world Light for the current base.

**Done - Cross-base compatibility model**  
Encounter mods are not baked into CSR/Highwind; per-base pack variants /
compatibleBases so stacks stay optional on clean / CSR / Highwind.

**Done - Shared verify / layer tooling**  
ic-layer-v1 publish path, verify_builder_config / built-disc checks used when
shipping (see repo AGENTS / findings).

**Done - History archive pointer**  
https://individualcontributor.dev/history/ (community chats that drove many of
these asks).

**Done - Early can-we-change-encounters-on-PSX**  
Blocked while only Makou field edits existed; resolved by engine RE + stubs
that made the density packs shippable on disc/hardware (2026).

---

## Explicitly not Modding-repo work

| Idea | Where it lives |
|------|----------------|
| Cutscene / skill-check / Highwind trims | CSR repo |
| Baking no-encounters into CSR or Highwind bases | Keep optional as mods |
| Full randomizers / major route rewrites | Out of scope for now |
| Official SRC boards | Out of scope |

---

## How to add more

Use the site builder with the base + mods you care about, then a short note:
what you ran, what you want (e.g. 0% world after Zolom), and hardware or emu
if it only shows up there.
