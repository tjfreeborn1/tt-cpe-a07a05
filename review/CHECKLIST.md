# Independent design review: tt_um_tjfreeborn1_cpe_a07a05 (TTSKY26e)

Reviewer brief. The goal is to regenerate the key results independently, not to re-read the existing ones.

## Ground rules
- Work only in `/home/claude/review/work/`. The repo copy to review is `/home/claude/review/repo/` (commit 9befd3a).
  Treat it as read-only.
- Do not modify, commit to or push `/home/claude/tt-cpe-a07a05`. Do not read or write `/home/claude/foc/`.
- **Blind phase (steps 1–3):** do not open `repo/sim/`, `repo/netlist/sim/`, `repo/verification/signoff_*.md` or
  `repo/layout/*.py`.
  - Allowed sources of design intent: `repo/docs/info.md`, `repo/info.yaml`, `repo/xschem/`, `repo/gds/`,
    `repo/lef/`, `repo/src/`, `repo/netlist/lvs/`, `repo/verification/lvs_netgen.out`, `run_lvs.tcl`,
    `precheck_results.md`.
  - Write your own testbenches from scratch.
- Machine: 2 cores, limited memory. Run at most 2 ngspice processes at a time.
- Tools:
  - PDK: `/home/claude/pdk/share/pdk/sky130A` (magic rc `libs.tech/magic/sky130A.magicrc`, ngspice
    `libs.tech/ngspice/sky130.lib.spice`).
  - `magic`, `netgen`, `ngspice`, `klayout`, `python3`.
  - The Tiny Tapeout precheck is in `/home/claude/src/tt-support-tools/precheck/precheck.py`; it needs `PDK_ROOT`
    and the staged project layout of gds/, lef/, src/ and info.yaml.
  - Magic hangs on Tcl errors, so always run it with `-dnull -noconsole` and `</dev/null`, under a `timeout`.
- **ngspice notes:**
  - The first line of a netlist is a title and is ignored.
  - With standard cells in the netlist, use `.option rshunt=1e12` or the operating point can fail silently.

## Design facts you may assume (from the design brief)
- `ua[0]`: α = 0.7 Morrison–Valsa RC ladder. `ua[1]`: α = 0.5. Both are passive.
- Each pin has a 5-bit trim bank of MIM capacitors switched to ground: `ui_in[4:0]` for `ua[0]` and `uio_in[4:0]` for
  `ua[1]`.
- Operating point: 1.0 V DC bias on the pin, small signal, 27 °C, VDPWR = 1.8 V.
- Pin-path model between the analyzer and the on-chip pin: series Rs ∈ {35, 100, 300, 500} Ω, then shunt Ce ∈ {4, 6.5,
  9} pF to ground on the analyzer side of Rs. That gives 12 models; nominal is 100 Ω / 6.5 pF.
- **Figure of merit:** the widest contiguous frequency band, within 20 Hz – 10 MHz, where the phase of Z seen through
  the pin model stays within ±2.5° of −90α°. Use the best trim code (0–31) per case, and quote the band in decades.
- **Sign-off targets:** at least 3.5 decades (α = 0.7) and 1.8 decades (α = 0.5) at the 3σ Monte Carlo limit after
  trim. Zero DRC, LVS, antenna and precheck errors.

## Steps
1. **Physical verification on `repo/gds/tt_um_tjfreeborn1_cpe_a07a05.gds`:**
   - Record the md5.
   - Magic DRC with the full rule style (`drc(full)`, euclidean on).
   - Netgen LVS of the layout extraction against the schematic netlist you build from `repo/xschem/` or
     `repo/netlist/lvs/`.
   - Magic `antennacheck`; first prove it flags a deliberate violation.
   - The TT precheck.
   - Your own parasitic extraction: capacitance plus coupling, cthresh 0.01 fF, hierarchical. Do not flatten: a flat
     extraction is known to misread the large MOS capacitors.
2. **Independent simulations with your own testbenches,** on your own extracted netlist:
   1. Typical corner, 1.0 V, 27 °C: the band in decades, its edges, the best code for both pins, at the nominal pin
      model and the worst of the 12.
   2. At least three hard corners, for example ff_ll at 0.7 V, fs_ll at 0.7 V and sf_ll at 1.5 V: the same metrics.
   3. Bias sweep at 0, 0.4, 0.5, 0.7, 1.0 and 1.5 V at the typical corner: the band in decades.
   4. Monte Carlo of about 50 samples with device mismatch plus global resistor and MIM variation, at the typical
      MOS corner.
      - Decide yourself how to model global variation.
      - **Verify by direct measurement on a single device** that every variation you apply actually changes that
        device's R or C, and by how much. Compare with the PDK corner spread (hh/ll for R, the cap corners for MIM).
      - Report the mean, σ and minimum band (best code, worst of the 12 pin models) and the spread of Cα.
   5. Fit α and Cα (|Z| = 1/(Cα·ω^α)) inside the band for the typical case.
3. **Hand calculations, independent of simulation:**
   - From the element values in the netlist, estimate the band edges, α, Cα and the trim LSB.
   - Check the DC parallel-resistor current at 1.0 V.
   - Flag any disagreement with the simulation larger than a factor of 1.5.
4. **Comparison and code review (the blind phase ends here):**
   1. Compare your numbers with `repo/docs/info.md` and `repo/verification/signoff_A.md`, `signoff_B.md` and
      `signoff_C.md`. Flag any of these differences: band > 0.05 decades, α > 0.01, Cα > 2 %, best code > 1 LSB, or
      any pass/fail disagreement.
   2. Code-review the original scripts in `repo/sim/signoff/` (and `repo/sim/`, `repo/layout/` where relevant). Look
      for silent failures:
      - parameters that do not take effect;
      - wrong data columns or indexing;
      - NaN or inf values silently dropped;
      - frequency grids that do not match;
      - title lines eaten by ngspice;
      - an operating point that failed;
      - non-deterministic seeds;
      - wrong signs or units.
5. **Datasheet consistency:** check `repo/docs/info.md` and `repo/info.yaml` against the extracted layout and the
   verification reports.
   - Pinout and bit mapping.
   - The test procedure: bias, amplitude, calibration method, safe operating limits.
   - Numbers, units and claims that are not supported by evidence.

## Deliverable
Write `/home/claude/review/REVIEW_REPORT.md` containing:
- A verdict: ready to submit / ready after listed fixes / not ready.
- Findings, each with a severity (BLOCKER: must fix before tape-out; SHOULD-FIX; NOTE), evidence and a suggested fix.
- A table comparing your numbers with the reported ones.
- A list of what you regenerated, and the scripts used (kept in `/home/claude/review/work/`).
- Anything you could not check, and why.
