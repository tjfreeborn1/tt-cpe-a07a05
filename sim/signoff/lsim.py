"""Large-signal transient: as-built network + trim bank + pin model, Vdc + Vpk sin. Fundamental Z and current THD."""
import numpy as np, subprocess, sys, json, os
P='/home/claude/pdk/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice'
AB='/home/claude/foc/lay/asbuilt'
NET={'cpe_a07':11,'cpe_a05':14}          # trim code at 1.0 V (post-layout, tt, nominal pin)
FREQ=[200,2e3,2e4,2e5,1e6]
AMP=[0.01,0.05,0.1,0.2,0.3,0.5]           # Vrms
jobs=[(n,fr,a,vdc) for n in NET for fr in FREQ for a in AMP for vdc in (1.0,)]
jobs+=[(n,fr,a,vdc) for n in NET for fr in (2e3,2e5) for a in (0.01,0.1,0.3) for vdc in (0.7,1.2)]
part,np_=int(sys.argv[1]),int(sys.argv[2]); jobs=jobs[part::np_]
res={}
for n,fr,a,vdc in jobs:
    code=NET[n]; g=' '.join('vdd' if code>>i&1 else '0' for i in range(5))
    vpk=a*np.sqrt(2); T=1/fr; ncyc=12 if fr<1e3 else 20
    tstop=ncyc*T; dt=T/400
    tag=f"{n}_{fr:g}_{a:g}_{vdc:g}"
    b=[f'* {tag}',f'.lib {P} tt',f'.include {AB}/{n}.spice',f'.include {AB}/trimbank.spice','.temp 27','.option rshunt=1e12',
       'Vdd vdd 0 1.8',f'Vs src 0 dc {vdc} sin({vdc} {vpk} {fr:g} 0 0 0)','Rs src p 100','Ce p 0 6.5p',
       f'X1 p {n}',f'XB p {g} trimbank',
       '.control','option interp',f'tran {dt:g} {tstop:g} 0 {dt:g}',
       f'wrdata {tag}.dat i(Vs) v(p) v(XB.b0) v(XB.b1) v(XB.b2) v(XB.b3) v(XB.b4)','.endc','.end']
    open(f'{tag}.sp','w').write('\n'.join(b)+'\n')
    subprocess.run(['ngspice','-b',f'{tag}.sp'],capture_output=True)
    d=np.loadtxt(f'{tag}.dat'); t=d[:,0]; i=-d[:,1]; vp=d[:,3]; vb=d[:,5::2]
    m=t>=t[-1]-4*T; tt=t[m]
    def fit(x):
        A=np.column_stack([np.ones_like(tt)]+[fn(2*np.pi*k*fr*tt) for k in (1,2,3,4,5) for fn in (np.cos,np.sin)])
        c=np.linalg.lstsq(A,x[m],rcond=None)[0]; return c
    ci=fit(i); cv=fit(d[:,2]*0+ (vdc+vpk*np.sin(2*np.pi*fr*t)))  # source voltage (ideal)
    I1=ci[1]-1j*ci[2]; V1=cv[1]-1j*cv[2]
    Z=V1/I1; harm=[abs(ci[2*k-1]-1j*ci[2*k]) for k in (2,3,4,5)]
    thd=np.sqrt(sum(h*h for h in harm))/abs(I1)
    off=[k for k in range(5) if not code>>k&1]
    bmin=min(vb[m][:,k].min() for k in range(5)); bmax=max(vb[m][:,k].max() for k in range(5))
    res[tag]=dict(net=n,f=fr,vrms=a,vdc=vdc,Zmag=abs(Z),ph=float(np.degrees(np.angle(Z))),thd=thd,Idc=ci[0],bmin=bmin,bmax=bmax,vpmin=vp[m].min())
    print(tag,f"|Z| {abs(Z):.4g} ph {np.degrees(np.angle(Z)):.2f} THD {thd*100:.2f}% bank node min {bmin:.3f} max {bmax:.3f}",flush=True)
    os.remove(f'{tag}.dat')
json.dump(res,open(f'ls_{part}.json','w'),indent=1)
