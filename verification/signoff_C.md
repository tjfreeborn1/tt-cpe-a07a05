# Sign-off checks C8–C10 (2026-11-24)

These checks ran on the submitted GDS (md5 `56774a0aaaf0854e4a37b15ef889f967`). Scripts are in
`sim/signoff/c/`.

## C8 Digital control path: PASS

- **Tie-offs:** all 24 outputs (`uo_out[7:0]`, `uio_out[7:0]`, `uio_oe[7:0]`) connect to the LO output of a
  `sky130_fd_sc_hd__conb_1` tie cell. Each tie cell is powered from VDPWR/VGND. `uio_oe = 0`, so the `uio` pins are
  inputs. This was checked in the LVS netlist extracted from the layout.
- **Unused inputs:** `ui_in[7:5]`, `uio_in[7:5]`, `ena`, `clk` and `rst_n` are not connected, which is allowed for
  inputs. `ua[7:2]` are not connected and not purchased.
- **Bit mapping:** `ui_in[k]` → `diode_2` + `buf_2` → `swA<k>` gate (α = 0.7 bank on `ua[0]`), and `uio_in[k]` →
  `swB<k>` gate (α = 0.5 bank on `ua[1]`), for k = 0–4.
  - Switch sizes: bit 0 is 2 × 1.5 µm, bit 1 2 × 3 µm, bit 2 2 × 6 µm, bit 3 4 × 6 µm and bit 4 8 × 6 µm, all at
    L = 0.15 µm.
  - The connection of each switch to its own capacitor bit is covered by the LVS match.
- **Gate drive** (extracted netlist, VDPWR = 1.62 V, corners tt/ss/ff at −40, 27 and 125 °C):
  - On: every switch gate reaches the full supply (1.620 V).
  - Off: the gate sits at 0.1 µV or less (1.9 µV in the worst case, ff at 125 °C).
  - The gate reaches 95 % of the supply 1.3–3 ns after the input edge.
  - Static supply current: 0.25 nA, or 29 nA at ff and 125 °C.
- **Switch on-resistance** (VGS = 1.62 V): at most 24 Ω for bit 4 and 400 Ω for bit 0 (ss, 125 °C).
  - The loss angle ωRC at 2 MHz is about 1.5 × 10⁻³ rad (0.09°) for every bit, because the switch width scales with
    the capacitance.
- **Unselected project:** when the project is not selected, the analog multiplexer disconnects the analog pins, so
  the trim state does not matter. When it is selected, the board drives every trim input; the datasheet tells the
  user to start at code 0.
- The Verilog stub (`src/project.v`) has no logic, as Tiny Tapeout expects for an analog project; the Tiny Tapeout
  pin check passes.

## C9 Coupling and crosstalk: PASS

AC analysis of the extracted netlist (with coupling capacitance), tt, 27 °C, 1.0 V bias, at trim codes 0 and 31.
Each figure is the worst error between 20 Hz and 10 MHz, relative to the current from a 100 mVrms test signal:

| Aggressor | Code 0 | Code 31 |
|---|---|---|
| 10 mV on VDPWR → `ua[0]` / `ua[1]` | −139 / −130 dB | −107 / −110 dB |
| All 10 trim inputs toggling at 1.8 V, at the test frequency | −111 / −109 dB | −160 / −161 dB |
| 100 mV on `ua[1]` → `ua[0]` | −54 dB (10 MHz) | −71 dB |

- The crosstalk between the two pins comes from about 3 fF of on-chip coupling (−67 dB at 2 MHz).
- The datasheet now says to leave the other pin idle while measuring.

## C10 Reliability: PASS (operating limits added to the datasheet)

- **Voltages:** the MOS capacitors are thin-oxide (1.8 V) devices with the gate on the pin, so the pin limit is
  (bias + peak) ≤ 1.8 V.
  - Off trim-bank nodes float. They pump to at most 1.19 V at 0.5 Vrms (A2), well inside the junction and oxide
    limits.
  - The MIM capacitors and the xhigh-poly resistors see at most the pin voltage.
  - Negative pin voltage: keep it above −0.3 V because of the junctions and ESD diodes. The recommended conditions
    keep the pin at 0.86 V or more.
- **Currents:** worst case is 1 Vrms (the E4990A maximum), 10 MHz, code 31, with a 35 Ω / 4 pF pin model.
  - Pin: 1.2 mA peak, carried on a 3.2 µm metal-4 strip. The Tiny Tapeout analog path is specified to 4 mA.
  - Bit 4 switch: 0.43 mA peak, shared over 8 fingers.
  - R5 (one 0.35 × 2.6 µm segment): 91 µA peak.
  - DC: at most 1.8 µA (through Rp of the α = 0.5 network).
  - These are orders of magnitude below typical aluminium electromigration limits. SkyWater's limit values could not
    be retrieved from a public source, so this conclusion is a margin argument, not a rule check.
- **Self-heating:** at 1 Vrms R5 dissipates about 64 µW. A one-dimensional thermal estimate gives at most about 20 K,
  which is about −3 % on R5 above 1 MHz. At the recommended 100 mVrms the heating is below 0.2 K.
- **Bias step:** when a 1 V bias is switched on, the inrush into about 15 pF is limited by the source and the pin
  path (at least 100 Ω). It lasts a few nanoseconds.
- **Latch-up:** rule LU.2 passed in the precheck (tap within 15 µm of every n-diffusion).
- **ESD:** the Tiny Tapeout pads provide it; there are no on-chip ESD devices in the design.
- The datasheet now has a "Safe operating limits" table.

> **Correction (2026-11-25):** 1 Vrms is no longer an allowed test level (see `signoff_D.md`, S1). The maximum is now the smaller of (1.8 V − bias) and (bias − 0.5 V) as a peak value: 0.35 Vrms at 1.0 V bias. The C10 current and self-heating figures above are worst-case abuse values.
