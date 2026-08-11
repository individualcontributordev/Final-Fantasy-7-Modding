# Task: Playtest CSR + CSR+ + Single-disc (no Cheat Engine)

## Already confirmed (chat / this session)

| Build | Field 122 stairs / early path | Notes |
|-------|-------------------------------|--------|
| Unmodified D1 | OK | Pristine baseline |
| CSR D1 only | OK | CSR base not the early freeze |
| Cheat Engine | off | Earlier freezes may have been CE attaching to DuckStation |

## What you are testing now

**CSR + CSR+ + Single-disc** Disc 1, cold DuckStation, **no Cheat Engine**.

## Setup

1. Hard-refresh the builder (recent fixes: disc-filtered APPLIED, no bogus size pad on CSR+)
2. Base: **CSR**
3. Mods: **CSR+** + **Single-disc** (no Fanfare unless noted)
4. Build Disc 1
5. Check **APPLIED.txt**:
   - Single-disc listed
   - CSR+ lines only packs that apply to **this disc** (not every disc2/3-only id)
   - Apply order intent: Single-disc before CSR+ in the stack
6. Quit DuckStation fully; open new `.bin` + `.cue`
7. **Do not** attach Cheat Engine

## Smoke path

1. New game → bomb mission → elevator → **field 122 stairs**
2. Continue → Guard Scorpion → **after battle** (back to field)
3. Optional later: Cosmo / disc1→2 if early path is clean

## Evidence (paste below)

```
APPLIED.txt (full or key lines):
Cheat Engine attached?: NO
Cold DuckStation quit/reopen?: YES/NO

field 122 stairs: OK / FREEZE
Guard Scorpion fight: OK / FREEZE
After Scorpion (field return): OK / FREEZE
notes (music continues? FPS 0? where exactly?):
```

## When done

Commit this file with evidence, push, say **check**.

Commit example: ops: playtest CSR+CSR++SD no CE early Midgar
