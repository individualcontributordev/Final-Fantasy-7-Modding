# Finding: BATRES late jals live + stuck battle tone

**Date:** 2026-08-09
**Status:** confirmed (BP hits) / symptom open
**Module:** BATRES @ 801B0000 + BATTLE.X helpers
**Source:** commit `4c347fb` shots + user note on audio freeze

## Live BP order (this kill)

| BP | Result | Key regs | Call |
|----|--------|----------|------|
| **801B0000** | HIT (count 2) | ra=**800A1734**, s5=800F83C6 | BATRES entry |
| **801B0278** | HIT | s2=**0x0020**, ra=801B0278 | jal **801B0E20** |
| **801B02FC** | **MISS** | (armed, hit 0) | jal 800B1060 — flag path not taken |
| **801B0458** | HIT | s2=0x20, s4=0x31, a0..a3=0 | jal **800A31A0**(0,0,0,0) |
| **801B0558** | HIT | a0 loaded -1 in delay | jal **800DCF94**(**-1**) |

User note on 0458: *hits near the end of the fanfare after the initial 801B0000 hit*.

Shots: `docs/801B0000.png`, `801B0278.png`, `801B0458.png`, `801B0558.png`.

## Why 02FC missed (expected)

s2 entered the late block as **0x0020**. Static gates for 801B02FC need **bit 0x2** (and not 0x40/0x8 early exit). Bit **0x20** alone takes the other branch (s4 ends **0x31** at 0458). So 800B1060 is **not** on this random-battle path.

## What the hits actually call

| Callee | Static role (pristine BATTLE_X) |
|--------|----------------------------------|
| **801B0E20** | BATRES-internal: clears tables at 800A D7D8/D7DC/... |
| **800A31A0** | tiny: queue/event slot via 800A2F4C; stores a0..a3 bytes (here all 0) |
| **800DCF94(-1)** | **not** a play call. a0==-1 → `sb 0, 800F1E4F` then jr. a0!=-1 sets flag+id and other code uses 80015248. This site is a **disable/clear**. |

800B1060 only wraps 800A31A0(a0=0xA,a1=2,a2=1) — also not raw AKAO.

## Stuck / frozen tone (user report)

> After **801B0000**, battle sound later breaks: **same tone holds** until world map loads. **Not** caused by pausing on the 801B0000 BP — multiple frames run first. Freeze is after entry into victory path.

Interpretation (working):

1. Freeze is **downstream of BATRES entry**, not the debugger stop itself.
2. Symptom is a **held SPU/BGM voice** (engine stop or missing key-off / missing track switch), **not** FAN2 fanfare melody.
3. Fanfare Skip 0.1.4 already: early-return **800A2974** (victory-queue) + quiet **FAN2.SND**. That can silence fanfare **and** skip work that stock uses around ceremony/music handoff — may leave battle BGM voices stuck until field restores audio.
4. **800DCF94(-1)** at 0558 is a flag clear; need to know if freeze is **before** or **after** this call.

Mod note (patches/README): older bit-0x20 force path was abandoned in 0.1.4; this fight still shows s2 bit **0x20** from normal end flags (800F83C6), separate from that old hack.

## Priority questions

1. First moment freeze is audible: before 0278 / between 0278–0458 / between 0458–0558 / after 0558?
2. Does freeze still happen if 0558/`800DCF94` never runs (unlikely skip) or on stock ISO without fanfare-skip?
3. Does anything still call **800A2974** victory-queue after BATRES on 0.1.4 (patched to jr immediately)?

## Next RE

Isolate freeze vs 0278/0458/0558; then dump/step music transition (AKAO / track change / SPU off), not more pose jals unless pose still wrong.

## Freeze timing (6fb15fb evidence)

| Mode | Result |
|------|--------|
| A **801B0278** | Freeze **NOT** already on at hit. Freeze **starts after continue** past 0278. |
| B **801B0458** | Freeze **already on** when BP hits. |
| C **801B0558** | Freeze already on (downstream of B). |
| D **stock ISO** | **No freeze at all** (verified). |

**Bracket:** freeze is introduced in BATRES work **after 801B0278 returns/continues** and **before 801B0458**.

**Causal class:** Fanfare Skip **0.1.4** regression (stock clean). Not debugger pause on 801B0000.

### Static work in the freeze window (s2≈0x20 path)

After `jal 801B0E20` @0278, before `jal 800A31A0` @0458:

1. Loop **10×** `jal 800A7254` (a2=4)
2. Mask words at 8016+0x36C0…
3. Flag branches: bit0x2/0x4 off → 0354 path; live had **s4=0x31**
4. Optional `jal 80014540`
5. Loop **`jal 800A3354`** up to s4 times (0x31) + wait spin @03FC
6. Then 0458 `800A31A0(0,0,0,0)`

0.1.4 patches (either may cause hang):

- BATTLE.X **800A2974** → immediate `jr ra` (victory-queue stub)
- **ENEMY6/FAN2.SND** body zeroed (fanfare asset silent)

Victory-queue is *not* in the 0278–0458 direct jal list; it is called from **800ABE4C**. Freeze may still be from FAN2 touch during this window, or from main-loop work while 800A3354 yields frames, with stubbed queue side effects.
