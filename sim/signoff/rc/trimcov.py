import numpy as np
exec(open('pexanalyze.py').read().split("res={}")[0])
out={}
for net,a,t in (('cpe_a07',0.7,'A'),('cpe_a05',0.5,'B')):
    i3=np.argmin(abs(f-3e5)); w=2*np.pi*f[i3]
    # (a) monotonicity / DNL of bank capacitance at 300 kHz, all 69 lib/bias/temp cases
    worst_dnl=(9,None); lsb=[]
    for (lib,vb,T) in cases:
        key=f"{lib}|{vb}|{T}"
        C=np.array([np.imag(bank(net,key,c)[i3])/w for c in range(32)])
        st=np.diff(C); L=(C[31]-C[0])/31; lsb.append(L); dnl=st/L-1
        if dnl.min()<worst_dnl[0]: worst_dnl=(dnl.min(),key,int(np.argmin(dnl)))
    lsb=np.array(lsb)
    print(f"{net}: bank LSB at 300 kHz {lsb.min()*1e12:.3f}-{lsb.max()*1e12:.3f} pF, full scale {31*lsb.min()*1e12:.2f}-{31*lsb.max()*1e12:.2f} pF; worst DNL {worst_dnl[0]:+.3f} LSB at {worst_dnl[1]} step {worst_dnl[2]}->{worst_dnl[2]+1} (monotonic if > -1)")
    # (b,c) per case: best code, band at best, best-1, best+1, and band with virtual negative codes
    loss_edge=[]; sens=[]; pinned=0; N=0
    for (lib,vb,T) in cases:
        key=f"{lib}|{vb}|{T}"
        yb=[bank(net,key,c) for c in range(32)]; lsby=(yb[31]-yb[0])/31
        for Rs,Ce in pins:
            N+=1
            def band(y):
                z=1/(s*Ce+1/(Rs+1/(1/D[f"{net}|{key}"]+y)))
                return run((np.abs(np.degrees(np.angle(z))+90*a)<=2.5)&(f>=20)&(f<=10e6))[0]
            b=[band(y) for y in yb]; c=int(np.argmax(b))
            nb=[b[c-1] if c>0 else np.nan, b[c+1] if c<31 else np.nan]; sens.append(b[c]-np.nanmin(nb))
            if c<=1 or c>=30:
                pinned+=1
                virt=[band(yb[0]+k*lsby) for k in range(-6,0)] if c<=1 else [band(yb[31]+k*lsby) for k in range(1,7)]
                loss_edge.append(max(max(virt)-b[c],0))
    sens=np.array(sens)
    print(f"   cases {N}: best code within 1 of an edge in {pinned}; band lost to the edge (vs. unlimited range): max {max(loss_edge) if loss_edge else 0:.3f} dec, mean {np.mean(loss_edge) if loss_edge else 0:.3f}")
    print(f"   band lost if the code is off by 1 LSB: median {np.median(sens):.3f} dec, 95th pct {np.percentile(sens,95):.3f}, max {sens.max():.3f}")
