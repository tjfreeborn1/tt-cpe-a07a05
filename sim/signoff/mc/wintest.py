# SUPERSEDED by mcsim2.py / mcan2.py (2026-11-25, after the independent review): this version reused mismatch
# seeds across MOS corners, excited both pins at once, did not check ngspice logs and zeroed NaN values.
# Kept unchanged as the record of what produced the 2026-11-24 results in signoff_B.md.
import numpy as np, glob, sys
exec(open('mcan.py').read().split("if __name__")[0])
MOS=sys.argv[1] if len(sys.argv)>1 else 'tt'
CAND={'cpe_a07':[(1.5e5,6e5,'max'),(1.5e5,1.5e6,'max'),(1.5e5,2e6,'max'),(3e5,2e6,'max'),(1.5e5,2e6,'rms'),(5e4,2e6,'max'),('band',)],
      'cpe_a05':[(5e4,2e5,'max'),(5e4,3e5,'max'),(3e4,3e5,'max'),(5e4,3e5,'rms'),(2e4,3e5,'max'),('band',)]}
fs=sorted(glob.glob(f'out_{MOS}/s*.npz')); acc={(n,i):[] for n in CAND for i in range(len(CAND[n]))}
for fn in fs:
    d=np.load(fn); f=d['f']; s=2j*np.pi*f; lf=np.log10(f); rng=(f>=20)&(f<=10e6)
    for net,a,t,zk in (('cpe_a07',0.7,'A','zA'),('cpe_a05',0.5,'B','zB')):
        Y0=1/d[zk]; yb=[np.nan_to_num(d[f'y{t}{i}']) for i in range(5)]
        Yc=[Y0+sum(yb[i] for i in range(5) if c>>i&1) for c in range(32)]
        for Rs,Ce in pins:
            sgn=[np.degrees(np.angle(1/(s*Ce+1/(Rs+1/y))))+90*a for y in Yc]; err=[np.abs(e) for e in sgn]
            b=[run((e<=2.5)&rng,f,lf)[0] for e in err]
            for i,cd in enumerate(CAND[net]):
                if cd[0]=='band': c=int(np.argmax(b))
                else:
                    w=(f>=cd[0])&(f<=cd[1]); c=int(np.argmin([(e[w].max() if cd[2]=='max' else np.sqrt(np.mean(e[w]**2))) for e in err]))
                acc[(net,i)].append(b[c])
print(MOS,len(fs),'samples x 12 pin models')
for net in CAND:
    for i,cd in enumerate(CAND[net]):
        x=np.array(acc[(net,i)]); print(f"  {net} {str(cd):28s} mean {x.mean():.3f} min {x.min():.3f} 1st pct {np.percentile(x,1):.3f} frac<{3.5 if net=='cpe_a07' else 1.8}: {np.mean(x<(3.5 if net=='cpe_a07' else 1.8))*100:.2f}%")
