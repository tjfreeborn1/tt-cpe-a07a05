import numpy as np, json, glob
D={}
for fn in sorted(glob.glob('zp_*.npz')):
    z=np.load(fn); D.update({k:z[k] for k in z.files})
f=D['f']; s=2j*np.pi*f; lf=np.log10(f); LSB=0.3e-12
cases=sorted({tuple(k.split('|')[1:]) for k in D if k.startswith('cpe_a07|')})
BC={}
def bank(net,key,c):
    if (net,key,c) not in BC:
        y=np.zeros_like(f,complex); tag='A' if net=='cpe_a07' else 'B'
        for i in range(5):
            if c>>i&1: y=y+1/D[f"bank{tag}{i}|{key}"]
        BC[(net,key,c)]=y
    return BC[(net,key,c)]
def run(o):
    o=o.astype(np.int8); d=np.diff(np.concatenate(([0],o,[0]))); st=np.where(d==1)[0]; en=np.where(d==-1)[0]-1
    if not len(st): return 0,0,0
    L=lf[en]-lf[st]; j=np.argmax(L); return L[j],f[st[j]],f[en[j]]
pins=[(Rs,Ce) for Rs in (35,100,300,500) for Ce in (4e-12,6.5e-12,9e-12)]
def zpin(net,key,c,Rs,Ce): return 1/(s*Ce+1/(Rs+1/(1/D[f"{net}|{key}"]+bank(net,key,c))))
res={}
for net,a in (('cpe_a07',0.7),('cpe_a05',0.5)):
    res[net]={}
    # open-loop targets per bias: best code at tt, Rs=100, Ce=6.5 pF -> target total external+bank C
    tgt={}
    for vb in ('0.7','1.0','1.5'):
        key=f"tt|{vb}|27"; best=(-1,)
        for c in range(32):
            r=run((np.abs(np.degrees(np.angle(zpin(net,key,c,100,6.5e-12)))+90*a)<=2.5)&(f>=20)&(f<=10e6))
            if r[0]>best[0]: best=(r[0],c)
        tgt[vb]=6.5e-12+best[1]*LSB
    for mode in ('closed','open'):
        for tol in (2.5,3.0):
            m=np.ones_like(f,bool); codes=[]; worst=(9,None)
            for (lib,vb,T) in cases:
                key=f"{lib}|{vb}|{T}"
                for Rs,Ce in pins:
                    if mode=='closed':
                        best=(-1,)
                        for c in range(32):
                            ok=(np.abs(np.degrees(np.angle(zpin(net,key,c,Rs,Ce)))+90*a)<=tol)&(f>=20)&(f<=10e6); r=run(ok)
                            if r[0]>best[0]: best=(r[0],c,ok)
                    else:
                        worst_ok=np.ones_like(f,bool)
                        for err in (-0.2e-12,0.2e-12):      # pin measured with +-0.2 pF error
                            c=int(np.clip(round((tgt[vb]-(Ce+err))/LSB),0,31))
                            worst_ok&=(np.abs(np.degrees(np.angle(zpin(net,key,c,Rs,Ce)))+90*a)<=tol)&(f>=20)&(f<=10e6)
                        r=run(worst_ok); best=(r[0],c,worst_ok)
                    m&=best[2]; codes.append(best[1])
                    if best[0]<worst[0]: worst=(best[0],(lib,vb,T,Rs,Ce,best[1]))
            r=run(m); codes=np.array(codes)
            res[net][f"{mode}|{tol}"]=dict(common=r,worst=worst,code_min=int(codes.min()),code_max=int(codes.max()),edge=int(((codes<=1)|(codes>=30)).sum()),n=len(codes))
            print(f"{net} {mode:6s} ±{tol}°: common {r[0]:.2f} dec {r[1]:.4g}-{r[2]:.4g} Hz | worst {worst[0]:.2f} at {worst[1]} | codes {codes.min()}-{codes.max()}, within 1 of edge {res[net][f'{mode}|{tol}']['edge']}/{len(codes)}",flush=True)
    # C_alpha tuning (tt, Rs 100, Ce 6.5 pF, closed-loop code), alpha fit from |Z| slope in the 1.0 V common band
    r10=res[net]['closed|2.5']['common']; sel=(f>=r10[1])&(f<=r10[2]); ca={}; al={}
    for vb in ('0.7','1.0','1.5'):
        key=f"tt|{vb}|27"; best=(-1,)
        for c in range(32):
            rr=run((np.abs(np.degrees(np.angle(zpin(net,key,c,100,6.5e-12)))+90*a)<=2.5)&(f>=20)&(f<=10e6))
            if rr[0]>best[0]: best=(rr[0],c)
        z=zpin(net,key,best[1],100,6.5e-12); p=np.polyfit(np.log10(2*np.pi*f[sel]),np.log10(np.abs(z[sel])),1)
        al[vb]=-p[0]; ca[vb]=float(10**(-p[1]))
    res[net]['alpha_fit']=al; res[net]['Calpha_fit']=ca
    print(f"   fitted alpha (|Z| slope): {al}; C_alpha [nF s^(a-1)]: { {k:round(v*1e9,3) for k,v in ca.items()} }")
json.dump(res,open('pex_results.json','w'),indent=1,default=str)
