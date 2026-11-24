"""Resistor array: xhigh_po_0p35 stripes at 0.83 um pitch, one common guard ring.
groups: list of lists of dict(name, nseg, L, kind) ; kind in {'R','Rp','D'}; a 'gap' entry dict(gap=n) inserts n empty pitches.
Series stripes are joined by met1 jumpers (top jumper after even stripe index, bottom after odd).
Ends: stripe0 bottom = 'a' (t side), last stripe end = 'b' (node / ground). Dummies: both ends grounded to the ring."""
from maglib import Tcl
PITCH = 0.83
def head_bot(x): return (x + 0.05, 0.03, x + 0.30, 2.135)
def head_top(x, L): return (x + 0.05, L + 2.025, x + 0.30, L + 4.13)
def build(t: Tcl, items, tag='r'):
    x = 0.0; out = {}; stripes = []
    for it in items:
        if 'gap' in it: x += it['gap'] * PITCH; continue
        n, L = it['nseg'], it['L']
        t.gencell('sky130_fd_pr__res_xhigh_po_0p35', f"{tag}_{it['name']}", x, 0, f'l {L} nx {n} snake 0 guard 0')
        xs = [x + i * PITCH for i in range(n)]
        for i in range(n - 1):
            if i % 2 == 0:       # top jumper
                y1, y2 = L + 3.71, L + 4.13
            else:
                y1, y2 = 0.03, 0.45
            t.rect('metal1', xs[i] + 0.05, y1, xs[i + 1] + 0.30, y2)
        top_end = (n % 2 == 1)
        out[it['name']] = dict(x=xs, L=L, n=n, a=(xs[0] + 0.175, 'bot'), b=(xs[-1] + 0.175, 'top' if top_end else 'bot'),
                               top=L + 4.32, kind=it.get('kind', 'R'))
        stripes += xs
        x = xs[-1] + PITCH
    x1, x2 = stripes[0] - 1.6, stripes[-1] + 0.35 + 1.6
    ymax = max(v['top'] for v in out.values())
    y1, y2 = -2.6, ymax + 1.2
    ring = (x1 - 0.6, y1 - 0.6, x2 + 0.6, y2 + 0.6)
    for (a, b, c, d) in ((x1 - 0.6, y1 - 0.6, x2 + 0.6, y1), (x1 - 0.6, y2, x2 + 0.6, y2 + 0.6), (x1 - 0.6, y1 - 0.6, x1, y2 + 0.6), (x2, y1 - 0.6, x2 + 0.6, y2 + 0.6)):
        for Ly in ('psubdiff', 'locali', 'metal1'): t.rect(Ly, a, b, c, d)
    for (a, b, c, d) in ((x1 - 0.3, y1 - 0.45, x2 + 0.3, y1 - 0.15), (x1 - 0.3, y2 + 0.15, x2 + 0.3, y2 + 0.45), (x1 - 0.45, y1 - 0.3, x1 - 0.15, y2 + 0.3), (x2 + 0.15, y1 - 0.3, x2 + 0.45, y2 + 0.3)):
        t.rect('psubdiffcont', a, b, c, d); t.rect('viali', a, b, c, d)
    # dummies: both heads to the ring with met1
    for nm, v in out.items():
        if v['kind'] != 'D': continue
        for xs in v['x']:
            t.rect('metal1', xs + 0.05, y1 - 0.3, xs + 0.30, 0.5)
            t.rect('metal1', xs + 0.05, v['L'] + 3.6, xs + 0.30, y2 + 0.3)
    return dict(res=out, ring=ring, inner=(x1, y1, x2, y2), ymax=ymax)
def via_up(t, x, y, kind):
    """via1 on a head (met1 widened) at stripe-centre x; kind 'bot' or 'top' head y centre given"""
    t.rect('metal1', x - 0.16, y - 0.35, x + 0.16, y + 0.35)
    t.rect('metal2', x - 0.16, y - 0.35, x + 0.16, y + 0.35)
    t.rect('via1', x - 0.13, y - 0.2, x + 0.13, y + 0.2)
