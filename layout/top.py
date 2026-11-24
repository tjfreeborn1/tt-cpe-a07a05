"""Top-level layout generator for tt_um_tjfreeborn1_cpe_a07a05 (Magic Tcl)."""
import json, sys, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
PDK = os.path.join(os.environ.get('PDK_ROOT', '/usr/local/share/pdk'), os.environ.get('PDK', 'sky130A'))
sys.path.insert(0, HERE)
from maglib import Tcl, iu
import capblock2 as cb, resarray as ra
TOP = 'tt_um_tjfreeborn1_cpe_a07a05'
DEF = os.path.join(HERE, 'tt_analog_2x2.def')
W, H = 334.88, 225.76
p = json.load(open(os.path.join(HERE, 'plan.json')))
STAGE = int(sys.argv[1]) if len(sys.argv) > 1 else 99
t = Tcl(); t(f'source {HERE}/drcrep.tcl')
geo = {}
# ------------------------------------------------------------------ leaf: capacitor blocks
t('load blk07 -silent'); t('select top cell')
i07 = cb.build(t, p['cpe_a07']['branches'], N=12, tag='a')
for b in i07['branches']: x1, y1, x2, y2 = b['sheet']; t.label('metal4', x1 + 0.5, (y1 + y2) / 2, 'n07_' + b['name'][1:])
t.label('metal4', i07['bank']['tsheet'][0] + 0.5, (i07['bank']['tsheet'][1] + i07['bank']['tsheet'][3]) / 2, 'ua0')
for bit, (x, y) in i07['bank']['exits'].items(): t.label('metal3', x + 0.3, y, f'bA{bit}')
x1, y1, x2, y2 = i07['ring']; t.label('metal1', x1 + 0.3, y1 + 0.3, 'VGND')
t('save blk07')
t('load blk05 -silent'); t('select top cell')
i05 = cb.build(t, p['cpe_a05']['branches'], N=12, tag='b')
for b in i05['branches']: x1, y1, x2, y2 = b['sheet']; t.label('metal4', x1 + 0.5, (y1 + y2) / 2, 'n05_' + b['name'][1:])
t.label('metal4', i05['bank']['tsheet'][0] + 0.5, (i05['bank']['tsheet'][1] + i05['bank']['tsheet'][3]) / 2, 'ua1')
for bit, (x, y) in i05['bank']['exits'].items(): t.label('metal3', x + 0.3, y, f'bB{bit}')
x1, y1, x2, y2 = i05['ring']; t.label('metal1', x1 + 0.3, y1 + 0.3, 'VGND')
t('save blk05')
# ------------------------------------------------------------------ leaf: resistor array
def R(net, nm, kind='R'):
    r = next(x for x in p[net]['res'] if x['name'] == nm); return dict(name=f"{net[-2:]}{nm}", nseg=r['nseg'], L=r['L'], kind=kind)
# stripes ordered by decreasing height so every stripe top merges its urpm with a taller neighbour (urpm width rule)
items = [R('cpe_a07', 'Rp', 'Rp'), R('cpe_a07', 'R1'), R('cpe_a07', 'R2'), R('cpe_a05', 'Rp', 'Rp'), R('cpe_a07', 'R3'), R('cpe_a05', 'R2'),
         R('cpe_a05', 'R1'), R('cpe_a07', 'R4'), R('cpe_a05', 'R3'), R('cpe_a07', 'R5'), dict(name='D', nseg=1, L=2.602, kind='D')]
t('load resarr -silent'); t('select top cell')
ir = ra.build(t, items)
t.label('metal1', ir['ring'][0] + 0.3, ir['ring'][1] + 0.3, 'VGND')
t('save resarr')
json.dump(dict(i07=i07, i05=i05, ir=ir), open('geo.json', 'w'), default=str, indent=0)
# ------------------------------------------------------------------ top
t(f'def read {DEF}')
t(f'cellname rename tt_um_template {TOP}')
t(f'load {TOP}'); t('select top cell')
def stripe(name, x):
    t.rect('metal4', x, 5.0, x + 2.0, 222.5)
    t(f'box values {iu(x)} {iu(5.0)} {iu(x + 2.0)} {iu(222.5)}; label {name} FreeSans 0.25u -metal4')
    t('port make'); t(f'port use {"ground" if name == "VGND" else "power"}'); t('port class bidirectional'); t('port connections n s e w')
stripe('VDPWR', 1.0); stripe('VGND', 4.0)
X7, Y7 = 334.38 - i07['ring'][2], 2.6
X5, Y5 = 6.5 + i05['ring'][2], 2.6
Xr, Yr = 147.4, 6.2
def place(cell, X, Y, orient=''):
    t('box values 0 0 0 0'); t(f'getcell {cell} {orient} child 0 0 parent {iu(X)} {iu(Y)}')
place('blk07', X7, Y7); place('blk05', X5, Y5, 'h'); place('resarr', Xr, Yr)
g7 = lambda x, y: (X7 + x, Y7 + y)
g5 = lambda x, y: (X5 - x, Y5 + y)
gr = lambda x, y: (Xr + x, Yr + y)
geo.update(X7=X7, Y7=Y7, X5=X5, Y5=Y5, Xr=Xr, Yr=Yr)
print('center', g5(i05['ring'][0], 0)[0], '->', g7(i07['ring'][0], 0)[0], ' resarr', gr(ir['ring'][0], 0)[0], gr(ir['ring'][2], 0)[0])
# ---------------------------------------------------------------- stage 2: switches, t, nodes, ground, std cells
if STAGE >= 2:
    sw = {4: (6.0, 8), 3: (6.0, 4), 2: (6.0, 2), 1: (3.0, 2), 0: (1.5, 2)}       # bit: (Wf, nf)
    sw_y = {4: 33.0, 3: 41.6, 2: 50.2, 1: 58.8, 0: 64.4}
    def sd(k): return 0.57 + 0.48 * k
    def switch(side, bit, xs, ys, lane_x, gline_x, exit_xy, gname, bname):
        Wf, nf = sw[bit]
        t.gencell('sky130_fd_pr__nfet_01v8', f'sw{side}{bit}', xs, ys, f'w {Wf} l 0.15 nf {nf} m 1 guard 1 topc 1 botc 0 conn_gates 1 full_metal 1')
        xr = xs + sd(nf) + 0.655
        # sources -> ring li, and met1 ground bar under the switch
        for k in range(0, nf + 1, 2):
            c = xs + sd(k); t.rect('locali', c - 0.085, ys - 0.05, c + 0.085, ys + 0.5)
        # drains: via1 + met2 strap at mid height, out to the lane
        ym = ys + 0.475 + Wf / 2
        for k in range(1, nf + 1, 2):
            c = xs + sd(k)
            t.rect('metal1', c - 0.16, ym - 0.3, c + 0.16, ym + 0.3); t.rect('via1', c - 0.13, ym - 0.2, c + 0.13, ym + 0.2)
        x1 = min(xs + sd(1) - 0.16, lane_x - 0.2); x2 = max(xs + sd(nf - 1) + 0.16, lane_x + 0.2)
        t.rect('metal2', x1, ym - 0.25, x2, ym + 0.25)
        t.rect('metal2', lane_x - 0.2, ym - 0.3, lane_x + 0.2, ym + 0.3)
        t.rect('via2', lane_x - 0.15, ym - 0.2, lane_x + 0.15, ym + 0.2)
        t.rect('metal3', lane_x - 0.25, ym - 0.3, lane_x + 0.25, ym + 0.3)
        t.rect('via3', lane_x - 0.16, ym - 0.16, lane_x + 0.16, ym + 0.16)
        # lane (met4) from the exit up to the strap; exit extension on met3
        ex, ey = exit_xy
        t.rect('metal3', min(ex, lane_x - 0.25), ey - 0.2, max(ex, lane_x + 0.25), ey + 0.2)
        t.rect('metal3', lane_x - 0.25, ey - 0.25, lane_x + 0.25, ey + 0.25)
        t.rect('via3', lane_x - 0.16, ey - 0.16, lane_x + 0.16, ey + 0.16)
        t.rect('metal4', lane_x - 0.15, ey - 0.25, lane_x + 0.15, ym + 0.25)
        t.rect('metal4', lane_x - 0.25, ey - 0.25, lane_x + 0.25, ey + 0.25); t.rect('metal4', lane_x - 0.25, ym - 0.25, lane_x + 0.25, ym + 0.25)
        # gate: extend gate strip up, via1 at the end nearest the gate lines, met3 hop to the line
        gy = ys + Wf + 0.635
        gx = xs + sd(0) + 0.2 if gline_x < xs else xs + sd(nf) - 0.2
        t.rect('metal1', gx - 0.2, gy, gx + 0.2, gy + 0.6)
        t.rect('via1', gx - 0.13, gy + 0.1, gx + 0.13, gy + 0.5)
        t.rect('metal2', gx - 0.2, gy + 0.05, gx + 0.2, gy + 0.55)
        t.rect('via2', gx - 0.15, gy + 0.1, gx + 0.15, gy + 0.5)
        t.rect('metal3', min(gx, gline_x) - 0.2, gy + 0.05, max(gx, gline_x) + 0.2, gy + 0.55)
        t.rect('via2', gline_x - 0.14, gy + 0.1, gline_x + 0.14, gy + 0.5)
        t.rect('metal2', gline_x - 0.19, gy + 0.05, gline_x + 0.19, gy + 0.55)
        # ground bar below the switch (met1) via the source strips
        for k in range(0, nf + 1, 2):
            c = xs + sd(k); t.rect('metal1', c - 0.115, ys - 0.75, c + 0.115, ys + 0.6)
        return dict(gate_y=gy + 0.3, bar=(min(xs, gline_x) , ys - 0.75, xr + 0.2, ys - 0.4), xr=xr)
    ex7 = {int(k): (X7 + v[0], Y7 + v[1]) for k, v in i07['bank']['exits'].items()}
    ex5 = {int(k): (X5 - v[0], Y5 + v[1]) for k, v in i05['bank']['exits'].items()}
    # column A (right of resarray), gate lines on the left of the switches
    rr = Xr + ir['ring'][2]                      # resarray ring right edge
    glA = [rr + 0.65 + 0.5 * j for j in range(5)]
    xsA = glA[-1] + 0.55
    lanesA = [197.6, 198.4, 199.2, 200.0, 200.8]
    rl = Xr + ir['ring'][0]                      # resarray ring left edge
    glB = [rl - 0.65 - 0.5 * j for j in range(5)]
    lanesB = [138.15, 138.95, 139.75, 140.55, 141.35]
    gates = {}
    for j, bit in enumerate((4, 3, 2, 1, 0)):
        Wf, nf = sw[bit]
        a = switch('A', bit, xsA, sw_y[bit], lanesA[j], glA[j], ex7[bit], f'gA{bit}', f'bA{bit}')
        xsB = glB[-1] - 0.55 - (sd(nf) + 0.655)
        b = switch('B', bit, xsB, sw_y[bit], lanesB[j], glB[j], ex5[bit], f'gB{bit}', f'bB{bit}')
        gates[('A', bit)] = (glA[j], a['gate_y']); gates[('B', bit)] = (glB[j], b['gate_y'])
        # ground bars to the resarray ring
        t.rect('metal1', rr - 0.3, a['bar'][1], a['xr'] + 0.1, a['bar'][3])
        t.rect('metal1', xsB - 0.2, b['bar'][1], rl + 0.3, b['bar'][3])
    # ---------------- t routing (met4 at the bottom edge) and resistor t-buses
    t.rect('metal4', 151.81, 0.0, 202.5, 2.45)                # ua[0] strip
    t.rect('metal4', 201.7, 0.0, 202.5, Y7 + i07['bank']['tsheet'][1] + 1.0)
    t.rect('metal4', 132.49, 0.0, 133.39, Y5 + i05['bank']['tsheet'][1] + 1.0)   # ua[1] stub into sheet
    res = ir['res']
    def tbus(names, ybus, xvia):
        xs_ = [Xr + res[n]['a'][0] for n in names]
        for x in xs_:
            ra.via_up(t, x, Yr + 1.0, 'bot')
            t.rect('metal2', x - 0.15, Yr + ybus, x + 0.15, Yr + 1.3)
        t.rect('metal2', min(xs_ + [xvia]) - 0.15, Yr + ybus, max(xs_ + [xvia]) + 0.15, Yr + ybus + 0.4)
        t.rect('metal2', xvia - 0.25, 0.6, xvia + 0.25, Yr + ybus + 0.4)
        t.rect('via2', xvia - 0.15, 0.8, xvia + 0.15, 1.2)
        t.rect('metal3', xvia - 0.25, 0.6, xvia + 0.25, 2.2)
        t.rect('via3', xvia - 0.16, 1.55, xvia + 0.16, 2.0)
        t.rect('metal4', xvia - 0.25, 0.0, xvia + 0.25, 2.45)
    tbus(['07R5', '07R4', '07R3', '07R2', '07R1', '07Rp'], -1.4, Xr + ir['inner'][2] - 0.6)
    # a05 t-bus on met3 (crosses the a07 met2 bus), exits at the left end of the array to the ua[1] strip
    xs5 = [Xr + res[n]['a'][0] for n in ('05R3', '05R2', '05R1', '05Rp')]
    xv5 = Xr + ir['inner'][0] + 0.6
    for x in xs5:
        ra.via_up(t, x, Yr + 1.0, 'bot')
        t.rect('via2', x - 0.14, Yr + 0.8, x + 0.14, Yr + 1.2)
        t.rect('metal3', x - 0.2, Yr - 2.45, x + 0.2, Yr + 1.3)
    t.rect('metal3', xv5 - 0.25, Yr - 2.45, max(xs5) + 0.2, Yr - 2.0)
    t.rect('metal3', xv5 - 0.25, Yr - 4.2, xv5 + 0.25, Yr - 2.0)
    t.rect('via3', xv5 - 0.16, Yr - 4.0, xv5 + 0.16, Yr - 3.6)
    t.rect('metal4', xv5 - 0.25, 0.0, xv5 + 0.25, Yr - 3.4)
    t.rect('metal4', 133.0, 0.0, xv5 + 0.25, 2.45)             # ua[1] strip
    # Rp b-ends to the ring (met1 down)
    for n in ('07Rp', '05Rp'):
        x = Xr + res[n]['b'][0]; t.rect('metal1', x - 0.125, Yr + ir['inner'][1] - 0.3, x + 0.125, Yr + 0.5)
    # ---------------- node routes: risers (met2) above the array, met3 lines to the bus columns
    ytop = Yr + ir['ring'][3] + 0.8
    def node(rn, k, busx, bus_ylo, ycols):
        r_ = res[rn]; x = Xr + r_['b'][0]; yh = Yr + r_['L'] + 3.0
        ra.via_up(t, x, yh, 'top')
        yl = ytop + 0.8 * k
        t.rect('metal2', x - 0.15, yh, x + 0.15, yl + 0.35)
        t.rect('metal2', x - 0.2, yl - 0.05, x + 0.2, yl + 0.35); t.rect('via2', x - 0.15, yl, x + 0.15, yl + 0.3)
        t.rect('metal3', min(x, busx) - 0.2, yl - 0.05, max(x, busx) + 0.2, yl + 0.35)
        t.rect('via2', busx - 0.15, yl, busx + 0.15, yl + 0.3)
        t.rect('metal2', busx - 0.25, min(yl - 0.1, bus_ylo), busx + 0.25, max(yl + 0.4, bus_ylo))
    for k, (rn, bi) in enumerate((('07R1', 0), ('07R2', 1), ('07R3', 2), ('07R4', 3), ('07R5', 4))):
        b = i07['branches'][bi]; node(rn, k, X7 + b['bus'][0], Y7 + (b['bus'][2] if Y7 + b['bus'][2] < ytop else b['bus'][1]), None)
    for k, (rn, bi) in enumerate((('05R1', 0), ('05R2', 1), ('05R3', 2)), start=5):
        b = i05['branches'][bi]; node(rn, k, X5 - b['bus'][0], Y5 + (b['bus'][2] if Y5 + b['bus'][2] < ytop else b['bus'][1]), None)
    # ---------------- ground: plane strap between blocks, VGND stripe to a05 plane, resarray ring to block rings
    # ground strap between the two planes at a height clear of every bus via island
    isl = [(Y7 + b['island'][1], Y7 + b['island'][3]) for b in i07['branches']] + [(Y5 + b['island'][1], Y5 + b['island'][3]) for b in i05['branches']]
    ys_ = next(y for y in [150 + 0.5 * k for k in range(100)] if all(y + 1.6 + 0.5 < a or y - 0.5 > b for a, b in isl) and y + 1.6 < Y5 + i05['ring'][3] - 1.0)
    t.rect('metal3', X5 - 0.6, ys_, X7 + 0.7, ys_ + 1.6)
    geo['gnd_strap_y'] = ys_
    t.rect('metal3', 3.8, 30.0, X5 - i05['ring'][2] + 0.6, 190.0)
    t.rect('via3', 4.3, 31.0, 5.7, 189.0)
    t.rect('metal1', X5 - i05['ring'][0] - 0.3, Yr + ir['ring'][1], rl + 0.3, Yr + ir['ring'][1] + 0.6)
    t.rect('metal1', rr - 0.3, Yr + ir['ring'][1], X7 + i07['ring'][0] + 0.3, Yr + ir['ring'][1] + 0.6)
    geo['gates'] = {f'{k[0]}{k[1]}': v for k, v in gates.items()}
if STAGE >= 3:
    # ---------------- std-cell row, pins, buffers, ties, power
    t(f'addpath {PDK}/libs.ref/sky130_fd_sc_hd/mag')
    yr0 = 219.0
    def cell(name, x, inst):
        t('box values 0 0 0 0'); t(f'getcell sky130_fd_sc_hd__{name} child 0 0 parent {iu(x)} {iu(yr0)}')
    def pin_drop(xp, ylanding):
        """met4 pin stub -> via3 -> met3 -> via2 -> met2 down to ylanding -> via1 -> met1 -> mcon (li below)"""
        t.rect('metal4', xp - 0.25, 223.2, xp + 0.25, 225.76)
        t.rect('via3', xp - 0.16, 223.4, xp + 0.16, 223.8)
        t.rect('metal3', xp - 0.25, 222.8, xp + 0.25, 223.9)
        t.rect('via2', xp - 0.15, 222.9, xp + 0.15, 223.3)
        t.rect('metal2', xp - 0.2, ylanding - 0.25, xp + 0.2, 223.4)
        t.rect('via1', xp - 0.13, ylanding - 0.2, xp + 0.13, ylanding + 0.2)
        t.rect('metal1', xp - 0.16, ylanding - 0.25, xp + 0.16, ylanding + 0.25)
        t.rect('viali', xp - 0.085, ylanding - 0.085, xp + 0.085, ylanding + 0.085)
    outs = [30.82 + 2.76 * k for k in range(24)]
    for k, xp in enumerate(outs):
        xc = xp - 1.035; cell('conb_1', xc, f'tie{k}')
        cell('tapvpwrvgnd_1', xc + 1.38, f'tp{k}'); cell('fill_1', xc + 1.84, f'fa{k}'); cell('fill_1', xc + 2.30, f'fb{k}')
        pin_drop(xp, yr0 + 1.15)
    ins = {('B', i): 116.38 - 2.76 * i for i in range(5)}
    ins.update({('A', i): 138.46 - 2.76 * i for i in range(5)})
    hy = {}
    order = [('B', 4), ('B', 3), ('B', 2), ('B', 1), ('B', 0), ('A', 4), ('A', 3), ('A', 2), ('A', 1), ('A', 0)]
    for j, key in enumerate(order):
        xp = ins[key]; xd = xp - 0.46; xb = xd + 0.92
        cell('diode_2', xd, f'd{key[0]}{key[1]}'); cell('buf_2', xb, f'u{key[0]}{key[1]}')
        t.rect('locali', xp + 0.3, yr0 + 1.0, xp + 0.6, yr0 + 1.34)            # diode <-> buffer A
        pin_drop(xp, yr0 + 1.15)
        # buffer output X -> met2 down to its horizontal line (met3) -> gate line
        xo = xb + 1.19; yo = yr0 + 1.8
        t.rect('viali', xo - 0.085, yo - 0.085, xo + 0.085, yo + 0.085)
        t.rect('metal1', xo - 0.16, yo - 0.2, xo + 0.16, yo + 0.2)
        t.rect('via1', xo - 0.13, yo - 0.15, xo + 0.13, yo + 0.15)
        geo.setdefault('bufout', {})[f'{key[0]}{key[1]}'] = (xo, yo)
    # gate routing: B lines cross above the a05 block on met3 levels 0-4 to their column-B line;
    # A lines drop into the free centre at x 137.35..140.1 (A2-A4 hop on levels 5-7), run on met3 at y~205 to column A
    ylev0 = Y5 + i05['ring'][3] + 0.8
    lev = lambda k: ylev0 + 0.7 * k
    def down_to(xo, yo, yl):
        t.rect('metal2', xo - 0.15, yl - 0.05, xo + 0.15, yo + 0.2)
        t.rect('metal2', xo - 0.19, yl - 0.05, xo + 0.19, yl + 0.35); t.rect('via2', xo - 0.14, yl, xo + 0.14, yl + 0.3)
    def hline(x1, x2, yl): t.rect('metal3', min(x1, x2) - 0.2, yl - 0.05, max(x1, x2) + 0.2, yl + 0.35)
    def up_from(x, yl, ylo):
        t.rect('via2', x - 0.14, yl, x + 0.14, yl + 0.3); t.rect('metal2', x - 0.19, yl - 0.05, x + 0.19, yl + 0.35)
        t.rect('metal2', x - 0.15, ylo, x + 0.15, yl + 0.35)
    bo = geo['bufout']
    for k, b in enumerate((4, 3, 2, 1, 0)):
        xo, yo = bo[f'B{b}']; gx, gy = gates[('B', b)]
        down_to(xo, yo, lev(k)); hline(xo, gx, lev(k)); up_from(gx, lev(k), gy)
    drops = {1: None, 0: None, 2: 137.95, 3: 138.55, 4: 139.15}
    for k, b in enumerate((0, 1, 2, 3, 4)):
        xo, yo = bo[f'A{b}']; gx, gy = gates[('A', b)]
        ya = 204.0 + 0.7 * k
        if drops[b] is None:
            xd = xo; t.rect('metal2', xd - 0.15, ya - 0.05, xd + 0.15, yo + 0.2)
        else:
            xd = drops[b]; kk = {2: 5, 3: 6, 4: 7}[b]
            down_to(xo, yo, lev(kk)); hline(xo, xd, lev(kk)); up_from(xd, lev(kk), ya - 0.05)
        t.rect('metal2', xd - 0.19, ya - 0.05, xd + 0.19, ya + 0.35); t.rect('via2', xd - 0.14, ya, xd + 0.14, ya + 0.3)
        hline(xd, gx, ya); up_from(gx, ya, gy)
    # fills/taps between the tie group and the input groups, nwell + rails across the row
    xa = outs[-1] - 1.035 + 2.76; xbn = ins[('B', 4)] - 0.46
    def nfill(a, b):
        n = int((b - a + 1e-6) // 0.46); g = (b - a) - n * 0.46
        if 1e-6 < g < 0.2: n -= 1
        return n
    x = xa
    for _ in range(nfill(xa, xbn)): cell('fill_1', x, 'fx'); x += 0.46
    xa = ins[('B', 0)] - 0.46 + 2.76; xbn = ins[('A', 4)] - 0.46
    x = xa
    for n in range(nfill(xa, xbn)): cell('tapvpwrvgnd_1' if n % 6 == 0 else 'fill_1', x, 'fy'); x += 0.46
    xend = ins[('A', 0)] - 0.46 + 2.76
    cell('tapvpwrvgnd_1', xend, 'tz')
    t.rect('nwell', outs[0] - 1.035 - 0.19, yr0 + 1.305, xend + 0.46 + 0.19, yr0 + 2.91)
    t.rect('metal1', 1.0, yr0 - 0.24, xend + 0.46, yr0 + 0.24)
    t.rect('metal1', 1.0, yr0 + 2.48, xend + 0.46, yr0 + 2.96)
    # power via stacks to the stripes (staircase)
    for (xs_, yrail) in ((1.2, yr0 + 2.72), (4.2, yr0)):
        t.rect('via1', xs_ + 0.1, yrail - 0.2, xs_ + 1.5, yrail + 0.2)
        t.rect('metal2', xs_, yrail - 1.2, xs_ + 1.6, yrail + 0.24)
        t.rect('via2', xs_ + 0.1, yrail - 1.1, xs_ + 1.5, yrail - 0.7)
        t.rect('metal3', xs_, yrail - 2.0, xs_ + 1.6, yrail - 0.6)
        t.rect('via3', xs_ + 0.1, yrail - 1.9, xs_ + 1.5, yrail - 1.5)

if STAGE >= 1:
    t('select top cell'); t('drcrep 10')
t('save')
t(f'gds write {TOP}.gds')
t('file mkdir lef'); t(f'lef write lef/{TOP}.lef -hide -pinonly')
if STAGE >= 4:
    t('extract do local'); t('extract all'); t('ext2spice lvs'); t(f'ext2spice -o {TOP}_lvs.spice')
t('quit -noprompt')
t.write('top.tcl')
json.dump(geo, open('geo_top.json', 'w'))
