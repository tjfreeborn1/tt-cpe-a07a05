crashbackups stop
drc off
load anttest
box 0um 0um 1um 0.42um
paint ndiff
box 0.43um -0.3um 0.58um 0.9um
paint poly
box 0.3um 0.9um 0.7um 1.4um
paint poly
box 0.42um 1.07um 0.59um 1.24um
paint pc
box 0.3um 0.95um 0.7um 1.35um
paint li
box 0.42um 1.07um 0.59um 1.24um
paint mcon
box 0.3um 0.95um 300um 1.4um
paint m1
select top cell
extract do local
extract no all
extract all
antennacheck
set n [feedback count]
puts "ANTFEEDBACK $n"
for {set i 1} {$i <= $n} {incr i} { feedback find $i; puts "FB $i box=[box values]" }
quit -noprompt
