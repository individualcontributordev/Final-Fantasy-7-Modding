# Goals

## Problem

FF7 PS1 field encounters look random but are fully deterministic:

- A fixed 256-byte RNG table
- Predictable state: StepID, Offset, Danger, Formation
- New game / hard reset starts all counters at 0
- Save files store StepID and Offset, preserving the sequence

Speedrunners exploit this with stutter-step, encounter table routing, and formation
manipulation to avoid or force specific battles.

## Desired outcome

Encounters should be **unknown** to the player:

| Priority | Behavior |
|----------|----------|
| Must have | Different encounter sequence after hard reset (power cycle) |
| Should have | Reseed RNG state each time a field map loads |
| Nice to have | Same treatment for world-map encounters (`WORLD.BIN`) |
| Out of scope (for now) | Changing which enemies appear per map (that's Makou encounter tables) |

## Proposed fix (high level)

Patch `FIELD.BIN` to reseed encounter RNG state on field load:

- StepID ← random
- Offset ← random
- Formation ← random
- Danger ← 0

Entropy source: PS1 hardware timer or FF7 kernel PRNG (same idea Bone Village uses
for field script RNG).

## Success criteria for "environment ready"

- [ ] Own a clean FF7 PS1 disc image (`.bin` + `.cue`) in `workspace/iso-extract/`
- [ ] Can extract and decompress `FIELD.BIN` with project scripts
- [ ] Ghidra opens `FIELD.BIN.dec` and finds the RNG table (`B1 CA EE 6C…`)
- [ ] Emulator runs the disc image and can show RAM at known addresses
- [ ] Can recompress `FIELD.BIN`, reinsert into ISO, and boot the game

## Non-goals

- Breaking encounter *rates* (how often battles happen in general) — unless needed as a side effect
- PC version / 7th Heaven (PS1 only for now)
- PPF patch distribution (direct ISO edit first, packaging later)
