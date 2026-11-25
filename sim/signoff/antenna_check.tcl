crashbackups stop
drc off
snap internal
gds read [file join [file dirname [file normalize [info script]]] .. .. gds tt_um_tjfreeborn1_cpe_a07a05.gds]
load tt_um_tjfreeborn1_cpe_a07a05
select top cell
expand
extract do local
extract no all
extract all
antennacheck
set n [feedback count]
puts "ANTFEEDBACK $n"
for {set i 1} {$i <= $n} {incr i} { feedback find $i; puts "FB $i box=[box values] why=[feedback why]" }
quit -noprompt
