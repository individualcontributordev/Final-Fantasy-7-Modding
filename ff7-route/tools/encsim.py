"""Field random-encounter simulator (model verified by disassembly + live check, see NOTES.md).
State: step_id/offset/rng_idx (u8), danger (u16), last (last battle id). One call of check() = one
8-frame encounter check (2 step() calls). Danger gain per check = move // rate (move live = 0x400)."""
import os

R = open(os.path.join(os.path.dirname(__file__), '..', 'data', 'rand_table.bin'), 'rb').read()


def sra(v, n): return (v - (1 << 16) if v & 0x8000 else v) >> (n - 16)   # sra(slot<<16, n), slot is u16


class Sim:
    def __init__(s, step_id=0, offset=0, rng=0, last=-1, danger=0, mod=0x10, preempt=0x10):
        s.step_id, s.offset, s.rng, s.last, s.danger, s.mod, s.preempt = step_id, offset, rng, last, danger, mod, preempt

    def step(s):
        s.step_id = (s.step_id + 1) & 255
        if s.step_id == 0: s.offset = (s.offset + 13) & 255
        return (R[s.step_id] - s.offset) & 255

    def rand(s):
        s.rng = (s.rng + 1) & 255
        return R[s.rng]

    def pick(s, tab):
        """tab: {'std': [(prob,id)]*6, 'spc': [(prob,id)]*4}; probs are the 6-bit field."""
        a = s.rand() >> 2
        sh = 27 if s.preempt & 0x80 else 26
        cum = 0
        for p, i in tab['spc']:
            cum += sra(p << 10, sh)
            if a < cum & 255: return i
        def std():
            b, c = s.rand() >> 2, 0
            for p, i in tab['std'][:5]:
                c += sra(p << 10, 26)
                if b < c & 255: return i
            return tab['std'][5][1]
        i = std()
        if i == s.last: i = std()
        s.last = i
        return i

    def check(s, tab, move=0x400):
        """-> (battle_id, preemptive) or None. Mutates state; caller resets danger after a battle."""
        s.danger = (s.danger + move // tab['rate']) & 0xFFFF
        pre = s.step() < (s.preempt & 0x7F)
        if s.step() < (s.danger * s.mod) >> 12:
            return s.pick(tab), pre
        return None


def checks_to_encounter(sim, tab, move=0x400, limit=100000):
    for n in range(1, limit):
        r = sim.check(tab, move)
        if r: return n, r
    return None


if __name__ == '__main__':
    # live case: idx 0x33, injected table, forced threshold 255 -> id 0x105 (rolls 28 then 55)
    tab = {'rate': 16, 'std': [(20, 0x100), (20, 0x101), (9, 0x102), (5, 0x103), (0, 0x104), (0, 0x105)], 'spc': [(0, 0)] * 4}
    s = Sim(step_id=0x62, offset=0xA9, rng=0x33, last=0x292, danger=0xFFBF)
    r = s.check(tab)
    assert r and r[0] == 0x105, r
    print('ok', hex(r[0]), 'rng idx', hex(s.rng))
