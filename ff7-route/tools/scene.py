"""Parse BATTLE/SCENE.BIN -> data/scenes.json. battle id b = scene b>>2, formation b&3 (verified against field enc tables by plausibility)."""
import json, struct, zlib


def load():
    b = open('data/raw/d1/BATTLE/SCENE.BIN', 'rb').read()
    sc = []
    for blk in range(33):
        base = blk * 0x2000
        offs = [o * 4 for o in struct.unpack('<16I', b[base:base + 64]) if o != 0xFFFFFFFF]
        for j, o in enumerate(offs):
            end = offs[j + 1] if j + 1 < len(offs) else 0x2000
            sc.append(zlib.decompressobj(31).decompress(b[base + o:base + end]))
    return sc


def parse(s):
    ids = struct.unpack_from('<3H', s, 0)
    en = {}
    for e in range(3):
        if ids[e] == 0xFFFF: continue
        d = s[0x298 + 184 * e:0x298 + 184 * (e + 1)]
        hp, exp, gil = struct.unpack_from('<3I', d, 0xA4)
        mp, ap = struct.unpack_from('<HH', d, 0x9C)
        en[ids[e]] = {'lv': d[32], 'hp': hp, 'exp': exp, 'gil': gil, 'ap': ap, 'drop': list(d[0x88:0x8C]), 'drop_id': list(struct.unpack_from('<4H', d, 0x8C))}
    forms = []
    for f in range(4):
        sl = [struct.unpack_from('<H', s, 0x118 + 96 * f + 16 * k)[0] for k in range(6)]
        forms.append([x for x in sl if x != 0xFFFF])
    setups = []
    for f in range(4):
        r = struct.unpack_from('<10H', s, 0x08 + 20 * f)
        setups.append(list(r))
    return {'enemies': en, 'forms': forms, 'setup': setups}


if __name__ == '__main__':
    out = [parse(s) for s in load()]
    json.dump(out, open('data/scenes.json', 'w'))
    print(len(out))
