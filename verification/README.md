# Verification of layout v1 (2026-11-24)

| Check | Tool | Result |
|---|---|---|
| Tiny Tapeout precheck (all 17 checks) | `tt-support-tools/precheck` run locally | Pass — see `precheck_results.md` |
| DRC, full rule deck | Magic `drc(full)` (inside the precheck), KLayout FEOL / BEOL / offgrid | 0 errors at the top level |
| LVS | Netgen vs `netlist/lvs` (Xschem) | Circuits match uniquely, no property errors — `lvs_netgen.out` |
| Post-layout simulation | Magic C + coupling extraction (`sim/pex`), 69 corner/bias/temperature runs × 12 pin models | see below |

Post-layout results (828 cases each, phase within ±2.5° of the target, best trim code per case):

| | α = 0.7 on `ua[0]` | α = 0.5 on `ua[1]` |
|---|---|---|
| Common band | 4.12 decades, 126 Hz – 1.68 MHz | 2.12 decades, 1.88 – 251 kHz |
| Pre-layout (v4b as drawn) | 4.15 decades | 2.12 decades |
| Top-window calibration (superseded: not recommended, see signoff_B) | 4.10 decades (window 150 – 600 kHz) | 2.10 decades (window 50 – 200 kHz) |
| Fitted α at 0.7 / 1.0 / 1.5 V | 0.713 / 0.713 / 0.712 | 0.501 / 0.498 / 0.498 |
| Cα at 0.7 / 1.0 / 1.5 V, fitted over the common band above | 1.59 / 1.67 / 1.71 nF·s^-0.3 | 29.0 / 30.9 / 31.5 nF·s^-0.5 |

Parasitic capacitance on the pin nets (excluding the bank capacitors themselves): 37 fF to ground and 15 fF to the
largest branch node; a further ~0.54 pF couples the pin's bank top plate to the bank bottom plates, which simply adds
about 5–11 % to each bank bit.

Note on simulation: with the buffers included, ngspice needs `.option rshunt=1e12` to find the operating point;
without it the transient-op fallback leaves the large capacitor nodes at the wrong bias and the results are wrong.

Cα depends on the fit window. `docs/info.md` quotes Cα fitted over each chip's own ±2.5° band, with the nominal
100 Ω / 6.5 pF pin model: 1.66 nF·s^-0.3 and about 30.0 nF·s^-0.5. The table above uses the band common to all 828
cases, which gives about 3 % more for α = 0.5. The units follow the fitted α (0.713, about 0.500). Forcing α to
exactly 0.7 raises Cα by about 16 %.

Note on post-layout transients: a hierarchical-output Magic extraction (`ext2spice hierarchy on`) contains about 55
small negative capacitors (−0.07 to −0.26 fF) from the parent/child coupling adjustment. These make long ngspice
transients diverge. Use the flat-output netlist (`sim/pex/top_pex.spice`, which has none) or remove them. AC results
are unaffected.

## Sign-off record

- `signoff_A.md`: antenna, measurement conditions, leakage.
- `signoff_B.md`: RC extraction, corners on the RC netlist, Monte Carlo, trim coverage.
- `signoff_C.md`: control path, coupling, reliability.
- `signoff_D.md`: independent review and the resulting fixes.
- `signoff_D12.md`: the CI build artifact matches the verified GDS; physical checks re-run on the committed file.
- `signoff_V.md`: extra validation (model-error envelope, TT switch and board, model physics, measurement rehearsal).

The scripts behind these results, the tool versions used, and how to rerun them are described in `sim/README.md`.
