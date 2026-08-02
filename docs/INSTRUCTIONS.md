# Task: No-swap mod — RE disc-change on pristine

Operational handoff. Agent overwrites this file and pushes.
You: git pull --ff-only, run steps, fill Evidence, commit+push. Say **check**.

## Goal

Find how pristine NTSC-U Disc 1 decides / enforces disc identity and disc swaps.
Baseline: **Unmodified only** (no CSR/Highwind). Later ship an add-on for any base.

Do **not** patch yet. Evidence only.

## Preconditions

- workspace/pristine/FINALFANTASY7_D1.bin (or symlink) present
- Copy for probes — do not mutate the pristine master

## Steps

1. git pull --ff-only
2. Work from repo root.
3. Run Copy-paste (working copy + string hits).
4. Optional: DuckStation notes if you have a save near a disc-change.
5. Paste output under Evidence. Commit this file only (no bins).

## Copy-paste

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only

mkdir -p workspace/iso-extract
PRISTINE="workspace/pristine/FINALFANTASY7_D1.bin"
WORK="workspace/iso-extract/ff7_d1_noswap_re.bin"
cp -f "$PRISTINE" "$WORK"

python3 - <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, "scripts")
from psx_mode2_iso import extract_file, _user, _u32_le, _list_dir

img = Path("workspace/iso-extract/ff7_d1_noswap_re.bin").read_bytes()

def tree(imgb):
    img = memoryview(imgb)
    pvd = _user(img, 16)
    root = pvd[156:156+34]
    def walk(lba, size, prefix=""):
        out = {}
        for name, lb, sz, is_dir in _list_dir(img, lba, size):
            p = f"{prefix}/{name}" if prefix else name
            if is_dir:
                out.update(walk(lb, sz, p))
            else:
                out[p] = sz
        return out
    return walk(_u32_le(root, 2), _u32_le(root, 10))

t = tree(img)
for p in sorted(t):
    if p.startswith("MINT/") or p == "SYSTEM.CNF" or p.startswith("SCUS_") or "DISK" in p.upper():
        print(f"{t[p]:10}  {p}")

for path in ("SYSTEM.CNF", "MINT/DISKINFO.CNF"):
    data = extract_file(img, path)
    print("---", path, "---")
    print(data.decode("ascii", "replace"))

mid = extract_file(img, "MINT/MOVIE_ID.BIN")
print("--- MINT/MOVIE_ID.BIN ---")
print("size", len(mid))
print(mid[:64].hex())
PY

python3 - <<'PY'
from pathlib import Path
img = Path("workspace/iso-extract/ff7_d1_noswap_re.bin").read_bytes()
needles = [
    b"DISK0001", b"DISK0002", b"DISK0003",
    b"DISKINFO", b"Please insert", b"insert disc",
    b"DISC", b"Disk", b"disk",
]
for n in needles:
    hits = []
    start = 0
    while True:
        i = img.find(n, start)
        if i < 0:
            break
        hits.append(i)
        start = i + 1
        if len(hits) >= 12:
            break
    print(f"{n!r}: count_at_least={len(hits)} first={hits[:8]}")
PY
```

## Evidence

```
(paste terminal output here)
```

### Notes (optional)

- DuckStation observations:
- Known disc-change scenes you hit:

## Done when

- Evidence filled and this file pushed
- Say **check**

## Out of scope this turn

- CSR / Highwind images
- Writing a stub or builder pack
- Full disc 2/3 sweeps (next after D1 hits)
