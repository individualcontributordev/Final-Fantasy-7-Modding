# FF7 route graph — status

Data built from the pristine disc BINs (data/raw/d1..d3). Run from this dir; `PYTHONPATH=tools`.

| file | what |
|---|---|
| tools/extract.py | pulls needed files from the BINs |
| tools/ff7field.py | FF7-LZS + field .DAT section split |
| tools/fieldtable.py | field id -> file (FIELD.BIN.dec table @0x3A5B8, 6 u32/field) -> data/fieldnames.json |
| tools/fieldparse.py | per field: INF exits, enc tables, script ops with path conditions -> data/fields.json |
| tools/graph.py | graph + (field, game-moment) BFS; `path()` = shortest hop path -> data/graph.json; `story()` = GM-gated route 116 -> LASTMAP |
| tools/plan.py | `plan()` = story() + greedy flag-write detours (see "Route model") |
| tools/route.py | renders plan() -> out/route_gm.png/.pdf (snake layout, one box per stay) |
| tools/render.py | full layered graph -> out/graph_reach.png/.pdf |
| tools/encsim.py | encounter model (step()/rand() verified; init state not) |
| data/gm_writes.json | every `S000w := v` with field/entity/conds (game-moment progression) |
| data/pickups.json | STITM/SMTRA/DMTRA/GOLDu with conds (items, materia, gil) |
| data/wm_entrances.json | WORLD/FIELD.TBL world->field entrances |

## Facts verified
- Field ids 1..64 = WM0..WM63 stubs. WM stub k+1 <-> FIELD.TBL record k (24 B = 2 x {s16 x, s16 z, u16 tri, u16 field, 4 B dir}). A field exiting to stub k+1 lands on the world map at that record; the record's field is what you enter from there.
- Id 65 STARTMAP, ZZ*, Q_* = debug/test fields (ignore). BLACKBG* are NOT debug: real cutscene hubs reachable from 116. User node rule: 116 is first; any field reachable by jump/gateway is valid; no incoming edge = debug, ignore. 13 ~2 KB junk fields fail to parse (Q_5, BLACKBGA/F/G, WHITEBG1, ONNA_6, BLIN69_2, TRAP, SUBIN_4, PASS, XMVTES, FALLP, FSHIP_26).
- New game starts in MD1STIN (116). Game moment = 16-bit var S000w.
- decode() bug fixed: do not trim after last RET (loop-ending scripts lost their body).

## Route model (tools/graph.py story(), tools/plan.py plan())
- Run: `cd ff7-route && PYTHONPATH=tools python tools/plan.py` (summary + unfixable list), `python tools/route.py` (render). No `-I`. Transient `OSError 22` saving the PNG: rerun.
- Edges: `inf` gateway, `MAPJUMP` 0x60, `PMJMP` 0xD8, `wm` FIELD.TBL, `walk` (free all-to-all WM hub = stand-in, drawn dashed). Conds = path conditions from fieldparse.
- story(): BFS over (field, S000w). GM only rises, never past the next story value written by a field reachable from 116. Jump GM effect = last S000w write earlier in the same script. A value only compared (never written, e.g. 1598) gets a ghost write. Must end LASTMAP at GM >= 1999 (else LookupError).
- Timer: edges with `S015 == 0` / `S016 == 0` (game-over jump to 119) skipped globally (`TIMEOUT`). STTIM (op 0x38) extracted in 13 fields: BWHLIN, BWHLIN2, GLDGATE, MKT_MENS, MOGU_1, NMKIN_5, RCKTIN4, RCKTIN5, SININ2_1, TIN_1, TIN_2, TIN_4, ZCOAL_1. Not modelled per field.
- plan(): replays the route tracking savemap vars (all 0 at new game). On an unmet edge/write cond, fix() inserts a writer (SETBYTE/SETWORD/BITON/BITOFF with a constant) at the nearest earlier position that works, plus a detour (fwd to writer field, on to R[j+1]'s field at same GM, else back). Strict search first, then one ignoring flag conds on the detour (later iterations repair those). Rules learned: never insert before the last earlier write of the same var (oscillation); writer in the edge's own target field is excluded; no "closer to value" heuristic (produced junk writes). Greedy, not globally optimal. Unfixable conds are assumed true and reported; plan() blocks the edge and replans only if the goal stays reachable.
- KEY/KEYON/KEYOFF conds = controller buttons, always satisfiable (not key items). M vars (banks 5/6) = field-local temps, assumed unable to link fields (UNVERIFIED in emulator). PARTY/MEMBER conds not modelled.
- Red box = BATTLE op (0x70) whose S000 conds hold at the stay's GM; box lists ids (`?` = var). Text line: `set Sxxx.b+/-` bit on/off, `Sxxx=n` byte write, amber `assume` = unmet cond.
- Last run: 794 states, 621 stays, 57 rows, 29 flag writes, 21 walk steps, 8 unfixable (below).

## Known gaps / over-approximations (path result is NOT yet a legal route)
- Residual assumed-true conds (state = field,gm): S109==2 and ==8 (field 73 write); S0E1 bitOFF 0 (ELEVTR1 121 gm 11 write); S0E3==7 (258 -> 296); S0E0>=69 (BLIN69_1 264 -> ELEOUT 233; no writer for 69 decoded, constants only reach 68); S183 bitOFF 1 (567 write); S481==3 (737/738 -> 1602). Likely need counters (PLUS/MINUS ops not modelled; fieldparse emits them, planner ignores) or recursive writer-cond planning.
- Planner models only const SETBYTE/SETWORD/BITON/BITOFF; var-source writes, PLUS/MINUS/AND/OR, and 16-bit overlap with byte vars are ignored.
- Route may show flag ping-pong (S0E1 on/off around ELEVTR1/NMKIN_1): legal by conds but probably not minimal.
- Only rows 1-2, 6-7, 9-10, 35-36 of route_gm.png visually checked.
- World map: any WM node reaches any other (no vehicle/terrain model, no cost).
- Unverified opcode arg layouts: SMTRA AP bytes, BATTLE bank, MENU ids.
- INF exits may be script-disabled (line-disable ops not tracked).
- Encounter sim unresolved: field-load init of step_id/offset/RNG idx, danger halfword write, WM encounter code, per-frame move.
- Not started: battle-minimizing route simulator, DuckStation validation of the route, 100% collection route.

## Next steps (in order)
1. Resolve residual conds: model PLUS/MINUS counters, recursive writer-cond planning; find S0E0=69 writer (undecoded script area?).
2. Verify route segments in DuckStation (set GM/flags, walk edges); verify M-var field-local assumption.
3. Real WM connectivity instead of walk hub; gateway enable/disable ops.
4. Battle-minimising simulator on top of plan() route (needs encounter init state).
5. 100% collection route from data/pickups.json.

## Battles (tools/scene.py -> data/scenes.json, data/battles.json)
- SCENE.BIN: 33 blocks x 0x2000, 16 u32 offsets (x4) of gzip scenes; 256 scenes. Battle id b -> scene b>>2, formation b&3.
- Enemy block 184 B at scene+0x298: lv@+32, MP@+0x9C, AP@+0x9E, HP/EXP/gil u32@+0xA4/A8/AC, drop rates@+0x88, drop ids@+0x8C. Enemies in a formation = slot ids at scene+0x118+96*f+16*k. Checked: Mono Drive-class early enemies (exp 16-22, AP 2-3) match field encounter tables (MD1_1 -> 301..303). Scene 1/3/6 are debug scenes (HP 9999/30000 junk).
- battles.json setup = raw 10 u16 of battle-setup (flags unverified: escape/preemptive).

## Field encounter algorithm (FIELD overlay @0x800A0000 = FIELD.BIN.dec offset + 0x800A0000; verified by disassembly, NOT yet by in-game trace)
Function 0x800ABA70, called once per frame in field mode.
- Table ptr: `[0x80071A54]` (+24 if byte `0x8009AC30` != 0) -> 24-byte record: u16 {bit0 on, byte1 rate}, 10 u16 slots (6 std at +2..+0xC, 4 special at +0xE..+0x14).
- Phase byte `0x8009C6D8` += 0x20 each frame; proceed only when it wraps to 0 (every 8th frame). Reset to 0 on battle end/field load.
- Gates: table.on&1, `lhu 0x80114488`==0, `lbu 0x8009AC2F`==0.
- `danger` (u16 0x8007173C) += lhu[0x80074F14 + 132*lh[0x800965E0]] / table.rate   (per-frame movement of the lead model / rate; rate 0 -> div-by-zero break).
- step(): `step_id`(u8 0x8009C540)++, if wraps to 0 `offset`(u8 0x8009AD2C) += 13; returns (rand[step_id] - offset)&0xFF.
- r1 = step(); `[0x800716D0]` = 4 if r1 < (b[0x80062F1B]&0x7F) else 0 (pre-emptive flag; cleared to 0 if a special slot is picked).
- r2 = step(); encounter iff r2 < (danger * b[0x80062F19]) >> 12.   (b[0x80062F19]=0x10 default; Enemy Lure/Away modifies it)
- On encounter: a = (RNG()&0xFF)>>2 (RNG: idx(u8 0x80071C20)++, rand[idx]).
  * Specials: cumulative sum of slot.prob (arith >>26, or >>27 if b[0x80062F1B]&0x80) over special slots 0..3; if a < sum(&0xFF) -> that slot's battle id, [16D0]=0, done.
  * Else std: new RNG()>>2; default = std slot 5; cumulative (>>26, sra: probs>=32 go negative = always first match) over slots 0..4; first with a < sum&0xFF wins.
  * If chosen == last battle id (`lh 0x8007E774`): reroll once with a fresh RNG (same cumulative loop, accepted unconditionally). Else store as last.
  * Battle id -> [0x8009ABF6]; [0x8009ABF5]=2; [0x8007EBC8]=1; call 0x800A1498.
- After battle: danger=0, phase=0 (0x800A1C70); step_id/offset are saved/restored around battle (SCUS 0x80011AC8/BA0), RNG idx persists.
- CT labels: "Formation" 0x80071C20 is really the RNG idx. Decomp (ff7-decomp world.c): 2F19 = encounter rate modifier (world uses x2 when >0x10), 2F1B&0x7F = pre-emptive chance (x2 when >0x10), 2F1B bit7 = halves special-slot odds.
Open: where field load sets step_id/offset; world-map encounter code (WORLD.BIN danger 0x80116284); what `lhu[0x80074F14+..]` equals per frame (walk vs run).

### Encounter model: in-game verification (CSR-plus state, injected table at 0x8011CD30)
- step(): confirmed. step_id=0x62, offset=0xA9 -> r2 = (rand[0x62]-0xA9)&0xFF = 0x8B, matches v0 live.
- Threshold with danger forced to 0xFFFF (via a0, see below): (0xFFFF*0x10)>>12 = 255 -> encounter fired at 0x800ABC48.
- Selection confirmed: RNG idx 0x33 -> first RNG() = rand[0x34]=0x70, a=28; specials empty -> no match; std draw is a FRESH RNG() = rand[0x35]=0xDC, a=55 >= cum 54 -> default slot 5 = 0x105; stored at [0x8009ABF6] (idx ends 0x35). Prediction by formula = 0x105: match.
- Call order inside the trigger: 0x800A1498 (no RNG use), then RNG() at 0x800ABA34 (jal at ABC68), selection, id store at ABE18.
- Pitfalls: (a) load delay slot: register write at the breakpoint right after an `lhu` is overwritten by the pending load; break one instruction later (0x800ABC24, not ABC20).
  (b) halfword at 0x8007173C (danger) reads 0x0001 and ignores write_memory (bytes 0x8007173E+ are writable) even while paused, in this loaded state. Cause unknown (emulator/MCP side?). So per-frame danger accumulation (+0x40 at rate 16) is verified only by disassembly + the lhu/addu/sh at ABBC0..ABBD0, not by observing memory growth.

- tools/encsim.py: Sim(step_id,offset,rng,last,danger).check(tab,move) = one 8-frame check; self-test reproduces the live 0x105 roll (run: PYTHONPATH=tools python tools/encsim.py).
