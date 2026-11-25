# Extra validation V1–V4: model trust, real-world path and measurement rehearsal (2026-11-25)

None of these checks changes the GDS (md5 `56774a0a…`, blob `47112fc7…`). They test the assumptions behind the
sign-off: the models, the pin path, and whether the measurement can show what the chip does. Scripts are in
`sim/signoff/v1/` and `sim/signoff/v2/`, and the analysis script is in `test/`.

## V1 How wrong can the models be? (`v1/v1sim.py`, `v1b.py`, `v1_summary.txt`)

**Method:** extracted netlist, tt, 27 °C, 1.0 V, no mismatch, best code, worst of 12 pin models. Each error was
applied by a method first verified on a single device.
- **MOS capacitors:** instance `m=`. The `mult=` parameter is silently ignored by both the MOS and resistor models.
- **Resistors:** the segment length is rewritten using the model's R = 5708.6·L + 623 Ω. `m=` is ignored by the
  xhigh_po model.
- **MIM:** `camimc` and `cpmimc` are scaled; checked on the bank (bit 4 rose ×1.147 for kC = 1.15).

**Common-mode errors (all devices of one type together): robust.** Total R ±25 %, MOS capacitance ±20 % and MIM ±15 %
were tested in all 75 combinations:
- α = 0.7 stays at 4.24–4.33 decades and α = 0.5 at 2.32–2.33 in every combination except one corner.
- That corner is MOS +20 % with MIM −15 %: 3.87–4.00 and 1.93–1.96 decades. It still passes, but trim code 31 is
  reached, which is the edge of the trim range.
- End-resistance errors from −50 % to +200 % cost at most 0.04 decades.

**A single branch resistor off on its own: sensitive.** The trim only adjusts the top-end capacitance and cannot repair
a ladder ratio. Each branch alone was changed by −25 % to +25 %:

| Branch | First failing error (target 3.5 / 1.8 decades) |
|---|---|
| α = 0.7: R1 | +15 % |
| α = 0.7: R2 | −15 %, +25 % |
| α = 0.7: R3 | −15 % |
| α = 0.7: R4 | −25 % |
| α = 0.7: R5 | none within ±25 % |
| α = 0.7: Rp | +25 % |
| α = 0.5: R1 | −25 % |
| α = 0.5: **R2** | **±10 % (passes at ±5 %)** |
| α = 0.5: R3 | −15 % |
| α = 0.5: Rp | −25 %, +10 % |

**Physical plausibility:** every resistor is the same 0.35 µm xhigh_po device, so a ratio error needs a
branch-specific cause.
- Mismatch is in the Monte Carlo: about 0.9 % σ for α = 0.5's R2 (one 38.8 µm segment), so ±10 % is about 10σ.
- Length-dependent effects (end resistance, edge bias) were tested above and are harmless.
- The remaining risk is a systematic length-dependent sheet-resistance error between the 2.6 µm and 98 µm segments
  that the PDK does not model. That would be a model bug, not a statistical effect.
- **α = 0.5 is the more fragile network**, consistent with where the Monte Carlo tail appears.

## V3 Pin path against real Tiny Tapeout hardware

- **TT specification:** path resistance < 500 Ω, capacitance < 5 pF, maximum 4 mA (tinytapeout.com/specs/analog).
  The pin model spans 35–500 Ω and 4–9 pF.
- **The switch itself** (`tt_asw_3v3`, extracted from its own GDS in TinyTapeout/tt-multiplexer), at tt/ss/ff,
  27/85 °C and 0.5–1.5 V:
  - On-resistance 35–104 Ω.
  - About 150–250 fF per switch on the bus side.
  - DC current of at most 44 pA. That is the simulator's minimum-conductance floor, so real leakage is lower. Even
    20 off-switches on one bus would add under 1 nA against the 55 nA through α = 0.7's Rp: at most 0.3° at the bottom
    of the band.
  - Topology check: the bus capacitance sits on the pad side of the switch resistance, as in the pin model.
- **Board (TT ETR demoboard v3 schematic, TinyTapeout/tt-demo-pcb):** "All analog pins pulled down on DB", with
  **10 MΩ** resistors (R40/R41/R44/R45…). See V2 for the consequence.

## V4 Model physics checks (`/home/claude/v4`, `v1/nqs.py`)

- **Model bin:** the W = L = 10 µm nfet sits in model bin 1 (L 8–20 µm, W 7–100 µm), inside the characterized range.
- **Oxide check:** with toxe = 4.148 nm, Cox·A = 0.833 pF. The model gives 0.759 pF at 1 V (91 %: poly depletion plus
  the inversion-layer charge centroid), 0.572 pF at 0.5 V and 0.349 pF at 0.3 V (tt). This is plausible physics.
- **Channel resistance:** the quasi-static BSIM4 model does not include the inversion-channel resistance. The
  distributed channel RC, with source and drain both grounded (R_eff = R_ch/12), has its corner at:
  - 311 MHz at 1.0 V, 114 MHz at 0.7 V, 11 MHz at 0.5 V, 1.4 MHz at 0.4 V.

  Adding R_eff in series with all 428 MOS fingers of the extracted netlist changes the band by at most −0.02 decades
  at 0.5 V and ≤ 0.01 decades at 0.6–1.0 V. Each finger's R_eff is small next to the branch resistor in series with
  it. **Conclusion:** the quasi-static model is adequate and the bias rule (bias − peak ≥ 0.5 V) stands.
- **Bench temperature (15–35 °C)** is inside the 0–70 °C range of the 828-case corner analysis.

## V2 Measurement rehearsal (`v2/rehearse.py`, `v2/e4990_acc.py`, `test/analyze_e4990.py`)

**Setup:**
- **Chips:** 100 revised Monte Carlo samples.
- **Path:** switch 60 Ω, on-chip bus/pad 4 pF, demoboard about 6 pF plus the 10 MΩ pull-down.
- **Analyzer error:** the E4990A data-sheet accuracy equation (4-terminal-pair, 1 m cable, mode 5), applied as a
  smooth systematic residual that all 32 code sweeps share, plus noise of 0.05 × E. Simulated at the guaranteed limit
  (k = 1) and at typical level (k = 1/3).
- **Calibration:** the widest ±2.5° band over the 32 codes.

| Setup | α = 0.7 measured: median / 5th percentile | α = 0.5 measured | Verdict |
|---|---|---|---|
| Open compensation with the project deselected | 3.4–3.9 / 3.3–3.8 decades | 1.0–1.8 / 0.9 | **Wrong**: it subtracts the ~4 pF of on-chip bus capacitance the design includes in its top-end capacitance. |
| Fixture-tip compensation, 10 MΩ pull-down in place | 3.1 / 3.1 (low edge ~1.5 kHz) | 2.28 | **Wrong**: the pull-down erases the bottom decade of α = 0.7. |
| Pull-down lifted, segment sweep | 4.28–4.32 / 3.86–3.97 | 2.33–2.34 / 2.32 | Good |
| Open/short at the demoboard header with the carrier removed, segment sweep | 4.29–4.33 / 3.87–3.97 | 2.34 / 2.31–2.32 | Good. The chosen code is the chip's best in 86–98 % of cases and always within one code. |
| Same with 100 mVrms throughout, guaranteed-limit accuracy | 3.98 / 3.73 (low edge 205 Hz) | 2.33 / 2.05 | The segment sweep recovers about 0.3 decades at the low end. |

**Analyzer limits:**
- The E4990A's guaranteed phase accuracy on the α = 0.7 element, which is 1–6 MΩ below 1 kHz:
  - ±0.9° at 1 kHz and ±4–5° at 100–126 Hz with 100 mVrms;
  - ±1.5° at 126 Hz with 300 mVrms.
- A segment sweep (300 mVrms below 10 kHz, 100 mVrms above) keeps the 1.0 V-bias limits. The A2 transients show the
  larger signal moves the phase by only 0.04°.

**Uncompensated external capacitance limit:** the trim absorbs about 6 pF beyond the on-chip 4 pF bus.

| Extra C | α = 0.7 band (best codes) | α = 0.5 band (best codes) |
|---|---|---|
| 0 pF | 4.33 decades (18–21) | 2.34 decades (21–25) |
| 3 pF | 4.33 (9–11) | 2.34 (12–14) |
| 6 pF | 4.32 (0–1) | 2.34 (2–4) |
| 10 pF | **0.78** (0) | **0.87** (0) |

Rules for the test plan: uncompensated external capacitance at most about 5 pF; a best code of 0 means too much
external capacitance.

**Silicon analysis script:** `test/analyze_e4990.py` reads 32 E4990A exports, picks the code, reports the ±2.5° and
±3° bands and fits α and Cα. It is tested on synthetic rehearsal data (`test/example_data/`): it reproduces the
rehearsal's choices (code 10, 4.38 decades, α = 0.7133; code 12, 2.36 decades, α = 0.5002).

## Changes made

- `docs/info.md`, *How to test*, rewritten:
  - lift the demoboard pull-downs;
  - compensate at the header without the chip, and never take the open with the project deselected;
  - keep external capacitance at most about 5 pF;
  - segment sweep at 300/100 mVrms;
  - the best-code sanity check;
  - the expected measured result.
- New: `test/analyze_e4990.py` and `test/example_data/`.
- No design change. The single-branch sensitivity of α = 0.5 and the ripple-margin tail are recorded as known
  limitations.
