# Measurement analysis

`analyze_e4990.py` processes the impedance sweeps of one pin (one file per trim code). It selects the trim code with
the widest constant phase band, reports that band at ±2.5° and ±3°, and fits α and Cα over it. The measurement
procedure that produces these files is given in the datasheet (`docs/info.md`, How to test).

| File | Purpose |
|---|---|
| `analyze_e4990.py` | The analysis script |
| `test_analyze_e4990.py` | Tests for the script (pytest) |
| `requirements-analysis.txt` | Python packages for the script and its tests |
| `example_data/cpe_a07/`, `example_data/cpe_a05/` | Synthetic sample sweeps (32 codes per pin) |
| `requirements.txt` | Tiny Tapeout template file for cocotb digital tests; not used by this analog project |

## Installation

Python 3.9 or newer, with NumPy (matplotlib only for `--plot`, pytest only for the tests):

```
pip install -r test/requirements-analysis.txt
```

## Exporting the data from the E4990A

1. Display two traces on the measurement channel, |Z| and θ (phase in degrees).
2. After each sweep, save both traces with **Save/Recall > Save Trace Data** as `codeNN.csv`, where NN is the trim
   code (`code00.csv` to `code31.csv`), with one folder per pin.

The script reads the E4990A file as saved: the `!` comment lines, title, and DC bias lines are skipped, and the |Z| and
θ columns are found from the header line (`Frequency(Hz), |Z|(Ohm)-data, theta-z(deg)-data, ...`) in any order, with
memory columns ignored. Files without a header are read as frequency (Hz), |Z| (Ω), and θ (degrees), in that order.
Comma, semicolon, tab, and space separators are accepted. A file saved with only one trace has an all-zero second data
column, and the script stops with an error rather than reading it as 0° phase. R and X data can be used instead with
`--rx`. Missing codes are skipped, so a partial set of sweeps can also be analyzed.

## Usage

```
python3 test/analyze_e4990.py <folder> --alpha 0.7 [--tol 2.5] [--rx] [--plot result.png]
```

| Option | Meaning |
|---|---|
| `<folder>` | Folder holding `code00.csv` to `code31.csv` for one pin |
| `--alpha` | Target order: 0.7 for `ua[0]`, 0.5 for `ua[1]` (required) |
| `--tol` | Phase tolerance in degrees for the band (default 2.5) |
| `--rx` | Files hold R and X instead of \|Z\| and θ |
| `--plot` | Save a plot of \|Z\| and phase for the selected code, with the band shaded |

Example, using the sample data for `ua[0]`:

```
$ python3 test/analyze_e4990.py test/example_data/cpe_a07 --alpha 0.7
codes measured: 32; best code 10
band within +-2.5 deg of -63.0 deg: 4.38 decades, 80.05 - 1.926e+06 Hz (+-3 deg: 4.41)
fit over the band: alpha = 0.7133, C_alpha = 1.627 nF*s^(-0.287); mean phase -63.70 deg, peak-to-peak 4.71 deg
band per code: 0:3.25 1:3.39 2:3.55 ... 31:0.63
```

- **best code:** the trim code with the widest ±2.5° band. Set this code for all later measurements of the chip.
- **band:** its width in decades, its edges in Hz, and the width at ±3°.
- **fit:** α and Cα from a straight-line fit of log |Z| against log ω over the band (Cα in nF·s^(α−1), using the
  fitted α), with the mean and peak-to-peak phase in the band.
- **band per code:** the ±2.5° band of every measured code, which shows how sharply the band depends on the code.
- **WARNING:** printed if the best code is 0 (too much uncompensated external capacitance) or 31 (less external
  capacitance than designed for, for example when the bus capacitance was compensated away). In either case the
  compensation should be checked before the result is used.

## Method

- The band is the widest continuous run of points from 20 Hz to 10 MHz where the phase is within ±tol of −90α°.
  Each edge is interpolated in log f between the last point inside and the first point outside the band; at the ends
  of the 20 Hz to 10 MHz window the band stops at the last measured point inside the window.
- The selected code is the one with the widest ±2.5° band. This is the calibration recommended in the datasheet.
- The fit is log10 |Z| = −log10(Cα) − α log10(ω) over the band of the selected code.

The `band()` function is the same algorithm used for the sign-off Monte Carlo analysis and the measurement rehearsal
(`sim/signoff/mc/mcan2.py`), and one of the tests checks that the two give identical results.

## Example data

The sample sweeps are synthetic E4990A data for a simulated chip, made with the measurement rehearsal model
(`sim/signoff/v2/rehearse.py`) with the demoboard pull-down lifted, 3 pF of board capacitance, the segment sweep, and
typical analyzer error. The short script that wrote these files was not kept, so they are provided as fixed sample
data rather than as a reproducible output. They are expected to give code 10 and 4.38 decades for `ua[0]`, and code 12 and 2.36 decades
for `ua[1]`.

## Tests

```
python3 -m pytest test/test_analyze_e4990.py -q
```

The 25 tests cover:

- the known results on both example datasets;
- recovery of α and Cα (to within 1e-9) from an ideal constant phase element;
- band edge interpolation and selection of the widest band;
- every accepted input layout: the E4990A export with comment, title, DC bias, header and memory columns; reordered
  columns; phase in radians; R and X; semicolon and tab separators; CRLF line endings; descending frequency; and the
  repeated point at a segment boundary;
- rejection of single-trace exports, files without data, and negative |Z|;
- the command-line interface, including the plot, missing codes, and an empty folder;
- agreement of `band()` with the sign-off implementation on 300 random phase curves.

All tests pass on Linux with Python 3.9 (NumPy 1.21, matplotlib 3.5) and Python 3.13 (NumPy 2.5, matplotlib 3.11).
The script uses only NumPy and the Python standard library, so no difference is expected on Windows or macOS, though
these have not been tested.

It is important to note that the script has not yet been run on a file saved by an actual E4990A. The export layout
used in the tests follows the example in the Keysight E4990A help ("Saving Trace Data to a File"). Therefore, the first
real sweep should be checked with `--plot` to confirm that the plotted |Z| and phase match the analyzer screen.
