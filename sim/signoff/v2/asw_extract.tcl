crashbackups stop
drc off
gds read /home/claude/v3/tt-multiplexer/asw/sky130/tt_asw_3v3/gds/tt_asw_3v3.gds
load tt_asw_3v3
select top cell
extract do capacitance
extract do coupling
extract all
ext2spice hierarchy off
ext2spice cthresh 0.01
ext2spice format ngspice
ext2spice -o asw.spice
quit -noprompt
