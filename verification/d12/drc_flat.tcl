crashbackups stop
gds read /home/claude/d12/chk/tt_um_tjfreeborn1_cpe_a07a05.gds
load tt_um_tjfreeborn1_cpe_a07a05
select top cell
flatten -nolabels flatchk
load flatchk
select top cell
drc euclidean on
drc style drc(full)
drc check
drc catchup
puts "FLATDRCTOTAL [drc listall count total]"
set n 0
foreach {why boxes} [drc listall why] { puts "FLATDRCERR [llength $boxes] $why"; incr n }
puts "FLATDRCTYPES $n"
quit -noprompt
