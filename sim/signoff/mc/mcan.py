import numpy as np, glob, json, sys
WIN={'cpe_a07':(1.5e5,6e5),'cpe_a05':(5e4,2e5)}
pins=[(Rs,Ce) for Rs in (35,100,300,500) for Ce in (4e-12,6.5e-12,9e-12)]
def run(o,f,lf):
    o=o.astype(np.int8); d=np.diff(np.concatenate(([0],o,[0]))); st=np.where(d==1)[0]; en=np.where(d==-1)[0]-1
    if not len(st): return 0,0,0
    L=lf[en]-lf[st]; j=np.argmax(L); return L[j],f[st[j]],f[en[j]]
def analyze(fn):
    d=np.load(fn); f=d['f']; s=2j*np.pi*f; lf=np.log10(f); res={}
    for net,a,t,zk in (('cpe_a07',0.7,'A','zA'),('cpe_a05',0.5,'B','zB')):
        Y0=1/d[zk]; yb=[np.nan_to_num(d[f'y{t}{i}']) for i in range(5)]
        Yc=[Y0+sum(yb[i] for i in range(5) if c>>i&1) for c in range(32)]
        w=(f>=WIN[net][0])&(f<=WIN[net][1]); rng=(f>=20)&(f<=10e6)
        r={}
        for Rs,Ce in pins:
            Z=[1/(s*Ce+1/(Rs+1/y)) for y in Yc]; err=[np.abs(np.degrees(np.angle(z))+90*a) for z in Z]
            cl=max(((run((e<=2.5)&rng,f,lf),c) for c,e in enumerate(err)),key=lambda x:x[0][0])
            cw=int(np.argmin([e[w].max() for e in err])); tw=run((err[cw]<=2.5)&rng,f,lf)
            r[(Rs,Ce)]=dict(cl=cl[0],clc=cl[1],tw=tw,twc=cw)
        n=r[(100,6.5e-12)]; z=1/(s*6.5e-12+1/(100+1/Yc[n['clc']])); sel=(f>=n['cl'][1])&(f<=n['cl'][2])
        p=np.polyfit(np.log10(2*np.pi*f[sel]),np.log10(np.abs(z[sel])),1)
        res[net]=dict(cl_nom=n['cl'][0],tw_nom=n['tw'][0],code_nom=n['clc'],twcode_nom=n['twc'],
                      cl_worst=min(v['cl'][0] for v in r.values()),tw_worst=min(v['tw'][0] for v in r.values()),
                      codes=[v['clc'] for v in r.values()],twcodes=[v['twc'] for v in r.values()],
                      lo=n['cl'][1],hi=n['cl'][2],alpha=-p[0],Ca=10**(-p[1]))
    return res
if __name__=='__main__':
    out={}
    for MOS in ('tt','ss','ff','sf','fs'):
        fs=sorted(glob.glob(f'out_{MOS}/s*.npz'))
        if not fs: continue
        R=[analyze(fn) for fn in fs]; out[MOS]=R
        for net in ('cpe_a07','cpe_a05'):
            def st(key):
                x=np.array([r[net][key] for r in R]); return f"{x.mean():.3f} ± {x.std():.3f} (min {x.min():.2f}, mean-3σ {x.mean()-3*x.std():.2f})"
            cod=np.array([c for r in R for c in r[net]['codes']]); tc=np.array([c for r in R for c in r[net]['twcodes']])
            print(f"{MOS} n={len(R)} {net}")
            for k in ('cl_nom','tw_nom','cl_worst','tw_worst','alpha'): print(f"   {k:9s}: {st(k)}")
            ca=np.array([r[net]['Ca'] for r in R])*1e9; print(f"   Ca nF.s^(a-1): {ca.mean():.3f} ± {ca.std():.3f} ({100*ca.std()/ca.mean():.1f} %)")
            print(f"   closed-loop codes {cod.min()}-{cod.max()} (edge<=1|>=30: {((cod<=1)|(cod>=30)).sum()}/{len(cod)}); top-window codes {tc.min()}-{tc.max()} (edge: {((tc<=1)|(tc>=30)).sum()}/{len(tc)})")
    json.dump({m:[{n:{k:(v if not isinstance(v,np.generic) else float(v)) for k,v in r[n].items()} for n in r} for r in R] for m,R in out.items()},open('mc_results.json','w'),indent=0,default=float)
