#!/bin/bash
# usage: runmagic.sh dir script.tcl log  (cleans .mag/.ext first)
cd "$1" && rm -f *.mag *.ext && timeout ${TMO:-900} magic -dnull -noconsole -rcfile $PDK_ROOT/sky130A/libs.tech/magic/sky130A.magicrc "$2" </dev/null > "$3" 2>&1
