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
| Top-window calibration | 4.10 decades (window 150 – 600 kHz) | 2.10 decades (window 50 – 200 kHz) |
| Fitted α at 0.7 / 1.0 / 1.5 V | 0.713 / 0.713 / 0.712 | 0.501 / 0.498 / 0.498 |
| Cα at 0.7 / 1.0 / 1.5 V | 1.59 / 1.67 / 1.71 nF·s^-0.3 | 29.0 / 30.9 / 31.5 nF·s^-0.5 |

Parasitic capacitance on the pin nets (excluding the bank capacitors themselves): 37 fF to ground and 15 fF to the
largest branch node; a further ~0.54 pF couples the pin's bank top plate to the bank bottom plates, which simply adds
about 5–11 % to each bank bit.

Note on simulation: with the buffers included, ngspice needs `.option rshunt=1e12` to find the operating point;
without it the transient-op fallback leaves the large capacitor nodes at the wrong bias and the results are wrong.
