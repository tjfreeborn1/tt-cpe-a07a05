import numpy as np
exec(open('vanalyze.py').read().split("res={}")[0])
WIN={'cpe_a07':(3e5,1.2e6),'cpe_a05':(6e4,2.2e5)}
for net,a in (('cpe_a07',0.7),('cpe_a05',0.5)):
    w=(f>=WIN[net][0])&(f<=WIN[net][1])
    for tol in (2.5,3.0):
        m=np.ones_like(f,bool); worst=(9,None)
        for (lib,vb,T) in cases:
            key=f"{lib}|{vb}|{T}"
            for Rs,Ce in pins:
                errs=[np.max(np.abs(np.degrees(np.angle(zpin(net,key,c,Rs,Ce)[w]))+90*a)) for c in range(32)]
                c=int(np.argmin(errs)); ok=(np.abs(np.degrees(np.angle(zpin(net,key,c,Rs,Ce)))+90*a)<=tol)&(f>=20)&(f<=10e6)
                m&=ok; r=run(ok)
                if r[0]<worst[0]: worst=(r[0],(lib,vb,T,Rs,Ce,c))
        r=run(m); held=(f>=r[1])&(f<=r[2])&~w
        print(f"{net} window-calibrated ±{tol}°: common {r[0]:.2f} dec {r[1]:.4g}-{r[2]:.4g} Hz | of which outside the calibration window: {np.log10(min(r[2],WIN[net][0])/r[1]) if r[1]<WIN[net][0] else 0:.2f} dec | worst single {worst[0]:.2f} at {worst[1]}")
