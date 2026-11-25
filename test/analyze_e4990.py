#!/usr/bin/env python3
"""Analyze E4990A sweeps of the CPE chip: choose the trim code, report the constant-phase band, fit alpha and C_alpha.

Input: a directory with one CSV per trim code, named code00.csv ... code31.csv (missing codes are skipped).
Accepted CSV layouts (comment lines starting with '!' or '#' and other text lines are skipped; comma, semicolon,
tab or space separated):
  E4990A Save Trace Data export with |Z| and theta traces: columns are found by the header line
    'Frequency(Hz), |Z|(Ohm)-data, theta-z(deg)-data, ...' in any order; memory columns are ignored; theta in rad is
    converted if the header says so.
  freq_Hz, |Z|_ohm, theta_deg        (no header: columns taken in this order)
  freq_Hz, R_ohm, X_ohm              (use --rx)
A file whose phase column is all zero (a single-trace export) is rejected with an error.

Method (as in docs/info.md):
- The band is the widest contiguous run between 20 Hz and 10 MHz where the phase stays within +-tol of -90*alpha
  degrees. Edges are interpolated in log f.
- The chosen code is the one with the widest band (+-2.5 deg). The +-3 deg band is reported too.
- Sanity checks: if the chosen code is 0, too much external (fixture/board) capacitance is still uncompensated; if it
  is 31, too little. In either case revisit the compensation.
- Fit: log10|Z| = -log10(C_alpha) - alpha*log10(omega) over the chosen band (C_alpha in F*s^(alpha-1)).

Usage: python3 analyze_e4990.py DIR --alpha 0.7 [--tol 2.5] [--rx] [--plot out.png]
"""
import argparse, glob, os, re, sys
import numpy as np


def _split(line):
    parts = [p.strip().strip('"') for p in re.split(r'[,;\t]', line)]
    parts = [p for p in parts if p]
    return parts if len(parts) > 1 else line.split()


def _find(names, pred):
    for i, n in enumerate(names):
        if pred(n) and 'mem' not in n: return i
    return None


def load(fn, rx=False):
    """Read one sweep. Columns are found by the header line if there is one (the E4990A writes
    'Frequency(Hz), |Z|(Ohm)-data, theta-z(deg)-data, ...'); memory columns are ignored. Without a usable header the
    columns are taken in order: frequency, |Z|, theta (or frequency, R, X with rx=True)."""
    names, rows = None, []
    for line in open(fn, encoding='utf-8', errors='replace'):
        s = line.strip()
        if not s or s[0] in '!#': continue
        parts = _split(s)
        try:
            vals = [float(p) for p in parts]
        except ValueError:
            if parts and parts[0].lower().startswith('freq'): names = [p.lower() for p in parts]
            continue
        if len(vals) >= 3: rows.append(vals)
    if not rows: raise ValueError(f'no numeric rows in {fn}')
    ncol = min(len(r) for r in rows)
    a = np.array([r[:ncol] for r in rows])
    i1, i2, rad = 1, 2, False
    if names:
        if rx:
            j1, j2 = _find(names, lambda n: n.startswith('r')), _find(names, lambda n: n.startswith('x'))
        else:
            j1 = _find(names, lambda n: '|z|' in n or n.startswith('z'))
            j2 = _find(names, lambda n: 'theta' in n or 'θ' in n or 'phase' in n)
        if j1 is not None and j2 is not None:
            if max(j1, j2) >= ncol: raise ValueError(f'{fn}: header names more columns than the data rows hold')
            i1, i2 = j1, j2
            rad = not rx and 'rad' in names[j2]
    a = a[np.argsort(a[:, 0], kind='stable')]
    f, c1, c2 = a[:, 0], a[:, i1], a[:, i2]
    if rx:
        z = c1 + 1j * c2
    else:
        if np.all(c2 == 0):
            raise ValueError(f'{fn}: the phase column is all zero. The file probably holds a single trace; save both '
                             'the |Z| and theta traces (Save/Recall > Save Trace Data with both traces displayed).')
        if np.any(c1 <= 0): raise ValueError(f'{fn}: |Z| column has zero or negative values; is it really |Z|?')
        z = c1 * np.exp(1j * (c2 if rad else np.radians(c2)))
    if not np.all(np.isfinite(z)) or not np.all(f > 0): raise ValueError(f'non-finite data or non-positive frequency in {fn}')
    return f, z


def band(f, err, tol, fmin=20.0, fmax=10e6):
    lf = np.log10(f); ok = (err <= tol) & (f >= fmin) & (f <= fmax)
    best = (0.0, None, None); i = 0; n = len(f)
    while i < n:
        if not ok[i]: i += 1; continue
        j = i
        while j + 1 < n and ok[j + 1]: j += 1
        def edge(a, b):
            if b < 0 or b >= n or f[b] < fmin or f[b] > fmax: return lf[a]
            ea, eb = err[a], err[b]; t = (tol - ea) / (eb - ea) if eb != ea else 0.0
            return lf[a] + t * (lf[b] - lf[a])
        lo, hi = edge(i, i - 1), edge(j, j + 1)
        if hi - lo > best[0]: best = (hi - lo, 10 ** lo, 10 ** hi)
        i = j + 1
    return best


def analyze(data, alpha, tol=2.5):
    res = {}
    for code, (f, z) in sorted(data.items()):
        err = np.abs(np.degrees(np.angle(z)) + 90 * alpha)
        res[code] = dict(b=band(f, err, tol), b3=band(f, err, 3.0))
    code = max(res, key=lambda c: res[c]['b'][0])
    f, z = data[code]; dec, lo, hi = res[code]['b']
    sel = (f >= lo) & (f <= hi)
    p = np.polyfit(np.log10(2 * np.pi * f[sel]), np.log10(np.abs(z[sel])), 1)
    ph = np.degrees(np.angle(z[sel]))
    return dict(code=code, decades=dec, f_lo=lo, f_hi=hi, decades_3deg=res[code]['b3'][0], alpha_fit=-p[0], C_alpha=10 ** (-p[1]),
                phase_mean=ph.mean(), phase_pp=ph.max() - ph.min(), per_code={c: r['b'][0] for c, r in res.items()},
                warning=('best code at the bottom of the range: too much uncompensated external capacitance' if code == 0 else
                         'best code at the top of the range: external capacitance lower than designed for' if code == 31 else ''))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('dir'); ap.add_argument('--alpha', type=float, required=True)
    ap.add_argument('--tol', type=float, default=2.5); ap.add_argument('--rx', action='store_true'); ap.add_argument('--plot')
    a = ap.parse_args()
    data = {}
    for fn in sorted(glob.glob(os.path.join(a.dir, 'code*.csv'))):
        m = re.search(r'code(\d+)', os.path.basename(fn))
        if m: data[int(m.group(1))] = load(fn, a.rx)
    if not data: sys.exit('no codeNN.csv files found')
    r = analyze(data, a.alpha, a.tol)
    print(f"codes measured: {len(data)}; best code {r['code']}")
    print(f"band within +-{a.tol} deg of {-90*a.alpha:.1f} deg: {r['decades']:.2f} decades, {r['f_lo']:.4g} - {r['f_hi']:.4g} Hz (+-3 deg: {r['decades_3deg']:.2f})")
    print(f"fit over the band: alpha = {r['alpha_fit']:.4f}, C_alpha = {r['C_alpha']*1e9:.4g} nF*s^({r['alpha_fit']-1:.3f}); mean phase {r['phase_mean']:.2f} deg, peak-to-peak {r['phase_pp']:.2f} deg")
    if r['warning']: print('WARNING:', r['warning'])
    print('band per code:', ' '.join(f"{c}:{d:.2f}" for c, d in sorted(r['per_code'].items())))
    if a.plot:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        f, z = data[r['code']]; fig, ax = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
        ax[0].loglog(f, np.abs(z)); ax[0].set_ylabel('|Z| (ohm)')
        ax[1].semilogx(f, np.degrees(np.angle(z))); ax[1].axhline(-90 * a.alpha, color='k', lw=0.8)
        for s_ in (-1, 1): ax[1].axhline(-90 * a.alpha + s_ * a.tol, color='k', lw=0.6, ls='--')
        ax[1].axvspan(r['f_lo'], r['f_hi'], alpha=0.1); ax[1].set_ylabel('phase (deg)'); ax[1].set_xlabel('frequency (Hz)')
        ax[0].set_title(f"alpha target {a.alpha}: code {r['code']}, {r['decades']:.2f} decades"); fig.tight_layout(); fig.savefig(a.plot, dpi=130)


if __name__ == '__main__':
    main()
