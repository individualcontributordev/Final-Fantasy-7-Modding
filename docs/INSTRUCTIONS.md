# Task: No-swap full-run — stage bins + freeze inventory (no pack yet)

Operational handoff. Agent overwrites this file and pushes.
You: git pull --ff-only, stage local bins, fill Evidence, commit this file only
(no .bin in git). Say **check**.

## Policy

**Do not ship** no-swap to the builder until a full Unmodified disc-1 run is
expected to work (hub + other Asks + movies + Supernova). Incomplete hub pack
is cancelled.

Prior: docs/findings/2026-08-03-noswap-full-run-scope.md

## Goal this turn

1. Put working/pristine bins where the agent can read them (local workspace only).
2. Confirm paths in Evidence.
3. Optional: note any known freeze points you already hit (Supernova, etc.).

## Local layout (gitignored — never commit .bin)

```text
workspace/pristine/FINALFANTASY7_D1.bin   (and D2/D3 if you have them)
workspace/iso-extract/ff7_d1_noswap_re.bin   (current blackbgb hub edit)
```

Copy from wherever they live on your machine. Keep names above if possible.

## Steps

1. git pull --ff-only
2. Copy/stage bins into the paths above (or list real paths under Evidence).
3. Do **not** git add *.bin (repo ignores them; that is intentional).
4. Optional quick check (if python/scripts available):

```bash
cd "$(git rev-parse --show-toplevel)"
ls -la workspace/pristine/FINALFANTASY7_D1.bin \
       workspace/iso-extract/ff7_d1_noswap_re.bin
# sizes should be ~747MB each for D1
```

5. Paste Evidence; commit **docs/INSTRUCTIONS.md only**; push; say **check**.

## Evidence

```
pristine D1 path + size:
noswap working D1 path + size:
pristine D2/D3 present? (yes/no + paths):
Known freezes still expected (Supernova / endings / other):
Notes:
```

## Done when

- Agent can see bins on next check (or clear paths in Evidence)
- Say **check**

## Out of scope this turn

- Publishing any builder pack
- CSR+ / encounter packs
- Full Makou pass (next task after bins are staged)
