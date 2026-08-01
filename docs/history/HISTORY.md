# A history of FF7 PSX CSR and the mods around it

Written so it still makes sense decades later.

This is the story of a **PlayStation disc cutscene-reduced** path for
*Final Fantasy VII*, grown in public with the FF7 speedrunning community,
then split into cleaner products: a skill-check-preserving **CSR**, optional
**CSR+ scene packs**, a separate aggressive **Highwind** base, and
**cross-base gameplay mods** (starting with encounter rates).

Primary sources (sanitized chat archives) live next to this file:

| Archive | What it is | Span | Messages |
|---------|------------|------|----------|
| [2024-09 CSR dev thread](archive/2024-09-csr-dev-thread.sanitized.har.gz) | Birth of the PSX CSR in a Discord thread | 2024-09 → 2024-11 | ~1355 |
| [2024-11 CSR channel](archive/2024-11-csr-channel.sanitized.har.gz) | Ongoing channel after the thread | 2024-11 → 2026-07 | ~1700 |

Readable extracts (gzipped JSON/Markdown): [`extracts/`](extracts/).  
Index: [`archive/MANIFEST.json`](archive/MANIFEST.json).

Cookies and auth headers were stripped before check-in. Bodies of public
channel messages were kept so the conversations remain legible.

---

## Why it existed

FF7 Any% on PSX is long not only because of battles and routing, but because
of **cutscenes, FMVs, and dialogue**. Runners already practiced with turbo,
save states, and route notes. What they lacked was a **console-faithful**
disc image: same game rules and skill checks, far less waiting.

There was precedent—Hope’s earlier CSR experiments, FF8/FF9 CSR culture,
PC/HD cutscene work—but PSX **disc** work is unforgiving: three discs,
field scripts, Mode 2 sectors, real hardware disc swaps, and Makou Reactor
as the daily instrument.

The project’s north star, said many ways over many months:

> **Same game, shorter. Keep the parts that teach the run.**

---

## Chapter 1 — Thread years: inventing the loop (autumn 2024)

It starts in a Discord **thread**, not a polished repo. Patches fly. Version
numbers are messy. Someone burns a disc for a PS2 session the same evening a
fix lands. Practice runners treat softlocks as weather and keep going.

Early rhythm:

1. Maintainers edit field scripts (Makou), ship a patch.
2. Runners play on DuckStation and **burned discs**.
3. Notes come back the same day: trim here, put a text box back there,
   something softlocked after Temple, Rocket Town eats a run, music feels wrong.
4. Another patch. Repeat.

What the community taught immediately:

- **Muscle memory matters.** Strip too many boxes before a choice and the CSR
  stops training the real game.
- **Skill checks are load-bearing.** Elevator manip (waterfall / List), Final
  Descent, certain movement windows—not “flavor.” Remove them and you practice
  a different sport.
- **Emu green is not hardware green.** Disc1→Disc2 swap bugs, POPStarter color
  weirdness, laser-friendly USB setups, plywood jokes about ruined burns…
  console truth became the bar.
- **Save states lie across patch versions.** RAM from yesterday’s build
  poisons today’s.

A landmark technical saga: **disc swap after Jenova**. For a stretch, CSR D1
would not hand off cleanly to D2 on real PS2. Binary search through git
history, mixed burned/retail discs, memory-card forensics, and patience from
people willing to reburn and retest tracked the break to specific field-script
churn—and fixed it without abandoning the project. That episode set a permanent
tone: *if it only works on emulator, it isn’t done.*

By mid-November 2024 the thread had already produced a usable Any%-oriented
CSR, unofficial tracking sheets, feedback forms, and a clear sense that this
was **community infrastructure**, not a one-off meme patch.

---

## Chapter 2 — A channel, a craft (late 2024 → 2025)

The work graduated into a **dedicated channel**. Releases stacked: Reno, boats,
Rocket Town, Midgar raid, NMS paths, Highwind bridge, little one-box restorations
after someone said “I always count seven.” People finished full CSR runs and
came back with timestamps and clips instead of vibes alone.

Design tension (never fully “won,” only balanced):

| Pull | Meaning |
|------|---------|
| **Practice transfer** | CSR should make you better at retail routes |
| **Category breadth** | NMS, All Bosses, Hundo don’t need the same leftover scenes as No Slots |
| **Feel** | Over-trim becomes a warp ballet; under-trim wastes lives |

Hope’s older CSR, PC CSR differences, and FF9’s more aggressive style were
reference points—not gospels. PSX kept veto power (remove the wrong boat scene
and Cloud is a chocobo stuck on the world map).

---

## Chapter 3 — “Why not both?” (2026)

Years of “leave FD scenes / cut FD scenes” debate got an architectural answer
instead of a single winner:

| Product | Idea |
|---------|------|
| **CSR** | Skill checks kept; filler cut |
| **CSR+ packs** | Optional scene trims **on CSR** (Aerith house, Hojo FD, CoTA FD, …) |
| **Highwind** | Separate aggressive base—“dad mode,” max short, not a pack stack |
| **Mods** | Gameplay layers for **every** base (encounter density first) |

The **browser builder** made that real: retail `.bin` in, choose base + packs +
mods, zip out with `APPLIED.txt`. No more only-whole-disc mystery patches as
the sole distribution story.

Encounter **Light / Standard / Dense** mods (field and world), per base, turned
“I wish battles felt less like a pure step-route” into a checkbox. Console burns
of stacks started to look possible—an old hope from the thread era.

CSR+ stayed honest about cost: cutting CoTA phone/FMV **changes FD List**.
Changelogs began to say so out loud.

---

## What this community actually built

Not only minutes saved:

- A **shared language** for trims vs skill checks vs category packs  
- A **hardware-first** QA culture  
- **Runner-as-QA**: practice attempts as continuous integration  
- An ethic of **putting boxes back** when the short path forgot the human  
- A path from chaotic PPF threads to **versioned packs, bases, and mods**

If you only remember one line from the chats, remember this mood:

*We’re not erasing FF7. We’re making more of life fit around loving it.*

---

## How to read the archives

```bash
# from Final-Fantasy-7-Modding repo root
gzip -dc docs/history/extracts/2024-09-csr-dev-thread-messages.md.gz | less
gzip -dc docs/history/extracts/2024-11-csr-channel-messages.md.gz | less
# or JSON for tools:
gzip -dc docs/history/extracts/all-messages-merged.json.gz | head
```

Sanitized HARs (research / re-extract):

```bash
gzip -dc docs/history/archive/2024-09-csr-dev-thread.sanitized.har.gz > /tmp/t.har
python scripts/har_discord_messages.py /tmp/t.har -o /tmp/out
```

---

## Repos today (snapshot)

| Repo | Holds |
|------|--------|
| **Final-Fantasy-7-CSR** | CSR & Highwind bases, CSR+ scene packs, builder CDN packs |
| **Final-Fantasy-7-Modding** | Encounter (and future engine) mods, RE docs, **this history** |
| **individualcontributordev.github.io** | Player builder UI |

Living backlog (short, public): each repo’s `docs/SUGGESTIONS.md`.

---

## Credit, without a scoreboard

This history is deliberately light on “who won an argument.”  
It is heavy on the fact that **many people** showed up—maintainers, practice
maniacs, hardware tinkerers, category specialists, joke-posters who still filed
a crisp bug. The archives name them in their own words. The products still
shipping are the dedication.

— Compiled 2026-08-01 from sanitized Discord HAR exports.
