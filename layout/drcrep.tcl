proc drcrep {{nmax 3}} {
  select top cell; drc euclidean on; drc style drc(full); drc check; drc catchup
  set sc [cif scale out]
  puts "DRCTOTAL [drc listall count total]"
  puts "DRCCOUNT [drc listall count]"
  foreach {why boxes} [drc listall why] {
    set s ""
    foreach b [lrange $boxes 0 [expr {$nmax-1}]] { append s [format " (%.3f %.3f %.3f %.3f)" [expr {[lindex $b 0]*$sc}] [expr {[lindex $b 1]*$sc}] [expr {[lindex $b 2]*$sc}] [expr {[lindex $b 3]*$sc}]] }
    puts [format "DRCERR %4d  %s  @%s" [llength $boxes] $why $s]
  }
}
