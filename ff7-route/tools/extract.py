"""Extract field DAT + key files from the three pristine discs into data/raw/discN/."""
import sys, os
sys.path.insert(0, r'D:\projects\ff7-modding\Final-Fantasy-7-Modding\scripts')
from psx_mode2_iso import walk_tree, extract_file
PR = r'D:\projects\ff7-modding\Final-Fantasy-7-Modding\workspace\pristine'
for d in (1, 2, 3):
    img = open(f'{PR}\FINALFANTASY7_D{d}.BIN', 'rb').read()
    tree = walk_tree(img)
    out = f'data/raw/d{d}'
    n = 0
    for p, f in tree.items():
        if p.endswith('/'): continue
        up = p.upper()
        keep = (up.endswith('.DAT') and '/FIELD/' in up) or up in (
            '/SCUS_941.63', '/BATTLE/SCENE.BIN', '/BATTLE/BATTLE.X', '/INIT/KERNEL.BIN', '/FIELD/FIELD.BIN',
            '/WORLD/WORLD.BIN', '/WORLD/FIELD.TBL', '/WORLD/WM0.EV', '/WORLD/WM2.EV', '/WORLD/WM3.EV', '/MINT/MOVIE_ID.BIN',
            '/BATTLE/BATRES.X', '/BATTLE/BATINI.X', '/INIT/WINDOW.BIN') or up.startswith('/MINI/')
        if not keep: continue
        dst = out + p
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'wb').write(extract_file(img, p)); n += 1
    print('disc', d, n, 'files')
