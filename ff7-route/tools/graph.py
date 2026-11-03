"""Build data/graph.json (nodes/edges/gm-writes) and BFS over (field, game moment).
Over-approximation: only S000w conditions are evaluated; every other condition is assumed satisfiable."""
import json, re, struct, collections

d = {o['id']: o for o in json.load(open('data/fields.json'))}
nm = {i: o['file'].split('/')[-1].split('.')[0] for i, o in d.items()}
tbl = open('data/raw/d1/WORLD/FIELD.TBL', 'rb').read()
CMP = re.compile(r'^S000w? (==|!=|>=|<=|>|<) (-?\d+)$')
TIMEOUT = {'S015 == 0', 'S016 == 0'}      # countdown timer (S015..S017) expired -> game-over jump, never on the route
OPS = {'==':int.__eq__, '!=': int.__ne__, '>=': int.__ge__, '<=': int.__le__, '>': int.__gt__, '<': int.__lt__}


def gm_ok(conds, gm):
    for c in conds:
        m = CMP.match(c)
        if m and not OPS[m.group(1)](gm, int(m.group(2))): return False
    return True


def wm_node(k): return 1000 + k          # world-map location of WM stub k (field id k+1 in FIELD.BIN)


def build():
    E, W = [], []                         # edges (src,dst,kind,conds,dstpos), gm writes (field,value,conds)
    for i, o in d.items():
        if 'ents' not in o: continue
        for x in o['exits']:
            E.append((i, x['to'], 'inf', [], x['dst']))
        for e in o['ents']:
            for s in e['scripts']:
                for x in s['ops']:
                    op = x['op']
                    if op[0] in ('MAPJUMP', 'PMJMP'):
                        E.append((i, op[1], op[0], x['if'], op[2] if op[0] == 'MAPJUMP' else None))
                    elif op[0] == 'VAR' and op[1] == 'SETWORD' and op[2] in ('S000w', 'S000') and isinstance(op[3], int):
                        W.append((i, op[3], x['if']))
    # WM stub id k+1 -> world node; world node -> field(s) of FIELD.TBL record k
    E2 = []
    for s, t, kind, c, p in E:
        E2.append((s, wm_node(t - 1) if t <= 64 else t, kind, c, p))
    for k in range(64):
        for sub in (0, 12):
            x, z, tri, f = struct.unpack_from('<hhHH', tbl, k * 24 + sub)
            if f: E2.append((wm_node(k), f, 'wm', [], [x, z, tri]))
    # shortcut: any world location reaches any other (walking/vehicle gating not modelled yet)
    for a in range(64):
        for b in range(64):
            if a != b: E2.append((wm_node(a), wm_node(b), 'walk', [], None))
    return E2, W


def reach(E, W, start=(116, 0), par=None):
    out = collections.defaultdict(list)
    for e in E: out[e[0]].append(e)
    wr = collections.defaultdict(list)
    for f, v, c in W: wr[f].append((v, c))
    seen, q = {start}, [start]
    while q:
        f, g = q.pop(0) if par is not None else q.pop()
        nxt = [(e[1], g) for e in out[f] if gm_ok(e[3], g)]
        nxt += [(f, v) for v, c in wr[f] if gm_ok(c, g)]
        for n in nxt:
            if n not in seen:
                seen.add(n); q.append(n)
                if par is not None: par[n] = (f, g)
    return seen


if __name__ == '__main__':
    E, W = build()
    json.dump({'names': {str(k): v for k, v in nm.items()}, 'edges': E, 'gmwrites': W}, open('data/graph.json', 'w'))
    S = reach(E, W)
    fs = {f for f, g in S}
    print(len(E), 'edges', len(W), 'gm writes;', len(S), 'states', len(fs), 'fields reached')
    print('unreached real fields:', sorted(nm[i] for i in d if 'ents' in d[i] and i not in fs)[:120])
    print('GM values reached:', sorted({g for f, g in S})[-12:])


def story(end='LASTMAP', block=()):
    """Shortest (field, game moment) path 116 -> end. -> [(field, gm, kind of edge taken into this state)].
    GM only rises, and never past the next story value written by a field reachable from 116 (no skipping story beats).
    A jump's gm effect = last S000w write earlier in the same script. A value that is only compared (`S000w == v`) but never
    written by a reachable field gets a ghost write (the writer is not decoded yet, e.g. 1598)."""
    import bisect
    E, W = build()
    out, wr = collections.defaultdict(list), collections.defaultdict(list)
    for e in E: out[e[0]].append(e)
    seen, q = {116}, [116]
    while q:
        for e in out[q.pop()]:
            if e[1] not in seen: seen.add(e[1]); q.append(e[1])
    pair, V, G = {}, set(), set()
    for i in seen & {i for i in d if 'ents' in d[i]}:
        for en in d[i]['ents']:
            for s in en['scripts']:
                last = None
                for x in s['ops']:
                    op = x['op']
                    if op[0] == 'VAR' and op[1] == 'SETWORD' and op[2] in ('S000w', 'S000') and isinstance(op[3], int):
                        last = op[3]; V.add(op[3]); wr[i].append((op[3], x['if']))
                    elif op[0] in ('MAPJUMP', 'PMJMP') and last is not None: pair[(i, op[0], op[1], tuple(x['if']))] = last
                    for c in x['if']:
                        m = CMP.match(c)
                        if m and m.group(1) == '==': G.add(int(m.group(2)))
    G -= V
    V = sorted(V | G)

    def nxt(g): k = bisect.bisect_right(V, g); return V[k] if k < len(V) else None
    def ok(g, v): n = nxt(g); return v > g and n is not None and v <= n
    goal = next(i for i in nm if nm[i] == end)
    start = (116, 0); par = {start: None}; q = collections.deque([start])
    while q:
        f, g = q.popleft()
        if f == goal and g >= 1999: break
        step = []
        for e in out[f]:
            if not gm_ok(e[3], g) or TIMEOUT <= set(e[3]) or (f, e[1], e[2]) in block: continue
            g2 = pair.get((f, e[2], e[1] if e[1] < 1000 else e[1] - 999, tuple(e[3]))) if e[2] in ('MAPJUMP', 'PMJMP') else None
            step.append(((e[1], g2 if g2 is not None and ok(g, g2) else g), e[2]))
        step += [((f, v), 'write') for v, c in wr[f] if gm_ok(c, g) and ok(g, v) and (f, v, 'write') not in block]
        if nxt(g) in G: step.append(((f, nxt(g)), 'ghost'))
        for s, k in step:
            if s not in par: par[s] = ((f, g), k); q.append(s)
    if not (f == goal and g >= 1999): raise LookupError('goal unreachable')
    t, P = (goal, g), []
    while t != start: p, k = par[t]; P.append((*t, k)); t = p
    return [(116, 0, 'start')] + P[::-1]


def path(goal=lambda f, g: g >= 1997):
    E, W = build(); par = {}
    S = reach(E, W, par=par)
    t = next((s for s in sorted(S, key=lambda s: s[1]) if goal(*s)), None)
    out = []
    while t != (116, 0):
        out.append(t); t = par[t]
    return [(nm.get(f, 'WM%d' % (f - 1000)) if f < 1000 else 'WM%d' % (f - 1000), g) for f, g in out[::-1]]
