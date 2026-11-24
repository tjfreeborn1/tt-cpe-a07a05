"""Layout-realistic v4b: segmented xhigh_po (<=100 um segments, head resistance compensated),
MIM split into <=30x30 um units, bank from unit cells (bits 3,4 = 2x,4x bit-2 cell), MOS 10x10 units + partial unit."""
import os, numpy as np, subprocess, json, math
P=os.path.join(os.environ.get('PDK_ROOT','/usr/local/share/pdk'),os.environ.get('PDK','sky130A'),'libs.tech','ngspice','sky130.lib.spice')
RSL, RH, LMAX = 5708.6, 623.0, 100.0
def segs(R):
    n=max(1,math.ceil((R-RH)/RSL/LMAX)); L=(R/n-RH)/RSL; return n,L
def res_lines(tag,a,b,R):
    n,L=segs(R); nodes=[a]+[f"{tag}_s{i}" for i in range(1,n)]+[b]
    return [f"XR{tag}_{i} {nodes[i]} {nodes[i+1]} 0 sky130_fd_pr__res_xhigh_po_0p35 L={L:.3f} mult=1" for i in range(n)], n, L
def stack_lines(tag,node,A):
    n=int(A//100); rem=A-100*n; L=[]
    if n: L.append(f"XM{tag} 0 {node} 0 0 sky130_fd_pr__nfet_01v8 W=10 L=10 nf=1 m={n}")
    if rem>4: L.append(f"XM{tag}p 0 {node} 0 0 sky130_fd_pr__nfet_01v8 W={rem/10:.3f} L=10 nf=1 m=1")
    Am=0.85*A; k=max(1,math.ceil(Am/900.0)); s=math.sqrt(Am/k)
    L.append(f"XK{tag} {node} 0 sky130_fd_pr__cap_mim_m3_1 W={s:.3f} L={s:.3f} MF={k} m={k}"); return L,k,s
def meas(lines):
    open('cc.spice','w').write(f"* c\n.lib {P} tt\nV1 a 0 dc 1.0 ac 1\n"+"\n".join(lines)+"\n.control\nac lin 1 100k 100k\nprint abs(imag(i(V1)))/(2*pi*100e3)\n.endc\n.end\n")
    o=subprocess.run(['ngspice','-b','cc.spice'],capture_output=True,text=True).stdout
    return float([l for l in o.splitlines() if l.strip().startswith('abs(imag')][0].split('=')[1])
rep={}
for name in ('cpe_a07','cpe_a05'):
    o=json.load(open(f'netlists/opt_{name}.json')); R=np.array(o['R']); C=np.array(o['C']); order=np.argsort(-C); R=R[order]; C=C[order]
    lines=[f"* {name} v4b layout-realistic", f".subckt {name} t"]; rows=[]
    for k,(r,c) in enumerate(zip(R,C)):
        A=c/9.348e-15
        for _ in range(4):
            l,_,_=stack_lines('x','a',A); A*=c/meas(l)
        sl,km,sm=stack_lines(str(k+1),f"n{k+1}",A); cm=meas(stack_lines('x','a',A)[0])
        rl,ns,Ls=res_lines(str(k+1),'t',f"n{k+1}",r)
        lines+=rl+sl; rows.append(dict(branch=k+1,R_kohm=r/1e3,segments=ns,seg_len_um=Ls,C_pF=c*1e12,C_sim_pF=cm*1e12,mos_area_um2=A,mim_units=km,mim_side_um=sm))
    rl,ns,Ls=res_lines('p','t','0',o['Rp']); lines+=rl; rows.append(dict(branch='p',R_kohm=o['Rp']/1e3,segments=ns,seg_len_um=Ls))
    lines.append(".ends"); open(f"netlists/{name}.spice","w").write("\n".join(lines)+"\n"); rep[name]=rows
    for r in rows: print(name,{k:(round(v,3) if isinstance(v,float) else v) for k,v in r.items()})
# bank: unit cells; bit0 0.3 pF, bit1 0.6 pF, bit2 1.2 pF cell; bit3 = 2 x bit2 cell; bit4 = 4 x bit2 cell
cells={}
for i,c in ((0,0.3e-12),(1,0.6e-12),(2,1.2e-12)):
    s=math.sqrt(c/2.07e-15)
    for _ in range(4):
        s*=math.sqrt(c/meas([f"XK a 0 sky130_fd_pr__cap_mim_m3_1 W={s:.3f} L={s:.3f} MF=1"])); 
    cells[i]=s
bank=[".subckt trimbank t g0 g1 g2 g3 g4"]
for i,(cell,mf) in enumerate(((0,1),(1,1),(2,1),(2,2),(2,4))):
    W=max(1.0,10.0*0.3*2**i)
    bank+=[f"XK{i} t b{i} sky130_fd_pr__cap_mim_m3_1 W={cells[cell]:.3f} L={cells[cell]:.3f} MF={mf} m={mf}",
           f"XS{i} b{i} g{i} 0 0 sky130_fd_pr__nfet_01v8 W={W:.2f} L=0.15 nf=1 m=1", f"RL{i} b{i} 0 1e10"]
    print(f"bank bit {i}: {mf} x {cells[cell]:.3f} um cell, switch W={W}")
bank.append(".ends"); open("netlists/trimbank.spice","w").write("\n".join(bank)+"\n")
json.dump(rep,open('netlists/design_v4bL.json','w'),indent=1)
