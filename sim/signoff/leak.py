import subprocess, re
import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)) if _o.path.basename(_o.path.dirname(_o.path.abspath(__file__)))=='signoff' else _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), '..'))
from common import run_ngspice, fresh, bank_y, LIB, PDK_NG, PEX, ASBUILT, GDS, REPO
P=LIB; AB=ASBUILT
for n in ('cpe_a07','cpe_a05'):
    s=open(f'{AB}/{n}.spice').read().replace(f'.subckt {n} t',f'.subckt {n}m t').replace('XRp_0 t ','XRp_0 tp ')
    s=s.replace('.ends','Vrp t tp 0\n.ends'); open(f'{n}m.spice','w').write(s)
print('net lib T | Itot pA | I_Rp pA | I_leak (network) pA | bank off-node V (code=0, all off) | I_bank pA')
for n in ('cpe_a07','cpe_a05'):
  for lib in ('tt','ff_ll','ff_hh','ss_hh'):
    for T in (27,85,125):
        b=[f'.lib {P} {lib}',f'.include {n}m.spice',f'.include tb_norl.spice',f'.temp {T}','.option rshunt=1e15',
           'V1 p 0 1.0','X1 p '+n+'m','V2 q 0 1.0','XB q 0 0 0 0 0 trimbank',
           '.control','op','print -i(V1)','print i(v.x1.vrp)','print -i(V2)','print v(XB.b0)','print v(XB.b4)','.endc','.end']
        open('l.sp','w').write('\n'.join(b)+'\n')
        o=run_ngspice('l.sp')
        v={}
        for line in o.splitlines():
            m=re.match(r'\s*(\S+)\s*=\s*([-\d.eE+]+)',line)
            if m: v[m.group(1)]=float(m.group(2))
        it=v.get('-i(v1)'); irp=v.get('i(v.x1.vrp)'); ib=v.get('-i(v2)')
        print(n,lib,T,'|',f"{it*1e12:.1f} | {irp*1e12:.1f} | {(it-irp)*1e12:.3f} | b0 {v.get('v(xb.b0)'):.3f} b4 {v.get('v(xb.b4)'):.3f} | {ib*1e12:.3f}")
