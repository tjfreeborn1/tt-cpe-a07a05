import numpy as np, subprocess
import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)) if _o.path.basename(_o.path.dirname(_o.path.abspath(__file__)))=='signoff' else _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), '..'))
from common import run_ngspice, fresh, bank_y, LIB, PDK_NG, PEX, ASBUILT, GDS, REPO
P=PDK_NG  # from PDK_ROOT (common.py)
def sim(code,src):
    g=['vdd' if code>>i&1 else 'gnd0' for i in range(5)]
    ac={'sig':('ac 1','ac 0','ac 0','ac 0'),'vdd':('ac 0','ac 0','ac 1','ac 0'),'gate':('ac 0','ac 0','ac 0','ac 1'),'xt':('ac 0','ac 1','ac 0','ac 0')}[src]
    # gate inputs: driven through sources tied to vdd/0 with an AC term
    b=['* coupling',f'.lib {P}/sky130.lib.spice tt',f'.include {PEX}','.temp 27','.option rshunt=1e12',
       f'Vdd vdd 0 dc 1.8 {ac[2]}',f'VA a 0 dc 1.0 {ac[0]}',f'VB b 0 dc 1.0 {ac[1]}']
    pins=[]
    for i in range(5):
        lvl=1.8 if code>>i&1 else 0
        b.append(f'VGa{i} ga{i} 0 dc {lvl} {ac[3]}'); b.append(f'VGb{i} gb{i} 0 dc {lvl} {ac[3]}')
    b+=['X1 a b '+' '.join(f'ga{i}' for i in range(5))+' '+' '.join(f'gb{i}' for i in range(5))+' vdd 0 toppex',
        '.control','set wr_singlescale','option numdgt=7','ac dec 20 10 10meg',
        'wrdata c.dat real(i(VA)) imag(i(VA)) real(i(VB)) imag(i(VB))','.endc','.end']
    open('c.sp','w').write('\n'.join(b)+'\n'); fresh('c.dat'); run_ngspice('c.sp')
    d=np.loadtxt('c.dat'); return d[:,0], d[:,1]+1j*d[:,2], d[:,3]+1j*d[:,4]
res={}
for code in (0,31):
    f,ia,ib=sim(code,'sig'); res[(code,'sig')]=(ia,ib)
    for src in ('vdd','gate','xt'):
        f,ja,jb=sim(code,src); res[(code,src)]=(ja,jb)
np.savez('coup.npz',f=f,**{f'{c}_{s}_{k}':v[i] for (c,s),v in res.items() for i,k in enumerate('ab')})
print('Transadmittance into each pin (|i| per 1 V of aggressor) relative to the pin\'s own |Y| at 1 V, in dB; error for 10 mV aggressor vs 100 mV test signal in %')
for code in (0,31):
    for fq in (100,1e3,1e4,1e5,1e6,2e6,1e7):
        i=np.argmin(abs(f-fq)); line=f"code {code:2d} f {fq:>8g}:"
        for k,pin in ((0,'ua0'),(1,'ua1')):
            ys=abs(res[(code,'sig')][k][i]) if k==0 else None
        ya=abs(res[(code,'sig')][0][i]); yb_=abs(sim_b:=0) if False else None
        out=[]
        for src in ('vdd','gate'):
            for k,pin in ((0,'ua0'),(1,'ua1')):
                yself=abs(res[(code,'sig')][0][i]) if k==0 else None
                out.append((src,pin,abs(res[(code,src)][k][i])))
        print(line, ' '.join(f"{s}->{p}:{v:.3g}S" for s,p,v in out), f"| Y_ua0 {ya:.3g}S | ua1->ua0 {abs(res[(code,'xt')][0][i]):.3g}S")
