set pdk $env(PDK_ROOT)/sky130A
set lay [readnet spice ../layout_build/tt_um_tjfreeborn1_cpe_a07a05_lvs.spice]
set sch [readnet spice $pdk/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice]
readnet spice ../netlist/lvs/tt_um_tjfreeborn1_cpe_a07a05.spice $sch
lvs "$lay tt_um_tjfreeborn1_cpe_a07a05" "$sch tt_um_tjfreeborn1_cpe_a07a05" $pdk/libs.tech/netgen/sky130A_setup.tcl lvs.out -json
