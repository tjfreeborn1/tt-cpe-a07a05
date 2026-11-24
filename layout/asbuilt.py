"""Write as-built SPICE netlists (sim format, ground = 0) from the layout plan/geometry."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
g = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'build/geo.json'))
p = json.load(open(os.path.join(HERE, 'plan.json')))
out = sys.argv[2] if len(sys.argv) > 2 else 'asbuilt'
os.makedirs(out, exist_ok=True)
for net, key, dummyL in (('cpe_a07', 'i07', 2.602), ('cpe_a05', 'i05', None)):
    L = [f'* {net}: as-built (layout v1). R segments, MOS units W=10 L=10, MIM tiles', f'.subckt {net} t']
    info = g[key]
    for k, (b, bi) in enumerate(zip(p[net]['branches'], info['branches'])):
        idx = b['name'][1:]
        r = next(x for x in p[net]['res'] if x['name'] == 'R' + idx)
        nodes = ['t'] + [f'{idx}_s{i}' for i in range(1, r['nseg'])] + [f'n{idx}']
        for i in range(r['nseg']):
            L.append(f'XR{idx}_{i} {nodes[i]} {nodes[i+1]} 0 sky130_fd_pr__res_xhigh_po_0p35 L={r["L"]} mult=1')
        L.append(f'XM{idx} 0 n{idx} 0 0 sky130_fd_pr__nfet_01v8 W=10 L=10 nf=1 m={b["units"]}')
        m = bi['mim']
        L.append(f'XK{idx} n{idx} 0 sky130_fd_pr__cap_mim_m3_1 W={m["sx"]} L={m["sy"]} MF={m["n"]} m={m["n"]}')
    r = next(x for x in p[net]['res'] if x['name'] == 'Rp')
    nodes = ['t'] + [f'p_s{i}' for i in range(1, r['nseg'])] + ['0']
    for i in range(r['nseg']):
        L.append(f'XRp_{i} {nodes[i]} {nodes[i+1]} 0 sky130_fd_pr__res_xhigh_po_0p35 L={r["L"]} mult=1')
    if dummyL: L.append(f'XRD 0 0 0 sky130_fd_pr__res_xhigh_po_0p35 L={dummyL} mult=1')
    L.append('.ends')
    open(f'{out}/{net}.spice', 'w').write('\n'.join(L) + '\n')
bk = g['i07']['bank']
sw = {4: (6.0, 8), 3: (6.0, 4), 2: (6.0, 2), 1: (3.0, 2), 0: (1.5, 2)}
cells = {4: (bk['cw'], bk['ch'], 4), 3: (bk['cw'], bk['ch'], 2), 2: (bk['cw'], bk['ch'], 1), 1: (bk['w1'], bk['ch'], 1), 0: (bk['w0'], bk['ch'], 1)}
L = ['* trimbank: as-built (layout v1); bit tiles share one bottom-plate island per bit', '.subckt trimbank t g0 g1 g2 g3 g4']
for i in range(5):
    w, h, n = cells[i]; Wf, nf = sw[i]
    L += [f'XK{i} t b{i} sky130_fd_pr__cap_mim_m3_1 W={w} L={h} MF={n} m={n}',
          f'XS{i} b{i} g{i} 0 0 sky130_fd_pr__nfet_01v8 W={Wf*nf} L=0.15 nf=1 m=1', f'RL{i} b{i} 0 1e10']
L.append('.ends'); open(f'{out}/trimbank.spice', 'w').write('\n'.join(L) + '\n')
print(open(f'{out}/cpe_a07.spice').read()[:900]); print(open(f'{out}/trimbank.spice').read())
