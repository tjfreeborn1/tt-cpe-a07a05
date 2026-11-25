crashbackups stop
drc off
gds read [file join [file dirname [file normalize [info script]]] .. .. .. gds tt_um_tjfreeborn1_cpe_a07a05.gds]
load tt_um_tjfreeborn1_cpe_a07a05
select top cell
extract do capacitance
extract do coupling
extract do resistance
extract do local
extract all
ext2sim labels on
ext2sim
extresist tolerance 10
extresist all
ext2spice hierarchy off
ext2spice cthresh 0.01
ext2spice extresist on
ext2spice format ngspice
ext2spice -o rcx.spice
quit -noprompt
