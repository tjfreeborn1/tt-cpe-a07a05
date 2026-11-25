"""Tests for analyze_e4990.py. Run from the repository root:  python3 -m pytest test/test_analyze_e4990.py -q

Covers: known results on the example data, every accepted input layout (plain, E4990A Save Trace Data export with
header, reordered columns, memory columns, radians, R-X, semicolons, tabs, CRLF), rejection of bad files, recovery of
alpha and C_alpha from an ideal CPE, the band edge interpolation, the command-line interface, and agreement of band()
with the implementation used for the sign-off Monte Carlo and measurement rehearsal (sim/signoff/mc/mcan2.py).
"""
import os, subprocess, sys
import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_e4990 as A

EX = os.path.join(HERE, 'example_data')
SCRIPT = os.path.join(HERE, 'analyze_e4990.py')


def load_dir(d, rx=False):
    out = {}
    for fn in sorted(os.listdir(d)):
        if fn.startswith('code') and fn.endswith('.csv'):
            out[int(fn[4:-4])] = A.load(os.path.join(d, fn), rx)
    return out


def ideal(f, alpha, C):
    return 1.0 / ((2j * np.pi * f) ** alpha * C)


F = np.logspace(1, 7, 601)


# ---------- known results on the shipped example data ----------
@pytest.mark.parametrize('pin, alpha, code, dec, afit', [('cpe_a07', 0.7, 10, 4.38, 0.7133), ('cpe_a05', 0.5, 12, 2.36, 0.5002)])
def test_example_data(pin, alpha, code, dec, afit):
    r = A.analyze(load_dir(os.path.join(EX, pin)), alpha)
    assert r['code'] == code
    assert r['decades'] == pytest.approx(dec, abs=0.005)
    assert r['alpha_fit'] == pytest.approx(afit, abs=5e-4)
    assert r['warning'] == ''
    assert len(r['per_code']) == 32


def test_selected_code_is_widest_band():
    r = A.analyze(load_dir(os.path.join(EX, 'cpe_a07')), 0.7)
    assert r['decades'] == max(r['per_code'].values())


# ---------- ideal CPE: alpha and C_alpha are recovered ----------
@pytest.mark.parametrize('alpha, C', [(0.7, 1.66e-9), (0.5, 30.1e-9), (0.3, 5e-9)])
def test_ideal_cpe_recovered(alpha, C):
    r = A.analyze({7: (F, ideal(F, alpha, C))}, alpha)
    assert r['alpha_fit'] == pytest.approx(alpha, abs=1e-9)
    assert r['C_alpha'] == pytest.approx(C, rel=1e-9)
    f_in = F[(F >= 20) & (F <= 10e6)]                    # band is clipped to the measured points in 20 Hz - 10 MHz
    assert r['decades'] == pytest.approx(np.log10(f_in[-1] / f_in[0]), abs=1e-9)
    assert r['phase_pp'] == pytest.approx(0, abs=1e-9)


def test_band_edges_interpolated():
    f = np.logspace(2, 6, 401)
    err = np.where((f > 1e3) & (f < 1e5), 0.0, 5.0)
    dec, lo, hi = A.band(f, err, 2.5)
    # 0.01-decade grid; the edge is interpolated halfway between the last point out (err 5) and the first point in (err 0)
    assert np.log10(lo) == pytest.approx(3.005, abs=1e-9) and np.log10(hi) == pytest.approx(4.995, abs=1e-9)
    assert dec == pytest.approx(1.99, abs=1e-9)


def test_band_picks_widest_run():
    f = np.logspace(1, 7, 601)
    err = np.full_like(f, 5.0)
    err[(f > 1e2) & (f < 1e3)] = 0
    err[(f > 1e4) & (f < 1e6)] = 0
    dec, lo, hi = A.band(f, err, 2.5)
    assert lo > 9e3 and hi < 1.1e6 and dec == pytest.approx(2.0, abs=0.02)


def test_warning_at_code_limits():
    z = ideal(F, 0.7, 1e-9)
    bad = z * np.exp(1j * np.radians(10))
    assert 'bottom' in A.analyze({0: (F, z), 5: (F, bad)}, 0.7)['warning']
    assert 'top' in A.analyze({31: (F, z), 5: (F, bad)}, 0.7)['warning']


# ---------- input layouts ----------
def write(path, text, crlf=False):
    with open(path, 'w', newline='') as fh:
        fh.write(text.replace('\n', '\r\n') if crlf else text)
    return str(path)


def rows(f, c1, c2, sep=','):
    return ''.join(f'{a:+.11e}{sep} {b:+.11e}{sep} {c:+.11e}\n' for a, b, c in zip(f, c1, c2))


Z = ideal(F, 0.7, 1.66e-9)
MAG, TH = np.abs(Z), np.degrees(np.angle(Z))


def check(f, z):
    assert np.allclose(f, F) and np.allclose(z, Z, rtol=1e-9)


def test_plain_three_columns(tmp_path):
    check(*A.load(write(tmp_path / 'a.csv', rows(F, MAG, TH))))


def test_e4990a_export_with_header_and_memory(tmp_path):
    # layout of the E4990A "Save Trace Data" CSV (Keysight E4990A help, "Saving Trace Data to a File")
    hdr = ('!Agilent Technologies,E4990A,MY521012345,A.02.10\n!Date: Fri Apr 03 13:41:16 2015\nTitle label, TEST DATA\n'
           'DCV(V), +1.000e+000, DCI(A), +2.335e-009\n'
           'Frequency(Hz), |Z|(Ohm)-data, |Z|(Ohm)-mem, theta-z(deg)-data, theta-z(deg)-mem\n')
    body = ''.join(f'{a:+.11e}, {b:+.11e}, {b*2:+.11e}, {c:+.11e}, {c/2:+.11e}\n' for a, b, c in zip(F, MAG, TH))
    check(*A.load(write(tmp_path / 'a.csv', hdr + body)))


def test_reordered_columns(tmp_path):
    hdr = 'Frequency(Hz), theta-z(deg)-data, |Z|(Ohm)-data\n'
    check(*A.load(write(tmp_path / 'a.csv', hdr + rows(F, TH, MAG))))


def test_theta_in_radians(tmp_path):
    hdr = 'Frequency(Hz), |Z|(Ohm)-data, theta-z(rad)-data\n'
    check(*A.load(write(tmp_path / 'a.csv', hdr + rows(F, MAG, np.radians(TH)))))


def test_rx_layout(tmp_path):
    check(*A.load(write(tmp_path / 'a.csv', 'Frequency(Hz), R(Ohm)-data, X(Ohm)-data\n' + rows(F, Z.real, Z.imag)), rx=True))


@pytest.mark.parametrize('sep', [';', '\t'])
def test_other_separators(tmp_path, sep):
    check(*A.load(write(tmp_path / 'a.csv', 'Frequency(Hz)' + sep + '|Z|(Ohm)' + sep + 'theta(deg)\n' + rows(F, MAG, TH, sep))))


def test_crlf_and_descending_frequency(tmp_path):
    text = rows(F[::-1], MAG[::-1], TH[::-1])
    check(*A.load(write(tmp_path / 'a.csv', text, crlf=True)))


def test_segment_sweep_duplicate_point(tmp_path):
    f2 = np.sort(np.append(F, 1e4))     # segment boundary measured twice
    z2 = ideal(f2, 0.7, 1.66e-9)
    f, z = A.load(write(tmp_path / 'a.csv', rows(f2, np.abs(z2), np.degrees(np.angle(z2)))))
    r = A.analyze({3: (f, z)}, 0.7)
    assert r['alpha_fit'] == pytest.approx(0.7, abs=1e-9)


# ---------- rejected files ----------
def test_single_trace_export_rejected(tmp_path):
    # single-trace layout: 'Frequency, Formatted Data, Formatted Data' with zeros in the second data column
    text = '"# Channel 1"\n"# Trace 1"\nFrequency, Formatted Data [Ohm], Formatted Data\n' + rows(F, MAG, 0 * MAG)
    with pytest.raises(ValueError, match='phase column is all zero'):
        A.load(write(tmp_path / 'a.csv', text))


def test_no_numeric_rows_rejected(tmp_path):
    with pytest.raises(ValueError, match='no numeric rows'):
        A.load(write(tmp_path / 'a.csv', '! nothing here\nFrequency, |Z|, theta\n'))


def test_negative_magnitude_rejected(tmp_path):
    with pytest.raises(ValueError, match='zero or negative'):
        A.load(write(tmp_path / 'a.csv', rows(F, -MAG, TH)))


# ---------- command line ----------
def test_cli_end_to_end(tmp_path):
    png = tmp_path / 'out.png'
    out = subprocess.run([sys.executable, '-I', SCRIPT, os.path.join(EX, 'cpe_a07'), '--alpha', '0.7', '--plot', str(png)],
                         capture_output=True, text=True, check=True).stdout
    assert 'best code 10' in out and '4.38 decades' in out
    assert png.stat().st_size > 10_000


def test_cli_missing_codes(tmp_path):
    for c in (3, 17):
        write(tmp_path / f'code{c:02d}.csv', rows(F, MAG, TH))
    out = subprocess.run([sys.executable, '-I', SCRIPT, str(tmp_path), '--alpha', '0.7'], capture_output=True, text=True,
                         check=True).stdout
    assert 'codes measured: 2' in out


def test_cli_empty_dir(tmp_path):
    p = subprocess.run([sys.executable, '-I', SCRIPT, str(tmp_path), '--alpha', '0.7'], capture_output=True, text=True)
    assert p.returncode != 0 and 'no codeNN.csv' in p.stderr


# ---------- same band() as the sign-off Monte Carlo and the measurement rehearsal ----------
def test_band_matches_signoff_implementation():
    mc = os.path.join(HERE, '..', 'sim', 'signoff', 'mc')
    if not os.path.exists(os.path.join(mc, 'mcan2.py')): pytest.skip('sim/signoff not present')
    sys.path.insert(0, mc)
    import mcan2
    rng = np.random.default_rng(1)
    for _ in range(300):
        f = np.sort(10 ** rng.uniform(0.5, 7.5, rng.integers(50, 800)))
        err = np.abs(np.cumsum(rng.normal(0, 0.6, f.size)))
        tol = rng.choice([2.5, 3.0])
        assert A.band(f, err, tol) == mcan2.band(f, err, tol)
