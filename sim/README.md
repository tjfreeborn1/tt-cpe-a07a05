# Simulation and sign-off scripts

These scripts produced the design, the post-layout results, and the sign-off records in `verification/`. They are
provided so the results can be inspected and rerun. The measurement analysis script for silicon is separate and is
described in `test/README.md`.

## Tools used

| Tool | Version used |
|---|---|
| SKY130 PDK (`sky130A`, built with open_pdks) | open_pdks commit `2fdf40d` (2026-11-20) |
| ngspice | 42 (with KLU) |
| Magic | 8.3.706 |
| Netgen | 1.5.332 |
| Xschem | 3.4.8RC |
| Python | 3.13, with NumPy 1.26 (most scripts need only NumPy) |
| Tiny Tapeout tools (precheck, datasheet) | tt-support-tools commit `21568ef` |

Other versions are expected to work, though results may differ slightly with a different PDK or ngspice version.

## Setup

1. Install the tools above and build the `sky130A` PDK.
2. Set `PDK_ROOT` to the folder that contains `sky130A`, for example `export PDK_ROOT=/usr/local/share/pdk`. The
   scripts find the ngspice models at `$PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice`. If `PDK_ROOT` is not
   set they fall back to the path on the original build machine, which will not exist elsewhere.
3. Run each script from its own folder (several read neighbouring files by relative path), for example
   `cd sim/signoff/mc && python3 mcsim2.py 0 2 tt`.

All sign-off scripts use `sim/signoff/common.py`, whose `run_ngspice()` runs ngspice in batch mode and raises an
error on a non-zero exit code or on any error line in the ngspice log, so a failed simulation cannot silently produce
results.

## Folder map

| Folder | Contents | Record |
|---|---|---|
| `sim/` | Pre-layout design: element construction (`build_L.py`), network simulation (`csim.py`), corner analysis (`vanalyze.py`), netlists, and the as-drawn results | |
| `sim/tb/` | Top-level testbench (`run.py`) for the schematic netlist | |
| `sim/pex/` | Magic extraction (`pex.tcl`), the 828-case post-layout corner analysis (`pexsim.py`, `pexanalyze.py`), and the extracted netlist `top_pex.spice` | `verification/README.md` |
| `sim/signoff/` | Bias and temperature corners (`pexbias.py`, `biasan.py`, `pexhot.py`, `hotan.py`), leakage (`leak.py`), large-signal distortion (`lsim.py`), antenna checks (`antenna_check.tcl`, `antenna_sanity.tcl`) | `signoff_A.md`, `signoff_C.md` |
| `sim/signoff/rc/` | Full RC extraction (`rcx_hier.tcl`, netlist `top_rc.spice.gz`), corners on the RC netlist (`pexrc.py`, `pexrc2.py`, `rccmp.py`, `rc2cmp.py`), trim coverage (`trimcov.py`) | `signoff_B.md` |
| `sim/signoff/mc/` | Monte Carlo (`mcsim2.py`, `run2.sh`) and its analysis (`mcan2.py`) | `signoff_D.md` |
| `sim/signoff/c/` | Pin-to-pin coupling and crosstalk (`coup.py`) | `signoff_C.md` |
| `sim/signoff/v1/` | Model-error envelope (`v1sim.py`, `v1b.py`, `v1an.py`) and MOS channel resistance (`nqs.py`) | `signoff_V.md` |
| `sim/signoff/v2/` | Measurement rehearsal (`rehearse.py`), E4990A accuracy model (`e4990_acc.py`), TT analog switch characterization (`asw_char.py`, `asw_extract.tcl`) | `signoff_V.md` |
| `sim/signoff/data/` | Stored simulation results (`.npz`) read by the analysis scripts | |
| `verification/d12/` | Final checks on the CI-built GDS: flattened DRC, antenna, LVS, GDS/OASIS comparison | `signoff_D12.md` |

## Reproducing the main results

| Result | Command (from the script's folder) | Run time (one core) |
|---|---|---|
| Monte Carlo, 500 chips | `bash run2.sh`, then `python3 mcan2.py` | approximately 17 s per chip, so approximately 1.2 h on the two parallel lanes in `run2.sh` |
| Measurement rehearsal | `python3 rehearse.py [N]` (needs the Monte Carlo outputs `mc/out2_tt/`; uses the analyzer accuracy model in `e4990_acc.py`) | not timed |
| Model-error envelope | `python3 v1sim.py PART NPARTS`, then `python3 v1an.py` | not timed |

Note that the Monte Carlo outputs (`mc/out2_*/`, one file per chip) are not stored in the repository because of their
size. The summary results are stored (`mc/mc2_results.json`, `mc/mcan2_all.txt`), and `rehearse.py` and `mcan2.py`
need the per-chip outputs to be regenerated first with `run2.sh`.

## Files that need editing before use

- `verification/d12/drc_flat.tcl` and `verification/d12/extract_antenna.tcl` read the GDS from a fixed path on the
  original build machine; change the `gds read` line to point at `gds/tt_um_tjfreeborn1_cpe_a07a05.gds`.
- `sim/signoff/v2/asw_extract.tcl` reads the TT analog switch layout from a local clone of the
  [tt-multiplexer](https://github.com/TinyTapeout/tt-multiplexer) repository; change the `gds read` line to that clone.

## Superseded scripts

These are kept as a record of the review and should not be used:

- `mc/mcsim.py`, `mc/mcan.py`, `mc/wintest.py`: the first Monte Carlo, replaced by `mcsim2.py` and `mcan2.py` after the
  independent review (see `signoff_D.md` for the reasons).
- `pex/pexwindow.py` and `windowcal.py`: the top-of-band calibration shortcut, which the datasheet does not
  recommend.

## What is not included

- The model-physics hand checks in V4 (model bin, oxide capacitance, and channel-resistance corner frequencies) were
  short calculations run outside the repository; their results are recorded in `verification/signoff_V.md`, and the
  simulation part of V4 is `v1/nqs.py`.
- The script that wrote the sample data in `test/example_data/` was not kept (see `test/README.md`).

## How these scripts were tested

- **By use:** each script produced the results recorded in `verification/`. During sign-off, settings that the
  models could silently ignore were checked on a single device before use (for example, the resistor variation
  parameter, and the `mult=` and `m=` instance parameters), and the DRC and antenna checks were run with a deliberate
  error first (positive controls) to confirm that they detect one.
- **Independent review (D11):** a separate reviewer regenerated the key results blind, with its own code and without
  access to these scripts or reports, so agreement between the two is an independent check of the scripts. The
  differences it found (for example the reused Monte Carlo seeds in `mcsim.py`) are listed in
  `verification/signoff_D.md` and were fixed before the datasheet results were produced.
- **Fresh-clone rerun:** on 2026-11-25 the repository was cloned into an empty folder, all 46 Python scripts were
  compiled, and two Monte Carlo chips were rerun with `mcsim2.py 0 2 tt`. Both outputs were identical to the stored
  sign-off outputs for the same seeds (zero difference in all 17 saved quantities).
- **Not tested:** the remaining scripts have not been rerun from a fresh clone, and none have been run on a machine
  other than the original build machine. There are no automated tests for the simulation scripts; the automated tests
  are for the measurement analysis script (`test/test_analyze_e4990.py`).
