<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project contains two passive **fractional-order capacitors** (constant-phase elements, CPEs). An ideal CPE has
impedance Z = 1 / ((jω)^α · Cα): its phase stays at −90·α degrees at every frequency, between a resistor (α = 0)
and a capacitor (α = 1).

- `ua[0]`: α = 0.7 element, target phase −63°.
- `ua[1]`: α = 0.5 element, target phase −45°.

Each element is a Morrison–Valsa RC network (parallel series-RC branches plus a parallel resistor) built from
SKY130 xhigh-poly resistors and stacked MOS + MIM capacitors, about 200 pF per network. The network was optimized
together with the Tiny Tapeout analog pin path (series resistance and pin capacitance), so that the pin capacitance
acts as part of the network.

Each element has a **5-bit on-chip trim bank** switched by NMOS transistors. The drawn steps are 0.3 pF (0–9.3 pF); the
extracted layout gives about 0.34 pF steps (0–9.5 pF) because of coupling to the top plate. The code is set
on `ui_in[4:0]` for `ua[0]` and on `uio_in[4:0]` for `ua[1]` (bit 0 = LSB). The bank compensates for the chip-to-chip
spread of the pin capacitance and process corners.

The DC bias applied by the impedance analyzer (0.7–1.5 V) changes the MOS-capacitor values and so tunes Cα by about 8 %.

Post-layout simulated performance (extracted layout, SKY130 models, phase within ±2.5° of the target, best trim
code per chip):

| Pin | Per chip, Monte Carlo: typical / 3σ limit / worst | Band shared by all 828 corner cases | Fitted α | Cα (1.0 V, typical, ±1σ) |
|---|---|---|---|---|
| `ua[0]` α = 0.7 | 4.31 / 4.23 / 4.25 decades | 4.12 decades, 126 Hz – 1.68 MHz | 0.713 | 1.66 nF·s^-0.3 ± 1.2 % |
| `ua[1]` α = 0.5 | 2.31 / 2.24 / 2.25 decades | 2.12 decades, 1.9 kHz – 251 kHz | 0.500 | 30.0 nF·s^-0.5 ± 2.5 % |

The Monte Carlo covers 400 samples: 200 at the typical MOS corner and 50 at each of ss/ff/sf/fs. Each sample has
device mismatch plus global resistor and MIM variation, and was evaluated with all 12 pin-path models. Results with
and without the wiring resistance agree to 0.03 decades.

![Layout](layout.png)

![Top-level schematic](schematic.png)

## How to test

You need an impedance analyzer with DC bias (designed around a Keysight E4990A, 20 Hz – 10 MHz).

1. Power the board and select this project. Set all of `ui_in[4:0]` and `uio_in[4:0]` low (code 0).
2. Connect the analyzer between `ua[0]` (or `ua[1]`) and ground with short leads, after open/short/load fixture
   compensation.
3. **Set the test-signal level before connecting.** The E4990A defaults to 500 mVrms, which is too large. Use
   100 mVrms (50 mVrms at 0.7 V bias). Then apply 1.0 V DC bias, kept between 0.7 V and 1.5 V. Apply the bias only
   after the chip is powered and the project is selected.
   - DC bias is required: the MOS capacitors need at least about 0.5 V on the pin. With no bias the constant-phase
     band collapses to under one decade.
   - Keep (bias − peak signal) ≥ 0.5 V and (bias + peak signal) ≤ 1.8 V. At 1.0 V bias that allows at most
     0.35 Vrms.
   - At 1.0 V bias and 100 mVrms, the simulated current distortion is 0.3–0.4 % at 1–2 kHz. The impedance changes by
     less than 0.1 % compared with a 10 mVrms signal.
4. Calibrate the trim code: measure the phase from 20 Hz to 10 MHz for each code 0–31 and keep the code with the
   widest continuous band within ±2.5° of −90α°. This takes 32 sweeps, about 10 minutes per pin.
   - The ±2.5° figure is a cliff. The simulated in-band phase ripple is about ±2.2°, so being one code off costs
     0.3–0.4 decades. Analyzer phase accuracy and fixture-compensation residue therefore matter.
   - Report the ±3° band as well.
   The quicker shortcut of picking the flattest phase over only the top of the band (150 – 600 kHz for α = 0.7,
   50 – 200 kHz for α = 0.5) is not recommended. In simulation it picks a code one to three steps off for about 1 % of
   chips, mostly when the pin resistance is high and the pin capacitance small, and that can cut the α = 0.7 band to
   about 2.2 decades.
5. Sweep 20 Hz – 10 MHz and fit α and Cα in the constant-phase band. Leave the other analog pin unconnected or
   idle while measuring. The on-chip crosstalk between `ua[0]` and `ua[1]` is −54 dB at 10 MHz; package and
   board coupling will be larger.
6. Repeat at 0.7 V and 1.5 V bias (recalibrating the code) to measure the Cα tuning.

### Safe operating limits

| Quantity | Limit | Why |
|---|---|---|
| Pin voltage, bias + peak signal | ≤ 1.8 V | The MOS capacitors are 1.8 V thin-oxide devices, with the gate on the pin. |
| Pin voltage, bias − peak signal | ≥ 0.5 V for valid data; never below −0.3 V | MOS capacitor bias; forward-biased junctions and ESD diodes. |
| Test signal | 100 mVrms recommended. Maximum peak = the smaller of (1.8 V − bias) and (bias − 0.5 V): 0.35 Vrms at 1.0 V bias, 0.21 Vrms at 1.5 V, 0.14 Vrms at 0.7 V. | Larger signals overstress the 1.8 V devices or forward-bias junctions. For example, 1 Vrms at 1.0 V bias puts 2.4 V on the MOS-capacitor gates and gives 12–15 % distortion at 1 kHz. |
| VDPWR | 1.62 – 1.8 V | The trim switches were checked at 1.62 V. The gates swing fully, and on-resistance runs from about 15 Ω (bit 4) to 243 Ω (bit 0) at tt, 27 °C, or at most 24–400 Ω at ss, 125 °C. |
| Order | Power the chip and select the project before applying bias; remove the bias first. | The trim-switch gates are undefined while the chip is unpowered. |

## External hardware

An impedance analyzer with DC bias, such as the Keysight E4990A, and a short fixture from the analog pins to its
test port.
