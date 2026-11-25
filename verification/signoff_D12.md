# Sign-off D12: the build artifact is the verified design (2026-11-25)

**Result: PASS.** The GDS Tiny Tapeout will receive is byte-identical to the verified file. Every physical check was
re-run on that exact file, taken straight from the commit.

## 1. The CI input is the verified file

- **Commit:** `9c898e3`, the GitHub `main` HEAD, built by the gds workflow run 45672345123: gds, precheck and viewer
  all succeeded.
- **The build step** (`tt-gds-action/custom_gds@ttsky26e`, commit `df73a1e`) copies `gds/<top>.gds` into
  `tt_submission/` with a plain `cp`. It also writes an OASIS copy with `strm2oas`, the LEF with `cp`, and the Verilog
  stub from `src/project.v`.
- **Git blob hashes:** the same locally and on GitHub at that commit.

| File | Blob hash |
|---|---|
| `gds/tt_um_tjfreeborn1_cpe_a07a05.gds` | `47112fc776ae333508eddcbba9a3e9a7e4dd20a2`; md5 `56774a0aaaf0854e4a37b15ef889f967`, the verified file |
| `lef/tt_um_tjfreeborn1_cpe_a07a05.lef` | `ed653ad6a1bc07a04a8c870214ce03e5b710ae04` |
| `info.yaml` | `df218175abcf439fc86127d05fdc0941c0bc8a7a` |

- **The artifact zip itself was not downloaded:** GitHub's artifact storage host is blocked by this workspace's
  network allowlist. The blob hashes and the plain `cp` above establish its GDS content instead.

## 2. The OASIS copy matches the GDS

The GDS was converted to OASIS locally (KLayout 0.28.16; CI uses 0.30.12) and XOR-compared layer by layer:
- 37 layers in each file, the same set;
- the same top cell;
- **0 XOR polygons.**

This shows the conversion is lossless for this layout. It does not reproduce CI's exact OASIS bytes.

## 3. Physical checks re-run on the committed GDS (md5 56774a0a…)

| Check | Result |
|---|---|
| Magic DRC, full rules, hierarchical | Top cell clean. The 80 per-subcell counts come from devices and standard cells checked on their own (no taps or context), as expected. |
| Magic DRC, full rules, **flattened** | **0 errors.** Positive control: an injected 0.05 µm met1 sliver is flagged. |
| Fresh extraction from the GDS + Netgen LVS against `netlist/lvs/` at that commit | **Circuits match uniquely**, no property errors. 91 devices and 90 nets after merging. `ua[2]` and `ua[3]` are unconnected, as intended. |
| Magic antennacheck | **0 violations.** One feedback entry: the known "could not determine device boundary" note on `diode_2` at (135.4, 219.8) µm, the same as in A1. |
| TT precheck, tt-support-tools `main` @ `21568ef` (current, includes the micro-tile changes) | **17/17 pass.** |

Note: a first precheck run with an empty `.v` failed the power-pin check, because the Verilog must contain
VGND/VDPWR. CI passes `src/project.v` (`verilog_path` in `gds.yaml`). Re-staged the same way, it passes. This was a
staging error in the local re-run, not a design issue.

## Freeze reference

From this point the design is identified by GDS blob `47112fc7…` (md5 `56774a0a…`). Any later commit that changes
this blob must repeat D12.
