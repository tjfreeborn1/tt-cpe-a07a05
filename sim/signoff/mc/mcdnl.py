import numpy as np, glob
for MOS in ('tt','ss','ff','sf','fs'):
    fs=sorted(glob.glob(f'out_{MOS}/s*.npz'))
    if not fs: continue
    w=[];lsb=[];fsc=[]
    for fn in fs:
        d=np.load(fn); f=d['f']; i=np.argmin(abs(f-3e5)); om=2*np.pi*f[i]
        for t in 'AB':
            cb=np.array([np.imag(d[f'y{t}{b}'][i])/om for b in range(5)])
            C=np.array([sum(cb[b] for b in range(5) if c>>b&1) for c in range(32)])
            L=(C[31]-C[0])/31; dnl=np.diff(C)/L-1; w.append(dnl.min()); lsb.append(L); fsc.append(C[31])
    w=np.array(w); lsb=np.array(lsb)
    print(f"{MOS}: {len(fs)} samples x 2 banks: worst DNL {w.min():+.3f} LSB (mean of worst {w.mean():+.3f}); LSB {lsb.min()*1e12:.3f}-{lsb.max()*1e12:.3f} pF; full scale {min(fsc)*1e12:.2f}-{max(fsc)*1e12:.2f} pF")
