"""Field ID -> name via the (LBA,size) triple table in FIELD.BIN (DAT,MIM,BSX per field)."""
import struct, json
fb = open('data/raw/d1/FIELD.BIN.dec', 'rb').read()
ls = {}
for l in open('out/d1_ls.txt'):
    p = l.split(None, 2)
    ls[int(p[0])] = p[2].strip()
N = 2362
tab = struct.unpack_from('<%dI' % (N * 2), fb, 0x3A5B8)
names = {}
for i in range(N // 3):
    lba = tab[i * 6]
    names[i] = ls.get(lba, '?')
json.dump(names, open('data/fieldnames.json', 'w'))
if __name__ == '__main__':
    print(len(names), [names[i] for i in (0, 1, 5, 6, 7, 100, 786)])
    print(sum(1 for v in names.values() if v == '?'))
