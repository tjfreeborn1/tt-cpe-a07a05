"""v4b combined corners: one ngspice run per (lib, bias, temp) holding both networks and all six bank states."""
import os, numpy as np, subprocess, sys
P=os.path.join(os.environ.get('PDK_ROOT','/usr/local/share/pdk'),os.environ.get('PDK','sky130A'),'libs.tech','ngspice','sky130.lib.spice')
libs=['tt','ll','hh','hl','lh']+[f'{m}_{rc}' for m in ('ss','ff','sf','fs') for rc in ('hh','ll','hl','lh')]
cases=[(l,v,27) for l in libs for v in (0.7,1.0,1.5)]+[(l,1.0,T) for l in ('tt','hh','ll') for T in (0,70)]
part=int(sys.argv[1]); nparts=int(sys.argv[2]); cases=cases[part::nparts]
g=lambda on: " ".join(("vdd" if i==on else "0") for i in range(5))
out={}
for lib,vb,T in cases:
    body=f"""* v4b {lib} {vb} {T}
.lib {P} {lib}
.include netlists/cpe_a07.spice
.include netlists/cpe_a05.spice
.include netlists/trimbank.spice
.temp {T}
Vdd vdd 0 1.8
VA ta 0 dc {vb} ac 1
XA ta cpe_a07
VB tb 0 dc {vb} ac 1
XB tb cpe_a05
VK0 k0 0 dc {vb} ac 1
XK0 k0 {g(-1)} trimbank
"""+"".join(f"VK{i+1} k{i+1} 0 dc {vb} ac 1\nXK{i+1} k{i+1} {g(i)} trimbank\n" for i in range(5))+f"""
.control
set wr_singlescale
option numdgt=7
ac dec 40 10 100meg
wrdata zz{part}.dat real(-1/i(VA)) imag(-1/i(VA)) real(-1/i(VB)) imag(-1/i(VB)) real(-1/i(VK0)) imag(-1/i(VK0)) real(-1/i(VK1)) imag(-1/i(VK1)) real(-1/i(VK2)) imag(-1/i(VK2)) real(-1/i(VK3)) imag(-1/i(VK3)) real(-1/i(VK4)) imag(-1/i(VK4)) real(-1/i(VK5)) imag(-1/i(VK5))
.endc
.end
"""
    open(f'cc{part}.spice','w').write(body)
    subprocess.run(['ngspice','-b',f'cc{part}.spice'],capture_output=True)
    d=np.loadtxt(f'zz{part}.dat'); f=d[:,0]
    cols=d[:,1:]
    key=f"{lib}|{vb}|{T}"
    out[f"cpe_a07|{key}"]=cols[:,0]+1j*cols[:,1]; out[f"cpe_a05|{key}"]=cols[:,2]+1j*cols[:,3]
    out[f"bank_off|{key}"]=cols[:,4]+1j*cols[:,5]
    for i in range(5): out[f"bank_on{i}|{key}"]=cols[:,6+2*i]+1j*cols[:,7+2*i]
    print(lib,vb,T,flush=True)
out['f']=f; np.savez(f'zv_{part}.npz',**out)
