![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg)

# Fractional-order capacitors on Tiny Tapeout (SKY130)

Two passive constant-phase elements (CPEs) in a 2×2 analog tile, targeting the **TTSKY27a** shuttle.

| Pin | Function |
|---|---|
| `ua[0]` | α = 0.7 CPE (phase −63°) |
| `ua[1]` | α = 0.5 CPE (phase −45°) |
| `ui_in[4:0]` | 5-bit trim code for `ua[0]` (0.3 pF steps) |
| `uio_in[4:0]` | 5-bit trim code for `ua[1]` (0.3 pF steps) |

Top module: `tt_um_tjfreeborn1_cpe_a07a05`. Datasheet text: [docs/info.md](docs/info.md).

## Status

| Step | State |
|---|---|
| Design and simulation (v4b) | Done: 4.15 decades (α = 0.7) and 2.12 decades (α = 0.5) within ±2.5° over 828 corner/bias/temperature/pin cases |
| Model check with as-drawn netlists | Done: no change |
| Xschem schematic, netgen check against simulation | Done |
| Layout (Magic) | Next — `gds/` and `lef/` do not exist yet, so the `gds` workflow fails until then |
| DRC / LVS / extraction | Planned |
| Submission | Planned (TTSKY27a; workflow tags will move from `ttsky26d` to the TTSKY27a release) |

## Repository layout

```
info.yaml          Tiny Tapeout project settings (2x2 tile, 2 analog pins)
src/project.v      Verilog stub with the top-module ports (the circuit itself is in the GDS)
docs/info.md       Datasheet page (how it works, how to test)
xschem/            Schematics and symbols; gen_sch.py regenerates them from sim/netlists
netlist/sim/       Xschem simulation netlist of the top cell
netlist/lvs/       Xschem LVS netlist of the top cell (top level as .subckt)
sim/netlists/      As-drawn SPICE netlists of the two networks and the trim bank (source of truth)
sim/               Corner simulation and analysis scripts; sim/tb/ = top-level sanity testbench
gds/, lef/, mag/   Layout (to come)
```

## Reproducing

Requires the SKY130A PDK (open_pdks), ngspice, Xschem and Netgen.

```
export PDK_ROOT=/path/to/pdk PDK=sky130A
cd xschem && python3 gen_sch.py                       # regenerate schematics from sim/netlists
xschem -q -x -n -s -o ../netlist/sim --rcfile ./xschemrc tt_um_tjfreeborn1_cpe_a07a05.sch
xschem -q -x -n -s -o ../netlist/lvs --tcl 'set lvs_netlist 1; set top_subckt 1' --rcfile ./xschemrc tt_um_tjfreeborn1_cpe_a07a05.sch
cd ../sim && cp spiceinit .spiceinit
python3 csim.py 0 2 & python3 csim.py 1 2; wait        # 69 corner/bias/temperature runs
python3 vanalyze.py && python3 windowcal.py           # 828-case pin analysis, calibration comparison
cd tb && cp ../spiceinit .spiceinit && python3 run.py  # top-level sim vs reference netlists
```

The full design history (earlier versions, studies, Monte Carlo, design log) is kept in the project archive, and a
step-by-step tutorial describes every design decision.

## About Tiny Tapeout

[Tiny Tapeout](https://tinytapeout.com) is an educational project that makes it easier and cheaper than ever to get
digital and analog designs manufactured on a real chip. See the
[analog specs](https://tinytapeout.com/specs/analog/) for the analog pin path and its limits.
