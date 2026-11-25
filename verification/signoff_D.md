# Sign-off D11: independent review and resulting fixes (2026-11-25)

- **Reviewed:** commit 9befd3a. The GDS md5 was `56774a0aaaf0854e4a37b15ef889f967` and is unchanged by every fix
  below.
- **Reviewer:** a separate agent with no access to the design history, working from a fresh clone and a written
  checklist.
- **Blind phase:** while regenerating results the reviewer could not open the sign-off scripts or reports, so it wrote
  its own testbenches and extraction.
- **Full report:** `review/REVIEW_REPORT.md`. The brief is `review/CHECKLIST.md`.

## Verdict

**Ready after fixes; no blockers; no GDS change.** The reviewer regenerated:
- DRC, both hierarchical and flattened: 0 errors.
- LVS: circuits match uniquely.
- Antenna, after a positive control: 0 violations.
- The TT precheck: 17 of 17 pass.

Its own extraction and testbenches reproduce the sign-off bands within 0.05 decades, and its hand calculations agree
within 12 %.

## Findings and what was done

| ID | Finding | Action |
|---|---|---|
| S1 | The datasheet allowed a 1 Vrms test signal, contradicting its own "bias + peak ≤ 1.8 V" limit. At 1.0 V bias that puts 2.4 V on the MOS-capacitor gates and about 2.6 V on the floating trim nodes. The "about 4.5 % THD at 1 Vrms" was really the 0.5 Vrms result; the 1 Vrms value is 12–15 % at 1 kHz. | **Fixed in `docs/info.md`.** The maximum peak signal is now the smaller of (1.8 V − bias) and (bias − 0.5 V): 0.35 Vrms at 1.0 V bias. Users are told to set the analyzer level before connecting, because the E4990A defaults to 500 mVrms. The C10 statements about 1 Vrms are superseded; see below. |
| S2 | α = 0.5 Monte Carlo has a rare low tail (2 of 150 samples at about 2.0 decades) that the 2026-11-24 Monte Carlo did not show. That run had only 200 independent mismatch draws, because seeds were reused across corners. | **Monte Carlo re-run** with the fixed scripts (`sim/signoff/mc/mcsim2.py`, `mcan2.py`): 500 samples, unique seeds, each pin excited alone, every log and operating point checked, band edges interpolated. 0 failed runs. Tail confirmed: see the table below. The datasheet now quotes the median, 99th-percentile and worst values, and the ±3° band. |
| S3 | Sign-off scripts read inputs from outside the repository and could fail silently: no log checks, reused output files, NaN values zeroed, no per-corner seeds, grid-snapped band edges. | **Fixed:** `sim/signoff/common.py` (repository paths, `run_ngspice()` that raises on any error, `fresh()`, `bank_y()` that raises on non-finite values in band). All runners and analyses were patched; Tcl scripts resolve the GDS inside the repository. The RC netlist (`rc/top_rc.spice.gz`) and the raw sign-off data (`sim/signoff/data/`) are committed. The old MC scripts are marked superseded and kept as the record. A re-run of one corner case with the patched runner reproduces the stored data: \|Z\| within 0.1 % at 10 Hz and within 10⁻⁵ at 1–10 MHz. |
| N1 | Cα was quoted as 30.0 in one place and 30.9 in another, because of different fit windows. | The fit definition is stated in `info.md` and `verification/README.md`. |
| N2 | "At most 24 Ω" switch on-resistance applies only to bit 4; bit 0 is about 243 Ω. | Wording fixed. |
| N3 | The hierarchical-output extraction has 55 small negative capacitors that make long transients diverge. | Noted in `verification/README.md`; the committed flat netlist has none. |
| N4 | The low end of the trim range runs out at slow/low corners with the 9 pF pin model. | Already covered by B7: the cost is at most 0.05 decades. No action. |
| N5 | The ±2.5° figure is a cliff: about ±2.2° typical ripple, and one code off costs 0.3–0.4 decades. | The test procedure now explains this and asks for the ±3° band to be reported too. |
| N6 | The control path was verified independently; the extracted LSB is about 0.34 pF against 0.3 pF drawn. | Both values are now in `info.md`. |
| N7 | The workflows used `@ttsky26d`. | Changed to `@ttsky26e`. Both tags point to the same commit (`df73a1e`), and CI passes on b37d609. |

## Revised Monte Carlo (500 samples, worst of 12 pin models, best code per chip, interpolated band edges)

| | α = 0.7 | α = 0.5 |
|---|---|---|
| ±2.5°: median / 1st percentile / worst | 4.32 / 4.28 / 3.96 decades | 2.33 / 2.29 / 1.99 decades |
| Chips below 4.2 (α = 0.7) or 2.25 (α = 0.5) decades | 1 of 500 (0.2 %) | 4 of 500 (0.8 %) |
| ±3°: median / worst | 4.38 / 4.32 decades | 2.38 / 2.34 decades |
| Fitted α | 0.713 ± 0.001 | 0.500 ± 0.0015 |
| Cα at tt, 1.0 V | 1.66 nF·s^-0.3 ± 1.1 % | 30.1 nF·s^-0.5 ± 2.3 % |
| Cα range over all corners | 1.56 – 1.76 | 26.2 – 32.4 |
| Target (3.5 / 1.8 decades) | **pass, every sample** | **pass, every sample** |

The tail comes from in-band phase-ripple peaks that sit about 0.3° inside the ±2.5° limit. In roughly 1 % of chips,
mismatch pushes one peak past the limit and splits the band. For α = 0.5 this is the peak near 170 kHz. It does not
occur at ±3°. Closing it would take a ladder re-optimization (a layout change), which was judged not worthwhile
three days before tape-out because every sample meets the target.

## Corrections to earlier sign-off documents

- **signoff_B (B6):** the "3σ limit 2.24 / worst 2.25 decades" for α = 0.5 is superseded by the table above. The
  conclusions (best-code calibration; the top-window shortcut is unreliable) stand.
- **signoff_C (C10):** the current and self-heating figures were computed at 1 Vrms. That level is no longer allowed;
  at the new maximum of 0.35 Vrms, currents are about 0.35 × and self-heating about 0.12 × those values.

## Not re-checked by the reviewer

- Any temperature other than 27 °C. The designer's A3 runs at 85 and 125 °C stand.
- Electromigration rule values (no public source), ESD, and the leakage of the TT analog multiplexer.
