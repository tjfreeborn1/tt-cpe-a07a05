"""Post-layout corner sims: one ngspice run per (lib, bias, temp); 6 copies of the extracted chip:
copy 0 all bank bits off, copy i (1..5) bank bit i-1 on in both banks."""
import numpy as np, subprocess, sys, os
P = os.path.join(os.environ.get('PDK_ROOT', '/home/claude/pdk/share/pdk'), 'sky130A', 'libs.tech', 'ngspice', 'sky130.lib.spice')
NET = sys.argv[3] if len(sys.argv) > 3 else 'top_pex.spice'
libs = ['tt', 'll', 'hh', 'hl', 'lh'] + [f'{m}_{rc}' for m in ('ss', 'ff', 'sf', 'fs') for rc in ('hh', 'll', 'hl', 'lh')]
cases = [(l, v, 27) for l in libs for v in (0.7, 1.0, 1.5)] + [(l, 1.0, T) for l in ('tt', 'hh', 'll') for T in (0, 70)]
part = int(sys.argv[1]); nparts = int(sys.argv[2]); cases = cases[part::nparts]
out = {}
for lib, vb, T in cases:
    b = [f'* pex {lib} {vb} {T}', f'.lib {P} {lib}', f'.include {NET}', f'.temp {T}', 'Vdd vdd 0 1.8', '.option rshunt=1e12']
    for c in range(6):
        g = ' '.join('vdd' if (c >= 1 and i == c - 1) else '0' for i in range(5))
        b += [f'VA{c} a{c} 0 dc {vb} ac 1', f'VB{c} b{c} 0 dc {vb} ac 1', f'X{c} a{c} b{c} {g} {g} vdd 0 toppex']
    vecs = ' '.join(f'real(-1/i(VA{c})) imag(-1/i(VA{c})) real(-1/i(VB{c})) imag(-1/i(VB{c}))' for c in range(6))
    b += ['.control', 'set wr_singlescale', 'option numdgt=7', 'ac dec 40 10 100meg', f'wrdata zp{part}.dat {vecs}', '.endc', '.end']
    open(f'pp{part}.spice', 'w').write('\n'.join(b) + '\n')
    subprocess.run(['ngspice', '-b', f'pp{part}.spice'], capture_output=True)
    d = np.loadtxt(f'zp{part}.dat'); f = d[:, 0]; cols = d[:, 1:]
    key = f'{lib}|{vb}|{T}'
    Z = lambda k: cols[:, 2 * k] + 1j * cols[:, 2 * k + 1]
    zA = [Z(2 * c) for c in range(6)]; zB = [Z(2 * c + 1) for c in range(6)]
    out[f'cpe_a07|{key}'] = zA[0]; out[f'cpe_a05|{key}'] = zB[0]
    for i in range(5):
        out[f'bankA{i}|{key}'] = 1 / (1 / zA[i + 1] - 1 / zA[0]); out[f'bankB{i}|{key}'] = 1 / (1 / zB[i + 1] - 1 / zB[0])
    print(lib, vb, T, flush=True)
out['f'] = f; np.savez(f'zp_{part}.npz', **out)
