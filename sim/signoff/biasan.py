import numpy as np, glob, json
D={}
for fn in sorted(glob.glob('zp_*.npz'))+sorted(glob.glob('bias/zp_*.npz')):
    z=np.load(fn); D.update({k:z[k] for k in z.files})
f=D['f']; s=2j*np.pi*f; lf=np.log10(f)
def bank(net,key,c):
    y=np.zeros_like(f,complex); tag='A' if net=='cpe_a07' else 'B'
    for i in range(5):
        if c>>i&1: y=y+1/D[f"bank{tag}{i}|{key}"]
    return y
def run(o):
    o=o.astype(np.int8); d=np.diff(np.concatenate(([0],o,[0]))); st=np.where(d==1)[0]; en=np.where(d==-1)[0]-1
    if not len(st): return 0,0,0
    L=lf[en]-lf[st]; j=np.argmax(L); return L[j],f[st[j]],f[en[j]]
def zpin(net,key,c,Rs,Ce): return 1/(s*Ce+1/(Rs+1/(1/D[f"{net}|{key}"]+bank(net,key,c))))
pins=[(Rs,Ce) for Rs in (35,100,300,500) for Ce in (4e-12,6.5e-12,9e-12)]
out={}
for net,a in (('cpe_a07',0.7),('cpe_a05',0.5)):
    print(net)
    for vb in ('0.0','0.2','0.4','0.5','0.6','0.7','0.8','1.0','1.2','1.5','1.8'):
        key=f"tt|{vb}|27"
        # nominal pin, best code
        best=(-1,)
        for c in range(32):
            r=run((np.abs(np.degrees(np.angle(zpin(net,key,c,100,6.5e-12)))+90*a)<=2.5)&(f>=20)&(f<=10e6))
            if r[0]>best[0]: best=(r[0],c,r)
        # worst over pin models (each re-trimmed)
        wr=9
        for Rs,Ce in pins:
            b2=max(run((np.abs(np.degrees(np.angle(zpin(net,key,c,Rs,Ce)))+90*a)<=2.5)&(f>=20)&(f<=10e6))[0] for c in range(32))
            wr=min(wr,b2)
        r=best[2]; sel=(f>=r[1])&(f<=r[2]); z=zpin(net,key,best[1],100,6.5e-12)
        p=np.polyfit(np.log10(2*np.pi*f[sel]),np.log10(np.abs(z[sel])),1)
        # Z at 1 kHz with code fixed at 1.0 V optimum, to show drift if not re-trimmed
        i1k=np.argmin(abs(f-1e3)); i100k=np.argmin(abs(f-1e5))
        out[f"{net}|{vb}"]=dict(dec=r[0],lo=r[1],hi=r[2],code=best[1],worst_pin=wr,alpha=-p[0],Ca_nF=10**(-p[1])*1e9,Z1k=abs(z[i1k]),ph1k=np.degrees(np.angle(z[i1k])),Z100k=abs(z[i100k]))
        o=out[f"{net}|{vb}"]
        print(f"  Vdc {vb}: {o['dec']:.2f} dec ({o['lo']:.3g}-{o['hi']:.3g} Hz) code {o['code']:2d} | worst pin {wr:.2f} dec | alpha {o['alpha']:.3f} Ca {o['Ca_nF']:.2f} | |Z|1k {o['Z1k']/1e3:.1f}k ph {o['ph1k']:.1f} | |Z|100k {o['Z100k']/1e3:.2f}k")
json.dump(out,open('bias/bias_results.json','w'),indent=1)
