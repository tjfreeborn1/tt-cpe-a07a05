"""Shared helpers for the sign-off scripts (added after the independent review).

- REPO / PDK paths: everything is read from this repository and PDK_ROOT. No paths outside the repo.
- run_ngspice(): runs ngspice in batch mode and raises on a non-zero exit or any error line in the log, so a failed
  run can never be silently replaced by stale data.
- fresh(): deletes output files before a run, for the same reason.
- bank_y(): converts a bank-bit impedance to admittance. Non-finite values are allowed only below FMIN_OK (where the
  bit effect is below numerical precision and outside every evaluated band); anywhere else they raise.
"""
import os, re, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
PDK_ROOT = os.environ.get('PDK_ROOT', '/home/claude/pdk/share/pdk')
PDK_NG = os.path.join(PDK_ROOT, 'sky130A', 'libs.tech', 'ngspice')
LIB = os.path.join(PDK_NG, 'sky130.lib.spice')
GDS = os.path.join(REPO, 'gds', 'tt_um_tjfreeborn1_cpe_a07a05.gds')
PEX = os.path.join(REPO, 'sim', 'pex', 'top_pex.spice')            # flat-output C + coupling extraction
ASBUILT = os.path.join(REPO, 'sim', 'netlists')                   # schematic-level as-built netlists
FMIN_OK = 20.0
_BAD = re.compile(r'\berror\b|abort|fail|singular|timestep too small|no convergence', re.I)


def fresh(*paths):
    for p in paths:
        if os.path.exists(p):
            os.remove(p)


def run_ngspice(spfile, cwd=None):
    r = subprocess.run(['ngspice', '-b', spfile], capture_output=True, text=True, cwd=cwd)
    log = r.stdout + r.stderr
    bad = [l for l in log.splitlines() if _BAD.search(l) and not l.lower().lstrip().startswith('warning')]
    if r.returncode != 0 or bad:
        raise RuntimeError(f'ngspice failed on {spfile} (rc={r.returncode}):\n' + '\n'.join(bad[:20]) + '\n' + log[-2000:])
    return r.stdout


def bank_y(z, f):
    y = 1 / np.asarray(z)
    badm = ~np.isfinite(y)
    if np.any(badm & (np.asarray(f) >= FMIN_OK)):
        raise ValueError('non-finite bank admittance inside the evaluated frequency range')
    return np.where(badm, 0.0, y)
