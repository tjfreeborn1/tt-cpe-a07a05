"""V2: measurement rehearsal. Synthetic E4990A data from Monte Carlo chips is fed through the planned calibration.

Chip: revised Monte Carlo samples (../mc/out2_tt), extracted netlist, mismatch + global variation.

Path, from the chip pin outward (TT data and the ETR demoboard v3 schematic):
- TT analog switch tt_asw_3v3: Ron 60 ohm (35-104 ohm extracted from its layout, all corners).
- Analog bus + pad: 4 pF (TT spec < 5 pF); switch off-state difference about 0.1 pF.
- Breakout + demoboard: about 6 pF of trace/header capacitance, plus the 10 Mohm pull-down to ground on every
  analog pin.

Target ("truth"): the element as designed, referenced to the pad, i.e. chip + switch Ron + on-chip bus/pad C.
The design was co-optimized with this capacitance (the 4-9 pF pin-model range), so it belongs to the CPE.

Compensation choices (open/short):
- 'deselect': open at the header with the project deselected (switch off). This subtracts board C, the 10 Mohm
  pull-down AND the on-chip bus/pad C (residual: 0.1 pF on/off difference). It removes part of the designed Cp.
- 'carrier': open/short at the demoboard analog header with the ASIC carrier removed. This subtracts the
  demoboard part (6 pF assumed here, plus the 10 Mohm); the carrier trace and pad stay, as intended.
- 'fixture': open/short at the fixture tip only; board C and the 10 Mohm remain.
- 'lifted': the fixture-only case with the 10 Mohm pull-down removed from the two used pins.

Analyzer error (Keysight E4990A data-sheet accuracy equation, 4-terminal-pair port, 1 m cable, measurement-time
mode 5, from e4990_acc.py):
- A systematic residual delta_phi(f) = k * E(f)/100 rad * s(f) and delta_|Z|/|Z| = k * E(f)/100 * s2(f), where s
  and s2 are smooth random functions of log f with |s| <= 1. The draw is fixed for a measurement session (all 32
  codes share it).
- Plus per-sweep random noise of 0.05 * E. k = 1 (the guaranteed bound) or 1/3 (typical).

Oscillator plans:
- 'flat100': 100 mVrms everywhere.
- 'seg': 300 mVrms below 10 kHz and 100 mVrms above (E4990A segment sweep).

Calibration as in the datasheet: sweep codes 0-31 and pick the widest +-2.5 deg band in the measured data.
"""
import numpy as np, glob, os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'mc')); from mcan2 import band
from e4990_acc import acc

RON, CBUS, CBOARD, RPD, DCOFF = 60.0, 4e-12, 6e-12, 10e6, 0.1e-12
NETS = (('cpe_a07', 0.7, 'A'), ('cpe_a05', 0.5, 'B'))
rng = np.random.default_rng(20261125)

def smooth(lf, rng):
    a = rng.uniform(-1, 1, 3); b = rng.uniform(0.15, 0.8, 3); c = rng.uniform(0, 2 * np.pi, 3)
    s = sum(a[j] * np.sin(2 * np.pi * b[j] * lf + c[j]) for j in range(3))
    return s / max(1e-9, np.max(np.abs(s)))

def session(f, Ztrue_codes, a, comp, osc, k, rng):
    s = 2j * np.pi * f; lf = np.log10(f)
    vmv = np.where(f < 1e4, 300.0, 100.0) if osc == 'seg' else np.full_like(f, 100.0)
    sp, sm = smooth(lf, rng), smooth(lf, rng)
    res = []
    for Zc in Ztrue_codes:
        Zs = RON + Zc                                    # chip + switch
        Zpad = 1 / (1 / Zs + s * CBUS)                   # target: pad-referenced element
        if comp == 'deselect':
            Zport = 1 / (1 / Zs + s * DCOFF)
        elif comp == 'carrier':
            Zport = Zpad
        else:
            Ypar = s * CBOARD + (1 / RPD if comp == 'fixture' else 0)
            Zport = 1 / (1 / Zpad + Ypar)
        E = np.array([acc(fm, abs(z), v, 5, 1) for fm, z, v in zip(f, Zport, vmv)]) / 100   # fraction
        ph = k * E * sp + 0.05 * E * rng.standard_normal(len(f))
        mg = k * E * sm + 0.05 * E * rng.standard_normal(len(f))
        res.append(Zport * (1 + mg) * np.exp(1j * ph))
    return res

def bands(f, Zs, a, tol=2.5):
    return [band(f, np.abs(np.degrees(np.angle(z)) + 90 * a), tol) for z in Zs]

if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(HERE, '..', 'mc', 'out2_tt', 's*.npz')))[:int(sys.argv[1]) if len(sys.argv) > 1 else 100]
    cases = [(comp, osc, k) for comp in ('deselect', 'carrier', 'fixture', 'lifted') for osc in ('flat100', 'seg') for k in (1 / 3, 1.0)]
    out = {f'{c}|{o}|{k:.2f}|{n}': [] for c, o, k in cases for n, _, _ in NETS}
    for fn in files:
        d = np.load(fn); f = d['f']; m = f <= 10e6; f = f[m]
        for net, a, t in NETS:
            Y0 = 1 / d[f'z{t}'][m]; yb = [d[f'y{t}{i}'][m] for i in range(5)]
            Zc = [1 / (Y0 + sum(yb[i] for i in range(5) if c >> i & 1)) for c in range(32)]
            s_ = 2j * np.pi * f
            true = bands(f, [1 / (1 / (RON + z) + s_ * CBUS) for z in Zc], a); cbest = int(np.argmax([b[0] for b in true]))
            for comp, osc, k in cases:
                Zm = session(f, Zc, a, comp, osc, k, rng); mb = bands(f, Zm, a); cm = int(np.argmax([b[0] for b in mb]))
                out[f'{comp}|{osc}|{k:.2f}|{net}'].append(dict(true_best=true[cbest][0], code_true=cbest, code_meas=cm,
                    meas_band=mb[cm][0], meas_lo=mb[cm][1], meas_hi=mb[cm][2], true_at_meas_code=true[cm][0]))
        print(os.path.basename(fn), flush=True)
    json.dump(out, open(os.path.join(HERE, 'rehearsal.json'), 'w'), default=float)
    print('\ncomp      osc      err  net      | true band (chip, best code) | measured band median/p5/min | low edge median | code right / within 1 | true band at measured code (min)')
    for key, R in out.items():
        comp, osc, k, net = key.split('|')
        tb = np.array([r['true_best'] for r in R]); mb = np.array([r['meas_band'] for r in R]); lo = np.array([r['meas_lo'] for r in R])
        ok = np.mean([r['code_meas'] == r['code_true'] for r in R]); ok1 = np.mean([abs(r['code_meas'] - r['code_true']) <= 1 for r in R])
        tm = np.array([r['true_at_meas_code'] for r in R])
        print(f"{comp:9s} {osc:8s} {'spec' if float(k) > 0.5 else 'typ ':4s} {net} | {np.median(tb):.2f} | {np.median(mb):.2f} / {np.percentile(mb,5):.2f} / {mb.min():.2f} | {np.median(lo):8.0f} Hz | {100*ok:5.1f}% / {100*ok1:5.1f}% | {np.median(tm):.2f} ({tm.min():.2f})")
