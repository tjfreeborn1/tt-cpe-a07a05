"""V1: model-error robustness envelope on the extracted netlist (typical corner, 27 C, 1.0 V, no mismatch).

How each error is applied (each method was verified on a single device first):
- MOS capacitors (nfet w=10 l=10): instance multiplier m=kM. (`mult=` is ignored by the model; `m=` scales C.)
- Resistors: the segment length is rewritten so that R = 5708.6*L + 623 ohm (tt model) changes by the intended
  amount. `m=` and `mult=` are both ignored by the xhigh_po model.
  - total-R error kR: L' = (kR*R(L) - 623) / 5708.6
  - end-resistance error h: L' = L + h*623/5708.6
- MIM (network and trim bank): camimc and cpmimc are scaled by kC in the r+c lin file.

Usage: python3 v1sim.py PART NPARTS
"""
import numpy as np, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from common import run_ngspice, fresh, PDK_NG, PEX
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out'); TMP = os.path.join(HERE, 'tmp')
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
RHO, RHEAD = 5708.6, 623.0
BR = {'07R1': r'r_07R1/', '07R2': r'r_07R2/', '07Rp': r'r_07Rp/', '07R3': r'blk07_0/n07_3\b', '07R4': r'blk07_0/n07_4\b',
      '07R5': r'blk07_0/n07_5\b', '05R1': r'r_05R1/', '05Rp': r'r_05Rp/', '05R2': r'blk05_0/n05_2\b', '05R3': r'blk05_0/n05_3\b'}

def scenarios():
    S = []
    for kR in (0.75, 0.85, 1.0, 1.15, 1.25):
        for kM in (0.8, 0.9, 1.0, 1.1, 1.2):
            for kC in (0.85, 1.0, 1.15):
                S.append(dict(name=f'g_R{kR}_M{kM}_C{kC}', kR=kR, kM=kM, kC=kC))
    for h in (-0.5, 0.5, 1.0, 2.0):
        S.append(dict(name=f'head_{h:+}', head=h))
    for b in BR:
        for k in (0.75, 1.25):
            S.append(dict(name=f'br_{b}_{k}', br=b, kb=k))
    return S

def netlist(sc):
    src = open(PEX).read(); out = []
    kR, kM, h = sc.get('kR', 1.0), sc.get('kM', 1.0), sc.get('head', 0.0)
    nres = nmos = nbr = 0
    for line in src.splitlines():
        if 'sky130_fd_pr__res_xhigh_po_0p35' in line:
            L = float(re.search(r'l=([\d.]+)', line).group(1)); k = kR
            if 'br' in sc and re.search(BR[sc['br']], line): k = k * sc['kb']; nbr += 1
            L2 = (k * (RHO * L + RHEAD) - RHEAD) / RHO + h * RHEAD / RHO
            line = re.sub(r'l=[\d.]+', f'l={L2:.4f}', line); nres += 1
        elif 'sky130_fd_pr__nfet_01v8' in line and ' w=10 l=10' in line and kM != 1.0:
            line = line + f' m={kM}'; nmos += 1
        out.append(line)
    if 'br' in sc: assert nbr >= 1, sc
    return '\n'.join(out) + '\n', nres, nmos, nbr

def run(sc):
    tag = sc['name']; net, nres, nmos, nbr = netlist(sc)
    nf = f'{TMP}/net_{tag}.spice'; open(nf, 'w').write(net)
    lin = open(f'{PDK_NG}/r+c/res_typical__cap_typical__lin.spice').read(); kC = sc.get('kC', 1.0)
    lin, n1 = re.subn(r'camimc=\s*([\d.e-]+)', lambda m: f'camimc= {float(m.group(1))*kC:.6e}', lin)
    lin, n2 = re.subn(r'cpmimc = ([\d.e-]+)', lambda m: f'cpmimc = {float(m.group(1))*kC:.6e}', lin); assert n1 == 1 and n2 == 1
    lf = f'{TMP}/lin_{tag}.spice'; open(lf, 'w').write(lin)
    b = [f'* v1 {tag}', '.param mc_mm_switch=0', '.param mc_pr_switch=0', f'.include {PDK_NG}/corners/tt.spice',
         f'.include {PDK_NG}/r+c/res_typical__cap_typical.spice', f'.include {lf}', f'.include {PDK_NG}/corners/tt/specialized_cells.spice',
         f'.include {nf}', '.temp 27', '.option rshunt=1e12', 'Vdd vdd 0 1.8'] + [f'VG{i} g{i} 0 0' for i in range(5)]
    b += ['VA a 0 dc 1.0 ac 1', 'VB b 0 dc 1.0 ac 0', 'X1 a b g0 g1 g2 g3 g4 g0 g1 g2 g3 g4 vdd 0 toppex', '.control', 'set wr_singlescale', 'option numdgt=7']
    outs = []
    for c in range(6):
        if c >= 1: b.append(f'alter VG{c-1} dc=1.8')
        if c >= 2: b.append(f'alter VG{c-2} dc=0')
        for pin, (sa, sb) in (('A', (1, 0)), ('B', (0, 1))):
            fn = f'{TMP}/z_{tag}_{c}_{pin}.dat'; outs.append(fn)
            b += [f'alter VA ac={sa}', f'alter VB ac={sb}', 'ac dec 40 10 100meg', f'wrdata {fn} real(-1/i(V{pin})) imag(-1/i(V{pin}))']
    b += ['.endc', '.end']; sp = f'{TMP}/{tag}.sp'; open(sp, 'w').write('\n'.join(b) + '\n')
    fresh(*outs); run_ngspice(sp)
    Z = {}
    for c in range(6):
        for pin in 'AB':
            d = np.loadtxt(f'{TMP}/z_{tag}_{c}_{pin}.dat'); Z[(c, pin)] = d[:, 1] + 1j * d[:, 2]; f = d[:, 0]
    o = dict(f=f, zA=Z[(0, 'A')], zB=Z[(0, 'B')])
    for i in range(5):
        for pin in 'AB': o[f'y{pin}{i}'] = 1 / Z[(i + 1, pin)] - 1 / Z[(0, pin)]
    np.savez(f'{OUT}/{tag}.npz', **o); fresh(*outs, nf)
    print(tag, f'res {nres} mos-scaled {nmos} branch-segs {nbr}', flush=True)

if __name__ == '__main__':
    part, n = int(sys.argv[1]), int(sys.argv[2])
    for sc in scenarios()[part::n]:
        if not os.path.exists(f'{OUT}/{sc["name"]}.npz'): run(sc)
