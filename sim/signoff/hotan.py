import numpy as np, glob, json
def load(pat):
    D={}
    for fn in sorted(glob.glob(pat)):
        z=np.load(fn); D.update({k:z[k] for k in z.files})
    return D
H=load('hot/zp_*.npz'); C=load('zp_*.npz')
def mk(D):
    f=D['f']; s=2j*np.pi*f; lf=np.log10(f)
    def yb(net,key,c):
        y=np.zeros_like(f,complex); tag='A' if net=='cpe_a07' else 'B'
        for i in range(5):
            if c>>i&1:
                yy=1/D[f"bank{tag}{i}|{key}"]; y=y+np.nan_to_num(yy,nan=0,posinf=0,neginf=0)
        return y
    def run(o):
        o=o.astype(np.int8); d=np.diff(np.concatenate(([0],o,[0]))); st=np.where(d==1)[0]; en=np.where(d==-1)[0]-1
        if not len(st): return 0,0,0
        L=lf[en]-lf[st]; j=np.argmax(L); return L[j],f[st[j]],f[en[j]]
    def best(net,a,key,Rs=100,Ce=6.5e-12,fmin=10):
        b=(-1,)
        for c in range(32):
            z=1/(s*Ce+1/(Rs+1/(1/D[f"{net}|{key}"]+yb(net,key,c))))
            r=run((np.abs(np.degrees(np.angle(z))+90*a)<=2.5)&(f>=fmin)&(f<=10e6))
            if r[0]>b[0]: b=(r[0],c,r[1],r[2],z)
        return b
    return f,best
fh,bh=mk(H); fc,bc=mk(C)
out={}
for net,a in (('cpe_a07',0.7),('cpe_a05',0.5)):
    print(net)
    for lib in ('tt','ff_ll','ff_hh','ff_lh','ff_hl','fs_hh','sf_ll','ss_hh'):
        r27=bc(net,a,f"{lib}|1.0|27")
        line=f"  {lib:6s} 27C: {r27[0]:.2f} dec {r27[2]:.4g}-{r27[3]:.4g} Hz (code {r27[1]})"
        for T in (85,125):
            r=bh(net,a,f"{lib}|1.0|{T}",fmin=1)
            # phase at 100 Hz, 20 Hz
            i100=np.argmin(abs(fh-100)); i20=np.argmin(abs(fh-20))
            ph=np.degrees(np.angle(r[4]))
            line+=f" | {T}C: {r[0]:.2f} dec {r[2]:.4g}-{r[3]:.4g} (code {r[1]}) ph@100Hz {ph[i100]:.2f}"
            out[f"{net}|{lib}|{T}"]=dict(dec=r[0],lo=r[2],hi=r[3],code=r[1],ph100=ph[i100])
        print(line)
    for lib in ('tt','ff_ll'):
        r=bh(net,a,f"{lib}|0.7|85",fmin=1); print(f"  {lib} 0.7V 85C: {r[0]:.2f} dec {r[2]:.4g}-{r[3]:.4g}")
json.dump(out,open('hot/hot_results.json','w'),indent=1)
