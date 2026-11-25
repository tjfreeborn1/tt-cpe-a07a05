# Independent sign-off review: tt_um_tjfreeborn1_cpe_a07a05 (TTSKY26e)

- **Reviewed:** `/home/claude/review/repo/`, commit 9befd3a.
- **GDS md5:** `56774a0aaaf0854e4a37b15ef889f967`. This matches the md5 quoted in signoff_A, signoff_B and signoff_C.
- **Date:** 2026-11-25.
- **Method:** Everything in steps 1–3 was regenerated blind, with my own scripts and testbenches, before I opened
  `repo/sim/`, `repo/netlist/sim/`, `repo/layout/*.py` or `verification/signoff_*.md`.
- **Scripts and raw data:** `/home/claude/review/work/`.

## Verdict

**Ready after the listed fixes. The fixes are to documentation and scripts only; the GDS needs no change.**

- **Physical verification is clean.** I regenerated every check:
  - DRC: Magic `drc(full)`, both hierarchical and flattened.
  - LVS: Netgen.
  - Antenna: Magic `antennacheck`, after a positive control.
  - The Tiny Tapeout precheck: all 17 checks pass.
- **Both elements meet their sign-off targets with margin** on my own hierarchical extraction, testbenches and Monte
  Carlo (MC). The table gives the worst of the 12 pin models, with the best trim code per case:

| | α = 0.7 | α = 0.5 |
|---|---|---|
| Typical (tt, 1.0 V) | 4.33 decades | 2.33 decades |
| Worst of 13 corner/bias cases | 4.29 decades | 2.32 decades |
| MC, 100 samples, PDK statistics: mean − 3σ | 4.27 decades | 2.19 decades |
| MC, 100 samples, PDK statistics: empirical worst | 4.28 decades | 2.02 decades |
| Target | 3.5 decades | 1.8 decades |

- **Hand calculations agree with simulation.** The band, α, Cα and band edges all match within a few per cent. My
  numbers agree with the designer's within the flag limits, apart from the items flagged below.
- **The blocking issues are in the datasheet.**
  - The safe-operating table allows a 1 Vrms test signal. That contradicts the table's own voltage limits and would
    overstress the 1.8 V devices.
  - The α = 0.5 Monte Carlo "worst sample" is not reproduced: I find a rare tail at about 2.0 decades. It still
    passes the target.
  - The sign-off scripts read their inputs from outside the repository and have several silent-failure modes.
    Independent regeneration shows that these did not change the conclusions.

## Findings

### BLOCKER

None.

### SHOULD-FIX

**S1. The datasheet's maximum test signal of 1 Vrms contradicts its own limits and overstresses thin-oxide devices.
The THD figure quoted for it is wrong.**

- **What `docs/info.md` says:**
  - The safe-operating table allows "Test signal: … 1 Vrms maximum".
  - The same table requires bias + peak ≤ 1.8 V and a pin voltage that never goes below −0.3 V.
- **Why that cannot hold:**
  - At any allowed bias (0.7–1.5 V), 1 Vrms is 1.41 V peak. At 1.0 V bias the pin then swings from −0.41 V to
    +2.41 V.
- **My transient on the extracted netlist** (tt, 1.0 V, 100 Ω / 6.5 pF, typical code):
  - The MOS-capacitor gate nodes reach 2.41 V.
  - The floating bottom plate of an off trim bit, which is the drain of a 1.8 V nfet, reaches 2.56–2.58 V.
- **The 4.5 % THD figure is wrong for 1 Vrms:**
  - `info.md` quotes "about 4.5 % distortion" at 1 Vrms. In signoff_A (A2), 4.5 % is the 500 mVrms result, and
    `lsim.py` never simulates 1 Vrms.
  - At 1 Vrms I get 15.2 % THD (α = 0.7) and 11.7 % (α = 0.5) at 1 kHz, and 4.7 % at 1 MHz.
- **What is fine:** at 100 mVrms the datasheet's 0.35 % is confirmed. I get 0.30–0.37 % at 1 kHz and 0.12–0.21 %
  at 100 kHz.
- **Fix:** state the maximum signal as the smaller of (1.8 V − bias) and (bias − 0.5 V) as a peak value. That is
  0.35 Vrms at 1.0 V bias and 0.21 Vrms at 1.5 V. Delete "1 Vrms maximum", or mark it as an absolute limit that is
  only allowed with no DC bias applied. Quote THD with its amplitude and frequency.

**S2. The α = 0.5 Monte Carlo has a rare low tail that the sign-off does not show, so the datasheet's "3σ limit
2.24 / worst 2.25" is not reproduced.**

- **My results:**
  - Main MC: 100 tt samples with PDK mismatch (`mc_mm_switch=1`) plus PDK-MC global R/MIM statistics. Two samples,
    #44 and #89, give 2.04 and 2.02 decades (worst of 12 pin models). The remaining 98 have a minimum of 2.30.
  - Both outliers have near-nominal global draws (|z| < 0.5), so mismatch drives them.
  - The mechanism is the top-of-band ripple peak at 150–210 kHz. Its typical value is +2.1 to +2.2°, only 0.3–0.4°
    inside the ±2.5° window. In the outliers it reaches +2.6 to +2.9°, which splits the band at about 150 kHz.
  - Re-running sample #89 on the netlist with the negative capacitors removed, and re-running it with the same seed,
    reproduces the result exactly. The run passes all operating-point checks.
  - A second, independent 50-sample MC uses the designer's more conservative global sigmas and new seeds. It shows
    no outlier (minimum 2.30).
  - In total, 2 of 150 mismatch realisations fall to about 2.0 decades.
- **The designer reports** 0 of 400 samples below 2.25. Their 400 samples contain only 200 distinct mismatch
  realisations; see S3.
- **Consequences:**
  - The pass/fail result is unchanged: 2.02 ≥ 1.8.
  - The distribution is bimodal, so "mean − 3σ" is not a meaningful statistic for α = 0.5.
  - The datasheet's "worst 2.25" and "band shared by all cases 2.12" are optimistic statements of the margin.
- **Fix:** quote empirical percentiles, for example "≥ 2.3 decades in 98 % of samples, ≥ 2.0 decades in all", and
  state that the ripple margin is only about 0.3°. Optionally re-run the MC with the script fixes in S3.

**S3. The sign-off evidence cannot be regenerated from the repository, and the scripts have silent-failure modes.**

These did not change the conclusions: my independent results reproduce the designer's within the flag limits, apart
from S2. They should still be fixed before the repository is cited as evidence.

- **Inputs from outside the repository:**
  - `sim/signoff/antenna_check.tcl` and `rc/rcx_hier.tcl` read `/home/claude/foc/lay/build/…gds`, not
    `repo/gds/`. The md5 claim in the sign-off documents therefore cannot be checked from these scripts.
  - `mc/mcsim.py` (default `NET`), `c/coup.py` and `c/gd.sp` read `/home/claude/foc/lay/pex/top_pex.spice`.
  - `lsim.py` and `leak.py` read `/home/claude/foc/lay/asbuilt`.
- **Large-signal and leakage checks were not done on the extracted netlist.**
  - A2 and C10 (large signal) and A3 (leakage) use schematic "as-built" netlists, not the extraction.
  - Those netlists add sim-only 10 GΩ bleeders (`RL0–RL4` in `sim/netlists/trimbank.spice`). These set the DC level
    of the floating bank nodes, which is exactly what the pumping analysis is about.
  - Note also that `lsim.py` puts Ce on the chip side of Rs, which differs from the stated pin model.
- **No error checking:**
  - Every runner calls `subprocess.run(…, capture_output=True)` and never inspects the log or the return code
    (`pexsim.py`, `pexbias.py`, `pexhot.py`, `rc/pexrc*.py`, `lsim.py`, `coup.py`, `mcsim.py`).
  - `pexsim.py`, `pexbias.py` and `pexrc2.py` reuse one output file (`zp{part}.dat`) for every case. A failed run
    would silently reload the previous case's data. I found no duplicate entries in the committed JSON results, so
    this did not visibly happen.
- **NaN and inf values are silently zeroed:** `np.nan_to_num(...)` on bank admittances in `mc/mcan.py`,
  `mc/wintest.py`, `rc/rccmp.py`, `rc/rc2cmp.py` and `hotan.py`. A failed bit simulation would look like a bit with no
  capacitance.
- **Path-dependent operating-point failures:**
  - `mcsim.py` alters the trim-gate sources between AC runs without `reset`.
  - With my testbench, the same pattern failed to converge going from code 7 to code 8 (gmin and source stepping
    failed, then "timestep too small"). Code 8 converges fine from a fresh start.
  - The designer's 1-bit pattern may avoid this, but nothing would detect it if it happened.
- **Mismatch seeds are reused across MOS corners:** `.option seed={1000+k}` is the same for tt, ss, ff, sf and fs. So
  samples 0–49 have identical mismatch realisations in every corner, and the 400 samples contain 200 independent
  mismatch draws.
- **Both pins are excited at once:** both sources carry `ac 1` in every PEX run. The measured impedance includes
  pin-to-pin crosstalk of up to −54 dB at 10 MHz. The effect is negligible in band, but it is not the stated
  "other pin idle" condition.
- **Bands are rounded down to the frequency grid:** 40 points per decade with no edge interpolation. Reported bands
  are low by 0.00–0.05 decades. This explains most of my systematic +0.02 to +0.03 decade offset.
- **Fix:**
  - Commit the actual netlists and GDS paths.
  - Check each log for errors, "aborted" and "failed", and use unique output files per case.
  - Replace `nan_to_num` with an assertion.
  - Use `reset` between operating-point changes.
  - Use per-corner seeds.
  - Interpolate the band edges.

### NOTE

**N1. Cα depends on the fit method, and the repository quotes two different values.**

- `info.md` gives 30.0 nF·s^-0.5 at 1.0 V, while `verification/README.md` gives 30.9 (2.8 % apart).
- My free (α, Cα) fit over each case's own band gives 29.6. Over the designer's common window (1.88 – 251 kHz) it
  gives 30.6.
- The difference is the fit window, not the circuit. With the same window my values match README's to ≤ 0.9 %
  (α = 0.7: 1.583 / 1.670 / 1.702 vs 1.59 / 1.67 / 1.71).
- Fixing α at exactly 0.7 changes Cα by +16 % (1.93 nF·s^-0.3), because the fitted α is 0.713.
- **Fix:** state the fit method, the window, and that the units follow the fitted α.

**N2. The datasheet's VDPWR row misquotes the switch on-resistance.**

- It says "trim switches … at most 24 Ω on-resistance". signoff_C (C8) says 24 Ω for bit 4 but 400 Ω for bit 0
  (ss, 125 °C).
- My numbers at VGS = 1.62 V, from bit 0 to bit 4:
  - tt, 27 °C: 243 / 118 / 59 / 29 / 14.7 Ω.
  - ss, 85 °C: 357 … 21 Ω.
- The pole this creates is above 2 GHz, so there is no performance impact. Correct the wording.

**N3. The hierarchical extraction contains negative capacitors that make transient simulation unstable.**

- The hierarchical C + coupling extraction (`ext2spice hierarchy on`) contains 55 negative capacitors to ground,
  between −0.07 and −0.26 fF. They come from Magic's parent/child coupling adjustment.
- A transient on that netlist diverges spontaneously on `ua[0]` after about 1 ms, even with no signal. I reproduced
  this with trap, Gear and tight tolerances.
- Removing the 55 elements makes it stable. AC results change by < 0.002 decades.
- This does not affect silicon. Anyone running a post-layout transient must either remove these elements or use a
  flat-output netlist. The designer's flat-output netlist has none.

**N4. The low end of the trim range is exhausted at slow/low corners with the 9 pF pin model.**

- At fs_ll, ss_ll and tt at 0.5–0.7 V, α = 0.7 with 500 Ω / 9 pF wants code 0–1.
- The band cost is small (4.24–4.30 decades), but there is no margin for a pin capacitance above 9 pF.

**N5. The figure of merit is a cliff.**

- One code away from the best costs 0.3–0.4 decades. For example:
  - α = 0.7: code 11 gives 4.34 decades and code 10 gives 3.91.
  - α = 0.5: code 15 gives 2.33 decades and code 14 gives 2.04.
- The typical ripple is ±2.2° against a ±2.5° window. So the measured band will depend strongly on the analyzer's
  phase accuracy and fixture compensation.
- The full 32-code sweep recommended in the datasheet is the right calibration.
- **Suggestion:** also publish the ±3° band. The designer's own `pex_results.json` gives a 4.20-decade common band
  at ±3°.

**N6. The digital control path is correct; I verified it independently.**

- On the extraction, each switch gate tracks its `ui_in[k]` / `uio_in[k]` input at 0 / 1.8 V for all 32 codes.
- The simulated bit weights are 0.337 / 0.643 / 1.245 / 2.449 / 4.883 pF at 100 kHz, which is binary and confirms
  the mapping. Steps are 0.275–0.337 pF and full scale is 9.47 pF.
- The datasheet's "0.3 pF steps, 0–9.3 pF" is the drawn value. The extracted LSB is about 12 % larger because of
  coupling to the top plate.
- All 24 outputs are tied LO.

**N7. The GitHub workflow uses `TinyTapeout/tt-gds-action/*@ttsky26d`, but the shuttle is TTSKY26e.** Check that this
matches the current template.

**N8. Methodology notes for future reviewers.**

- `set rndseed` in `.spiceinit` did not make ngspice-42 Monte Carlo reproducible: the same seed gave different draws.
  `.option seed=N` in the netlist does.
- Repeating `antennacheck` in the same Magic session after an edit did not pick up the change. Run the positive
  control in a fresh session, as I did.

## Comparison with the reported numbers

Flag criteria: band > 0.05 decades, α > 0.01, Cα > 2 %, best code > 1 LSB, or any pass/fail disagreement. "Worst" means
the worst of the 12 pin models, each re-trimmed. All my bands use edges interpolated in log f on a 60 points-per-decade
grid. The designer's bands are snapped to a 40 points-per-decade grid.

| Quantity | Reported (source) | Mine | Δ | Flag |
|---|---|---|---|---|
| tt 1.0 V, α = 0.7: nominal band / code | 4.30–4.33 / 11 (A2, `lsim` NET) | 4.344 (96 Hz–2.12 MHz) / 11 | ≤ 0.04 / 0 | – |
| tt 1.0 V, α = 0.5: nominal band / code | 2.30–2.33 / 14 (A2, `lsim`) | 2.329 (1.43–304 kHz) / 15 | ≤ 0.03 / 1 | – |
| tt 0.7–1.5 V, worst: α = 0.7 / α = 0.5 | ≥ 4.28 / ≥ 2.30 (A2) | 4.325–4.330 / 2.325–2.330 | +0.05 / +0.03 | – (borderline) |
| Bias 0 V, nominal (worst) | 0.57 (0.30) / 0.68 (0.23) | 0.586 (0.318) / 0.702 (0.241) | ≤ 0.02 | – |
| Bias 0.4 V | 4.30 (0.77) / 2.30 (0.90) | 4.324 (0.780) / 2.331 (0.932) | ≤ 0.03 | – |
| Bias 0.5 V | 4.30 (4.23) / 2.32 (2.30) | 4.325 (4.238) / 2.340 (2.311) | ≤ 0.03 | – |
| Best code 0.7 → 1.5 V | 9 → 12 / 12 → 15 (A2) | 9, 11, 12 / 12, 15, 15 | 0 | – |
| Worst single corner case | 4.25 (fs_ll 0.7 V, code 0) / 2.27 (B5) | 4.287 (fs_ll 0.7 V, 500 Ω/9 pF, code 0) / 2.317 (ss_ll 0.7 V) | +0.04 / +0.05 | – (borderline) |
| Common band, all cases | 4.12, 126 Hz–1.68 MHz / 2.12, 1.88–251 kHz | 4.16, 120 Hz–1.75 MHz / 2.16, 1.79–260 kHz (my 13 cases) | +0.04 / +0.04 | – |
| MC typical | 4.31 / 2.31 (info.md, B6) | 4.338 / 2.332 (nominal mean); 4.323 / 2.320 (worst-model mean) | ≤ 0.03 | – |
| MC 3σ limit | 4.23 / 2.24 | 4.268 / **2.189** (PDK σ); 4.280 / 2.294 (designer σ, 50 samples) | +0.04 / **−0.05** | **α = 0.5 flagged** (bimodal, see S2) |
| MC worst sample | 4.25 / 2.25 | 4.277 / **2.015** | +0.03 / **−0.24** | **α = 0.5 flagged** (S2) |
| Sign-off pass (≥ 3.5 / ≥ 1.8) | PASS / PASS | PASS / PASS | – | – |
| Fitted α, tt 1.0 V | 0.713 / 0.500 (info.md); 0.713 / 0.498 (README) | 0.7126 / 0.5014 | ≤ 0.004 | – |
| Fitted α, MC | 0.713 ± 0.001 / 0.500 ± 0.002 | 0.7131 ± 0.0007 / 0.5002 ± 0.0020 | – | – |
| Cα at 1.0 V, α = 0.7 (nF·s^-0.3) | 1.66 (info.md), 1.67 (README) | 1.662 (own band), 1.670 (common window) | ≤ 0.5 % | – |
| Cα at 1.0 V, α = 0.5 (nF·s^-0.5) | 30.0 (info.md), **30.9 (README)** | 29.62 (own band), 30.63 (common window) | 1.3 % / **4.1 %** | **README flagged** (fit-window definition, N1) |
| Cα at 0.7 / 1.5 V, α = 0.7 | 1.59 / 1.71 | 1.594 / 1.695 (own); 1.583 / 1.702 (common window) | ≤ 0.9 % | – |
| Cα at 0.7 / 1.5 V, α = 0.5 | 29.0 / 31.5 | 29.31 / 30.73 (own); 29.17 / 31.76 (common window) | 1.1 % / 2.4 % (own); ≤ 0.8 % (window) | – (window) |
| Cα MC 1σ | 1.2 % / 2.5 % (or 2.0–2.6 %) | 0.92 % / 2.53 % (PDK σ); 1.03 % / 1.71 % (designer σ) | – | – |
| Trim LSB / full scale | 0.27–0.35 pF / 8.4–10.8 pF (B7) | 0.275–0.337 pF / 9.47 pF (tt) | – | – |
| DC current at 1.0 V through Rp | 51–69 nA / 1.35–1.81 µA (A3) | 55.55 nA / 1.465 µA (tt); hand 55.5 nA / 1.464 µA | – | – |
| Crosstalk `ua[1]` → `ua[0]` at 10 MHz | −54 dB (C9) | −53.8 dB (code 0) | – | – |
| THD, 100 mVrms, 1.0 V | 0.31 % at 2 kHz (A2), 0.35 % (info.md) | 0.30 % (α = 0.5) / 0.37 % (α = 0.7) at 1 kHz | – | – |
| THD, 1 Vrms | "about 4.5 %" (info.md) | 15.2 % / 11.7 % at 1 kHz; 4.7 % at 1 MHz | – | **flagged** (S1) |
| Switch Ron at 1.62 V | "at most 24 Ω" (info.md); 24 Ω bit 4 / 400 Ω bit 0 (C8) | 14.7–243 Ω (tt 27 °C); 21–357 Ω (ss 85 °C) | – | **info.md flagged** (N2) |
| Wiring R vs C-only | ≤ 0.03 decades; in band \|Z\| < 0.2 %, phase < 0.6° (B4, B5) | ≤ 0.017 decades, codes ±1; in band \|Z\| ≤ 0.29 %, phase ≤ 0.09° | – | – |
| Pin-net parasitics | 37 fF to ground, 15 fF to branch, 0.54 pF bank coupling (README) | ≈ 33 fF, 15.4 fF, 0.533 pF | – | – |
| DRC / LVS / antenna / precheck | 0 / match / 0 / pass | 0 (hierarchical and flat) / match uniquely / 0 (hierarchical and flat) / 17 of 17 pass | – | – |

### Hard corners in detail (my results)

All at nominal pin model 100 Ω / 6.5 pF unless stated, and on my extracted (hierarchical C + coupling) netlist.

| Corner and bias | α | Nominal: band, edges, code | Worst of 12 models: band (model, code) |
|---|---|---|---|
| tt 1.0 V | 0.7 | 4.344, 96 Hz–2.12 MHz, 11 | 4.330 (500 Ω/9 pF, 3) |
| tt 1.0 V | 0.5 | 2.329, 1.43–304 kHz, 15 | 2.329 (100 Ω/6.5 pF, 15) |
| ff_ll 0.7 V | 0.7 / 0.5 | 4.332, 110 Hz–2.36 MHz, 11 / 2.328, 1.63–346 kHz, 15 | 4.313 (500/9, 2) / 2.319 (500/9, 6) |
| fs_ll 0.7 V | 0.7 / 0.5 | 4.329, 120 Hz–2.56 MHz, 8 / 2.334, 1.79–385 kHz, 11 | 4.287 (500/9, **0**) / 2.319 (500/6.5, 12) |
| sf_ll 1.5 V | 0.7 / 0.5 | 4.328, 100 Hz–2.13 MHz, 15 / 2.329, 1.48–316 kHz, 19 | 4.316 (300/9, 6) / 2.321 (500/9, 10) |
| ss_ll 0.7 V | 0.7 / 0.5 | 4.319, 118 Hz–2.46 MHz, 9 / 2.328, 1.76–374 kHz, 12 | 4.297 (500/9, **0**) / 2.317 (500/9, 3) |
| ss_hh, ff_hh, sf_hh, fs_hh, ff_ll 1.5 V, ss_hh 1.5 V | both | 4.336–4.356 / 2.330–2.349 | ≥ 4.320 / ≥ 2.324 |

### Hand calculation compared with simulation

The hand model uses the PDK formulas for the xhigh_po resistors (body 5714 Ω/µm plus 588 Ω ends) and the MIM
capacitors (2.0 fF/µm² plus 0.19 fF/µm perimeter). The MOS capacitance is 7.59 fF/µm² at 1.0 V, inversion. A plain
Cox estimate (tox about 4.15 nm gives 8.3 fF/µm², about 7.6 fF/µm² in inversion) agrees with this value.

| | α = 0.7: hand | α = 0.7: simulation | α = 0.5: hand | α = 0.5: simulation |
|---|---|---|---|---|
| Rp; DC current at 1 V | 18.02 MΩ; 55.5 nA | 55.55 nA | 0.683 MΩ; 1.464 µA | 1.465 µA |
| Branch poles | 403 Hz, 2.99 k, 17.8 k, 112 k, 838 kHz | – | 2.97 k, 9.32 k, 97.8 kHz | – |
| Total network capacitance | 198 pF | – | 199 pF | – |
| Band (nominal pin model), code | 4.340, 98 Hz–2.14 MHz, 12 | 4.344, 96 Hz–2.12 MHz, 11 | 2.332, 1.45–311 kHz, 16 | 2.329, 1.43–304 kHz, 15 |
| Fitted α / Cα | 0.711 / 1.662 nF·s^-0.3 | 0.7126 / 1.662 | 0.5006 / 29.64 nF·s^-0.5 | 0.5014 / 29.62 |
| Trim LSB | 0.301 pF (drawn) | 0.337 pF (extracted, ×1.12) | same | 0.335 pF |

No disagreement exceeds a factor of 1.5. The largest ratio is 1.12, for the LSB, and it is explained by top-plate
coupling.

## What I regenerated, and how

All of this is under `/home/claude/review/work/`.

1. **Physical verification (`pv/`, `lvs/`, `ant/`, `precheck/`, `sch/`).**
   - **DRC (`drc4.tcl`, `drcflat.tcl`):** Magic `drc(full)` with euclidean on and `drc on`. It reports 0 errors
     both hierarchically and on a flattened copy.
   - **DRC positive control (`drc3.tcl`, `drc_precheckstyle_inj.tcl`):** a 0.1 µm met1 sliver is caught.
   - **Schematic netlist:** I netlisted the Xschem schematic myself (`sch/tt_um_mine.spice`). Its topology and device
     sizes match the committed `netlist/lvs`.
   - **LVS (`ext_lvs.tcl`, `e2s.tcl`, `lvs.tcl`):** Magic extraction, then Netgen gives "Circuits match uniquely".
   - **Antenna (`anttest.tcl`, `anthier.tcl`, `antinj.tcl`, `antreal.tcl`, `antflat.tcl`, `antflatinj.tcl`):**
     - The positive control (a gate under 400 µm² of met1) is flagged at a ratio of 1940 against a limit of 400. It
       is flagged as a standalone cell, inside a hierarchy, and painted into the flattened design.
     - The real design has 0 violations, both hierarchically and flattened.
   - **TT precheck:** run on a staged copy, with the tools copied to `precheck/tools`. All 17 checks pass.
2. **Parasitic extraction (`pex/pex.tcl`).** Hierarchical C + coupling with cthresh 0.01 fF, giving `pex/pex.spice`.
   I also made a copy with the 55 negative capacitors removed (`pex_noneg.spice`). For the wiring-resistance check,
   `rcx/rcx.tcl` runs `extresist` and gives 97,661 resistors.
3. **Device-level verification (`dev/devtest.py`, `dev/mcdev.py`).**
   - R, MIM C and MOS C-V were measured on single devices at tt, ll, hh, ff, ss, sf, fs and with my override files.
   - R (98.453 µm segment) is 562.65 kΩ. ll/hh change it by −8.28 / +8.27 %. My `var_mult` override gives
     +1.655 % per unit.
   - MIM (29.96 × 25.02 µm) is 1.5173 pF. ll/hh change it by −11.8 / +12.2 %. A +10 % `camimc` gives +9.86 %.
   - The MOS 10 × 10 µm capacitor is 0.759 pF at 1.0 V and 0.221 pF at 0 V. ff/ss change it by +4.1 / −3.8 %; ll/hh
     do not change it.
   - Mismatch is active (two identical instances differ) and is reproducible with `.option seed`.
   - Each of the 100 MC samples was re-measured with its own library file and seed:
     - The R spread is 2.37 % (slope 1.74 % per `var_mult`; 0.53 % residual from mismatch).
     - The MIM spread is 2.77 %.
     - The MOS-capacitor spread is 0.03 % (mismatch only, as intended).
     - This places the PDK ll/hh corners at about 3.5σ for R and 4.3σ for MIM.
4. **AC simulations (`sim/tb.py`, `runcase.py`, `batch.py`).**
   - **Testbench:** the full top level with the extracted buffers, VDPWR = 1.8 V, and `rshunt=1e12`. For every code
     I `reset`, then set the 10 gate sources. The operating point is checked for pin bias and for all 10 internal
     switch gates. I scan the log for errors.
   - **Analysis:** each pin is excited separately while the other is AC-grounded, 20 Hz–10 MHz at 60 points per
     decade. The 12 pin models are applied analytically as Ce ∥ (Rs + Z_chip), with Ce on the analyzer side.
   - **Cases:** tt 1.0 V; bias sweep 0, 0.4, 0.5, 0.7, 1.0 and 1.5 V; and 10 hard corner/bias cases (ff_ll, fs_ll,
     ss_ll, ss_hh and fs_hh at 0.7 V; sf_ll, ff_hh, sf_hh, ff_ll and ss_hh at 1.5 V). Results are in `runs/`.
5. **Monte Carlo.**
   - **MC1:** 100 tt samples with PDK mismatch plus PDK-MC global statistics: `var_mult = 1.25·N` and the PDK
     `camimc(mim)` polynomial (σ 2.83 %).
   - **MC2:** 50 tt samples with the designer's statistics: σ_var_mult = 5/3, MIM σ 3.7 %, cpmimc σ 0.053 fF/µm,
     and new seeds.
   - Statistics are computed by `sim/mcstats.py`.
6. **Fits, trim-bit weights and crosstalk.** These come from the saved admittances (`runs/*/Y.npz`).
7. **Wiring resistance (`sim/rcrun.py`).** I simulated the R + C netlist at 20 codes and compared it with the C-only
   netlist.
8. **Large signal (`tran/tran.py`).** Transients at 0.01, 0.1 and 1 Vrms, at 1 kHz, 100 kHz and 1 MHz, on the
   extraction with the negative capacitors removed.
9. **Switch on-resistance (`dev/ron/ron.py`)** and **hand calculations (`hand/hand.py`).**

### Inputs I used during the blind phase

I used only the allowed design-intent files. In addition, `verification/README.md` was printed once, unintentionally,
at the start. That file is neither on the forbidden list nor on the allowed list. It contains the reported Cα and band
values. My testbenches, statistics and analysis do not use anything from it.

## What I could not check

- **Temperature:** I ran no simulations other than at 27 °C. The 85 / 125 °C claims in A3 and the 0 / 70 °C cases in
  the 828-case set are not regenerated.
- **MOS global variation inside the MC:** this follows the brief, so the MC is at the tt MOS corner only. The ss, ff,
  sf and fs corners are covered only by my deterministic corner runs.
- **The designer's inputs under `/home/claude/foc/`:** I was not allowed to read them. So I cannot confirm that the
  GDS and netlists the designer's scripts actually used are the submitted ones. My own regeneration from
  `repo/gds/` stands on its own.
- **Self-heating (about 20 K), electromigration margins, bias-step inrush, ESD and the leakage of the Tiny Tapeout
  multiplexer:** not checked. These are outside the design or have no PDK rule data.
- **Measurement realism:** analyzer phase accuracy, fixture compensation residue and board coupling are not modelled.
  N5 explains why they matter for this figure of merit.
- **Root cause of the S2 outliers:** I did not trace them to a single device. The ripple peak is near the third (R3,
  C3) branch of the α = 0.5 network, but the exact element is unconfirmed.
