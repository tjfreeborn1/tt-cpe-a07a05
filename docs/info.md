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

Each element has a **5-bit on-chip trim bank** (0.3 pF steps, 0–9.3 pF) switched by NMOS transistors. The code is set
on `ui_in[4:0]` for `ua[0]` and on `uio_in[4:0]` for `ua[1]` (bit 0 = LSB). The bank compensates for the chip-to-chip
spread of the pin capacitance and process corners.

The DC bias applied by the impedance analyzer (0.7–1.5 V) changes the MOS-capacitor values and so tunes Cα by about 8 %.

Post-layout simulated performance (extracted layout, SKY130 models, 828 process/bias/temperature/pin cases,
best trim code per case):

| Pin | Phase within ±2.5° of target | Band |
|---|---|---|
| `ua[0]` α = 0.7 | 4.12 decades | 126 Hz – 1.68 MHz |
| `ua[1]` α = 0.5 | 2.12 decades | 1.9 kHz – 251 kHz |

![Layout](layout.png)

![Top-level schematic](schematic.png)

## How to test

You need an impedance analyzer with DC bias (designed around a Keysight E4990A, 20 Hz – 10 MHz).

1. Power the board and select this project. Set all of `ui_in[4:0]` and `uio_in[4:0]` low (code 0).
2. Connect the analyzer between `ua[0]` (or `ua[1]`) and ground with short leads, after open/short/load fixture
   compensation.
3. Apply 1.0 V DC bias (keep it between 0.7 V and 1.5 V, never above 1.5 V) and a 100 mVrms test signal
   (50 mVrms at 0.7 V bias). Apply bias only after the chip is powered and the project is selected.
   DC bias is required: the MOS capacitors need at least about 0.5 V on the pin, and with no bias the constant-phase
   band collapses to under one decade. Keep (bias − peak signal) above 0.5 V. At 1.0 V bias and 100 mVrms the
   simulated current distortion is 0.35 % and the impedance changes by less than 0.1 % compared with a 10 mVrms signal.
4. Calibrate the trim code: sweep codes 0–31 and keep the one with the flattest phase over the top of the band
   only (150 – 600 kHz for α = 0.7, 50 – 200 kHz for α = 0.5). The rest of the band is then an independent check.
5. Sweep 20 Hz – 10 MHz and fit α and Cα in the constant-phase band.
6. Repeat at 0.7 V and 1.5 V bias (recalibrating the code) to measure the Cα tuning.

## External hardware

An impedance analyzer with DC bias, such as the Keysight E4990A, and a short fixture from the analog pins to its
test port.
