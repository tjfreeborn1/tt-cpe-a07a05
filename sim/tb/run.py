import subprocess, os, numpy as np
PDKPATH=os.path.join(os.environ.get('PDK_ROOT','/usr/local/share/pdk'),os.environ.get('PDK','sky130A'))
res={}
for cA,cB in ((0,31),(21,10)):
    t=open('tb_top.spice').read().replace('PDKPATH',PDKPATH).replace('CODEA',str(cA)).replace('CODEB',str(cB)); open('t.spice','w').write(t)
    o=subprocess.run(['ngspice','-b','t.spice'],capture_output=True,text=True).stdout
    print(cA,cB,[l for l in o.splitlines() if '=' in l and l.split('=')[0].strip().startswith(('v(','i(')) or 'v(' in l])
    g="\n".join(f"V{n}{i} G{n}{i} 0 {1.8*((c>>i)&1)}" for n,c in (('A',cA),('B',cB)) for i in range(5))
    r=open('tb_ref.spice').read().replace('PDKPATH',PDKPATH).replace('GSRC',g); open('r.spice','w').write(r)
    subprocess.run(['ngspice','-b','r.spice'],capture_output=True)
    a=np.loadtxt('tbout'); b=np.loadtxt('refout'); f=a[:,0]
    for j,nm in ((1,'ua0'),(3,'ua1')):
        za=a[:,j]+1j*a[:,j+1]; zb=b[:,j]+1j*b[:,j+1]
        m=f<=1e6
        print(f"  {nm} (10 Hz-1 MHz): max |Z| diff {np.max(np.abs(np.abs(za[m])/np.abs(zb[m])-1))*100:.3f} %, max phase diff {np.max(np.abs(np.degrees(np.angle(za[m])-np.angle(zb[m])))):.3f} deg")
        print(f"  {nm} (to 100 MHz): max |Z| diff {np.max(np.abs(np.abs(za)/np.abs(zb)-1))*100:.4f} %, max phase diff {np.max(np.abs(np.degrees(np.angle(za)-np.angle(zb)))):.4f} deg; phase@1kHz {np.degrees(np.angle(za[f.searchsorted(1e3)])):.2f}")
