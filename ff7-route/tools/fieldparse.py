"""Parse every field: INF exits, encounter tables, scripts (semantic ops + path conditions) -> data/fields.json."""
import json, struct, sys
from ff7field import load_dat

OPL = {int(k): v for k, v in json.load(open('data/oplen.json')).items()}
NAMES = {int(k): v for k, v in json.load(open('data/fieldnames.json')).items()}
OPER = ['==', '!=', '>', '<', '>=', '<=', '&', '^', '|', 'bitON', 'bitOFF']
WIDE = (2, 4, 6, 7, 12, 14)
BASE = {1: 0, 2: 0, 3: 0x100, 4: 0x100, 11: 0x200, 12: 0x200, 13: 0x300, 14: 0x300, 7: 0x400, 15: 0x400}
SPEC1 = (0xF5, 0xF6, 0xF7, 0xFB, 0xFC)
SPEC2 = (0xF8, 0xFD)
ARITH8 = (0x80, 0x76, 0x78, 0x85, 0x87, 0x89, 0x8B, 0x8D, 0x8F, 0x91, 0x93, 0x82, 0x83, 0x84)
ARITH16 = (0x81, 0x77, 0x79, 0x86, 0x88, 0x8A, 0x8C, 0x8E, 0x90, 0x92, 0x94)


def ref(nib, raw, w=1, signed=False):
    """-> int const, or 'S%03X' (savemap var) / 'M%02X' (field-local), 'w' suffix = 16-bit."""
    if nib == 0:
        if signed and w == 2 and raw >= 0x8000: raw -= 0x10000
        return raw
    if nib in (5, 6): return 'M%02X%s' % (raw, 'w' if nib == 6 and w == 2 else '')
    if nib in BASE: return 'S%03X%s' % (BASE[nib] | raw, 'w' if nib in WIDE and w == 2 else '')
    return '?%d:%d' % (nib, raw)


def u16(d, i): return d[i] | d[i + 1] << 8


def decode(sc, start, end):
    ops, pos = [], start
    while pos < end:
        op = sc[pos]
        n = OPL[op][1]
        if op == 0x28: n = max(sc[pos + 1], 1)
        elif op == 0x0F and pos + 1 < len(sc):
            n += 1 if sc[pos + 1] in SPEC1 else 2 if sc[pos + 1] in SPEC2 else 0
        d = sc[pos:pos + n]
        if len(d) < n: break
        ops.append((pos, op, d))
        pos += n
    return ops


SHIFT = {0x14: 5, 0x15: 5, 0x16: 7, 0x17: 7, 0x18: 7, 0x19: 7, 0x30: 3, 0x31: 3, 0x32: 3, 0xCB: 2, 0xCC: 2}


def jump_target(pos, op, d):
    if op in (0x10, 0x11): return pos + (u16(d, 1) if op == 0x11 else d[1]) + 1
    if op in (0x12, 0x13): return pos - (u16(d, 1) if op == 0x13 else d[1])
    sh = SHIFT.get(op)
    if sh is None: return None
    return pos + sh + (u16(d, sh) if op in (0x15, 0x17, 0x19) else d[sh])


def cond_str(op, d):
    b = d[1]
    if op in (0x14, 0x15):
        return '%s %s %s' % (ref(b >> 4, d[2]), OPER[d[4]] if d[4] < 11 else d[4], ref(b & 15, d[3]))
    if op in (0x16, 0x17, 0x18, 0x19):
        s = op in (0x16, 0x17)
        return '%s %s %s' % (ref(b >> 4, u16(d, 2), 2, s), OPER[d[6]] if d[6] < 11 else d[6], ref(b & 15, u16(d, 4), 2, s))
    if op in (0x30, 0x31, 0x32): return 'KEY%s 0x%X' % ({0x30: '', 0x31: 'ON', 0x32: 'OFF'}[op], u16(d, 1))
    if op == 0xCB: return 'PARTY has %d' % d[1]
    if op == 0xCC: return 'MEMBER %d' % d[1]


def neg(c):
    for a, b in (('==', '!='), ('!=', '=='), ('>=', '<'), ('<=', '>'), ('>', '<='), ('<', '>=')):
        if ' %s ' % a in c: return c.replace(' %s ' % a, ' %s ' % b, 1)
    return 'NOT(%s)' % c


def sem(op, d):
    """Semantic summary of an opcode, or None if irrelevant to routing."""
    nm = OPL[op][0]
    b = d[1] if len(d) > 1 else 0
    if op == 0x60: return ['MAPJUMP', u16(d, 1), list(struct.unpack('<hhH', d[3:9])), d[9]]
    if op == 0xD8: return ['PMJMP', u16(d, 1)]
    if op == 0x20: return ['MINIGAME', u16(d, 1), d[9], d[10]]
    if op == 0x70: return ['BATTLE', ref(b >> 4, u16(d, 2), 2)]
    if op == 0x38: return ['STTIM']
    if op == 0x72: return ['BTLMD', u16(d, 1)]
    if op == 0x71: return ['BTLON', d[1]]
    if op in (0x58, 0x59, 0x5A): return [nm, ref(b >> 4, u16(d, 2), 2), ref(b & 15, d[4])]
    if op == 0x5B: return [nm, ref(b >> 4, d[3]), [ref(b & 15, d[4]), ref(d[2] >> 4, d[5]), ref(d[2] & 15, d[6])]]
    if op == 0x5C: return [nm, ref(b >> 4, d[3]), [ref(b & 15, d[4]), ref(d[2] >> 4, d[5]), ref(d[2] & 15, d[6])], d[7]]
    if op == 0x5D: return [nm, d[1:10].hex()]
    if op in (0x39, 0x3A): return [nm, ref(b >> 4, struct.unpack('<i', d[2:6])[0], 4)]
    if op == 0x49: return ['MENU', d[2], ref(b & 15, d[3])]
    if op == 0x4A: return ['MENU2', d[1]]
    if op in (0xC8, 0xC9, 0xCE, 0xCF, 0xF8): return [nm, d[1]]
    if op == 0xF9: return [nm]
    if op == 0xCA: return ['PRTYE', list(d[1:4])]
    if op == 0xCD: return ['MMBud', d[1], d[2]]
    if op == 0x0F: return ['SPECIAL', d[1], d[2:].hex()]
    if op == 0x21: return ['TUTOR', d[1]]
    if 1 <= op <= 6: return [nm, d[1], d[2] & 31]
    if op == 0x6E: return ['LSTMP', ref(b >> 4, d[2])]
    if op == 0xD2: return ['MPJPO', d[1]]
    if op == 0xF0: return ['MUSIC', d[1]]
    if op == 0x74: return ['GETPC', ref(b >> 4, d[2]), d[3]]
    if op in ARITH8:
        t = ref(b >> 4, d[2])
        return ['VAR', nm, t, ref(b & 15, d[3])] if isinstance(t, str) and t[0] == 'S' else None
    if op in ARITH16:
        t = ref(b >> 4, d[2], 2)
        return ['VAR', nm, t, ref(b & 15, u16(d, 3), 2)] if isinstance(t, str) and t[0] == 'S' else None
    if op in (0x7A, 0x95, 0x7C, 0x97):
        t = ref(b >> 4, d[2])
        return ['VAR', nm, t, 1] if isinstance(t, str) and t[0] == 'S' else None
    if op in (0x7B, 0x96, 0x7D, 0x98):
        t = ref(b >> 4, d[2], 2)
        return ['VAR', nm, t, 1] if isinstance(t, str) and t[0] == 'S' else None
    if op == 0x99:
        t = ref(b >> 4, d[2])
        return ['VAR', nm, t, 'rand'] if isinstance(t, str) and t[0] == 'S' else None
    return None


def analyze(ops):
    """Attach path conditions (list of cond strings that must hold) to each semantic op."""
    reg = []   # (start, end, cond)
    ends = {p + len(d): (p, op, d) for p, op, d in ops}
    for pos, op, d in ops:
        t = jump_target(pos, op, d)
        c = cond_str(op, d) if (0x14 <= op <= 0x19 or op in (0x30, 0x31, 0x32, 0xCB, 0xCC)) else None
        if c and t and t > pos:
            reg.append((pos + len(d), t, c))
            lj = ends.get(t)    # then-part ends with a forward JMPF -> else-part follows
            if lj and lj[1] in (0x10, 0x11):
                jt = jump_target(*lj)
                if jt > t: reg.append((t, jt, neg(c)))
    res = []
    for pos, op, d in ops:
        s = sem(op, d)
        if s: res.append({'pos': pos, 'op': s, 'if': [c for a, b, c in reg if a <= pos < b]})
    return res


def parse_field(fid):
    secs, _ = load_dat('data/raw/d1' + NAMES[fid])
    out = {'id': fid, 'file': NAMES[fid].split('/')[-1][:-4]}
    inf = secs['inf']
    out['map'] = inf[:9].split(b'\0')[0].decode('latin1')
    ex = []
    for i in range(12):
        x = inf[56 + 24 * i:80 + 24 * i]
        if len(x) < 24: break
        line = struct.unpack('<6h', x[:12])
        if not any(line): continue
        ex.append({'i': i, 'to': u16(x, 18), 'dst': list(struct.unpack('<3h', x[12:18])), 'dir': x[20], 'line': list(line)})
    out['exits'] = ex
    e = secs['enc']
    tabs = []
    for t in range(2):
        r = e[24 * t:24 * t + 24]
        if len(r) < 24: break
        sl = struct.unpack('<10H', r[2:22])
        tabs.append({'on': r[0], 'rate': r[1], 'std': [(s >> 10, s & 0x3FF) for s in sl[:6]], 'spc': [(s >> 10, s & 0x3FF) for s in sl[6:]]})
    out['enc'] = tabs
    sc = secs['script']
    ne = sc[2]; nak = u16(sc, 6); post = u16(sc, 4)
    pt = 32 + 8 * ne + 4 * nak
    allpos = []
    for i in range(ne):
        allpos += struct.unpack('<32H', sc[pt + 64 * i:pt + 64 * i + 64])
    akao = struct.unpack('<%dI' % nak, sc[32 + 8 * ne:32 + 8 * ne + 4 * nak]) if nak else ()
    lim = min([a for a in akao if a] + [post])
    bounds = sorted(set(p for p in allpos if p < lim) | {lim})
    ents = []
    for i in range(ne):
        nm = sc[32 + 8 * i:40 + 8 * i].split(b'\0')[0].decode('latin1')
        ps = struct.unpack('<32H', sc[pt + 64 * i:pt + 64 * i + 64])
        scripts, seen = [], set()
        for k, p in enumerate(ps):
            if p >= lim or p in seen: continue
            seen.add(p)
            ops = decode(sc, p, next(b for b in bounds if b > p))
            a = analyze(ops)
            if a: scripts.append({'k': k, 'ops': a})
        ents.append({'name': nm, 'scripts': scripts})
    out['ents'] = ents
    return out


if __name__ == '__main__':
    out = []
    for f in range(1, 787):
        try:
            out.append(parse_field(f))
        except Exception as ex:
            print('ERR', f, NAMES[f], repr(ex)); out.append({'id': f, 'file': NAMES[f], 'err': repr(ex)})
    json.dump(out, open('data/fields.json', 'w'))
    print(len(out), sum(1 for o in out if 'err' in o))
