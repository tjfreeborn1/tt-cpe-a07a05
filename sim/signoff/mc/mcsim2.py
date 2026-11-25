"""Monte Carlo on the extracted netlist (revision 2, after the independent review).

Fixes against mcsim.py:
- Inputs come from this repository; PDK_ROOT comes from the environment.
- The mismatch seed is unique per (corner, sample) and recorded in the output.
- Each pin is excited on its own (the other pin is AC-grounded), so the result has no pin-to-pin crosstalk.
- Every ngspice log is scanned for errors; the operating point (pin bias and the 10 switch gates) is checked for
  every trim state; output files are unique and deleted before each run; a non-finite value aborts the sample.

Statistics:
- Per-device mismatch from the PDK models (mc_mm_switch=1, per instance).
- Global Gaussian shifts with 3 sigma equal to the PDK corner:
  - resistor res_high_po__var_mult, sigma 5/3 (this is the parameter the xhigh_po base model reads; +-5 is about
    +-8.2 %);
  - MIM camimc, sigma 3.7 %;
  - MIM cpmimc, sigma 0.053 fF/um.
- MOS process: the corner file named on the command line.

Usage: python3 mcsim2.py K0 K1 MOS [SEEDBASE]
"""
import numpy as np, subprocess, sys, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
PDK = os.path.join(os.environ.get('PDK_ROOT', '/home/claude/pdk/share/pdk'), 'sky130A', 'libs.tech', 'ngspice')
NET = os.path.join(REPO, 'sim', 'pex', 'top_pex.spice')
MOS = sys.argv[3]; k0, k1 = int(sys.argv[1]), int(sys.argv[2])
SEEDBASE = int(sys.argv[4]) if len(sys.argv) > 4 else 50000
CI = {'tt': 0, 'ss': 1, 'ff': 2, 'sf': 3, 'fs': 4}[MOS]
OUT = os.path.join(HERE, f'out2_{MOS}'); TMP = os.path.join(HERE, 'tmp2')
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
lin = open(f'{PDK}/r+c/res_typical__cap_typical__lin.spice').read()
assert 'sky130_fd_pr__res_high_po__var_mult = 0.0' in lin, 'unexpected PDK lin file'
BAD = re.compile(r'error|abort|fail|singular|too small|no convergence', re.I)

for k in range(k0, k1):
    seed = SEEDBASE + 1000 * CI + k
    rng = np.random.default_rng(seed); gR, gC, gP = rng.standard_normal(3)
    vm = (5.0 / 3) * gR; ca = 2.0e-15 * (1 + 0.037 * gC); cp = max(0.19e-15 + 0.053e-15 * gP, 0.0)
    L = lin.replace('sky130_fd_pr__res_high_po__var_mult = 0.0', f'sky130_fd_pr__res_high_po__var_mult = {vm:.6f}')
    L, n1 = re.subn(r'camimc=\s*[\d.e-]+', f'camimc= {ca:.6e}', L); L, n2 = re.subn(r'cpmimc = [\d.e-]+', f'cpmimc = {cp:.6e}', L)
    assert n1 == 1 and n2 == 1
    lf = f'{TMP}/lin_{MOS}_{k}.spice'; open(lf, 'w').write(L)
    tag = f'{MOS}_{k}'; outs = []
    b = [f'* mc2 {tag} seed {seed}', '.param mc_mm_switch=1', '.param mc_pr_switch=0', f'.include {PDK}/corners/{MOS}.spice',
         f'.include {PDK}/r+c/res_typical__cap_typical.spice', f'.include {lf}', f'.include {PDK}/corners/{MOS}/specialized_cells.spice',
         f'.option seed={seed}', f'.include {NET}', '.temp 27', '.option rshunt=1e12', 'Vdd vdd 0 1.8']
    b += [f'VG{i} g{i} 0 0' for i in range(5)]
    b += ['VA a 0 dc 1.0 ac 1', 'VB b 0 dc 1.0 ac 0', 'X1 a b g0 g1 g2 g3 g4 g0 g1 g2 g3 g4 vdd 0 toppex', '.control', 'set wr_singlescale', 'option numdgt=7']
    for c in range(6):                       # state 0: all bits off; state c: bit c-1 alone
        if c >= 1: b.append(f'alter VG{c-1} dc=1.8')
        if c >= 2: b.append(f'alter VG{c-2} dc=0')
        b.append('op')
        b.append('echo OPCHK_BEGIN')
        b += ['print v(a)', 'print v(b)'] + [f'print v(x1.swA{i}/G)\nprint v(x1.swB{i}/G)' for i in range(5)]
        b.append('echo OPCHK_END')
        for pin, (sa, sb) in (('A', (1, 0)), ('B', (0, 1))):
            b += [f'alter VA ac={sa}', f'alter VB ac={sb}', 'ac dec 40 10 100meg']
            fn = f'{TMP}/z_{tag}_{c}_{pin}.dat'; outs.append(fn)
            b.append(f'wrdata {fn} real(-1/i(V{pin})) imag(-1/i(V{pin}))')
    b += ['.endc', '.end']
    for fn in outs:
        if os.path.exists(fn): os.remove(fn)
    sp = f'{TMP}/mc_{tag}.sp'; open(sp, 'w').write('\n'.join(b) + '\n')
    r = subprocess.run(['ngspice', '-b', sp], capture_output=True, text=True)
    log = r.stdout + r.stderr
    errs = [l for l in log.splitlines() if BAD.search(l) and 'warning' not in l.lower()]
    ops = []
    for blk in re.findall(r'OPCHK_BEGIN(.*?)OPCHK_END', r.stdout, re.S):
        ops.append([float(x) for x in re.findall(r'^\S+\s*=\s*([-+\d.eE]+)\s*$', blk, re.M)])
    ops = [o for o in ops if len(o) == 12]
    ok = r.returncode == 0 and not errs and len(ops) == 6 and all(os.path.exists(f) for f in outs)
    if ok:
        for c, v in enumerate(ops):
            on = c - 1
            ok &= abs(v[0] - 1.0) < 1e-3 and abs(v[1] - 1.0) < 1e-3
            for i in range(5):
                want = 1.8 if i == on else 0.0
                ok &= abs(v[2 + 2 * i] - want) < 0.01 and abs(v[3 + 2 * i] - want) < 0.01
    if not ok:
        open(f'{OUT}/FAIL_{k:04d}.log', 'w').write(log[-4000:] + '\nERRS:\n' + '\n'.join(errs[:20]) + f'\nOPS {ops}')
        print('FAIL', tag, flush=True); continue
    Z = {}
    for c in range(6):
        for pin in 'AB':
            d = np.loadtxt(f'{TMP}/z_{tag}_{c}_{pin}.dat'); Z[(c, pin)] = d[:, 1] + 1j * d[:, 2]; f = d[:, 0]
    out = dict(f=f, zA=Z[(0, 'A')], zB=Z[(0, 'B')], gR=gR, gC=gC, gP=gP, seed=seed)
    for i in range(5):
        for pin in 'AB':
            y = 1 / Z[(i + 1, pin)] - 1 / Z[(0, pin)]
            assert np.all(np.isfinite(y)), f'non-finite bank admittance {tag} bit {i} pin {pin}'
            out[f'y{pin}{i}'] = y
    np.savez(f'{OUT}/s{k:04d}.npz', **out)
    for fn in outs: os.remove(fn)
    print(MOS, k, f'seed {seed} gR {gR:+.2f} gC {gC:+.2f}', flush=True)
