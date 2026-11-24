gds read ../../gds/tt_um_tjfreeborn1_cpe_a07a05.gds
load tt_um_tjfreeborn1_cpe_a07a05
select top cell
extract do capacitance
extract do coupling
extract do local
extract all
ext2spice hierarchy off
ext2spice cthresh 0.01
ext2spice format ngspice
ext2spice -o pex.spice
quit -noprompt
