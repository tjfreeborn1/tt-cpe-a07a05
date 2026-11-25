crashbackups stop
drc off
gds read /home/claude/d12/chk/tt_um_tjfreeborn1_cpe_a07a05.gds
load tt_um_tjfreeborn1_cpe_a07a05
select top cell
extract do local
extract no all
extract all
ext2spice lvs
ext2spice -o tt_um_tjfreeborn1_cpe_a07a05_lvs.spice
antennacheck
puts "ANTFEEDBACK [feedback count]"
quit -noprompt
