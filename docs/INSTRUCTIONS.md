# Task: No-swap — dump blackbgb S0-Main disc branches

Operational handoff. Agent overwrites this file and pushes.
You: git pull --ff-only, fill Evidence, commit+push. Say **check**.

## Goal

Document the **four** `Ask for disc` sites in pristine **blackbgb (#103)**
`init` / **S0 - Main**, including the condition bits and the map jump after each.
That script is the live disc-change hub on D1.

Prior: `docs/findings/2026-08-02-noswap-ask-for-disc-inventory.md`

## Preconditions

- Pristine D1 in Makou; open map **blackbgb** (field 103)
- Read-only — do not save script edits yet

## Steps

1. git pull --ff-only
2. Makou → blackbgb → group **init** → script **S0 - Main**
3. For each Ask line (**43, 64, 73, 95**), copy the surrounding branch:
   - gating `If` / Var bits / GameMoment
   - save prompt if any
   - `Ask for disc N`
   - waits / music
   - **Jump to map** (name + id + coords if shown)
   - any `Var[13][0] = disc` style writes
4. Paste under Evidence (four blocks or one annotated dump of the whole S0-Main
   disc-related section). Commit **this file only** (no bins; no screenshot files
   under docs/ — paste text).

## Evidence

### blackbgb / init / S0 - Main

#### Branch A (Ask line 43) — disc ?

```
(paste)
```

#### Branch B (Ask line 64) — disc ?

```
(paste)
```

#### Branch C (Ask line 73) — disc ?

```
(paste)
```

#### Branch D (Ask line 95) — disc ?

```
(paste)
```

### Quick table

| Line | Ask disc | Jump map (id) | Notes |
|------|----------|---------------|-------|
| 43 | | | |
| 64 | | | |
| 73 | | | |
| 95 | | | |

## Done when

- All four branches pasted with jump targets
- Pushed; say **check**

## Out of scope

- Editing opcodes / shipping packs
- blackbg3 / blackbge deep dump (after hub is locked)
- CSR / Highwind
