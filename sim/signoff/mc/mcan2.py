"""Analysis for mcsim2.py output (revision 2, after the independent review).

- Band edges are interpolated in log f; a band is the widest contiguous run inside 20 Hz - 10 MHz.
- Each of the 12 pin models (series Rs, then Ce to ground on the analyzer side) is evaluated with its own best code
  (0-31). This "widest band" calibration is the one the datasheet recommends.
- Results are reported at +-2.5 and +-3.0 degrees, with empirical percentiles; mean - 3 sigma is also given, but the
  alpha = 0.5 distribution can be bimodal.
- Any non-finite value raises an error.
"""
import numpy as np, glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PINS = [(Rs, Ce) for Rs in (35, 100, 300, 500) for Ce in (4e-12, 6.5e-12, 9e-12)]
NETS = (('cpe_a07', 0.7, 'A'), ('cpe_a05', 0.5, 'B'))

def band(f, err, tol, fmin=20.0, fmax=10e6):
    lf = np.log10(f); ok = (err <= tol) & (f >= fmin) & (f <= fmax)
    best = (0.0, None, None); i = 0; n = len(f)
    while i < n:
        if not ok[i]: i += 1; continue
        j = i
        while j + 1 < n and ok[j + 1]: j += 1
        def edge(a, b):                       # a inside, b outside: interpolate err = tol
            if b < 0 or b >= n or f[b] < fmin or f[b] > fmax: return lf[a]
            ea, eb = err[a], err[b]
            t = (tol - ea) / (eb - ea) if eb != ea else 0.0
            return lf[a] + t * (lf[b] - lf[a])
        lo = edge(i, i - 1); hi = edge(j, j + 1)
        if hi - lo > best[0]: best = (hi - lo, 10 ** lo, 10 ** hi)
        i = j + 1
    return best

def analyze(fn):
    d = np.load(fn); f = d['f']; s = 2j * np.pi * f; res = {}
    for net, a, t in NETS:
        Y0 = 1 / d[f'z{t}']; yb = [d[f'y{t}{i}'] for i in range(5)]
        assert np.all(np.isfinite(Y0)) and all(np.all(np.isfinite(y)) for y in yb), fn
        Yc = [Y0 + sum(yb[i] for i in range(5) if c >> i & 1) for c in range(32)]
        r = {}
        for tol in (2.5, 3.0):
            per = []
            for Rs, Ce in PINS:
                errs = [np.abs(np.degrees(np.angle(1 / (s * Ce + 1 / (Rs + 1 / y))))+ 90 * a) for y in Yc]
                bs = [band(f, e, tol) for e in errs]; c = int(np.argmax([b[0] for b in bs]))
                per.append(dict(dec=bs[c][0], lo=bs[c][1], hi=bs[c][2], code=c, Rs=Rs, Ce=Ce))
            r[tol] = per
        nom = [p for p in r[2.5] if p['Rs'] == 100 and p['Ce'] == 6.5e-12][0]
        z = 1 / (s * 6.5e-12 + 1 / (100 + 1 / Yc[nom['code']])); sel = (f >= nom['lo']) & (f <= nom['hi'])
        p = np.polyfit(np.log10(2 * np.pi * f[sel]), np.log10(np.abs(z[sel])), 1)
        res[net] = dict(nom25=nom['dec'], worst25=min(q['dec'] for q in r[2.5]), worst30=min(q['dec'] for q in r[3.0]),
                        nom30=[q for q in r[3.0] if q['Rs'] == 100 and q['Ce'] == 6.5e-12][0]['dec'],
                        codes=[q['code'] for q in r[2.5]], lo=nom['lo'], hi=nom['hi'], alpha=-p[0], Ca=10 ** (-p[1]),
                        worst_pin=[(q['Rs'], q['Ce']) for q in r[2.5] if q['dec'] == min(x['dec'] for x in r[2.5])][0])
    return res

if __name__ == '__main__':
    allres = {}
    for MOS in ('tt', 'ss', 'ff', 'sf', 'fs'):
        fs = sorted(glob.glob(f'{HERE}/out2_{MOS}/s*.npz'))
        fails = sorted(glob.glob(f'{HERE}/out2_{MOS}/FAIL_*'))
        if not fs: continue
        R = [analyze(fn) for fn in fs]; allres[MOS] = R
        print(f'{MOS}: {len(R)} samples, {len(fails)} failed runs')
        for net, a, t in NETS:
            for key in ('nom25', 'worst25', 'worst30'):
                x = np.array([r[net][key] for r in R])
                print(f'  {net} {key:8s}: mean {x.mean():.3f} sd {x.std():.3f} | min {x.min():.3f} | p1 {np.percentile(x,1):.3f} p5 {np.percentile(x,5):.3f} | mean-3sd {x.mean()-3*x.std():.3f}')
            al = np.array([r[net]['alpha'] for r in R]); ca = np.array([r[net]['Ca'] for r in R])
            cod = np.array([c for r in R for c in r[net]['codes']])
            print(f'  {net} alpha {al.mean():.4f} +- {al.std():.4f}; Ca {ca.mean()*1e9:.3f} +- {100*ca.std()/ca.mean():.2f} %; codes {cod.min()}-{cod.max()}')
    json.dump({m: [{n: {k: (float(v) if np.isscalar(v) else v) for k, v in r[n].items()} for n in r} for r in R] for m, R in allres.items()},
              open(f'{HERE}/mc2_results.json', 'w'), default=float)
