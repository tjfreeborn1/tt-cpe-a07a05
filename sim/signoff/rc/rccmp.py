import numpy as np, glob
def load(p):
    D={}
    for fn in sorted(glob.glob(p)): z=np.load(fn); D.update({k:z[k] for k in z.files})
    return D
R=load('rc/zp_*.npz'); C=load('zp_*.npz'); H=load('hot/zp_*.npz')
f=R['f']; s=2j*np.pi*f; lf=np.log10(f)
def run(o):
    o=o.astype(np.int8); d=np.diff(np.concatenate(([0],o,[0]))); st=np.where(d==1)[0]; en=np.where(d==-1)[0]-1
    if not len(st): return 0,0,0
    L=lf[en]-lf[st]; j=np.argmax(L); return L[j],f[st[j]],f[en[j]]
def yb(D,net,key,c,ff):
    y=np.zeros(len(ff),complex); t='A' if net=='cpe_a07' else 'B'
    for i in range(5):
        if c>>i&1: y+=np.nan_to_num(1/D[f"bank{t}{i}|{key}"],nan=0,posinf=0,neginf=0)
    return y
def best(D,ff,net,a,key):
    ss=2j*np.pi*ff; l=np.log10(ff); b=(-1,)
    for c in range(32):
        z=1/(ss*6.5e-12+1/(100+1/(1/D[f"{net}|{key}"]+yb(D,net,key,c,ff))))
        ok=(np.abs(np.degrees(np.angle(z))+90*a)<=2.5)&(ff>=10)&(ff<=10e6)
        o=ok.astype(np.int8); d=np.diff(np.concatenate(([0],o,[0]))); st=np.where(d==1)[0]; en=np.where(d==-1)[0]-1
        if len(st):
            L=l[en]-l[st]; j=np.argmax(L); r=(L[j],ff[st[j]],ff[en[j]])
            if r[0]>b[0]: b=(r[0],c,r[1],r[2])
    return b
for key,ref,fr in (('tt|1.0|27',C,C['f']),('ff_ll|1.0|27',C,C['f']),('ss_hh|1.0|27',C,C['f']),('tt|1.0|125',H,H['f'])):
    for net,a in (('cpe_a07',0.7),('cpe_a05',0.5)):
        zr=R[f"{net}|{key}"]; zc=np.interp(lf,np.log10(fr),ref[f"{net}|{key}"].real)+1j*np.interp(lf,np.log10(fr),ref[f"{net}|{key}"].imag)
        m=(f>=20)&(f<=10e6)
        dm=100*np.max(np.abs(np.abs(zr[m])/np.abs(zc[m])-1)); dp=np.max(np.abs(np.degrees(np.angle(zr[m])-np.angle(zc[m]))))
        t='A' if net=='cpe_a07' else 'B'; i1=np.argmin(abs(f-3e5))
        db=[100*(abs(1/R[f'bank{t}{i}|{key}'][i1]) / abs(np.interp(np.log10(3e5),np.log10(fr),np.abs(1/ref[f'bank{t}{i}|{key}'])))-1) for i in range(5)]
        br=best(R,f,net,a,key); bc=best(ref,fr,net,a,key)
        print(f"{key:13s} {net}: max d|Z| {dm:.3f}%  max dphase {dp:.3f} deg | bank bits |Y| at 300k: "+' '.join(f'{x:+.2f}%' for x in db)+f" | band RC {br[0]:.2f} dec {br[2]:.4g}-{br[3]:.4g} code {br[1]} vs C-only {bc[0]:.2f} dec {bc[2]:.4g}-{bc[3]:.4g} code {bc[1]}")
