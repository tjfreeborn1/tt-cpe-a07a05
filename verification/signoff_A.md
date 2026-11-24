# Sign-off checks A1–A3 (2026-11-24)

All checks were run on the submitted GDS (`gds/tt_um_tjfreeborn1_cpe_a07a05.gds`, md5 `56774a0aaaf0854e4a37b15ef889f967`).
Scripts and raw results are in `sim/signoff/`.

## A1 Antenna check: PASS

- Magic `antennacheck` with the SKY130A extraction rules (partial-metal model, ratios as in `sky130A-extract.tech`),
  flattened over the whole design.
- **0 antenna violations.**
- One note: "Could not determine device boundary" on the `sky130_fd_sc_hd__diode_2` standard cell. This is a known
  device-recognition note on that cell, not a violation.
- Checker sanity test (`antenna_sanity.tcl`): a 300 µm met1 strip on a 0.42 × 0.15 µm gate is flagged (6 errors),
  which confirms the check is active.
- Why the design is safe:
  - The MOS-capacitor gates have about 100 µm² of gate area per unit, so their metal-to-gate ratios are very low.
  - The switch gates are driven by `buf_2` outputs, whose drain diffusion protects them.
  - The buffer inputs have `diode_2` cells.

## A2 Measurement conditions: PASS, with a required DC bias

Small-signal response of the extracted netlist at the typical corner and 27 °C. The trim code is re-chosen at each
bias; "worst" is the worst of the 12 pin models.

| DC bias (V) | α = 0.7: decades within ±2.5° (worst) | α = 0.5: decades within ±2.5° (worst) |
|---|---|---|
| 0.0 | 0.57 (0.30) | 0.68 (0.23) |
| 0.2 | 0.68 (0.40) | 0.82 (0.42) |
| 0.4 | 4.30 (0.77) | 2.30 (0.90) |
| 0.5 | 4.30 (4.23) | 2.32 (2.30) |
| 0.7 – 1.8 | 4.30 – 4.33 (≥ 4.28) | 2.30 – 2.33 (≥ 2.30) |

- **A DC bias of at least 0.5 V on the pin is required.** Above about 0.7 V the result is flat.
- The best trim code moves from 9 to 12 (α = 0.7) and from 12 to 15 (α = 0.5) between 0.7 and 1.8 V, all well
  inside 0–31.

Large-signal transient on the as-built netlist with the trim bank and a 100 Ω / 6.5 pF pin model. Each figure is the
change compared with a 10 mVrms signal at 1.0 V bias, at 2 kHz:

| Signal (mVrms) | Change in \|Z\| | Change in phase | Current THD |
|---|---|---|---|
| 50 | +0.01 % | 0.00° | 0.15 % |
| 100 | +0.05 % | 0.00° | 0.31 % |
| 200 | +0.24 % | +0.02° | 0.72 % |
| 300 | +0.65 % | +0.04° | 1.40 % |
| 500 | +2.7 % | +0.14° | 4.5 % |

- At 0.7 V bias, distortion roughly quadruples (100 mVrms: 1.5 % THD). At 1.2 V it is about half the 1.0 V figure.
- Off trim-bank nodes float. They start to clamp at about −0.2 V once the signal reaches about 300 mVrms, and they
  pump themselves up to a positive DC level. The effect on impedance is included in the figures above.
- Recommended measurement conditions: 1.0 V bias with 100 mVrms (50 mVrms at 0.7 V bias). Keep (bias − peak) above
  0.5 V and (bias + peak) at or below 1.8 V. `docs/info.md` is updated to match.

## A3 Leakage: PASS

- DC operating point, as-built netlists, corners tt / ff_ll / ff_hh / ss_hh, at 27, 85 and 125 °C:
  - Network leakage excluding the parallel resistor Rp: below 0.03 pA.
  - Trim-bank leakage: below 0.001 pA.
  - Current through Rp by design: 51–69 nA (α = 0.7) and 1.35–1.81 µA (α = 0.5).
- Extracted netlist, AC from 1 Hz, at 85 and 125 °C, across 8 process corners: the constant-phase band keeps its full
  width (α = 0.7: 4.30–4.35 decades; α = 0.5: 2.28–2.33 decades). Its edges move up about 12 % because of the
  resistor temperature coefficient.
- No leakage floor appears; the low edge of the band is set by Rp, as designed.
- The leakage of the Tiny Tapeout analog multiplexer and pad is outside this design. To de-embed it, do the
  analyzer's open compensation with the project deselected.
