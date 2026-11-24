"""Design plan: branch MOS units / MIM targets from v4b (as-drawn) values; resistor segmentation."""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
CU = 0.75876          # pF per W=10/L=10 nfet unit at 1.0 V (ngspice tt)
d = json.load(open(os.path.join(HERE, 'design_v4bL.json')))
RSL, RH = 5708.6, 623.0
def plan():
    out = {}
    for net in ('cpe_a07', 'cpe_a05'):
        br = []; res = []
        for r in d[net]:
            if r['branch'] == 'p':
                res.append(dict(name='Rp', R=r['R_kohm'] * 1e3)); continue
            n = round(r['mos_area_um2'] / 100.0)
            br.append(dict(name=f"C{r['branch']}", units=n, cmim=r['C_pF'] - n * CU, C=r['C_pF']))
            res.append(dict(name=f"R{r['branch']}", R=r['R_kohm'] * 1e3))
        out[net] = dict(branches=br, res=res)
    # resistor segmentation for layout
    seg = {'cpe_a07': {'R1': 7, 'R2': 3, 'R3': 1, 'R4': 1, 'R5': 1, 'Rp': 32},
           'cpe_a05': {'R1': 3, 'R2': 1, 'R3': 1, 'Rp': 2}}
    for net in out:
        for r in out[net]['res']:
            n = seg[net][r['name']]; r['nseg'] = n; r['L'] = round((r['R'] / n - RH) / RSL, 3)
    return out
if __name__ == '__main__':
    p = plan()
    for net, v in p.items():
        print(net, [(b['name'], b['units'], round(b['cmim'], 3)) for b in v['branches']])
        print('   ', [(r['name'], r['nseg'], r['L']) for r in v['res']])
    json.dump(p, open(os.path.join(HERE, 'plan.json'), 'w'), indent=1)
