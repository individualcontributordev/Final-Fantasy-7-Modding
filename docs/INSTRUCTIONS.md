# Task: No-swap — enumerate every Ask-for-disc on pristine D1

Operational handoff. Agent overwrites this file and pushes.
You: git pull --ff-only, run steps, fill Evidence, commit+push. Say **check**.

## Goal

Build a complete list of field-script disc-change call sites on **Unmodified Disc 1**
(pristine). This drives the no-swap add-on (later: any base).

Prior finding: `docs/findings/2026-08-02-noswap-disc-change-pristine.md`
(Ask for disc N then jump map; DISKINFO is DISK0001 only on D1).

## Preconditions

- Pristine D1 in Makou (working copy under workspace/iso-extract is fine)
- Do not save permanent script edits yet — search only

## Steps

1. git pull --ff-only
2. Open pristine Disc 1 in Makou Reactor.
3. Use **Find All** (or equivalent global script search) for each of:
   - `Ask for disc 1`
   - `Ask for disc 2`
   - `Ask for disc 3`
   - If the UI groups them: search `Ask for disc` once.
4. For **every** hit, record one table row (Evidence):
   - Map name + id (e.g. blackbgb #103)
   - Group / script / line if shown
   - Disc requested (1/2/3)
   - **Next important ops** after the ask (map jump target, movie set, save flag, Var writes like Var[13][0])
5. Optional: Find All for `Set next movie` lines that list different files per disc; add a second short table.
6. Paste tables under Evidence. Commit **this file only** (no bins, no new screenshots unless tiny).

## Copy-paste (optional ISO sanity — skip if Makou-only)

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
# no required shell work this turn
```

## Evidence

### Ask for disc — full list

| Map | Id | Script locus | Ask disc | After (jump / movie / notes) |
|-----|----|--------------|----------|------------------------------|
| | | | | |

see screenshot

field numbers

blackbge 106 (no jumps to this field from anywhere in the scripts on disc 1)
blackbgb 103 
blackbg3 95 (no jumps to this field from anywhere in the scripts on disc 1)

blackbgb 103 is also used to run mini games like the byke(motorcycle) mini-game

### Set next movie (multi-disc) — optional

| Map | Id | Script locus | Per-disc movies | Notes |
|-----|----|--------------|-----------------|-------|
| | | | | |



### Counts

- Ask disc 1: N
- Ask disc 2: N
- Ask disc 3: N



## Done when

- Table filled for all hits you can find on D1
- File pushed; say **check**

## Out of scope

- Editing scripts / shipping a pack
- CSR or Highwind
- Disc 2/3 ISO opens (D1 scripts that request 2/3 are enough for the inventory)
