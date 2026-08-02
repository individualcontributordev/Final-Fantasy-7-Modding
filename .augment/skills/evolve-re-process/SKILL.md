---
name: evolve-re-process
description: >-
  Updates the living reverse-engineering and new-mod process as capabilities
  unlock or workflows improve in Final-Fantasy-7-Modding. Use after a process
  breakthrough, when a new binary/surface becomes injectable, when retiring a
  dead-end method, or when the user asks to optimize the RE loop.
---

# Evolve the RE process

Goal: the next mod is faster than the last because the **process docs stay true**.

## When to run (also enforced by `.agents/rules/evolve-re-process.mdc`)

Run this skill at the end of a session (or mid-session after a breakthrough) if you can answer yes to any:

1. Would a future agent waste time without this note?
2. Did we unlock a **new capability** (new file, new verify method, new ship path)?
3. Did we **invalidate** a step in `docs/06-new-mod-research.md` or `docs/04-workflow.md`?
4. Did we add a script that should replace a manual manual chore?

## Checklist

Copy and tick:

```
Process update:
- [ ] Finding filed (if factual discovery) — record-findings
- [ ] docs/06-new-mod-research.md updated (loop, layers, or Capabilities table)
- [ ] Relevant docs/0N-*.md updated (only confirmed facts)
- [ ] research-new-mod skill still matches the loop (edit if drifted)
- [ ] Obsolete steps removed or marked dead
- [ ] AGENTS.md / README index row if a new doc entry point appeared
- [ ] Committed + pushed
```

## Capabilities unlocked table

In `docs/06-new-mod-research.md`, keep a short table:

| Capability | Since | Notes / entry doc |
|------------|-------|-------------------|
| … | date or mod | link |

Add a row when something new is **repeatably** possible (not a one-off hack).

## Optimize, don’t bloat

- One improved sentence beats a new essay
- Merge duplicate advice; point to a single home
- Scripts > prose when the step is mechanical (`scripts/`, `mods/*/scripts/`)
- Never invent process for untested ideas — mark `likely` in a finding first

## Related

- Start a mod: `research-new-mod`
- Journal facts: `record-findings`
- Ship Field packs: `ship-field-encounters`
