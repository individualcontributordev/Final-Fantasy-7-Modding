# Task: DuckStation breakpoints — catch world Light FORCE hit (0xFFFF)

## Goal

Confirm g_world_danger is set to **0xFFFF** on a stub FORCE hit (not only the miss path writing **0**).
Prior shots already showed stub at 0x800B7DB4 and sw to 0x80116284 with v0=0.

## Success

At the store (0x800B7DF4) or right after it:

- Register **v0** = 0x0000FFFF (or 0xFFFFFFFF if shown wide — low half FFFF is what matters)
- Memory **0x80116284** (4 bytes LE) = FF FF 00 00 or word 0000FFFF

Miss path is also valid (v0=0, memory 0). You need **at least one hit path** while walking toward a fight.

## Breakpoints (set these)

In DuckStation CPU Debugger -> Breakpoints:

| # | Address | Type | Why |
|---|---------|------|-----|
| 1 | 0x800B7DE0 | **Execute** | ori v0, zero, 0xffff — FORCE hit branch |
| 2 | 0x800B7DF4 | **Execute** | sw v0, 0x6284(at) — store to g_world_danger |
| 3 | 0x80116284 | **Write** (memory write), not Execute | Fires when danger is stored |

Optional:

| Address | Type | Why |
|---------|------|-----|
| 0x800B7DEC | Execute | miss path (v0 = 0) — contrast only |
| 0x800B7E1C | Execute | jal WorldRand after stub — battle roll |

**Do not** use Execute on 0x80116284 (that is data).

## Steps

1. Boot the same builder zip cue (clean + field Light + world Light).
2. Enter **world map** grass where encounters happen.
3. Set breakpoints above; unpause.
4. Run until #1 or #2 hits with **v0 = FFFF**, or until #3 write shows FFFF in memory.
5. Note hit counts / one line of register+memory under Evidence (or new docs/image.png).
6. Commit this file + screenshot. Say **check**.

## Memory / CE (while broken)

- DS Memory goto 0x80116284 — 4-byte hex
- CE: duckstation exe +7F1600 +116284 — 4 Bytes, Hex

## Reference addresses

```

Execute: 800B7DE0   ori v0, zero, 0xffff     (FORCE)

Execute: 800B7DF4   sw  v0, 0x6284(at)       (store g_world_danger)

Write:   80116284   g_world_danger

```


## Evidence

```
```
