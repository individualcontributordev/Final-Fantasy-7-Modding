"""story() route + the detours/flag writes needed so every taken edge's savemap conditions hold.
story() settles S000w (game moment). Here savemap vars (Sxxx, all 0 at new game) are tracked on the route: when an edge needs an
unset flag, a writer op (SETBYTE/SETWORD/BITON/BITOFF with a constant) is inserted at the cheapest earlier route position, with a
there-and-back walk if that position is not in the writer's field. Field-local temp vars (M..) and button checks (KEY..) are not
tracked: they cannot depend on other fields. Greedy, not globally optimal."""
import re, collections
from graph import build, story, nm, d, TIMEOUT, CMP, OPS

P_ = re.compile(r'^(NOT\()?(S[0-9A-F]{3})w? (==|!=|>=|<=|>|<|&|bitON|bitOFF) (-?\d+)\)?$')
NEG = {'==': '!=', '!=': '==', '>=': '<', '<=': '>', '>': '<=', '<': '>=', 'bitON': 'bitOFF', 'bitOFF': 'bitON', '&': '!&'}
APPLY = {'SETBYTE': lambda v, x: x, 'SETWORD': lambda v, x: x, 'BITON': lambda v, x: v | 1 << x, 'BITOFF': lambda v, x: v & ~(1 << x)}


def parse(c):
    m = P_.match(c)
    if not m or m.group(2) == 'S000': return None
    return (m.group(2), NEG[m.group(3)] if m.group(1) else m.group(3), int(m.group(4)))


def test(vals, p):
    var, op, k = p; v = vals.get(var, 0)
    if op == 'bitON': return bool(v >> k & 1)
    if op == 'bitOFF': return not v >> k & 1
    if op == '&': return bool(v & k)
    if op == '!&': return not v & k
    return OPS[op](v, k)


def mk(conds):
    return [(OPS[m.group(1)], int(m.group(2))) for c in conds if (m := CMP.match(c))], [p for c in conds if (p := parse(c))]


okgm = lambda gm, g: all(f(g, k) for f, k in gm)

E, Wg = build()
EE = [(a, b, k, *mk(c)) for a, b, k, c, _ in E if not TIMEOUT <= set(c)]
OUT, INN, EK = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(list)
for a, b, k, gm, fl in EE:
    OUT[a].append((b, k, gm, fl)); INN[b].append((a, k, gm, fl)); EK[a, b, k].append((gm, fl))
GW = collections.defaultdict(list)             # (field, gm value) -> flag conds of each S000w write
for f, v, c in Wg: GW[f, v].append(mk(c)[1])
WRV = collections.defaultdict(list)            # var -> (field, var, kind, value, gm conds, flag conds)
for i, o in d.items():
    for e in o.get('ents', []):
        for s in e['scripts']:
            for x in s['ops']:
                op = x['op']
                if op[0] == 'VAR' and op[1] in APPLY and isinstance(op[3], int) and op[2][0] == 'S' and op[2].rstrip('w') != 'S000':
                    WRV[op[2].rstrip("w")].append((i, op[2].rstrip('w'), op[1], op[3], *mk(x['if'])))
_bc = {}


def bfs(s, g, vals, rev, strict=True):
    key = (s, g, rev, strict, frozenset(vals.items()) if strict else 0)
    if key in _bc: return _bc[key]
    adj = INN if rev else OUT
    par, dist, q = {s: None}, {s: 0}, collections.deque([s])
    while q:
        a = q.popleft()
        for b, k, gm, fl in adj[a]:
            if b not in par and okgm(gm, g) and (not strict or all(test(vals, p) for p in fl)): par[b] = (a, k); dist[b] = dist[a] + 1; q.append(b)
    _bc[key] = par, dist
    return _bc[key]


def unmet(R, i, vals, bad):
    (pf, pg, _, _), (f, g, k, _) = R[i - 1], R[i]
    if k in ('write', 'ghost'): cands = GW.get((pf, g), [])
    elif k in ('start', 'walk'): return []
    else: cands = [fl for gm, fl in EK[pf, f, k] if okgm(gm, pg)]
    best = None
    for fl in cands:
        u = [p for p in fl if not test(vals, p) and (tuple(R[i - 1][:3]), tuple(R[i][:3]), p) not in bad]
        if not u: return []
        if best is None or len(u) < len(best): best = u
    return best or []


def fix(R, V, i, p, banned, excl=None):
    """Insert a write (plus detour) before R[i] so p holds. -> True if done.
    Detour = walk from R[j] to the writer's field and on to R[j+1]'s field (same gm) or back to R[j]'s field. Flag conds met on the
    detour itself are repaired by later iterations (a strict search first, then one that ignores flag conds)."""
    var, best = p[0], None
    lo = max((k for k in range(i) if any(w[0] == var for w in R[k][3])), default=0)   # an earlier write would be overridden by the later one
    for strict in (True, False):
        for j in range(i - 1, lo - 1, -1):         # nearest position first; cost 0 cannot be beaten
            f, g, vals = R[j][0], R[j][1], V[j]
            cands = []
            for w in WRV[var]:
                if w[0] == excl or not okgm(w[4], g) or (w[0], w[1], w[2], w[3], repr(w[5])) in banned: continue
                new = APPLY[w[2]](vals.get(var, 0), w[3])
                if test({**vals, var: new}, p): cands.append(w)
            if not cands: continue
            tgt = R[j + 1][0] if j + 1 < len(R) and R[j + 1][1] == g and R[j + 1][2] not in ('write', 'ghost') else f
            df, db = bfs(f, g, vals, False, strict)[1], bfs(tgt, g, vals, True, strict)[1]
            for w in cands:
                if (var, w[2], w[3]) in [x[:3] for x in R[j][3]] and w[0] == f: continue
                if w[0] in df and w[0] in db and (best is None or df[w[0]] + db[w[0]] < best[0]): best = (df[w[0]] + db[w[0]], j, w, tgt, strict)
            if best and best[0] == 0: break
        if best: break
    if not best: return False
    c, j, w, tgt, strict = best; f, g = R[j][0], R[j][1]; wr = (var, w[2], w[3], w[5], (w[0], w[1], w[2], w[3], repr(w[5])))
    if c == 0: R[j][3].append(wr); return True
    pf, pb = bfs(f, g, V[j], False, strict)[0], bfs(tgt, g, V[j], True, strict)[0]
    fwd, n = [], w[0]
    while pf[n]: a, k = pf[n]; fwd.append([n, g, k, []]); n = a
    fwd.reverse()
    back, n = [], w[0]
    while pb[n]: a, k = pb[n]; back.append([a, g, k, []]); n = a
    (fwd or [R[j]])[-1][3].append(wr)             # w[0] == f never reaches here with c > 0 unless the writer sits on R[j]
    det = fwd + back
    if tgt != f: det[-1][3].extend(R[j + 1][3]); R[j + 1:j + 2] = det    # R[j+1] (same field/gm) is replaced by the detour's end
    else: R[j + 1:j + 1] = det
    return True


def plan1(block, cap=400):
    R = [[f, g, k, []] for f, g, k in story('LASTMAP', block)]
    bad, banned = set(), set()
    for it in range(cap):
        vals, V, hit = {}, [], None
        for i, (f, g, k, wr) in enumerate(R):
            if i and (u := unmet(R, i, V[i - 1], bad)): hit = i, u[0], None; break
            for w in wr:
                if u := [q for q in w[3] if not test(vals, q) and (tuple(R[i - 1][:3]) if i else None, tuple(R[i][:3]), q) not in bad]: hit = i, u[0], w; break
                vals[w[0]] = APPLY[w[1]](vals.get(w[0], 0), w[2])
            if hit: break
            V.append(dict(vals))
        if not hit: break
        i, p, w = hit
        if w is not None and i == 0: R[0][3].remove(w); banned.add(w[4]); continue
        if fix(R, V, i, p, banned, R[i][0] if w is None else None): continue   # a writer in the edge's own target cannot enable the edge
        if w is None: bad.add((tuple(R[i - 1][:3]), tuple(R[i][:3]), p))
        else: R[i][3].remove(w); banned.add(w[4])
    return R, bad, it


def plan(maxrep=30):
    """-> (route [(field, gm, kind, [flag writes (var, op, value)])], unfixable conds, replans).
    An edge whose flag cond cannot be met (no usable writer) is blocked in story() and the route is rebuilt."""
    block = set()
    for rep in range(maxrep):
        try: R, bad, it = plan1(block)
        except LookupError: break                 # blocked every way to the goal: keep the previous result
        best = R, bad, rep
        nb = {(a[0], b[1], 'write') if b[2] == 'write' else (a[0], b[0], b[2]) for a, b, p in bad if b[2] not in ('ghost', 'start', 'walk')} - block
        if not nb: break
        block |= nb
    return [tuple(r) for r in best[0]], best[1], best[2]


if __name__ == '__main__':
    n = lambda f: nm.get(f, 'WM%d' % (f - 1000))
    R, bad, it = plan()
    print(len(R), 'states', it, 'iterations,', sum(bool(r[3]) for r in R), 'with flag writes,', len(bad), 'unfixable')
    for a, b, p in sorted(bad): print('  unfixable', n(a[0]), '->', n(b[0]), b[2], 'gm', a[1], p)
