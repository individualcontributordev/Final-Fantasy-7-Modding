"""FF7 PSX field (.DAT) reader: LZS -> 7 sections."""
import struct

def lzs(src):
    out = bytearray(); i = 0; n = len(src)
    while i < n:
        flags = src[i]; i += 1
        for bit in range(8):
            if i >= n: break
            if (flags >> bit) & 1:
                out.append(src[i]); i += 1
            else:
                if i + 1 >= n: break
                b1 = src[i]; b2 = src[i + 1]; i += 2
                off = b1 | ((b2 & 0xF0) << 4); ln = (b2 & 0x0F) + 3
                ref = len(out) - ((len(out) - 18 - off) & 0xFFF)
                for k in range(ln):
                    j = ref + k
                    out.append(out[j] if 0 <= j < len(out) else 0)
    return bytes(out)

SEC = ['script', 'walkmesh', 'bg', 'camera', 'inf', 'enc', 'models']

def load_dat(path):
    b = open(path, 'rb').read()
    sz = struct.unpack('<I', b[:4])[0]
    d = lzs(b[4:4 + sz])
    pos = list(struct.unpack('<7I', d[:28]))
    diff = pos[0] - 28
    pos = [p - diff for p in pos]
    pos.append(len(d))
    return {SEC[i]: d[pos[i]:pos[i + 1]] for i in range(7)}, d

if __name__ == '__main__':
    import sys
    s, d = load_dat(sys.argv[1])
    for k, v in s.items(): print(k, len(v), v[:24].hex())
