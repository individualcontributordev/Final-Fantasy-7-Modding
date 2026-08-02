# Task: No-swap full-run — manual edits (you drive)

Agent plans and reviews. You edit in Makou / DuckStation / optional Ghidra.
No builder pack until full-run playtest PASS.

Policy: docs/findings/2026-08-03-noswap-full-run-scope.md

---

## Working image (always the same)

```text
workspace/iso-extract/ff7_d1_noswap_work.bin
```

- Start from pristine D1 if you do not already have a good copy.
- If you still have `ff7_d1_noswap_re.bin` (hub fixed), copy it to that name and keep using it.
- Never commit `.bin`. Say **check** after each task with paste/evidence.

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
mkdir -p workspace/iso-extract workspace/pristine
# once:
# cp workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin
# or: cp workspace/iso-extract/ff7_d1_noswap_re.bin workspace/iso-extract/ff7_d1_noswap_work.bin
```

---

## Full manual checklist (order)

Do **one block per turn** unless a block is tiny. After each block: save ISO, note Evidence, **check**.

### A. Field — Ask for disc (Makou) — IN PROGRESS

| Status | Map | What to do |
|--------|-----|------------|
| DONE | blackbgb #103 | Four Asks removed; Bit OFF kept; jumps kept |
| THIS TURN | blackbg3 #95 | Remove every Ask for disc; keep Bit clears / jumps / talk flow |
| THIS TURN | blackbge #106 | Remove Ask for disc 2; keep rest of script |
| Verify | whole D1 | Makou Find All `Ask for disc` → **0 hits** |

### B. Field — multi-disc movies (Makou)

Find All `Set next movie` (or lines that list different files per disc).
For each: force **disc 1** filename only, or skip `Play movie` if D1 has no file.
Paste a table (map, old line, new behavior).

### C. Battle — Supernova / SNOVA (known freeze)

D3-only folder `SNOVA/` (~1.1 MB). Options (pick one, document):

1. **Preferred for full-run without fat ISO rebuild:** find battle/effect path that loads Supernova FMV and **skip/no-op** when missing (Ghidra + test), or
2. Copy entire `SNOVA/` from pristine D3 onto the D1 work image (needs free space + ISO file inject; only if you have a workflow you trust).

Evidence: which option + how you verified no freeze (or still stuck).

### D. Endings / last movies

D3-only `MOVIE/ENDING*`, `LAST*`, etc. Same policy: skip Play movie / stub / copy.
At least confirm Final Battle → ending does not hard-lock on D1-only.

### E. Disc id (only if something still rejects the disc)

`MINT/DISKINFO.CNF` is `DISK0001` on D1 — usually OK if we never swap.
If something still checks disc 2/3 id, note it; do not invent patches yet.

### F. Playtest gate (before any pack)

On **work** D1 bin in DuckStation (Unmodified, no CSR required):

- [ ] blackbgb disc2 path → lost2, no prompt, no loop
- [ ] blackbgb disc3 path → las0_1, no prompt, no loop
- [ ] Supernova (or safe battle save) → no freeze
- [ ] One multi-disc field movie site you patched → no freeze
- [ ] Quick blackbgb bike/other hub still OK

### G. Ship (later, CSR pack task — agent will write)

Only after F is PASS: diff work vs pristine → one pack on clean.

---

## THIS TURN only (A — remaining Asks)

### Edits

1. Open `ff7_d1_noswap_work.bin` in Makou.
2. **blackbg3** (#95): Find All / open groups that Ask for disc (p7/p8 Talk from inventory).
   - Delete each `Ask for disc 1/2/3`.
   - Do **not** skip Bit OFF or jumps the way the broken hub Goto did.
   - Prefer clean delete (same style as final blackbgb).
3. **blackbge** (#106): group AD / Script 4 — remove `Ask for disc 2` only; keep surrounding ops.
4. Global Find All `Ask for disc` on this ISO → expect **zero**.
5. Save field(s) back into the work ISO.
6. Optional DS smoke if you can reach those maps; not required if zero Find All.

### Evidence to paste

```
Work bin path:
Find All Ask for disc count after edit: 0 / N
blackbg3: what you changed (brief)
blackbge: what you changed (brief)
Optional paste: one cleaned branch from blackbg3
DS notes (if any):
```

Commit **this file only** (or leave evidence in chat and say check — file preferred).

### Do not

- Publish pack / touch builder
- CSR or Highwind images this turn
- SNOVA/movie deep dive yet (turn B/C after this checks out)

## Done when

- Zero Ask-for-disc on work D1 (Find All)
- Evidence filled; say **check**
