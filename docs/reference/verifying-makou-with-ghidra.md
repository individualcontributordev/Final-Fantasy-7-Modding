# Verifying Makou Reactor claims against Ghidra + raw bytes

Makou Reactor's UI/source tells you what a field script opcode is *supposed*
to mean. Ghidra tells you what the PSX executable *actually does* with it.
Trusting only one source has produced real hallucinated conclusions in this
repo (see `docs/findings/2026-08-24-canonon-hardcode-clean-room-reverification.md`).
This doc is the reusable method, taught via that real worked example.

## The method (3 independent evidence classes)

Per the verified-reference-evidence rule, never conclude engine
behavior from a single source. Always seek two of:

1. **Raw bytes** — hex dump of the actual field script / table / executable
2. **Source code** — Makou Reactor's C++ (opcode struct layout, UI behavior)
3. **Live test** — emulator/hardware trace with a literal observed result

Source code alone tells you Makou's *model* of the format — it does not
prove the PS1 executable honors that model at runtime. Bytes alone tell you
what's stored, not how it's interpreted. Only a live test closes the loop.

## Worked example: was PMVIE's LBA "hardcoded"?

**Question:** Does the field engine resolve `PMVIE`'s movie id through
`MOVIE_ID.BIN`, or is there a hardcoded LBA somewhere bypassing it?

**Step 1 — read Makou's opcode model (source code class):**
```
workspace/makoureactor/src/core/field/Opcode.h:1497-1501
STRUCTPACK(struct OpcodeMovie : public OpcodeBase { quint8 movieID; });
```
One byte. Physically cannot store a 32-bit LBA. This rules out the opcode
itself as an LBA carrier, but does **not** yet rule out a hardcoded LBA
living elsewhere in the executable (e.g. a lookup ignoring the table).

**Step 2 — scan the executable for candidate LBA literals (raw bytes class):**
Scanned `SCUS_941.63` for the suspected LBAs (163608 / 172631 / 197242 /
250450) as both 32-bit LE words and BCD MSF triples, both byte orders. Zero
static hits. This is evidence *against* a hardcoded literal, but a
computed/indirect LBA wouldn't show up as a literal anyway — inconclusive on
its own.

**Step 3 — decode the actual field script bytes (raw bytes class):**
```
FIELD/LOSLAKE1.DAT (D2): f8 2f  → PMVIE id 47
FIELD/LAS4_0.DAT   (D3): f8 19  → PMVIE id 25
```
Confirms real discs use small table ids, consistent with Step 1's struct.

**Step 4 — cross-check id meaning against a second Makou source path (source class, independent of Opcode.h):**
`Data.cpp:607-623` builds `movieList[106]` from disc-specific slices.
`movieList[81] = "canonon"` → D2 list index `20+(81-54) = 47`. Matches the
byte-decoded id 47 from Step 3 exactly. Two independent parts of Makou's own
source (opcode struct + name-list construction) and the raw script bytes now
triangulate on the same number — strong internal consistency.

**Step 5 — the live test (the only class that proves runtime behavior):**
Steps 1-4 only prove the **data model** is table-driven and internally
consistent. They cannot prove the *executable* actually reads
`MOVIE_ID.BIN` at runtime instead of, say, a separate hardcoded jump table
compiled from it. This required a single-variable emulator test (patch only
`MOVIE_ID.BIN` row 47, change nothing else, observe what plays) — tracked in
`docs/INSTRUCTIONS.md` and closed out in
`docs/findings/2026-08-24-canonon-hardcode-clean-room-reverification.md`'s
follow-ups.

**Lesson:** 4 out of 5 steps here were pure source/byte analysis and were
enough to *overturn* a prior wrong conclusion (which itself came from an
emulator test — but one that changed 3 variables at once, so it wasn't
actually a valid live-test data point). A live test is necessary but not
sufficient by itself either — it must be a **single-variable** test to count
as real evidence (see `docs/findings/2026-08-07-ending-credits-test-inject.md`,
now marked superseded for exactly this reason).

## Ghidra's role when source code isn't available

The example above didn't need Ghidra because Makou Reactor is open source —
reading `Opcode.h`/`Data.cpp` directly was faster and more precise than
disassembling the interpreter. **Use Ghidra when:**

- Verifying the PS1 *executable's* opcode interpreter itself (does
  `SCUS_941.63` really read `MOVIE_ID.BIN[id]`, byte-for-byte, at some
  address?) — this is the still-open half of the example above.
- The behavior in question has no open-source reference implementation
  (e.g. custom RNG tables, encounter math — see `docs/05-ghidra-guide.md`).
- You need a RAM address to set a breakpoint/watch for the live-test step.

Concrete Ghidra technique for finding the `MOVIE_ID.BIN`-reading code: table
scalar search for the table's known byte pattern or a distinctive row's LBA
(e.g. `250450` as `0x0003D252` LE) via **Search → For Scalars**, then read
xrefs — same technique as `05-ghidra-guide.md`'s RNG-table win, applied to a
different table.

## Checklist for any new "how does the engine do X" question

- [ ] Can you decode the relevant bytes yourself (script opcode, table row)? Do it — don't trust a prior finding's numbers.
- [ ] Does an open-source tool (Makou Reactor / ff7tk) model this format? Read the actual struct/function, cite file:line.
- [ ] Do two independent source-code paths (e.g. opcode struct + separate UI/data code) agree on the same interpretation?
- [ ] Is there a **single-variable** live test that would prove or disprove the runtime behavior? Design it before assuming source-level analysis is sufficient.
- [ ] Write the finding with all evidence classes cited — `docs/findings/YYYY-MM-DD-slug.md`, confidence tag (`likely` until live-tested, `confirmed` after).

## Sources

- `.agents/rules/verified-reference-evidence.mdc`
- `docs/findings/2026-08-24-canonon-hardcode-clean-room-reverification.md`
- `docs/findings/2026-08-07-ending-credits-test-inject.md` (superseded — the anti-pattern)
- `docs/05-ghidra-guide.md` (RNG-table scalar-search technique)
- `docs/reference/movie-system.md`
