import subprocess, re
import os; P=os.path.join(os.environ.get('PDK_ROOT', '/usr/local/share/pdk'), 'sky130A', 'libs.tech', 'ngspice', 'sky130.lib.spice')
def run(lib,T,vb,ctrl):
    s=f"""* asw char
.lib {P} {lib}
.include asw_sub.spice
.temp {T}
Vd vdpwr 0 1.8
Va vapwr 0 3.3
Vc ctrl 0 {ctrl}
Vm mod 0 dc {vb} ac 0
Vb bus 0 dc {vb} ac 1
X1 mod bus ctrl vdpwr vapwr 0 asw
.control
op
let idcm = i(Vm)
let idcb = i(Vb)
echo DC $&idcm $&idcb
ac lin 1 1e6 1e6
let ron = real(-1/i(Vm))
let cbus = imag(i(Vb))/(2*pi*1e6)
echo AC $&ron $&cbus
.endc
.end
"""
    open('c.sp','w').write(s); r=subprocess.run(['ngspice','-b','c.sp'],capture_output=True,text=True)
    a=re.search(r'^DC (\S+) (\S+)',r.stdout,re.M); b=re.search(r'^AC (\S+) (\S+)',r.stdout,re.M)
    if not (a and b): print(r.stdout[-1500:]); raise SystemExit
    return [float(x) for x in a.groups()+b.groups()]
for lib in ('tt','ss','ff'):
  for T in (27,85):
    for vb in (0.5,1.0,1.5):
        im,ib,ron,cb=run(lib,T,vb,1.8); im0,ib0,_,cb0=run(lib,T,vb,0)
        print(f"{lib} {T:2d}C V {vb}: ON Ron {ron:6.0f} ohm, C(bus side, incl. through-switch) {cb*1e15:5.0f} fF, DC current mod/bus {im*1e12:+8.2f}/{ib*1e12:+8.2f} pA | OFF DC current bus {ib0*1e12:+8.2f} pA, C_bus {cb0*1e15:5.0f} fF")
