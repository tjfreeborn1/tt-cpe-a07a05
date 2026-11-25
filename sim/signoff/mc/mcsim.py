"""Monte Carlo on the extracted netlist: per-device mismatch (PDK mc_mm models, per instance) + Gaussian global
R (res_high_po__var_mult, used by the xhigh_po base model; sigma 5/3 = corner/3, i.e. 2.7 % on a 98 um segment) and MIM (camimc sigma 3.7 %, cpmimc sigma 0.053 fF/um) shifts.
MOS process = corner file given by MOS argument. One ngspice run per sample, 6 AC sweeps (code 0, each bit alone)."""
import numpy as np, subprocess, sys, os, re
P='/home/claude/pdk/share/pdk/sky130A/libs.tech/ngspice'
NET=os.path.abspath(sys.argv[4]) if len(sys.argv)>4 else '/home/claude/foc/lay/pex/top_pex.spice'
MOS=sys.argv[3]; k0,k1=int(sys.argv[1]),int(sys.argv[2])
lin=open(f'{P}/r+c/res_typical__cap_typical__lin.spice').read()
os.makedirs(f'out_{MOS}',exist_ok=True); os.makedirs('tmp',exist_ok=True)
for k in range(k0,k1):
    rng=np.random.default_rng(10007*k+{'tt':1,'ss':2,'ff':3,'sf':4,'fs':5}[MOS]); gR,gC,gP=rng.standard_normal(3)
    vm=(5.0/3)*gR; ca=2.0e-15*(1+0.037*gC); cp=max(0.19e-15+0.053e-15*gP,0.0)
    L=re.sub(r'sky130_fd_pr__res_high_po__var_mult = [-\d.e]+',f'sky130_fd_pr__res_high_po__var_mult = {vm:.6f}',lin)
    L=re.sub(r'camimc=\s*[\d.e-]+',f'camimc= {ca:.6e}',L); L=re.sub(r'cpmimc = [\d.e-]+',f'cpmimc = {cp:.6e}',L)
    open(f'tmp/lin_{MOS}_{k}.spice','w').write(L)
    b=[f'* mc {MOS} {k}','.param mc_mm_switch=1','.param mc_pr_switch=0',f'.include {P}/corners/{MOS}.spice',
       f'.include {P}/r+c/res_typical__cap_typical.spice',f'.include tmp/lin_{MOS}_{k}.spice',f'.include {P}/corners/{MOS}/specialized_cells.spice',
       f'.option seed={1000+k}', f'.include {NET}','.temp 27','.option rshunt=1e12','Vdd vdd 0 1.8']
    b+=[f'VG{i} g{i} 0 0' for i in range(5)]
    b+=['VA a 0 dc 1.0 ac 1','VB b 0 dc 1.0 ac 1','X1 a b g0 g1 g2 g3 g4 g0 g1 g2 g3 g4 vdd 0 toppex','.control','set wr_singlescale','option numdgt=7']
    for c in range(6):
        if c>=1: b.append(f'alter VG{c-1} dc=1.8')
        if c>=2: b.append(f'alter VG{c-2} dc=0')
        b+=['ac dec 40 10 100meg',f'wrdata tmp/z_{MOS}_{k}_{c}.dat real(-1/i(VA)) imag(-1/i(VA)) real(-1/i(VB)) imag(-1/i(VB))']
    b+=['.endc','.end']
    open(f'tmp/mc_{MOS}_{k}.sp','w').write('\n'.join(b)+'\n')
    r=subprocess.run(['ngspice','-b',f'tmp/mc_{MOS}_{k}.sp'],capture_output=True,text=True)
    try:
        Z=[np.loadtxt(f'tmp/z_{MOS}_{k}_{c}.dat') for c in range(6)]
    except Exception as e:
        print('FAIL',k,r.stdout[-500:],flush=True); continue
    f=Z[0][:,0]; za=[z[:,1]+1j*z[:,2] for z in Z]; zb=[z[:,3]+1j*z[:,4] for z in Z]
    out=dict(f=f,zA=za[0],zB=zb[0],gR=gR,gC=gC,gP=gP)
    for i in range(5): out[f'yA{i}']=1/za[i+1]-1/za[0]; out[f'yB{i}']=1/zb[i+1]-1/zb[0]
    np.savez(f'out_{MOS}/s{k:04d}.npz',**out)
    for c in range(6): os.remove(f'tmp/z_{MOS}_{k}_{c}.dat')
    print(MOS,k,f'gR {gR:+.2f} gC {gC:+.2f}',flush=True)
