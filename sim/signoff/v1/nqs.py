"""V4b: effect of the MOS-capacitor inversion-channel resistance, which the quasi-static BSIM4 model does not
include, on the extracted netlist.

Each 10x10 um MOS-capacitor finger gets a series resistance Reff = Rch/12 in its gate connection. That is the
distributed RC of a channel contacted at both ends (source and drain are both tied to VGND). Rch is the measured
small-signal channel resistance of the same device at that gate voltage (tt corner, 27 C, from v4 C-V runs).
Each bias is simulated with and without Reff.

Usage: python3 nqs.py PART NPARTS
"""
import numpy as np, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from common import run_ngspice, fresh, PDK_NG, PEX
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out_nqs'); TMP = os.path.join(HERE, 'tmp')
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
RCH = {0.5: 301.8e3, 0.6: 59.6e3, 0.7: 23.8e3, 0.8: 14.3e3, 1.0: 8.1e3}   # tt, W/L = 1

def netlist(reff):
    out = []; n = 0
    for line in open(PEX).read().splitlines():
        if reff and 'sky130_fd_pr__nfet_01v8' in line and ' w=10 l=10' in line:
            t = line.split(); g = t[2]; ng = f'nq_{n}'; t[2] = ng
            out.append(' '.join(t)); out.append(f'Rnq{n} {g} {ng} {reff:.3f}'); n += 1
        else:
            out.append(line)
    return '\n'.join(out) + '\n', n

def run(vb, with_r):
    tag = f'v{vb}_{"nqs" if with_r else "qs"}'; reff = RCH[vb] / 12 if with_r else 0
    net, n = netlist(reff); nf = f'{TMP}/nqs_{tag}.spice'; open(nf, 'w').write(net)
    b = [f'* nqs {tag}', f'.lib {PDK_NG}/sky130.lib.spice tt', f'.include {nf}', '.temp 27', '.option rshunt=1e12', 'Vdd vdd 0 1.8'] + [f'VG{i} g{i} 0 0' for i in range(5)]
    b += [f'VA a 0 dc {vb} ac 1', f'VB b 0 dc {vb} ac 0', 'X1 a b g0 g1 g2 g3 g4 g0 g1 g2 g3 g4 vdd 0 toppex', '.control', 'set wr_singlescale', 'option numdgt=7']
    outs = []
    for c in range(6):
        if c >= 1: b.append(f'alter VG{c-1} dc=1.8')
        if c >= 2: b.append(f'alter VG{c-2} dc=0')
        for pin, (sa, sb) in (('A', (1, 0)), ('B', (0, 1))):
            fn = f'{TMP}/zn_{tag}_{c}_{pin}.dat'; outs.append(fn)
            b += [f'alter VA ac={sa}', f'alter VB ac={sb}', 'ac dec 40 10 100meg', f'wrdata {fn} real(-1/i(V{pin})) imag(-1/i(V{pin}))']
    b += ['.endc', '.end']; sp = f'{TMP}/nqs_{tag}.sp'; open(sp, 'w').write('\n'.join(b) + '\n')
    fresh(*outs); run_ngspice(sp)
    Z = {}
    for c in range(6):
        for pin in 'AB':
            d = np.loadtxt(f'{TMP}/zn_{tag}_{c}_{pin}.dat'); Z[(c, pin)] = d[:, 1] + 1j * d[:, 2]; f = d[:, 0]
    o = dict(f=f, zA=Z[(0, 'A')], zB=Z[(0, 'B')])
    for i in range(5):
        for pin in 'AB': o[f'y{pin}{i}'] = 1 / Z[(i + 1, pin)] - 1 / Z[(0, pin)]
    np.savez(f'{OUT}/{tag}.npz', **o); fresh(*outs, nf)
    print(tag, f'MOS fingers with series R: {n}, Reff {reff:.0f} ohm', flush=True)

if __name__ == '__main__':
    part, npart = int(sys.argv[1]), int(sys.argv[2])
    jobs = [(vb, w) for vb in (0.5, 0.6, 0.7, 0.8, 1.0) for w in (False, True)]
    for vb, w in jobs[part::npart]: run(vb, w)
