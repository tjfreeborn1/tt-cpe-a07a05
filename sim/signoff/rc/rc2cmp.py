import numpy as np, glob, json
def load(p):
    D={}
    for fn in sorted(glob.glob(p)): z=np.load(fn); D.update({k:z[k] for k in z.files})
    return D
R=load('rc2/zp_*.npz'); C=load('zp_*.npz'); f=R['f']; assert np.allclose(f,C['f'])
s=2j*np.pi*f; lf=np.log10(f); WIN={'cpe_a07':(1.5e5,6e5),'cpe_a05':(5e4,2e5)}
pins=[(Rs,Ce) for Rs in (35,100,300,500) for Ce in (4e-12,6.5e-12,9e-12)]
def run(o):
    o=o.astype(np.int8); d=np.diff(np.concatenate(([0],o,[0]))); st=np.where(d==1)[0]; en=np.where(d==-1)[0]-1
    if not len(st): return 0,0,0
    L=lf[en]-lf[st]; j=np.argmax(L); return L[j],f[st[j]],f[en[j]]
def ev(D,net,a,key):
    t='A' if net=='cpe_a07' else 'B'; yb=[np.nan_to_num(1/D[f"bank{t}{i}|{key}"],nan=0,posinf=0,neginf=0) for i in range(5)]
    Y=[1/D[f"{net}|{key}"]+sum(yb[i] for i in range(5) if c>>i&1) for c in range(32)]
    w=(f>=WIN[net][0])&(f<=WIN[net][1]); rng=(f>=20)&(f<=10e6); cl=[];tw=[]
    mcl=np.ones_like(f,bool); mtw=np.ones_like(f,bool)
    for Rs,Ce in pins:
        err=[np.abs(np.degrees(np.angle(1/(s*Ce+1/(Rs+1/y)))) +0*Ce + 90*a) for y in Y]
        err=[np.abs(np.degrees(np.angle(1/(s*Ce+1/(Rs+1/y))))+90*a) for y in Y]
        ok=[(e<=2.5)&rng for e in err]; b=[run(o)[0] for o in ok]; c=int(np.argmax(b)); cl.append(b[c]); mcl&=ok[c]
        cw=int(np.argmin([e[w].max() for e in err])); tw.append(b[cw]); mtw&=ok[cw]
    return min(cl),min(tw),run(mcl),run(mtw)
keys=sorted({k.split('|',1)[1] for k in R if k.startswith('cpe_a07|')})
res={}
for net,a in (('cpe_a07',0.7),('cpe_a05',0.5)):
    print(net, '   case            | RC: worst closed / worst top-window | C-only: same')
    allr=[];allc=[]
    for key in keys:
        r=ev(R,net,a,key); c=ev(C,net,a,key); allr.append(r); allc.append(c)
        print(f"   {key:14s} | {r[0]:.2f} / {r[1]:.2f} (common {r[2][0]:.2f}/{r[3][0]:.2f}) | {c[0]:.2f} / {c[1]:.2f} (common {c[2][0]:.2f}/{c[3][0]:.2f})")
    res[net]=dict(rc=[list(map(lambda x: x if not isinstance(x,tuple) else list(x),r)) for r in allr],c=[list(map(lambda x: x if not isinstance(x,tuple) else list(x),c)) for c in allc],keys=keys)
json.dump(res,open('rc2/rc2_results.json','w'),indent=0,default=float)
