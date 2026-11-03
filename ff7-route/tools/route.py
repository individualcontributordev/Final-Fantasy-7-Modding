"""Story route 116 -> LASTMAP over (field, game moment) -> out/route_gm.png/.pdf. Snake layout, one box per stay in a field."""
import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D
from graph import nm, d, gm_ok
from plan import plan

RED = '#ff4d4d'
BTL = {i: [(x['op'][1], x['if']) for e in o['ents'] for s in e['scripts'] for x in s['ops'] if x['op'][0] == 'BATTLE'] for i, o in d.items() if 'ents' in o}

name = lambda f: 'WM%d' % (f - 1000) if f >= 1000 else nm[f]
fid = lambda f: f - 999 if f >= 1000 else f
P, bad, _ = plan()
assume = {}                                  # (field, gm) -> flag conds the planner could not meet (assumed true)
for a, b, c in bad: assume.setdefault(b[:2], []).append('%s %s %d' % c)
stays = []                                   # consecutive states in one field -> one box; gm list keeps every value seen there
for f, g, k, wr in P:
    if stays and stays[-1]['f'] == f: stays[-1]['gm'].append(g); stays[-1]['wr'] += wr
    else: stays.append({'f': f, 'gm': [g], 'k': k, 'wr': list(wr), 'as': []})
    stays[-1]['as'] += assume.get((f, g), [])
wl = lambda w: '%s.%d+' % (w[0], w[2]) if w[1] == 'BITON' else '%s.%d-' % (w[0], w[2]) if w[1] == 'BITOFF' else '%s=%d' % (w[0], w[2])
for s in stays:
    s['gm'] = sorted(set(s['gm']))
    s['btl'] = sorted({str(b) for b, c in BTL.get(s['f'], []) if any(gm_ok(c, g) for g in s['gm'])})   # only battle ops whose game-moment conds can hold here
    t = []
    if s['btl']: t.append('btl ' + ','.join(s['btl'][:4]) + ('+' if len(s['btl']) > 4 else ''))
    if s['wr']: t.append('set ' + ' '.join(dict.fromkeys(wl(w) for w in s['wr'])))
    if s['as']: t.append('assume ' + ', '.join(dict.fromkeys(s['as'])))
    s['txt'] = ' | '.join(t)
COLS, BW, BH, GX, GY, TOP = 11, 190, 64, 70, 74, 200
BG, FG = '#0d1117', '#c9d1d9'
KIND = {'inf': '#8b949e', 'MAPJUMP': '#ff7b72', 'PMJMP': '#56d364', 'wm': '#ffa657', 'walk': '#ffd33d', 'write': '#8b949e', 'ghost': '#8b949e', 'start': '#8b949e'}
rows = -(-len(stays) // COLS)
W, H = COLS * (BW + GX) + 80, rows * (BH + GY) + TOP + 60
fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')
cmap = plt.get_cmap('cool'); top = max(g for s in stays for g in s['gm'])
pos, seen, box = [], set(), []
for i, s in enumerate(stays):
    r, c = divmod(i, COLS)
    if r % 2: c = COLS - 1 - c                # snake: odd rows run right to left
    x, y = 40 + c * (BW + GX), TOP + r * (BH + GY)
    wm = s['f'] >= 1000; col = cmap((s['gm'][-1] / top) ** .5); b = bool(s['btl'])
    if b: col = RED
    box.append(ax.add_patch(Rectangle((x, y), BW, BH, fc='#4a1414' if b else '#ffa657' if wm else '#161b22', ec='#ffa657' if wm else col, lw=2.6 if b else 1.6, zorder=3,
                                      ls='--' if s['f'] in seen else '-')))
    seen.add(s['f'])
    ax.text(x + BW / 2, y + BH * .27, '%d %s' % (fid(s['f']), name(s['f'])), ha='center', va='center', fontsize=11, fontweight='bold', color=BG if wm else col, zorder=4)
    g = s['gm']; t = 'GM %d' % g[0] if len(g) == 1 else 'GM %d → %d' % (g[0], g[-1]) if len(g) < 4 else 'GM %d → … → %d' % (g[0], g[-1])
    ax.text(x + BW / 2, y + BH * .56, t, ha='center', va='center', fontsize=9, color=BG if wm else FG, zorder=4)
    ax.text(x + BW / 2, y + BH * .84, s['txt'] if len(s['txt']) < 36 else s['txt'][:34] + '…', ha='center', va='center', fontsize=7, color=BG if wm else '#e3b341' if s['as'] else '#8b949e', zorder=4)
    pos.append((x, y))
for i in range(1, len(stays)):
    (x0, y0), (x1, y1) = pos[i - 1], pos[i]; k = stays[i]['k']
    ax.add_patch(FancyArrowPatch((x0 + BW / 2, y0 + BH / 2), (x1 + BW / 2, y1 + BH / 2), patchA=box[i - 1], patchB=box[i], shrinkA=0, shrinkB=0,
                                 arrowstyle='-|>', mutation_scale=18, color=KIND[k], lw=2, ls=(0, (2, 2)) if k == 'walk' else '-',
                                 connectionstyle='arc3,rad=0' if y0 == y1 else 'arc3,rad=%g' % (-.5 if (i - 1) // COLS % 2 == 0 else .5), zorder=2))
for r in range(rows):
    a, b = stays[r * COLS]['gm'][0], stays[min((r + 1) * COLS, len(stays)) - 1]['gm'][-1]
    ax.text(10, TOP + r * (BH + GY) - 14, 'row %d   GM %d – %d' % (r + 1, a, b), color='#6e7681', fontsize=11, ha='left', va='center')
ax.text(40, 50, 'FF7 story route: field 116 (MD1STIN) to LASTMAP, game moment (S000w) tracked', color=FG, fontsize=28, fontweight='bold', va='center')
ax.text(40, 100, '%d stays in fields, read left to right (rows alternate direction); GM = S000w on entry/exit' % len(stays), color='#6e7681', fontsize=14, va='center')
leg = [Line2D([], [], color=KIND[k], lw=2, ls=(0, (2, 2)) if k == 'walk' else '-', label=l) for k, l in (('inf', 'gateway / in-field GM step'), ('MAPJUMP', 'script jump (MAPJUMP)'),
       ('PMJMP', 'script jump (PMJMP)'), ('wm', 'world map -> field'), ('walk', 'free world-map walk (not a real mechanic)'))]
leg += [Line2D([], [], marker='s', ls='', mfc='#4a1414', mec=RED, label='red: a start-battle opcode can fire at this game moment (btl ids; ? = from variable)'),
        Line2D([], [], marker='s', ls='--', mfc='none', mec=FG, label='dashed border: field visited before (detour or return)'), Line2D([], [], color='#e3b341', label='set Sxxx.b+/-: flag bit on/off, Sxxx=n: byte write, amber assume: unmet cond'), Line2D([], [], marker='s', ls='', mfc='none', mec=cmap(0), label='colour: GM, cyan early to magenta late')]
fig.legend(handles=leg, loc='upper right', bbox_to_anchor=(.995, 1 - 8 / H), ncol=2, facecolor=BG, edgecolor='#30363d', labelcolor=FG, fontsize=12)
os.makedirs('out', exist_ok=True)
fig.savefig('out/route_gm.png', dpi=100, facecolor=BG); fig.savefig('out/route_gm.pdf', facecolor=BG)
print(len(P), 'states', len(stays), 'stays', rows, 'rows', 'size px', W, H, 'walk steps', sum(s['k'] == 'walk' for s in stays))
