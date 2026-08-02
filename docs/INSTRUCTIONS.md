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
       270  MINT/DISKINFO.CNF
      1080  MINT/MOVIE_ID.BIN
     28051  MOVIE/DISK1.LZS
     28391  MOVIE/DISK2.LZS
     28477  MOVIE/DISK3.LZS
    397312  SCUS_941.63
        68  SYSTEM.CNF
--- SYSTEM.CNF ---
BOOT = cdrom:\SCUS_941.63;1
TCB = 4
EVENT = 16
STACK = 801fff00

--- MINT/DISKINFO.CNF ---
DISK0001
------------------------------------------------------------
����CD��FinalFantasy7 Disk1�����B
�����������������������������������B

���[�r�[���R�}�����������������������������������o��������
�b�c�������Y���|�����������������������������������������B

→
--- MINT/MOVIE_ID.BIN ---
size 1080
e4f80100d813040000000000400180002c00020067f901008426040000000000400180002c000200ecf90100e068400000000000ff00ff0086000000fb000200


➜  Final-Fantasy-7-Modding git:(main) python3 - <<'PY'
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
b'DISK0001': count_at_least=1 first=[298609944]
b'DISK0002': count_at_least=0 first=[]
b'DISK0003': count_at_least=0 first=[]
b'DISKINFO': count_at_least=2 first=[59986, 298605369]
b'Please insert': count_at_least=0 first=[]
b'insert disc': count_at_least=0 first=[]
b'DISC': count_at_least=12 first=[134202176, 134920908, 135073788, 135265117, 136207817, 137900501, 142109487, 150811728]
b'Disk': count_at_least=3 first=[60724, 60832, 298610038]
b'disk': count_at_least=1 first=[75884300]

### Notes (optional)

- DuckStation observations:
- Known disc-change scenes you hit:

Makou scripts

If Var[3][136] bitON 7 (else goto label 1)
	Play music #0
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=1, param2=127, param3=0, param4=0, param5=0)
	Play a sound effect on channel #1 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Play a sound effect on channel #2 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Play a sound effect on channel #3 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Play a sound effect on channel #4 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Volume control (channel #1) [param1: volume] (param1 (8-bit)=127, param2=0, param3=0, param4=0, param5=0)
	Volume control (channel #2) [param1: volume] (param1 (8-bit)=127, param2=0, param3=0, param4=0, param5=0)
	Volume control (channel #3) [param1: volume] (param1 (8-bit)=127, param2=0, param3=0, param4=0, param5=0)
	Volume control (channel #4) [param1: volume] (param1 (8-bit)=127, param2=0, param3=0, param4=0, param5=0)
	Tempo control (channel #1) (param1 (8-bit)=0, param2=0, param3=0, param4=0, param5=0)
	Tempo control (channel #2) (param1 (8-bit)=0, param2=0, param3=0, param4=0, param5=0)
	Tempo control (channel #3) (param1 (8-bit)=0, param2=0, param3=0, param4=0, param5=0)
	Tempo control (channel #4) (param1 (8-bit)=0, param2=0, param3=0, param4=0, param5=0)
	Set the music #1 for next battle
	Bit 7 OFF in Var[3][136]
	Show menu HP to 1 (parameter Var[3][0])
	Start battle #468
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=255, param2=0, param3=0, param4=0, param5=0)
	Wait 80 frame
	Play music #0
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=0, param2=127, param3=0, param4=0, param5=0)
	Jump to map roadend (#226) (X=-1243, Y=-34, triangle ID=50, direction=0)
Label 1
If Var[13][91] bitON 2 (else goto label 2)
	Bit 7 ON in Var[3][136]
	Bit 2 OFF in Var[13][91]
	Restores full HP and MP of every available character and removing status effects
	Set the window #0 mode: No Background/Border (prevent the closing of the window by the player)
	Set the window #1 mode: Normal (prevent the closing of the window by the player)
	Set the window #2 mode: Normal (prevent the closing of the window by the player)
	Set the window #3 mode: Transparent Background (prevent the closing of the window by the player)
	Wait 1 frame
	Execute script #3 in extern group byke (No6) (priority 6/6) - Only if the script is not already running
	Execute script #3 in extern group bcloud (No7) (priority 6/6) - Only if the script is not already running
	Create window #0 (X=16, Y=8, Width=287, Height=57)
	Displays the dialog "Control the bike with the ¶[Directi...uck from the Shinra Pursuit Troops." in the window #0
Label 2
If Var[3][136] bitON 5 (else goto label 3)
	Bit 5 OFF in Var[3][136]
	Wait 4 frame
	Ask for disc 3
	Play music #2
	Wait 8 frame
	Jump to map las0_1 (#744) (X=-7, Y=-917, triangle ID=243, direction=228)
	Goto label 8
Label 3
If Var[13][82] bitON 6 (else goto label 5)
	Bit 6 OFF in Var[13][82]
	Execute script #4 in extern group cloud (No5) (priority 6/6) - Only if the script is not already running
	Wait 16 frame
	Create window #1 (X=70, Y=125, Width=180, Height=73)
	Ask Question "Save the game to this point on the memory card? Yes No" in the window #1 (and put selected answer in Var[5][0]) first line=2, last line=3
	Restores full HP and MP of every available character and removing status effects
	If Var[5][0] == 2 (else goto label 4)
		Wait 4 frame
		Bit 5 ON in Var[3][136]
		Var[13][0] = 3 (8 bit)
		Show menu Save (parameter 0)
	Label 4
	Bit 5 OFF in Var[3][136]
	Wait 4 frame
	Ask for disc 3
	Play music #2
	Wait 8 frame
	Jump to map las0_1 (#744) (X=-7, Y=-917, triangle ID=243, direction=228)
	Goto label 8
Label 5
If Var[3][134] bitON 2 (else goto label 6)
	Bit 2 OFF in Var[3][134]
	Wait 4 frame
	Ask for disc 2
	Wait 8 frame
	Bit 1 ON in Var[3][137]
	Play music #3
	Wait 8 frame
	Jump to map lost2 (#634) (X=-259, Y=5042, triangle ID=113, direction=0)
	Goto label 8
Label 6
If Var[3][136] bitON 4 (else goto label 8)
	Bit 4 OFF in Var[3][136]
	Execute script #3 in extern group cloud (No5) (priority 6/6) - Only if the script is not already running
	Wait 16 frame
	Create window #1 (X=70, Y=125, Width=180, Height=73)
	Ask Question "Save the game to this point on the memory card? Yes No" in the window #1 (and put selected answer in Var[5][0]) first line=2, last line=3
	If Var[5][0] == 2 (else goto label 7)
		Wait 4 frame
		Bit 2 ON in Var[3][134]
		Var[13][0] = 2 (8 bit)
		Show menu Save (parameter 0)
	Label 7
	Bit 2 OFF in Var[3][134]
	Wait 4 frame
	Ask for disc 2
	Wait 8 frame
	Bit 1 ON in Var[3][137]
	Play music #3
	Wait 8 frame
	Jump to map lost2 (#634) (X=-259, Y=5042, triangle ID=113, direction=0)
Label 8
If Var[3][131] bitON 2 (else goto label 9)
	Deactivate the movability of the playable character
	Disables access to the main menu
	Fades the screen to the colour RGB(0, 0, 0) (speed=0, type=0)
	Volume transitions (channel #1) [param1: transition time, param2: target volume] (param1 (8-bit)=16, param2=0, param3=0, param4=0, param5=0)
	Volume transitions (channel #2) [param1: transition time, param2: target volume] (param1 (8-bit)=16, param2=0, param3=0, param4=0, param5=0)
	Volume control (channel #4) [param1: volume] (param1 (8-bit)=16, param2=0, param3=0, param4=0, param5=0)
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=16, param2=0, param3=0, param4=0, param5=0)
	Wait 6 frame
	Play a sound effect on channel #1 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Play a sound effect on channel #2 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Play a sound effect on channel #3 [param1: panning, param2: effect ID] (param1 (8-bit)=64, param2=0, param3=0, param4=0, param5=0)
	Volume transitions (channel #1) [param1: transition time, param2: target volume] (param1 (8-bit)=1, param2=127, param3=0, param4=0, param5=0)
	Volume transitions (channel #2) [param1: transition time, param2: target volume] (param1 (8-bit)=1, param2=127, param3=0, param4=0, param5=0)
	Volume control (channel #4) [param1: volume] (param1 (8-bit)=1, param2=127, param3=0, param4=0, param5=0)
	Play music #0
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=1, param2=127, param3=0, param4=0, param5=0)
	Set next movie: rcktfail (disc 1), rckethit1 (disc 2), No45 (disc 3)
	Play movie
	Wait 3 frame
	Lock music
	Jump to map rktsid (#558) (X=-41, Y=409, triangle ID=85, direction=240)
	Goto label 10
Label 9
If $GameMoment == 638 (else goto label 10)
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=96, param2=0, param3=0, param4=0, param5=0)
	Wait 48 frame
	Play music #0
	Music volume transition [param1: transition time, param2: target volume] (param1 (8-bit)=1, param2=0, param3=0, param4=0, param5=0)
	Wait 4 frame
	Aerith not available
	Show menu Remove Aerith's Materia
	Jump to map gninn (#522) (X=-119, Y=240, triangle ID=34, direction=255)
Label 10
Return

## Done when

- Evidence filled and this file pushed
- Say **check**

## Out of scope this turn

- CSR / Highwind images
- Writing a stub or builder pack
- Full disc 2/3 sweeps (next after D1 hits)
