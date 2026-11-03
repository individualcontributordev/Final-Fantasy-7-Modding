"""Edges -> out/graph_reach.png/.pdf: only nodes reachable from field 116 (new game) by any jump/gateway, conditions ignored.
Left-to-right layers = fewest jumps from field 116 (116 far left, LASTMAP far right). Solid arrows go forward, dashed arrows go
back or sideways. Gold = one shortest 116 -> LASTMAP route (jump count only, conditions ignored). Orange boxes = world-map locations.
The all-to-all 'walk' hub edges count for distance but are only drawn on the gold route."""
import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D
import networkx as nx
import numpy as np
from graph import build, nm, d

END = next(i for i, n in nm.items() if n == 'LASTMAP')
E, W = build()
out = {}
for a, b, k, *_ in E: out.setdefault(a, []).append((b, k))
dist, par, q = {116: 0}, {}, [116]         # plain reachability, 'walk' hub edges included
while q:
    a = q.pop(0)
    for b, k in out.get(a, []):
        if b not in dist: dist[b], par[b] = dist[a] + 1, (a, k); q.append(b)
hit = set(dist)
route, n = [], END                         # gold edges, END back to 116
while n != 116: a, k = par[n]; route.append((a, n, k)); n = a
name = lambda n: 'WM%d' % (n - 1000) if n >= 1000 else nm.get(n, str(n))
label = lambda n: '%d %s' % (n - 999 if n >= 1000 else n, name(n))   # WM stub k is field id k+1
BG, FG = '#0d1117', '#c9d1d9'
KIND = {'inf': ('#8b949e', 'gateway (INF exit)'), 'MAPJUMP': ('#ff7b72', 'script jump (MAPJUMP)'),
        'PMJMP': ('#56d364', 'script jump (PMJMP)'), 'wm': ('#ffa657', 'world map -> field')}
G = nx.DiGraph()
for a, b, k, c, p in E:
    if k != 'walk' and a in hit and a != b: G.add_edge(a, b, k=k)
nodes = list(G)

# layers by distance; a layer taller than CAP is split into staggered sub-columns
FS, CAP, ROW, GAP, SUB = 7, 60, 7 * 1.9 + 7, 130, 40
layers = {}
for n in nodes: layers.setdefault(dist[n], []).append(n)
w = {n: (len(label(n)) * FS * 0.62 + 6) * (1.3 if n >= 1000 else 1) for n in nodes}
y = {n: (i + .5) / len(L) for L in layers.values() for i, n in enumerate(sorted(L, key=name))}
nb = {n: list(G.pred[n]) + list(G.succ[n]) for n in nodes}
for it in range(30):                       # barycentre sweeps, alternating direction; y = relative rank in its layer
    for dl in (sorted(layers) if it % 2 == 0 else sorted(layers, reverse=True)):
        L = layers[dl]
        bc = {n: np.mean([y[m] for m in nb[n]]) if nb[n] else y[n] for n in L}
        for r, n in enumerate(sorted(L, key=lambda n: bc[n])): y[n] = (r + .5) / len(L)
P, x0, colx = {}, 0, {}
for dl in sorted(layers):
    L = sorted(layers[dl], key=lambda n: y[n])
    nc = -(-len(L) // CAP)
    cw = max(w[n] for n in L)
    for i, n in enumerate(L):
        c = i % nc                         # neighbours in the order land in different sub-columns
        P[n] = (x0 + c * (cw + SUB) + cw / 2, ((i // nc) - (len(L) / nc - 1) / 2) * -ROW)
    colx[dl] = x0 + (nc * cw + (nc - 1) * SUB) / 2
    x0 += nc * cw + (nc - 1) * SUB + GAP
H = max(abs(p[1]) for p in P.values()) + 120
fig, ax = plt.subplots(figsize=(x0 / 72, 2 * H / 72 + 2), dpi=100, facecolor=BG)
ax.set_facecolor(BG); ax.set_xlim(-60, x0); ax.set_ylim(-H, H + 60); ax.axis('off')
fig.subplots_adjust(0, 0, 1, 1 - 1.4 / fig.get_figheight())

cmap = plt.get_cmap('cool')
top = max(dist[n] for n in nodes)
box = {}
for n in nodes:
    x, yy = P[n]; wmn = n >= 1000; c = cmap(dist[n] / top)
    box[n] = ax.add_patch(Rectangle((x - w[n] / 2, yy - ROW / 2 + 3.5), w[n], ROW - 7, fc='#ffa657' if wmn else '#161b22', ec='#ffa657' if wmn else c, lw=1.2, zorder=3))
    ax.text(x, yy, label(n), ha='center', va='center', fontsize=FS + (1 if wmn else 0), fontweight='bold' if wmn else 'normal', color=BG if wmn else c, zorder=4)
for dl in layers: ax.text(colx[dl], H + 20, dl, ha='center', color='#6e7681', fontsize=10)
ax.text(0, H + 50, 'jumps from field 116', color='#6e7681', fontsize=10, ha='left')

def arrow(a, b, color, lw, ls, rad, z, ms, alpha):
    ax.add_patch(FancyArrowPatch(P[a], P[b], patchA=box[a], patchB=box[b], shrinkA=0, shrinkB=0, arrowstyle='-|>', mutation_scale=ms,
                                 connectionstyle='arc3,rad=%g' % rad, color=color, lw=lw, ls=ls, alpha=alpha, zorder=z))
for a, b, dd in G.edges(data=True):
    fwd = dist[a] < dist[b]
    arrow(a, b, KIND[dd['k']][0], 1.1 if fwd else 0.6, '-' if fwd else (0, (4, 3)), 0.06 if fwd else 0.28, 2, 13 if fwd else 8, 0.9 if fwd else 0.16)
for a, b, k in route:
    arrow(a, b, '#ffd33d', 3, '-' if k != 'walk' else (0, (2, 2)), 0.06, 2.5, 20, 1)

ax.set_title('FF7 field graph: %d nodes, %d edges, reachable from field 116 (left) to LASTMAP (right)' % (G.number_of_nodes(), G.number_of_edges()),
             color=FG, fontsize=28, pad=60, loc='left')
leg = [Line2D([], [], color=KIND[k][0], lw=2, label=KIND[k][1]) for k in KIND]
leg += [Line2D([], [], color='#ffd33d', lw=3, label='one shortest route 116 -> LASTMAP (%d jumps; dotted = free world-map walk)' % len(route)),
        Line2D([], [], color=FG, lw=1.5, label='solid arrow: forward, dashed arrow: back / sideways'),
        Line2D([], [], marker='s', ls='', mfc='none', mec=cmap(0), label='field; colour = jumps from 116')]
fig.legend(handles=leg, loc='lower left', bbox_to_anchor=(0.005, 0.01), facecolor=BG, edgecolor='#30363d', labelcolor=FG, fontsize=14)
os.makedirs('out', exist_ok=True)
fig.savefig('out/graph_reach.png', dpi=100, facecolor=BG); fig.savefig('out/graph_reach.pdf', facecolor=BG)
print(G.number_of_nodes(), G.number_of_edges(), 'fig inches', fig.get_size_inches(), 'route', [name(a) for a, b, k in route[::-1]] + [name(END)])
real = {i for i in nm if i in d and 'ents' in d[i]}
indeg = {b for a, b, *_ in E}
print('real fields', len(real), 'reached', len(real & hit), 'no incoming edge', len(real - indeg), 'unreached but has incoming', len(real - hit - (real - indeg)))
