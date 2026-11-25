"""V1 analysis: band (best code, worst of 12 pin models, interpolated edges) per model-error scenario."""
import numpy as np, glob, os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'mc'))
from mcan2 import analyze
R = {}
for fn in sorted(glob.glob(f'{HERE}/out/*.npz')):
    R[os.path.basename(fn)[:-4]] = analyze(fn)
nom = R['g_R1.0_M1.0_C1.0']
# check that the MIM scaling really moved the trim bank (bit 4 admittance at 300 kHz)
d0 = np.load(f'{HERE}/out/g_R1.0_M1.0_C1.0.npz'); d1 = np.load(f'{HERE}/out/g_R1.0_M1.0_C1.15.npz'); f = d0['f']; i = np.argmin(abs(f - 3e5))
print(f"check: bank bit-4 C ratio for kC=1.15: {np.imag(d1['yA4'][i])/np.imag(d0['yA4'][i]):.3f}")
print(f"nominal: a07 {nom['cpe_a07']['worst25']:.3f} dec (codes {min(nom['cpe_a07']['codes'])}-{max(nom['cpe_a07']['codes'])}), a05 {nom['cpe_a05']['worst25']:.3f} dec (codes {min(nom['cpe_a05']['codes'])}-{max(nom['cpe_a05']['codes'])})")
print('\nGrid (worst of 12 pin models, +-2.5 deg / +-3 deg), codes used; FAIL if < 3.5 (a07) or < 1.8 (a05)')
for kC in (0.85, 1.0, 1.15):
    print(f'\n kC (MIM) = {kC}')
    print('   kR\\kM  ' + ''.join(f'{kM:^30}' for kM in (0.8, 0.9, 1.0, 1.1, 1.2)))
    for kR in (0.75, 0.85, 1.0, 1.15, 1.25):
        row = f'   {kR:5}  '
        for kM in (0.8, 0.9, 1.0, 1.1, 1.2):
            r = R[f'g_R{kR}_M{kM}_C{kC}']; a, b = r['cpe_a07'], r['cpe_a05']
            fa = '!' if a['worst25'] < 3.5 else ' '; fb = '!' if b['worst25'] < 1.8 else ' '
            ca = f"{min(a['codes'])}-{max(a['codes'])}"; cb = f"{min(b['codes'])}-{max(b['codes'])}"
            row += f"{a['worst25']:.2f}{fa}/{b['worst25']:.2f}{fb} [{ca:>5}|{cb:>5}]  "
        print(row)
print('\nEnd-resistance and single-branch errors (a07 / a05 worst-pin decades, +-2.5; +-3):')
for k in sorted(R):
    if k.startswith('g_'): continue
    a, b = R[k]['cpe_a07'], R[k]['cpe_a05']
    print(f"  {k:16s} {a['worst25']:.2f} / {b['worst25']:.2f}   (+-3: {a['worst30']:.2f} / {b['worst30']:.2f})  codes a07 {min(a['codes'])}-{max(a['codes'])}, a05 {min(b['codes'])}-{max(b['codes'])}")
json.dump({k: {n: {kk: (float(vv) if np.isscalar(vv) else vv) for kk, vv in v[n].items()} for n in v} for k, v in R.items()}, open(f'{HERE}/v1_results.json', 'w'), default=float)
