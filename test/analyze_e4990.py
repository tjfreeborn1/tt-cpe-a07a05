#!/usr/bin/env python3
"""Analyze E4990A sweeps of the CPE chip: choose the trim code, report the constant-phase band, fit alpha and C_alpha.

Input: a directory with one CSV per trim code, named code00.csv ... code31.csv (missing codes are skipped).
Accepted CSV layouts (header lines starting with '!', '#' or text are skipped; comma, semicolon or tab separated):
  freq_Hz, |Z|_ohm, theta_deg        (default; E4990A "|Z|-theta" trace export)
  freq_Hz, R_ohm, X_ohm              (use --rx)

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


def load(fn, rx=False):
    rows = []
    for line in open(fn, encoding='utf-8', errors='replace'):
        parts = [p for p in re.split(r'[,;\t ]+', line.strip()) if p]
        try:
            vals = [float(p) for p in parts[:3]]
        except ValueError:
            continue
        if len(vals) == 3: rows.append(vals)
    a = np.array(rows)
    if a.size == 0: raise ValueError(f'no numeric rows in {fn}')
    a = a[np.argsort(a[:, 0])]
    f = a[:, 0]
    z = a[:, 1] + 1j * a[:, 2] if rx else a[:, 1] * np.exp(1j * np.radians(a[:, 2]))
    if not np.all(np.isfinite(z)): raise ValueError(f'non-finite data in {fn}')
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
