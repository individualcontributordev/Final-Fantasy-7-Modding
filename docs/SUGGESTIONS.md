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

### Encounter off (0%)

Request: field and world packs with encounters fully off, as their own density
(not almost-Light). Long-standing need for cleaner world-map work and low-enc
practice without only the 25% Light preset.

Context: luzbel asked early (2024-11) for a world-map no-encounter option
(e.g. around ocean skip / super-low IGT segments) when Makou did not expose WM
the same way as fields. Engine stubs later made field/world density packs
possible; 0% is the missing step below Light.

Should ship on the same bases as existing densities (clean / CSR / Highwind)
and stay a mod, not baked into CSR or Highwind.

### Battle pacing (entry / win-death / fanfare)

Request: shorten battle entry, win/death, and/or fanfare where safe on PSX
disc (same class of time-save runners know from other CSR games).

Context: cornfed pointed at FF9 PSX CSR cutting fanfares and boss death
anims (2026-07). phek / okamikaze discussed priority - often last after big
cutscene work, and FF9 fight ends are longer than FF7 so the win may be
smaller here; still wanted as an optional mod. Encounter mods working on
console made related battle binary work more plausible than when everything
was Makou-only fields.

Separate from cutscene packs: lives in this repo as engine layers.

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
