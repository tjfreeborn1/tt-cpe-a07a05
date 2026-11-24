"""Generate Xschem schematics/symbols for the v4b CPE project from the layout-realistic SPICE netlists.
Pins: res P(0,-30) M(0,30) B(-20,0); nfet D(20,-30) G(-20,0) S(20,30) B(20,0); mim c0(0,-30) c1(0,30);
buf_2 A(-40,0) X(40,0); conb_1 HI(60,-20) LO(60,20). Labels sit exactly on pin coordinates."""
import re, sys, os
TOP = sys.argv[1] if len(sys.argv) > 1 else 'tt_um_tjfreeborn1_cpe_a07a05'
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sim', 'netlists')
HDR = 'v {xschem version=3.4.8RC file_version=1.2}\nG {}\nK {}\nV {}\nS {}\nE {}\n'
class Sch:
    def __init__(s): s.o = [HDR.rstrip('\n')]; s.n = 0
    def lab(s, x, y, net, sym='lab_pin.sym', rot=0, flip=0):
        s.n += 1; s.o.append(f'C {{{sym}}} {x} {y} {rot} {flip} {{name=l{s.n} sig_type=std_logic lab={net}}}')
    def inst(s, sym, x, y, attrs, rot=0, flip=0):
        s.o.append(f'C {{{sym}}} {x} {y} {rot} {flip} {{{attrs}}}')
    def text(s, x, y, t, size=0.4):
        s.o.append(f'T {{{t}}} {x} {y} 0 0 {size} {size} {{}}')
    def save(s, fn): open(fn, 'w').write('\n'.join(s.o) + '\n')
def symbol(fn, name, left, right, h=None):
    n = max(len(left), len(right)); H = h or max(60, 20 * n + 20); W = 120
    o = [HDR.replace('K {}', 'K {type=subcircuit\nformat="@name @pinlist @symname"\ntemplate="name=x1"\n}').rstrip('\n'),
         f'L 4 -60 {-H//2} 60 {-H//2} {{}}', f'L 4 60 {-H//2} 60 {H//2} {{}}', f'L 4 60 {H//2} -60 {H//2} {{}}', f'L 4 -60 {H//2} -60 {-H//2} {{}}',
         f'T {{@symname}} -55 {-H//2-25} 0 0 0.25 0.25 {{}}', f'T {{@name}} -55 {H//2+5} 0 0 0.25 0.25 {{}}']
    for side, pins, sx in (('l', left, -80), ('r', right, 80)):
        for i, p in enumerate(pins):
            y = -H // 2 + 20 + 20 * i
            o += [f'B 5 {sx-2.5} {y-2.5} {sx+2.5} {y+2.5} {{name={p} dir=inout}}',
                  f'L 7 {sx} {y} {sx//abs(sx)*60} {y} {{}}',
                  f'T {{{p}}} {sx//abs(sx)*55 - (0 if sx<0 else 0)} {y-6} 0 {1 if sx>0 else 0} 0.2 0.2 {{}}']
    open(fn, 'w').write('\n'.join(o) + '\n')
    return {p: (-80, -H // 2 + 20 + 20 * i) for i, p in enumerate(left)} | {p: (80, -H // 2 + 20 + 20 * i) for i, p in enumerate(right)}
def kv(s):
    return dict(re.findall(r'(\w+)=([^\s]+)', s))
def net(n): return 'VGND' if n == '0' else n
def leaf(name, ports):
    """Turn a .subckt from SRC/name.spice into name.sch (+ name.sym)."""
    lines = [l for l in open(f'{SRC}/{name}.spice') if l.startswith('X')]
    s = Sch(); s.text(0, -200, f'{name}  (generated from v4b layout-realistic netlist)')
    for i, p in enumerate(ports): s.lab(-300, i * 40, p, 'iopin.sym')
    for i, p in enumerate(ports): s.lab(-300, i * 40, p)
    x = 0; y = 0; col = 0
    for l in lines:
        tok = l.split(); inst = tok[0][1:]; a = kv(l)
        if 'res_xhigh_po' in l:
            p, m, b = map(net, tok[1:4])
            s.inst('sky130_fd_pr/res_xhigh_po_0p35.sym', x, y, f'name=R{inst} L={a["L"]} model=res_xhigh_po_0p35 spiceprefix=X mult=1')
            s.lab(x, y - 30, p); s.lab(x, y + 30, m); s.lab(x - 20, y, b)
        elif 'nfet_01v8' in l:
            d, g, sr, b = map(net, tok[1:5])
            s.inst('sky130_fd_pr/nfet_01v8.sym', x, y, f'name=M{inst} W={a["W"]} L={a["L"]} nf=1 mult={a.get("m","1")} model=nfet_01v8 spiceprefix=X')
            s.lab(x + 20, y - 30, d, flip=1); s.lab(x - 20, y, g); s.lab(x + 20, y + 30, sr, flip=1); s.lab(x + 20, y, b, flip=1)
        elif 'cap_mim' in l:
            c0, c1 = map(net, tok[1:3])
            s.inst('sky130_fd_pr/cap_mim_m3_1.sym', x, y, f'name=C{inst} model=cap_mim_m3_1 W={a["W"]} L={a["L"]} MF={a["MF"]} spiceprefix=X')
            s.lab(x, y - 30, c0); s.lab(x, y + 30, c1)
        else: continue
        col += 1; x += 160
        if col % 8 == 0: x = 0; y += 160
    s.save(f'{name}.sch')
    return symbol(f'{name}.sym', name, ports[:1], ports[1:])
# trimbank switches have RL helpers in sim only -> skipped (not X lines). Ports
pins = {'cpe_a07': leaf('cpe_a07', ['t', 'VGND']), 'cpe_a05': leaf('cpe_a05', ['t', 'VGND']),
        'trimbank': leaf('trimbank', ['t', 'g0', 'g1', 'g2', 'g3', 'g4', 'VGND'])}
# ---------------- top level
s = Sch(); s.text(-400, -500, f'{TOP}: fractional-order capacitors (CPE) alpha=0.7 on ua[0], alpha=0.5 on ua[1], 5-bit trim banks')
ports_in = ['VGND', 'VDPWR', 'ui_in[7:0]', 'uio_in[7:0]', 'ena', 'clk', 'rst_n']
ports_out = ['uo_out[7:0]', 'uio_out[7:0]', 'uio_oe[7:0]']
for i, p in enumerate(ports_in): s.lab(-900, -400 + 40 * i, p, 'ipin.sym')
for i, p in enumerate(ports_out): s.lab(-900, 0 + 40 * i, p, 'opin.sym')
s.lab(-900, 200, 'ua[7:0]', 'iopin.sym')
def place(sym, x, y, name, conn):
    s.inst(f'{sym}.sym', x, y, f'name={name}')
    for p, n in conn.items(): px, py = pins[sym][p]; s.lab(x + px, y + py, n, flip=1 if px > 0 else 0)
place('cpe_a07', 0, -300, 'xcpe07', {'t': 'ua[0]', 'VGND': 'VGND'})
place('cpe_a05', 0, 0, 'xcpe05', {'t': 'ua[1]', 'VGND': 'VGND'})
place('trimbank', 400, -300, 'xbank07', {'t': 'ua[0]', 'VGND': 'VGND', **{f'g{i}': f'gA{i}' for i in range(5)}})
place('trimbank', 400, 0, 'xbank05', {'t': 'ua[1]', 'VGND': 'VGND', **{f'g{i}': f'gB{i}' for i in range(5)}})
sc = 'name={n} VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__'
for i in range(5):
    for j, (src, dst) in enumerate(((f'ui_in[{i}]', f'gA{i}'), (f'uio_in[{i}]', f'gB{i}'))):
        x, y = 900 + 300 * j, -300 + 80 * i
        s.inst('sky130_stdcells/buf_2.sym', x, y, sc.format(n=f'xbuf{"AB"[j]}{i}'))
        s.lab(x - 40, y, src); s.lab(x + 40, y, dst, flip=1)
k = 0
for bus in ('uo_out', 'uio_out', 'uio_oe'):
    for b in range(8):
        x, y = 800 + 260 * (k % 6), 250 + 120 * (k // 6)
        s.inst('sky130_stdcells/conb_1.sym', x, y, sc.format(n=f'xtie{k}'))
        s.lab(x + 60, y + 20, f'{bus}[{b}]', flip=1); s.lab(x + 60, y - 20, f'nc_hi{k}', flip=1); k += 1
s.save(f'{TOP}.sch')
print('wrote', TOP)
