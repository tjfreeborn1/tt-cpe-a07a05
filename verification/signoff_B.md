# Sign-off checks B4–B7 (2026-11-24)

These checks ran on the submitted GDS (md5 `56774a0aaaf0854e4a37b15ef889f967`). Scripts and summaries are in
`sim/signoff/rc/` and `sim/signoff/mc/`. Pass criteria, set before the runs:
- After trim, at least 3.5 decades (α = 0.7) and 1.8 decades (α = 0.5) at the 3σ Monte Carlo limit.

## B4 Full RC extraction: PASS

- **Method:** Magic hierarchical extraction with `extresist` (tolerance 10), capacitance and coupling (threshold
  0.01 fF): 97,661 wiring resistors.
  - A flattened extraction was tried first and discarded: it misread the MOS capacitors (429 "multiple lengths"
    warnings) and lost net names.
  - In the hierarchical netlist every ground fragment connects to VGND through the extracted resistors.
- **Wiring resistance against the capacitance-only netlist** (typical corner, 1.0 V, 27 °C):
  - Inside the band: |Z| changes by less than 0.2 % and phase by less than 0.6° (largest at the top edge, near 2 MHz).
  - Above 3 MHz, outside the band: up to 8 % on the α = 0.5 network alone, before the trim bank is added.
  - The constant-phase band, its edges and the best trim codes are the same at tt, ff_ll and ss_hh at 27 °C, and at
    tt at 125 °C.

## B5 Corners on the RC netlist: PASS

- The worst cases from the 828-case analysis were re-run on the RC netlist: fs_ll, sf_ll and ff_ll at 0.7, 1.0 and
  1.5 V, ff_lh, hl, lh, and tt at 0.7 and 1.5 V. Each was evaluated with all 12 pin-path models and both calibration
  methods.
- RC and capacitance-only results agree within one frequency-grid step (±0.03 decades) in every case.
- Worst single case with the best code: 4.25 decades (α = 0.7) and 2.27 decades (α = 0.5).
- Together with the 828-case analysis and the 85/125 °C runs from A3, the corner coverage is complete.

## B6 Monte Carlo: PASS (with the best-code calibration)

- **PDK model status:**
  - The SKY130 process Monte Carlo library (`mc`) fails on our 10 µm × 10 µm nfet ("could not find a valid
    modelname"), so it was not used.
  - The xhigh_po resistor's global spread comes from `sky130_fd_pr__res_high_po__var_mult`. The corner value of ±5
    gives ±8.2 % on a 98 µm segment. The `..._xhigh_po__var_mult` parameter has no effect on this model; this was
    checked directly.
- **Statistical model used:**
  - The PDK mismatch models (`mc_mm_switch=1`), applied per device instance. The extracted netlist has 428 separate
    MOS-capacitor fingers, 53 resistor segments and 74 MIM tiles.
  - Global Gaussian shifts with 3σ equal to the PDK corner limits: resistor `var_mult` σ = 5/3 and MIM area
    capacitance σ = 3.7 %. MIM perimeter capacitance has σ = 0.053 fF/µm.
  - MOS process: the tt corner (200 samples) and the ss/ff/sf/fs corners (50 samples each).
  - Every sample was evaluated with all 12 pin-path models, at 1.0 V and 27 °C, on the capacitance-only extracted
    netlist (equivalent to the RC netlist, see B4 and B5).

| Network | Calibration | Typical | 3σ limit (worst pin model, worst MOS corner) | Worst sample |
|---|---|---|---|---|
| α = 0.7 | widest ±2.5° band (code sweep) | 4.31 decades | **4.23** | 4.25 |
| α = 0.7 | flattest phase in 150–600 kHz | 4.29 | 2.03 (heavy tail) | 2.17 |
| α = 0.5 | widest ±2.5° band | 2.31 | **2.24** | 2.25 |
| α = 0.5 | flattest phase in 50–200 kHz | 2.29 | 2.09 | 1.85 |

- Fitted α: 0.713 ± 0.001 and 0.500 ± 0.002.
- Cα within one MOS corner: σ = 1.2 % (α = 0.7) and 2.0–2.6 % (α = 0.5).
- Cα between MOS corners: 1.60–1.72 nF·s^-0.3 and 29.3–30.8 nF·s^-0.5.
- **Finding:** the top-window shortcut picks a code one to three LSB off for about 1 % of (chip, pin-model)
  combinations, mostly at a pin resistance of 300–500 Ω with 4 pF. In those cases the α = 0.7 band falls to about
  2.2 decades.
  - Wider windows and RMS criteria were tested; none removes the tail.
  - Choosing the code with the widest measured ±2.5° band has no failures in any of the 4,800 (chip, pin-model)
    combinations.
  - The test procedure in `docs/info.md` is changed accordingly. The silicon needs no change.

## B7 Trim-bank coverage: PASS

- **Monotonic:** the worst differential non-linearity is −0.34 LSB over the corners and −0.38 LSB with mismatch, at
  the 15→16 carry. It is systematic: parasitics make bit 0 relatively larger.
- **Step size:** the LSB at 300 kHz is 0.27–0.35 pF and full scale is 8.4–10.8 pF across corners and mismatch.
- **Range:** the best code is 0–28. With the 9 pF pin model at the ss/fs corners, α = 0.7 wants code 0 or 1 in up to
  17 % of cases. The cost of hitting the end of the range is at most 0.05 decades (extrapolated with virtual codes
  below 0).
- **Resolution:** being one code off from the best costs about 0.4 decades (median), so the bench calibration must
  find the exact code. The full code sweep in B6 does this.
